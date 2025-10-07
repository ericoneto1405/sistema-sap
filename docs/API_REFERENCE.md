# REFERÊNCIA DA API - SISTEMA DE APURAÇÃO FINANCEIRA

## 📋 **VISÃO GERAL**

Esta documentação descreve todos os **endpoints da API** disponíveis no sistema, incluindo parâmetros, respostas e exemplos de uso.

**Base URL**: `http://localhost:5004/api`
**Versão**: 1.0
**Formato**: JSON
**Autenticação**: Session-based (cookies)

---

## 🔐 **AUTENTICAÇÃO**

### **Login**
```http
POST /api/login
```

**Parâmetros:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Resposta de Sucesso:**
```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "user": {
    "id": 1,
    "username": "admin",
    "name": "Administrador"
  }
}
```

**Resposta de Erro:**
```json
{
  "success": false,
  "message": "Usuário ou senha inválidos"
}
```

### **Logout**
```http
POST /api/logout
```

**Resposta:**
```json
{
  "success": true,
  "message": "Logout realizado com sucesso"
}
```

---

## 📊 **MÓDULO DE APURAÇÃO**

### **Listar Apurações**
```http
GET /api/apuracao
```

**Parâmetros de Query:**
- `mes` (opcional): Mês (1-12)
- `ano` (opcional): Ano (ex: 2025)
- `status` (opcional): "pendente" ou "definitiva"
- `page` (opcional): Número da página
- `per_page` (opcional): Itens por página

**Resposta:**
```json
{
  "success": true,
  "data": {
    "apuracoes": [
      {
        "id": 1,
        "mes": 8,
        "ano": 2025,
        "receita_total": 50000.0,
        "custo_produtos": 35000.0,
        "verba_scann": 2000.0,
        "outros_custos": 1000.0,
        "status": "pendente",
        "data_criacao": "2025-08-12T10:00:00",
        "usuario_id": 1
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 1,
      "pages": 1
    }
  }
}
```

### **Obter Apuração por ID**
```http
GET /api/apuracao/{id}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "mes": 8,
    "ano": 2025,
    "receita_total": 50000.0,
    "custo_produtos": 35000.0,
    "verba_scann": 2000.0,
    "outros_custos": 1000.0,
    "status": "pendente",
    "data_criacao": "2025-08-12T10:00:00",
    "usuario_id": 1,
    "usuario": {
      "id": 1,
      "username": "admin",
      "name": "Administrador"
    }
  }
}
```

### **Calcular Dados do Período**
```http
POST /api/apuracao/calcular
```

**Parâmetros:**
```json
{
  "mes": 8,
  "ano": 2025
}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "receita_total": 50000.0,
    "custo_produtos": 35000.0,
    "total_pedidos": 25,
    "pedidos_pagos": 23,
    "pedidos_pendentes": 2,
    "periodo": {
      "mes": 8,
      "ano": 2025,
      "nome_mes": "Agosto"
    }
  }
}
```

### **Criar Nova Apuração**
```http
POST /api/apuracao
```

**Parâmetros:**
```json
{
  "mes": 8,
  "ano": 2025,
  "receita_total": 50000.0,
  "custo_produtos": 35000.0,
  "verba_scann": 2000.0,
  "outros_custos": 1000.0
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Apuração criada com sucesso",
  "data": {
    "id": 2,
    "mes": 8,
    "ano": 2025,
    "receita_total": 50000.0,
    "custo_produtos": 35000.0,
    "verba_scann": 2000.0,
    "outros_custos": 1000.0,
    "status": "pendente",
    "data_criacao": "2025-08-12T10:30:00",
    "usuario_id": 1
  }
}
```

### **Atualizar Apuração**
```http
PUT /api/apuracao/{id}
```

**Parâmetros:**
```json
{
  "receita_total": 52000.0,
  "custo_produtos": 36000.0,
  "verba_scann": 2200.0,
  "outros_custos": 1200.0
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Apuração atualizada com sucesso",
  "data": {
    "id": 1,
    "mes": 8,
    "ano": 2025,
    "receita_total": 52000.0,
    "custo_produtos": 36000.0,
    "verba_scann": 2200.0,
    "outros_custos": 1200.0,
    "status": "pendente",
    "data_modificacao": "2025-08-12T11:00:00"
  }
}
```

### **Tornar Apuração Definitiva**
```http
POST /api/apuracao/{id}/definitiva
```

