#!/bin/bash
# Script para testar a aplicação em ambiente limpo

# Remover DATABASE_URL do ambiente
unset DATABASE_URL

# Ativar venv
source venv/bin/activate

# Testar importação
echo "🧪 Testando importação..."
python3 -c "
from meu_app import create_app
from config import DevelopmentConfig
app = create_app(DevelopmentConfig)
print('=' * 60)
print('✅ APP INICIALIZADA COM SUCESSO!')
print('=' * 60)
print(f'Database: {app.config[\"SQLALCHEMY_DATABASE_URI\"]}')
print(f'Debug: {app.debug}')
print(f'Blueprints: {len(app.blueprints)}')
print('=' * 60)
"
