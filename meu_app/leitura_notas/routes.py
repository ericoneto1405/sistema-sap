from flask import render_template, request, flash

from ..decorators import login_obrigatorio, permissao_necessaria
from . import leitura_notas_bp
from .services import NotaFiscalReaderService


@leitura_notas_bp.route('/', methods=['GET', 'POST'])
@login_obrigatorio
@permissao_necessaria('acesso_financeiro')
def index():
    """
    Tela principal para leitura de DANFE via Google Vision.
    """
    resultado = None

    if request.method == 'POST':
        arquivo = request.files.get('arquivo')
        if not arquivo or not arquivo.filename:
            flash('Selecione um arquivo PDF ou imagem da DANFE.', 'error')
        else:
            leitura = NotaFiscalReaderService.process_upload(arquivo)
            resultado = leitura
            if leitura['ok']:
                flash(leitura['mensagem'], 'success')
            else:
                flash(leitura['mensagem'], 'error')

    return render_template('leitura_notas/index.html', resultado=resultado)