**Resposta:**
```json
{
  "success": true,
  "message": "Apuração tornada definitiva com sucesso",
  "data": {
    "id": 1,
    "status": "definitiva",
    "data_definitiva": "2025-08-12T11:30:00"
  }
}
```

### **Excluir Apuração**
```http
DELETE /api/apuracao/{id}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Apuração excluída com sucesso"
}
```

### **Dashboard de Apuração**
```http
GET /api/apuracao/dashboard
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "estatisticas": {
      "total_apuracoes": 15,
      "apuracoes_pendentes": 3,
      "apuracoes_definitivas": 12,
      "receita_total": 750000.0,
      "custo_total": 525000.0,
      "margem_total": 225000.0
    },
    "ultimas_apuracoes": [
      {
        "id": 15,
        "mes": 8,
        "ano": 2025,
        "receita_total": 50000.0,
        "status": "pendente"
      }
    ],
    "periodo_atual": {
      "mes": 8,
      "ano": 2025,
      "nome_mes": "Agosto"
    }
  }
}
```

---

## 📦 **MÓDULO DE ESTOQUES**

### **Listar Estoques**
```http
GET /api/estoques
```

**Parâmetros de Query:**
- `produto` (opcional): Nome do produto
- `status` (opcional): Status do estoque
- `conferente` (opcional): Nome do conferente
- `page` (opcional): Número da página

**Resposta:**
```json
{
  "success": true,
  "data": {
    "estoques": [
      {
        "id": 1,
        "produto_id": 1,
        "produto": {
          "id": 1,
          "nome": "Notebook Dell Inspiron",
          "descricao": "Notebook Dell Inspiron 15\""
        },
        "quantidade": 10,
        "status": "disponivel",
        "conferente": "João Silva",
        "data_modificacao": "2025-08-12T10:00:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 1,
      "pages": 1
    }
  }
}
```

### **Obter Estoque por ID**
```http
GET /api/estoques/{id}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "produto_id": 1,
    "produto": {
      "id": 1,
      "nome": "Notebook Dell Inspiron",
      "descricao": "Notebook Dell Inspiron 15\""
    },
    "quantidade": 10,
    "status": "disponivel",
    "conferente": "João Silva",
    "data_modificacao": "2025-08-12T10:00:00"
  }
}
```

### **Atualizar Estoque**
```http
POST /api/estoques/atualizar
```

**Parâmetros:**
```json
{
  "produto_id": 1,
  "quantidade": 5,
  "status": "disponivel",
  "observacoes": "Entrada de estoque"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Estoque atualizado com sucesso",
  "data": {
    "id": 1,
    "quantidade": 15,
    "status": "disponivel",
    "data_modificacao": "2025-08-12T11:00:00"
  }
}
```

### **Histórico de Movimentação**
```http
GET /api/estoques/{produto_id}/historico
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "produto": {
      "id": 1,
      "nome": "Notebook Dell Inspiron"
    },
    "movimentacoes": [
      {
        "id": 1,
        "tipo": "entrada",
        "quantidade_anterior": 0,
        "quantidade_movimentada": 10,
        "quantidade_atual": 10,
        "responsavel": "João Silva",
        "observacoes": "Estoque inicial",
        "data_movimentacao": "2025-08-12T10:00:00"
      }
    ],
    "total": 10
  }
}
```

### **Estoque Atual (AJAX)**
```http
GET /api/estoques/produto/{produto_id}/atual
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "produto_id": 1,
    "quantidade": 15,
    "status": "disponivel",
    "conferente": "João Silva",
    "data_modificacao": "2025-08-12T11:00:00"
  }
}
```

---

## 📋 **MÓDULO DE PEDIDOS**

### **Listar Pedidos**
```http
GET /api/pedidos
```

**Parâmetros de Query:**
- `cliente` (opcional): Nome do cliente
- `status` (opcional): Status do pedido
- `data_inicio` (opcional): Data de início
- `data_fim` (opcional): Data de fim
- `page` (opcional): Número da página

**Resposta:**
```json
{
  "success": true,
  "data": {
    "pedidos": [
      {
        "id": 1,
        "cliente_id": 1,
        "cliente": {
          "id": 1,
          "nome": "João Silva"
        },
        "data": "2025-08-12",
        "total": 7000.0,
        "status": "pago",
        "itens": [
          {
            "id": 1,
            "produto_id": 1,
            "produto": {
              "nome": "Notebook Dell Inspiron"
            },
            "quantidade": 2,
            "preco_unitario": 3500.0,
            "total": 7000.0
          }
        ]
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 1,
      "pages": 1
    }
  }
}
```

