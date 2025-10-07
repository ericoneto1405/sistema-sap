"""
Aplicação Flask - Sistema SAP
==============================

App Factory pattern com suporte a múltiplos ambientes e extensões.

Autor: Sistema SAP
Data: Outubro 2025
"""

import logging
import os
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar extensões (sem app ainda)
db = SQLAlchemy()
csrf = CSRFProtect()
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
talisman = None  # Será inicializado condicionalmente


def create_app(config_class=None):
    """
    Função fábrica para criar a aplicação Flask
    
    Args:
        config_class: Classe de configuração a ser usada.
                     Se None, usa FLASK_ENV para determinar.
    
    Returns:
        Flask: Instância configurada da aplicação
    """
    app = Flask(__name__)
    
    # Carregar configuração
    if config_class is None:
        from config import get_config
        config_class = get_config()
    
    app.config.from_object(config_class)
    
    # Inicializar extensões com a aplicação
    initialize_extensions(app)
    
    # Configurar logging
    setup_logging(app)
    
    # Registrar error handlers
    register_error_handlers(app)
    
    # Registrar filtros personalizados
    register_custom_filters(app)
    
    # Registrar blueprints
    register_blueprints(app)
    
    # Warm-up do OCR (opcional)
    warmup_ocr(app)
    
    # Log de inicialização
    app.logger.info('=' * 60)
    app.logger.info(f'Aplicação SAP iniciada')
    app.logger.info(f'Ambiente: {app.config.get("ENV", "development")}')
    app.logger.info(f'Debug: {app.debug}')
    app.logger.info(f'Database: {app.config["SQLALCHEMY_DATABASE_URI"][:50]}...')
    app.logger.info('=' * 60)
    
    return app


def initialize_extensions(app):
    """Inicializa todas as extensões Flask"""
    
    # Database
    db.init_app(app)
    
    # CSRF Protection
    csrf.init_app(app)
    
    # Cache
    cache.init_app(app)
    
    # Rate Limiting
    limiter.init_app(app)
    
    # Security Headers (apenas em produção)
    if app.config.get('SECURITY_HEADERS_ENABLED'):
        global talisman
        csp = app.config.get('CSP_DIRECTIVES', {})
        talisman = Talisman(
            app,
            force_https=True,
            strict_transport_security=True,
            content_security_policy=csp,
            content_security_policy_nonce_in=['script-src'],
            feature_policy={
                'geolocation': "'none'",
                'camera': "'none'",
                'microphone': "'none'",
            }
        )
        app.logger.info('Talisman habilitado - Headers de segurança ativos')


def setup_logging(app):
    """Configura o sistema de logging estruturado"""
    
    # Criar pasta de logs
    log_dir = app.config.get('LOG_DIR')
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'app.log') if log_dir else 'app.log'
    
    # Configurar formato
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Handler para arquivo com rotação
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=app.config.get('LOG_MAX_BYTES', 10 * 1024 * 1024),
        backupCount=app.config.get('LOG_BACKUP_COUNT', 5)
    )
    file_handler.setFormatter(formatter)
    
    # Definir nível de log
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    file_handler.setLevel(log_level)
    
    # Handler para console (apenas em desenvolvimento)
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(log_level)


def register_error_handlers(app):
    """Registra manipuladores de erro globais"""
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Manipulador global de exceções"""
        # Log detalhado
        app.logger.error(f'Erro não tratado: {str(e)}')
        app.logger.error(f'Traceback: {traceback.format_exc()}')
        app.logger.error(f'URL: {request.url}')
        app.logger.error(f'Método: {request.method}')
        app.logger.error(f'IP: {request.remote_addr}')
        
        # Retornar resposta JSON
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'error': True,
                'message': 'Erro interno do servidor' if not app.debug else str(e),
                'type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }), 500
        
        return jsonify({
            'error': True,
            'message': 'Ocorreu um erro inesperado. Por favor, tente novamente.',
            'type': 'InternalServerError',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Manipulador para erros 404"""
        app.logger.warning(f'Página não encontrada: {request.url}')
        
        return jsonify({
            'error': True,
            'message': 'Recurso não encontrado',
            'type': 'NotFound',
            'timestamp': datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Manipulador para erros 403"""
        app.logger.warning(f'Acesso negado: {request.url} - IP: {request.remote_addr}')
        
        return jsonify({
            'error': True,
            'message': 'Acesso negado',
            'type': 'Forbidden',
            'timestamp': datetime.now().isoformat()
        }), 403
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Manipulador para rate limit excedido"""
        app.logger.warning(f'Rate limit excedido: {request.url} - IP: {request.remote_addr}')
        
        return jsonify({
            'error': True,
            'message': 'Muitas requisições. Tente novamente mais tarde.',
            'type': 'RateLimitExceeded',
            'timestamp': datetime.now().isoformat()
        }), 429


def register_custom_filters(app):
    """Registra filtros personalizados para os templates"""
    
    @app.template_filter('currency_brl')
    def currency_brl_filter(value):
        """Filtro para formatação de moeda brasileira"""
        if value is None or value == '':
            return 'R$ 0,00'
        
        try:
            if isinstance(value, str):
                value = float(value.replace(',', '.'))
            
            formatted = "{:,.2f}".format(float(value))
            formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
            
            return f'R$ {formatted}'
        except (ValueError, TypeError):
            return 'R$ 0,00'
    
    @app.template_filter('number_brl')
    def number_brl_filter(value):
        """Filtro para formatação de números no padrão brasileiro"""
        if value is None or value == '':
            return '0,00'
        
        try:
            if isinstance(value, str):
                value = float(value.replace(',', '.'))
            
            formatted = "{:,.2f}".format(float(value))
            formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
            
            return formatted
        except (ValueError, TypeError):
            return '0,00'


def register_blueprints(app):
    """Registra todos os blueprints da aplicação"""
    
    # Blueprint principal
    from . import routes
    app.register_blueprint(routes.bp)
    
    # Blueprints de domínio
    from .produtos import produtos_bp
    from .clientes import clientes_bp
    from .pedidos import pedidos_bp
    from .usuarios import usuarios_bp
    from .estoques import estoques_bp
    from .financeiro import financeiro_bp
    from .coletas import coletas_bp
    from .apuracao import apuracao_bp
    from .log_atividades import log_atividades_bp
    from .vendedor import vendedor_bp
    
    app.register_blueprint(produtos_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(estoques_bp)
    app.register_blueprint(financeiro_bp)
    app.register_blueprint(coletas_bp)
    app.register_blueprint(apuracao_bp)
    app.register_blueprint(log_atividades_bp)
    app.register_blueprint(vendedor_bp)
    
    app.logger.info(f'Blueprints registrados: {len(app.blueprints)}')


def warmup_ocr(app):
    """Warm-up opcional do OCR para reduzir latência"""
    try:
        from .financeiro.config import FinanceiroConfig
        if getattr(FinanceiroConfig, 'OCR_WARMUP', False):
            from .financeiro.ocr_service import OcrService
            OcrService._get_reader()
            app.logger.info('OCR warm-up concluído')
    except Exception as e:
        app.logger.warning(f'OCR warm-up falhou: {e}')
