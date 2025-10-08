#!/usr/bin/env python3
"""
Teste: Validação de Recebedor
Verifica se o sistema identifica pagamentos para conta correta/incorreta
"""

from meu_app import create_app
from meu_app.financeiro.vision_service import VisionOcrService
from config import DevelopmentConfig

def criar_comprovante_teste(tipo='correto'):
    """Cria texto de comprovante de teste"""
    if tipo == 'correto':
        return """
        Comprovante de Pagamento PIX
        
        De: Cliente Teste
        CPF: 123.456.789-00
        
        Para: Grupo Sertão
        CNPJ: 30.080.209/0004-16
        Chave PIX: pix@gruposertao.com
        
        Valor: R$ 500,00
        Número da transação: TEST123456789
        Data: 08/10/2025
        """
    elif tipo == 'cnpj_errado':
        return """
        Comprovante de Pagamento PIX
        
        Para: Outra Empresa
        CNPJ: 11.222.333/0001-44
        Chave PIX: outro@empresa.com
        
        Valor: R$ 500,00
        Número da transação: TEST987654321
        """
    else:  # sem_dados
        return """
        Comprovante de Pagamento
        
        Valor Total: R$ 500,00
        Pagamento efetuado com sucesso
        """

def testar_validacao():
    """Testa validação de recebedor"""
    print("=" * 70)
    print("🧪 TESTE: Validação de Recebedor")
    print("=" * 70)
    
    app = create_app(DevelopmentConfig)
    
    with app.app_context():
        # Teste 1: Comprovante CORRETO
        print("\n📝 Teste 1: Comprovante para Grupo Sertão (CORRETO)")
        print("-" * 70)
        
        texto1 = criar_comprovante_teste('correto')
        bank_info1 = VisionOcrService._find_bank_info_in_text(texto1)
        
        from meu_app.financeiro.config import FinanceiroConfig
        recebedor_esperado = FinanceiroConfig.get_recebedor_esperado()
        validacao1 = VisionOcrService._validar_recebedor(bank_info1, recebedor_esperado)
        
        print(f"PIX extraído: {bank_info1.get('chave_pix_recebedor')}")
        print(f"CNPJ extraído: {bank_info1.get('cnpj_recebedor')}")
        print(f"Nome extraído: {bank_info1.get('nome_recebedor')}")
        print(f"\n✅ Validação:")
        print(f"   Válido: {validacao1['valido']}")
        print(f"   Confiança: {validacao1['confianca']}%")
        for motivo in validacao1['motivo']:
            print(f"   {motivo}")
        
        # Teste 2: Comprovante INCORRETO
        print("\n📝 Teste 2: Comprovante para Outra Empresa (INCORRETO)")
        print("-" * 70)
        
        texto2 = criar_comprovante_teste('cnpj_errado')
        bank_info2 = VisionOcrService._find_bank_info_in_text(texto2)
        validacao2 = VisionOcrService._validar_recebedor(bank_info2, recebedor_esperado)
        
        print(f"PIX extraído: {bank_info2.get('chave_pix_recebedor')}")
        print(f"CNPJ extraído: {bank_info2.get('cnpj_recebedor')}")
        print(f"Nome extraído: {bank_info2.get('nome_recebedor')}")
        print(f"\n⚠️ Validação:")
        print(f"   Válido: {validacao2['valido']}")
        print(f"   Confiança: {validacao2['confianca']}%")
        for motivo in validacao2['motivo']:
            print(f"   {motivo}")
        
        # Teste 3: Sem dados do recebedor
        print("\n📝 Teste 3: Comprovante Sem Dados do Recebedor")
        print("-" * 70)
        
        texto3 = criar_comprovante_teste('sem_dados')
        bank_info3 = VisionOcrService._find_bank_info_in_text(texto3)
        validacao3 = VisionOcrService._validar_recebedor(bank_info3, recebedor_esperado)
        
        print(f"PIX extraído: {bank_info3.get('chave_pix_recebedor')}")
        print(f"CNPJ extraído: {bank_info3.get('cnpj_recebedor')}")
        print(f"\nℹ️ Validação:")
        print(f"   Válido: {validacao3['valido']}")
        for motivo in validacao3['motivo']:
            print(f"   {motivo}")
        
        # Resumo
        print("\n" + "=" * 70)
        print("📊 RESUMO DOS TESTES")
        print("=" * 70)
        print(f"Teste 1 (Correto):   {'✅ PASSOU' if validacao1['valido'] == True else '❌ FALHOU'}")
        print(f"Teste 2 (Incorreto): {'✅ PASSOU' if validacao2['valido'] == False else '❌ FALHOU'}")
        print(f"Teste 3 (Sem dados): {'✅ PASSOU' if validacao3['valido'] == None else '❌ FALHOU'}")
        
        if validacao1['valido'] == True and validacao2['valido'] == False and validacao3['valido'] == None:
            print("\n🎉 TODOS OS TESTES PASSARAM!")
            return True
        else:
            print("\n❌ Algum teste falhou")
            return False

if __name__ == "__main__":
    import sys
    sucesso = testar_validacao()
    sys.exit(0 if sucesso else 1)
