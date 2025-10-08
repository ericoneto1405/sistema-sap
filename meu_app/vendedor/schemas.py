"""
Schemas Pydantic para validação de dados do módulo vendedor.

O módulo vendedor não possui models próprios, mas usa agregações
de clientes e pedidos. Estes schemas definem as respostas específicas.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal


class ClienteAtividadeSchema(BaseModel):
    """Schema para cliente com dados de atividade"""
    id: int
    nome: str
    fantasia: Optional[str] = None
    telefone: str
    ultima_compra: Optional[date] = None
    valor_ultima_compra: Decimal
    dias_desde_ultima_compra: Optional[int] = None
    categoria_atividade: str  # ativo, pouco_ativo, inativo, novo
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat() if v else None
        }


class DetalhesClienteSchema(BaseModel):
    """Schema para detalhes completos do cliente"""
    id: int
    nome: str
    fantasia: Optional[str] = None
    telefone: str
    endereco: str
    cidade: str
    total_compras: Decimal
    total_pedidos: int
    ticket_medio: Decimal
    ultima_compra: Optional[date] = None
    produtos_mais_comprados: List[Dict[str, Any]]
    historico_pedidos: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }


class RankingClienteSchema(BaseModel):
    """Schema para ranking de clientes"""
    posicao: int
    cliente_id: int
    cliente_nome: str
    valor_total: Decimal
    quantidade_pedidos: int
    ticket_medio: Decimal
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class RankingProdutoSchema(BaseModel):
    """Schema para ranking de produtos"""
    posicao: int
    produto_id: int
    produto_nome: str
    quantidade_vendida: int
    valor_total: Decimal
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class RankingsResponseSchema(BaseModel):
    """Schema para resposta completa de rankings"""
    periodo: str
    top_clientes: List[RankingClienteSchema]
    top_produtos: List[RankingProdutoSchema]
    
    class Config:
        from_attributes = True


class ClientesBuscaSchema(BaseModel):
    """Schema para busca de clientes no módulo vendedor"""
    termo: str = Field(..., min_length=2, description="Termo de busca")
    categoria: Optional[str] = Field(None, description="Categoria de atividade")
    
    class Config:
        from_attributes = True

