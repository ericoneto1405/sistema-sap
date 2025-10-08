#!/usr/bin/env python3
"""
Diagnóstico Completo: OCR + Financeiro + Coleta
Ajuda a identificar problemas no fluxo completo
"""

import sys
from meu_app import create_app
from meu_app.models import Pedido, Pagamento, OcrQuota, StatusPedido
from meu_app.financeiro.config import FinanceiroConfig
from config import DevelopmentConfig
from datetime import datetime
import os

def verificar_configuracao():
    """Verifica configurações do sistema"""
    print("=" * 70)
    print("1️⃣ VERIFICAÇÃO DE CONFIGURAÇÃO")
    print("=" * 70)
    
    # Credenciais Google Vision
    cred_path = FinanceiroConfig.GOOGLE_VISION_CREDENTIALS_PATH
    existe = os.path.exists(cred_path)
    print(f"\n📁 Credenciais Google Vision:")
    print(f"   Caminho: {cred_path}")
    print(f"   Status: {'✅ ENCONTRADO' if existe else '❌ NÃO ENCONTRADO'}")
    
    if not existe:
        print("   ⚠️ AÇÃO: Configure GOOGLE_VISION_CREDENTIALS_PATH em financeiro/config.py")
        return False
    
    # Quota OCR
    app = create_app(DevelopmentConfig)
    with app.app_context():
        agora = datetime.now()
        quota = OcrQuota.query.filter_by(ano=agora.year, mes=agora.month).first()
        limite = FinanceiroConfig.get_ocr_monthly_limit()
        
        if quota:
            usado = quota.contador
            disponivel = limite - usado
            print(f"\n📊 Quota OCR:")
            print(f"   Usado: {usado}/{limite}")
            print(f"   Disponível: {disponivel}")
            
            if disponivel <= 0:
                print(f"   ❌ LIMITE ATINGIDO!")
                print(f"   ⚠️ AÇÃO: Aguardar próximo mês ou aumentar limite")
                return False
            else:
                print(f"   ✅ {disponivel} chamadas disponíveis")
        else:
            print(f"\n📊 Quota OCR:")
            print(f"   ✅ Nenhuma chamada feita este mês")
            print(f"   Limite: {limite}")
    
    # CSP Configuration
    print(f"\n🔒 CSP Configuration:")
    print(f"   CSP_NONCE_SOURCES: {app.config.get('CSP_NONCE_SOURCES', 'DEFAULT')}")
    if not app.config.get('CSP_NONCE_SOURCES'):
        print(f"   ✅ Nonce desabilitado (permite unsafe-inline)")
    else:
        print(f"   ⚠️ Nonce habilitado (pode bloquear scripts inline)")
    
    return True

def verificar_pedidos_financeiro():
    """Verifica pedidos pendentes no financeiro"""
    print("\n" + "=" * 70)
    print("2️⃣ PEDIDOS NO FINANCEIRO")
    print("=" * 70)
    
    app = create_app(DevelopmentConfig)
    with app.app_context():
        pedidos_pendentes = Pedido.query.filter_by(
            status=StatusPedido.PENDENTE
        ).all()
        
        print(f"\n📋 Pedidos com status PENDENTE: {len(pedidos_pendentes)}")
        
        if pedidos_pendentes:
            print("\n   Top 5:")
            for p in pedidos_pendentes[:5]:
                totais = p.calcular_totais()
                print(f"   • Pedido #{p.id}")
                print(f"     Cliente: {p.cliente.nome}")
                print(f"     Total: R$ {totais['total_pedido']}")
                print(f"     Pago: R$ {totais['total_pago']}")
                print(f"     Saldo: R$ {totais['saldo']}")
                print(f"     Link: http://localhost:5004/financeiro/pagamento/{p.id}")
                print()
        else:
            print("   ℹ️ Nenhum pedido pendente")

def verificar_pedidos_coleta():
    """Verifica pedidos disponíveis para coleta"""
    print("\n" + "=" * 70)
    print("3️⃣ PEDIDOS DISPONÍVEIS PARA COLETA")
    print("=" * 70)
    
    app = create_app(DevelopmentConfig)
    with app.app_context():
        from meu_app.coletas.services.coleta_service import ColetaService
        
        pedidos_disponiveis = ColetaService.listar_pedidos_para_coleta()
        
        print(f"\n📦 Pedidos disponíveis: {len(pedidos_disponiveis)}")
        
        if pedidos_disponiveis:
            print("\n   Detalhes:")
            for item in pedidos_disponiveis[:5]:
                p = item['pedido']
                print(f"   • Pedido #{p.id}")
                print(f"     Cliente: {p.cliente.nome}")
                print(f"     Status: {p.status.value}")
                print(f"     Total itens: {item['total_itens']}")
                print(f"     Itens coletados: {item['itens_coletados']}")
                print(f"     Itens pendentes: {item['itens_pendentes']}")
                print(f"     Link: http://localhost:5004/coletas")
                print()
        else:
            print("   ℹ️ Nenhum pedido disponível para coleta")
            print("   💡 Dica: Complete o pagamento de algum pedido pendente")

