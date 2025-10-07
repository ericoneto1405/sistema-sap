"""
Schemas Pydantic para validação de dados do módulo coletas
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class ItemColetaSchema(BaseModel):
    """Schema para item de coleta"""
    item_id: int = Field(..., gt=0, description="ID do item do pedido")
    quantidade: int = Field(..., gt=0, description="Quantidade a ser coletada")
    
    @validator('quantidade')
    def validar_quantidade(cls, v):
        if v <= 0:
            raise ValueError('Quantidade deve ser maior que zero')
        return v


class ColetaRequestSchema(BaseModel):
    """Schema para requisição de coleta"""
    pedido_id: int = Field(..., gt=0, description="ID do pedido")
    responsavel_coleta_id: int = Field(..., gt=0, description="ID do responsável pela coleta")
    nome_retirada: str = Field(..., min_length=2, max_length=100, description="Nome de quem está retirando")
    documento_retirada: str = Field(..., min_length=5, max_length=20, description="Documento de quem está retirando")
    itens_coleta: List[ItemColetaSchema] = Field(..., min_items=1, description="Lista de itens para coleta")
    observacoes: Optional[str] = Field(None, max_length=500, description="Observações opcionais")
    
    @validator('nome_retirada')
    def validar_nome_retirada(cls, v):
        if not v or not v.strip():
            raise ValueError('Nome da retirada é obrigatório')
        return v.strip()
    
    @validator('documento_retirada')
    def validar_documento_retirada(cls, v):
        if not v or not v.strip():
            raise ValueError('Documento da retirada é obrigatório')
        return v.strip()


class ColetaResult(BaseModel):
    """Schema para resultado de operações de coleta"""
    sucesso: bool = Field(..., description="Indica se a operação foi bem-sucedida")
    dados: Optional[Any] = Field(None, description="Dados retornados pela operação")
    mensagem: str = Field(..., description="Mensagem descritiva do resultado")
    
    class Config:
        arbitrary_types_allowed = True


class ColetaResponseSchema(BaseModel):
    """Schema para resposta de coleta processada"""
    id: int = Field(..., description="ID da coleta")
    pedido_id: int = Field(..., description="ID do pedido")
    responsavel_coleta_id: int = Field(..., description="ID do responsável")
    nome_retirada: str = Field(..., description="Nome de quem retirou")
    documento_retirada: str = Field(..., description="Documento de quem retirou")
    status: str = Field(..., description="Status da coleta")
    data_coleta: datetime = Field(..., description="Data da coleta")
    observacoes: Optional[str] = Field(None, description="Observações")
    
    class Config:
        from_attributes = True
