# 📤 Guia de Importação de Pedidos Históricos

## Visão Geral

A funcionalidade de importação de pedidos permite que você adicione pedidos antigos ao sistema, criando uma base histórica completa. Isso é útil para:

- Migração de sistemas antigos
- Consolidação de dados históricos
- Backup e restauração de pedidos
- Análise de tendências históricas

## Como Acessar

1. Acesse o módulo **Pedidos** no menu principal
2. Clique no botão **"📤 Importar Histórico"** no topo da página
3. Você será direcionado para a página de importação

## Formato do Arquivo

A importação aceita dois formatos de arquivo:

### CSV (Comma Separated Values)
- Extensão: `.csv`
- Codificação: UTF-8
- Separador: vírgula (`,`)

### Excel
- Extensões: `.xlsx` ou `.xls`
- Formato moderno do Microsoft Excel

## Estrutura dos Dados

O arquivo deve conter as seguintes colunas obrigatórias:

| Coluna | Descrição | Exemplo | Tipo |
|--------|-----------|---------|------|
| `cliente_id` | ID do cliente no sistema | 1 | Número inteiro |
| `produto_id` | ID do produto no sistema | 5 | Número inteiro |
| `quantidade` | Quantidade do produto | 10 | Número inteiro |
| `preco_venda` | Preço de venda unitário | 25.50 | Número decimal |
| `data` | Data do pedido | 2024-01-15 | Data (YYYY-MM-DD) |

### Formatos de Data Aceitos

- **ISO 8601**: `2024-01-15` (recomendado)
- **Formato brasileiro**: `15/01/2024`
- **Com hora**: `2024-01-15 14:30:00`

## Exemplo de Arquivo CSV

```csv
cliente_id,produto_id,quantidade,preco_venda,data
1,5,10,25.50,2024-01-15
1,3,5,15.00,2024-01-15
2,7,20,8.75,2024-01-16
2,5,8,25.50,2024-01-16
3,5,15,25.50,2024-01-17
3,3,10,15.00,2024-01-17
3,7,25,8.75,2024-01-17
```

### Como Interpretar o Exemplo

No exemplo acima:
- **Pedido 1**: Cliente 1, em 15/01/2024, comprou 10 unidades do produto 5 e 5 unidades do produto 3
- **Pedido 2**: Cliente 2, em 16/01/2024, comprou 20 unidades do produto 7 e 8 unidades do produto 5
- **Pedido 3**: Cliente 3, em 17/01/2024, comprou 15 unidades do produto 5, 10 unidades do produto 3 e 25 unidades do produto 7

> **Nota**: Linhas com mesma data e cliente são agrupadas em um único pedido.

## Passo a Passo para Importação

### 1. Preparar o Arquivo

1. Baixe o arquivo de exemplo clicando em **"Baixar Arquivo de Exemplo"**
2. Abra o arquivo em um editor de planilhas (Excel, Google Sheets, LibreOffice Calc)
3. Preencha com seus dados históricos
4. Certifique-se de que:
   - Os IDs de clientes existem no sistema
   - Os IDs de produtos existem no sistema
   - As datas estão no formato correto
   - Os valores numéricos não contêm caracteres especiais (use ponto para decimais)

### 2. Validar os Dados

Antes de importar, verifique:

- [ ] Todos os clientes estão cadastrados no sistema
- [ ] Todos os produtos estão cadastrados no sistema
- [ ] As datas estão corretas e no formato adequado
- [ ] Os preços estão com valores válidos
- [ ] As quantidades são números inteiros positivos
- [ ] Não há linhas vazias ou com dados incompletos

### 3. Fazer o Upload

1. Na página de importação, clique em **"Clique para selecionar"** ou arraste o arquivo
2. O sistema mostrará o nome do arquivo selecionado
3. Clique em **"Importar Pedidos"**
4. Aguarde o processamento (uma barra de progresso será exibida)

### 4. Verificar o Resultado

Após a importação, o sistema mostrará:

