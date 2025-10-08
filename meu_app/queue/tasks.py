"""
Tasks assíncronas para processamento em background
"""

import os
from typing import Dict, Optional


def process_ocr_task(file_path: str, pedido_id: int, pagamento_id: Optional[int] = None) -> Dict:
    """
    Task assíncrona para processar OCR de comprovante
    
    Args:
        file_path: Caminho do arquivo PDF/imagem
        pedido_id: ID do pedido
        pagamento_id: ID do pagamento (opcional)
    
    Returns:
        Dict com resultado do OCR
    """
    from meu_app.financeiro.vision_service import VisionOcrService
    from rq import get_current_job
    
    job = get_current_job()
    
    try:
        # Atualizar progresso
        if job:
            job.meta['progress'] = 10
            job.meta['stage'] = 'Validando arquivo'
            job.save_meta()
        
        # Validar que arquivo existe
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Atualizar progresso
        if job:
            job.meta['progress'] = 30
            job.meta['stage'] = 'Processando OCR'
            job.save_meta()
        
        # Processar OCR
        result = VisionOcrService.process_receipt(file_path)
        
        # Atualizar progresso
        if job:
            job.meta['progress'] = 80
            job.meta['stage'] = 'Finalizando'
            job.save_meta()
        
        # Adicionar metadados
        result['pedido_id'] = pedido_id
        result['pagamento_id'] = pagamento_id
        result['file_path'] = file_path
        
        # Atualizar progresso
        if job:
            job.meta['progress'] = 100
            job.meta['stage'] = 'Concluído'
            job.save_meta()
        
        return {
            'success': True,
            'data': result
        }
        
    except Exception as e:
        # Log do erro
        error_msg = f"Erro no processamento OCR: {str(e)}"
        
        if job:
            job.meta['error'] = error_msg
            job.save_meta()
        
        return {
            'success': False,
            'error': error_msg,
            'pedido_id': pedido_id,
            'pagamento_id': pagamento_id
        }
