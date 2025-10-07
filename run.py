# run.py
from config import DevelopmentConfig
from meu_app import create_app

app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5004, debug=True)
