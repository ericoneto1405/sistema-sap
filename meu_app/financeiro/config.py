"""
Configurações do módulo financeiro
"""
import os
from flask import current_app


class FinanceiroConfig:
    """Configurações centralizadas para o módulo financeiro"""
    
    # Configurações de upload de recibos
    UPLOAD_RECIBOS_DIR = 'uploads/recibos_pagamento'
    UPLOAD_TEMP_DIR = 'uploads/temp_recibos'
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf', '.doc', '.docx'}
    
    # Configurações de OCR - APENAS Google Vision
    OCR_CACHE_ENABLED = True
    OCR_CACHE_DIR = 'uploads/temp_recibos/.ocr_cache'
    OCR_TIMEOUT_SECONDS = 12
    
    # Configurações de quota OCR
    OCR_ENFORCE_LIMIT = True
    OCR_MONTHLY_LIMIT = 1000
    # OCR_BACKEND removido - usando APENAS Google Vision
    
    # Configurações Google Vision
    GOOGLE_VISION_CREDENTIALS_PATH = '/Users/ericobrandao/keys/gvision-credentials.json'
    GOOGLE_VISION_DETECTION_TYPE = 'TEXT_DETECTION'  # ou 'DOCUMENT_TEXT_DETECTION'
    
    # Configurações de validação
    PIX_REQUIRES_RECEIPT = False
    MIN_PAYMENT_VALUE = 0.01
    
    @classmethod
    def get_upload_directory(cls, upload_type: str = 'recibos') -> str:
        """
        Obtém o diretório de upload baseado no tipo
        
        Args:
            upload_type: Tipo de upload ('recibos' ou 'temp')
            
        Returns:
            str: Caminho completo do diretório
        """
        base_dir = current_app.root_path
        if upload_type == 'recibos':
            upload_dir = os.path.join(base_dir, '..', cls.UPLOAD_RECIBOS_DIR)
        elif upload_type == 'temp':
            upload_dir = os.path.join(base_dir, '..', cls.UPLOAD_TEMP_DIR)
        else:
            raise ValueError(f"Tipo de upload inválido: {upload_type}")
        
        # Criar diretório se não existir
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    
    @classmethod
    def get_max_file_size(cls) -> int:
        """Retorna o tamanho máximo de arquivo em bytes"""
        return cls.MAX_FILE_SIZE
    
    @classmethod
    def get_allowed_extensions(cls) -> set:
        """Retorna as extensões permitidas"""
        return cls.ALLOWED_EXTENSIONS
    
    @classmethod
    def is_pix_payment_requiring_receipt(cls) -> bool:
        """Verifica se pagamentos PIX requerem comprovante"""
        return cls.PIX_REQUIRES_RECEIPT
    
    @classmethod
    def is_ocr_limit_enforced(cls) -> bool:
        """Verifica se o limite de OCR está habilitado"""
        return cls.OCR_ENFORCE_LIMIT
    
    @classmethod
    def get_ocr_monthly_limit(cls) -> int:
        """Retorna o limite mensal de OCR"""
        return cls.OCR_MONTHLY_LIMIT
    
    # Método get_ocr_backend removido - usando APENAS Google Vision
