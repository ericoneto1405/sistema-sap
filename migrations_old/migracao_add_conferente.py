
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

    # Verificar se a coluna nome_conferente já existe
    cursor.execute("PRAGMA table_info(coleta)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'nome_conferente' not in columns:
        print("Adicionando coluna 'nome_conferente'...")
        cursor.execute('ALTER TABLE coleta ADD COLUMN nome_conferente VARCHAR(100)')
        print("Coluna 'nome_conferente' adicionada.")
    else:
        print("Coluna 'nome_conferente' já existe.")

    # Verificar se a coluna cpf_conferente já existe
    cursor.execute("PRAGMA table_info(coleta)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'cpf_conferente' not in columns:
        print("Adicionando coluna 'cpf_conferente'...")
        cursor.execute('ALTER TABLE coleta ADD COLUMN cpf_conferente VARCHAR(20)')
        print("Coluna 'cpf_conferente' adicionada.")
    else:
        print("Coluna 'cpf_conferente' já existe.")

    # Commit e fechar a conexão
    conn.commit()
    conn.close()
    
    print("\nMigração concluída com sucesso!")

except sqlite3.Error as e:
    print(f"\nErro durante a migração: {e}")
