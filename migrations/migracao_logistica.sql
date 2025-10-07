
-- Script de migração: Logística -> Coletas
-- Data: 2025-09-28 18:34:59
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
