from flask import render_template, request, jsonify
from meu_app.decorators import login_obrigatorio, permissao_necessaria
from app.auth.rbac import requires_vendedor
from meu_app.cache import cached_with_invalidation
from . import vendedor_bp
from .services import VendedorService

@vendedor_bp.route('/')
@login_obrigatorio
@requires_vendedor
@permissao_necessaria('acesso_clientes')
@cached_with_invalidation(
    timeout=600,  # 10 minutos
    key_prefix='vendedor_dashboard',
    invalidate_on=['pedido.criado', 'pedido.atualizado', 'cliente.atualizado']
)
def dashboard():
    """
    Dashboard renovado com cards resumo e rankings
    
    Cache: 10 minutos
    Invalidação: pedidos e clientes atualizados
    """
    resumo = VendedorService.get_resumo_dashboard()
    
    # Rankings
    rankings_data = VendedorService.get_rankings('todos')
    ranking_faturamento = rankings_data['faturamento'][:10]
    ranking_margem = rankings_data['margem'][:10]
    ranking_produtos = VendedorService.get_ranking_produtos(10)
    
    return render_template('vendedor/dashboard.html',
                         resumo=resumo,
                         ranking_faturamento=ranking_faturamento,
                         ranking_margem=ranking_margem,
                         ranking_produtos=ranking_produtos)

@vendedor_bp.route('/cliente/<int:cliente_id>')
@login_obrigatorio
@permissao_necessaria('acesso_clientes')
@cached_with_invalidation(
    timeout=300,  # 5 minutos
    key_prefix='cliente_detalhes',
    invalidate_on=['pedido.criado', 'pedido.atualizado', 'cliente.atualizado']
)
def detalhes_cliente(cliente_id):
    """
    TELA 2: Detalhes do Cliente
    
    Cache: 5 minutos (queries pesadas com joins)
    Invalidação: pedidos e clientes atualizados
    """
    detalhes = VendedorService.get_detalhes_cliente(cliente_id)
    
    return render_template('vendedor/detalhes_cliente.html', 
                         detalhes=detalhes)

@vendedor_bp.route('/rankings')
@login_obrigatorio
@permissao_necessaria('acesso_clientes')
@cached_with_invalidation(
    timeout=900,  # 15 minutos
    key_prefix='vendedor_rankings',
    invalidate_on=['pedido.criado', 'pedido.atualizado']
)
def rankings():
    """
    TELA 3: Rankings
    
    Cache: 15 minutos (análise pesada)
    Invalidação: pedidos atualizados
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

@vendedor_bp.route('/api/clientes-por-periodo/<periodo>')
@login_obrigatorio
@permissao_necessaria('acesso_clientes')
def api_clientes_por_periodo(periodo):
    """API para buscar clientes por período"""
    clientes = VendedorService.get_clientes_por_periodo(periodo)
    return jsonify({'clientes': clientes})

@vendedor_bp.route('/api/cliente/<int:cliente_id>/pedidos')
@login_obrigatorio
@permissao_necessaria('acesso_clientes')
def api_pedidos_cliente(cliente_id):
    """API para buscar pedidos de um cliente"""
    pedidos = VendedorService.get_pedidos_cliente(cliente_id)
    return jsonify({'pedidos': pedidos})

@vendedor_bp.route('/api/cliente/<int:cliente_id>/produtos')
@login_obrigatorio
@permissao_necessaria('acesso_clientes')
def api_produtos_cliente(cliente_id):
    """API para buscar produtos compilados de um cliente"""
    produtos = VendedorService.get_produtos_cliente(cliente_id)
    return jsonify({'produtos': produtos})
