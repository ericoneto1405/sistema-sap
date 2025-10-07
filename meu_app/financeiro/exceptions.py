"""
Exceções específicas do módulo financeiro
"""


class FinanceiroException(Exception):
    """Exceção base para o módulo financeiro"""
    pass


class FinanceiroValidationError(FinanceiroException):
    """Erro de validação no módulo financeiro"""
    pass


class PagamentoDuplicadoError(FinanceiroException):
    """Erro quando um pagamento duplicado é detectado"""
    pass


class PedidoNaoEncontradoError(FinanceiroException):
    """Erro quando um pedido não é encontrado"""
    pass


class ValorInvalidoError(FinanceiroValidationError):
    """Erro quando um valor inválido é fornecido"""
    pass


class ComprovanteObrigatorioError(FinanceiroValidationError):
    """Erro quando comprovante é obrigatório mas não fornecido"""
    pass


class ArquivoInvalidoError(FinanceiroValidationError):
    """Erro quando um arquivo inválido é enviado"""
    pass


class OcrProcessingError(FinanceiroException):
    """Erro durante processamento OCR"""
    pass
