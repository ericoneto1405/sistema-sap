"""
Schemas Pydantic para validação de dados do módulo de log de atividades.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import json


class LogAtividadeCreateSchema(BaseModel):
    """Schema para criação de log de atividade"""
    usuario_id: Optional[int] = Field(None, description="ID do usuário (None para atividades do sistema)")
    tipo_atividade: str = Field(..., min_length=2, max_length=100, description="Tipo da atividade")
    titulo: str = Field(..., min_length=2, max_length=200, description="Título da atividade")
    descricao: str = Field(..., min_length=2, description="Descrição detalhada")
    modulo: str = Field(..., min_length=2, max_length=50, description="Módulo onde ocorreu")
    dados_extras: Optional[Dict[str, Any]] = Field(None, description="Dados extras em formato dict")
    ip_address: Optional[str] = Field(None, max_length=45, description="Endereço IP do usuário")
    
    @validator('tipo_atividade')
    def validar_tipo(cls, v):
        """Valida e sanitiza tipo"""
        if not v or not v.strip():
            raise ValueError('Tipo de atividade é obrigatório')
        return v.strip()
    
    @validator('titulo')
    def validar_titulo(cls, v):
        """Valida e sanitiza título"""
        if not v or not v.strip():
            raise ValueError('Título é obrigatório')
        return v.strip()
    
    @validator('descricao')
    def validar_descricao(cls, v):
        """Valida e sanitiza descrição"""
        if not v or not v.strip():
            raise ValueError('Descrição é obrigatória')
        return v.strip()
    
    @validator('modulo')
    def validar_modulo(cls, v):
        """Valida e sanitiza módulo"""
        if not v or not v.strip():
            raise ValueError('Módulo é obrigatório')
        return v.strip()
    
    @validator('dados_extras')
    def validar_dados_extras(cls, v):
        """Valida dados extras"""
        if v is not None:
            # Tenta serializar para garantir que é JSON válido
            try:
                json.dumps(v)
            except (TypeError, ValueError) as e:
                raise ValueError(f'Dados extras devem ser serializáveis em JSON: {str(e)}')
        return v


class LogAtividadeResponseSchema(BaseModel):
    """Schema para resposta de log de atividade"""
    id: int
    usuario_id: Optional[int] = None
    tipo_atividade: str
    titulo: str
    descricao: str
    modulo: str
    dados_extras: Optional[str] = None  # JSON string
    data_hora: datetime
    ip_address: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class LogAtividadeBuscaSchema(BaseModel):
    """Schema para busca/filtro de logs"""
    usuario_id: Optional[int] = None
    modulo: Optional[str] = Field(None, max_length=50)
    tipo_atividade: Optional[str] = Field(None, max_length=100)
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    limit: int = Field(default=100, gt=0, le=1000, description="Limite de resultados")


class LogAtividadeStatsSchema(BaseModel):
    """Schema para estatísticas de logs"""
    total_logs: int
    logs_por_modulo: Dict[str, int]
    logs_por_usuario: Dict[int, int]
    logs_ultimas_24h: int
    
    class Config:
        from_attributes = True

