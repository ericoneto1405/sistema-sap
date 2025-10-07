#!/usr/bin/env python3
"""
Migração para adicionar novos campos ao modelo Pagamento
Campos adicionados: data_comprovante, banco_emitente, agencia_recebedor, conta_recebedor, chave_pix_recebedor
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from meu_app import create_app
from meu_app.models import db
from sqlalchemy import text

def executar_migracao():
    """Executa a migração para adicionar novos campos ao modelo Pagamento"""
    
    app = create_app()
    
    with app.app_context():
        try:
            print("🚀 Iniciando migração para adicionar campos de comprovante...")
            
            # Verificar se os campos já existem
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(pagamento)"))
                colunas_existentes = [row[1] for row in result]
            
            campos_para_adicionar = [
                ('data_comprovante', 'DATE'),
                ('banco_emitente', 'VARCHAR(100)'),
                ('agencia_recebedor', 'VARCHAR(20)'),
                ('conta_recebedor', 'VARCHAR(50)'),
                ('chave_pix_recebedor', 'VARCHAR(255)')
            ]
            
            campos_adicionados = []
            
            for nome_campo, tipo_campo in campos_para_adicionar:
                if nome_campo not in colunas_existentes:
                    sql = f"ALTER TABLE pagamento ADD COLUMN {nome_campo} {tipo_campo}"
                    with db.engine.connect() as conn:
                        conn.execute(text(sql))
                        conn.commit()
                    campos_adicionados.append(nome_campo)
                    print(f"✅ Campo '{nome_campo}' adicionado com sucesso")
                else:
                    print(f"⚠️  Campo '{nome_campo}' já existe, pulando...")
            
            if campos_adicionados:
                print(f"\n🎉 Migração concluída! {len(campos_adicionados)} campos adicionados:")
                for campo in campos_adicionados:
                    print(f"   - {campo}")
            else:
                print("\n✅ Todos os campos já existem. Migração não necessária.")
                
            print("\n📊 Verificando estrutura da tabela pagamento...")
            with db.engine.connect() as conn:
                result = conn.execute(text("PRAGMA table_info(pagamento)"))
                print("\nEstrutura atual da tabela 'pagamento':")
                print("-" * 50)
                for row in result:
                    print(f"{row[1]:<25} {row[2]:<15} {'NOT NULL' if row[3] else 'NULL':<10}")
            
        except Exception as e:
            print(f"❌ Erro durante a migração: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    sucesso = executar_migracao()
    if sucesso:
        print("\n🎯 Migração executada com sucesso!")
        print("💡 Os novos campos estão prontos para uso:")
        print("   - data_comprovante: Data extraída do comprovante")
        print("   - banco_emitente: Banco de quem enviou")
        print("   - agencia_recebedor: Agência do recebedor")
        print("   - conta_recebedor: Conta ou PIX do recebedor")
        print("   - chave_pix_recebedor: Chave PIX específica")
    else:
        print("\n💥 Migração falhou!")
        sys.exit(1)
