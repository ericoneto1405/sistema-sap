from flask import render_template, request, redirect, url_for, flash, current_app, session
from flask import Blueprint
from .services import ClienteService

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')
from functools import wraps
from ..decorators import login_obrigatorio, permissao_necessaria, admin_necessario

# Decorador login_obrigatorio movido para meu_app/decorators.py
@clientes_bp.route('/', methods=['GET'])
@login_obrigatorio
@permissao_necessaria('acesso_clientes')
def listar_clientes():
    """Lista todos os clientes"""
    try:
        # Obter mensagem de erro da URL, se houver
        error_message = request.args.get('error')

        clientes = ClienteService.listar_clientes()
        current_app.logger.info(f"Listagem de clientes acessada por {session.get('usuario_nome', 'N/A')}")
        
        # Passar a mensagem de erro para o template
        return render_template('clientes.html', clientes=clientes, error_modal=error_message)
    except Exception as e:
        current_app.logger.error(f"Erro ao listar clientes: {str(e)}")
        flash(f"Erro ao carregar clientes: {str(e)}", 'error')
        return render_template('clientes.html', clientes=[], error_modal=None)

@clientes_bp.route('/novo', methods=['GET', 'POST'])
@login_obrigatorio
@permissao_necessaria('acesso_clientes')
def novo_cliente():
    """Cria um novo cliente"""
    if request.method == 'POST':
        # Extrair dados do formulário
        nome = request.form.get('nome', '').strip()
        fantasia = request.form.get('fantasia', '').strip()
        telefone = request.form.get('telefone', '').strip()
        endereco = request.form.get('endereco', '').strip()
        cidade = request.form.get('cidade', '').strip()
        cpf_cnpj = request.form.get('cpf_cnpj', '').strip()
        
        # Usar o serviço para criar o cliente
        sucesso, mensagem, cliente = ClienteService.criar_cliente(
            nome=nome,
            fantasia=fantasia,
            telefone=telefone,
            endereco=endereco,
            cidade=cidade,
            cpf_cnpj=cpf_cnpj
        )
        
        if sucesso:
            current_app.logger.info(f"Cliente criado por {session.get('usuario_nome', 'N/A')}")
            flash(mensagem, 'success')
            return redirect(url_for('clientes.listar_clientes'))
        else:
            flash(mensagem, 'error')
            # Retornar dados para o formulário em caso de erro
            return render_template('novo_cliente.html', cliente={
                'nome': nome,
                'fantasia': fantasia,
                'telefone': telefone,
                'endereco': endereco,
                'cidade': cidade,
                'cpf_cnpj': cpf_cnpj
            })
    
    # GET: Mostrar formulário vazio
    return render_template('novo_cliente.html', cliente=None)

@clientes_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_obrigatorio
@permissao_necessaria('acesso_clientes')
def editar_cliente(id):
    """Edita um cliente existente"""
    if request.method == 'POST':
        # Extrair dados do formulário
        nome = request.form.get('nome', '').strip()
        fantasia = request.form.get('fantasia', '').strip()
        telefone = request.form.get('telefone', '').strip()
        endereco = request.form.get('endereco', '').strip()
        cidade = request.form.get('cidade', '').strip()
        cpf_cnpj = request.form.get('cpf_cnpj', '').strip()
        
        # Usar o serviço para editar o cliente
        sucesso, mensagem, cliente = ClienteService.editar_cliente(
            cliente_id=id,
            nome=nome,
            fantasia=fantasia,
            telefone=telefone,
            endereco=endereco,
            cidade=cidade,
            cpf_cnpj=cpf_cnpj
        )
        
        if sucesso:
            current_app.logger.info(f"Cliente editado por {session.get('usuario_nome', 'N/A')}")
            flash(mensagem, 'success')
            return redirect(url_for('clientes.listar_clientes'))
        else:
            flash(mensagem, 'error')
            # Retornar dados para o formulário em caso de erro
            return render_template('novo_cliente.html', cliente={
                'id': id,
                'nome': nome,
                'fantasia': fantasia,
                'telefone': telefone,
                'endereco': endereco,
                'cidade': cidade,
                'cpf_cnpj': cpf_cnpj
            })
    
    # GET: Buscar cliente e mostrar formulário
    cliente = ClienteService.buscar_cliente_por_id(id)
    if not cliente:
        flash('Cliente não encontrado', 'error')
        return redirect(url_for('clientes.listar_clientes'))
    
    return render_template('novo_cliente.html', cliente=cliente)

@clientes_bp.route('/excluir/<int:id>', methods=['GET', 'POST'])
@login_obrigatorio
@permissao_necessaria('acesso_clientes')
def excluir_cliente(id):
    """Exclui um cliente"""
    # Usar o serviço para excluir o cliente
    sucesso, mensagem = ClienteService.excluir_cliente(id)
    
    if sucesso:
        current_app.logger.info(f"Cliente excluído (ID: {id}) por {session.get('usuario_nome', 'N/A')}")
        flash(mensagem, 'success')
        return redirect(url_for('clientes.listar_clientes'))
    else:
        # Redirecionar com a mensagem de erro como parâmetro de consulta
        return redirect(url_for('clientes.listar_clientes', error=mensagem))
