from flask import Blueprint

leitura_notas_bp = Blueprint('leitura_notas', __name__, url_prefix='/leitura-notas')

from . import routes  # noqa: E402,F401
