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

    # Verificar se a coluna caminho_recibo já existe
    cursor.execute("PRAGMA table_info(pagamento)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'caminho_recibo' not in columns:
        print("Adicionando coluna 'caminho_recibo'...")
        cursor.execute('ALTER TABLE pagamento ADD COLUMN caminho_recibo VARCHAR(255)')
        print("Coluna 'caminho_recibo' adicionada.")
    else:
        print("Coluna 'caminho_recibo' já existe.")

    # Commit e fechar a conexão
    conn.commit()
    conn.close()
    
    print("\nMigração do recibo concluída com sucesso!")

except sqlite3.Error as e:
    print(f"\nErro durante a migração: {e}")
