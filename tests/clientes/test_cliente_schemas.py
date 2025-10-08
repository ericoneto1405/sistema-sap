"""
Testes para schemas Pydantic do módulo de clientes - Fase 4 Clean Architecture

Demonstra validação robusta de dados com Pydantic.
"""

import pytest
from pydantic import ValidationError
from meu_app.clientes.schemas import (
    ClienteCreateSchema,
    ClienteUpdateSchema,
    ClienteResponseSchema
)


class TestClienteCreateSchema:
    """Testes para schema de criação de cliente"""
    
    def test_criar_cliente_valido(self):
        """Testa criação de cliente com dados válidos"""
        # Arrange
        dados = {
            'nome': 'Cliente Teste',
            'fantasia': 'Teste Fantasia',
            'telefone': '(11) 98765-4321',
            'endereco': 'Rua Teste, 123',
            'cidade': 'São Paulo',
            'cpf_cnpj': '12.345.678/0001-90'
        }
        
        # Act
        schema = ClienteCreateSchema(**dados)
        
        # Assert
        assert schema.nome == 'Cliente Teste'
        assert schema.telefone == '(11) 98765-4321'
        assert schema.cidade == 'São Paulo'
    
    def test_criar_cliente_nome_obrigatorio(self):
        """Testa validação de nome obrigatório"""
        # Arrange
        dados = {
            'telefone': '(11) 98765-4321',
            'endereco': 'Rua Teste, 123',
            'cidade': 'São Paulo'
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ClienteCreateSchema(**dados)
        
        errors = exc_info.value.errors()
        assert any(err['loc'] == ('nome',) for err in errors)
    
    def test_criar_cliente_nome_muito_curto(self):
        """Testa validação de nome com tamanho mínimo"""
        # Arrange
        dados = {
            'nome': 'A',  # Menor que 2 caracteres
            'telefone': '(11) 98765-4321',
            'endereco': 'Rua Teste, 123',
            'cidade': 'São Paulo'
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ClienteCreateSchema(**dados)
        
        errors = exc_info.value.errors()
        assert any('nome' in str(err) for err in errors)
    
    def test_criar_cliente_telefone_invalido(self):
        """Testa validação de telefone"""
        # Arrange
        dados = {
            'nome': 'Cliente Teste',
            'telefone': '123',  # Telefone muito curto
            'endereco': 'Rua Teste, 123',
            'cidade': 'São Paulo'
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ClienteCreateSchema(**dados)
        
        errors = exc_info.value.errors()
        assert any('telefone' in str(err) for err in errors)
    
    def test_criar_cliente_cpf_cnpj_invalido(self):
        """Testa validação de CPF/CNPJ"""
        # Arrange
        dados = {
            'nome': 'Cliente Teste',
            'telefone': '(11) 98765-4321',
            'endereco': 'Rua Teste, 123',
            'cidade': 'São Paulo',
            'cpf_cnpj': '123'  # Formato inválido
        }
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            ClienteCreateSchema(**dados)
        
        errors = exc_info.value.errors()
        assert any('cpf_cnpj' in str(err) for err in errors)
    
    def test_criar_cliente_sem_fantasia(self):
        """Testa criação de cliente sem nome fantasia (opcional)"""
        # Arrange
        dados = {
            'nome': 'Cliente Teste',
            'telefone': '(11) 98765-4321',
            'endereco': 'Rua Teste, 123',
            'cidade': 'São Paulo'
        }
        
        # Act
        schema = ClienteCreateSchema(**dados)
        
        # Assert
        assert schema.fantasia is None
    
    def test_criar_cliente_sanitiza_espacos(self):
        """Testa sanitização de espaços em branco"""
        # Arrange
        dados = {
            'nome': '  Cliente Teste  ',
            'telefone': '  (11) 98765-4321  ',
            'endereco': 'Rua Teste, 123',
            'cidade': '  São Paulo  '
        }
        
        # Act
        schema = ClienteCreateSchema(**dados)
        
        # Assert
        assert schema.nome == 'Cliente Teste'
        assert schema.telefone == '(11) 98765-4321'
        assert schema.cidade == 'São Paulo'


class TestClienteUpdateSchema:
    """Testes para schema de atualização de cliente"""
    
    def test_atualizar_cliente_parcial(self):
        """Testa atualização parcial de cliente"""
        # Arrange
        dados = {
            'nome': 'Cliente Atualizado'
        }
        
        # Act
        schema = ClienteUpdateSchema(**dados)
        
        # Assert
        assert schema.nome == 'Cliente Atualizado'
        assert schema.telefone is None
        assert schema.endereco is None
    
    def test_atualizar_cliente_vazio(self):
        """Testa atualização sem campos"""
        # Arrange & Act
        schema = ClienteUpdateSchema()
        
        # Assert
        assert schema.nome is None
        assert schema.telefone is None


class TestClienteResponseSchema:
    """Testes para schema de resposta de cliente"""
    
    def test_criar_resposta_cliente(self):
        """Testa criação de schema de resposta"""
        from datetime import datetime
        
        # Arrange
        dados = {
            'id': 1,
            'nome': 'Cliente Teste',
            'fantasia': 'Teste Fantasia',
            'telefone': '(11) 98765-4321',
            'endereco': 'Rua Teste, 123',
            'cidade': 'São Paulo',
            'cpf_cnpj': '12.345.678/0001-90',
            'data_cadastro': datetime.now()
        }
        
        # Act
        schema = ClienteResponseSchema(**dados)
        
        # Assert
        assert schema.id == 1
        assert schema.nome == 'Cliente Teste'
        assert isinstance(schema.data_cadastro, datetime)


# Executar testes com: pytest tests/clientes/test_cliente_schemas.py -v

