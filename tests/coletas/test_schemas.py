"""
Testes unitários para schemas Pydantic do módulo coletas
"""
import pytest
from pydantic import ValidationError
from meu_app.coletas.schemas import (
    ItemColetaSchema, ColetaRequestSchema, ColetaResult, ColetaResponseSchema
)


class TestItemColetaSchema:
    """Testes para ItemColetaSchema"""

    def test_item_coleta_valido(self):
        """Testa criação de item de coleta válido"""
        item = ItemColetaSchema(
            item_id=1,
            quantidade=5
        )
        
        assert item.item_id == 1
        assert item.quantidade == 5

    def test_item_coleta_quantidade_zero(self):
        """Testa item com quantidade zero (inválido)"""
        with pytest.raises(ValidationError) as exc_info:
            ItemColetaSchema(
                item_id=1,
                quantidade=0
            )
        
        assert "Quantidade deve ser maior que zero" in str(exc_info.value)

    def test_item_coleta_quantidade_negativa(self):
        """Testa item com quantidade negativa (inválido)"""
        with pytest.raises(ValidationError) as exc_info:
            ItemColetaSchema(
                item_id=1,
                quantidade=-1
            )
        
        assert "Quantidade deve ser maior que zero" in str(exc_info.value)

    def test_item_coleta_item_id_zero(self):
        """Testa item com ID zero (inválido)"""
        with pytest.raises(ValidationError):
            ItemColetaSchema(
                item_id=0,
                quantidade=5
            )


class TestColetaRequestSchema:
    """Testes para ColetaRequestSchema"""

    def test_coleta_request_valida(self):
        """Testa criação de requisição de coleta válida"""
        request = ColetaRequestSchema(
            pedido_id=1,
            responsavel_coleta_id=1,
            nome_retirada="João Silva",
            documento_retirada="12345678901",
            itens_coleta=[
                ItemColetaSchema(item_id=1, quantidade=2),
                ItemColetaSchema(item_id=2, quantidade=1)
            ]
        )
        
        assert request.pedido_id == 1
        assert request.nome_retirada == "João Silva"
        assert len(request.itens_coleta) == 2

    def test_coleta_request_nome_vazio(self):
        """Testa requisição com nome vazio (inválido)"""
        with pytest.raises(ValidationError) as exc_info:
            ColetaRequestSchema(
                pedido_id=1,
                responsavel_coleta_id=1,
                nome_retirada="",  # Nome vazio
                documento_retirada="12345678901",
                itens_coleta=[ItemColetaSchema(item_id=1, quantidade=2)]
            )
        
        assert "Nome da retirada é obrigatório" in str(exc_info.value)

    def test_coleta_request_documento_vazio(self):
        """Testa requisição com documento vazio (inválido)"""
        with pytest.raises(ValidationError) as exc_info:
            ColetaRequestSchema(
                pedido_id=1,
                responsavel_coleta_id=1,
                nome_retirada="João Silva",
                documento_retirada="",  # Documento vazio
                itens_coleta=[ItemColetaSchema(item_id=1, quantidade=2)]
            )
        
        assert "Documento da retirada é obrigatório" in str(exc_info.value)

    def test_coleta_request_sem_itens(self):
        """Testa requisição sem itens (inválido)"""
        with pytest.raises(ValidationError):
            ColetaRequestSchema(
                pedido_id=1,
                responsavel_coleta_id=1,
                nome_retirada="João Silva",
                documento_retirada="12345678901",
                itens_coleta=[]  # Lista vazia
            )

    def test_coleta_request_nome_espacos(self):
        """Testa requisição com nome apenas com espaços (inválido)"""
        with pytest.raises(ValidationError) as exc_info:
            ColetaRequestSchema(
                pedido_id=1,
                responsavel_coleta_id=1,
                nome_retirada="   ",  # Apenas espaços
                documento_retirada="12345678901",
                itens_coleta=[ItemColetaSchema(item_id=1, quantidade=2)]
            )
        
        assert "Nome da retirada é obrigatório" in str(exc_info.value)

    def test_coleta_request_observacoes_opcional(self):
        """Testa requisição com observações opcionais"""
        request = ColetaRequestSchema(
            pedido_id=1,
            responsavel_coleta_id=1,
            nome_retirada="João Silva",
            documento_retirada="12345678901",
            itens_coleta=[ItemColetaSchema(item_id=1, quantidade=2)],
            observacoes="Observação teste"
        )
        
        assert request.observacoes == "Observação teste"

    def test_coleta_request_observacoes_none(self):
        """Testa requisição sem observações (None)"""
        request = ColetaRequestSchema(
            pedido_id=1,
            responsavel_coleta_id=1,
            nome_retirada="João Silva",
            documento_retirada="12345678901",
            itens_coleta=[ItemColetaSchema(item_id=1, quantidade=2)]
        )
        
        assert request.observacoes is None


class TestColetaResult:
    """Testes para ColetaResult"""

    def test_coleta_result_sucesso(self):
        """Testa resultado de sucesso"""
        resultado = ColetaResult(
            sucesso=True,
            dados={"id": 1, "status": "processada"},
            mensagem="Coleta processada com sucesso"
        )
        
        assert resultado.sucesso is True
        assert resultado.dados["id"] == 1
        assert "sucesso" in resultado.mensagem

    def test_coleta_result_erro(self):
        """Testa resultado de erro"""
        resultado = ColetaResult(
            sucesso=False,
            dados=None,
            mensagem="Erro ao processar coleta"
        )
        
        assert resultado.sucesso is False
        assert resultado.dados is None
        assert "erro" in resultado.mensagem.lower()

    def test_coleta_result_dados_none(self):
        """Testa resultado com dados None"""
        resultado = ColetaResult(
            sucesso=True,
            dados=None,
            mensagem="Operação concluída"
        )
        
        assert resultado.sucesso is True
        assert resultado.dados is None


class TestColetaResponseSchema:
    """Testes para ColetaResponseSchema"""

    def test_coleta_response_valida(self):
        """Testa criação de resposta de coleta válida"""
        from datetime import datetime
        
        response = ColetaResponseSchema(
            id=1,
            pedido_id=1,
            responsavel_coleta_id=1,
            nome_retirada="João Silva",
            documento_retirada="12345678901",
            status="PROCESSADA",
            data_coleta=datetime.now(),
            observacoes="Observação teste"
        )
        
        assert response.id == 1
        assert response.pedido_id == 1
        assert response.nome_retirada == "João Silva"
        assert response.status == "PROCESSADA"

    def test_coleta_response_sem_observacoes(self):
        """Testa resposta sem observações"""
        from datetime import datetime
        
        response = ColetaResponseSchema(
            id=1,
            pedido_id=1,
            responsavel_coleta_id=1,
            nome_retirada="João Silva",
            documento_retirada="12345678901",
            status="PROCESSADA",
            data_coleta=datetime.now()
        )
        
        assert response.observacoes is None

    def test_coleta_response_id_zero(self):
        """Testa resposta com ID zero (inválido)"""
        from datetime import datetime
        
        with pytest.raises(ValidationError):
            ColetaResponseSchema(
                id=0,  # ID zero
                pedido_id=1,
                responsavel_coleta_id=1,
                nome_retirada="João Silva",
                documento_retirada="12345678901",
                status="PROCESSADA",
                data_coleta=datetime.now()
            )
