from collections import defaultdict
from decimal import Decimal, InvalidOperation
from io import BytesIO

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from sqlalchemy.exc import SQLAlchemyError

from meu_app.models import Pedido, Cliente, Produto, ItemPedido, db
from meu_app.pedidos.services import PedidoService
from meu_app.decorators import login_obrigatorio, permissao_necessaria

pedidos_bp = Blueprint('pedidos', __name__, url_prefix='/pedidos')

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
    resultado = session.pop('resultado_importacao_pedidos', None)

    if request.method == 'POST':
        try:
            # Verificar se um arquivo foi enviado
            if 'arquivo' not in request.files:
                flash('Nenhum arquivo foi selecionado.', 'error')
                return redirect(url_for('pedidos.importar_pedidos'))
            
            arquivo = request.files['arquivo']
            
            if arquivo.filename == '':
                flash('Nenhum arquivo foi selecionado.', 'error')
                return redirect(url_for('pedidos.importar_pedidos'))
            
            # Verificar extensão do arquivo
            extensao = arquivo.filename.rsplit('.', 1)[1].lower() if '.' in arquivo.filename else ''
            if extensao not in ['csv', 'xlsx', 'xls']:
                flash('Formato de arquivo inválido. Use CSV ou Excel (.xlsx, .xls).', 'error')
                return redirect(url_for('pedidos.importar_pedidos'))
            
            # Processar arquivo
            import pandas as pd
            
            conteudo = arquivo.read()
            if not conteudo:
                flash('O arquivo enviado está vazio.', 'error')
                return redirect(url_for('pedidos.importar_pedidos'))
            
            if extensao == 'csv':
                df = pd.read_csv(BytesIO(conteudo))
            else:
                df = pd.read_excel(BytesIO(conteudo))
            
            if df.empty:
                flash('O arquivo não contém linhas para importar.', 'warning')
                return redirect(url_for('pedidos.importar_pedidos'))
            
            df.columns = [str(col).strip().lower() for col in df.columns]
            colunas_necessarias = ['cliente_id', 'produto_id', 'quantidade', 'preco_venda', 'data']
            colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
            
            if colunas_faltantes:
                flash(f'Colunas faltantes no arquivo: {", ".join(colunas_faltantes)}.', 'error')
                return redirect(url_for('pedidos.importar_pedidos'))
            
            df = df[colunas_necessarias].copy()
            df['linha_planilha'] = df.index + 2  # Considera cabeçalho na linha 1
            
            erros = []
            registros_validos = []
            
            def _parse_inteiro(valor, coluna, linha, minimo=None):
                if pd.isna(valor) or str(valor).strip() == '':
                    erros.append(f"Linha {linha}: campo '{coluna}' está vazio.")
                    return None
                try:
                    numero = int(Decimal(str(valor).strip()))
                except (ValueError, InvalidOperation):
                    erros.append(f"Linha {linha}: campo '{coluna}' precisa ser um número inteiro.")
                    return None
                if minimo is not None and numero < minimo:
                    erros.append(f"Linha {linha}: campo '{coluna}' deve ser maior ou igual a {minimo}.")
                    return None
                return numero
            
            def _parse_decimal(valor, coluna, linha):
                if pd.isna(valor) or str(valor).strip() == '':
                    erros.append(f"Linha {linha}: campo '{coluna}' está vazio.")
                    return None
                valor_str = str(valor).strip().replace('R$', '').replace(' ', '').replace(',', '.')
                try:
                    return Decimal(valor_str)
                except (ValueError, InvalidOperation):
                    erros.append(f"Linha {linha}: campo '{coluna}' possui valor inválido: {valor}.")
                    return None
            
            def _parse_data(valor, linha):
                if pd.isna(valor) or str(valor).strip() == '':
                    erros.append(f"Linha {linha}: campo 'data' está vazio.")
                    return None
                data_convertida = pd.to_datetime(valor, errors='coerce', dayfirst=True)
                if pd.isna(data_convertida):
                    erros.append(f"Linha {linha}: data inválida '{valor}'. Use formatos YYYY-MM-DD ou DD/MM/YYYY.")
                    return None
                return data_convertida.to_pydatetime()
            
            for _, row in df.iterrows():
                linha = int(row['linha_planilha'])
                cliente_id = _parse_inteiro(row['cliente_id'], 'cliente_id', linha)
                produto_id = _parse_inteiro(row['produto_id'], 'produto_id', linha)
                quantidade = _parse_inteiro(row['quantidade'], 'quantidade', linha, minimo=1)
                preco_venda = _parse_decimal(row['preco_venda'], 'preco_venda', linha)
                data = _parse_data(row['data'], linha)
                
                if None in (cliente_id, produto_id, quantidade, preco_venda, data):
                    continue
                
                registros_validos.append({
                    'linha': linha,
                    'cliente_id': cliente_id,
                    'produto_id': produto_id,
                    'quantidade': quantidade,
                    'preco_venda': preco_venda,
                    'data': data
                })
            
            if not registros_validos:
                flash('Nenhum registro válido encontrado. Corrija os erros apontados e tente novamente.', 'error')
                session['resultado_importacao_pedidos'] = {'sucesso': 0, 'erros': erros}
                return redirect(url_for('pedidos.importar_pedidos'))
            
            pedidos_por_chave = defaultdict(list)
            for registro in registros_validos:
                chave = (registro['cliente_id'], registro['data'])
                pedidos_por_chave[chave].append(registro)
            
            pedidos_importados = 0
            
            for (cliente_id, data), itens in pedidos_por_chave.items():
                cliente = Cliente.query.get(cliente_id)
                if not cliente:
                    linhas_relacionadas = ', '.join(str(item['linha']) for item in itens)
                    erros.append(f"Cliente ID {cliente_id} não encontrado (linhas {linhas_relacionadas}).")
                    continue
                
                pedido = Pedido(cliente_id=cliente_id, data=data)
                itens_validos = 0
                
                for item in itens:
                    produto = Produto.query.get(item['produto_id'])
                    if not produto:
                        erros.append(f"Linha {item['linha']}: produto ID {item['produto_id']} não existe.")
                        continue
                    
                    preco_compra = Decimal(str(getattr(produto, 'preco_medio_compra', 0) or 0))
                    quantidade = item['quantidade']
                    preco_venda = item['preco_venda']
                    valor_total_venda = preco_venda * quantidade
                    valor_total_compra = preco_compra * quantidade
                    lucro_bruto = valor_total_venda - valor_total_compra
                    
                    pedido.itens.append(ItemPedido(
                        produto_id=produto.id,
                        quantidade=quantidade,
                        preco_venda=preco_venda,
                        preco_compra=preco_compra,
                        valor_total_venda=valor_total_venda,
                        valor_total_compra=valor_total_compra,
                        lucro_bruto=lucro_bruto
                    ))
                    itens_validos += 1
                
                if itens_validos == 0:
                    erros.append(
                        f"Pedido do cliente ID {cliente_id} em {data.strftime('%d/%m/%Y')} ignorado: nenhum item válido."
                    )
                    continue
                
                db.session.add(pedido)
                pedidos_importados += 1
            
            if pedidos_importados == 0:
                db.session.rollback()
            else:
                db.session.commit()
                PedidoService._registrar_atividade(
                    'importacao',
                    'Importação de pedidos históricos',
                    f'{pedidos_importados} pedido(s) importado(s) via planilha',
                    'pedidos',
                    {
                        'pedidos_importados': pedidos_importados,
                        'erros': len(erros)
                    }
                )
            
            if pedidos_importados > 0:
                flash(f'{pedidos_importados} pedido(s) importados com sucesso.', 'success')
            if erros:
                flash('Alguns registros apresentaram erro. Veja os detalhes abaixo.', 'warning')
                current_app.logger.warning(f'Erros na importação de pedidos: {erros}')
            
            current_app.logger.info(f"{pedidos_importados} pedidos importados por {session.get('usuario_nome', 'N/A')}")
            
            session['resultado_importacao_pedidos'] = {
                'sucesso': pedidos_importados,
                'erros': erros
            }
            
            return redirect(url_for('pedidos.importar_pedidos'))
        
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Erro de banco ao importar pedidos: {str(e)}")
            flash('Erro de banco de dados ao importar pedidos.', 'error')
            return redirect(url_for('pedidos.importar_pedidos'))
        except ImportError:
            current_app.logger.error("Pandas não está instalado para processar a planilha de pedidos.")
            flash('Dependência ausente: instale o pacote pandas para importar planilhas.', 'error')
            return redirect(url_for('pedidos.importar_pedidos'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Erro ao importar pedidos: {str(e)}")
            flash(f'Erro ao importar pedidos: {str(e)}', 'error')
            return redirect(url_for('pedidos.importar_pedidos'))
    
    # GET: Mostrar formulário de importação
    return render_template('importar_pedidos.html', resultado_importacao=resultado)

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
