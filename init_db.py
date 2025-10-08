#!/usr/bin/env python3
"""
Script de inicialização do banco de dados.

Cria as tabelas necessárias e, opcionalmente, um usuário administrador
com base em variáveis de ambiente. Não são utilizadas credenciais padrão.
"""

import os

from meu_app import create_app, db
from meu_app.models import Usuario

ADMIN_USERNAME_ENV = "INITIAL_ADMIN_USERNAME"
ADMIN_PASSWORD_ENV = "INITIAL_ADMIN_PASSWORD"


def init_database():
    """Inicializa o banco de dados com tabelas e usuário admin opcional."""
    app = create_app()

    with app.app_context():
        print("Criando tabelas do banco de dados...")
        db.create_all()
        print("✓ Tabelas criadas com sucesso!")

        _create_initial_admin_if_configured()

        print("Banco de dados inicializado com sucesso!")
        print(
            "Configure as credenciais iniciais via variáveis de ambiente "
            f"{ADMIN_USERNAME_ENV}/{ADMIN_PASSWORD_ENV} ou crie usuários pelo painel."
        )
        print("Execute 'python3 run.py' para iniciar a aplicação.")


def _create_initial_admin_if_configured() -> None:
    """Cria um administrador inicial se as variáveis de ambiente estiverem presentes."""
    username = os.environ.get(ADMIN_USERNAME_ENV)
    password = os.environ.get(ADMIN_PASSWORD_ENV)

    if not username or not password:
        print(
            f"Nenhum usuário administrador criado automaticamente. "
            f"Defina {ADMIN_USERNAME_ENV} e {ADMIN_PASSWORD_ENV} para criar um."
        )
        return

    existente = Usuario.query.filter_by(nome=username).first()
    if existente:
        print(f"Usuário administrador '{username}' já existe. Nenhuma alteração realizada.")
        return

    print(f"Criando usuário administrador '{username}' a partir das variáveis de ambiente...")
    admin = Usuario(
        nome=username,
        senha_hash="",
        tipo="admin",
        acesso_clientes=True,
        acesso_produtos=True,
        acesso_pedidos=True,
        acesso_financeiro=True,
        acesso_logistica=True,
    )
    admin.set_senha(password)
    db.session.add(admin)
    db.session.commit()
    print("✓ Usuário administrador configurado com sucesso.")


if __name__ == "__main__":
    init_database()
