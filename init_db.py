#!/usr/bin/env python3
"""
Script de inicialização do banco de dados
Cria as tabelas e o usuário administrador inicial
"""

from meu_app import create_app, db
from meu_app.models import Usuario

def init_database():
    """Inicializa o banco de dados com tabelas e usuário admin"""
    app = create_app()
    
    with app.app_context():
        print("Criando tabelas do banco de dados...")
        db.create_all()
        print("✓ Tabelas criadas com sucesso!")
        
        # Verificar se já existe um usuário admin
        admin = Usuario.query.filter_by(nome='admin').first()
        if not admin:
            print("Criando usuário administrador...")
            admin = Usuario(
                nome='admin',
                senha_hash='',  # Será definido pelo método set_senha
                tipo='admin',
                acesso_clientes=True,
                acesso_produtos=True,
                acesso_pedidos=True,
                acesso_financeiro=True,
                acesso_logistica=True
            )
            # Definir senha segura
            admin.set_senha('Admin@2024')
            db.session.add(admin)
            db.session.commit()
            print("✓ Usuário admin criado com sucesso!")
        else:
            print("✓ Usuário admin já existe!")
            # Atualizar senha para uma mais segura se ainda for a padrão
            if admin.check_senha('123456'):
                print("Atualizando senha padrão do admin para uma mais segura...")
                admin.set_senha('Admin@2024')
                db.session.commit()
                print("✓ Senha do admin atualizada com sucesso!")

        # Verificar se já existe um usuário de teste
        test_user = Usuario.query.filter_by(nome='testuser').first()
        if not test_user:
            print("Criando usuário de teste...")
            test_user = Usuario(
                nome='testuser',
                senha='testpassword',
                tipo='comum',
                acesso_clientes=True,
                acesso_produtos=True,
                acesso_pedidos=True,
                acesso_financeiro=True,
                acesso_logistica=True
            )
            db.session.add(test_user)
            db.session.commit()
            print("✓ Usuário de teste criado com sucesso!")
        else:
            print("✓ Usuário de teste já existe!")
        
        print("\n=== CREDENCIAIS DE ACESSO ===")
        print("Usuário: admin")
        print("Senha: Admin@2024")
        print("=============================\n")
        print("⚠️  IMPORTANTE: Altere esta senha após o primeiro login!")
        print("📋 Use o módulo Usuários para gerenciar senhas e permissões.")
        
        print("Banco de dados inicializado com sucesso!")
        print("Execute 'python3 run.py' para iniciar a aplicação.")

if __name__ == '__main__':
    init_database()
