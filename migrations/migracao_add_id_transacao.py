import sqlite3
import os

# Obtenha o caminho absoluto para o diretório do projeto
project_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_dir, 'instance', 'sistema.db')

print(f"Conectando ao banco de dados em: {db_path}")

try:
    # Conectar ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Verificar se a coluna id_transacao já existe
    cursor.execute("PRAGMA table_info(pagamento)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'id_transacao' not in columns:
        print("Adicionando coluna 'id_transacao'...")
        cursor.execute('ALTER TABLE pagamento ADD COLUMN id_transacao VARCHAR(255)')
        print("Coluna 'id_transacao' adicionada.")
    else:
        print("Coluna 'id_transacao' já existe.")

    # 2. Criar um índice UNIQUE na coluna para garantir que não haja duplicatas
    print("Criando índice UNIQUE para 'id_transacao'...")
    # O índice não será criado se já existir um com o mesmo nome
    # A restrição UNIQUE em SQLite permite múltiplos valores NULL, o que é ideal para nós.
    cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS ix_pagamento_id_transacao ON pagamento (id_transacao)')
    print("Índice UNIQUE 'ix_pagamento_id_transacao' verificado/criado.")

    # Commit e fechar a conexão
    conn.commit()
    conn.close()
    
    print("\nMigração do id_transacao concluída com sucesso!")

except sqlite3.Error as e:
    print(f"\nErro durante a migração: {e}")
