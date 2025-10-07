"""
Serviços para o módulo de clientes - Versão Atualizada com Validação
===================================================================

Contém toda a lógica de negócio separada das rotas com validação robusta.

Autor: Sistema de Gestão Empresarial
Data: 2024
"""

from ..models import db, Cliente, LogAtividade
from flask import current_app, session
from typing import Dict, List, Tuple, Optional
import json
from ..validators import validar_entrada_completa


class ClienteService:
    """Serviço para operações relacionadas a clientes"""
    
    @staticmethod
    def criar_cliente(nome: str, fantasia: str, telefone: str, endereco: str, cidade: str, cpf_cnpj: str) -> Tuple[bool, str, Optional[Cliente]]:
        """
        Cria um novo cliente com validação robusta
        
        Args:
            nome: Nome do cliente
            fantasia: Nome fantasia
            telefone: Telefone do cliente
            endereco: Endereço do cliente
            cidade: Cidade do cliente
            cpf_cnpj: CPF/CNPJ do cliente
            
        Returns:
            Tuple[bool, str, Optional[Cliente]]: (sucesso, mensagem, cliente)
        """
        try:
            # Definir regras de validação
            regras_validacao = {
                'nome': {'tipo': 'texto', 'obrigatorio': True, 'max_length': 255},
                'fantasia': {'tipo': 'texto', 'obrigatorio': False, 'max_length': 255},
                'telefone': {'tipo': 'telefone', 'obrigatorio': True},
                'endereco': {'tipo': 'texto', 'obrigatorio': True, 'max_length': 255},
                'cidade': {'tipo': 'texto', 'obrigatorio': True, 'max_length': 100},
                'cpf_cnpj': {'tipo': 'cpf_cnpj', 'obrigatorio': False}
            }
            
            # Preparar dados para validação
            dados_entrada = {
                'nome': nome,
                'fantasia': fantasia,
                'telefone': telefone,
                'endereco': endereco,
                'cidade': cidade,
                'cpf_cnpj': cpf_cnpj
            }
            
            # Validar entradas
            valido, dados_sanitizados, erros = validar_entrada_completa(dados_entrada, regras_validacao)
            
            if not valido:
                return False, f"Erro de validação: {'; '.join(erros)}", None
            
            # Verificar se já existe cliente com mesmo nome
            cliente_existente = Cliente.query.filter_by(nome=dados_sanitizados['nome']).first()
            if cliente_existente:
                return False, f"Já existe um cliente com o nome '{dados_sanitizados['nome']}'", None
            
            # Criar cliente com dados sanitizados
            novo_cliente = Cliente(
                nome=dados_sanitizados['nome'],
                fantasia=dados_sanitizados['fantasia'] or None,
                telefone=dados_sanitizados['telefone'],
                endereco=dados_sanitizados['endereco'],
                cidade=dados_sanitizados['cidade'],
                cpf_cnpj=dados_sanitizados['cpf_cnpj'] or None
            )
            
            db.session.add(novo_cliente)
            db.session.commit()
            
            # Registrar atividade
            ClienteService._registrar_atividade(
                'criacao',
                'Cliente criado',
                f"Cliente '{dados_sanitizados['nome']}' foi criado",
                'clientes',
                {'cliente_id': novo_cliente.id, 'cliente_nome': dados_sanitizados['nome']}
            )
            
            current_app.logger.info(f"Cliente criado: {dados_sanitizados['nome']} (ID: {novo_cliente.id})")
            return True, "Cliente criado com sucesso", novo_cliente
            
        except Exception as e:
            current_app.logger.error(f"Erro ao criar cliente: {str(e)}")
            db.session.rollback()
            return False, f"Erro ao criar cliente: {str(e)}", None
    
    @staticmethod
    def editar_cliente(cliente_id: int, nome: str, fantasia: str, telefone: str, endereco: str, cidade: str, cpf_cnpj: str) -> Tuple[bool, str, Optional[Cliente]]:
        """
        Edita um cliente existente com validação robusta
        
        Args:
            cliente_id: ID do cliente
            nome: Nome do cliente
            fantasia: Nome fantasia
            telefone: Telefone do cliente
            endereco: Endereço do cliente
            cidade: Cidade do cliente
            cpf_cnpj: CPF/CNPJ do cliente
            
        Returns:
            Tuple[bool, str, Optional[Cliente]]: (sucesso, mensagem, cliente)
        """
        try:
            # Buscar cliente
            cliente = Cliente.query.get(cliente_id)
            if not cliente:
                return False, "Cliente não encontrado", None
            
            # Definir regras de validação
            regras_validacao = {
                'nome': {'tipo': 'texto', 'obrigatorio': True, 'max_length': 255},
                'fantasia': {'tipo': 'texto', 'obrigatorio': False, 'max_length': 255},
                'telefone': {'tipo': 'telefone', 'obrigatorio': True},
                'endereco': {'tipo': 'texto', 'obrigatorio': True, 'max_length': 255},
                'cidade': {'tipo': 'texto', 'obrigatorio': True, 'max_length': 100},
                'cpf_cnpj': {'tipo': 'cpf_cnpj', 'obrigatorio': False}
            }
            
            # Preparar dados para validação
            dados_entrada = {
                'nome': nome,
                'fantasia': fantasia,
                'telefone': telefone,
                'endereco': endereco,
                'cidade': cidade,
                'cpf_cnpj': cpf_cnpj
            }
            
            # Validar entradas
            valido, dados_sanitizados, erros = validar_entrada_completa(dados_entrada, regras_validacao)
            
            if not valido:
                return False, f"Erro de validação: {'; '.join(erros)}", None
            
            # Verificar se já existe outro cliente com mesmo nome
            cliente_existente = Cliente.query.filter(
                Cliente.nome == dados_sanitizados['nome'],
                Cliente.id != cliente_id
            ).first()
            if cliente_existente:
                return False, f"Já existe outro cliente com o nome '{dados_sanitizados['nome']}'", None
            
            # Atualizar cliente com dados sanitizados
            cliente.nome = dados_sanitizados['nome']
            cliente.fantasia = dados_sanitizados['fantasia'] or None
            cliente.telefone = dados_sanitizados['telefone']
            cliente.endereco = dados_sanitizados['endereco']
            cliente.cidade = dados_sanitizados['cidade']
            cliente.cpf_cnpj = dados_sanitizados['cpf_cnpj'] or None
            
            db.session.commit()
            
            # Registrar atividade
            ClienteService._registrar_atividade(
                'edicao',
                'Cliente editado',
                f"Cliente '{dados_sanitizados['nome']}' foi editado",
                'clientes',
                {'cliente_id': cliente.id, 'cliente_nome': dados_sanitizados['nome']}
            )
            
            current_app.logger.info(f"Cliente editado: {dados_sanitizados['nome']} (ID: {cliente.id})")
            return True, "Cliente editado com sucesso", cliente
            
        except Exception as e:
            current_app.logger.error(f"Erro ao editar cliente: {str(e)}")
            db.session.rollback()
            return False, f"Erro ao editar cliente: {str(e)}", None
    
    @staticmethod
    def excluir_cliente(cliente_id: int) -> Tuple[bool, str]:
        """
        Exclui um cliente
        
        Args:
            cliente_id: ID do cliente
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            cliente = Cliente.query.get(cliente_id)
            if not cliente:
                return False, "Cliente não encontrado"
            
            nome_cliente = cliente.nome
            
            # Verificar se há pedidos associados
            from ..models import Pedido
            pedidos = Pedido.query.filter_by(cliente_id=cliente_id).count()
            if pedidos > 0:
                return False, f"Não é possível excluir o cliente. Existem {pedidos} pedido(s) associado(s)."
            
            # Verificação de coletas temporariamente desabilitada
            # (Tabela coleta não foi atualizada no banco de dados)
            # TODO: Ativar após migração do banco de dados
            
            db.session.delete(cliente)
            db.session.commit()
            
            # Registrar atividade
            ClienteService._registrar_atividade(
                'exclusao',
                'Cliente excluído',
                f"Cliente '{nome_cliente}' foi excluído",
                'clientes',
                {'cliente_id': cliente_id, 'cliente_nome': nome_cliente}
            )
            
            current_app.logger.info(f"Cliente excluído: {nome_cliente} (ID: {cliente_id})")
            return True, "Cliente excluído com sucesso"
            
        except Exception as e:
            current_app.logger.error(f"Erro ao excluir cliente: {str(e)}")
            db.session.rollback()
            return False, f"Erro ao excluir cliente: {str(e)}"
    
    @staticmethod
    def listar_clientes() -> List[Cliente]:
        """
        Lista todos os clientes
        
        Returns:
            List[Cliente]: Lista de clientes
        """
        try:
            return Cliente.query.all()
        except Exception as e:
            current_app.logger.error(f"Erro ao listar clientes: {str(e)}")
            return []
    
    @staticmethod
    def buscar_cliente_por_id(cliente_id: int) -> Optional[Cliente]:
        """
        Busca um cliente por ID
        
        Args:
            cliente_id: ID do cliente
            
        Returns:
            Optional[Cliente]: Cliente encontrado ou None
        """
        try:
            return Cliente.query.get(cliente_id)
        except Exception as e:
            current_app.logger.error(f"Erro ao buscar cliente: {str(e)}")
            return None
    
    @staticmethod
    def buscar_clientes_por_nome(nome: str) -> List[Cliente]:
        """
        Busca clientes por nome (busca parcial)
        
        Args:
            nome: Nome ou parte do nome
            
        Returns:
            List[Cliente]: Lista de clientes encontrados
        """
        try:
            return Cliente.query.filter(
                Cliente.nome.ilike(f'%{nome}%')
            ).all()
        except Exception as e:
            current_app.logger.error(f"Erro ao buscar clientes por nome: {str(e)}")
            return []
    
    @staticmethod
    def _registrar_atividade(tipo_atividade: str, titulo: str, descricao: str, modulo: str, dados_extras: Dict = None) -> None:
        """
        Registra atividade no log do sistema
        
        Args:
            tipo_atividade: Tipo da atividade
            titulo: Título da atividade
            descricao: Descrição da atividade
            modulo: Módulo onde ocorreu a atividade
            dados_extras: Dados extras em formato de dicionário
        """
        try:
            from ..log_atividades.services import LogAtividadesService
            
            sucesso, mensagem, _ = LogAtividadesService.registrar_atividade(
                tipo_atividade=tipo_atividade,
                titulo=titulo,
                descricao=descricao,
                modulo=modulo,
                dados_extras=dados_extras
            )
            
            if not sucesso:
                current_app.logger.warning(f"Falha ao registrar atividade: {mensagem}")
                
        except Exception as e:
            current_app.logger.error(f"Erro ao registrar atividade: {e}")
            # Não falhar se a atividade não puder ser registrada
            pass