### **Obter Pedido por ID**
```http
GET /api/pedidos/{id}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "cliente_id": 1,
    "cliente": {
      "id": 1,
      "nome": "João Silva",
      "cpf": "123.456.789-00",
      "telefone": "(11) 99999-9999"
    },
    "data": "2025-08-12",
    "total": 7000.0,
    "status": "pago",
    "observacoes": "Pedido realizado via telefone",
    "itens": [
      {
        "id": 1,
        "produto_id": 1,
        "produto": {
          "id": 1,
          "nome": "Notebook Dell Inspiron",
          "descricao": "Notebook Dell Inspiron 15\""
        },
        "quantidade": 2,
        "preco_unitario": 3500.0,
        "total": 7000.0
      }
    ],
    "pagamentos": [
      {
        "id": 1,
        "valor": 7000.0,
        "forma": "pix",
        "data": "2025-08-12T10:00:00"
      }
    ]
  }
}
```

### **Criar Novo Pedido**
```http
POST /api/pedidos
```

**Parâmetros:**
```json
{
  "cliente_id": 1,
  "data": "2025-08-12",
  "observacoes": "Pedido realizado via telefone",
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 2,
      "preco_unitario": 3500.0
    }
  ]
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Pedido criado com sucesso",
  "data": {
    "id": 2,
    "total": 7000.0,
    "status": "pendente"
  }
}
```

### **Atualizar Pedido**
```http
PUT /api/pedidos/{id}
```

**Parâmetros:**
```json
{
  "observacoes": "Pedido atualizado",
  "itens": [
    {
      "produto_id": 1,
      "quantidade": 3,
      "preco_unitario": 3500.0
    }
  ]
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Pedido atualizado com sucesso",
  "data": {
    "id": 1,
    "total": 10500.0
  }
}
```

### **Excluir Pedido**
```http
DELETE /api/pedidos/{id}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Pedido excluído com sucesso"
}
```

### **Registrar Pagamento**
```http
POST /api/pedidos/{id}/pagamento
```

**Parâmetros:**
```json
{
  "valor": 7000.0,
  "forma": "pix",
  "data": "2025-08-12",
  "observacoes": "Pagamento realizado no ato"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Pagamento registrado com sucesso",
  "data": {
    "id": 1,
    "pedido_id": 1,
    "valor": 7000.0,
    "forma": "pix",
    "data": "2025-08-12T10:00:00"
  }
}
```

---

## 👥 **MÓDULO DE CLIENTES**

### **Listar Clientes**
```http
GET /api/clientes
```

**Parâmetros de Query:**
- `nome` (opcional): Nome do cliente
- `cpf` (opcional): CPF/CNPJ
- `cidade` (opcional): Cidade
- `page` (opcional): Número da página

**Resposta:**
```json
{
  "success": true,
  "data": {
    "clientes": [
      {
        "id": 1,
        "nome": "João Silva",
        "cpf": "123.456.789-00",
        "telefone": "(11) 99999-9999",
        "email": "joao.silva@email.com",
        "endereco": "Rua das Flores, 123 - São Paulo/SP"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 1,
      "pages": 1
    }
  }
}
```

### **Obter Cliente por ID**
```http
GET /api/clientes/{id}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "nome": "João Silva",
    "cpf": "123.456.789-00",
    "telefone": "(11) 99999-9999",
    "email": "joao.silva@email.com",
    "endereco": "Rua das Flores, 123 - São Paulo/SP",
    "pedidos": [
      {
        "id": 1,
        "data": "2025-08-12",
        "total": 7000.0,
        "status": "pago"
      }
    ]
  }
}
```

### **Criar Novo Cliente**
```http
POST /api/clientes
```

**Parâmetros:**
```json
{
  "nome": "João Silva",
  "cpf": "123.456.789-00",
  "telefone": "(11) 99999-9999",
  "email": "joao.silva@email.com",
  "endereco": "Rua das Flores, 123 - São Paulo/SP"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Cliente cadastrado com sucesso",
  "data": {
    "id": 2,
    "nome": "João Silva"
  }
}
```

### **Atualizar Cliente**
```http
PUT /api/clientes/{id}
```

**Parâmetros:**
```json
{
  "telefone": "(11) 88888-8888",
  "email": "joao.silva.novo@email.com"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Cliente atualizado com sucesso",
  "data": {
    "id": 1,
    "telefone": "(11) 88888-8888",
    "email": "joao.silva.novo@email.com"
  }
}
```

