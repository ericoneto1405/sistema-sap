# 📊 FLUXO FINANCEIRO → COLETA

## Visão Geral

Este documento descreve o fluxo completo de um pedido desde o financeiro até a liberação para coleta.

---

## 🔄 Fluxo Completo

```
[Pedido Criado]
      ↓
[Status: PENDENTE]
      ↓
[Registrar Pagamento 1] → Valor parcial
      ↓
[Status: PENDENTE] (ainda falta pagar)
      ↓
[Registrar Pagamento N] → Completa o valor
      ↓
[Verificação: total_pago >= total_pedido?]
      ↓ SIM
[Status: PAGAMENTO_APROVADO]
      ↓
[Pedido disponível em /coletas]
      ↓
[Processar Coleta]
      ↓
[Status: COLETA_PARCIAL ou COLETA_CONCLUIDA]
```

---

## 📋 Estados do Pedido (StatusPedido)

| Status | Descrição | Quando ocorre |
|--------|-----------|---------------|
| **PENDENTE** | Pedido criado, aguardando pagamento | Criação do pedido |
| **PAGAMENTO_APROVADO** | Pagamento completo recebido | total_pago >= total_pedido |
| **COLETA_PARCIAL** | Coleta iniciada mas não finalizada | Alguns itens coletados |
| **COLETA_CONCLUIDA** | Todos itens foram coletados | 100% dos itens coletados |
| **CANCELADO** | Pedido cancelado | Cancelamento manual |

---

## 💰 Módulo Financeiro

### Endpoint: `/financeiro/pagamento/<pedido_id>`

#### Fluxo de Pagamento

1. **Upload de Comprovante (Opcional)**
   - Suporta: JPG, PNG, PDF
   - Google Vision OCR extrai automaticamente:
     - Valor do pagamento
     - ID da transação
     - Data
     - Dados bancários

2. **Preenchimento do Formulário**
   - Valor a Pagar (obrigatório)
   - Método de Pagamento (obrigatório)
   - Observações (opcional)
   - ID Transação (auto-preenchido por OCR)

3. **Validações**
   ```python
   # meu_app/financeiro/services.py linha 236-237
   if total_pago_decimal >= total_pedido_decimal:
       pedido.status = StatusPedido.PAGAMENTO_APROVADO
   ```

4. **Salvamento**
   - Pagamento salvo em `pagamentos`
   - Comprovante salvo em `uploads/recibos_pagamento/`
   - Hash SHA-256 evita duplicatas
   - Status do pedido atualizado automaticamente

### Campos da Tabela `pagamentos`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | Integer | PK |
| pedido_id | Integer | FK para pedido |
| valor | Decimal(10,2) | Valor pago |
| metodo_pagamento | String(50) | PIX, Cartão, Dinheiro, etc |
| data_pagamento | DateTime | Timestamp do pagamento |
| caminho_recibo | String(255) | Nome do arquivo do comprovante |
| recibo_sha256 | String(64) | Hash para evitar duplicatas |
| id_transacao | String(100) | ID extraído pelo OCR |
| data_comprovante | Date | Data extraída do comprovante |
| banco_emitente | String(100) | Banco extraído do comprovante |
| observacoes | Text | Observações opcionais |

---

## 🚚 Módulo Coletas

### Endpoint: `/coletas`

#### Query de Pedidos Disponíveis

```python
# meu_app/coletas/services/coleta_service.py linha 103
Pedido.status.in_([
    StatusPedido.PAGAMENTO_APROVADO,
    StatusPedido.COLETA_PARCIAL
])
```

#### Critérios para Aparecer em Coletas

1. ✅ **Status = PAGAMENTO_APROVADO** OU **COLETA_PARCIAL**
2. ✅ **Pelo menos 1 item no pedido**
3. ✅ **Itens pendentes > 0** (ainda há algo para coletar)

#### Fluxo de Coleta

1. **Listar Pedidos Disponíveis**
   - Mostra apenas pedidos com pagamento aprovado
   - Exibe total de itens vs itens coletados

2. **Selecionar Pedido**
   - Ver detalhes dos itens
   - Registrar quantidades coletadas

3. **Processar Coleta**
   - Movimentação de estoque
   - Atualização de status:
     - **COLETA_PARCIAL**: Se ainda falta coletar itens
     - **COLETA_CONCLUIDA**: Se todos itens foram coletados

---

## 🧪 Teste End-to-End

Execute o teste automático:

```bash
python test_fluxo_financeiro_coleta.py
```

### O que o teste faz:

1. Cria pedido de teste (R$ 100.00)
2. Registra pagamento parcial (R$ 50.00) → Status: PENDENTE
3. Registra pagamento final (R$ 50.00) → Status: PAGAMENTO_APROVADO
4. Verifica se pedido aparece em /coletas ✅

### Resultado esperado:

