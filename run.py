"""
Script de Desenvolvimento
=========================

Este script é usado APENAS para desenvolvimento local.
Em produção, use wsgi.py com Gunicorn.

Uso:
    python run.py
    
    ou
    
    flask run

Autor: Sistema SAP
Data: Outubro 2025
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Garantir ambiente de desenvolvimento
os.environ['FLASK_ENV'] = 'development'

from meu_app import create_app
from config import DevelopmentConfig

# Criar aplicação com configuração de desenvolvimento
app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Servidor de Desenvolvimento - Sistema SAP")
    print("=" * 60)
    print(f"Ambiente: {app.config.get('ENV', 'development')}")
    print(f"Debug: {app.debug}")
    print(f"URL: http://localhost:{os.getenv('PORT', '5004')}")
    print("=" * 60)
    print("\n⚠️  NÃO USE EM PRODUÇÃO!")
    print("   Para produção, use: gunicorn -w 4 wsgi:app\n")
    
    app.run(
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5004)),
        debug=True,
        use_reloader=True
    )
