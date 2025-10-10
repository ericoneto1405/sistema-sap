# Modelo de planilha para importar pedidos

Use este guia para montar o arquivo CSV ou Excel antes de fazer o upload no modulo **Pedidos -> Importar**.

## Colunas obrigatorias

O arquivo deve conter exatamente as colunas abaixo (nomes em letras minusculas, sem acentos):

| coluna       | descricao                                                                 | exemplo          |
|--------------|----------------------------------------------------------------------------|------------------|
| cliente_id   | ID cadastrado do cliente (consulte em Clientes -> Listar)                 | 12               |
| produto_id   | ID cadastrado do produto (consulte em Produtos -> Listar)                 | 45               |
| quantidade   | Quantidade inteira vendida                                                | 120              |
| preco_venda  | Preco unitario de venda (use ponto como separador decimal)                | 32.50            |
| data         | Data do pedido (YYYY-MM-DD ou DD/MM/YYYY)                                 | 2025-04-29       |

**Importante**
- Cada linha representa um item. Linhas com o mesmo `cliente_id` e a mesma `data` sao combinadas em um unico pedido com varios itens.
- Preencha somente com IDs reais que ja existem no sistema.
- Evite formulas ou celulas mescladas. Salve o arquivo final como CSV ou XLSX.

## Exemplo pronto (CSV)

```
cliente_id,produto_id,quantidade,preco_venda,data
8,21,84,40.00,2025-04-29
8,32,560,32.50,29/04/2025
15,21,168,40.00,2025-04-29
```

No exemplo acima, o cliente 8 gera dois pedidos diferentes porque as datas de cada linha sao diferentes. No segundo pedido (data 29/04/2025) existem dois itens: produto 21 e produto 32.

## Checklist rapido antes do upload

- [ ] Conferi se todos os clientes/produtos existem no sistema.
- [ ] Usei ponto (.) como separador decimal no `preco_venda`.
- [ ] Conferi se todas as datas estao em um formato valido (YYYY-MM-DD ou DD/MM/YYYY).
- [ ] Exportei/salvei o arquivo como CSV, XLSX ou XLS antes de enviar.
