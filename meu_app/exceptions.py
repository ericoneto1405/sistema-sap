"""
Exceções Personalizadas do Sistema
==================================

Este módulo contém exceções específicas para diferentes tipos de erros
no sistema, permitindo tratamento mais granular e mensagens mais claras.

Autor: Sistema de Gestão Empresarial
Data: 2024
"""


class SistemaException(Exception):
    """Exceção base para todos os erros do sistema"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(SistemaException):
    """Erro de validação de dados"""
    pass


class BusinessLogicError(SistemaException):
    """Erro de lógica de negócio"""
    pass


class DatabaseError(SistemaException):
    """Erro de banco de dados"""
    pass


class AuthenticationError(SistemaException):
    """Erro de autenticação"""
    pass


class AuthorizationError(SistemaException):
    """Erro de autorização/permissão"""
    pass


class FileProcessingError(SistemaException):
    """Erro no processamento de arquivos"""
    pass


class ImportError(SistemaException):
    """Erro na importação de dados"""
    pass


class ExportError(SistemaException):
    """Erro na exportação de dados"""
    pass


class NotFoundError(SistemaException):
    """Recurso não encontrado"""
    pass


class DuplicateError(SistemaException):
    """Recurso duplicado"""
    pass


class IntegrityError(SistemaException):
    """Erro de integridade de dados"""
    pass


class ConfigurationError(SistemaException):
    """Erro de configuração do sistema"""
    pass


class ExternalServiceError(SistemaException):
    """Erro em serviço externo"""
    pass


class PerformanceError(SistemaException):
    """Erro de performance"""
    pass


# Exceções específicas para diferentes módulos

class ClienteError(BusinessLogicError):
    """Erro específico do módulo de clientes"""
    pass


class ProdutoError(BusinessLogicError):
    """Erro específico do módulo de produtos"""
    pass


class PedidoError(BusinessLogicError):
    """Erro específico do módulo de pedidos"""
    pass


class EstoqueError(BusinessLogicError):
    """Erro específico do módulo de estoque"""
    pass


class FinanceiroError(BusinessLogicError):
    """Erro específico do módulo financeiro"""
    pass


class LogisticaError(BusinessLogicError):
    """Erro específico do módulo de logística"""
    pass


class UsuarioError(BusinessLogicError):
    """Erro específico do módulo de usuários"""
    pass


class ApuracaoError(BusinessLogicError):
    """Erro específico do módulo de apuração"""
    pass


# Funções auxiliares para tratamento de erros

def handle_database_error(error, context: str = ""):
    """
    Trata erros de banco de dados de forma padronizada
    
    Args:
        error: Exceção do banco de dados
        context: Contexto onde ocorreu o erro
        
    Returns:
        DatabaseError: Exceção tratada
    """
    from sqlalchemy.exc import IntegrityError as SQLIntegrityError
    from sqlalchemy.exc import OperationalError
    from sqlalchemy.exc import DataError
    
    if isinstance(error, SQLIntegrityError):
        return DatabaseError(
            message="Erro de integridade de dados",
            error_code="INTEGRITY_ERROR",
            details={
                "context": context,
                "original_error": str(error),
                "suggestion": "Verifique se os dados estão corretos e não violam restrições"
            }
        )
    elif isinstance(error, OperationalError):
        return DatabaseError(
            message="Erro de operação no banco de dados",
            error_code="OPERATIONAL_ERROR",
            details={
                "context": context,
                "original_error": str(error),
                "suggestion": "Verifique a conexão com o banco de dados"
            }
        )
    elif isinstance(error, DataError):
        return DatabaseError(
            message="Erro de dados no banco",
            error_code="DATA_ERROR",
            details={
                "context": context,
                "original_error": str(error),
                "suggestion": "Verifique os tipos e formatos dos dados"
            }
        )
    else:
        return DatabaseError(
            message="Erro desconhecido no banco de dados",
            error_code="UNKNOWN_DATABASE_ERROR",
            details={
                "context": context,
                "original_error": str(error),
                "suggestion": "Contate o administrador do sistema"
            }
        )


def handle_validation_error(field: str, value, rule: str, context: str = ""):
    """
    Trata erros de validação de forma padronizada
    
    Args:
        field: Campo que falhou na validação
        value: Valor que causou o erro
        rule: Regra de validação que falhou
        context: Contexto onde ocorreu o erro
        
    Returns:
        ValidationError: Exceção tratada
    """
    return ValidationError(
        message=f"Erro de validação no campo '{field}'",
        error_code="VALIDATION_ERROR",
        details={
            "field": field,
            "value": str(value),
            "rule": rule,
            "context": context,
            "suggestion": f"Verifique se o campo '{field}' atende aos requisitos"
        }
    )


def handle_business_logic_error(operation: str, reason: str, context: str = ""):
    """
    Trata erros de lógica de negócio de forma padronizada
    
    Args:
        operation: Operação que falhou
        reason: Motivo da falha
        context: Contexto onde ocorreu o erro
        
    Returns:
        BusinessLogicError: Exceção tratada
    """
    return BusinessLogicError(
        message=f"Erro na operação '{operation}': {reason}",
        error_code="BUSINESS_LOGIC_ERROR",
        details={
            "operation": operation,
            "reason": reason,
            "context": context,
            "suggestion": "Verifique as regras de negócio e tente novamente"
        }
    )


def handle_file_error(filename: str, operation: str, reason: str, context: str = ""):
    """
    Trata erros de arquivo de forma padronizada
    
    Args:
        filename: Nome do arquivo
        operation: Operação que falhou
        reason: Motivo da falha
        context: Contexto onde ocorreu o erro
        
    Returns:
        FileProcessingError: Exceção tratada
    """
    return FileProcessingError(
        message=f"Erro no arquivo '{filename}': {reason}",
        error_code="FILE_ERROR",
        details={
            "filename": filename,
            "operation": operation,
            "reason": reason,
            "context": context,
            "suggestion": "Verifique o arquivo e tente novamente"
        }
    )


def get_user_friendly_message(error: Exception) -> str:
    """
    Retorna uma mensagem amigável para o usuário baseada no tipo de erro
    
    Args:
        error: Exceção que ocorreu
        
    Returns:
        str: Mensagem amigável para o usuário
    """
    if isinstance(error, ValidationError):
        return f"Erro de validação: {error.message}"
    elif isinstance(error, BusinessLogicError):
        return f"Erro de negócio: {error.message}"
    elif isinstance(error, DatabaseError):
        return "Erro interno do sistema. Tente novamente em alguns instantes."
    elif isinstance(error, AuthenticationError):
        return "Erro de autenticação. Verifique suas credenciais."
    elif isinstance(error, AuthorizationError):
        return "Você não tem permissão para realizar esta operação."
    elif isinstance(error, FileProcessingError):
        return f"Erro no arquivo: {error.message}"
    elif isinstance(error, NotFoundError):
        return "Recurso não encontrado."
    elif isinstance(error, DuplicateError):
        return "Este recurso já existe."
    else:
        return "Ocorreu um erro inesperado. Tente novamente ou contate o administrador."