### **Excluir Cliente**
```http
DELETE /api/clientes/{id}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Cliente excluído com sucesso"
}
```

---

## 🛍️ **MÓDULO DE PRODUTOS**

### **Listar Produtos**
```http
GET /api/produtos
```

**Parâmetros de Query:**
- `nome` (opcional): Nome do produto
- `categoria` (opcional): Categoria
- `preco_min` (opcional): Preço mínimo
- `preco_max` (opcional): Preço máximo
- `page` (opcional): Número da página

**Resposta:**
```json
{
  "success": true,
  "data": {
    "produtos": [
      {
        "id": 1,
        "nome": "Notebook Dell Inspiron",
        "descricao": "Notebook Dell Inspiron 15\"",
        "categoria": "Eletrônicos",
        "preco_venda": 3500.0,
        "preco_custo": 2800.0,
        "unidade": "UN"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 1,
      "pages": 1
    }
  }
}
```

### **Obter Produto por ID**
```http
GET /api/produtos/{id}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "nome": "Notebook Dell Inspiron",
    "descricao": "Notebook Dell Inspiron 15\"",
    "categoria": "Eletrônicos",
    "preco_venda": 3500.0,
    "preco_custo": 2800.0,
    "unidade": "UN",
    "estoque": {
      "quantidade": 15,
      "status": "disponivel"
    }
  }
}
```

### **Criar Novo Produto**
```http
POST /api/produtos
```

**Parâmetros:**
```json
{
  "nome": "Notebook Dell Inspiron",
  "descricao": "Notebook Dell Inspiron 15\"",
  "categoria": "Eletrônicos",
  "preco_venda": 3500.0,
  "preco_custo": 2800.0,
  "unidade": "UN"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Produto cadastrado com sucesso",
  "data": {
    "id": 2,
    "nome": "Notebook Dell Inspiron"
  }
}
```

### **Atualizar Produto**
```http
PUT /api/produtos/{id}
```

**Parâmetros:**
```json
{
  "preco_venda": 3600.0,
  "preco_custo": 2900.0
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Produto atualizado com sucesso",
  "data": {
    "id": 1,
    "preco_venda": 3600.0,
    "preco_custo": 2900.0
  }
}
```

### **Excluir Produto**
```http
DELETE /api/produtos/{id}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Produto excluído com sucesso"
}
```

---

## 💰 **MÓDULO FINANCEIRO**

### **Listar Receitas**
```http
GET /api/financeiro/receitas
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "receitas": [
      {
        "id": 1,
        "descricao": "Venda de produtos",
        "valor": 7000.0,
        "data": "2025-08-12",
        "categoria": "Vendas",
        "observacoes": "Venda de notebooks"
      }
    ]
  }
}
```

### **Listar Despesas**
```http
GET /api/financeiro/despesas
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "despesas": [
      {
        "id": 1,
        "descricao": "Compra de produtos",
        "valor": 5600.0,
        "data": "2025-08-12",
        "categoria": "Compras",
        "observacoes": "Compra de notebooks"
      }
    ]
  }
}
```

### **Fluxo de Caixa**
```http
GET /api/financeiro/fluxo-caixa
```

**Parâmetros de Query:**
- `data_inicio` (opcional): Data de início
- `data_fim` (opcional): Data de fim

**Resposta:**
```json
{
  "success": true,
  "data": {
    "periodo": {
      "inicio": "2025-08-01",
      "fim": "2025-08-31"
    },
    "receitas": {
      "total": 7000.0,
      "quantidade": 1
    },
    "despesas": {
      "total": 5600.0,
      "quantidade": 1
    },
    "saldo": 1400.0
  }
}
```

---

## 🚚 **MÓDULO DE LOGÍSTICA**

### **Listar Coletas**
```http
GET /api/logistica/coletas
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "coletas": [
      {
        "id": 1,
        "pedido_id": 1,
        "pedido": {
          "id": 1,
          "cliente": {
            "nome": "João Silva"
          }
        },
        "data": "2025-08-12",
        "responsavel": "Carlos Silva",
        "status": "concluida"
      }
    ]
  }
}
```

### **Registrar Coleta**
```http
POST /api/logistica/coletas
```

**Parâmetros:**
```json
{
  "pedido_id": 1,
  "data": "2025-08-12",
  "responsavel": "Carlos Silva",
  "observacoes": "Coleta realizada com sucesso"
}
```

