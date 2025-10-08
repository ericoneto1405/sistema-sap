#!/usr/bin/env python3
"""
Script temporário para executar migrations do Alembic
Força o uso do SQLite ignorando DATABASE_URL do sistema
"""
import os
import sys

# Forçar SQLite
os.environ['DATABASE_URL'] = 'sqlite:////Users/ericobrandao/Projects/SAP/instance/sistema.db'

from flask.cli import FlaskGroup
from meu_app import create_app

app = create_app()
cli = FlaskGroup(create_app=lambda: app)

if __name__ == '__main__':
    cli()

