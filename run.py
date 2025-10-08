# run.py
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env.dev
dotenv_path = os.path.join(os.path.dirname(__file__), '.env.dev')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)

from config import DevelopmentConfig
from meu_app import create_app

app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5004, debug=True)
