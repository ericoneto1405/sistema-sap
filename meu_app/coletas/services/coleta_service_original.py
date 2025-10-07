"""
Serviço principal para operações de coleta - VERSÃO CORRIGIDA
"""
from typing import Dict, List, Tuple, Optional
from flask import current_app
from sqlalchemy import func

from meu_app.models import (
    db, Pedido, Coleta, ItemColetado, ItemPedido, 
    Usuario, Estoque, MovimentacaoEstoque, StatusColeta, StatusPedido
)


class ColetaService:
    """Serviço para operações relacionadas à coleta"""
    
    @staticmethod
    def listar_pedidos_para_coleta() -> List[Dict]:
        """
        Lista pedidos com status 'Pagamento Aprovado' ou 'Coleta Parcial' disponíveis para coleta.
        
        Returns:
            List[Dict]: Lista de pedidos com informações de coleta
        """
        try:
            # Buscar pedidos com pagamento aprovado ou coleta parcial
            pedidos = Pedido.query.filter(
                Pedido.status.in_([StatusPedido.PAGAMENTO_APROVADO, StatusPedido.COLETA_PARCIAL])
            ).options(
                db.joinedload(Pedido.cliente),
                db.joinedload(Pedido.itens).joinedload(ItemPedido.produto)
            ).all()
            
            lista_pedidos = []
            
            for pedido in pedidos:
                # Calcular quantidades já coletadas
                total_itens_pedido = 0
                total_itens_coletados = 0
                for item in pedido.itens:
                    total_itens_pedido += item.quantidade
                    total_coletado_item = db.session.query(
                        func.coalesce(func.sum(ItemColetado.quantidade_coletada), 0)
                    ).join(Coleta).filter(
                        Coleta.pedido_id == pedido.id,
                        ItemColetado.item_pedido_id == item.id
                    ).scalar()
                    total_itens_coletados += total_coletado_item
                
                itens_pendentes = total_itens_pedido - total_itens_coletados
                
                # Adicionar à lista apenas se houver itens pendentes
                if itens_pendentes > 0:
                    lista_pedidos.append({
                        'pedido': pedido,
                        'total_itens': total_itens_pedido,
                        'itens_coletados': total_itens_coletados,
                        'itens_pendentes': itens_pendentes
                    })
            
            return lista_pedidos
            
        except Exception as e:
            current_app.logger.error(f"Erro ao listar pedidos para coleta: {str(e)}")
            return []

    @staticmethod
    def buscar_detalhes_pedido(pedido_id: int) -> Optional[Dict]:
        """
        Busca detalhes completos de um pedido para coleta
        
        Args:
            pedido_id: ID do pedido
            
        Returns:
            Optional[Dict]: Detalhes do pedido ou None se não encontrado
        """
        try:
            pedido = Pedido.query.filter(
                Pedido.id == pedido_id,
                Pedido.status.in_([StatusPedido.PAGAMENTO_APROVADO, StatusPedido.COLETA_PARCIAL])
            ).options(
                db.joinedload(Pedido.cliente),
                db.joinedload(Pedido.itens).joinedload(ItemPedido.produto)
            ).first()
            
            if not pedido:
                return None
            
            # Calcular quantidades já coletadas e pendentes
            for item in pedido.itens:
                total_coletado = db.session.query(
                    func.coalesce(func.sum(ItemColetado.quantidade_coletada), 0)
                ).join(Coleta).filter(
                    Coleta.pedido_id == pedido.id,
                    ItemColetado.item_pedido_id == item.id
                ).scalar()
                
                item.quantidade_coletada = total_coletado
                item.quantidade_pendente = item.quantidade - total_coletado
                
                # Verificar estoque disponível
                estoque = Estoque.query.filter_by(produto_id=item.produto_id).first()
                item.estoque_disponivel = estoque.quantidade if estoque else 0
            
            return {
                'pedido': pedido,
                'cliente': pedido.cliente,
                'itens': pedido.itens,
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao buscar detalhes do pedido {pedido_id}: {str(e)}")
            return None

    @staticmethod
    def processar_coleta(
        pedido_id: int,
        responsavel_coleta_id: int,
        nome_retirada: str,
        documento_retirada: str,
        itens_coleta: List[Dict],
        observacoes: str = None,
        nome_conferente: str = None,
        cpf_conferente: str = None
    ) -> Tuple[bool, str, Optional[Coleta]]:
        """
        Processa uma nova coleta
        
        Args:
            pedido_id: ID do pedido
            responsavel_coleta_id: ID do usuário responsável pela coleta
            nome_retirada: Nome de quem está retirando
            documento_retirada: CPF de quem está retirando
            itens_coleta: Lista de itens e quantidades a coletar
            observacoes: Observações opcionais
            nome_conferente: Nome do conferente
            cpf_conferente: CPF do conferente
            
        Returns:
            Tuple[bool, str, Optional[Coleta]]: (sucesso, mensagem, coleta)
        """
        try:
            # Validar dados básicos
            if not nome_retirada or not documento_retirada:
                return False, "Nome e documento da retirada são obrigatórios", None
            
            if not itens_coleta:
                return False, "Selecione pelo menos um item para coleta", None
            
            # Buscar pedido com lock para evitar race conditions
            pedido = db.session.query(Pedido).filter(
                Pedido.id == pedido_id
            ).with_for_update().first()
            
            if not pedido or pedido.status not in [StatusPedido.PAGAMENTO_APROVADO, StatusPedido.COLETA_PARCIAL]:
                return False, "Pedido não encontrado ou não disponível para coleta", None
            
            # Validar itens e quantidades
            for item_data in itens_coleta:
                item_id = item_data.get('item_id')
                quantidade = item_data.get('quantidade', 0)
                
                if quantidade <= 0:
                    continue
                
                # Buscar item do pedido com lock
                item_pedido = db.session.query(ItemPedido).filter(
                    ItemPedido.id == item_id,
                    ItemPedido.pedido_id == pedido_id
                ).with_for_update().first()
                
                if not item_pedido:
                    return False, f"Item {item_id} não encontrado no pedido", None
                
                # Calcular quantidade já coletada
                total_coletado_item = db.session.query(
                    func.coalesce(func.sum(ItemColetado.quantidade_coletada), 0)
                ).join(Coleta).filter(
                    Coleta.pedido_id == pedido.id,
                    ItemColetado.item_pedido_id == item_pedido.id
                ).scalar()
                
                quantidade_pendente = item_pedido.quantidade - total_coletado_item
                
                # Validar se não excede o pendente
                if quantidade > quantidade_pendente:
                    return False, f"Quantidade {quantidade} excede o pendente {quantidade_pendente} para {item_pedido.produto.nome}", None
                
                # Validar estoque com lock
                estoque = db.session.query(Estoque).filter_by(
                    produto_id=item_pedido.produto_id
                ).with_for_update().first()
                
                if estoque and quantidade > estoque.quantidade:
                    return False, f"Quantidade {quantidade} excede o estoque disponível {estoque.quantidade} para {item_pedido.produto.nome}", None
            
            # Determinar status da coleta
            total_pendente_geral = 0
            for item_pedido in pedido.itens:
                total_coletado_item = db.session.query(
                    func.coalesce(func.sum(ItemColetado.quantidade_coletada), 0)
                ).join(Coleta).filter(
                    Coleta.pedido_id == pedido.id,
                    ItemColetado.item_pedido_id == item_pedido.id
                ).scalar()
                total_pendente_geral += item_pedido.quantidade - total_coletado_item

            total_coletado_nesta_vez = sum(item_data.get('quantidade', 0) for item_data in itens_coleta)
            
            if total_coletado_nesta_vez >= total_pendente_geral:
                status_coleta = StatusColeta.TOTALMENTE_COLETADO
                status_pedido = StatusPedido.COLETA_CONCLUIDA
            else:
                status_coleta = StatusColeta.PARCIALMENTE_COLETADO
                status_pedido = StatusPedido.COLETA_PARCIAL
            
            # CORREÇÃO: Remover transação aninhada - usar transação única
            # Criar registro de coleta
            nova_coleta = Coleta(
                pedido_id=pedido_id,
                responsavel_coleta_id=responsavel_coleta_id,
                nome_retirada=nome_retirada,
                documento_retirada=documento_retirada,
                status=status_coleta,
                observacoes=observacoes
            )
            
            db.session.add(nova_coleta)
            db.session.flush()  # Para obter o ID da coleta
        
            # Criar registros de itens coletados e dar baixa no estoque
            for item_data in itens_coleta:
                quantidade = item_data.get('quantidade', 0)
                if quantidade > 0:
                    item_coletado = ItemColetado(
                        coleta_id=nova_coleta.id,
                        item_pedido_id=item_data['item_id'],
                        quantidade_coletada=quantidade
                    )
                    db.session.add(item_coletado)
                    
                    # Dar baixa no estoque
                    ColetaService._registrar_movimentacao_estoque(
                        item_data['item_id'],
                        quantidade,
                        nome_retirada
                    )
            
            # Atualizar status do pedido
            pedido.status = status_pedido
            
            # Commit da transação
            db.session.commit()
            
            current_app.logger.info(f"Coleta processada: ID {nova_coleta.id}, Pedido {pedido_id}, Status {status_coleta.value}")
            
            return True, f"Coleta registrada com sucesso. Status: {status_coleta.value}", nova_coleta
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao processar coleta: {str(e)}")
            return False, f"Erro ao processar coleta: {str(e)}", None

    @staticmethod
    def _registrar_movimentacao_estoque(item_pedido_id: int, quantidade: int, responsavel: str):
        """
        Registra movimentação de estoque para uma coleta
        
        Args:
            item_pedido_id: ID do item do pedido
            quantidade: Quantidade coletada
            responsavel: Nome do responsável
        """
        try:
            # Buscar item do pedido com lock
            item_pedido = db.session.query(ItemPedido).options(
                db.joinedload(ItemPedido.produto)
            ).filter(ItemPedido.id == item_pedido_id).with_for_update().first()
            
            if not item_pedido:
                return
            
            produto_id = item_pedido.produto_id
            
            # Buscar estoque atual com lock
            estoque = db.session.query(Estoque).filter_by(
                produto_id=produto_id
            ).with_for_update().first()
            
            if not estoque:
                return
            
            # Calcular novas quantidades
            quantidade_anterior = estoque.quantidade
            quantidade_atual = quantidade_anterior - quantidade
            
            # Criar movimentação
            movimentacao = MovimentacaoEstoque(
                produto_id=produto_id,
                tipo_movimentacao="Saída",
                quantidade_anterior=quantidade_anterior,
                quantidade_movimentada=-quantidade,  # Negativo para saída
                quantidade_atual=quantidade_atual,
                motivo=f"Saída por coleta - Responsável: {responsavel}",
                responsavel=responsavel,
                observacoes=f"Coleta do pedido {item_pedido.pedido_id}"
            )
            
            db.session.add(movimentacao)
            
            # Atualizar estoque
            estoque.quantidade = quantidade_atual
            
            current_app.logger.info(f"Movimentação de estoque registrada: {item_pedido.produto.nome} - Saída: {quantidade}")
            
        except Exception as e:
            current_app.logger.error(f"Erro ao registrar movimentação de estoque: {str(e)}")

    @staticmethod
    def buscar_historico_coletas(pedido_id: int) -> Optional[Dict]:
        """
        Busca o histórico de coletas de um pedido.

        Args:
            pedido_id: ID do pedido.

        Returns:
            Optional[Dict]: Dicionário com o histórico do pedido ou None.
        """
        try:
            pedido = db.session.query(Pedido).filter(Pedido.id == pedido_id).first()
            if not pedido:
                return None

            coletas = Coleta.query.filter_by(pedido_id=pedido_id).order_by(Coleta.data_coleta.desc()).all()

            return {
                'pedido': pedido,
                'coletas': coletas
            }
        except Exception as e:
            current_app.logger.error(f"Erro ao buscar histórico de coletas: {str(e)}")
            return None
