from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, jsonify, send_from_directory
import os

financeiro_bp = Blueprint('financeiro', __name__, url_prefix='/financeiro')
from .services import FinanceiroService
from functools import wraps
from ..decorators import login_obrigatorio, permissao_necessaria, admin_necessario
from ..upload_security import FileUploadValidator
from .ocr_service import OcrService
from .config import FinanceiroConfig
from .exceptions import (
    FinanceiroValidationError, 
    PagamentoDuplicadoError, 
    PedidoNaoEncontradoError,
    ValorInvalidoError,
    ComprovanteObrigatorioError,
    ArquivoInvalidoError,
    OcrProcessingError
)

# Decorador login_obrigatorio movido para meu_app/decorators.py
@financeiro_bp.route('/', methods=['GET'])
@login_obrigatorio
@permissao_necessaria('acesso_financeiro')
def listar_financeiro():
    """Lista dados financeiros"""
    try:
        tipo = request.args.get('filtro', 'pendentes')
        mes = request.args.get('mes', '')
        ano = request.args.get('ano', '')
        
        pedidos = FinanceiroService.listar_pedidos_financeiro(tipo, mes, ano)
        
        current_app.logger.info(f"Financeiro acessado por {session.get('usuario_nome', 'N/A')}")
        
        return render_template('financeiro.html', pedidos=pedidos, filtro=tipo, mes=mes, ano=ano)
    except Exception as e:
        current_app.logger.error(f"Erro ao listar financeiro: {str(e)}")
        flash(f"Erro ao carregar dados financeiros: {str(e)}", 'error')
        return render_template('financeiro.html', pedidos=[], filtro='pendentes')

@financeiro_bp.route('/exportar', methods=['GET'])
@login_obrigatorio
@permissao_necessaria('acesso_financeiro')
def exportar_financeiro():
    """Exporta dados financeiros"""
    try:
        mes = request.args.get('mes', '')
        ano = request.args.get('ano', '')
        
        dados = FinanceiroService.exportar_dados_financeiro(mes, ano)
        
        current_app.logger.info(f"Exportação financeira solicitada por {session.get('usuario_nome', 'N/A')}")
        
        return jsonify(dados)
    except Exception as e:
        current_app.logger.error(f"Erro ao exportar financeiro: {str(e)}")
        return jsonify({'error': str(e)}), 500

