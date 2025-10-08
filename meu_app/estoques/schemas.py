"""
Schemas Pydantic para validação de dados do módulo de estoques.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class EstoqueCreateSchema(BaseModel):
    """Schema para criação de estoque"""
    produto_id: int = Field(..., gt=0, description="ID do produto")
    quantidade: int = Field(..., ge=0, description="Quantidade em estoque")
    conferente: str = Field(..., min_length=2, max_length=100, description="Nome do conferente")
    status: str = Field(default='Contagem', description="Status do estoque")
    
    @validator('conferente')
    def validar_conferente(cls, v):
        """Valida e sanitiza conferente"""
        if not v or not v.strip():
            raise ValueError('Conferente é obrigatório')
        return v.strip()
    
    @validator('status')
    def validar_status(cls, v):
        """Valida status"""
        status_validos = ['Contagem', 'Confirmado', 'Divergente']
        if v not in status_validos:
            raise ValueError(f'Status deve ser um de: {", ".join(status_validos)}')
        return v


class EstoqueUpdateSchema(BaseModel):
    """Schema para atualização de estoque"""
    quantidade: Optional[int] = Field(None, ge=0)
    conferente: Optional[str] = Field(None, min_length=2, max_length=100)
    status: Optional[str] = None
    
    @validator('conferente')
    def validar_conferente(cls, v):
        """Valida e sanitiza conferente"""
        if v is not None:
            if not v.strip():
                raise ValueError('Conferente não pode ser vazio')
            return v.strip()
        return v


class MovimentacaoEstoqueCreateSchema(BaseModel):
    """Schema para criação de movimentação de estoque"""
    produto_id: int = Field(..., gt=0, description="ID do produto")
    tipo_movimentacao: str = Field(..., description="Tipo (Entrada, Saída, Ajuste)")
    quantidade_movimentada: int = Field(..., description="Quantidade movimentada")
    motivo: str = Field(..., min_length=2, max_length=200, description="Motivo da movimentação")
    responsavel: str = Field(..., min_length=2, max_length=100, description="Responsável")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações")
    
    @validator('tipo_movimentacao')
    def validar_tipo(cls, v):
        """Valida tipo de movimentação"""
        tipos_validos = ['Entrada', 'Saída', 'Ajuste']
        if v not in tipos_validos:
            raise ValueError(f'Tipo deve ser um de: {", ".join(tipos_validos)}')
        return v
    
    @validator('motivo')
    def validar_motivo(cls, v):
        """Valida motivo"""
        if not v or not v.strip():
            raise ValueError('Motivo é obrigatório')
        return v.strip()
    
    @validator('responsavel')
    def validar_responsavel(cls, v):
        """Valida responsável"""
        if not v or not v.strip():
            raise ValueError('Responsável é obrigatório')
        return v.strip()


class EstoqueResponseSchema(BaseModel):
    """Schema para resposta de estoque"""
    id: int
    produto_id: int
    quantidade: int
    conferente: str
    data_conferencia: datetime
    data_entrada: datetime
    data_modificacao: datetime
    status: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MovimentacaoEstoqueResponseSchema(BaseModel):
    """Schema para resposta de movimentação"""
    id: int
    produto_id: int
    tipo_movimentacao: str
    quantidade_anterior: int
    quantidade_movimentada: int
    quantidade_atual: int
    motivo: str
    responsavel: str
    data_movimentacao: datetime
    observacoes: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

