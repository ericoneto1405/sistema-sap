from flask import render_template, request, jsonify
from meu_app.decorators import login_obrigatorio, permissao_necessaria
from . import vendedor_bp
from .services import VendedorService

@vendedor_bp.route('/')
@login_obrigatorio
@permissao_necessaria('acesso_clientes')
def dashboard():
    """
    TELA 1: Visão de Atividade dos Clientes
    """
    clientes_por_atividade = VendedorService.get_clientes_por_atividade()
    
    return render_template('vendedor/dashboard.html', 
                         clientes=clientes_por_atividade)

@vendedor_bp.route('/cliente/<int:cliente_id>')
@login_obrigatorio
@permissao_necessaria('acesso_clientes')
def detalhes_cliente(cliente_id):
    """
    TELA 2: Detalhes do Cliente
    """
    detalhes = VendedorService.get_detalhes_cliente(cliente_id)
    
    return render_template('vendedor/detalhes_cliente.html', 
                         detalhes=detalhes)

@vendedor_bp.route('/rankings')
@login_obrigatorio
@permissao_necessaria('acesso_clientes')
def rankings():
    """
    TELA 3: Rankings
    """
    periodo = request.args.get('periodo', 'todos')
    rankings_data = VendedorService.get_rankings(periodo)
    
    return render_template('vendedor/rankings.html', 
                         rankings=rankings_data,
                         periodo_atual=periodo)

@vendedor_bp.route('/api/buscar-cliente')
@login_obrigatorio
@permissao_necessaria('acesso_clientes')
def buscar_cliente():
    """
    API para busca de clientes
    """
    termo = request.args.get('q', '')
    
    if not termo:
        return jsonify({'clientes': []})
    
    # Buscar clientes que contenham o termo
    from meu_app.models import Cliente
    clientes = Cliente.query.filter(
        Cliente.nome.contains(termo) | 
        Cliente.fantasia.contains(termo)
    ).limit(10).all()
    
    resultados = []
    for cliente in clientes:
        # Buscar última compra
        from meu_app.models import Pedido
        ultimo_pedido = Pedido.query.filter_by(cliente_id=cliente.id)\
                                   .order_by(Pedido.data.desc()).first()
        
        resultados.append({
            'id': cliente.id,
            'nome': cliente.nome,
            'fantasia': cliente.fantasia,
            'ultima_compra': ultimo_pedido.data if ultimo_pedido else None,
            'valor_ultima_compra': float(ultimo_pedido.receita_total or 0) if ultimo_pedido else 0
        })
    
    return jsonify({'clientes': resultados})
