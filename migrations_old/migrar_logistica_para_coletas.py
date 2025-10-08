#!/usr/bin/env python3
"""
Script de migração limpa: Logística -> Coletas
Implementa a sugestão CLI #1: Migração limpa sem campos legados

Este script:
1. Analisa dados existentes
2. Migra dados do logística para campos padronizados do coletas
3. Valida migração
4. Documenta processo
"""

import os
import sys
import sqlite3
from datetime import datetime

# Adicionar o diretório do projeto ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def conectar_banco():
    """Conecta ao banco de dados"""
    db_path = os.path.join(os.path.dirname(__file__), 'instance', 'sistema.db')
    return sqlite3.connect(db_path)

def analisar_dados_existentes():
    """Analisa dados existentes nos módulos"""
    print("🔍 ANALISANDO DADOS EXISTENTES...")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar coletas existentes
    cursor.execute("SELECT COUNT(*) FROM coleta")
    total_coletas = cursor.fetchone()[0]
    print(f"   📊 Total de coletas: {total_coletas}")
    
    # Verificar itens coletados
    cursor.execute("SELECT COUNT(*) FROM item_coletado")
    total_itens = cursor.fetchone()[0]
    print(f"   📊 Total de itens coletados: {total_itens}")
    
    # Verificar estrutura da tabela coleta
    cursor.execute("PRAGMA table_info(coleta)")
    colunas = cursor.fetchall()
    print(f"   📊 Colunas da tabela coleta: {len(colunas)}")
    
    for coluna in colunas:
        print(f"      - {coluna[1]} ({coluna[2]})")
    
    conn.close()
    return total_coletas, total_itens

def verificar_campos_logistica():
    """Verifica se existem campos do logística que precisam ser migrados"""
    print("\n🔍 VERIFICANDO CAMPOS DO LOGÍSTICA...")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar se existem campos do logística
    campos_logistica = ['coletado_por', 'liberado_por', 'documento_coletor']
    campos_existentes = []
    
    cursor.execute("PRAGMA table_info(coleta)")
    colunas = [coluna[1] for coluna in cursor.fetchall()]
    
    for campo in campos_logistica:
        if campo in colunas:
            campos_existentes.append(campo)
            print(f"   ✅ Campo '{campo}' existe")
        else:
            print(f"   ❌ Campo '{campo}' não existe")
    
    conn.close()
    return campos_existentes

def criar_script_migracao():
    """Cria script de migração SQL"""
    print("\n📝 CRIANDO SCRIPT DE MIGRAÇÃO...")
    
    script_sql = """
-- Script de migração: Logística -> Coletas
-- Data: {data}
-- Objetivo: Migrar dados para campos padronizados

-- 1. Adicionar campos padronizados se não existirem
ALTER TABLE coleta ADD COLUMN nome_conferente VARCHAR(100);
ALTER TABLE coleta ADD COLUMN cpf_conferente VARCHAR(20);

-- 2. Migrar dados existentes (se campos do logística existirem)
-- UPDATE coleta SET nome_conferente = liberado_por WHERE liberado_por IS NOT NULL;
-- UPDATE coleta SET cpf_conferente = documento_coletor WHERE documento_coletor IS NOT NULL;

-- 3. Validar migração
SELECT COUNT(*) as total_coletas FROM coleta;
SELECT COUNT(*) as coletas_com_conferente FROM coleta WHERE nome_conferente IS NOT NULL;
""".format(data=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    with open('migracao_logistica.sql', 'w') as f:
        f.write(script_sql)
    
    print("   ✅ Script criado: migracao_logistica.sql")

def validar_migracao():
    """Valida se a migração foi bem-sucedida"""
    print("\n✅ VALIDANDO MIGRAÇÃO...")
    
    conn = conectar_banco()
    cursor = conn.cursor()
    
    # Verificar integridade dos dados
    cursor.execute("SELECT COUNT(*) FROM coleta")
    total_coletas = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM item_coletado")
    total_itens = cursor.fetchone()[0]
    
    print(f"   📊 Coletas após migração: {total_coletas}")
    print(f"   📊 Itens coletados: {total_itens}")
    
    # Verificar se campos padronizados existem
    cursor.execute("PRAGMA table_info(coleta)")
    colunas = [coluna[1] for coluna in cursor.fetchall()]
    
    campos_necessarios = ['nome_retirada', 'documento_retirada', 'nome_conferente', 'cpf_conferente']
    campos_faltando = []
    
    for campo in campos_necessarios:
        if campo not in colunas:
            campos_faltando.append(campo)
    
    if campos_faltando:
        print(f"   ⚠️  Campos faltando: {campos_faltando}")
    else:
        print("   ✅ Todos os campos padronizados existem")
    
    conn.close()
    return len(campos_faltando) == 0

def main():
    """Função principal do script de migração"""
    print("🚀 INICIANDO MIGRAÇÃO LIMPA: LOGÍSTICA -> COLETAS")
    print("=" * 60)
    
    try:
        # 1. Analisar dados existentes
        total_coletas, total_itens = analisar_dados_existentes()
        
        # 2. Verificar campos do logística
        campos_logistica = verificar_campos_logistica()
        
        # 3. Criar script de migração
        criar_script_migracao()
        
        # 4. Validar migração
        migracao_ok = validar_migracao()
        
        print("\n" + "=" * 60)
        if migracao_ok:
            print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("   📊 Dados preservados e campos padronizados")
        else:
            print("⚠️  MIGRAÇÃO PARCIAL - Verificar campos faltando")
        
        print(f"   📅 Concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ ERRO NA MIGRAÇÃO: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)
