"""
WSGI Entry Point para Produção
===============================

Este arquivo é usado para servir a aplicação em produção
usando servidores WSGI como Gunicorn ou uWSGI.

Uso com Gunicorn:
    gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

Uso com uWSGI:
    uwsgi --http :8000 --wsgi-file wsgi.py --callable app

Autor: Sistema SAP
Data: Outubro 2025
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Forçar ambiente de produção
os.environ['FLASK_ENV'] = 'production'

from meu_app import create_app
from config import ProductionConfig

# Criar aplicação com configuração de produção
app = create_app(ProductionConfig)

if __name__ == "__main__":
    # Fallback para desenvolvimento direto
    # NÃO usar em produção real
    print("=" * 60)
    print("AVISO: Executando wsgi.py diretamente")
    print("Em produção, use: gunicorn -w 4 wsgi:app")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8000)
