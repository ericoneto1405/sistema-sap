import os
import re
from typing import Dict, Optional

from flask import current_app

from ..financeiro.vision_service import VisionOcrService
from ..financeiro.exceptions import OcrProcessingError
from ..upload_security import FileUploadValidator


class NotaFiscalReaderService:
    """Serviço simples para leitura de DANFE usando Google Vision."""

    @staticmethod
    def _parse_currency(value: str) -> Optional[float]:
        if not value:
            return None
        cleaned = value.strip().replace(' ', '')
        if cleaned.count(',') == 1 and cleaned.count('.') > 1:
            cleaned = cleaned.replace('.', '').replace(',', '.')
        elif cleaned.count(',') == 1 and cleaned.count('.') == 0:
            cleaned = cleaned.replace(',', '.')
        try:
            return float(cleaned)
        except ValueError:
            return None

    @staticmethod
    def _extract_summary(texto: str) -> Dict[str, Optional[str]]:
        resumo: Dict[str, Optional[str]] = {
            'emitente': None,
            'destinatario': None,
            'cnpjs': [],
            'chave_acesso': None,
            'numero_nfe': None,
            'data_emissao': None,
            'valor_total': None
        }

        # CNPJs formatados
        cnpjs = re.findall(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', texto)
        if cnpjs:
            resumo['cnpjs'] = list(dict.fromkeys(cnpjs))

        # Chave de acesso (agrupada ou não)
        chave_match = re.search(r'(?:\d{4}[ \t-]?){10}\d{4}', texto)
        if chave_match:
            resumo['chave_acesso'] = re.sub(r'\D', '', chave_match.group(0))

        # Número da NF-e
        numero_match = re.search(r'(?:NF[-\s]?E|Nº\s*NF|No\s*NF)[^\d]*(\d{3,})', texto, re.IGNORECASE)
        if numero_match:
            resumo['numero_nfe'] = numero_match.group(1)

        # Data de emissão (dd/mm/aaaa)
        data_match = re.search(r'DATA\s+DE\s+EMISSAO[:\s]*([0-3]\d/[0-1]\d/\d{4})', texto, re.IGNORECASE)
        if not data_match:
            data_match = re.search(r'EMISSAO[:\s]*([0-3]\d/[0-1]\d/\d{4})', texto, re.IGNORECASE)
        if data_match:
            resumo['data_emissao'] = data_match.group(1)

        # Valor total da nota
        valor_match = re.search(r'VALOR\s+TOTAL\s+(?:DA\s+NOTA\s+FISCAL|DA\s+NF[\-]E|NF[\-]E)?[:\s]*R?\$?\s*([\d.,]+)', texto, re.IGNORECASE)
        if valor_match:
            valor = NotaFiscalReaderService._parse_currency(valor_match.group(1))
            if valor is not None:
                resumo['valor_total'] = valor

        # Emitente (linha após "Emitente" ou "Razão Social")
        emitente_match = re.search(r'(?:EMITENTE|RAZAO\s+SOCIAL)\s*[:\-]?\s*(.+)', texto, re.IGNORECASE)
        if emitente_match:
            resumo['emitente'] = emitente_match.group(1).strip()

        # Destinatário
        destinatario_match = re.search(r'(?:DESTINATARIO|DEST\s+FINAL)\s*[:\-]?\s*(.+)', texto, re.IGNORECASE)
        if destinatario_match:
            resumo['destinatario'] = destinatario_match.group(1).strip()

        return resumo

    @staticmethod
    def process_upload(uploaded_file) -> Dict[str, object]:
        """
        Processa o upload, executa OCR e retorna dados estruturados.
        """
        file_type = 'document'
        is_valid, error_msg, metadata = FileUploadValidator.validate_file(uploaded_file, file_type)
        if not is_valid:
            uploaded_file.stream.seek(0)
            is_valid, error_msg, metadata = FileUploadValidator.validate_file(uploaded_file, 'image')
            if is_valid:
                file_type = 'image'
        if not is_valid:
            return {
                'ok': False,
                'mensagem': error_msg,
                'texto': '',
                'resumo': {}
            }

        uploaded_file.stream.seek(0)
        sucesso, msg, caminho = FileUploadValidator.save_file(uploaded_file, file_type)
        if not sucesso or not caminho:
            return {
                'ok': False,
                'mensagem': msg,
                'texto': '',
                'resumo': {}
            }

        try:
            texto = VisionOcrService.extract_text(caminho)
            resumo = NotaFiscalReaderService._extract_summary(texto or '')
            return {
                'ok': True,
                'mensagem': 'Leitura concluída com sucesso.',
                'texto': texto,
                'resumo': resumo
            }
        except OcrProcessingError as e:
            current_app.logger.error(f"Erro ao processar DANFE: {e}")
            return {
                'ok': False,
                'mensagem': str(e),
                'texto': '',
                'resumo': {}
            }
        except Exception as e:
            current_app.logger.exception("Erro inesperado ao processar a DANFE")
            return {
                'ok': False,
                'mensagem': f"Erro inesperado ao processar a DANFE: {e}",
                'texto': '',
                'resumo': {}
            }
        finally:
            try:
                FileUploadValidator.cleanup_file(caminho)
            except Exception as cleanup_err:
                current_app.logger.warning(f"Não foi possível remover arquivo temporário: {cleanup_err}")
