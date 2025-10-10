# Modelo de planilha para importar pedidos

Use este guia para montar o arquivo CSV ou Excel antes de fazer o upload no modulo **Pedidos -> Importar**.

## Colunas obrigatorias

O arquivo deve conter exatamente as colunas abaixo (nomes em letras minusculas, sem acentos):

| coluna        | descricao                                                                 | exemplo                         |
|---------------|----------------------------------------------------------------------------|---------------------------------|
| cliente_nome  | Nome do cliente exatamente como aparece na tela de Clientes               | KAIQUE ITATIM                   |
| produto_nome  | Nome do produto exatamente como aparece na tela de Produtos               | SKOL LATA 350ML                 |
| quantidade    | Quantidade inteira vendida                                                | 120                             |
| preco_venda   | Preco unitario de venda (use ponto como separador decimal)                | 32.50                           |
| data          | Data do pedido (YYYY-MM-DD ou DD/MM/YYYY)                                 | 2025-04-29                      |

**Importante**
    - Cada linha representa um item. Linhas com o mesmo `cliente_nome` e a mesma `data` sao combinadas em um unico pedido com varios itens.
- Utilize nomes exatamente iguais aos cadastrados (o sistema ignora maiusculas/minusculas e acentos, mas nomes duplicados geram erro).
- Evite formulas ou celulas mescladas. Salve o arquivo final como CSV ou XLSX.

## Exemplo pronto (CSV)

```
cliente_nome,produto_nome,quantidade,preco_venda,data
KAIQUE ITATIM,SKOL LATA 350ML,286,31.00,2025-04-29
KAIQUE ITATIM,BRAHMA CHOPP LATA 350 ML,286,32.00,29/04/2025
LUCIANO MOURA,RED BULL ENERGY DRINK 250 ML,144,150.00,2025-04-30
```

No exemplo acima, o cliente "KAIQUE ITATIM" gera um pedido com dois itens (mesma data) e o cliente "LUCIANO MOURA" gera outro pedido com um item.

## Checklist rapido antes do upload

- [ ] Copiei os nomes direto das telas de Clientes e Produtos para evitar erros de digitacao.
- [ ] Usei ponto (.) como separador decimal no `preco_venda`.
- [ ] Conferi se todas as datas estao em um formato valido (YYYY-MM-DD ou DD/MM/YYYY).
- [ ] Exportei/salvei o arquivo como CSV, XLSX ou XLS antes de enviar.
