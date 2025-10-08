"""
Serviço de OCR usando Google Vision API - Versão baseada em GCS.
"""
import os
import json
import re
import uuid
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from google.cloud import vision, storage
from google.api_core.exceptions import NotFound
from .config import FinanceiroConfig
from .exceptions import OcrProcessingError


class VisionOcrService:
    """Serviço de OCR usando Google Vision API com extração avançada de dados"""
    
    _client = None
    _storage_client = None
    _initialized = False
    
    @classmethod
    def _get_client(cls):
        """
        Obtém o cliente do Google Vision com lazy loading
        Returns:
            vision.ImageAnnotatorClient: Cliente do Google Vision
        """
        if cls._client is None:
            try:
                credentials_path = FinanceiroConfig.GOOGLE_VISION_CREDENTIALS_PATH
                if not credentials_path or not os.path.exists(credentials_path):
                    raise OcrProcessingError("Credenciais do Google Vision não configuradas ou arquivo não encontrado")
                
                if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                
                print("Inicializando cliente Google Vision...")
                cls._client = vision.ImageAnnotatorClient()
                cls._initialized = True
                print("Cliente Google Vision pronto.")
                
            except Exception as e:
                print(f"Erro ao inicializar Google Vision: {e}")
                raise OcrProcessingError(f"Falha ao inicializar Google Vision: {str(e)}")
        
        return cls._client
    
    @classmethod
    def _get_storage_client(cls):
        """Obtém cliente do Google Cloud Storage"""
        if cls._storage_client is None:
            try:
                credentials_path = FinanceiroConfig.GOOGLE_VISION_CREDENTIALS_PATH
                if not credentials_path or not os.path.exists(credentials_path):
                    raise OcrProcessingError("Credenciais do Google Vision não configuradas ou arquivo não encontrado")
                
                if not os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
                
                cls._storage_client = storage.Client()
            except Exception as e:
                print(f"Erro ao inicializar Storage: {e}")
                raise OcrProcessingError(f"Falha ao inicializar Storage: {str(e)}")
        return cls._storage_client
    
    @classmethod
    def is_initialized(cls) -> bool:
        """Verifica se o Google Vision foi inicializado"""
        return cls._initialized
    
    @staticmethod
    def _split_gcs_uri(uri: str) -> Tuple[str, str]:
        if not uri.startswith("gs://"):
            raise OcrProcessingError(f"URI inválida para GCS: {uri}")
        path = uri[5:]
        bucket, _, blob = path.partition('/')
        if not bucket or not blob:
            raise OcrProcessingError(f"URI incompleta para GCS: {uri}")
        return bucket, blob
    
    @classmethod
    def _upload_pdf_to_gcs(cls, file_path: str) -> str:
        """Carrega PDF para bucket de entrada e retorna URI gs://"""
        if not os.path.exists(file_path):
            raise OcrProcessingError("PDF não encontrado")
        
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            raise OcrProcessingError("PDF está vazio")
        
        max_size = FinanceiroConfig.get_max_pdf_size()
        if max_size and file_size > max_size:
            raise OcrProcessingError(f"PDF muito grande ({file_size} bytes). Limite: {max_size} bytes")
        
        storage_client = cls._get_storage_client()
        bucket_name = FinanceiroConfig.get_gcs_input_bucket()
        object_prefix = FinanceiroConfig.get_gcs_input_prefix()
        blob_name = f"{object_prefix}/{uuid.uuid4()}.pdf" if object_prefix else f"{uuid.uuid4()}.pdf"
        
        try:
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(file_path, content_type="application/pdf")
            print(f"PDF enviado para GCS: gs://{bucket_name}/{blob_name}")
            return f"gs://{bucket_name}/{blob_name}"
        except Exception as exc:
            raise OcrProcessingError(f"Falha ao enviar PDF para GCS: {exc}")
    
    @classmethod
    def _prepare_output_uri(cls) -> Tuple[str, str]:
        """Gera URI de saída única para resultados do OCR"""
        bucket = FinanceiroConfig.get_gcs_output_bucket()
        prefix = FinanceiroConfig.get_gcs_output_prefix()
        output_id = uuid.uuid4()
        object_prefix = f"{prefix}/{output_id}" if prefix else str(output_id)
        output_uri = f"gs://{bucket}/{object_prefix}/"
        return output_uri, object_prefix
    
    @classmethod
    def _fetch_output_text(cls, output_uri: str) -> str:
        """Baixa os resultados do Vision do bucket de saída"""
        storage_client = cls._get_storage_client()
        bucket_name, prefix = cls._split_gcs_uri(output_uri)
        # Remover barra final para listagem
        prefix = prefix.rstrip('/')
        
        texts: List[str] = []
        try:
            blobs = list(storage_client.list_blobs(bucket_name, prefix=prefix))
        except Exception as exc:
            raise OcrProcessingError(f"Falha ao listar resultados no GCS: {exc}")
        
        if not blobs:
            raise OcrProcessingError("Vision não retornou resultados para o PDF enviado")
        
        for blob in blobs:
            try:
                data = json.loads(blob.download_as_text())
                for response in data.get('responses', []):
                    full_text = response.get('fullTextAnnotation', {}).get('text')
                    if full_text:
                        texts.append(full_text)
            except Exception as exc:
                print(f"Erro ao ler resultado OCR ({blob.name}): {exc}")
                continue
        
        combined = "\n".join(texts).strip()
        if not combined:
            raise OcrProcessingError("Vision processou o PDF mas não encontrou texto")
        return combined
    
    @classmethod
    def _cleanup_gcs_resources(cls, input_uri: str, output_uri: str):
        """Remove arquivos temporários do GCS"""
        storage_client = cls._get_storage_client()
        
        # Remover PDF de entrada
        try:
            bucket_name, blob_name = cls._split_gcs_uri(input_uri)
            storage_client.bucket(bucket_name).blob(blob_name).delete()
        except NotFound:
            pass
        except Exception as exc:
            print(f"Falha ao remover PDF de entrada no GCS: {exc}")
        
        # Remover resultados
        try:
            bucket_name, prefix = cls._split_gcs_uri(output_uri)
            prefix = prefix.rstrip('/')
            bucket = storage_client.bucket(bucket_name)
            for blob in storage_client.list_blobs(bucket_name, prefix=prefix):
                try:
                    bucket.blob(blob.name).delete()
                except Exception as exc:
                    print(f"Falha ao remover resultado OCR ({blob.name}): {exc}")
        except NotFound:
            pass
        except Exception as exc:
            print(f"Falha ao limpar resultados OCR no GCS: {exc}")
    
    @classmethod
    def _extract_text_from_file(cls, file_path: str) -> str:
        """
        Usa o Google Vision para extrair texto de PDFs (via GCS) ou imagens locais.
        """
        try:
            client = cls._get_client()
            file_ext = os.path.splitext(file_path)[1].lower()
            is_pdf = file_ext == '.pdf'
            
            if is_pdf:
                input_uri = cls._upload_pdf_to_gcs(file_path)
                output_uri, _ = cls._prepare_output_uri()
                
                feature = vision.Feature(type=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
                gcs_source = vision.GcsSource(uri=input_uri)
                input_config = vision.InputConfig(gcs_source=gcs_source, mime_type="application/pdf")
                gcs_destination = vision.GcsDestination(uri=output_uri)
                output_config = vision.OutputConfig(gcs_destination=gcs_destination, batch_size=1)
                
                request = vision.AsyncAnnotateFileRequest(
                    features=[feature],
                    input_config=input_config,
                    output_config=output_config,
                )
                
                print("🔍 Iniciando OCR assíncrono para PDF...")
                operation = client.async_batch_annotate_files(requests=[request])
                timeout = FinanceiroConfig.get_ocr_operation_timeout()
                operation.result(timeout=timeout)
                print("✅ OCR concluído pelo Vision, baixando resultado...")
                
                try:
                    text = cls._fetch_output_text(output_uri)
                finally:
                    cls._cleanup_gcs_resources(input_uri, output_uri)
                
                return text
            
            with open(file_path, 'rb') as image_file:
                content = image_file.read()
            
            image = vision.Image(content=content)
            detection_type = FinanceiroConfig.get_detection_type()
            if detection_type == 'DOCUMENT_TEXT_DETECTION':
                response = client.document_text_detection(image=image)
            else:
                response = client.text_detection(image=image)
            
            error_info = getattr(response, 'error', None)
            if error_info and getattr(error_info, 'code', 0):
                error_msg = None
                if getattr(error_info, 'message', None):
                    error_msg = error_info.message
                elif getattr(error_info, 'code', None):
                    error_msg = f"Code: {error_info.code}"
                elif str(error_info).strip():
                    error_msg = str(error_info)
                else:
                    error_msg = "Erro desconhecido do Google Vision"
                raise OcrProcessingError(f"Erro do Google Vision: {error_msg}")
            
            texts = []
            for text in response.text_annotations:
                texts.append(text.description)
            
            return '\n'.join(texts) if texts else ""
            
        except OcrProcessingError:
            raise
        except Exception as e:
            print(f"Erro durante extração de texto com Google Vision: {e}")
            raise OcrProcessingError(f"Falha na extração de texto: {str(e)}")
    
    @staticmethod
    def _find_amount_in_text(text: str) -> Optional[float]:
        """
        Encontra o valor monetário mais provável em uma string de texto,
        dando prioridade a palavras-chave específicas.
        """
        text = text.upper().replace('\u00A0', ' ').replace('\t', ' ')
        
        # Padrões prioritários para valores
        priority_patterns = [
            r'(?:VALOR\s+DA\s+TRANSFER.NCIA|VALOR\s+DO\s+PAGAMENTO|VALOR\s+DO\s+PIX|TOTAL\s+GERAL|VALOR\s+L.QUIDO|VALOR\s+A\s+TRANSFERIR)[\s\S]{0,120}?R?\$?\s*(\d{1,3}(?:[.,\s]\d{3})*[.,]\d{2})',
            r'(?:TRANSFERIDO|PAGO|VALOR|TOTAL)[\s\S]{0,80}?R?\$?\s*(\d{1,3}(?:[.,\s]\d{3})*[.,]\d{2})'
        ]
        
        for pattern in priority_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                value_str = matches[0]
                try:
                    return VisionOcrService._parse_currency_value(value_str)
                except (ValueError, TypeError):
                    continue

        # Padrões secundários
        secondary_patterns = [
            r'(?:TOTAL|VALOR\s+A\s+PAGAR|VALOR\s+TOTAL|VALOR\s+PAGO|TOTAL\s+PAGO)\s*[:\-]?\s*R?\$?\s*(\d{1,3}(?:[.,\s]\d{3})*[.,]\d{2})'
        ]
        
        found_values = []
        for pattern in secondary_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    found_values.append(VisionOcrService._parse_currency_value(match))
                except ValueError:
                    continue
        
        if found_values:
            return max(found_values)

        # Fallback: qualquer valor monetário
        fallback_pattern = r'R?\$?\s*(\d{1,3}(?:[.,\s]\d{3})*[.,]\d{2})'
        matches = re.findall(fallback_pattern, text)
        found_values = []
        for match in matches:
            try:
                found_values.append(VisionOcrService._parse_currency_value(match))
            except ValueError:
                continue
        
        if found_values:
            return max(found_values)

        return None

    @staticmethod
    def _parse_currency_value(value_str: str) -> float:
        """Converte string de valor monetário para float"""
        value_str = value_str.replace(' ', '')
        if '.' in value_str and ',' in value_str:
            if value_str.rfind('.') > value_str.rfind(','):
                # Formato americano: 1,234.56
                cleaned_value = value_str.replace(',', '')
            else:
                # Formato brasileiro: 1.234,56
                cleaned_value = value_str.replace('.', '').replace(',', '.')
        else:
            # Apenas vírgula ou ponto
            cleaned_value = value_str.replace(',', '.')
        
        return float(cleaned_value)

    @staticmethod
    def _find_transaction_id_in_text(text: str) -> Optional[str]:
        """
        Encontra um ID de transação em uma string de texto.
        Suporta múltiplos padrões de bancos brasileiros.
        """
        import unicodedata
        
        # Debug: mostrar texto recebido
        print(f"[DEBUG OCR] Buscando ID no texto (primeiros 200 chars): {text[:200]}")
        
        # Normalizar texto removendo acentos para facilitar regex
        def remove_accents(input_str):
            nfkd = unicodedata.normalize('NFKD', input_str)
            return ''.join([c for c in nfkd if not unicodedata.combining(c)])
        
        text_normalized = remove_accents(text).upper()
        print(f"[DEBUG OCR] Texto normalizado (primeiros 200 chars): {text_normalized[:200]}")
        
        # Padrão 1: Labels explícitos (prioridade alta)
        # IMPORTANTE: Aceitar IDs numéricos OU alfanuméricos (mínimo 8 chars)
        explicit_patterns = [
            # Mercado Pago e similares - "Número da transação" (numérico OU alfanumérico)
            r'(?:NUMERO\s+DA\s+TRANSACAO|NUMERO\s+TRANSACAO)\s*[:\-]?\s*([a-zA-Z0-9]{8,50})',
            
            # PIX - Diversos formatos
            r'(?:ID\s+DA\s+TRANSACAO|ID\s+TRANSACAO|IDENTIFICACAO)\s*[:\-]?\s*([a-zA-Z0-9]{8,50})',
            r'(?:CODIGO\s+DA\s+TRANSACAO|CODIGO\s+TRANSACAO)\s*[:\-]?\s*([a-zA-Z0-9]{8,50})',
            
            # Termos comuns
            r'(?:ID\s+PAGAMENTO|PAGAMENTO\s+ID|ID\s+PIX)\s*[:\-]?\s*([a-zA-Z0-9]{8,50})',
            r'(?:CODIGO\s+DA\s+OPERACAO|COD\.\s+OPERACAO|OPERACAO)\s*[:\-]?\s*([a-zA-Z0-9]{8,50})',
            r'(?:NUMERO\s+DA\s+OPERACAO|N\.\s+OPERACAO)\s*[:\-]?\s*([a-zA-Z0-9]{8,50})',
            r'(?:N\.\s+DOCUMENTO|NUMERO\s+DOCUMENTO|DOCUMENTO)\s*[:\-]?\s*([a-zA-Z0-9]{8,50})',
            r'(?:NOSSO\s+NUMERO|NOSSO\s+NUM)\s*[:\-]?\s*([a-zA-Z0-9]{8,50})',
            r'(?:PROTOCOLO|AUTENTICACAO)\s*[:\-]?\s*([a-zA-Z0-9]{8,50})',
            r'(?:COMPROVACAO|COMPROVANTE)\s*[:\-]?\s*([a-zA-Z0-9]{15,50})',
            
            # Nubank/Inter (UUID-like)
            r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})',
        ]
        
        for i, pattern in enumerate(explicit_patterns, 1):
            matches = re.findall(pattern, text_normalized, re.IGNORECASE)
            if matches:
                print(f"[DEBUG OCR] Padrão {i} encontrou: {matches}")
                candidate = matches[0].strip()
                # Validar que não é data ou valor monetário
                if not re.match(r'^\d{1,2}[/\-\.]\d{1,2}', candidate):
                    # Validar tamanho mínimo razoável (8+ chars)
                    if len(candidate) >= 8:
                        print(f"[DEBUG OCR] ✅ ID da Transação extraído: {candidate}")
                        return candidate
                    else:
                        print(f"[DEBUG OCR] ⚠️ Candidato muito curto: {candidate} ({len(candidate)} chars)")
                else:
                    print(f"[DEBUG OCR] ⚠️ Candidato parece ser data: {candidate}")
        
        # Padrão 2: IDs PIX padrão brasileiro (começam com E ou D)
        # Formato: E00000000202510021939023026977590 (32+ caracteres)
        pix_pattern = r'\b([ED][0-9]{25,40})\b'
        matches = re.findall(pix_pattern, text_upper)
        if matches:
            # Retornar o mais longo (geralmente mais completo)
            return max(matches, key=len)
        
        # Padrão 3: Sequências alfanuméricas longas (15-50 chars)
        # Após palavras-chave relacionadas a transação
        context_pattern = r'(?:TRANSA(?:ÇÃO|CAO)|PAGAMENTO|PIX|TRANSFER[EÊ]NCIA)\s*[:\-]?\s*([A-Z0-9]{15,50})'
        matches = re.findall(context_pattern, text_upper)
        if matches:
            return matches[0].strip()
        
        # Padrão 4: Busca genérica por códigos longos
        # Evitar datas (com /) e valores (com , ou R$)
        generic_pattern = r'\b([A-Z0-9]{20,50})\b'
        matches = re.findall(generic_pattern, text_upper)
        if matches:
            # Filtrar candidatos válidos
            for candidate in matches:
                # Não pode ser só números (pode ser CPF, telefone, etc)
                if not candidate.isdigit():
                    # Não pode ter padrão de data
                    if not re.search(r'\d{2}[/\-\.]\d{2}', candidate):
                        return candidate

        return None

    @staticmethod
    def _find_date_in_text(text: str) -> Optional[str]:
        """
        Encontra data no texto do comprovante.
        """
        text = text.upper()
        
        # Padrões de data brasileira
        date_patterns = [
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            r'(?:DATA\s+DA\s+TRANSACAO|DATA\s+DO\s+PAGAMENTO|DATA)\s*[:\-]?\s*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            r'(\d{1,2}\s+DE\s+\w+\s+DE\s+\d{4})'  # "15 de janeiro de 2024"
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return None

    @staticmethod
    def _find_bank_info_in_text(text: str) -> Dict[str, Optional[str]]:
        """
        Encontra informações bancárias no texto.
        """
        text = text.upper()
        
        result = {
            'banco_emitente': None,
            'agencia_recebedor': None,
            'conta_recebedor': None,
            'chave_pix_recebedor': None
        }
        
        # Padrões para banco emitente
        bank_patterns = [
            r'(?:BANCO\s+DO\s+BRASIL|BB|CAIXA\s+ECONOMICA|ITAU|BRADESCO|SANTANDER|NUBANK|INTER|SICOOB|SICREDI)',
            r'(?:BANCO\s+)[A-Z\s]+(?=\s|$)'
        ]
        
        for pattern in bank_patterns:
            matches = re.findall(pattern, text)
            if matches:
                result['banco_emitente'] = matches[0].strip()
                break
        
        # Padrões para agência
        agency_patterns = [
            r'(?:AGENCIA|AG\.?)\s*[:\-]?\s*(\d{4,5})',
            r'(\d{4,5})\s*(?:AGENCIA|AG\.?)'
        ]
        
        for pattern in agency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                result['agencia_recebedor'] = matches[0]
                break
        
        # Padrões para conta
        account_patterns = [
            r'(?:CONTA|CC)\s*[:\-]?\s*(\d{5,15})',
            r'(\d{5,15})\s*(?:CONTA|CC)'
        ]
        
        for pattern in account_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                result['conta_recebedor'] = matches[0]
                break
        
        # Padrões para chave PIX
        pix_patterns = [
            r'(?:CHAVE\s+PIX|PIX)\s*[:\-]?\s*([a-zA-Z0-9@\.\-]{20,})',
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Email
            r'(\d{11})',  # CPF
            r'(\d{14})',  # CNPJ
            r'(\+55\s?\d{2}\s?\d{4,5}\s?\d{4})'  # Telefone
        ]
        
        for pattern in pix_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                result['chave_pix_recebedor'] = matches[0]
                break
        
        return result
    
    @classmethod
    def process_receipt(cls, file_path: str) -> Dict:
        """
        Processa um arquivo de recibo usando Google Vision.
        Retorna um dicionário com todos os dados encontrados.
        """
        try:
            text = cls._extract_text_from_file(file_path)
            if not text:
                return {
                    'amount': None, 
                    'transaction_id': None,
                    'date': None,
                    'bank_info': {},
                    'error': 'Não foi possível extrair texto do documento.'
                }

            print(f"[DEBUG] Texto extraído ({len(text)} chars), iniciando busca de dados...")
            
            # Extrair todos os dados
            amount = cls._find_amount_in_text(text)
            print(f"[DEBUG] Valor encontrado: {amount}")
            
            transaction_id = cls._find_transaction_id_in_text(text)
            print(f"[DEBUG] ID Transação após busca: {transaction_id}")
            
            date = cls._find_date_in_text(text)
            print(f"[DEBUG] Data encontrada: {date}")
            
            bank_info = cls._find_bank_info_in_text(text)
            print(f"[DEBUG] Bank info: {bank_info}")

            return {
                'amount': amount,
                'transaction_id': transaction_id,
                'date': date,
                'bank_info': bank_info
            }
            
        except OcrProcessingError as e:
            return {
                'amount': None, 
                'transaction_id': None,
                'date': None,
                'bank_info': {},
                'error': str(e)
            }
        except Exception as e:
            return {
                'amount': None, 
                'transaction_id': None,
                'date': None,
                'bank_info': {},
                'error': f'Erro inesperado no Google Vision: {str(e)}'
            }
