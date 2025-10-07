"""
Tratadores de Erro e Decoradores
===============================

Este módulo contém decoradores e funções para tratamento padronizado
de erros em todo o sistema.

Autor: Sistema de Gestão Empresarial
Data: 2024
"""

import functools
import traceback
from flask import current_app, jsonify, request
from typing import Callable, Any, Tuple, Optional
from .exceptions import (
    SistemaException, ValidationError, BusinessLogicError, DatabaseError,
    AuthenticationError, AuthorizationError, FileProcessingError,
    NotFoundError, DuplicateError, get_user_friendly_message,
    handle_database_error, handle_validation_error, handle_business_logic_error
)


def handle_errors(return_json: bool = False, log_error: bool = True):
    """
    Decorador para tratamento padronizado de erros
    
    Args:
        return_json: Se True, retorna erro em formato JSON
        log_error: Se True, registra o erro no log
        
    Returns:
        Decorador que trata erros automaticamente
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except SistemaException as e:
                # Erro conhecido do sistema
                if log_error:
                    current_app.logger.warning(f"Erro do sistema em {func.__name__}: {e.message}")
                
                if return_json:
                    return jsonify({
                        'success': False,
                        'error': True,
                        'message': e.message,
                        'error_code': e.error_code,
                        'details': e.details
                    }), 400
                else:
                    from flask import flash
                    flash(e.message, 'error')
                    return None
                    
            except Exception as e:
                # Erro não tratado
                error_message = f"Erro inesperado em {func.__name__}: {str(e)}"
                
                if log_error:
                    current_app.logger.error(error_message)
                    current_app.logger.error(traceback.format_exc())
                
                # Converter erro genérico em DatabaseError se for do SQLAlchemy
                if 'sqlalchemy' in str(type(e)).lower():
                    db_error = handle_database_error(e, func.__name__)
                    user_message = get_user_friendly_message(db_error)
                else:
                    user_message = "Ocorreu um erro inesperado. Tente novamente."
                
                if return_json:
                    return jsonify({
                        'success': False,
                        'error': True,
                        'message': user_message,
                        'error_code': 'UNEXPECTED_ERROR',
                        'details': {
                            'function': func.__name__,
                            'original_error': str(e)
                        }
                    }), 500
                else:
                    from flask import flash
                    flash(user_message, 'error')
                    return None
                    
        return wrapper
    return decorator


def validate_required_fields(required_fields: list, data_source: str = 'form'):
    """
    Decorador para validar campos obrigatórios
    
    Args:
        required_fields: Lista de campos obrigatórios
        data_source: Fonte dos dados ('form', 'json', 'args')
        
    Returns:
        Decorador que valida campos obrigatórios
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                # Obter dados baseado na fonte
                if data_source == 'form':
                    data = request.form
                elif data_source == 'json':
                    data = request.get_json() or {}
                elif data_source == 'args':
                    data = request.args
                else:
                    raise ValueError(f"Fonte de dados inválida: {data_source}")
                
                # Validar campos obrigatórios
                missing_fields = []
                for field in required_fields:
                    if not data.get(field):
                        missing_fields.append(field)
                
                if missing_fields:
                    error = ValidationError(
                        message=f"Campos obrigatórios faltando: {', '.join(missing_fields)}",
                        error_code="MISSING_REQUIRED_FIELDS",
                        details={
                            'missing_fields': missing_fields,
                            'function': func.__name__
                        }
                    )
                    raise error
                
                return func(*args, **kwargs)
                
            except SistemaException:
                raise
            except Exception as e:
                current_app.logger.error(f"Erro na validação de campos em {func.__name__}: {str(e)}")
                raise ValidationError(
                    message="Erro na validação dos dados",
                    error_code="VALIDATION_ERROR",
                    details={'function': func.__name__, 'original_error': str(e)}
                )
                
        return wrapper
    return decorator


def require_permissions(permissions: list):
    """
    Decorador para verificar permissões específicas
    
    Args:
        permissions: Lista de permissões necessárias
        
    Returns:
        Decorador que verifica permissões
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from flask import session
            
            # Verificar se usuário está logado
            if 'usuario_id' not in session:
                raise AuthenticationError(
                    message="Usuário não autenticado",
                    error_code="NOT_AUTHENTICATED",
                    details={'function': func.__name__}
                )
            
            # Verificar permissões
            missing_permissions = []
            for permission in permissions:
                if not session.get(permission, False):
                    missing_permissions.append(permission)
            
            if missing_permissions:
                raise AuthorizationError(
                    message=f"Permissões insuficientes: {', '.join(missing_permissions)}",
                    error_code="INSUFFICIENT_PERMISSIONS",
                    details={
                        'required_permissions': permissions,
                        'missing_permissions': missing_permissions,
                        'function': func.__name__
                    }
                )
            
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


def log_activity(activity_type: str, description: str = None):
    """
    Decorador para registrar atividades automaticamente
    
    Args:
        activity_type: Tipo da atividade
        description: Descrição da atividade (opcional)
        
    Returns:
        Decorador que registra atividades
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                result = func(*args, **kwargs)
                
                # Registrar atividade de sucesso
                from .log_atividades.services import LogAtividadesService
                LogAtividadesService.registrar_atividade(
                    tipo_atividade=activity_type,
                    titulo=f"Operação {activity_type}",
                    descricao=description or f"Operação {activity_type} executada com sucesso",
                    modulo=func.__module__.split('.')[-1],
                    dados_extras={
                        'function': func.__name__,
                        'success': True
                    }
                )
                
                return result
                
            except Exception as e:
                # Registrar atividade de erro
                from .log_atividades.services import LogAtividadesService
                LogAtividadesService.registrar_atividade(
                    tipo_atividade=f"{activity_type}_error",
                    titulo=f"Erro em {activity_type}",
                    descricao=f"Erro ao executar {activity_type}: {str(e)}",
                    modulo=func.__module__.split('.')[-1],
                    dados_extras={
                        'function': func.__name__,
                        'success': False,
                        'error': str(e)
                    }
                )
                raise
                
        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorador para tentar novamente em caso de falha
    
    Args:
        max_retries: Número máximo de tentativas
        delay: Delay entre tentativas em segundos
        
    Returns:
        Decorador que tenta novamente em caso de falha
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import time
            
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        current_app.logger.warning(
                            f"Tentativa {attempt + 1} falhou em {func.__name__}: {str(e)}. "
                            f"Tentando novamente em {delay} segundos..."
                        )
                        time.sleep(delay)
                    else:
                        current_app.logger.error(
                            f"Todas as {max_retries + 1} tentativas falharam em {func.__name__}: {str(e)}"
                        )
            
            # Se chegou aqui, todas as tentativas falharam
            raise last_exception
            
        return wrapper
    return decorator


def performance_monitor(threshold_seconds: float = 1.0):
    """
    Decorador para monitorar performance de funções
    
    Args:
        threshold_seconds: Limite em segundos para alerta de performance
        
    Returns:
        Decorador que monitora performance
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import time
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > threshold_seconds:
                    current_app.logger.warning(
                        f"Performance lenta detectada em {func.__name__}: "
                        f"{execution_time:.2f}s (limite: {threshold_seconds}s)"
                    )
                else:
                    current_app.logger.debug(
                        f"Performance OK em {func.__name__}: {execution_time:.2f}s"
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                current_app.logger.error(
                    f"Erro em {func.__name__} após {execution_time:.2f}s: {str(e)}"
                )
                raise
                
        return wrapper
    return decorator
