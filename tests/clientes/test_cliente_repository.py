"""
Testes unitários para ClienteRepository - Fase 4 Clean Architecture

Demonstra como testar repositories independentemente do app context.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from meu_app.clientes.repositories import ClienteRepository
from meu_app.models import Cliente


class TestClienteRepository:
    """Testes para ClienteRepository"""
    
    @pytest.fixture
    def repository(self):
        """Fixture para criar instância do repository"""
        return ClienteRepository()
    
    @pytest.fixture
    def mock_cliente(self):
        """Fixture para criar cliente mock"""
        cliente = Mock(spec=Cliente)
        cliente.id = 1
        cliente.nome = "Cliente Teste"
        cliente.fantasia = "Teste Fantasia"
        cliente.telefone = "(11) 98765-4321"
        cliente.endereco = "Rua Teste, 123"
        cliente.cidade = "São Paulo"
        cliente.cpf_cnpj = "12.345.678/0001-90"
        return cliente
    
    @patch('meu_app.clientes.repositories.Cliente')
    def test_buscar_por_id_encontrado(self, mock_model, repository, mock_cliente):
        """Testa busca de cliente por ID quando encontrado"""
        # Arrange
        mock_model.query.get.return_value = mock_cliente
        
        # Act
        resultado = repository.buscar_por_id(1)
        
        # Assert
        assert resultado is not None
        assert resultado.id == 1
        assert resultado.nome == "Cliente Teste"
        mock_model.query.get.assert_called_once_with(1)
    
    @patch('meu_app.clientes.repositories.Cliente')
    def test_buscar_por_id_nao_encontrado(self, mock_model, repository):
        """Testa busca de cliente por ID quando não encontrado"""
        # Arrange
        mock_model.query.get.return_value = None
        
        # Act
        resultado = repository.buscar_por_id(999)
        
        # Assert
        assert resultado is None
        mock_model.query.get.assert_called_once_with(999)
    
    @patch('meu_app.clientes.repositories.Cliente')
    def test_buscar_por_nome(self, mock_model, repository, mock_cliente):
        """Testa busca de cliente por nome"""
        # Arrange
        mock_query = Mock()
        mock_model.query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_cliente
        
        # Act
        resultado = repository.buscar_por_nome("Cliente Teste")
        
        # Assert
        assert resultado is not None
        assert resultado.nome == "Cliente Teste"
        mock_model.query.filter_by.assert_called_once_with(nome="Cliente Teste")
    
    @patch('meu_app.clientes.repositories.Cliente')
    def test_listar_todos(self, mock_model, repository, mock_cliente):
        """Testa listagem de todos os clientes"""
        # Arrange
        mock_query = Mock()
        mock_model.query.order_by.return_value = mock_query
        mock_query.all.return_value = [mock_cliente, mock_cliente]
        
        # Act
        resultado = repository.listar_todos()
        
        # Assert
        assert len(resultado) == 2
        assert all(c.nome == "Cliente Teste" for c in resultado)
    
    @patch('meu_app.clientes.repositories.Cliente')
    def test_verificar_nome_existe_true(self, mock_model, repository, mock_cliente):
        """Testa verificação de nome existente"""
        # Arrange
        mock_query = Mock()
        mock_model.query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock_cliente
        
        # Act
        resultado = repository.verificar_nome_existe("Cliente Teste")
        
        # Assert
        assert resultado is True
        mock_model.query.filter_by.assert_called_once_with(nome="Cliente Teste")
    
    @patch('meu_app.clientes.repositories.Cliente')
    def test_verificar_nome_existe_false(self, mock_model, repository):
        """Testa verificação de nome não existente"""
        # Arrange
        mock_query = Mock()
        mock_model.query.filter_by.return_value = mock_query
        mock_query.first.return_value = None
        
        # Act
        resultado = repository.verificar_nome_existe("Cliente Inexistente")
        
        # Assert
        assert resultado is False
    
    @patch('meu_app.clientes.repositories.Cliente')
    @patch('meu_app.clientes.repositories.db')
    def test_criar_cliente(self, mock_db, mock_model, repository, mock_cliente):
        """Testa criação de cliente"""
        # Arrange
        mock_db.session.add = Mock()
        mock_db.session.commit = Mock()
        
        # Act
        resultado = repository.criar(mock_cliente)
        
        # Assert
        mock_db.session.add.assert_called_once_with(mock_cliente)
        mock_db.session.commit.assert_called_once()
        assert resultado == mock_cliente
    
    @patch('meu_app.clientes.repositories.db')
    def test_atualizar_cliente(self, mock_db, repository, mock_cliente):
        """Testa atualização de cliente"""
        # Arrange
        mock_db.session.commit = Mock()
        
        # Act
        resultado = repository.atualizar(mock_cliente)
        
        # Assert
        mock_db.session.commit.assert_called_once()
        assert resultado == mock_cliente
    
    @patch('meu_app.clientes.repositories.db')
    def test_excluir_cliente(self, mock_db, repository, mock_cliente):
        """Testa exclusão de cliente"""
        # Arrange
        mock_db.session.delete = Mock()
        mock_db.session.commit = Mock()
        
        # Act
        resultado = repository.excluir(mock_cliente)
        
        # Assert
        mock_db.session.delete.assert_called_once_with(mock_cliente)
        mock_db.session.commit.assert_called_once()
        assert resultado is True
    
    @patch('meu_app.clientes.repositories.Cliente')
    def test_contar_total(self, mock_model, repository):
        """Testa contagem total de clientes"""
        # Arrange
        mock_query = Mock()
        mock_model.query.count.return_value = 10
        
        # Act
        resultado = repository.contar_total()
        
        # Assert
        assert resultado == 10
        mock_model.query.count.assert_called_once()


# Executar testes com: pytest tests/clientes/test_cliente_repository.py -v

