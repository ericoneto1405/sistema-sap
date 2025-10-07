"""
Serviços para o módulo de financeiro
Contém toda a lógica de negócio separada das rotas
"""
from ..models import db, Pedido, Pagamento, StatusPedido
from flask import current_app
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload
import calendar
from decimal import Decimal
from .config import FinanceiroConfig
from .exceptions import (
    FinanceiroValidationError, 
    PagamentoDuplicadoError, 
    PedidoNaoEncontradoError,
    ValorInvalidoError,
    ComprovanteObrigatorioError
)

class FinanceiroService:
    """Serviço para operações relacionadas ao financeiro"""
    
    @staticmethod
    def _get_date_range(mes: str, ano: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Calcula o range de datas para filtros de mês e ano
        
        Args:
            mes: Mês como string (1-12)
            ano: Ano como string
            
        Returns:
            Tuple[Optional[datetime], Optional[datetime]]: (data_inicio, data_fim)
        """
        if not mes and not ano:
            return None, None
            
        if mes and ano:
            # Filtro por mês e ano específicos
            ano_int = int(ano)
            mes_int = int(mes)
            data_inicio = datetime(ano_int, mes_int, 1)
            # Usar calendar.monthrange para obter o último dia do mês
            ultimo_dia = calendar.monthrange(ano_int, mes_int)[1]
            data_fim = datetime(ano_int, mes_int, ultimo_dia, 23, 59, 59)
            return data_inicio, data_fim
            
        elif ano:
            # Filtro apenas por ano
            ano_int = int(ano)
            data_inicio = datetime(ano_int, 1, 1)
            data_fim = datetime(ano_int, 12, 31, 23, 59, 59)
            return data_inicio, data_fim
            
        elif mes:
            # Filtro apenas por mês (ano atual)
            ano_atual = datetime.now().year
            mes_int = int(mes)
            data_inicio = datetime(ano_atual, mes_int, 1)
            ultimo_dia = calendar.monthrange(ano_atual, mes_int)[1]
            data_fim = datetime(ano_atual, mes_int, ultimo_dia, 23, 59, 59)
            return data_inicio, data_fim
            
        return None, None
    
    @staticmethod
    def listar_pedidos_financeiro(tipo_filtro: str = 'pendentes', mes: str = '', ano: str = '') -> List[Dict]:
        """
        Lista pedidos para análise financeira
        
        Args:
            tipo_filtro: Tipo de filtro (pendentes, pagos, etc.)
            mes: Mês para filtrar
            ano: Ano para filtrar
            
        Returns:
            List[Dict]: Lista de pedidos com informações financeiras
        """
        try:
            # IMPORTANTE: O módulo financeiro só deve mostrar pedidos confirmados pelo comercial
            pedidos_query = Pedido.query.filter(Pedido.confirmado_comercial == True)
            
            # Aplicar filtros de data usando função helper
            data_inicio, data_fim = FinanceiroService._get_date_range(mes, ano)
            if data_inicio and data_fim:
                pedidos_query = pedidos_query.filter(Pedido.data >= data_inicio, Pedido.data <= data_fim)
            
            # Otimização: Carregar relacionamentos de uma vez para evitar N+1 queries
            pedidos = pedidos_query.options(
                joinedload(Pedido.itens),
                joinedload(Pedido.pagamentos)
            ).order_by(Pedido.data.desc()).all()
            
            resultado = []

            for pedido in pedidos:
                # Usar método centralizado do modelo
                totais = pedido.calcular_totais()
                status = pedido.obter_status_pagamento()
                
                # Aplicar filtro de tipo
                if tipo_filtro == 'pendentes' and (status == 'Pendente' or status == 'Parcial'):
                    resultado.append({
                        'pedido': pedido,
                        'total_pedido': totais['total_pedido'],
                        'total_pago': totais['total_pago'],
                        'saldo': totais['saldo'],
                        'status': status
                    })
                elif tipo_filtro == 'pagos' and status == 'Pago':
                    resultado.append({
                        'pedido': pedido,
                        'total_pedido': totais['total_pedido'],
                        'total_pago': totais['total_pago'],
                        'saldo': totais['saldo'],
                        'status': status
                    })
                elif tipo_filtro == 'todos':
                    resultado.append({
                        'pedido': pedido,
                        'total_pedido': totais['total_pedido'],
                        'total_pago': totais['total_pago'],
                        'saldo': totais['saldo'],
                        'status': status
                    })
            
            return resultado
            
        except Exception as e:
            current_app.logger.error(f"Erro ao listar pedidos financeiro: {str(e)}")
            return []
    
    @staticmethod
    def registrar_pagamento(
        pedido_id: int, 
        valor: float, 
        forma_pagamento: str, 
        observacoes: str = '', 
        caminho_recibo: str = None, 
        id_transacao: str = None, 
        recibo_mime: Optional[str] = None, 
        recibo_tamanho: Optional[int] = None, 
        recibo_sha256: Optional[str] = None,
        # NOVOS PARÂMETROS - dados extraídos do comprovante
        data_comprovante: Optional[str] = None,
        banco_emitente: Optional[str] = None,
        agencia_recebedor: Optional[str] = None,
        conta_recebedor: Optional[str] = None,
        chave_pix_recebedor: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Pagamento]]:
        """
        Registra um pagamento com dados completos extraídos do comprovante.
        """
        try:
            # Validações com exceções específicas
            if not pedido_id:
                raise FinanceiroValidationError("Pedido é obrigatório")
            
            pedido = Pedido.query.get(pedido_id)
            if not pedido:
                raise PedidoNaoEncontradoError(f"Pedido {pedido_id} não encontrado")
            
            if valor <= 0:
                raise ValorInvalidoError(f"Valor deve ser maior que zero. Valor fornecido: {valor}")
            
            if not forma_pagamento or not forma_pagamento.strip():
                raise FinanceiroValidationError("Forma de pagamento é obrigatória")

            # Validação para PIX: comprovante é obrigatório (usando configuração)
            if FinanceiroConfig.is_pix_payment_requiring_receipt() and 'pix' in forma_pagamento.lower() and not caminho_recibo:
                raise ComprovanteObrigatorioError("Para pagamentos com PIX, o envio do comprovante é obrigatório.")

            # VERIFICAÇÃO DE DUPLICIDADE PELO ID DA TRANSAÇÃO
            if id_transacao and id_transacao.strip():
                id_transacao_limpo = id_transacao.strip()
                pagamento_existente = Pagamento.query.filter_by(id_transacao=id_transacao_limpo).first()
                if pagamento_existente:
                    mensagem_erro = f"Este recibo (ID: {id_transacao_limpo}) já foi utilizado no pagamento do pedido #{pagamento_existente.pedido_id} em {pagamento_existente.data_pagamento.strftime('%d/%m/%Y')}."
                    current_app.logger.warning(mensagem_erro)
                    raise PagamentoDuplicadoError(mensagem_erro)
            else:
                id_transacao_limpo = None

            # Converter valor para Decimal para consistência com o banco
            valor_decimal = Decimal(str(valor))
            
            # Processar data do comprovante se fornecida
            data_comprovante_parsed = None
            if data_comprovante:
                try:
                    # Tentar diferentes formatos de data
                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y-%m-%d']:
                        try:
                            data_comprovante_parsed = datetime.strptime(data_comprovante, fmt).date()
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    current_app.logger.warning(f"Erro ao processar data do comprovante '{data_comprovante}': {e}")
            
            # Criar pagamento com todos os dados
            novo_pagamento = Pagamento(
                pedido_id=pedido_id,
                valor=valor_decimal,
                metodo_pagamento=forma_pagamento.strip(),
                observacoes=observacoes.strip() if observacoes else None,
                caminho_recibo=caminho_recibo,
                id_transacao=id_transacao_limpo,
                recibo_mime=recibo_mime,
                recibo_tamanho=recibo_tamanho,
                recibo_sha256=recibo_sha256,
                # NOVOS CAMPOS - dados extraídos do comprovante
                data_comprovante=data_comprovante_parsed,
                banco_emitente=banco_emitente.strip() if banco_emitente else None,
                agencia_recebedor=agencia_recebedor.strip() if agencia_recebedor else None,
                conta_recebedor=conta_recebedor.strip() if conta_recebedor else None,
                chave_pix_recebedor=chave_pix_recebedor.strip() if chave_pix_recebedor else None
            )
            
            db.session.add(novo_pagamento)
            db.session.flush() # Garante que o novo pagamento esteja na sessão para o cálculo abaixo

            # CORREÇÃO CRÍTICA: Forçar atualização da coleção pagamentos
            # Após flush(), a coleção self.pagamentos não é automaticamente atualizada
            db.session.refresh(pedido)  # Força reload do objeto pedido do banco

            # Usar método centralizado do modelo - CORRIGINDO O ERRO DE TIPO
            totais = pedido.calcular_totais()

            # CORREÇÃO: Converter para Decimal antes da comparação
            total_pago_decimal = Decimal(str(totais['total_pago']))
            total_pedido_decimal = Decimal(str(totais['total_pedido']))
            
            # O status do pedido é atualizado para pago se o valor total for atingido
            if total_pago_decimal >= total_pedido_decimal:
                pedido.status = StatusPedido.PAGAMENTO_APROVADO

            db.session.commit()

            current_app.logger.info(f"Pagamento registrado: Pedido #{pedido_id} - R$ {valor:.2f} - ID Transação: {id_transacao_limpo}")
            current_app.logger.info(f"Dados extraídos - Banco: {banco_emitente}, Agência: {agencia_recebedor}, Conta: {conta_recebedor}")
            
            return True, "Pagamento registrado com sucesso", novo_pagamento
            
        except (FinanceiroValidationError, PagamentoDuplicadoError, PedidoNaoEncontradoError, 
                ValorInvalidoError, ComprovanteObrigatorioError) as e:
            db.session.rollback()
            current_app.logger.warning(f"Erro de validação no pagamento: {str(e)}")
            return False, str(e), None
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro inesperado ao registrar pagamento: {str(e)}")
            return False, f"Erro interno ao registrar pagamento. Tente novamente.", None
    
    @staticmethod
    def exportar_dados_financeiro(mes: str = '', ano: str = '') -> Dict:
        """
        Exporta dados financeiros
        
        Args:
            mes: Mês para filtrar
            ano: Ano para filtrar
            
        Returns:
            Dict: Dados financeiros para exportação
        """
        try:
            pedidos = FinanceiroService.listar_pedidos_financeiro('todos', mes, ano)
            
            total_receita = sum(p['total_pedido'] for p in pedidos)
            total_recebido = sum(p['total_pago'] for p in pedidos)
            total_pendente = sum(max(0, p['saldo']) for p in pedidos)
            
            return {
                'pedidos': pedidos,
                'total_receita': total_receita,
                'total_recebido': total_recebido,
                'total_pendente': total_pendente,
                'mes': mes,
                'ano': ano
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao exportar dados financeiros: {str(e)}")
            return {
                'pedidos': [],
                'total_receita': 0,
                'total_recebido': 0,
                'total_pendente': 0,
                'mes': mes,
                'ano': ano
            }
    
    @staticmethod
    def listar_comprovantes_por_cliente(mes: str = '', ano: str = '') -> Dict:
        """
        Lista todos os comprovantes de pagamento organizados por cliente
        
        Args:
            mes: Mês para filtrar
            ano: Ano para filtrar
            
        Returns:
            Dict: Dicionário com clientes e seus comprovantes
        """
        try:
            from ..models import Pagamento, Cliente
            
            # Aplicar filtros de data
            data_inicio, data_fim = FinanceiroService._get_date_range(mes, ano)
            
            # Query base para pagamentos com comprovantes
            query = Pagamento.query.filter(Pagamento.caminho_recibo.isnot(None))
            
            if data_inicio and data_fim:
                query = query.filter(Pagamento.data_pagamento >= data_inicio, 
                                   Pagamento.data_pagamento <= data_fim)
            
            # Carregar relacionamentos necessários
            pagamentos = query.options(
                joinedload(Pagamento.pedido).joinedload(Pedido.cliente)
            ).order_by(Pagamento.data_pagamento.desc()).all()
            
            # Organizar por cliente
            comprovantes_por_cliente = {}
            
            for pagamento in pagamentos:
                cliente_id = pagamento.pedido.cliente.id
                cliente_nome = pagamento.pedido.cliente.nome
                
                if cliente_id not in comprovantes_por_cliente:
                    comprovantes_por_cliente[cliente_id] = {
                        'cliente': {
                            'id': cliente_id,
                            'nome': cliente_nome
                        },
                        'comprovantes': []
                    }
                
                comprovantes_por_cliente[cliente_id]['comprovantes'].append({
                    'pagamento': pagamento,
                    'pedido_id': pagamento.pedido.id,
                    'data_pagamento': pagamento.data_pagamento,
                    'valor': pagamento.valor,
                    'metodo_pagamento': pagamento.metodo_pagamento,
                    'caminho_recibo': pagamento.caminho_recibo,
                    'id_transacao': pagamento.id_transacao,
                    'observacoes': pagamento.observacoes,
                    # NOVOS CAMPOS - dados extraídos
                    'data_comprovante': pagamento.data_comprovante,
                    'banco_emitente': pagamento.banco_emitente,
                    'agencia_recebedor': pagamento.agencia_recebedor,
                    'conta_recebedor': pagamento.conta_recebedor,
                    'chave_pix_recebedor': pagamento.chave_pix_recebedor
                })
            
            # Ordenar clientes por nome
            clientes_ordenados = sorted(
                comprovantes_por_cliente.values(), 
                key=lambda x: x['cliente']['nome']
            )
            
            return {
                'clientes': clientes_ordenados,
                'total_comprovantes': sum(len(cliente['comprovantes']) for cliente in clientes_ordenados),
                'mes': mes,
                'ano': ano
            }
            
        except Exception as e:
            current_app.logger.error(f"Erro ao listar comprovantes por cliente: {str(e)}")
            return {
                'clientes': [],
                'total_comprovantes': 0,
                'mes': mes,
                'ano': ano
            }