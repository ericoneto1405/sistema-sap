from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import os
import logging
from logging.handlers import RotatingFileHandler
import traceback
from datetime import datetime
from dotenv import load_dotenv

# Inicializar extensões
db = SQLAlchemy()

def create_app():
    """
    Função fábrica para criar a aplicação Flask
    """
    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()
    
    app = Flask(__name__)
    
    # Configuração do banco de dados
    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "sistema.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuração de segurança - SECRET_KEY agora vem de variável de ambiente
    secret_key = os.environ.get('SECRET_KEY')
    # if not secret_key:
    secret_key = "gerpedplus_default_secret_key_2024_secure"
    app.config['SECRET_KEY'] = secret_key
    
    # Configurar logging estruturado
    setup_logging(app, basedir)
    
    # Inicializar extensões com a aplicação
    db.init_app(app)
    
    # Registrar error handlers
    register_error_handlers(app)
    
    # Registrar filtros personalizados
    register_custom_filters(app)
    
    # Importar e registrar as rotas do app.py original
    from . import routes
    app.register_blueprint(routes.bp)
    
    # Registrar blueprint de produtos
    from .produtos import produtos_bp
    app.register_blueprint(produtos_bp)
    
    # Registrar blueprint de clientes
    from .clientes import clientes_bp
    app.register_blueprint(clientes_bp)
    
    # Registrar blueprint de pedidos
    from .pedidos import pedidos_bp
    app.register_blueprint(pedidos_bp)
    
    # Registrar blueprint de usuários
    from .usuarios import usuarios_bp
    app.register_blueprint(usuarios_bp)
    
    # Registrar blueprint de estoques
    from .estoques import estoques_bp
    app.register_blueprint(estoques_bp)
    
    # Registrar blueprint de financeiro
    from .financeiro import financeiro_bp
    app.register_blueprint(financeiro_bp)
    
    # Registrar blueprint de logística (TEMPORARIAMENTE COMENTADO PARA RECONSTRUÇÃO)
    # from .logistica import logistica_bp
    # app.register_blueprint(logistica_bp)
    
    # Registrar blueprint de coletas (NOVO MÓDULO)
    from .coletas import coletas_bp
    app.register_blueprint(coletas_bp)
    
    # Registrar blueprint de apuração
    from .apuracao import apuracao_bp
    app.register_blueprint(apuracao_bp)
    
    # Registrar blueprint de log de atividades
    from .log_atividades import log_atividades_bp
    app.register_blueprint(log_atividades_bp)
    # Registrar blueprint de vendedor
    from .vendedor import vendedor_bp
    app.register_blueprint(vendedor_bp)
    
    # Warm-up opcional do OCR para reduzir latência da 1ª chamada
    try:
        from .financeiro.config import FinanceiroConfig
        if getattr(FinanceiroConfig, 'OCR_WARMUP', False):
            from .financeiro.ocr_service import OcrService
            OcrService._get_reader()
    except Exception:
        pass
    
    return app

def setup_logging(app, basedir):
    """
    Configura o sistema de logging estruturado
    """
    # Criar pasta de logs se não existir
    log_dir = os.path.join(basedir, 'instance', 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'app.log')
    
    # Configurar formato do log
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Handler para arquivo com rotação (máximo 10MB por arquivo, manter 5 arquivos)
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Handler para console (apenas em desenvolvimento)
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # Log de inicialização com informações do sistema
    app.logger.info('Aplicação iniciada')
    app.logger.info(f'Modo debug: {app.debug}')
    app.logger.info(f'Banco de dados: {app.config["SQLALCHEMY_DATABASE_URI"]}')
    app.logger.info(f'Diretório de logs: {log_dir}')

def register_error_handlers(app):
    """
    Registra os manipuladores de erro globais
    """
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """
        Manipulador global de exceções não tratadas
        Retorna sempre JSON para evitar erros de sintaxe no frontend
        """
        # Log detalhado do erro
        app.logger.error(f'Erro não tratado: {str(e)}')
        app.logger.error(f'Traceback: {traceback.format_exc()}')
        app.logger.error(f'URL: {request.url}')
        app.logger.error(f'Método: {request.method}')
        app.logger.error(f'IP: {request.remote_addr}')
        
        # Se for uma requisição AJAX ou API, retornar JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
           request.path.startswith('/api/') or \
           request.headers.get('Accept') == 'application/json':
            
            return jsonify({
                'error': True,
                'message': 'Erro interno do servidor',
                'type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Para requisições normais, retornar página de erro amigável
        return jsonify({
            'error': True,
            'message': 'Ocorreu um erro inesperado. Por favor, tente novamente.',
            'type': 'InternalServerError',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    @app.errorhandler(404)
    def not_found_error(error):
        """
        Manipulador para erros 404
        """
        app.logger.warning(f'Página não encontrada: {request.url}')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
           request.path.startswith('/api/'):
            
            return jsonify({
                'error': True,
                'message': 'Recurso não encontrado',
                'type': 'NotFound',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        return jsonify({
            'error': True,
            'message': 'Página não encontrada',
            'type': 'NotFound',
            'timestamp': datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """
        Manipulador para erros 403 (acesso negado)
        """
        app.logger.warning(f'Acesso negado: {request.url} - IP: {request.remote_addr}')
        
        return jsonify({
            'error': True,
            'message': 'Acesso negado',
            'type': 'Forbidden',
            'timestamp': datetime.now().isoformat()
        }), 403

def register_custom_filters(app):
    """
    Registra filtros personalizados para os templates
    """
    @app.template_filter('currency_brl')
    def currency_brl_filter(value):
        """
        Filtro para formatação de moeda brasileira
        Converte valor numérico para formato R$ 10.000,00
        """
        if value is None or value == '':
            return 'R$ 0,00'
        
        try:
            # Converte para float se for string
            if isinstance(value, str):
                value = float(value.replace(',', '.'))
            
            # Formata usando locale brasileiro
            formatted = "{:,.2f}".format(float(value))
            # Troca separadores para padrão brasileiro
            formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
            
            return f'R$ {formatted}'
        except (ValueError, TypeError):
            return 'R$ 0,00'
    
    @app.template_filter('number_brl')
    def number_brl_filter(value):
        """
        Filtro para formatação de números no padrão brasileiro (sem símbolo de moeda)
        """
        if value is None or value == '':
            return '0,00'
        
        try:
            # Converte para float se for string
            if isinstance(value, str):
                value = float(value.replace(',', '.'))
            
            # Formata usando locale brasileiro
            formatted = "{:,.2f}".format(float(value))
            # Troca separadores para padrão brasileiro
            formatted = formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
            
            return formatted
        except (ValueError, TypeError):
            return '0,00'
