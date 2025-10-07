"""
Serviço de OCR usando Google Vision API - Versão aprimorada.
"""
import os
import json
import re
import tempfile
from typing import Optional, Dict
from datetime import datetime
from google.cloud import vision
from .config import FinanceiroConfig
from .exceptions import OcrProcessingError

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None


class VisionOcrService:
    """Serviço de OCR usando Google Vision API com extração avançada de dados"""
    
    _client = None
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
                # Verificar se as credenciais estão configuradas
                credentials_path = FinanceiroConfig.GOOGLE_VISION_CREDENTIALS_PATH
                if not credentials_path or not os.path.exists(credentials_path):
                    raise OcrProcessingError("Credenciais do Google Vision não configuradas ou arquivo não encontrado")
                
                # Configurar variável de ambiente se necessário
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
    def is_initialized(cls) -> bool:
        """Verifica se o Google Vision foi inicializado"""
        return cls._initialized
    
    @classmethod
    def _convert_pdf_to_image(cls, pdf_path: str) -> str:
        """
        Converte PDF para imagem usando pdf2image
        Returns:
            str: Caminho da imagem convertida
        """
        if convert_from_path is None:
            raise OcrProcessingError("pdf2image não está instalado. Execute: pip install pdf2image")
        
        try:
            # OTIMIZAÇÃO 1: Validação prévia do PDF
            if not os.path.exists(pdf_path):
                raise OcrProcessingError("PDF não encontrado")
            
            pdf_size = os.path.getsize(pdf_path)
            if pdf_size == 0:
                raise OcrProcessingError("PDF está vazio")
            
            # Limite de 10MB para PDF (antes da conversão)
            if pdf_size > 10 * 1024 * 1024:  # 10MB
                raise OcrProcessingError(f"PDF muito grande ({pdf_size:,} bytes). Limite: 10MB")
            
            print(f"📄 PDF validado: {pdf_size:,} bytes")
            
            # Criar diretório temporário
            temp_dir = tempfile.mkdtemp()
            
            # OTIMIZAÇÃO 2: Configurações otimizadas (2 tentativas em vez de 4)
            configs = [
                {"dpi": 120, "format": "JPEG", "quality": 90},  # Configuração otimizada
                {"dpi": 100, "format": "PNG", "quality": None}   # Fallback de alta qualidade
            ]
            
            for i, config in enumerate(configs):
                try:
                    print(f"🔍 Tentativa {i+1}: DPI={config['dpi']}, Formato={config['format']}, Qualidade={config.get('quality', 'N/A')}")
                    
                    # Converter primeira página do PDF
                    pages = convert_from_path(
                        pdf_path, 
                        first_page=1, 
                        last_page=1, 
                        dpi=config['dpi']
                    )
                    
                    if not pages:
                        print(f"❌ Conversão falhou - nenhuma página retornada")
                        continue
                    
                    # Salvar com configuração atual
                    ext = config['format'].lower()
                    image_path = os.path.join(temp_dir, f"converted_page.{ext}")
                    
                    # OTIMIZAÇÃO 3: Salvar com configurações otimizadas
                    if config['quality']:
                        pages[0].save(
                            image_path, 
                            config['format'], 
                            quality=config['quality'], 
                            optimize=True
                        )
                    else:
                        pages[0].save(
                            image_path, 
                            config['format'], 
                            optimize=True
                        )
                    
                    # OTIMIZAÇÃO 4: Validação robusta do arquivo convertido
                    if not os.path.exists(image_path):
                        print(f"❌ Arquivo não foi criado")
                        continue
                    
                    file_size = os.path.getsize(image_path)
                    if file_size == 0:
                        print(f"❌ Arquivo está vazio")
                        continue
                    
                    # Verificar se arquivo não é muito grande (limite Google Vision: 20MB)
                    if file_size > 20 * 1024 * 1024:  # 20MB
                        print(f"❌ Arquivo muito grande: {file_size:,} bytes")
                        continue
                    
                    print(f"✅ PDF convertido com sucesso: {image_path} ({file_size:,} bytes)")
                    return image_path
                    
                except Exception as e:
                    print(f"❌ Tentativa {i+1} falhou: {e}")
                    continue
            
            # Se todas as tentativas falharam
            raise OcrProcessingError("Todas as tentativas de conversão PDF falharam")
            
        except OcrProcessingError:
            raise
        except Exception as e:
            raise OcrProcessingError(f"Erro ao converter PDF para imagem: {str(e)}")
        finally:
            # OTIMIZAÇÃO 5: Limpeza robusta de arquivos temporários
            # NOTA: Não removemos temp_dir aqui pois o código atual já limpa os arquivos
            # e remover o diretório aqui causaria erro
            pass
    
    @classmethod
    def _extract_text_from_image(cls, file_path: str) -> str:
        """
        Usa o Google Vision para extrair texto de uma imagem ou documento.
        Detecta automaticamente o tipo de arquivo e usa o método apropriado.
        """
        try:
            client = cls._get_client()
            
            # CORREÇÃO CRÍTICA: Detectar tipo de arquivo PRIMEIRO
            file_ext = os.path.splitext(file_path)[1].lower()
            is_pdf = file_ext == '.pdf'
            
            # Processar arquivo baseado no tipo
            if is_pdf:
                # Para PDFs, converter para imagem primeiro
                print(f"🔍 Convertendo PDF para imagem...")
                image_path = cls._convert_pdf_to_image(file_path)
                
                # Ler imagem convertida
                with open(image_path, 'rb') as image_file:
                    content = image_file.read()
                
                image = vision.Image(content=content)
                print(f"🔍 Processando imagem convertida com text_detection...")
                response = client.text_detection(image=image)
                
                # Limpar arquivo temporário DEPOIS do processamento
                try:
                    os.remove(image_path)
                    os.rmdir(os.path.dirname(image_path))
                except:
                    pass
            else:
                # Para imagens, ler diretamente
                with open(file_path, 'rb') as image_file:
                    content = image_file.read()
                
                image = vision.Image(content=content)
                print(f"🔍 Processando imagem com text_detection...")
                response = client.text_detection(image=image)
            
            # Verificar se há erro na resposta (respeitando code == 0 como sucesso)
            error_info = getattr(response, 'error', None)
            if error_info and getattr(error_info, 'code', 0):
                # Tentar obter mensagem de erro de diferentes formas
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
            
            # Extrair texto dos resultados (sempre usando text_detection)
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
        text = text.upper()
        
        # Padrões prioritários para valores
        priority_patterns = [
            r'(?:VALOR\s+DA\s+TRANSFER.NCIA|VALOR\s+DO\s+PAGAMENTO|VALOR\s+DO\s+PIX|TOTAL\s+GERAL|VALOR\s+L.QUIDO|VALOR\s+A\s+TRANSFERIR)[\s\S]{0,100}?R?\$\s*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})',
            r'(?:TRANSFERIDO|PAGO|VALOR)[\s\S]{0,50}?R?\$\s*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})'
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
            r'(?:TOTAL|VALOR\s+A\s+PAGAR|VALOR\s+TOTAL)\s*[:\-]?\s*R?\$\s*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})'
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
        fallback_pattern = r'R\$\s*(\d{1,3}(?:[.,]\d{3})*[.,]\d{2})'
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
        """
        text = text.upper()
        
        # Padrões para ID de transação
        patterns = [
            r'(?:ID\s+DA\s+TRANSA(?:ÇÃO|CAO)|ID\s+TRANSACAO|ID\s+PAGAMENTO|CODIGO\s+DA\s+OPERACAO|N\.\s+DOCUMENTO|NOSSO\s+NUMERO)\s*[:\-]?\s*([a-zA-Z0-9]{10,40})\b',
            r'(?:TRANSACAO|OPERACAO|PAGAMENTO)\s*[:\-]?\s*([a-zA-Z0-9]{10,40})\b'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
            
        # Fallback: IDs PIX (inicia com E ou D)
        fallback_pattern = r'\b([ED][a-zA-Z0-9]{20,})\b'
        matches = re.findall(fallback_pattern, text)
        if matches:
            return matches[0]

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
            text = cls._extract_text_from_image(file_path)
            if not text:
                return {
                    'amount': None, 
                    'transaction_id': None,
                    'date': None,
                    'bank_info': {},
                    'error': 'Não foi possível extrair texto da imagem.'
                }

            # Extrair todos os dados
            amount = cls._find_amount_in_text(text)
            transaction_id = cls._find_transaction_id_in_text(text)
            date = cls._find_date_in_text(text)
            bank_info = cls._find_bank_info_in_text(text)

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