**Resposta:**
```json
{
  "success": true,
  "message": "Coleta registrada com sucesso",
  "data": {
    "id": 2,
    "pedido_id": 1,
    "status": "concluida"
  }
}
```

---

## 📊 **RELATÓRIOS**

### **Relatório de Vendas**
```http
GET /api/relatorios/vendas
```

**Parâmetros de Query:**
- `data_inicio`: Data de início
- `data_fim`: Data de fim
- `formato`: "pdf", "excel" ou "csv"

**Resposta:**
```json
{
  "success": true,
  "data": {
    "periodo": {
      "inicio": "2025-08-01",
      "fim": "2025-08-31"
    },
    "resumo": {
      "total_vendas": 7000.0,
      "total_pedidos": 1,
      "pedidos_pagos": 1,
      "pedidos_pendentes": 0
    },
    "vendas_por_produto": [
      {
        "produto": "Notebook Dell Inspiron",
        "quantidade": 2,
        "total": 7000.0
      }
    ],
    "vendas_por_cliente": [
      {
        "cliente": "João Silva",
        "total": 7000.0
      }
    ]
  }
}
```

### **Relatório de Estoque**
```http
GET /api/relatorios/estoque
```

**Parâmetros de Query:**
- `formato`: "pdf", "excel" ou "csv"

**Resposta:**
```json
{
  "success": true,
  "data": {
    "resumo": {
      "total_produtos": 1,
      "valor_total": 42000.0
    },
    "produtos": [
      {
        "produto": "Notebook Dell Inspiron",
        "quantidade": 15,
        "valor_unitario": 2800.0,
        "valor_total": 42000.0
      }
    ]
  }
}
```

### **Relatório de Apuração**
```http
GET /api/relatorios/apuracao
```

**Parâmetros de Query:**
- `mes`: Mês (1-12)
- `ano`: Ano
- `formato`: "pdf", "excel" ou "csv"

**Resposta:**
```json
{
  "success": true,
  "data": {
    "periodo": {
      "mes": 8,
      "ano": 2025,
      "nome_mes": "Agosto"
    },
    "resumo": {
      "receita_total": 50000.0,
      "custo_produtos": 35000.0,
      "verba_scann": 2000.0,
      "outros_custos": 1000.0,
      "margem_bruta": 15000.0,
      "margem_liquida": 12000.0
    },
    "detalhamento": {
      "pedidos": 25,
      "clientes": 20,
      "produtos": 15
    }
  }
}
```

---

## 🚨 **CÓDIGOS DE ERRO**

### **Erros HTTP Comuns**

#### **400 Bad Request**
```json
{
  "success": false,
  "error": "BadRequest",
  "message": "Dados inválidos fornecidos",
  "details": {
    "campo": "Erro específico do campo"
  }
}
```

#### **401 Unauthorized**
```json
{
  "success": false,
  "error": "Unauthorized",
  "message": "Usuário não autenticado"
}
```

#### **403 Forbidden**
```json
{
  "success": false,
  "error": "Forbidden",
  "message": "Acesso negado"
}
```

#### **404 Not Found**
```json
{
  "success": false,
  "error": "NotFound",
  "message": "Recurso não encontrado"
}
```

#### **422 Unprocessable Entity**
```json
{
  "success": false,
  "error": "ValidationError",
  "message": "Erro de validação",
  "details": [
    {
      "campo": "nome",
      "erro": "Campo obrigatório"
    }
  ]
}
```

#### **500 Internal Server Error**
```json
{
  "success": false,
  "error": "InternalServerError",
  "message": "Erro interno do servidor",
  "timestamp": "2025-08-12T12:00:00"
}
```

---

## 🔧 **EXEMPLOS DE USO**

### **Exemplo 1: Fluxo Completo de Venda**

#### **1. Criar Cliente**
```bash
curl -X POST http://localhost:5004/api/clientes \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "João Silva",
    "cpf": "123.456.789-00",
    "telefone": "(11) 99999-9999",
    "email": "joao.silva@email.com",
    "endereco": "Rua das Flores, 123 - São Paulo/SP"
  }'
```

#### **2. Criar Produto**
```bash
curl -X POST http://localhost:5004/api/produtos \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Notebook Dell Inspiron",
    "descricao": "Notebook Dell Inspiron 15\"",
    "categoria": "Eletrônicos",
    "preco_venda": 3500.0,
    "preco_custo": 2800.0,
    "unidade": "UN"
  }'
```

