import unicodedata
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from io import BytesIO
from types import SimpleNamespace

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from sqlalchemy.exc import SQLAlchemyError

from meu_app.models import Pedido, Cliente, Produto, ItemPedido, db
from meu_app.pedidos.services import PedidoService
from meu_app.decorators import login_obrigatorio, permissao_necessaria

pedidos_bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')


def normalizar_nome(valor):
    """Remove acentos e padroniza nomes para busca case-insensitive."""
    if valor is None:
        return ''
    ascii_safe = unicodedata.normalize('NFKD', str(valor)).encode('ASCII', 'ignore').decode('ASCII')
    return ascii_safe.strip().lower()


@pedidos_bp.route('/', methods=['GET'])
@login_obrigatorio
@permissao_necessaria('acesso_pedidos')
def listar_pedidos():
    """Lista todos os pedidos com filtros e ordenação"""
    try:
        filtro_status = request.args.get('filtro', 'todos')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        ordenar_por = request.args.get('sort', 'data')
        direcao = request.args.get('direction', 'desc')
        
        # Validar parâmetros de ordenação
        campos_validos = ['id', 'cliente', 'data', 'valor', 'status']
        if ordenar_por not in campos_validos:
            ordenar_por = 'data'
        
        if direcao not in ['asc', 'desc']:
            direcao = 'desc'
        
        pedidos = PedidoService.listar_pedidos(filtro_status, data_inicio, data_fim, ordenar_por, direcao)
        
        # Calcular necessidade de compra
        necessidade_compra = PedidoService.calcular_necessidade_compra()
        
        current_app.logger.info(f"Listagem de pedidos acessada por {session.get('usuario_nome', 'N/A')} - Ordenado por: {ordenar_por} ({direcao})")
        
        return render_template(
            'listar_pedidos.html',
            pedidos=pedidos,
            filtro=filtro_status,
            data_inicio=data_inicio or '',
            data_fim=data_fim or '',
            current_sort=ordenar_por,
            current_direction=direcao,
            necessidade_compra=necessidade_compra
        )
        
    except Exception as e:
        current_app.logger.error(f"Erro ao listar pedidos: {str(e)}")
        flash(f"Erro ao carregar pedidos: {str(e)}", 'error')
        return render_template('listar_pedidos.html', pedidos=[], filtro='todos', necessidade_compra=[])

@pedidos_bp.route('/novo', methods=['GET', 'POST'])
@login_obrigatorio
@permissao_necessaria('acesso_pedidos')
def novo_pedido():
    """Cria um novo pedido"""
    if request.method == 'POST':
        # Extrair dados do formulário
        cliente_id = request.form.get('cliente_id')
        
        # Processar itens do pedido
        itens_data = []
        for produto_id, qtd, pv in zip(
            request.form.getlist('produto_id'),
            request.form.getlist('quantidade'),
            request.form.getlist('preco_venda')
        ):
            if produto_id and qtd and pv:
                # Limpar formatação do preço (R$ 32,00 -> 32.00)
                preco_limpo = pv.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
                try:
                    preco_float = float(preco_limpo)
                    itens_data.append({
                        'produto_id': produto_id,
                        'quantidade': qtd,
                        'preco_venda': preco_float
                    })
                except ValueError:
                    current_app.logger.error(f"Erro ao converter preço: {pv}")
                    continue
        
        # Usar o serviço para criar o pedido
        sucesso, mensagem, pedido = PedidoService.criar_pedido(cliente_id, itens_data)
        
        if sucesso:
            flash(mensagem, 'success')
            return redirect(url_for('pedidos.listar_pedidos', filtro='todos'))
        else:
            flash(mensagem, 'error')
            # Retornar dados para o formulário em caso de erro
            clientes = Cliente.query.all()
            produtos = Produto.query.all()
            return render_template('novo_pedido.html', clientes=clientes, produtos=produtos)
    
    # GET: Mostrar formulário
    clientes = Cliente.query.all()
    produtos = Produto.query.all()
    return render_template('novo_pedido.html', clientes=clientes, produtos=produtos)

