"""
Repository para o módulo de estoques.

Implementa o padrão Repository para acesso a dados de estoques e movimentações.
"""

from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from ..models import db, Estoque, MovimentacaoEstoque, Produto


class EstoqueRepository:
    """Repository para operações de banco de dados de estoques."""
    
    def __init__(self):
        """Inicializa o repositório"""
        self.db = db
    
    def buscar_por_id(self, estoque_id: int) -> Optional[Estoque]:
        """Busca estoque por ID."""
        try:
            return Estoque.query.get(estoque_id)
        except SQLAlchemyError as e:
            print(f"Erro ao buscar estoque por ID {estoque_id}: {str(e)}")
            return None
    
    def buscar_por_produto_id(self, produto_id: int) -> Optional[Estoque]:
        """Busca estoque por ID do produto."""
        try:
            return Estoque.query.filter_by(produto_id=produto_id).first()
        except SQLAlchemyError as e:
            print(f"Erro ao buscar estoque por produto ID {produto_id}: {str(e)}")
            return None
    
    def listar_todos(self) -> List[Estoque]:
        """Lista todos os estoques."""
        try:
            return Estoque.query.join(Produto).order_by(Produto.nome).all()
        except SQLAlchemyError as e:
            print(f"Erro ao listar estoques: {str(e)}")
            return []
    
    def listar_por_status(self, status: str) -> List[Estoque]:
        """Lista estoques por status."""
        try:
            return Estoque.query.filter_by(status=status).join(Produto).order_by(Produto.nome).all()
        except SQLAlchemyError as e:
            print(f"Erro ao listar estoques por status '{status}': {str(e)}")
            return []
    
    def criar(self, estoque: Estoque) -> Estoque:
        """Cria novo registro de estoque."""
        try:
            self.db.session.add(estoque)
            self.db.session.commit()
            return estoque
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Erro ao criar estoque: {str(e)}")
            raise
    
    def atualizar(self, estoque: Estoque) -> Estoque:
        """Atualiza estoque existente."""
        try:
            self.db.session.commit()
            return estoque
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Erro ao atualizar estoque: {str(e)}")
            raise
    
    def excluir(self, estoque: Estoque) -> bool:
        """Exclui estoque do banco de dados."""
        try:
            self.db.session.delete(estoque)
            self.db.session.commit()
            return True
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Erro ao excluir estoque: {str(e)}")
            raise


class MovimentacaoEstoqueRepository:
    """Repository para operações de movimentações de estoque."""
    
    def __init__(self):
        """Inicializa o repositório"""
        self.db = db
    
    def buscar_por_id(self, movimentacao_id: int) -> Optional[MovimentacaoEstoque]:
        """Busca movimentação por ID."""
        try:
            return MovimentacaoEstoque.query.get(movimentacao_id)
        except SQLAlchemyError as e:
            print(f"Erro ao buscar movimentação por ID {movimentacao_id}: {str(e)}")
            return None
    
    def listar_por_produto(self, produto_id: int, limit: int = 100) -> List[MovimentacaoEstoque]:
        """Lista movimentações de um produto."""
        try:
            return MovimentacaoEstoque.query.filter_by(produto_id=produto_id)\
                .order_by(MovimentacaoEstoque.data_movimentacao.desc())\
                .limit(limit).all()
        except SQLAlchemyError as e:
            print(f"Erro ao listar movimentações do produto {produto_id}: {str(e)}")
            return []
    
    def listar_todas(self, limit: int = 1000) -> List[MovimentacaoEstoque]:
        """Lista todas as movimentações."""
        try:
            return MovimentacaoEstoque.query\
                .order_by(MovimentacaoEstoque.data_movimentacao.desc())\
                .limit(limit).all()
        except SQLAlchemyError as e:
            print(f"Erro ao listar movimentações: {str(e)}")
            return []
    
    def criar(self, movimentacao: MovimentacaoEstoque) -> MovimentacaoEstoque:
        """Registra nova movimentação de estoque."""
        try:
            self.db.session.add(movimentacao)
            self.db.session.commit()
            return movimentacao
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Erro ao criar movimentação: {str(e)}")
            raise

