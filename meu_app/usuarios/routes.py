from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')
from .services import UsuarioService
from functools import wraps
from ..decorators import login_obrigatorio, permissao_necessaria, admin_necessario
from app.auth.rbac import requires_admin

# Decoradores movidos para meu_app/decorators.py

@usuarios_bp.route('/', methods=['GET', 'POST'])
@login_obrigatorio
@requires_admin
@admin_necessario
def listar_usuarios():
    """Lista e cria usuários"""
    if request.method == 'POST':
        # Extrair dados do formulário
        nome = request.form.get('nome', '').strip()
        senha = request.form.get('senha', '').strip()
        tipo = request.form.get('tipo', 'comum')
        
        # Coletar acessos do formulário
        acessos = {
            'acesso_clientes': 'acesso_clientes' in request.form,
            'acesso_produtos': 'acesso_produtos' in request.form,
            'acesso_pedidos': 'acesso_pedidos' in request.form,
            'acesso_financeiro': 'acesso_financeiro' in request.form,
            'acesso_logistica': 'acesso_logistica' in request.form
        }
        
        # Usar o serviço para criar o usuário
        sucesso, mensagem, usuario = UsuarioService.criar_usuario(nome, senha, tipo, acessos)
        
        if sucesso:
            current_app.logger.info(f"Usuário criado por {session.get('usuario_nome', 'N/A')}")
            flash(mensagem, 'success')
        else:
            flash(mensagem, 'error')
        
        return redirect(url_for('usuarios.listar_usuarios'))
    
    # Listar usuários
    usuarios = UsuarioService.listar_usuarios()
    current_app.logger.info(f"Listagem de usuários acessada por {session.get('usuario_nome', 'N/A')}")
    return render_template('usuarios.html', usuarios=usuarios)

@usuarios_bp.route('/alterar_senha/<int:id>', methods=['POST'])
@login_obrigatorio
@admin_necessario
def alterar_senha_usuario(id):
    """Altera a senha de um usuário"""
    senha_atual = request.form.get('senha_atual')
    nova_senha = request.form.get('nova_senha')
    confirmar_senha = request.form.get('confirmar_senha')
    
    sucesso, mensagem = UsuarioService.alterar_senha_usuario(id, senha_atual, nova_senha, confirmar_senha)
    
    if sucesso:
        current_app.logger.info(f"Senha alterada para usuário (ID: {id}) por {session.get('usuario_nome', 'N/A')}")
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.route('/editar/<int:id>', methods=['POST'])
@login_obrigatorio
@admin_necessario
def editar_usuario(id):
    """Edita um usuário"""
    nome = request.form.get('nome')
    tipo = request.form.get('tipo')
    
    acessos = {
        'acesso_clientes': 'acesso_clientes' in request.form,
        'acesso_produtos': 'acesso_produtos' in request.form,
        'acesso_pedidos': 'acesso_pedidos' in request.form,
        'acesso_financeiro': 'acesso_financeiro' in request.form,
        'acesso_logistica': 'acesso_logistica' in request.form
    }
    
    sucesso, mensagem = UsuarioService.editar_usuario(id, nome, tipo, acessos)
    
    if sucesso:
        current_app.logger.info(f"Usuário editado (ID: {id}) por {session.get('usuario_nome', 'N/A')}")
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.route('/redefinir_senha/<int:id>', methods=['POST'])
@login_obrigatorio
@admin_necessario
def redefinir_senha_usuario(id):
    """Redefine a senha de um usuário (apenas para admins)"""
    nova_senha = request.form.get('nova_senha')
    senha_admin = request.form.get('senha_admin')
    
    sucesso, mensagem = UsuarioService.redefinir_senha_usuario(id, nova_senha, senha_admin)
    
    if sucesso:
        current_app.logger.info(f"Senha redefinida para usuário (ID: {id}) por {session.get('usuario_nome', 'N/A')}")
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('usuarios.listar_usuarios'))

@usuarios_bp.route('/excluir/<int:id>')
@login_obrigatorio
@admin_necessario
def excluir_usuario(id):
    """Exclui um usuário"""
    # Usar o serviço para excluir o usuário
    sucesso, mensagem = UsuarioService.excluir_usuario(id)
    
    if sucesso:
        current_app.logger.info(f"Usuário excluído (ID: {id}) por {session.get('usuario_nome', 'N/A')}")
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'error')
    
    return redirect(url_for('usuarios.listar_usuarios'))
