#!/usr/bin/env python3
"""
Debug: Mostrar texto completo extraído pelo Google Vision
"""

import sys
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/ericobrandao/keys/gvision-credentials.json'

from meu_app import create_app
from meu_app.financeiro.vision_service import VisionOcrService
from config import DevelopmentConfig

def mostrar_texto_completo(caminho_arquivo):
    """Mostra texto completo extraído pelo OCR"""
    print("=" * 70)
    print("🔍 DEBUG: TEXTO COMPLETO DO OCR")
    print("=" * 70)
    
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        print(f"\n📁 Arquivo: {caminho_arquivo}\n")
        
        try:
            # Extrair texto bruto
            texto = VisionOcrService._extract_text_from_file(caminho_arquivo)
            
            if not texto:
                print("❌ Nenhum texto extraído!")
                return
            
            print("=" * 70)
            print("📄 TEXTO COMPLETO EXTRAÍDO PELO GOOGLE VISION:")
            print("=" * 70)
            print(texto)
            print("=" * 70)
            
            print(f"\n📊 Estatísticas:")
            print(f"   • Caracteres: {len(texto)}")
            print(f"   • Linhas: {len(texto.split(chr(10)))}")
            print(f"   • Palavras: {len(texto.split())}")
            
            # Buscar padrões manualmente
            print(f"\n🔍 Buscando padrões...")
            
            texto_upper = texto.upper()
            
            # Procurar por termos comuns
            termos = ['TRANSACAO', 'TRANSAÇÃO', 'ID', 'CODIGO', 'CÓDIGO', 'OPERACAO', 'OPERAÇÃO', 
                      'DOCUMENTO', 'PROTOCOLO', 'AUTENTICACAO', 'AUTENTICAÇÃO', 'COMPROVANTE']
            
            print("\n   Termos encontrados:")
            for termo in termos:
                if termo in texto_upper:
                    print(f"   ✅ {termo}")
                    # Mostrar contexto
                    idx = texto_upper.find(termo)
                    contexto = texto[max(0, idx-20):min(len(texto), idx+60)]
                    print(f"      Contexto: ...{contexto}...")
            
            # Procurar sequências longas de letras/números
            import re
            print("\n   Sequências alfanuméricas longas (20+ chars):")
            pattern = r'\b([A-Z0-9]{20,})\b'
            matches = re.findall(pattern, texto_upper)
            for i, match in enumerate(matches[:5], 1):
                print(f"   {i}. {match}")
            
            # Procurar IDs que começam com E ou D
            print("\n   IDs PIX (começam com E ou D):")
            pix_pattern = r'\b([ED][0-9]{20,})\b'
            matches = re.findall(pix_pattern, texto_upper)
            for i, match in enumerate(matches, 1):
                print(f"   {i}. {match}")
                
        except Exception as e:
            print(f"\n❌ ERRO: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python debug_texto_ocr.py <caminho_arquivo>")
        sys.exit(1)
    
    mostrar_texto_completo(sys.argv[1])