@pedidos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_obrigatorio
@permissao_necessaria('acesso_pedidos')
def editar_pedido(id):
    """Edita um pedido existente"""
    pedido = PedidoService.buscar_pedido(id)
    if not pedido:
        flash('Pedido não encontrado', 'error')
        return redirect(url_for('pedidos.listar_pedidos'))
    
    if request.method == 'POST':
        # Extrair dados do formulário
        cliente_id = request.form.get('cliente_id')
        
        # Processar itens do pedido (similar ao novo_pedido)
        itens_data = []
        for produto_id, qtd, pv in zip(
            request.form.getlist('produto_id'),
            request.form.getlist('quantidade'),
            request.form.getlist('preco_venda')
        ):
            if produto_id and qtd and pv:
                # Limpar formatação do preço (R$ 32,00 -> 32.00)
                preco_limpo = pv.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
                try:
                    preco_float = float(preco_limpo)
                    itens_data.append({
                        'produto_id': produto_id,
                        'quantidade': qtd,
                        'preco_venda': preco_float
                    })
                except ValueError:
                    current_app.logger.error(f"Erro ao converter preço: {pv}")
                    continue
        
        # Usar o serviço para atualizar o pedido
        sucesso, mensagem = PedidoService.atualizar_pedido(id, cliente_id, itens_data)
        
        if sucesso:
            current_app.logger.info(f"Pedido editado por {session.get('usuario_nome', 'N/A')}")
            flash(mensagem, 'success')
            return redirect(url_for('pedidos.listar_pedidos'))
        else:
            flash(mensagem, 'error')
            # Retornar dados para o formulário em caso de erro
            clientes = Cliente.query.all()
            produtos = Produto.query.all()
            return render_template('editar_pedido.html', pedido=pedido, clientes=clientes, produtos=produtos)
    
    clientes = Cliente.query.all()
    produtos = Produto.query.all()
    return render_template('editar_pedido.html', pedido=pedido, clientes=clientes, produtos=produtos)

@pedidos_bp.route('/confirmar/<int:id>', methods=['POST'])
@login_obrigatorio
@permissao_necessaria('acesso_pedidos')
def confirmar_pedido(id):
    """Confirma um pedido"""
    sucesso, mensagem = PedidoService.confirmar_pedido(id)
    
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('pedidos.listar_pedidos'))

@pedidos_bp.route('/editar/<int:id>/confirmar', methods=['POST'])
@login_obrigatorio
@permissao_necessaria('acesso_pedidos')
def confirmar_edicao_pedido(id):
    """Confirma a edição de um pedido"""
    try:
        # Extrair dados do formulário
        cliente_id = request.form.get('cliente_id')
        
        # Processar itens do pedido
        itens_data = []
        for produto_id, qtd, pv in zip(
            request.form.getlist('produto_id'),
            request.form.getlist('quantidade'),
            request.form.getlist('preco_venda')
        ):
            if produto_id and qtd and pv:
                # Limpar formatação do preço (R$ 32,00 -> 32.00)
                preco_limpo = pv.replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')
                try:
                    preco_float = float(preco_limpo)
                    itens_data.append({
                        'produto_id': produto_id,
                        'quantidade': qtd,
                        'preco_venda': preco_float
                    })
                except ValueError:
                    current_app.logger.error(f"Erro ao converter preço: {pv}")
                    continue
        
        # Usar o serviço para atualizar o pedido
        sucesso, mensagem = PedidoService.atualizar_pedido(id, cliente_id, itens_data)
        
        if sucesso:
            flash(mensagem, 'success')
        else:
            flash(mensagem, 'error')
            
    except Exception as e:
        current_app.logger.error(f"Erro ao confirmar edição do pedido: {str(e)}")
        flash('Erro ao salvar alterações', 'error')
    
    return redirect(url_for('pedidos.listar_pedidos'))