@financeiro_bp.route('/pagamento/<int:pedido_id>', methods=['GET', 'POST'])
@login_obrigatorio
@permissao_necessaria('acesso_financeiro')
def registrar_pagamento(pedido_id):
    """Registra um pagamento"""
    if request.method == 'POST':
        # Extrair dados do formulário
        valor = request.form.get('valor')
        forma_pagamento = request.form.get('metodo_pagamento')
        observacoes = request.form.get('observacoes', '')
        id_transacao = request.form.get('id_transacao') # Captura o ID da transação do campo oculto
        recibo = request.files.get('recibo')
        caminho_recibo = None

        try:
            valor = float(valor)
            if valor <= 0:
                raise ValueError("Valor deve ser maior que zero")
        except (ValueError, TypeError) as e:
            flash(f'Valor inválido: {str(e)}', 'error')
            return redirect(url_for('financeiro.registrar_pagamento', pedido_id=pedido_id))

        # Lógica de upload do recibo
        if recibo and recibo.filename:
            # Tenta validar como documento ou imagem
            is_valid, error_msg, metadata = FileUploadValidator.validate_file(recibo, 'document')
            if not is_valid:
                # Se falhar, tenta como imagem
                is_valid, error_msg, metadata = FileUploadValidator.validate_file(recibo, 'image')

            if not is_valid:
                flash(f"Erro no upload do recibo: {error_msg}", 'error')
                return redirect(url_for('financeiro.registrar_pagamento', pedido_id=pedido_id))

            # Gera nome seguro e salva usando configuração centralizada
            secure_name = FileUploadValidator.generate_secure_filename(recibo.filename, 'recibo_pagamento')
            upload_dir = FinanceiroConfig.get_upload_directory('recibos')
            file_path = os.path.join(upload_dir, secure_name)
            
            try:
                # Salvar temporariamente em memória para calcular hash e tamanho
                file_bytes = recibo.read()
                recibo.seek(0)
                import hashlib
                sha256 = hashlib.sha256(file_bytes).hexdigest()
                tamanho = len(file_bytes)

                # Evitar duplicidade pelo hash
                from ..models import Pagamento
                existente = Pagamento.query.filter_by(recibo_sha256=sha256).first()
                if existente:
                    flash(f"Este comprovante já foi enviado (ID pagamento #{existente.id}).", 'error')
                    return redirect(url_for('financeiro.registrar_pagamento', pedido_id=pedido_id))

                # Salvar arquivo em disco
                recibo.save(file_path)
                caminho_recibo = secure_name # Salva apenas o nome do arquivo

                # Anexar metadados na sessão (usaremos ao chamar o serviço)
                request.recibo_meta = {
                    'recibo_mime': metadata.get('mime_type') if metadata else None,
                    'recibo_tamanho': tamanho,
                    'recibo_sha256': sha256
                }
            except Exception as e:
                flash(f"Erro ao salvar o arquivo de recibo: {str(e)}", 'error')
                return redirect(url_for('financeiro.registrar_pagamento', pedido_id=pedido_id))

        # Extrair dados extras do formulário (se fornecidos via OCR)
        data_comprovante = request.form.get('data_comprovante', '')
        banco_emitente = request.form.get('banco_emitente', '')
        agencia_recebedor = request.form.get('agencia_recebedor', '')
        conta_recebedor = request.form.get('conta_recebedor', '')
        chave_pix_recebedor = request.form.get('chave_pix_recebedor', '')

        # Usar o serviço para registrar o pagamento
        try:
            sucesso, mensagem, pagamento = FinanceiroService.registrar_pagamento(
                pedido_id=pedido_id,
                valor=valor,
                forma_pagamento=forma_pagamento,
                observacoes=observacoes,
                caminho_recibo=caminho_recibo,
                recibo_mime=(getattr(request, 'recibo_meta', {}) or {}).get('recibo_mime'),
                recibo_tamanho=(getattr(request, 'recibo_meta', {}) or {}).get('recibo_tamanho'),
                recibo_sha256=(getattr(request, 'recibo_meta', {}) or {}).get('recibo_sha256'),
                id_transacao=id_transacao,
                # NOVOS DADOS EXTRAÍDOS DO COMPROVANTE
                data_comprovante=data_comprovante if data_comprovante else None,
                banco_emitente=banco_emitente if banco_emitente else None,
                agencia_recebedor=agencia_recebedor if agencia_recebedor else None,
                conta_recebedor=conta_recebedor if conta_recebedor else None,
                chave_pix_recebedor=chave_pix_recebedor if chave_pix_recebedor else None
            )
            
            if sucesso:
                current_app.logger.info(f"Pagamento registrado por {session.get('usuario_nome', 'N/A')}")
                flash(mensagem, 'success')
                return redirect(url_for('financeiro.listar_financeiro'))
            else:
                flash(mensagem, 'error')
                return redirect(url_for('financeiro.registrar_pagamento', pedido_id=pedido_id))
        except (FinanceiroValidationError, PagamentoDuplicadoError, PedidoNaoEncontradoError,
                ValorInvalidoError, ComprovanteObrigatorioError) as e:
            flash(str(e), 'error')
            return redirect(url_for('financeiro.registrar_pagamento', pedido_id=pedido_id))
    
    # GET: Mostrar formulário
    try:
        from ..models import Pedido
        
        # Buscar pedido
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            flash('Pedido não encontrado', 'error')
            return redirect(url_for('financeiro.listar_financeiro'))
        
        # Usar método centralizado do modelo
        totais = pedido.calcular_totais()
        
        return render_template('lancar_pagamento.html', 
                             pedido=pedido, 
                             total=totais['total_pedido'], 
                             pago=totais['total_pago'], 
                             saldo=totais['saldo'])
    except Exception as e:
        current_app.logger.error(f"Erro ao carregar formulário de pagamento: {str(e)}")
        flash('Erro ao carregar dados do pedido', 'error')
        return redirect(url_for('financeiro.listar_financeiro'))

@financeiro_bp.route('/recibos/<path:filename>')
@login_obrigatorio
def ver_recibo(filename):
    """Serve um arquivo de recibo de forma segura"""
    # Usar configuração centralizada
    directory = FinanceiroConfig.get_upload_directory('recibos')
    return send_from_directory(directory, filename, as_attachment=False)