```
✅ Status mudou para PAGAMENTO_APROVADO corretamente!
✅ Pedido 5 ESTÁ DISPONÍVEL para coleta!
🎉 TESTE COMPLETO: TODOS OS PASSOS OK!
```

---

## 🔍 Troubleshooting

### Problema: Pedido não aparece em Coletas após pagamento

**Diagnóstico:**

```python
# 1. Verificar status do pedido
pedido = Pedido.query.get(pedido_id)
print(f"Status: {pedido.status.value}")

# 2. Verificar totais
totais = pedido.calcular_totais()
print(f"Total pedido: {totais['total_pedido']}")
print(f"Total pago: {totais['total_pago']}")
print(f"Saldo: {totais['saldo']}")

# 3. Verificar pagamentos
for pag in pedido.pagamentos:
    print(f"Pagamento #{pag.id}: R$ {pag.valor}")
```

**Causas possíveis:**

1. **Status não mudou para PAGAMENTO_APROVADO**
   - Verificar se `total_pago >= total_pedido`
   - Ver logs em `meu_app/financeiro/services.py`

2. **Query de coletas não inclui o status**
   - Verificar `meu_app/coletas/services/coleta_service.py` linha 103

3. **Pedido sem itens**
   - Verificar se `pedido.itens` tem pelo menos 1 item

### Problema: Campo "Valor a Pagar" não preenche automaticamente

**Diagnóstico:**

1. **Abrir Console do Browser (F12)**
   - Verificar logs do JavaScript
   - Procurar erros de CSP ou fetch

2. **Verificar CSP**
   ```python
   # config.py - DevelopmentConfig
   CSP_NONCE_SOURCES = []  # Deve estar vazio em dev
   ```

3. **Testar OCR isoladamente**
   ```bash
   python test_ocr_direto.py /caminho/comprovante.jpg
   ```

4. **Verificar credenciais Google Vision**
   ```bash
   ls /Users/ericobrandao/keys/gvision-credentials.json
   ```

5. **Verificar quota OCR**
   ```python
   from meu_app.models import OcrQuota
   quota = OcrQuota.query.filter_by(ano=2025, mes=10).first()
   print(f"Quota: {quota.contador}/1000")
   ```

**Causas possíveis:**

1. **JavaScript não carrega** → Erro de CSP
2. **Fetch bloqueado** → Verificar `connect-src` no CSP
3. **OCR falha** → Ver logs do servidor
4. **Quota esgotada** → Aguardar próximo mês ou aumentar limite
5. **Comprovante incompatível** → Testar com outro arquivo

---

## 📊 Logs Importantes

### Financeiro - Pagamento Registrado

```
[2025-10-08 11:07:29] INFO [meu_app] Pagamento registrado: Pedido #5 - R$ 50.00 - ID Transação: TEST001
[2025-10-08 11:07:29] INFO [meu_app] Dados extraídos - Banco: None, Agência: None, Conta: None
```

### Status Mudou

```python
# Verificar no banco
SELECT id, status FROM pedido WHERE id = ?;
# Deve retornar: status = 'Pagamento Aprovado'
```

---

## 🔒 Segurança

### Upload de Comprovantes

1. **Validação de Tipo**
   - Apenas: JPG, PNG, PDF, DOC, DOCX
   - Tamanho máximo: 5MB

2. **Hash SHA-256**
   - Evita upload duplicado do mesmo comprovante
   - Hash salvo em `recibo_sha256`

3. **Nome Seguro**
   - Gerado automaticamente
   - Não expõe nome original do arquivo

4. **Armazenamento**
   - Diretório: `uploads/recibos_pagamento/`
   - Permissões: Apenas leitura para usuários autenticados

---

## 📈 Métricas

### Performance

- **OCR com cache**: ~500ms
- **OCR sem cache**: ~2-5s (Google Vision)
- **Salvamento de pagamento**: ~100ms
- **Query de pedidos para coleta**: ~50ms

### Quota OCR

- **Limite mensal**: 1.000 chamadas
- **Cache**: Ativado (reduz consumo)
- **Status atual**: Ver `/financeiro/quota-ocr`

---

## 🎯 Próximas Melhorias

1. **OCR Offline** (Tesseract) como fallback
2. **Webhook para notificações** de pagamento aprovado
3. **Dashboard** com métricas de pagamentos
4. **Exportação** de comprovantes em lote
5. **API REST** para integração externa

---

## 📞 Suporte

**Logs do Sistema:**
```bash
tail -f logs/app.log
```

**Debug Mode:**
```python
# config.py
DEBUG = True
LOG_LEVEL = 'DEBUG'
```

**Testes:**
```bash
# Teste completo
python test_fluxo_financeiro_coleta.py

# Teste OCR isolado
python test_ocr_direto.py /caminho/comprovante.jpg
```

---

**Última atualização**: 08/10/2025  
**Versão**: 1.0  
**Status**: ✅ Fluxo testado e funcionando
