"""
Testes unitários para ClienteService - garantem isolamento de contexto Flask.
"""

import pytest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from meu_app.clientes.services import ClienteService


@pytest.fixture
def repository():
    """Retorna repositório mockado para os testes."""
    repo = MagicMock()
    repo.verificar_nome_existe.return_value = False
    repo.criar.return_value = MagicMock(id=1, nome="Cliente Teste")
    repo.atualizar.return_value = MagicMock(
        id=1,
        nome="Cliente Atualizado",
        fantasia="Fantasia Atualizada",
        telefone="(11) 99999-9999",
        endereco="Rua Atualizada, 200",
        cidade="Campinas",
        cpf_cnpj="12.345.678/0001-90",
    )
    return repo


@pytest.fixture
def service(repository):
    """Instância do serviço com o repository mockado."""
    return ClienteService(repository=repository)


def _mock_current_app():
    """Cria mock minimamente compatível de current_app."""
    logger = MagicMock()
    return SimpleNamespace(logger=logger)


def test_criar_cliente_sucesso(service, repository):
    """Deve criar cliente quando dados são válidos."""
    cliente_mock = MagicMock(id=1, nome="Cliente Teste")
    repository.criar.return_value = cliente_mock

    with patch("meu_app.clientes.services.Cliente", return_value=cliente_mock), \
         patch("meu_app.clientes.services.current_app", new=_mock_current_app()), \
         patch.object(service, "_registrar_atividade") as registrar_mock:

        sucesso, mensagem, resultado = service.criar_cliente(
            nome="Cliente Teste",
            fantasia="Cliente Fantasia",
            telefone="(11) 98765-4321",
            endereco="Rua Teste, 123",
            cidade="São Paulo",
            cpf_cnpj="12.345.678/0001-90",
        )

    assert sucesso is True
    assert mensagem == "Cliente criado com sucesso"
    assert resultado is cliente_mock
    repository.verificar_nome_existe.assert_called_once_with("Cliente Teste")
    repository.criar.assert_called_once()
    registrar_mock.assert_called_once()


def test_criar_cliente_validacao_falha(service, repository):
    """Deve retornar erro quando dados são inválidos."""
    sucesso, mensagem, resultado = service.criar_cliente(
        nome="",
        fantasia="",
        telefone="123",
        endereco="",
        cidade="",
        cpf_cnpj="123",
    )

    assert sucesso is False
    assert mensagem.startswith("Erro de validação")
    assert resultado is None
    repository.verificar_nome_existe.assert_not_called()
    repository.criar.assert_not_called()


def test_criar_cliente_nome_duplicado(service, repository):
    """Não deve criar cliente se já existir nome igual."""
    repository.verificar_nome_existe.return_value = True

    sucesso, mensagem, resultado = service.criar_cliente(
        nome="Cliente Duplicado",
        fantasia=None,
        telefone="(11) 98765-4321",
        endereco="Rua Teste, 123",
        cidade="São Paulo",
        cpf_cnpj=None,
    )

    assert sucesso is False
    assert "já existe um cliente" in mensagem.lower()
    assert resultado is None
    repository.criar.assert_not_called()


def test_editar_cliente_sucesso(service, repository):
    """Deve editar cliente com dados válidos."""
    cliente_existente = MagicMock(
        id=1,
        nome="Cliente Original",
        fantasia="Fantasia Original",
        telefone="(11) 90000-0000",
        endereco="Rua Original, 100",
        cidade="São Paulo",
        cpf_cnpj="12.345.678/0001-90",
    )
    repository.buscar_por_id.return_value = cliente_existente

    with patch("meu_app.clientes.services.current_app", new=_mock_current_app()), \
         patch.object(service, "_registrar_atividade") as registrar_mock:

        sucesso, mensagem, resultado = service.editar_cliente(
            cliente_id=1,
            nome="Cliente Atualizado",
            fantasia="Fantasia Atualizada",
            telefone="(11) 99999-9999",
            endereco="Rua Atualizada, 200",
            cidade="Campinas",
            cpf_cnpj="12.345.678/0001-90",
        )

    assert sucesso is True
    assert mensagem == "Cliente editado com sucesso"
    assert resultado is repository.atualizar.return_value
    repository.buscar_por_id.assert_called_once_with(1)
    repository.verificar_nome_existe.assert_called_with("Cliente Atualizado", excluir_id=1)
    repository.atualizar.assert_called_once_with(cliente_existente)
    registrar_mock.assert_called_once()


def test_editar_cliente_validacao_falha(service, repository):
    """Deve retornar erro de validação ao editar com dados inválidos."""
    cliente_existente = MagicMock(
        id=1,
        nome="Cliente Original",
        fantasia="Fantasia Original",
        telefone="(11) 90000-0000",
        endereco="Rua Original, 100",
        cidade="São Paulo",
        cpf_cnpj="12.345.678/0001-90",
    )
    repository.buscar_por_id.return_value = cliente_existente

    sucesso, mensagem, resultado = service.editar_cliente(
        cliente_id=1,
        nome="",
        fantasia=None,
        telefone="123",
        endereco="",
        cidade="",
        cpf_cnpj="123",
    )

    assert sucesso is False
    assert mensagem.startswith("Erro de validação")
    assert resultado is None
    repository.atualizar.assert_not_called()
