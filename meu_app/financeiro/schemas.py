"""
Schemas Pydantic para validação de dados do módulo financeiro.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class PagamentoFinanceiroCreateSchema(BaseModel):
    """Schema para criação de pagamento via módulo financeiro"""
    pedido_id: int = Field(..., gt=0, description="ID do pedido")
    valor: Decimal = Field(..., gt=0, description="Valor do pagamento")
    metodo_pagamento: str = Field(..., min_length=2, max_length=255, description="Método de pagamento")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações")
    id_transacao: Optional[str] = Field(None, max_length=255, description="ID da transação")
    
    @validator('valor')
    def validar_valor(cls, v):
        """Valida valor"""
        if v <= 0:
            raise ValueError('Valor deve ser maior que zero')
        return v
    
    @validator('metodo_pagamento')
    def validar_metodo(cls, v):
        """Valida método de pagamento"""
        if not v or not v.strip():
            raise ValueError('Método de pagamento é obrigatório')
        return v.strip()


class ComprovantePagamentoUploadSchema(BaseModel):
    """Schema para upload de comprovante de pagamento"""
    pedido_id: int = Field(..., gt=0, description="ID do pedido")
    pagamento_id: Optional[int] = Field(None, gt=0, description="ID do pagamento (opcional)")
    
    @validator('pedido_id')
    def validar_pedido_id(cls, v):
        """Valida ID do pedido"""
        if v <= 0:
            raise ValueError('ID do pedido inválido')
        return v


class OcrResultadoSchema(BaseModel):
    """Schema para resultado de OCR"""
    sucesso: bool = Field(..., description="Indica se OCR foi bem-sucedido")
    confianca: Optional[Decimal] = Field(None, description="Nível de confiança do OCR")
    data_comprovante: Optional[date] = Field(None, description="Data extraída do comprovante")
    banco_emitente: Optional[str] = Field(None, description="Banco emissor")
    agencia_recebedor: Optional[str] = Field(None, description="Agência recebedor")
    conta_recebedor: Optional[str] = Field(None, description="Conta recebedor")
    chave_pix_recebedor: Optional[str] = Field(None, description="Chave PIX")
    valor_detectado: Optional[Decimal] = Field(None, description="Valor detectado no comprovante")
    mensagem: Optional[str] = Field(None, description="Mensagem de erro ou aviso")
    
    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat() if v else None
        }


class PagamentoFinanceiroResponseSchema(BaseModel):
    """Schema para resposta de pagamento financeiro"""
    id: int
    pedido_id: int
    valor: Decimal
    data_pagamento: datetime
    metodo_pagamento: str
    id_transacao: Optional[str] = None
    observacoes: Optional[str] = None
    caminho_recibo: Optional[str] = None
    data_comprovante: Optional[date] = None
    banco_emitente: Optional[str] = None
    agencia_recebedor: Optional[str] = None
    conta_recebedor: Optional[str] = None
    chave_pix_recebedor: Optional[str] = None
    ocr_confidence: Optional[Decimal] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat() if v else None
        }


class OcrQuotaStatusSchema(BaseModel):
    """Schema para status de quota de OCR"""
    ano: int
    mes: int
    contador: int
    limite: int
    disponivel: int
    percentual_uso: float
    
    class Config:
        from_attributes = True

