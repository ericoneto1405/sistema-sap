from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import func, desc
from meu_app.models import Cliente, Pedido, ItemPedido, Produto
from meu_app import db

class VendedorService:
    
    @staticmethod
    def get_clientes_por_atividade():
        """
        Organiza clientes em 4 categorias baseadas na data da última compra
        """
        hoje = datetime.now().date()
        
        # Buscar todos os clientes com dados de última compra
        # Primeiro, buscar a data da última compra de cada cliente
        clientes_ultima_compra = db.session.query(
            Cliente.id,
            Cliente.nome,
            Cliente.fantasia,
            Cliente.telefone,
            func.max(Pedido.data).label('ultima_compra')
        ).join(Pedido, Cliente.id == Pedido.cliente_id)\
         .group_by(Cliente.id, Cliente.nome, Cliente.fantasia, Cliente.telefone)\
         .all()
        
        # Para cada cliente, buscar o valor da última compra
        clientes_com_pedidos = []
        for cliente in clientes_ultima_compra:
            # Buscar o valor total do último pedido
            ultimo_pedido = db.session.query(Pedido).filter(
                Pedido.cliente_id == cliente.id,
                Pedido.data == cliente.ultima_compra
            ).first()
            
            if ultimo_pedido:
                # Calcular valor total dos itens do último pedido
                valor_ultima_compra = db.session.query(
                    func.sum(ItemPedido.valor_total_venda)
                ).filter(ItemPedido.pedido_id == ultimo_pedido.id).scalar() or 0
            else:
                valor_ultima_compra = 0
            
            clientes_com_pedidos.append({
                'id': cliente.id,
                'nome': cliente.nome,
                'fantasia': cliente.fantasia,
                'telefone': cliente.telefone,
                'ultima_compra': cliente.ultima_compra,
                'valor_ultima_compra': float(valor_ultima_compra)
            })
        
        # Categorizar clientes
        ativos = []
        atencao = []
        em_risco = []
        inativos = []
        
        for cliente in clientes_com_pedidos:
            dias_desde_ultima_compra = (hoje - cliente['ultima_compra'].date()).days
            
            cliente_data = {
                'id': cliente['id'],
                'nome': cliente['nome'],
                'fantasia': cliente['fantasia'],
                'telefone': cliente['telefone'],
                'ultima_compra': cliente['ultima_compra'],
                'valor_ultima_compra': cliente['valor_ultima_compra'],
                'dias_sem_comprar': dias_desde_ultima_compra
            }
            
            if dias_desde_ultima_compra <= 7:
                ativos.append(cliente_data)
            elif dias_desde_ultima_compra <= 14:
                atencao.append(cliente_data)
            elif dias_desde_ultima_compra <= 30:
                em_risco.append(cliente_data)
            else:
                inativos.append(cliente_data)
        
        # Buscar clientes sem pedidos
        clientes_sem_pedidos = db.session.query(Cliente).filter(
            ~Cliente.id.in_([c['id'] for c in clientes_com_pedidos])
        ).all()
        
        for cliente in clientes_sem_pedidos:
            cliente_data = {
                'id': cliente.id,
                'nome': cliente.nome,
                'fantasia': cliente.fantasia,
                'telefone': cliente.telefone,
                'ultima_compra': None,
                'valor_ultima_compra': 0,
                'dias_sem_comprar': None
            }
            inativos.append(cliente_data)
        
        return {
            'ativos': ativos,
            'atencao': atencao,
            'em_risco': em_risco,
            'inativos': inativos
        }
    
    @staticmethod
    def get_detalhes_cliente(cliente_id):
        """
        Retorna detalhes completos de um cliente
        """
        cliente = Cliente.query.get_or_404(cliente_id)
        
        # Buscar pedidos do cliente
        pedidos = Pedido.query.filter_by(cliente_id=cliente_id)\
                             .order_by(desc(Pedido.data)).all()
        
        # Calcular estatísticas
        total_gasto = 0
        for pedido in pedidos:
            valor_pedido = db.session.query(
                func.sum(ItemPedido.valor_total_venda)
            ).filter(ItemPedido.pedido_id == pedido.id).scalar() or 0
            total_gasto += float(valor_pedido)
        
        total_pedidos = len(pedidos)
        ticket_medio = total_gasto / total_pedidos if total_pedidos > 0 else 0
        
        # Produtos diferentes comprados
        produtos_diferentes = db.session.query(
            func.count(func.distinct(ItemPedido.produto_id))
        ).join(Pedido, ItemPedido.pedido_id == Pedido.id)\
         .filter(Pedido.cliente_id == cliente_id).scalar() or 0
        
        # Primeiro e último pedido
        primeiro_pedido = pedidos[-1] if pedidos else None
        ultimo_pedido = pedidos[0] if pedidos else None
        
        # Detalhes dos pedidos
        pedidos_detalhados = []
        for pedido in pedidos:
            itens = ItemPedido.query.filter_by(pedido_id=pedido.id).all()
            
            itens_detalhados = []
            for item in itens:
                itens_detalhados.append({
                    'quantidade': item.quantidade,
                    'produto_nome': item.produto.nome,
                    'preco_unitario': float(item.preco_venda),
                    'subtotal': float(item.valor_total_venda)
                })
            
            # Calcular valor total do pedido
            valor_total_pedido = db.session.query(
                func.sum(ItemPedido.valor_total_venda)
            ).filter(ItemPedido.pedido_id == pedido.id).scalar() or 0
            
            pedidos_detalhados.append({
                'id': pedido.id,
                'data': pedido.data,
                'valor_total': float(valor_total_pedido),
                'status': pedido.status.value if pedido.status else 'N/A',
                'itens': itens_detalhados
            })
        
        return {
            'cliente': cliente,
            'estatisticas': {
                'total_gasto': total_gasto,
                'total_pedidos': total_pedidos,
                'ticket_medio': ticket_medio,
                'produtos_diferentes': produtos_diferentes,
                'primeiro_pedido': primeiro_pedido,
                'ultimo_pedido': ultimo_pedido
            },
            'pedidos': pedidos_detalhados
        }
    
    @staticmethod
    def get_rankings(periodo='todos'):
        """
        Retorna rankings de clientes
        """
        # Definir filtro de período
        filtro_data = None
        if periodo != 'todos':
            hoje = datetime.now().date()
            if periodo == 'ultimo_mes':
                filtro_data = hoje - timedelta(days=30)
            elif periodo == 'ultimos_3_meses':
                filtro_data = hoje - timedelta(days=90)
            elif periodo == 'ultimos_6_meses':
                filtro_data = hoje - timedelta(days=180)
            elif periodo == 'ultimo_ano':
                filtro_data = hoje - timedelta(days=365)
        
        # Query base - buscar clientes com pedidos
        query = db.session.query(
            Cliente.id,
            Cliente.nome,
            func.count(Pedido.id).label('total_pedidos')
        ).join(Pedido, Cliente.id == Pedido.cliente_id)
        
        if filtro_data:
            query = query.filter(Pedido.data >= filtro_data)
        
        clientes_data = query.group_by(Cliente.id, Cliente.nome).all()
        
        # Calcular valores totais e custos para cada cliente
        clientes_com_valores = []
        for cliente_data in clientes_data:
            # Calcular valor total (receita)
            valor_total = db.session.query(
                func.sum(ItemPedido.valor_total_venda)
            ).join(Pedido, ItemPedido.pedido_id == Pedido.id)\
             .filter(Pedido.cliente_id == cliente_data.id)
            
            if filtro_data:
                valor_total = valor_total.filter(Pedido.data >= filtro_data)
            
            valor_total = valor_total.scalar() or 0
            
            # Calcular custo total
            custo_total = db.session.query(
                func.sum(ItemPedido.valor_total_compra)
            ).join(Pedido, ItemPedido.pedido_id == Pedido.id)\
             .filter(Pedido.cliente_id == cliente_data.id)
            
            if filtro_data:
                custo_total = custo_total.filter(Pedido.data >= filtro_data)
            
            custo_total = custo_total.scalar() or 0
            
            clientes_com_valores.append({
                'id': cliente_data.id,
                'nome': cliente_data.nome,
                'valor_total': float(valor_total),
                'total_pedidos': cliente_data.total_pedidos,
                'custo_total': float(custo_total)
            })
        
        # Ranking por faturamento
        ranking_faturamento = sorted(
            clientes_com_valores, 
            key=lambda x: x['valor_total'], 
            reverse=True
        )[:20]
        
        # Ranking por diversidade (produtos diferentes)
        ranking_diversidade = []
        for cliente_data in clientes_com_valores:
            produtos_diferentes = db.session.query(
                func.count(func.distinct(ItemPedido.produto_id))
            ).join(Pedido, ItemPedido.pedido_id == Pedido.id)\
             .filter(Pedido.cliente_id == cliente_data['id'])
            
            if filtro_data:
                produtos_diferentes = produtos_diferentes.filter(Pedido.data >= filtro_data)
            
            produtos_diferentes = produtos_diferentes.scalar() or 0
            
            ranking_diversidade.append({
                'id': cliente_data['id'],
                'nome': cliente_data['nome'],
                'produtos_diferentes': produtos_diferentes,
                'valor_total': cliente_data['valor_total']
            })
        
        ranking_diversidade = sorted(
            ranking_diversidade,
            key=lambda x: x['produtos_diferentes'],
            reverse=True
        )[:20]
        
        # Ranking por margem de lucro
        ranking_margem = []
        for cliente_data in clientes_com_valores:
            lucro_total = cliente_data['valor_total'] - cliente_data['custo_total']
            margem_media = (lucro_total / cliente_data['valor_total']) * 100 if cliente_data['valor_total'] > 0 else 0
            
            ranking_margem.append({
                'id': cliente_data['id'],
                'nome': cliente_data['nome'],
                'lucro_total': lucro_total,
                'margem_media': margem_media
            })
        
        ranking_margem = sorted(
            ranking_margem,
            key=lambda x: x['lucro_total'],
            reverse=True
        )[:20]
        
        return {
            'faturamento': ranking_faturamento,
            'diversidade': ranking_diversidade,
            'margem': ranking_margem
        }
