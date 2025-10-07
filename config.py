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
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'sistema.db')}")
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
    
    # Cache
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Rate Limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    
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
    RATELIMIT_DEFAULT = "1000 per day;200 per hour"


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
        'script-src': ["'self'", "'unsafe-inline'"],
        'style-src': ["'self'", "'unsafe-inline'"],
        'img-src': ["'self'", 'data:', 'https:'],
        'font-src': ["'self'", 'data:'],
        'connect-src': ["'self'"],
        'frame-ancestors': ["'none'"],
    }
    
    # Cache Redis
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
    CACHE_REDIS_URL = os.getenv('REDIS_URL')
    
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
