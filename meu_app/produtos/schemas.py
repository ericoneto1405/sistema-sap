"""
Schemas Pydantic para validação de dados do módulo de produtos.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal


class ProdutoCreateSchema(BaseModel):
    """Schema para criação de produto"""
    nome: str = Field(..., min_length=2, max_length=255, description="Nome do produto")
    codigo_interno: Optional[str] = Field(None, max_length=50, description="Código interno")
    categoria: str = Field(default='OUTROS', description="Categoria (CERVEJA, NAB, OUTROS)")
    preco_medio_compra: Decimal = Field(default=Decimal('0.00'), ge=0, description="Preço médio de compra")
    ean: Optional[str] = Field(None, max_length=50, description="Código EAN")
    
    @validator('nome')
    def validar_nome(cls, v):
        """Valida e sanitiza nome"""
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')
        return v.strip()
    
    @validator('categoria')
    def validar_categoria(cls, v):
        """Valida categoria"""
        categorias_validas = ['CERVEJA', 'NAB', 'OUTROS']
        v_upper = v.upper() if v else 'OUTROS'
        if v_upper not in categorias_validas:
            raise ValueError(f'Categoria deve ser uma de: {", ".join(categorias_validas)}')
        return v_upper
    
    @validator('codigo_interno')
    def validar_codigo_interno(cls, v):
        """Sanitiza código interno"""
        return v.strip() if v and v.strip() else None
    
    @validator('ean')
    def validar_ean(cls, v):
        """Sanitiza EAN"""
        return v.strip() if v and v.strip() else None
    
    @validator('preco_medio_compra')
    def validar_preco(cls, v):
        """Valida preço"""
        if v < 0:
            raise ValueError('Preço não pode ser negativo')
        return v


class ProdutoUpdateSchema(BaseModel):
    """Schema para atualização de produto"""
    nome: Optional[str] = Field(None, min_length=2, max_length=255)
    codigo_interno: Optional[str] = Field(None, max_length=50)
    categoria: Optional[str] = Field(None, description="Categoria (CERVEJA, NAB, OUTROS)")
    preco_medio_compra: Optional[Decimal] = Field(None, ge=0)
    ean: Optional[str] = Field(None, max_length=50)
    
    @validator('nome')
    def validar_nome(cls, v):
        """Valida e sanitiza nome"""
        if v is not None:
            if not v.strip():
                raise ValueError('Nome não pode ser vazio')
            return v.strip()
        return v
    
    @validator('categoria')
    def validar_categoria(cls, v):
        """Valida categoria"""
        if v is not None:
            categorias_validas = ['CERVEJA', 'NAB', 'OUTROS']
            v_upper = v.upper()
            if v_upper not in categorias_validas:
                raise ValueError(f'Categoria deve ser uma de: {", ".join(categorias_validas)}')
            return v_upper
        return v


class ProdutoResponseSchema(BaseModel):
    """Schema para resposta de produto"""
    id: int
    nome: str
    codigo_interno: Optional[str] = None
    categoria: str
    preco_medio_compra: Decimal
    ean: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class ProdutoBuscaSchema(BaseModel):
    """Schema para busca de produtos"""
    nome: Optional[str] = Field(None, max_length=255)
    categoria: Optional[str] = Field(None, max_length=20)
    codigo_interno: Optional[str] = Field(None, max_length=50)
    ean: Optional[str] = Field(None, max_length=50)

