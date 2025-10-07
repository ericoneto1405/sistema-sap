"""
Decoradores de Acesso e Segurança
================================

Este módulo contém decoradores centralizados para controle de acesso,
autenticação e validação de permissões no sistema.

Autor: Sistema de Gestão Empresarial
Data: 2024
"""

from functools import wraps
from flask import session, redirect, url_for, request, jsonify, current_app
from datetime import datetime


def login_obrigatorio(f):
    """
    Decorador que verifica se o usuário está logado
    
    Args:
        f: Função a ser decorada
        
    Returns:
        Função decorada que verifica autenticação
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            # Se for uma requisição AJAX ou API, retornar JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
               request.path.startswith('/api/') or \
               request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'error': True,
                    'message': 'Acesso negado. Faça login para continuar.',
                    'type': 'AuthenticationRequired',
                    'timestamp': datetime.now().isoformat()
                }), 401
            
            # Para requisições normais, redirecionar para login
            return redirect(url_for('main.login'))
        
        return f(*args, **kwargs)
    return decorated_function


def permissao_necessaria(permissao):
    """
    Decorador que verifica se o usuário tem a permissão necessária
    
    Args:
        permissao (str): Nome da permissão necessária (ex: 'acesso_clientes')
        
    Returns:
        Decorador que verifica permissão
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Primeiro verificar se está logado
            if 'usuario_id' not in session:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                   request.path.startswith('/api/') or \
                   request.headers.get('Accept') == 'application/json':
                    return jsonify({
                        'error': True,
                        'message': 'Acesso negado. Faça login para continuar.',
                        'type': 'AuthenticationRequired',
                        'timestamp': datetime.now().isoformat()
                    }), 401
                return redirect(url_for('main.login'))
            
            # Verificar se tem a permissão necessária
            # Admin tem acesso a todas as permissões
            if session.get('usuario_tipo') == 'admin':
                return f(*args, **kwargs)

            if not session.get(permissao, False):
                current_app.logger.warning(
                    f"Tentativa de acesso negada: usuário {session.get('usuario_nome', 'desconhecido')} "
                    f"tentou acessar {request.endpoint} sem permissão '{permissao}' "
                    f"(IP: {request.remote_addr})"
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                   request.path.startswith('/api/') or \
                   request.headers.get('Accept') == 'application/json':
                    return jsonify({
                        'error': True,
                        'message': f'Acesso negado. Você não tem permissão para acessar esta funcionalidade.',
                        'type': 'InsufficientPermissions',
                        'permission_required': permissao,
                        'timestamp': datetime.now().isoformat()
                    }), 403
                
                return jsonify({
                    'error': True,
                    'message': f'Acesso negado. Você não tem permissão para acessar esta funcionalidade.',
                    'type': 'InsufficientPermissions',
                    'permission_required': permissao,
                    'timestamp': datetime.now().isoformat()
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_necessario(f):
    """
    Decorador que verifica se o usuário é administrador
    
    Args:
        f: Função a ser decorada
        
    Returns:
        Função decorada que verifica se é admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Primeiro verificar se está logado
        if 'usuario_id' not in session:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
               request.path.startswith('/api/') or \
               request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'error': True,
                    'message': 'Acesso negado. Faça login para continuar.',
                    'type': 'AuthenticationRequired',
                    'timestamp': datetime.now().isoformat()
                }), 401
            return redirect(url_for('main.login'))
        
        # Verificar se é administrador
        if session.get('usuario_tipo') != 'admin':
            current_app.logger.warning(
                f"Tentativa de acesso de não-admin: usuário {session.get('usuario_nome', 'desconhecido')} "
                f"tentou acessar {request.endpoint} (IP: {request.remote_addr})"
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
               request.path.startswith('/api/') or \
               request.headers.get('Accept') == 'application/json':
                return jsonify({
                    'error': True,
                    'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.',
                    'type': 'AdminRequired',
                    'timestamp': datetime.now().isoformat()
                }), 403
            
            return jsonify({
                'error': True,
                'message': 'Acesso negado. Apenas administradores podem acessar esta funcionalidade.',
                'type': 'AdminRequired',
                'timestamp': datetime.now().isoformat()
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function


def validar_metodo_http(metodos_permitidos):
    """
    Decorador que valida o método HTTP da requisição
    
    Args:
        metodos_permitidos (list): Lista de métodos HTTP permitidos
        
    Returns:
        Decorador que valida método HTTP
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method not in metodos_permitidos:
                current_app.logger.warning(
                    f"Método HTTP não permitido: {request.method} para {request.endpoint} "
                    f"(IP: {request.remote_addr})"
                )
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
                   request.path.startswith('/api/') or \
                   request.headers.get('Accept') == 'application/json':
                    return jsonify({
                        'error': True,
                        'message': f'Método {request.method} não permitido para esta rota.',
                        'type': 'MethodNotAllowed',
                        'allowed_methods': metodos_permitidos,
                        'timestamp': datetime.now().isoformat()
                    }), 405
                
                return jsonify({
                    'error': True,
                    'message': f'Método {request.method} não permitido para esta rota.',
                    'type': 'MethodNotAllowed',
                    'allowed_methods': metodos_permitidos,
                    'timestamp': datetime.now().isoformat()
                }), 405
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_acesso(modulo):
    """
    Decorador que registra o acesso a funcionalidades sensíveis
    
    Args:
        modulo (str): Nome do módulo acessado
        
    Returns:
        Decorador que registra acesso
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Registrar acesso
            current_app.logger.info(
                f"Acesso autorizado: usuário {session.get('usuario_nome', 'desconhecido')} "
                f"acessou {request.endpoint} no módulo {modulo} "
                f"(IP: {request.remote_addr})"
            )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Decoradores compostos para facilitar o uso
def login_e_permissao(permissao):
    """
    Decorador composto que verifica login e permissão
    
    Args:
        permissao (str): Nome da permissão necessária
        
    Returns:
        Decorador composto
    """
    def decorator(f):
        @wraps(f)
        @login_obrigatorio
        @permissao_necessaria(permissao)
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def login_e_admin():
    """
    Decorador composto que verifica login e se é admin
    
    Returns:
        Decorador composto
    """
    def decorator(f):
        @wraps(f)
        @login_obrigatorio
        @admin_necessario
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator
