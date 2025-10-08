"""
Repository para o módulo de produtos.

Implementa o padrão Repository para acesso a dados de produtos.
"""

from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from ..models import db, Produto


class ProdutoRepository:
    """Repository para operações de banco de dados de produtos."""
    
    def __init__(self):
        """Inicializa o repositório"""
        self.db = db
    
    def buscar_por_id(self, produto_id: int) -> Optional[Produto]:
        """
        Busca produto por ID.
        
        Args:
            produto_id: ID do produto
            
        Returns:
            Produto encontrado ou None
        """
        try:
            return Produto.query.get(produto_id)
        except SQLAlchemyError as e:
            print(f"Erro ao buscar produto por ID {produto_id}: {str(e)}")
            return None
    
    def buscar_por_nome(self, nome: str) -> Optional[Produto]:
        """
        Busca produto por nome exato.
        
        Args:
            nome: Nome do produto
            
        Returns:
            Produto encontrado ou None
        """
        try:
            return Produto.query.filter_by(nome=nome).first()
        except SQLAlchemyError as e:
            print(f"Erro ao buscar produto por nome '{nome}': {str(e)}")
            return None
    
    def buscar_por_codigo(self, codigo_interno: str) -> Optional[Produto]:
        """
        Busca produto por código interno.
        
        Args:
            codigo_interno: Código interno do produto
            
        Returns:
            Produto encontrado ou None
        """
        try:
            return Produto.query.filter_by(codigo_interno=codigo_interno).first()
        except SQLAlchemyError as e:
            print(f"Erro ao buscar produto por código '{codigo_interno}': {str(e)}")
            return None
    
    def buscar_por_ean(self, ean: str) -> Optional[Produto]:
        """
        Busca produto por EAN.
        
        Args:
            ean: Código EAN do produto
            
        Returns:
            Produto encontrado ou None
        """
        try:
            return Produto.query.filter_by(ean=ean).first()
        except SQLAlchemyError as e:
            print(f"Erro ao buscar produto por EAN '{ean}': {str(e)}")
            return None
    
    def buscar_por_nome_parcial(self, nome: str) -> List[Produto]:
        """
        Busca produtos por nome parcial (LIKE).
        
        Args:
            nome: Parte do nome do produto
            
        Returns:
            Lista de produtos encontrados
        """
        try:
            return Produto.query.filter(Produto.nome.ilike(f'%{nome}%')).all()
        except SQLAlchemyError as e:
            print(f"Erro ao buscar produtos por nome parcial '{nome}': {str(e)}")
            return []
    
    def listar_todos(self) -> List[Produto]:
        """
        Lista todos os produtos.
        
        Returns:
            Lista de todos os produtos
        """
        try:
            return Produto.query.order_by(Produto.nome).all()
        except SQLAlchemyError as e:
            print(f"Erro ao listar produtos: {str(e)}")
            return []
    
    def listar_por_categoria(self, categoria: str) -> List[Produto]:
        """
        Lista produtos por categoria.
        
        Args:
            categoria: Categoria do produto (CERVEJA, NAB, OUTROS)
            
        Returns:
            Lista de produtos da categoria
        """
        try:
            return Produto.query.filter_by(categoria=categoria).order_by(Produto.nome).all()
        except SQLAlchemyError as e:
            print(f"Erro ao listar produtos por categoria '{categoria}': {str(e)}")
            return []
    
    def criar(self, produto: Produto) -> Produto:
        """
        Cria novo produto no banco de dados.
        
        Args:
            produto: Objeto Produto a ser criado
            
        Returns:
            Produto criado com ID
            
        Raises:
            SQLAlchemyError: Em caso de erro no banco
        """
        try:
            self.db.session.add(produto)
            self.db.session.commit()
            return produto
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Erro ao criar produto: {str(e)}")
            raise
    
    def atualizar(self, produto: Produto) -> Produto:
        """
        Atualiza produto existente.
        
        Args:
            produto: Produto com dados atualizados
            
        Returns:
            Produto atualizado
            
        Raises:
            SQLAlchemyError: Em caso de erro no banco
        """
        try:
            self.db.session.commit()
            return produto
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Erro ao atualizar produto: {str(e)}")
            raise
    
    def excluir(self, produto: Produto) -> bool:
        """
        Exclui produto do banco de dados.
        
        Args:
            produto: Produto a ser excluído
            
        Returns:
            True se excluído com sucesso
            
        Raises:
            SQLAlchemyError: Em caso de erro no banco
        """
        try:
            self.db.session.delete(produto)
            self.db.session.commit()
            return True
        except SQLAlchemyError as e:
            self.db.session.rollback()
            print(f"Erro ao excluir produto: {str(e)}")
            raise
    
    def contar_total(self) -> int:
        """
        Conta total de produtos cadastrados.
        
        Returns:
            Número total de produtos
        """
        try:
            return Produto.query.count()
        except SQLAlchemyError as e:
            print(f"Erro ao contar produtos: {str(e)}")
            return 0
    
    def verificar_nome_existe(self, nome: str, excluir_id: Optional[int] = None) -> bool:
        """
        Verifica se já existe produto com o nome.
        
        Args:
            nome: Nome a verificar
            excluir_id: ID do produto a excluir da verificação (para edição)
            
        Returns:
            True se nome já existe
        """
        try:
            query = Produto.query.filter_by(nome=nome)
            if excluir_id:
                query = query.filter(Produto.id != excluir_id)
            return query.first() is not None
        except SQLAlchemyError as e:
            print(f"Erro ao verificar nome '{nome}': {str(e)}")
            return False

