"""
Schemas Pydantic para validação de dados do módulo de usuários.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional


class UsuarioCreateSchema(BaseModel):
    """Schema para criação de usuário"""
    nome: str = Field(..., min_length=3, max_length=50, description="Nome de usuário (único)")
    senha: str = Field(..., min_length=6, max_length=128, description="Senha do usuário")
    tipo: str = Field(..., description="Tipo de usuário (admin ou comum)")
    acesso_clientes: bool = Field(default=False, description="Acesso ao módulo de clientes")
    acesso_produtos: bool = Field(default=False, description="Acesso ao módulo de produtos")
    acesso_pedidos: bool = Field(default=False, description="Acesso ao módulo de pedidos")
    acesso_financeiro: bool = Field(default=False, description="Acesso ao módulo financeiro")
    acesso_logistica: bool = Field(default=False, description="Acesso ao módulo de logística")
    
    @validator('nome')
    def validar_nome(cls, v):
        """Valida e sanitiza nome"""
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')
        # Remove espaços e caracteres especiais perigosos
        nome_limpo = v.strip()
        if len(nome_limpo) < 3:
            raise ValueError('Nome deve ter pelo menos 3 caracteres')
        return nome_limpo
    
    @validator('senha')
    def validar_senha(cls, v):
        """Valida senha"""
        if not v or len(v) < 6:
            raise ValueError('Senha deve ter pelo menos 6 caracteres')
        return v
    
    @validator('tipo')
    def validar_tipo(cls, v):
        """Valida tipo de usuário"""
        tipos_validos = ['admin', 'comum']
        if v not in tipos_validos:
            raise ValueError(f'Tipo deve ser um de: {", ".join(tipos_validos)}')
        return v


class UsuarioUpdateSchema(BaseModel):
    """Schema para atualização de usuário"""
    nome: Optional[str] = Field(None, min_length=3, max_length=50)
    senha: Optional[str] = Field(None, min_length=6, max_length=128)
    tipo: Optional[str] = None
    acesso_clientes: Optional[bool] = None
    acesso_produtos: Optional[bool] = None
    acesso_pedidos: Optional[bool] = None
    acesso_financeiro: Optional[bool] = None
    acesso_logistica: Optional[bool] = None
    
    @validator('nome')
    def validar_nome(cls, v):
        """Valida e sanitiza nome"""
        if v is not None:
            if not v.strip():
                raise ValueError('Nome não pode ser vazio')
            if len(v.strip()) < 3:
                raise ValueError('Nome deve ter pelo menos 3 caracteres')
            return v.strip()
        return v
    
    @validator('senha')
    def validar_senha(cls, v):
        """Valida senha"""
        if v is not None and len(v) < 6:
            raise ValueError('Senha deve ter pelo menos 6 caracteres')
        return v
    
    @validator('tipo')
    def validar_tipo(cls, v):
        """Valida tipo de usuário"""
        if v is not None:
            tipos_validos = ['admin', 'comum']
            if v not in tipos_validos:
                raise ValueError(f'Tipo deve ser um de: {", ".join(tipos_validos)}')
        return v


class UsuarioResponseSchema(BaseModel):
    """Schema para resposta de usuário (sem senha)"""
    id: int
    nome: str
    tipo: str
    acesso_clientes: bool
    acesso_produtos: bool
    acesso_pedidos: bool
    acesso_financeiro: bool
    acesso_logistica: bool
    
    class Config:
        from_attributes = True


class UsuarioLoginSchema(BaseModel):
    """Schema para login de usuário"""
    nome: str = Field(..., min_length=3, max_length=50, description="Nome de usuário")
    senha: str = Field(..., min_length=6, max_length=128, description="Senha")
    
    @validator('nome')
    def validar_nome(cls, v):
        """Valida nome"""
        if not v or not v.strip():
            raise ValueError('Nome é obrigatório')
        return v.strip()
    
    @validator('senha')
    def validar_senha(cls, v):
        """Valida senha"""
        if not v or len(v) < 6:
            raise ValueError('Senha inválida')
        return v