#### **3. Atualizar Estoque**
```bash
curl -X POST http://localhost:5004/api/estoques/atualizar \
  -H "Content-Type: application/json" \
  -d '{
    "produto_id": 1,
    "quantidade": 5,
    "status": "disponivel",
    "observacoes": "Estoque inicial"
  }'
```

#### **4. Criar Pedido**
```bash
curl -X POST http://localhost:5004/api/pedidos \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "data": "2025-08-12",
    "observacoes": "Pedido realizado via telefone",
    "itens": [
      {
        "produto_id": 1,
        "quantidade": 2,
        "preco_unitario": 3500.0
      }
    ]
  }'
```

#### **5. Registrar Pagamento**
```bash
curl -X POST http://localhost:5004/api/pedidos/1/pagamento \
  -H "Content-Type: application/json" \
  -d '{
    "valor": 7000.0,
    "forma": "pix",
    "data": "2025-08-12",
    "observacoes": "Pagamento realizado no ato"
  }'
```

#### **6. Calcular Dados para Apuração**
```bash
curl -X POST http://localhost:5004/api/apuracao/calcular \
  -H "Content-Type: application/json" \
  -d '{
    "mes": 8,
    "ano": 2025
  }'
```

#### **7. Criar Apuração**
```bash
curl -X POST http://localhost:5004/api/apuracao \
  -H "Content-Type: application/json" \
  -d '{
    "mes": 8,
    "ano": 2025,
    "receita_total": 7000.0,
    "custo_produtos": 5600.0,
    "verba_scann": 200.0,
    "outros_custos": 100.0
  }'
```

### **Exemplo 2: Consultas com Filtros**

#### **Buscar Pedidos por Período**
```bash
curl "http://localhost:5004/api/pedidos?data_inicio=2025-08-01&data_fim=2025-08-31"
```

#### **Buscar Produtos por Categoria**
```bash
curl "http://localhost:5004/api/produtos?categoria=Eletrônicos"
```

#### **Buscar Clientes por Cidade**
```bash
curl "http://localhost:5004/api/clientes?cidade=São Paulo"
```

---

## 📱 **INTEGRAÇÃO COM FRONTEND**

### **Exemplo de JavaScript (AJAX)**

#### **Listar Apurações**
```javascript
fetch('/api/apuracao')
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log('Apurações:', data.data.apuracoes);
    } else {
      console.error('Erro:', data.message);
    }
  })
  .catch(error => {
    console.error('Erro na requisição:', error);
  });
```

#### **Criar Nova Apuração**
```javascript
const novaApuração = {
  mes: 8,
  ano: 2025,
  receita_total: 50000.0,
  custo_produtos: 35000.0,
  verba_scann: 2000.0,
  outros_custos: 1000.0
};

fetch('/api/apuracao', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(novaApuração)
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Apuração criada:', data.data);
  } else {
    console.error('Erro:', data.message);
  }
})
.catch(error => {
  console.error('Erro na requisição:', error);
});
```

#### **Atualizar Estoque**
```javascript
const atualizacaoEstoque = {
  produto_id: 1,
  quantidade: 5,
  status: 'disponivel',
  observacoes: 'Entrada de estoque'
};

fetch('/api/estoques/atualizar', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(atualizacaoEstoque)
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Estoque atualizado:', data.data);
  } else {
    console.error('Erro:', data.message);
  }
})
.catch(error => {
  console.error('Erro na requisição:', error);
});
```

---

## 📚 **RECURSOS ADICIONAIS**

### **Documentação Relacionada**
- **Guia do Usuário**: `docs/GUIA_USUARIO.md`
- **Tutorial Interativo**: `docs/TUTORIAL_INTERATIVO.md`
- **Documentação Técnica**: `docs/FASE7_DOCUMENTACAO_COMPLETA.md`
- **Guia do Desenvolvedor**: `docs/GUIA_DESENVOLVEDOR.md`

### **Ferramentas de Teste**
- **Postman**: Coleção de endpoints
- **Insomnia**: Testes de API
- **cURL**: Linha de comando
- **Thunder Client**: Extensão do VS Code

### **Suporte e Contato**
- **Email**: suporte@sistema.com
- **Telefone**: (11) 9999-9999
- **Documentação**: docs/ (pasta de documentação)
- **Issues**: Sistema de tickets integrado

---

**© 2025 Sistema de Apuração Financeira - Referência da API**