- ✅ **Mensagem de sucesso**: Quantidade de pedidos importados
- ⚠️ **Avisos**: Se houver erros em algumas linhas
- ❌ **Erro**: Se a importação falhar completamente

## Tratamento de Erros

### Erros Comuns e Soluções

| Erro | Causa | Solução |
|------|-------|---------|
| "Cliente X não encontrado" | ID do cliente não existe | Cadastre o cliente primeiro ou corrija o ID |
| "Produto Y não encontrado" | ID do produto não existe | Cadastre o produto primeiro ou corrija o ID |
| "Formato de arquivo inválido" | Arquivo não é CSV ou Excel | Converta o arquivo para CSV ou Excel |
| "Colunas faltantes" | Arquivo não tem todas as colunas | Adicione as colunas obrigatórias |
| "Erro ao converter data" | Formato de data inválido | Use o formato YYYY-MM-DD |

### Comportamento em Caso de Erro

O sistema é **tolerante a falhas**:

- Se houver erro em uma linha, ela será ignorada
- As linhas válidas serão importadas normalmente
- Um log de erros será registrado no sistema
- Você verá um resumo dos erros ao final

## Cálculos Automáticos

Durante a importação, o sistema calcula automaticamente:

- **Preço de compra**: Obtido do cadastro do produto
- **Valor total de venda**: quantidade × preço_venda
- **Valor total de compra**: quantidade × preço_compra (do produto)
- **Lucro bruto**: valor_total_venda - valor_total_compra

## Boas Práticas

### 1. Teste com Poucos Dados
Comece importando um arquivo pequeno (5-10 pedidos) para validar o formato.

### 2. Faça Backup
Antes de importações grandes, faça backup do banco de dados.

### 3. Organize por Data
Ordene seus dados por data para facilitar a visualização e análise posterior.

### 4. Use IDs Corretos
Sempre verifique os IDs de clientes e produtos antes de importar:
- Acesse **Clientes** → **Listar** para ver os IDs dos clientes
- Acesse **Produtos** → **Listar** para ver os IDs dos produtos

### 5. Evite Duplicação
O sistema não verifica duplicatas automaticamente. Certifique-se de não importar pedidos já existentes.

## Limitações

- **Tamanho máximo**: Depende da configuração do servidor (padrão: 16MB)
- **Status inicial**: Todos os pedidos importados começam como "Pendente"
- **Pagamentos**: Não são importados automaticamente (devem ser adicionados manualmente depois)
- **Confirmação comercial**: Pedidos importados não são confirmados automaticamente

## Segurança

- ✅ Requer login no sistema
- ✅ Requer permissão de acesso a pedidos
- ✅ Registra log de atividade
- ✅ Valida dados antes de inserir no banco
- ✅ Usa transações para garantir integridade

## Monitoramento

Após a importação, você pode:

1. **Ver os pedidos importados**: Vá para **Pedidos** → **Listar**
2. **Verificar logs**: Consulte o arquivo `instance/logs/app.log`
3. **Conferir atividades**: Acesse o módulo de auditoria (se disponível)

## Suporte

Em caso de problemas:

1. Verifique o log de erros do sistema
2. Consulte este guia novamente
3. Entre em contato com o administrador do sistema
4. Envie o arquivo que está causando problema para análise

## Exemplo Completo

### Cenário: Importar 3 pedidos históricos

**Arquivo: `pedidos_antigos.csv`**

```csv
cliente_id,produto_id,quantidade,preco_venda,data
1,5,10,25.50,2024-01-15
1,3,5,15.00,2024-01-15
2,7,20,8.75,2024-01-16
2,5,8,25.50,2024-01-16
3,5,15,25.50,2024-01-17
```

**Resultado esperado:**
- ✅ 3 pedidos importados
- Pedido 1: Cliente 1, Total R$ 330,00 (10×25.50 + 5×15.00)
- Pedido 2: Cliente 2, Total R$ 379,00 (20×8.75 + 8×25.50)
- Pedido 3: Cliente 3, Total R$ 382,50 (15×25.50)

---

**Versão**: 1.0  
**Data**: Outubro 2025  
**Autor**: Sistema SAP