@financeiro_bp.route('/processar-recibo-ocr', methods=['POST'])
@login_obrigatorio
def processar_recibo_ocr():
    """Processa o upload de um recibo com OCR para encontrar valor e ID da transação."""
    if 'recibo' not in request.files:
        return jsonify({'error': 'Nenhum arquivo de recibo enviado'}), 400

    recibo = request.files['recibo']
    if recibo.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    # Validar arquivo como documento OU imagem
    is_valid, error_msg, metadata = FileUploadValidator.validate_file(recibo, 'document')
    if not is_valid:
        # Se falhar como documento, tenta como imagem
        is_valid, error_msg, metadata = FileUploadValidator.validate_file(recibo, 'image')
    if not is_valid:
        return jsonify({'error': f"Arquivo inválido: {error_msg}"}), 400

    # Salvar arquivo temporariamente usando configuração centralizada
    secure_name = FileUploadValidator.generate_secure_filename(recibo.filename, 'temp_recibo_ocr')
    upload_dir = FinanceiroConfig.get_upload_directory('temp')
    file_path = os.path.join(upload_dir, secure_name)

    try:
        recibo.save(file_path)

        # CORREÇÃO: OCR opcional e não bloqueante
        try:
            # Tentar processar com OCR
            ocr_results = OcrService.process_receipt(file_path)
            
            # Preparar dados para o frontend
            response_data = {
                'valor_encontrado': ocr_results.get('amount'),
                'id_transacao_encontrado': ocr_results.get('transaction_id'),
                # NOVOS DADOS EXTRAÍDOS
                'data_encontrada': ocr_results.get('date'),
                'banco_emitente': ocr_results.get('bank_info', {}).get('banco_emitente'),
                'agencia_recebedor': ocr_results.get('bank_info', {}).get('agencia_recebedor'),
                'conta_recebedor': ocr_results.get('bank_info', {}).get('conta_recebedor'),
                'chave_pix_recebedor': ocr_results.get('bank_info', {}).get('chave_pix_recebedor'),
                'ocr_status': 'success'  # Indicar que OCR funcionou
            }

            # Se OCR retornou erro, marcar como falha mas não bloquear
            if ocr_results.get('error'):
                response_data['ocr_status'] = 'failed'
                response_data['ocr_error'] = ocr_results.get('error')
                response_data['ocr_message'] = 'OCR indisponível - digite os dados manualmente'
            else:
                response_data['ocr_message'] = 'Dados extraídos automaticamente!'
                
        except Exception as ocr_error:
            # Se OCR falhar completamente, retornar resposta vazia mas não erro
            current_app.logger.warning(f"OCR falhou, mas sistema continua funcionando: {str(ocr_error)}")
            response_data = {
                'valor_encontrado': None,
                'id_transacao_encontrado': None,
                'data_encontrada': None,
                'banco_emitente': None,
                'agencia_recebedor': None,
                'conta_recebedor': None,
                'chave_pix_recebedor': None,
                'ocr_status': 'failed',
                'ocr_message': 'OCR temporariamente indisponível - digite os dados manualmente'
            }

        return jsonify(response_data)

    except Exception as e:
        current_app.logger.error(f"Erro no processamento OCR: {str(e)}")
        return jsonify({'error': 'Erro interno ao processar o arquivo.'}), 500
    finally:
        # Limpar o arquivo temporário
        if os.path.exists(file_path):
            os.remove(file_path)

@financeiro_bp.route('/comprovantes', methods=['GET'])
@login_obrigatorio
@permissao_necessaria('acesso_financeiro')
def listar_comprovantes():
    """Lista comprovantes de pagamento organizados por cliente"""
    try:
        mes = request.args.get('mes', '')
        ano = request.args.get('ano', '')
        
        dados = FinanceiroService.listar_comprovantes_por_cliente(mes, ano)
        
        current_app.logger.info(f"Comprovantes acessados por {session.get('usuario_nome', 'N/A')}")
        
        return render_template('comprovantes_pagamento.html', 
                             clientes=dados['clientes'],
                             total_comprovantes=dados['total_comprovantes'],
                             mes=mes, 
                             ano=ano)
    except Exception as e:
        current_app.logger.error(f"Erro ao listar comprovantes: {str(e)}")
        flash(f"Erro ao carregar comprovantes: {str(e)}", 'error')
        return render_template('comprovantes_pagamento.html', 
                             clientes=[], 
                             total_comprovantes=0)
