#!/usr/bin/env python3
"""
Script de teste isolado do OCR
Testa o Google Vision sem passar pelo frontend
"""

import sys
from meu_app import create_app
from meu_app.financeiro.ocr_service import OcrService
from config import DevelopmentConfig

def testar_ocr(caminho_arquivo):
    """Testa OCR com arquivo específico"""
    print("=" * 60)
    print("🧪 TESTE ISOLADO - Google Vision OCR")
    print("=" * 60)
    
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        print(f"\n📁 Arquivo: {caminho_arquivo}")
        print("🔍 Processando com Google Vision...\n")
        
        try:
            result = OcrService.process_receipt(caminho_arquivo)
            
            print("✅ OCR EXECUTADO")
            print("-" * 60)
            
            # Exibir resultados
            print(f"💰 Valor encontrado: {result.get('amount')}")
            print(f"🔢 ID Transação: {result.get('transaction_id')}")
            print(f"📅 Data: {result.get('date')}")
            print(f"🏦 Banco: {result.get('bank_info', {}).get('banco_emitente')}")
            print(f"⚠️ Erro: {result.get('error')}")
            
            print("\n📊 Resultado completo:")
            print(result)
            
            # Verificar se valor foi extraído
            if result.get('amount'):
                print(f"\n✅ SUCESSO: Valor R$ {result.get('amount')} extraído!")
                return True
            elif result.get('error'):
                print(f"\n❌ ERRO: {result.get('error')}")
                return False
            else:
                print("\n⚠️ AVISO: OCR executou mas não encontrou valor")
                return False
                
        except Exception as e:
            print(f"\n❌ ERRO CRÍTICO: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_ocr_direto.py <caminho_arquivo>")
        print("\nExemplo:")
        print("  python test_ocr_direto.py /Users/ericobrandao/Downloads/comprovante_pix.jpg")
        sys.exit(1)
    
    caminho = sys.argv[1]
    sucesso = testar_ocr(caminho)
    
    sys.exit(0 if sucesso else 1)
