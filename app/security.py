"""
Utilitários de segurança centralizados para a aplicação Flask.

Este módulo concentra a inicialização do CSRF, rate limiting e headers
de segurança, expondo instâncias reutilizáveis pelas blueprints.
"""

from flask import current_app, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect, CSRFError

# Instâncias globais compartilhadas
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)
_talisman = None


def init_security(app):
    """
    Configura proteções padrão (CSRF, rate limiting, headers e cookies).
    
    Deve ser chamada uma única vez durante a criação da aplicação.
    """
    configure_session_cookies(app)
    configure_csrf(app)
    configure_rate_limiter(app)
    configure_security_headers(app)


def configure_session_cookies(app):
    """Garante atributos seguros para o cookie de sessão."""
    if app.config.get("SESSION_COOKIE_SECURE") is None:
        app.config["SESSION_COOKIE_SECURE"] = not app.debug
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    same_site_default = "Lax" if app.debug else "Strict"
    app.config.setdefault("SESSION_COOKIE_SAMESITE", same_site_default)


def configure_csrf(app):
    """Inicializa o CSRF global e registra tratadores de erro."""
    csrf.init_app(app)
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        current_app.logger.warning(
            "Falha de CSRF: %s - Rota: %s - IP: %s",
            error.description,
            request.path,
            request.remote_addr,
        )
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'error': True,
                'type': 'CSRFError',
                'message': error.description,
            }), 400
        
        try:
            return render_template(
                'csrf_error.html',
                message="Sua sessão expirou. Atualize a página e tente novamente.",
            ), 400
        except:
            return jsonify({
                'error': True,
                'type': 'CSRFError',
                'message': 'Token CSRF inválido ou expirado.',
            }), 400


def configure_rate_limiter(app):
    """Inicializa o rate limiter respeitando as configurações do app."""
    enabled = app.config.get("RATELIMIT_ENABLED", True)
    default_limits = app.config.get("RATELIMIT_DEFAULT", "200 per day;50 per hour")
    storage_url = app.config.get("RATELIMIT_STORAGE_URL", "memory://")
    
    # Configurar storage antes de init
    limiter.storage_uri = storage_url
    
    # Inicializar com app
    limiter.init_app(app)
    
    # Configurar após init
    limiter.enabled = enabled
    if default_limits:
        app.config["RATELIMIT_DEFAULT"] = default_limits


def configure_security_headers(app):
    """Aplica headers seguros via Flask-Talisman quando habilitado."""
    global _talisman
    
    if not app.config.get("SECURITY_HEADERS_ENABLED"):
        return
    
    csp = app.config.get("CSP_DIRECTIVES", {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'"],
        'style-src': ["'self'", "'unsafe-inline'"],
        'img-src': ["'self'", 'data:', 'https:'],
    })
    
    _talisman = Talisman(
        app,
        content_security_policy=csp,
        force_https=not (app.debug or app.testing),
        strict_transport_security=True,
        frame_options='SAMEORIGIN',
        session_cookie_secure=app.config.get("SESSION_COOKIE_SECURE", True),
    )
    
    app.logger.info('Talisman habilitado - Headers de segurança ativos')


__all__ = ["csrf", "limiter", "init_security"]
