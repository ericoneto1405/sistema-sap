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
    
    # Configurações de OCR - Google Vision
    OCR_CACHE_ENABLED = True
    OCR_CACHE_DIR = 'uploads/temp_recibos/.ocr_cache'
    OCR_OPERATION_TIMEOUT = 120
    OCR_MAX_PDF_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Configurações de quota OCR
    OCR_ENFORCE_LIMIT = True
    OCR_MONTHLY_LIMIT = 1000
    
    # Configurações Google Vision
    GOOGLE_VISION_CREDENTIALS_PATH = '/Users/ericobrandao/keys/gvision-credentials.json'
    GOOGLE_VISION_DETECTION_TYPE = 'TEXT_DETECTION'  # ou 'DOCUMENT_TEXT_DETECTION'
    GOOGLE_VISION_INPUT_BUCKET = 'sap-ocr-input'
    GOOGLE_VISION_INPUT_PREFIX = 'financeiro/ocr/input'
    GOOGLE_VISION_OUTPUT_BUCKET = 'sap-ocr-output'
    GOOGLE_VISION_OUTPUT_PREFIX = 'financeiro/ocr/output'
    
    # Configurações de validação
    PIX_REQUIRES_RECEIPT = False
    MIN_PAYMENT_VALUE = 0.01
    
    # Configurações do RECEBEDOR (Grupo Sertão) - Para validação de comprovantes
    RECEBEDOR_PIX = 'pix@gruposertao.com'
    RECEBEDOR_CNPJ = '30080209000416'
    RECEBEDOR_CNPJ_FORMATADO = '30.080.209/0004-16'
    RECEBEDOR_NOME = 'GRUPO SERTAO'  # Possíveis variações: "GRUPO SERTÃO", "SERTAO", etc
    
    # Validação de recebedor
    VALIDAR_RECEBEDOR = True  # Se True, gera aviso quando recebedor não bate
    BLOQUEAR_RECEBEDOR_INVALIDO = False  # Se True, bloqueia pagamento (mais restritivo)
    
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
    def get_max_pdf_size(cls) -> int:
        """Retorna o tamanho máximo do PDF aceito antes do envio ao Vision"""
        return int(os.getenv('FINANCEIRO_MAX_PDF_SIZE', cls.OCR_MAX_PDF_SIZE))
    
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
    
    @classmethod
    def get_ocr_operation_timeout(cls) -> int:
        """Retorna timeout máximo (segundos) para operação assíncrona do Vision"""
        return int(os.getenv('FINANCEIRO_OCR_TIMEOUT', cls.OCR_OPERATION_TIMEOUT))
    
    @classmethod
    def validar_recebedor_habilitado(cls) -> bool:
        """Verifica se validação de recebedor está habilitada"""
        return cls.VALIDAR_RECEBEDOR
    
    @classmethod
    def bloquear_recebedor_invalido(cls) -> bool:
        """Verifica se deve bloquear pagamentos com recebedor inválido"""
        return cls.BLOQUEAR_RECEBEDOR_INVALIDO
    
    @classmethod
    def get_recebedor_esperado(cls) -> dict:
        """Retorna dados do recebedor esperado"""
        return {
            'pix': cls.RECEBEDOR_PIX,
            'cnpj': cls.RECEBEDOR_CNPJ,
            'cnpj_formatado': cls.RECEBEDOR_CNPJ_FORMATADO,
            'nome': cls.RECEBEDOR_NOME
        }
    
    @classmethod
    def get_detection_type(cls) -> str:
        """Retorna o modo de detecção a usar para imagens"""
        value = os.getenv('GOOGLE_VISION_DETECTION_TYPE', cls.GOOGLE_VISION_DETECTION_TYPE)
        return value.upper() if value else 'TEXT_DETECTION'
    
    @classmethod
    def get_gcs_input_bucket(cls) -> str:
        """Bucket de entrada para PDFs"""
        return os.getenv('FINANCEIRO_OCR_INPUT_BUCKET', cls.GOOGLE_VISION_INPUT_BUCKET)
    
    @classmethod
    def get_gcs_input_prefix(cls) -> str:
        """Prefixo do objeto no bucket de entrada"""
        return os.getenv('FINANCEIRO_OCR_INPUT_PREFIX', cls.GOOGLE_VISION_INPUT_PREFIX).strip('/')
    
    @classmethod
    def get_gcs_output_bucket(cls) -> str:
        """Bucket de saída para resultados OCR"""
        return os.getenv('FINANCEIRO_OCR_OUTPUT_BUCKET', cls.GOOGLE_VISION_OUTPUT_BUCKET)
    
    @classmethod
    def get_gcs_output_prefix(cls) -> str:
        """Prefixo do objeto no bucket de saída"""
        return os.getenv('FINANCEIRO_OCR_OUTPUT_PREFIX', cls.GOOGLE_VISION_OUTPUT_PREFIX).strip('/')
