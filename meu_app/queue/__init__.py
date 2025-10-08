"""
Sistema de filas assíncronas com RQ (Redis Queue)
Fase 7 - Processamento assíncrono de OCR e uploads
"""

from redis import Redis
from rq import Queue
from flask import current_app

# Redis connection (singleton)
redis_conn = None
ocr_queue = None


def init_queue(app):
    """
    Inicializa a conexão Redis e a fila RQ
    """
    global redis_conn, ocr_queue
    
    redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
    
    try:
        redis_conn = Redis.from_url(redis_url, decode_responses=True)
        redis_conn.ping()  # Testar conexão
        
        # Criar fila para OCR (com timeout de 5 minutos)
        ocr_queue = Queue('ocr', connection=redis_conn, default_timeout=300)
        
        app.logger.info(f"✅ RQ inicializado: {redis_url}")
        app.logger.info(f"✅ Fila 'ocr' criada com sucesso")
        
    except Exception as e:
        app.logger.warning(f"⚠️ Redis não disponível: {e}")
        app.logger.warning("⚠️ Processamento OCR será SÍNCRONO")
        redis_conn = None
        ocr_queue = None


def get_queue():
    """Retorna a fila de OCR (ou None se Redis indisponível)"""
    return ocr_queue


def get_redis():
    """Retorna a conexão Redis (ou None se indisponível)"""
    return redis_conn


def enqueue_ocr_job(file_path: str, pedido_id: int, pagamento_id: int = None):
    """
    Enfileira um job de OCR para processamento assíncrono
    
    Args:
        file_path: Caminho do arquivo a processar
        pedido_id: ID do pedido associado
        pagamento_id: ID do pagamento (opcional)
    
    Returns:
        Job ID ou None se fila indisponível
    """
    if ocr_queue is None:
        current_app.logger.warning("⚠️ Fila não disponível, processamento será síncrono")
        return None
    
    try:
        from .tasks import process_ocr_task
        
        job = ocr_queue.enqueue(
            process_ocr_task,
            file_path,
            pedido_id,
            pagamento_id,
            job_timeout=300,  # 5 minutos
            result_ttl=3600,  # Resultado expira em 1 hora
            failure_ttl=86400  # Falhas expiram em 24h
        )
        
        current_app.logger.info(f"✅ Job OCR enfileirado: {job.id}")
        return job.id
        
    except Exception as e:
        current_app.logger.error(f"❌ Erro ao enfileirar OCR: {e}")
        return None


def get_job_status(job_id: str):
    """
    Retorna o status de um job
    
    Returns:
        dict com status, progress, result ou error
    """
    if redis_conn is None or ocr_queue is None:
        return {
            'status': 'unavailable',
            'message': 'Fila não disponível'
        }
    
    try:
        from rq.job import Job
        
        job = Job.fetch(job_id, connection=redis_conn)
        
        response = {
            'job_id': job.id,
            'status': job.get_status(),
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'ended_at': job.ended_at.isoformat() if job.ended_at else None,
        }
        
        # Status: queued, started, finished, failed
        if job.is_finished:
            response['result'] = job.result
        elif job.is_failed:
            response['error'] = str(job.exc_info)
        elif job.is_started:
            response['progress'] = job.meta.get('progress', 0)
        
        return response
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erro ao buscar job: {str(e)}'
        }
