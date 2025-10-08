"""
Configurações da Aplicação por Ambiente
========================================

Configuração simples e objetiva para Flask App Factory.

Autor: Sistema SAP
Data: Outubro 2025
"""

import os
from datetime import timedelta


class BaseConfig:
    """Configuração base compartilhada entre todos os ambientes"""
    
    # Diretório base
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Segurança - SECRET_KEY obrigatória
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-insecure-change-me")
    
    # Banco de dados
    # SQLite requer /// para caminho relativo ou //// para caminho absoluto
    # FIX: Ignorar DATABASE_URL se tiver valores de exemplo inválidos
    _db_url = os.getenv("DATABASE_URL", "")
    if _db_url and ("usuario" in _db_url or "senha" in _db_url or "porta" in _db_url or "host" in _db_url):
        # DATABASE_URL tem valores de exemplo, ignorar
        _db_url = ""
    
    SQLALCHEMY_DATABASE_URI = _db_url or f"sqlite:///{os.path.abspath(os.path.join(BASE_DIR, 'instance', 'sistema.db'))}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # Sessão
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    
    # Uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Logging
    LOG_DIR = os.path.join(BASE_DIR, 'instance', 'logs')
    LOG_LEVEL = 'INFO'
    
    # CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    WTF_CSRF_SSL_STRICT = False
    
    # Cache (FASE 8)
    CACHE_TYPE = 'SimpleCache'  # SimpleCache para dev, Redis para prod
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    CACHE_KEY_PREFIX = 'flask_cache_'
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "200 per hour"
    
    # Security Headers
    SECURITY_HEADERS_ENABLED = False
    
    # Google Vision (OCR)
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    OCR_MONTHLY_LIMIT = int(os.getenv('OCR_MONTHLY_LIMIT', '1000'))
    OCR_ENFORCE_LIMIT = os.getenv('OCR_ENFORCE_LIMIT', 'True').lower() == 'true'


class DevelopmentConfig(BaseConfig):
    """Configuração para desenvolvimento"""
    
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    LOG_LEVEL = 'DEBUG'
    RATELIMIT_DEFAULT = "500 per hour"
    
    # CSP mais permissivo para desenvolvimento (permite CDNs e scripts inline)
    CSP_DIRECTIVES = {
        "default-src": ["'self'"],
        "script-src": [
            "'self'", 
            "'unsafe-inline'",  # Permite scripts inline em dev
            "https://cdn.jsdelivr.net",
            "https://code.jquery.com",
            "https://cdnjs.cloudflare.com"
        ],
        "style-src": [
            "'self'", 
            "'unsafe-inline'",
            "https://cdn.jsdelivr.net",
            "https://fonts.googleapis.com"
        ],
        "img-src": ["'self'", "data:", "https:"],
        "font-src": ["'self'", "data:", "https://cdn.jsdelivr.net", "https://fonts.gstatic.com"],
        "connect-src": ["'self'"],
    }


class TestingConfig(BaseConfig):
    """Configuração para testes"""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    RATELIMIT_ENABLED = False
    CACHE_TYPE = 'NullCache'
    OCR_ENFORCE_LIMIT = False


class ProductionConfig(BaseConfig):
    """Configuração para produção"""
    
    DEBUG = False
    SESSION_COOKIE_SAMESITE = "Strict"
    WTF_CSRF_SSL_STRICT = True
    LOG_LEVEL = 'INFO'
    
    # Validação estrita em produção
    @classmethod
    def init_app(cls, app):
        """Validações adicionais para produção"""
        if cls.SECRET_KEY == "dev-key-insecure-change-me":
            raise RuntimeError("SECRET_KEY padrão detectada em produção! Configure SECRET_KEY.")
        if 'sqlite' in cls.SQLALCHEMY_DATABASE_URI.lower():
            import warnings
            warnings.warn("SQLite em produção não é recomendado. Use PostgreSQL ou MySQL.")
    
    # Headers de segurança habilitados em produção
    SECURITY_HEADERS_ENABLED = True
    CSP_DIRECTIVES = {
        'default-src': ["'self'"],
        'script-src': ["'self'"],
        'style-src': ["'self'", "'unsafe-inline'"],
        'img-src': ["'self'", 'data:'],
        'font-src': ["'self'", 'data:'],
        'connect-src': ["'self'"],
        'object-src': ["'none'"],
        'base-uri': ["'self'"],
        'frame-ancestors': ["'none'"],
    }
    
    # Cache Redis (FASE 8)
    CACHE_TYPE = 'redis' if os.getenv('REDIS_URL') else 'SimpleCache'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_OPTIONS = {
        'socket_connect_timeout': 2,
        'socket_timeout': 2,
        'connection_pool_kwargs': {'max_connections': 50}
    }
    
    # Rate Limiting com Redis
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')


# Mapeamento de ambientes
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Retorna a configuração apropriada baseada no ambiente
    
    Args:
        env: Nome do ambiente ou None para auto-detectar via FLASK_ENV
    
    Returns:
        Classe de configuração apropriada
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    
    return config.get(env, config['default'])