@pedidos_bp.route('/confirmar_comercial/<int:id>', methods=['POST'])
@login_obrigatorio
@permissao_necessaria('acesso_pedidos')
def confirmar_comercial_pedido(id):
    """Confirma pedido pelo comercial"""
    try:
        senha_admin = request.form.get('senha')
        
        if not senha_admin:
            return jsonify({'success': False, 'message': 'Senha é obrigatória'})
        
        # Validar senha do administrador
        usuario_logado = session.get('usuario_nome', 'N/A')
        current_app.logger.info(f"Tentativa de confirmação comercial do pedido {id} por {usuario_logado}")
        
        # Validar senha usando o serviço
        sucesso, mensagem = PedidoService.confirmar_pedido_comercial(id, senha_admin)
        
        if sucesso:
            current_app.logger.info(f"Pedido {id} confirmado comercialmente por {usuario_logado}")
            return jsonify({'success': True, 'message': mensagem})
        else:
            current_app.logger.warning(f"Falha na confirmação comercial do pedido {id}: {mensagem}")
            return jsonify({'success': False, 'message': mensagem})
            
    except Exception as e:
        current_app.logger.error(f"Erro ao confirmar pedido comercial {id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

@pedidos_bp.route('/excluir/<int:id>/confirmar', methods=['POST'])
@login_obrigatorio
@permissao_necessaria('acesso_pedidos')
def excluir_pedido_confirmar(id):
    """Exclui pedido após confirmação de senha"""
    try:
        senha_admin = request.form.get('senha')
        
        if not senha_admin:
            return jsonify({'success': False, 'message': 'Senha é obrigatória'})
        
        # Validar senha do administrador
        usuario_logado = session.get('usuario_nome', 'N/A')
        current_app.logger.info(f"Tentativa de exclusão do pedido {id} por {usuario_logado}")
        
        # Verificar senha do administrador
        from meu_app.models import Usuario
        admin = Usuario.query.filter_by(tipo='admin').first()
        if not admin or not admin.check_senha(senha_admin):
            return jsonify({'success': False, 'message': 'Senha incorreta'})
        
        # Excluir pedido
        sucesso, mensagem = PedidoService.excluir_pedido(id)
        
        if sucesso:
            current_app.logger.info(f"Pedido {id} excluído por {usuario_logado}")
            return jsonify({'success': True, 'message': mensagem})
        else:
            current_app.logger.warning(f"Falha na exclusão do pedido {id}: {mensagem}")
            return jsonify({'success': False, 'message': mensagem})
            
    except Exception as e:
        current_app.logger.error(f"Erro ao excluir pedido {id}: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'})

@pedidos_bp.route('/cancelar/<int:id>', methods=['POST'])
@login_obrigatorio
@permissao_necessaria('acesso_pedidos')
def cancelar_pedido(id):
    """Cancela um pedido"""
    sucesso, mensagem = PedidoService.cancelar_pedido(id)
    
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('pedidos.listar_pedidos'))

@pedidos_bp.route('/visualizar/<int:id>')
@login_obrigatorio
@permissao_necessaria('acesso_pedidos')
def visualizar_pedido(id):
    """Visualiza os detalhes de um pedido"""
    try:
        pedido = PedidoService.buscar_pedido(id)
        if not pedido:
            flash("Pedido não encontrado", "error")
            return redirect(url_for("pedidos.listar_pedidos"))
    
        # Calcular totais usando o serviço
        totais = PedidoService.calcular_totais_pedido(id)
        
        # Capturar parâmetro origem para o template
        origem = request.args.get('origem', 'pedidos')
        
        current_app.logger.info(f"Pedido {id} visualizado por {session.get('usuario_nome', 'N/A')} (origem: {origem})")
        
        return render_template('visualizar_pedido.html', 
                             pedido=pedido, 
                             total=totais['total'], 
                             pago=totais['pago'], 
                             saldo=totais['saldo'],
                             origem=origem)
        
    except Exception as e:
        current_app.logger.error(f"Erro ao visualizar pedido: {str(e)}")
        flash("Erro ao carregar pedido", "error")
        return redirect(url_for("pedidos.listar_pedidos"))

@pedidos_bp.route('/importar', methods=['GET', 'POST'])
@login_obrigatorio
@permissao_necessaria('acesso_pedidos')
def importar_pedidos():
    """Importa pedidos históricos de arquivo CSV ou Excel"""
    resultado_importacao = session.pop('resultado_importacao_pedidos', None)

    if request.method == 'POST':
        if 'arquivo' not in request.files or not request.files['arquivo'].filename:
            flash('Nenhum arquivo foi selecionado.', 'error')
            return redirect(url_for('pedidos.importar_pedidos'))

        arquivo = request.files['arquivo']
        extensao = arquivo.filename.rsplit('.', 1)[1].lower() if '.' in arquivo.filename else ''

        if extensao not in ['csv', 'xlsx', 'xls']:
            flash('Formato de arquivo inválido. Use CSV ou Excel (.xlsx, .xls).', 'error')
            return redirect(url_for('pedidos.importar_pedidos'))

        try:
            import pandas as pd
            conteudo = arquivo.read()
            if not conteudo:
                flash('O arquivo enviado está vazio.', 'error')
                return redirect(url_for('pedidos.importar_pedidos'))

            # Ler CSV/Excel com fallback de separador (CSV com ';' é comum em PT-BR)
            if extensao == 'csv':
                try:
                    df = pd.read_csv(BytesIO(conteudo))
                except Exception:
                    df = pd.read_csv(BytesIO(conteudo), sep=';')
                else:
                    # Se leu uma coluna só e há ';' no conteúdo, tentar novamente com ';'
                    if getattr(df, 'shape', (0, 0))[1] == 1 and b';' in conteudo:
                        df = pd.read_csv(BytesIO(conteudo), sep=';')
            else:
                df = pd.read_excel(BytesIO(conteudo))

            if df.empty:
                flash('O arquivo não contém linhas para importar.', 'warning')
                return redirect(url_for('pedidos.importar_pedidos'))

            # Normalizar cabeçalhos
            df.columns = [str(col).strip().lower() for col in df.columns]

            # Suportar dois formatos de cabeçalho: por NOME ou por ID
            colunas_comuns = {'quantidade', 'preco_venda', 'data'}
            formato_nomes = {'cliente_nome', 'produto_nome'} | colunas_comuns
            formato_ids = {'cliente_id', 'produto_id'} | colunas_comuns

            presentes = set(df.columns)
            usa_nomes = formato_nomes.issubset(presentes)
            usa_ids = formato_ids.issubset(presentes)

            if not (usa_nomes or usa_ids):
                faltando_nomes = sorted(list(formato_nomes - presentes))
                faltando_ids = sorted(list(formato_ids - presentes))
                msg = [
                    'Cabeçalho inválido no arquivo.',
                    'Você pode usar UM dos formatos abaixo:',
                    f"• Por nomes: {', '.join(sorted(list(formato_nomes)))}",
                    f"• Por IDs: {', '.join(sorted(list(formato_ids)))}",
                ]
                if faltando_nomes:
                    msg.append(f"Faltando para formato por nomes: {', '.join(faltando_nomes)}")
                if faltando_ids:
                    msg.append(f"Faltando para formato por IDs: {', '.join(faltando_ids)}")
                flash(' '.join(msg), 'error')
                return redirect(url_for('pedidos.importar_pedidos'))

            # Filtrar somente as colunas necessárias conforme o formato detectado
            colunas_necessarias = list(formato_nomes if usa_nomes else formato_ids)
            df_filtrado = df[colunas_necessarias]

            resultado = PedidoService.processar_planilha_importacao(df_filtrado)
            
            resumo = resultado.get('resumo', {})
            if resumo.get('pedidos_criados', 0) > 0:
                flash(f"{resumo['pedidos_criados']} pedido(s) importado(s) com sucesso!", 'success')
            if resumo.get('falha', 0) > 0:
                flash(f"{resumo['falha']} linha(s) contiveram erros e não foram importadas. Verifique os detalhes abaixo.", 'warning')

            session['resultado_importacao_pedidos'] = resultado
            return redirect(url_for('pedidos.importar_pedidos'))

        except ImportError:
            current_app.logger.error("Pandas ou openpyxl não estão instalados.")
            flash('Dependência ausente para processar planilhas. Contate o suporte.', 'error')
            return redirect(url_for('pedidos.importar_pedidos'))
        except Exception as e:
            current_app.logger.error(f"Erro inesperado ao importar pedidos: {e}", exc_info=True)
            flash(f'Ocorreu um erro inesperado ao processar o arquivo: {e}', 'error')
            return redirect(url_for('pedidos.importar_pedidos'))

    return render_template('importar_pedidos.html', resultado_importacao=resultado_importacao)

@pedidos_bp.route('/importar/exemplo')
@login_obrigatorio
@permissao_necessaria('acesso_pedidos')
def download_exemplo():
    """Baixa arquivo de exemplo para importação"""
    from flask import send_file
    import os
    
    arquivo_exemplo = os.path.join(current_app.root_path, '..', 'docs', 'EXEMPLO_IMPORTACAO_PEDIDOS.csv')
    
    try:
        return send_file(
            arquivo_exemplo,
            as_attachment=True,
            download_name='exemplo_importacao_pedidos.csv',
            mimetype='text/csv'
        )
    except Exception as e:
        current_app.logger.error(f"Erro ao baixar arquivo de exemplo: {str(e)}")
        flash('Erro ao baixar arquivo de exemplo', 'error')
        return redirect(url_for('pedidos.importar_pedidos'))
