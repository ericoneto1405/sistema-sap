# Migrations

Esta pasta contém todos os scripts de migração do banco de dados.

## Arquivos Disponíveis

### Migrações de Campos
- `migracao_add_campos_comprovante.py` - Adiciona campos extraídos do comprovante via OCR
- `migracao_add_conferente.py` - Adiciona campos do conferente
- `migracao_add_id_transacao.py` - Adiciona campo ID da transação
- `migracao_add_recibo_meta.py` - Adiciona metadados do recibo
- `migracao_add_recibo.py` - Adiciona campos básicos do recibo

### Migrações de Sistema
- `migracao_logistica.sql` - Script SQL para migração do módulo logística
- `migrar_logistica_para_coletas.py` - Script Python para migração completa

## Como Usar

Para executar uma migração específica:

```bash
cd /path/to/project
python3 migrations/migracao_nome.py
```

Para migrações SQL:

```bash
cd /path/to/project
sqlite3 instance/sistema.db < migrations/migracao_logistica.sql
```

## Status

✅ **Todas as migrações foram executadas** - Estes arquivos são mantidos apenas para histórico e referência.
