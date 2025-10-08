from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, jsonify

log_atividades_bp = Blueprint('log_atividades', __name__, url_prefix='/log_atividades')
from .services import LogAtividadesService
from functools import wraps
from ..decorators import login_obrigatorio, admin_necessario

@log_atividades_bp.route('/', methods=['GET'])
@login_obrigatorio
@admin_necessario
def listar_atividades():
    """Lista atividades do sistema com paginação e filtros"""
    try:
        # Parâmetros de paginação
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filtros
        filtro_modulo = request.args.get('modulo')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Validar parâmetros
        if page < 1:
            page = 1
        if per_page not in [20, 50, 100]:
            per_page = 20
        
        # Buscar atividades com paginação
        service = LogAtividadesService()
        resultado = service.listar_atividades(
            filtro_modulo=filtro_modulo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            page=page,
            per_page=per_page
        )
        
        # Listar módulos disponíveis para filtro
        service = LogAtividadesService()
        modulos = service.listar_modulos()
        
        current_app.logger.info(f"Log de atividades acessado por {session.get('usuario_nome', 'N/A')}")
        
        return render_template('log_atividades.html', 
                             atividades=resultado['atividades'],
                             modulos=modulos,
                             filtro_modulo=filtro_modulo,
                             data_inicio=data_inicio or '',
                             data_fim=data_fim or '',
                             page=resultado['page'],
                             per_page=resultado['per_page'],
                             total_registros=resultado['total_registros'],
                             total_paginas=resultado['total_paginas'])
                             
    except ValueError as e:
        flash(f"Erro de validação: {str(e)}", 'error')
        return render_template('log_atividades.html', 
                             atividades=[],
                             modulos=[],
                             filtro_modulo='',
                             data_inicio='',
                             data_fim='',
                             page=1,
                             per_page=20,
                             total_registros=0,
                             total_paginas=0)
    except Exception as e:
        current_app.logger.error(f"Erro ao listar atividades: {str(e)}")
        flash(f"Erro ao carregar log de atividades: {str(e)}", 'error')
        return render_template('log_atividades.html', 
                             atividades=[],
                             modulos=[],
                             filtro_modulo='',
                             data_inicio='',
                             data_fim='',
                             page=1,
                             per_page=20,
                             total_registros=0,
                             total_paginas=0)

@log_atividades_bp.route('/atividade/<int:atividade_id>', methods=['GET'])
@login_obrigatorio
def visualizar_atividade(atividade_id):
    """Visualiza detalhes de uma atividade específica"""
    try:
        service = LogAtividadesService()
        atividade = service.buscar_atividade(atividade_id)
        
        if not atividade:
            flash("Atividade não encontrada", "error")
            return redirect(url_for('log_atividades.listar_atividades'))
        
        current_app.logger.info(f"Atividade #{atividade_id} visualizada por {session.get('usuario_nome', 'N/A')}")
        
        return render_template('visualizar_atividade.html', atividade=atividade)
        
    except Exception as e:
        current_app.logger.error(f"Erro ao visualizar atividade: {str(e)}")
        flash("Erro ao carregar atividade", "error")
        return redirect(url_for('log_atividades.listar_atividades'))

@log_atividades_bp.route('/limpar', methods=['POST'])
@login_obrigatorio
def limpar_logs():
    """Limpa logs antigos"""
    try:
        # Verificar se o usuário tem permissão de admin
        if not session.get('acesso_admin'):
            return jsonify({'success': False, 'message': 'Acesso negado. Apenas administradores podem limpar logs.'})
        
        dias = request.form.get('dias', 90, type=int)
        
        if dias < 1:
            return jsonify({'success': False, 'message': 'Número de dias deve ser maior que zero.'})
        
        service = LogAtividadesService()
        sucesso, mensagem, quantidade = service.limpar_logs_antigos(dias)
        
        if sucesso:
            current_app.logger.info(f"Logs limpos por {session.get('usuario_nome', 'N/A')}: {quantidade} registros")
        
        return jsonify({'success': sucesso, 'message': mensagem, 'quantidade': quantidade})
        
    except Exception as e:
        current_app.logger.error(f"Erro ao limpar logs: {str(e)}")
        return jsonify({'success': False, 'message': f'Erro ao limpar logs: {str(e)}'})

@log_atividades_bp.route('/estatisticas', methods=['GET'])
@login_obrigatorio
def obter_estatisticas():
    """Obtém estatísticas dos logs de atividades"""
    try:
        service = LogAtividadesService()
        stats = service.obter_estatisticas()
        
        current_app.logger.info(f"Estatísticas de log acessadas por {session.get('usuario_nome', 'N/A')}")
        
        return jsonify(stats)
        
    except Exception as e:
        current_app.logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({'error': str(e)}), 500

@log_atividades_bp.route('/exportar', methods=['GET'])
@login_obrigatorio
def exportar_logs():
    """Exporta logs de atividades"""
    try:
        # Parâmetros de filtro
        filtro_modulo = request.args.get('modulo')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Buscar todas as atividades (sem paginação)
        service = LogAtividadesService()
        resultado = service.listar_atividades(
            filtro_modulo=filtro_modulo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            page=1,
            per_page=10000  # Número alto para pegar todos
        )
        
        # Preparar dados para exportação
        dados_exportacao = []
        for atividade in resultado['atividades']:
            dados_exportacao.append({
                'id': atividade.id,
                'usuario': atividade.usuario.nome if atividade.usuario else 'N/A',
                'tipo_atividade': atividade.tipo_atividade,
                'titulo': atividade.titulo,
                'descricao': atividade.descricao,
                'modulo': atividade.modulo,
                'data_criacao': atividade.data_criacao.strftime('%d/%m/%Y %H:%M:%S') if atividade.data_criacao else 'N/A',
                'dados_extras': atividade.dados_extras
            })
        
        current_app.logger.info(f"Exportação de logs solicitada por {session.get('usuario_nome', 'N/A')}")
        
        return jsonify({
            'success': True,
            'dados': dados_exportacao,
            'total': len(dados_exportacao),
            'filtros': {
                'modulo': filtro_modulo,
                'data_inicio': data_inicio,
                'data_fim': data_fim
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Erro ao exportar logs: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
