"""
Repository para o módulo de log de atividades.

Implementa o padrão Repository para acesso a dados de logs.
"""

from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from ..models import db, LogAtividade


class LogAtividadeRepository:
    """Repository para operações de banco de dados de logs de atividade."""
    
    def __init__(self):
        """Inicializa o repositório"""
        self.db = db
    
    def buscar_por_id(self, log_id: int) -> Optional[LogAtividade]:
        """Busca log por ID."""
        try:
            return LogAtividade.query.get(log_id)
        except SQLAlchemyError as e:
            print(f"Erro ao buscar log por ID {log_id}: {str(e)}")
            return None
    
    def listar_todos(self, limit: int = 1000) -> List[LogAtividade]:
        """Lista todos os logs com limite."""
        try:
            return LogAtividade.query.order_by(LogAtividade.data_hora.desc())\
                .limit(limit).all()
        except SQLAlchemyError as e:
            print(f"Erro ao listar logs: {str(e)}")
            return []
    
    def listar_por_usuario(self, usuario_id: int, limit: int = 500) -> List[LogAtividade]:
        """Lista logs de um usuário específico."""
        try:
            return LogAtividade.query.filter_by(usuario_id=usuario_id)\
                .order_by(LogAtividade.data_hora.desc())\
                .limit(limit).all()
        except SQLAlchemyError as e:
            print(f"Erro ao listar logs do usuário {usuario_id}: {str(e)}")
            return []
    
    def listar_por_modulo(self, modulo: str, limit: int = 500) -> List[LogAtividade]:
        """Lista logs de um módulo específico."""
        try:
            return LogAtividade.query.filter_by(modulo=modulo)\
                .order_by(LogAtividade.data_hora.desc())\
                .limit(limit).all()
        except SQLAlchemyError as e:
            print(f"Erro ao listar logs do módulo '{modulo}': {str(e)}")
            return []
    
    def listar_por_tipo(self, tipo_atividade: str, limit: int = 500) -> List[LogAtividade]:
        """Lista logs de um tipo de atividade."""
        try:
            return LogAtividade.query.filter_by(tipo_atividade=tipo_atividade)\
                .order_by(LogAtividade.data_hora.desc())\
                .limit(limit).all()
        except SQLAlchemyError as e:
            print(f"Erro ao listar logs do tipo '{tipo_atividade}': {str(e)}")
            return []
    
    def listar_por_periodo(self, data_inicio: datetime, data_fim: datetime, limit: int = 1000) -> List[LogAtividade]:
        """Lista logs em um período."""
        try:
            return LogAtividade.query.filter(
                LogAtividade.data_hora >= data_inicio,
                LogAtividade.data_hora <= data_fim
            ).order_by(LogAtividade.data_hora.desc())\
            .limit(limit).all()
        except SQLAlchemyError as e:
            print(f"Erro ao listar logs por período: {str(e)}")
            return []
    
    def criar(self, log: LogAtividade) -> LogAtividade:
        """Cria novo registro de log."""
        try:
            self.db.session.add(log)
            self.db.session.commit()
            return log
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Erro ao criar log: {str(e)}")
            # Não propaga exceção para não quebrar fluxo principal
            # Log é registro secundário
            return log
    
    def contar_total(self) -> int:
        """Conta total de logs."""
        try:
            return LogAtividade.query.count()
        except SQLAlchemyError as e:
            print(f"Erro ao contar logs: {str(e)}")
            return 0
    
    def contar_por_usuario(self, usuario_id: int) -> int:
        """Conta logs de um usuário."""
        try:
            return LogAtividade.query.filter_by(usuario_id=usuario_id).count()
        except SQLAlchemyError as e:
            print(f"Erro ao contar logs do usuário {usuario_id}: {str(e)}")
            return 0
    
    def limpar_logs_antigos(self, data_limite: datetime) -> int:
        """
        Remove logs anteriores à data limite.
        
        Args:
            data_limite: Data limite (logs mais antigos serão removidos)
            
        Returns:
            Número de registros removidos
        """
        try:
            logs_antigos = LogAtividade.query.filter(
                LogAtividade.data_hora < data_limite
            ).all()
            
            count = len(logs_antigos)
            for log in logs_antigos:
                self.db.session.delete(log)
            
            self.db.session.commit()
            return count
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Erro ao limpar logs antigos: {str(e)}")
            return 0

