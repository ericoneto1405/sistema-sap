# GUIA DO USUÁRIO - SISTEMA DE APURAÇÃO FINANCEIRA

## 📋 ÍNDICE

1. [Primeiros Passos](#primeiros-passos)
2. [Interface do Sistema](#interface-do-sistema)
3. [Módulo de Apuração](#módulo-de-apuração)
4. [Módulo de Estoques](#módulo-de-estoques)
5. [Módulo de Pedidos](#módulo-de-pedidos)
6. [Módulo de Clientes](#módulo-de-clientes)
7. [Módulo de Produtos](#módulo-de-produtos)
8. [Módulo Financeiro](#módulo-financeiro)
9. [Módulo de Logística](#módulo-de-logística)
10. [Dicas e Truques](#dicas-e-truques)
11. [Solução de Problemas](#solução-de-problemas)
12. [FAQ](#faq)

---

## 🚀 PRIMEIROS PASSOS

### **1. Acessar o Sistema**

#### **Passo 1: Iniciar o Sistema**
```bash
# Na pasta do projeto
cd /Users/ericobrandao/Downloads/SAP

# Executar o sistema
python3 run.py
```

#### **Passo 2: Abrir no Navegador**
```
http://localhost:5004
```

#### **Passo 3: Fazer Login**
- **Usuário**: [Seu usuário]
- **Senha**: [Sua senha]
- **Clique**: "Entrar"

### **2. Navegação Básica**

#### **Menu Principal:**
- **🏠 Dashboard**: Visão geral do sistema
- **📊 Apuração**: Gestão de apurações financeiras
- **📦 Estoques**: Controle de estoque
- **📋 Pedidos**: Gestão de pedidos
- **👥 Clientes**: Cadastro de clientes
- **🛍️ Produtos**: Cadastro de produtos
- **💰 Financeiro**: Controle financeiro
- **🚚 Logística**: Gestão logística

#### **Atalhos de Teclado:**
- **Ctrl + N**: Nova entrada
- **Ctrl + S**: Salvar
- **Ctrl + F**: Buscar
- **Ctrl + P**: Imprimir
- **F5**: Atualizar página

---

## 🖥️ INTERFACE DO SISTEMA

### **1. Layout Principal**

#### **Cabeçalho:**
- **Logo**: Sistema de Apuração Financeira
- **Menu**: Navegação principal
- **Usuário**: Nome e opções
- **Notificações**: Alertas e mensagens

#### **Barra Lateral:**
- **Módulos**: Acesso rápido aos módulos
- **Favoritos**: Módulos mais usados
- **Histórico**: Últimas páginas visitadas

#### **Área de Conteúdo:**
- **Título**: Nome da página atual
- **Breadcrumb**: Navegação hierárquica
- **Conteúdo**: Formulários, tabelas, etc.
- **Rodapé**: Informações da página

### **2. Elementos Comuns**

#### **Botões:**
- **🆕 Novo**: Criar nova entrada
- **💾 Salvar**: Salvar alterações
- **❌ Cancelar**: Descartar alterações
- **🔍 Buscar**: Pesquisar dados
- **📤 Exportar**: Exportar dados
- **🖨️ Imprimir**: Imprimir relatórios

#### **Formulários:**
- **Campos obrigatórios**: Marcados com *
- **Validação**: Mensagens de erro em tempo real
- **Auto-complete**: Sugestões automáticas
- **Máscaras**: Formatação automática de dados

#### **Tabelas:**
- **Ordenação**: Clique no cabeçalho para ordenar
- **Filtros**: Filtros rápidos por coluna
- **Paginação**: Navegação entre páginas
- **Seleção**: Checkbox para ações em lote

---

## 📊 MÓDULO DE APURAÇÃO

### **1. Visão Geral**

#### **O que é:**
O módulo de apuração permite calcular e gerenciar dados financeiros mensais, incluindo receitas, custos e margens.

#### **Funcionalidades:**
- ✅ Cálculo automático de dados financeiros
- ✅ Criação e gestão de apurações
- ✅ Controle de status (pendente/definitiva)
- ✅ Relatórios e estatísticas
- ✅ Histórico de alterações

### **2. Criar Nova Apuração**

#### **Passo 1: Acessar o Módulo**
1. Menu → **Apuração**
2. Clique em **"Nova Apuração"**

#### **Passo 2: Preencher Dados**
- **Mês**: Selecione o mês (1-12)
- **Ano**: Digite o ano (ex: 2025)
- **Receita**: Valor total de receita
- **CPV**: Custo dos produtos vendidos
- **Verbas**: Verbas adicionais (opcional)
- **Outros Custos**: Custos extras (opcional)

#### **Passo 3: Salvar**
1. Clique em **"Salvar"**
2. Confirme os dados
3. Apuração criada com sucesso!

### **3. Gerenciar Apurações Existentes**

#### **Visualizar Apuração:**
1. Na lista de apurações
2. Clique no **ícone de olho** 👁️
3. Visualize todos os detalhes

#### **Editar Apuração:**
1. Na lista de apurações
2. Clique no **ícone de lápis** ✏️
3. Faça as alterações
4. Clique em **"Salvar"**

#### **Excluir Apuração:**
1. Na lista de apurações
2. Clique no **ícone de lixeira** 🗑️
3. Confirme a exclusão

#### **Tornar Definitiva:**
1. Na lista de apurações
2. Clique em **"Tornar Definitiva"**
3. Confirme a ação
4. **⚠️ Atenção**: Apuração definitiva não pode ser editada

### **4. Relatórios e Estatísticas**

#### **Dashboard de Apuração:**
- **Total de Apurações**: Contador geral
- **Receita Total**: Soma de todas as receitas
- **CPV Total**: Soma de todos os custos
- **Margem Total**: Receita - CPV
- **Apurações Definitivas**: Contador de definitivas
- **Apurações Pendentes**: Contador de pendentes

#### **Filtros Disponíveis:**
- **Por Período**: Mês e ano específicos
- **Por Status**: Pendente ou definitiva
- **Por Valor**: Faixas de receita
- **Por Usuário**: Quem criou a apuração

---

## 📦 MÓDULO DE ESTOQUES

### **1. Visão Geral**

#### **O que é:**
O módulo de estoques permite controlar o inventário de produtos, incluindo quantidades, movimentações e histórico.

#### **Funcionalidades:**
- ✅ Controle de quantidade por produto
- ✅ Histórico de movimentações
- ✅ Atualização de estoque
- ✅ Relatórios de inventário
- ✅ Controle de conferentes

### **2. Visualizar Estoque**

#### **Lista de Produtos:**
- **Descrição**: Nome do produto
- **Data de Modificação**: Última atualização
- **Conferente**: Quem conferiu o estoque
- **Status**: Situação atual
- **Estoque Atual**: Quantidade disponível
- **Ações**: Botões de ação

#### **Filtros Disponíveis:**
- **Por Produto**: Buscar produto específico
- **Por Status**: Filtrar por situação
- **Por Conferente**: Quem conferiu
- **Por Data**: Período de modificação

### **3. Atualizar Estoque**

#### **Passo 1: Acessar Atualização**
1. Na lista de estoques
2. Clique em **"Adicionar ao Estoque"**

#### **Passo 2: Selecionar Produto**
- **Produto**: Escolha o produto
- **Quantidade**: Digite a quantidade a adicionar
- **Status**: Selecione o status
- **Observações**: Adicione comentários (opcional)

#### **Passo 3: Salvar**
1. Clique em **"Salvar"**
2. Estoque atualizado automaticamente
3. Histórico registrado

### **4. Histórico de Movimentações**

#### **Acessar Histórico:**
1. Na lista de estoques
2. Clique no **nome do produto** (link azul)
3. Abre nova aba com histórico

#### **Informações do Histórico:**
- **Data**: Quando ocorreu a movimentação
- **Tipo**: Entrada, saída, contagem
- **Quantidade Anterior**: Estoque antes
- **Quantidade Movimentada**: Valor da operação
- **Quantidade Atual**: Estoque depois
- **Responsável**: Quem fez a operação
- **Observações**: Comentários adicionais

---

## 📋 MÓDULO DE PEDIDOS

### **1. Visão Geral**

#### **O que é:**
O módulo de pedidos permite gerenciar pedidos de clientes, incluindo itens, valores e status de pagamento.

#### **Funcionalidades:**
- ✅ Criação de novos pedidos
- ✅ Gestão de itens do pedido
- ✅ Controle de pagamentos
- ✅ Status de pedidos
- ✅ Relatórios de vendas

### **2. Criar Novo Pedido**

#### **Passo 1: Acessar o Módulo**
1. Menu → **Pedidos**
2. Clique em **"Novo Pedido"**

#### **Passo 2: Dados do Cliente**
- **Cliente**: Selecione o cliente
- **Data**: Data do pedido
- **Observações**: Comentários adicionais

#### **Passo 3: Adicionar Itens**
- **Produto**: Selecione o produto
- **Quantidade**: Digite a quantidade
- **Preço Unitário**: Preço por unidade
- **Clique**: **"Adicionar Item"**

#### **Passo 4: Finalizar Pedido**
1. Revise os itens
2. Verifique o total
3. Clique em **"Salvar Pedido"**

### **3. Gerenciar Pedidos Existentes**

#### **Visualizar Pedido:**
1. Na lista de pedidos
2. Clique no **botão "VER"** 👁️
3. Visualize todos os detalhes

#### **Editar Pedido:**
1. Na lista de pedidos
2. Clique no **ícone de lápis** ✏️
3. Faça as alterações
4. Clique em **"Salvar"**

#### **Excluir Pedido:**
1. Na lista de pedidos
2. Clique no **ícone de lixeira** 🗑️
3. Confirme a exclusão

### **4. Controle de Pagamentos**

#### **Registrar Pagamento:**
1. No pedido específico
2. Clique em **"Registrar Pagamento"**
3. Preencha:
   - **Valor**: Valor do pagamento
   - **Forma**: Dinheiro, cartão, PIX
   - **Data**: Data do pagamento
4. Clique em **"Salvar"**

#### **Status de Pagamento:**
- **🟡 Pendente**: Pedido sem pagamento
- **🟢 Pago**: Pedido totalmente pago
- **🔴 Parcial**: Pedido parcialmente pago

---

## 👥 MÓDULO DE CLIENTES

### **1. Visão Geral**

#### **O que é:**
O módulo de clientes permite cadastrar e gerenciar informações dos clientes, incluindo dados pessoais e histórico.

#### **Funcionalidades:**
- ✅ Cadastro de novos clientes
- ✅ Edição de dados existentes
- ✅ Histórico de pedidos
- ✅ Relatórios de clientes
- ✅ Busca e filtros

### **2. Cadastrar Novo Cliente**

#### **Passo 1: Acessar o Módulo**
1. Menu → **Clientes**
2. Clique em **"Novo Cliente"**

#### **Passo 2: Dados Pessoais**
- **Nome**: Nome completo
- **CPF/CNPJ**: Documento de identificação
- **Telefone**: Número de contato
- **Email**: Endereço eletrônico
- **Endereço**: Endereço completo

#### **Passo 3: Salvar**
1. Clique em **"Salvar"**
2. Cliente cadastrado com sucesso!

### **3. Gerenciar Clientes**

#### **Buscar Cliente:**
- **Campo de busca**: Digite nome ou documento
- **Filtros**: Por cidade, status, etc.
- **Resultados**: Lista filtrada

#### **Editar Cliente:**
1. Na lista de clientes
2. Clique no **ícone de lápis** ✏️
3. Faça as alterações
4. Clique em **"Salvar"**

#### **Visualizar Histórico:**
1. No cliente específico
2. Clique em **"Histórico"**
3. Veja todos os pedidos

---

## 🛍️ MÓDULO DE PRODUTOS

### **1. Visão Geral**

#### **O que é:**
O módulo de produtos permite cadastrar e gerenciar o catálogo de produtos, incluindo preços, custos e categorias.

#### **Funcionalidades:**
- ✅ Cadastro de novos produtos
- ✅ Gestão de preços e custos
- ✅ Categorização de produtos
- ✅ Controle de estoque
- ✅ Relatórios de produtos

### **2. Cadastrar Novo Produto**

#### **Passo 1: Acessar o Módulo**
1. Menu → **Produtos**
2. Clique em **"Novo Produto"**

#### **Passo 2: Dados do Produto**
- **Nome**: Nome do produto
- **Descrição**: Descrição detalhada
- **Categoria**: Categoria do produto
- **Preço de Venda**: Preço para o cliente
- **Preço de Custo**: Custo de aquisição
- **Unidade**: Unidade de medida

#### **Passo 3: Salvar**
1. Clique em **"Salvar"**
2. Produto cadastrado com sucesso!

### **3. Gerenciar Produtos**

#### **Buscar Produto:**
- **Campo de busca**: Digite nome ou descrição
- **Filtros**: Por categoria, preço, etc.
- **Resultados**: Lista filtrada

#### **Editar Produto:**
1. Na lista de produtos
2. Clique no **ícone de lápis** ✏️
3. Faça as alterações
4. Clique em **"Salvar"**

#### **Excluir Produto:**
1. Na lista de produtos
2. Clique no **ícone de lixeira** 🗑️
3. Confirme a exclusão

---

## 💰 MÓDULO FINANCEIRO

### **1. Visão Geral**

#### **O que é:**
O módulo financeiro permite controlar receitas, despesas e fluxo de caixa, incluindo relatórios e análises.

#### **Funcionalidades:**
- ✅ Controle de receitas
- ✅ Gestão de despesas
- ✅ Fluxo de caixa
- ✅ Relatórios financeiros
- ✅ Análises de rentabilidade

### **2. Registrar Receita**

#### **Passo 1: Acessar o Módulo**
1. Menu → **Financeiro**
2. Clique em **"Nova Receita"**

#### **Passo 2: Dados da Receita**
- **Descrição**: Descrição da receita
- **Valor**: Valor recebido
- **Data**: Data do recebimento
- **Categoria**: Tipo de receita
- **Observações**: Comentários adicionais

#### **Passo 3: Salvar**
1. Clique em **"Salvar"**
2. Receita registrada com sucesso!

### **3. Registrar Despesa**

#### **Passo 1: Acessar o Módulo**
1. Menu → **Financeiro**
2. Clique em **"Nova Despesa"**

#### **Passo 2: Dados da Despesa**
- **Descrição**: Descrição da despesa
- **Valor**: Valor gasto
- **Data**: Data do gasto
- **Categoria**: Tipo de despesa
- **Observações**: Comentários adicionais

#### **Passo 3: Salvar**
1. Clique em **"Salvar"**
2. Despesa registrada com sucesso!

### **4. Relatórios Financeiros**

#### **Fluxo de Caixa:**
- **Receitas**: Total de receitas do período
- **Despesas**: Total de despesas do período
- **Saldo**: Diferença entre receitas e despesas
- **Gráficos**: Visualização temporal

#### **Análise de Rentabilidade:**
- **Margem Bruta**: Receita - Custos
- **Margem Líquida**: Lucro após despesas
- **ROI**: Retorno sobre investimento
- **Tendências**: Análise temporal

---

## 🚚 MÓDULO DE LOGÍSTICA

### **1. Visão Geral**

#### **O que é:**
O módulo de logística permite gerenciar entregas, coletas e rotas, incluindo controle de veículos e motoristas.

#### **Funcionalidades:**
- ✅ Gestão de entregas
- ✅ Controle de coletas
- ✅ Roteirização
- ✅ Controle de veículos
- ✅ Relatórios de logística

### **2. Registrar Coleta**

#### **Passo 1: Acessar o Módulo**
1. Menu → **Logística**
2. Clique em **"Nova Coleta"**

#### **Passo 2: Dados da Coleta**
- **Pedido**: Selecione o pedido
- **Data**: Data da coleta
- **Responsável**: Quem fará a coleta
- **Observações**: Comentários adicionais

#### **Passo 3: Salvar**
1. Clique em **"Salvar"**
2. Coleta registrada com sucesso!

### **3. Gerenciar Entregas**

#### **Lista de Entregas:**
- **Cliente**: Nome do cliente
- **Produto**: Produto a ser entregue
- **Data**: Data da entrega
- **Status**: Situação da entrega
- **Responsável**: Quem fará a entrega

#### **Status de Entrega:**
- **🟡 Pendente**: Entrega agendada
- **🔵 Em Andamento**: Em trânsito
- **🟢 Entregue**: Entrega concluída
- **🔴 Cancelada**: Entrega cancelada

---

## 💡 DICAS E TRUQUES

### **1. Produtividade**

#### **Atalhos de Teclado:**
- **Tab**: Navegar entre campos
- **Enter**: Confirmar/avançar
- **Esc**: Cancelar/voltar
- **Ctrl + Z**: Desfazer
- **Ctrl + Y**: Refazer

#### **Busca Rápida:**
- **Filtros**: Use filtros para encontrar dados rapidamente
- **Busca**: Campo de busca em tempo real
- **Favoritos**: Marque módulos mais usados

### **2. Organização**

#### **Categorização:**
- **Produtos**: Organize por categorias
- **Clientes**: Agrupe por região ou tipo
- **Pedidos**: Use status para organização
- **Apurações**: Mantenha por período

#### **Backup:**
- **Dados**: Faça backup regular dos dados
- **Configurações**: Salve configurações importantes
- **Relatórios**: Exporte relatórios importantes

### **3. Relatórios**

#### **Relatórios Automáticos:**
- **Diários**: Resumo diário de atividades
- **Semanais**: Relatório semanal de vendas
- **Mensais**: Apuração financeira mensal
- **Anuais**: Relatório anual consolidado

#### **Exportação:**
- **PDF**: Para impressão e arquivo
- **Excel**: Para análise e cálculos
- **CSV**: Para integração com outros sistemas

---

## 🚨 SOLUÇÃO DE PROBLEMAS

### **1. Problemas Comuns**

#### **Erro de Login:**
- **Verificar**: Usuário e senha corretos
- **Solução**: Resetar senha se necessário
- **Contato**: Suporte técnico

#### **Sistema Lento:**
- **Verificar**: Conexão com internet
- **Solução**: Atualizar página (F5)
- **Contato**: Verificar servidor

#### **Dados Não Salvos:**
- **Verificar**: Campos obrigatórios preenchidos
- **Solução**: Verificar validações
- **Contato**: Verificar banco de dados

### **2. Mensagens de Erro**

#### **"Campo Obrigatório":**
- **Causa**: Campo não preenchido
- **Solução**: Preencher todos os campos marcados com *

#### **"Dados Inválidos":**
- **Causa**: Formato incorreto
- **Solução**: Verificar formato (data, CPF, etc.)

#### **"Erro Interno":**
- **Causa**: Problema no servidor
- **Solução**: Tentar novamente ou contatar suporte

### **3. Contato com Suporte**

#### **Informações Necessárias:**
- **Usuário**: Seu nome de usuário
- **Módulo**: Qual módulo apresentou problema
- **Ação**: O que estava tentando fazer
- **Erro**: Mensagem de erro exata
- **Data/Hora**: Quando ocorreu o problema

#### **Canais de Suporte:**
- **Email**: suporte@sistema.com
- **Telefone**: (11) 9999-9999
- **Chat**: Sistema de chat integrado
- **Ticket**: Sistema de tickets

---

## ❓ FAQ

### **1. Como alterar minha senha?**
1. Menu → **Usuário** → **Perfil**
2. Clique em **"Alterar Senha"**
3. Digite senha atual e nova
4. Clique em **"Salvar"**

### **2. Como exportar relatórios?**
1. No relatório desejado
2. Clique em **"Exportar"**
3. Escolha formato (PDF, Excel, CSV)
4. Clique em **"Baixar"**

### **3. Como fazer backup dos dados?**
1. Menu → **Sistema** → **Backup**
2. Clique em **"Gerar Backup"**
3. Escolha local para salvar
4. Clique em **"Confirmar"**

### **4. Como configurar notificações?**
1. Menu → **Usuário** → **Configurações**
2. Aba **"Notificações"**
3. Configure tipos e frequência
4. Clique em **"Salvar"**

### **5. Como recuperar dados excluídos?**
1. Menu → **Sistema** → **Lixeira**
2. Localize o item excluído
3. Clique em **"Restaurar"**
4. Confirme a restauração

### **6. Como personalizar o dashboard?**
1. Menu → **Dashboard**
2. Clique em **"Personalizar"**
3. Arraste widgets para posições desejadas
4. Clique em **"Salvar"**

### **7. Como gerar relatórios personalizados?**
1. Menu → **Relatórios** → **Personalizados**
2. Clique em **"Novo Relatório"**
3. Configure campos e filtros
4. Clique em **"Gerar"**

### **8. Como integrar com outros sistemas?**
1. Menu → **Sistema** → **Integrações**
2. Escolha o sistema desejado
3. Configure parâmetros de conexão
4. Clique em **"Testar Conexão"**

---

## 📞 SUPORTE

### **Horários de Atendimento:**
- **Segunda a Sexta**: 8h às 18h
- **Sábados**: 8h às 12h
- **Emergências**: 24/7

### **Canais de Contato:**
- **Email**: suporte@sistema.com
- **Telefone**: (11) 9999-9999
- **WhatsApp**: (11) 99999-9999
- **Chat**: Sistema integrado

### **Documentação Adicional:**
- **Manual Técnico**: Para desenvolvedores
- **Vídeos Tutoriais**: Canal do YouTube
- **Base de Conhecimento**: Wiki integrada
- **Comunidade**: Fórum de usuários

---

**© 2025 Sistema de Apuração Financeira - Guia do Usuário**