def verificar_logs_recentes():
    """Mostra logs recentes de pagamento"""
    print("\n" + "=" * 70)
    print("4️⃣ ÚLTIMOS PAGAMENTOS REGISTRADOS")
    print("=" * 70)
    
    app = create_app(DevelopmentConfig)
    with app.app_context():
        pagamentos = Pagamento.query.order_by(
            Pagamento.data_pagamento.desc()
        ).limit(5).all()
        
        if pagamentos:
            print(f"\n💰 Últimos 5 pagamentos:")
            for pag in pagamentos:
                print(f"   • Pagamento #{pag.id}")
                print(f"     Pedido: #{pag.pedido_id}")
                print(f"     Valor: R$ {pag.valor}")
                print(f"     Método: {pag.metodo_pagamento}")
                print(f"     Data: {pag.data_pagamento.strftime('%d/%m/%Y %H:%M')}")
                if pag.id_transacao:
                    print(f"     ID Transação: {pag.id_transacao}")
                if pag.caminho_recibo:
                    print(f"     Comprovante: ✅ {pag.caminho_recibo}")
                print()
        else:
            print("   ℹ️ Nenhum pagamento registrado ainda")

def testar_endpoint_ocr():
    """Testa se endpoint OCR está acessível"""
    print("\n" + "=" * 70)
    print("5️⃣ TESTE DO ENDPOINT OCR")
    print("=" * 70)
    
    app = create_app(DevelopmentConfig)
    
    print("\n🌐 Endpoint: /financeiro/processar-recibo-ocr")
    
    # Verificar se rota existe
    with app.app_context():
        for rule in app.url_map.iter_rules():
            if 'ocr' in rule.rule.lower():
                print(f"   ✅ Registrado: {rule.rule}")
                print(f"   Métodos: {rule.methods}")
    
    print("\n💡 Para testar manualmente:")
    print("   1. Abra: http://localhost:5004/financeiro")
    print("   2. Clique em 'Lançar Pagamento' em um pedido")
    print("   3. Abra Console (F12)")
    print("   4. Faça upload de um comprovante")
    print("   5. Verifique os logs no console")

def resumo_e_recomendacoes():
    """Mostra resumo e próximos passos"""
    print("\n" + "=" * 70)
    print("6️⃣ RESUMO E PRÓXIMOS PASSOS")
    print("=" * 70)
    
    print("\n✅ O QUE FOI VERIFICADO:")
    print("   • Configurações do Google Vision")
    print("   • Quota OCR disponível")
    print("   • CSP Configuration")
    print("   • Pedidos pendentes no financeiro")
    print("   • Pedidos disponíveis para coleta")
    print("   • Últimos pagamentos registrados")
    print("   • Endpoint OCR")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("   1. Execute o teste end-to-end:")
    print("      python test_fluxo_financeiro_coleta.py")
    print()
    print("   2. Teste OCR com seu comprovante real:")
    print("      python test_ocr_direto.py /caminho/seu_comprovante.jpg")
    print()
    print("   3. Teste no navegador:")
    print("      • Abra: http://localhost:5004/financeiro")
    print("      • Faça upload de um comprovante")
    print("      • Verifique console (F12) para logs")
    print()
    print("   4. Consulte a documentação:")
    print("      cat FLUXO_FINANCEIRO_COLETA.md")

def main():
    """Executa diagnóstico completo"""
    print("\n" * 2)
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 20 + "DIAGNÓSTICO DO SISTEMA" + " " * 25 + "║")
    print("║" + " " * 18 + "Financeiro → OCR → Coleta" + " " * 23 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        # 1. Configuração
        if not verificar_configuracao():
            print("\n❌ Configure o sistema antes de continuar")
            return 1
        
        # 2. Pedidos Financeiro
        verificar_pedidos_financeiro()
        
        # 3. Pedidos Coleta
        verificar_pedidos_coleta()
        
        # 4. Logs
        verificar_logs_recentes()
        
        # 5. Endpoint OCR
        testar_endpoint_ocr()
        
        # 6. Resumo
        resumo_e_recomendacoes()
        
        print("\n" + "=" * 70)
        print("✅ DIAGNÓSTICO COMPLETO!")
        print("=" * 70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
