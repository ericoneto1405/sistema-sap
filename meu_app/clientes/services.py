"""
Serviços para o módulo de clientes - Versão Atualizada com Validação
===================================================================

Contém toda a lógica de negócio separada das rotas com validação robusta.

Autor: Sistema de Gestão Empresarial
Data: 2024
"""

from ..models import db, Cliente
from flask import current_app
from typing import Dict, List, Tuple, Optional
from pydantic import ValidationError
from .repositories import ClienteRepository
from .schemas import ClienteCreateSchema, ClienteUpdateSchema


class ClienteService:
    """Serviço para operações relacionadas a clientes"""
    
    def __init__(self, repository: Optional[ClienteRepository] = None):
        """Inicializa o serviço com seu repository"""
        self.repository = repository or ClienteRepository()

    @staticmethod
    def _format_validation_errors(error: ValidationError) -> str:
        """Monta string legível das mensagens de validação"""
        mensagens = []
        for detalhe in error.errors():
            campo = ".".join(str(parte) for parte in detalhe.get("loc", ()))
            mensagens.append(f"{campo}: {detalhe.get('msg')}")
        return "; ".join(mensagens)
    
    def criar_cliente(self, nome: str, fantasia: str, telefone: str, endereco: str, cidade: str, cpf_cnpj: str) -> Tuple[bool, str, Optional[Cliente]]:
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
            try:
                payload = ClienteCreateSchema(
                    nome=nome,
                    fantasia=fantasia,
                    telefone=telefone,
                    endereco=endereco,
                    cidade=cidade,
                    cpf_cnpj=cpf_cnpj
                )
            except ValidationError as exc:
                mensagem = self._format_validation_errors(exc)
                return False, f"Erro de validação: {mensagem}", None

            dados = payload.model_dump()

            # Verificar duplicidade de nome usando repository
            if self.repository.verificar_nome_existe(dados['nome']):
                return False, f"Já existe um cliente com o nome '{dados['nome']}'", None
            
            novo_cliente = Cliente(
                nome=dados['nome'],
                fantasia=dados.get('fantasia'),
                telefone=dados['telefone'],
                endereco=dados['endereco'],
                cidade=dados['cidade'],
                cpf_cnpj=dados.get('cpf_cnpj')
            )
            
            novo_cliente = self.repository.criar(novo_cliente)
            
            self._registrar_atividade(
                'criacao',
                'Cliente criado',
                f"Cliente '{dados['nome']}' foi criado",
                'clientes',
                {'cliente_id': novo_cliente.id, 'cliente_nome': dados['nome']}
            )
            
            current_app.logger.info(f"Cliente criado: {dados['nome']} (ID: {novo_cliente.id})")
            return True, "Cliente criado com sucesso", novo_cliente
            
        except Exception as e:
            current_app.logger.error(f"Erro ao criar cliente: {str(e)}")
            return False, f"Erro ao criar cliente: {str(e)}", None
    
    def editar_cliente(self, cliente_id: int, nome: str, fantasia: str, telefone: str, endereco: str, cidade: str, cpf_cnpj: str) -> Tuple[bool, str, Optional[Cliente]]:
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
            cliente = self.repository.buscar_por_id(cliente_id)
            if not cliente:
                return False, "Cliente não encontrado", None
            
            try:
                payload_update = ClienteUpdateSchema(
                    nome=nome,
                    fantasia=fantasia,
                    telefone=telefone,
                    endereco=endereco,
                    cidade=cidade,
                    cpf_cnpj=cpf_cnpj
                )
            except ValidationError as exc:
                mensagem = self._format_validation_errors(exc)
                return False, f"Erro de validação: {mensagem}", None
            
            dados_atualizados = payload_update.model_dump(exclude_unset=True)
            
            dados_finais = {
                'nome': dados_atualizados.get('nome', cliente.nome),
                'fantasia': dados_atualizados.get('fantasia', cliente.fantasia),
                'telefone': dados_atualizados.get('telefone', cliente.telefone),
                'endereco': dados_atualizados.get('endereco', cliente.endereco),
                'cidade': dados_atualizados.get('cidade', cliente.cidade),
                'cpf_cnpj': dados_atualizados.get('cpf_cnpj', cliente.cpf_cnpj),
            }
            
            # Validar dados finais completos para garantir consistência
            try:
                payload_final = ClienteCreateSchema(**dados_finais)
            except ValidationError as exc:
                mensagem = self._format_validation_errors(exc)
                return False, f"Erro de validação: {mensagem}", None
            
            dados_validados = payload_final.model_dump()
            
            if self.repository.verificar_nome_existe(dados_validados['nome'], excluir_id=cliente_id):
                return False, f"Já existe outro cliente com o nome '{dados_validados['nome']}'", None
            
            cliente.nome = dados_validados['nome']
            cliente.fantasia = dados_validados.get('fantasia')
            cliente.telefone = dados_validados['telefone']
            cliente.endereco = dados_validados['endereco']
            cliente.cidade = dados_validados['cidade']
            cliente.cpf_cnpj = dados_validados.get('cpf_cnpj')
            
            cliente = self.repository.atualizar(cliente)
            
            self._registrar_atividade(
                'edicao',
                'Cliente editado',
                f"Cliente '{dados_validados['nome']}' foi editado",
                'clientes',
                {'cliente_id': cliente.id, 'cliente_nome': dados_validados['nome']}
            )
            
            current_app.logger.info(f"Cliente editado: {dados_validados['nome']} (ID: {cliente.id})")
            return True, "Cliente editado com sucesso", cliente
            
        except Exception as e:
            current_app.logger.error(f"Erro ao editar cliente: {str(e)}")
            return False, f"Erro ao editar cliente: {str(e)}", None
    
    def excluir_cliente(self, cliente_id: int) -> Tuple[bool, str]:
        """
        Exclui um cliente
        
        Args:
            cliente_id: ID do cliente
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Buscar cliente usando repository
            cliente = self.repository.buscar_por_id(cliente_id)
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
            
            # Usar repository para excluir
            self.repository.excluir(cliente)
            
            # Registrar atividade
            self._registrar_atividade(
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
            return False, f"Erro ao excluir cliente: {str(e)}"
    
    def listar_clientes(self) -> List[Cliente]:
        """
        Lista todos os clientes
        
        Returns:
            List[Cliente]: Lista de clientes
        """
        try:
            return self.repository.listar_todos()
        except Exception as e:
            current_app.logger.error(f"Erro ao listar clientes: {str(e)}")
            return []
    
    def buscar_cliente_por_id(self, cliente_id: int) -> Optional[Cliente]:
        """
        Busca um cliente por ID
        
        Args:
            cliente_id: ID do cliente
            
        Returns:
            Optional[Cliente]: Cliente encontrado ou None
        """
        try:
            return self.repository.buscar_por_id(cliente_id)
        except Exception as e:
            current_app.logger.error(f"Erro ao buscar cliente: {str(e)}")
            return None
    
    def buscar_clientes_por_nome(self, nome: str) -> List[Cliente]:
        """
        Busca clientes por nome (busca parcial)
        
        Args:
            nome: Nome ou parte do nome
            
        Returns:
            List[Cliente]: Lista de clientes encontrados
        """
        try:
            return self.repository.buscar_por_nome_parcial(nome)
        except Exception as e:
            current_app.logger.error(f"Erro ao buscar clientes por nome: {str(e)}")
            return []
    
    def _registrar_atividade(self, tipo_atividade: str, titulo: str, descricao: str, modulo: str, dados_extras: Dict = None) -> None:
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
