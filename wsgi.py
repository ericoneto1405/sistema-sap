# wsgi.py
from config import ProductionConfig
from meu_app import create_app

app = create_app(ProductionConfig)
