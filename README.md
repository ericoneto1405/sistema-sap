# 🏢 Sistema SAP - Gestão de Pedidos e Vendas

Sistema completo de gestão empresarial desenvolvido em Flask.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red)

---

## ✨ Funcionalidades

- 🛒 **Gestão de Pedidos** - Criação, edição e acompanhamento
- 👥 **Gestão de Clientes** - Cadastro completo e histórico
- 📦 **Controle de Estoque** - Produtos e movimentações
- 💰 **Financeiro** - Pagamentos e OCR de recibos
- 📊 **Apuração Mensal** - Relatórios automatizados
- 🎯 **Painel do Vendedor** - Análise de clientes e rankings
- 📋 **Coletas** - Logística e geração de recibos PDF

---

## 🚀 Instalação Rápida

```bash
git clone https://github.com/ericoneto1405/sistema-sap.git
cd sistema-sap
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python init_db.py
python run.py
```

Acesse: `http://127.0.0.1:5004`

---

## 🔑 Primeiro Acesso

- **Usuário:** `admin`
- **Senha:** `admin123`

⚠️ **Altere a senha após o primeiro login!**

---

## 📂 Estrutura do Projeto

```
sistema-sap/
├── meu_app/              # Aplicação principal
│   ├── clientes/         # Módulo de clientes
│   ├── produtos/         # Módulo de produtos
│   ├── pedidos/          # Módulo de pedidos
│   ├── financeiro/       # Módulo financeiro (OCR)
│   ├── vendedor/         # Painel do vendedor
│   ├── apuracao/         # Apuração mensal
│   ├── coletas/          # Coletas e logística
│   └── ...
├── docs/                 # Documentação completa
├── tests/                # Testes automatizados
├── instance/             # Dados (não versionado)
└── requirements.txt
```

---

## 🛠 Tecnologias

- **Backend:** Flask 3.0, SQLAlchemy 2.0
- **Banco de Dados:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript
- **APIs:** Google Cloud Vision (OCR)
- **PDF:** ReportLab

---

## 📚 Documentação

- [Guia do Usuário](docs/GUIA_USUARIO.md)
- [Guia do Desenvolvedor](docs/GUIA_DESENVOLVEDOR.md)
- [Arquitetura do Sistema](docs/ARQUITETURA_SISTEMA.md)
- [API Reference](docs/API_REFERENCE.md)

---

## 🤝 Contribuição

1. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
2. Commit: `git commit -m 'Adiciona nova funcionalidade'`
3. Push: `git push origin feature/nova-funcionalidade`
4. Abra um Pull Request

---

## 📝 Licença

Projeto privado. Todos os direitos reservados.

---

## 👤 Autor

**Érico Brandão**
- GitHub: [@ericoneto1405](https://github.com/ericoneto1405)

---

**Desenvolvido com ❤️ em Python + Flask**
# Teste de auto-commit

---

## 🚀 Como Iniciar a Aplicação

### **Desenvolvimento**

1. **Configure as variáveis de ambiente:**
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
# A SECRET_KEY já foi gerada automaticamente
```

2. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

3. **Inicialize o banco de dados:**
```bash
python init_db.py
```

4. **Inicie o servidor de desenvolvimento:**
```bash
# Método 1: Usando run.py
python run.py

# Método 2: Usando Flask CLI
export FLASK_APP=wsgi:app
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5004
```

5. **Acesse:** `http://localhost:5004`

### **Produção**

1. **Configure as variáveis de ambiente de produção:**
```bash
export FLASK_ENV=production
export SECRET_KEY="sua-chave-secreta-forte-aqui"
export DATABASE_URL="postgresql://user:pass@localhost/sap"
export REDIS_URL="redis://localhost:6379/0"
```

2. **Instale as dependências de produção:**
```bash
pip install -r requirements.txt
```

3. **Inicie com Gunicorn:**
```bash
# 4 workers, bind na porta 8000
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

# Com log de acesso
gunicorn -w 4 -b 0.0.0.0:8000 --access-logfile - wsgi:app

# Com reload automático (apenas staging)
gunicorn -w 4 -b 0.0.0.0:8000 --reload wsgi:app
```

### **Testes**

```bash
# Configurar ambiente de testes
export FLASK_ENV=testing

# Executar testes
pytest

# Com cobertura
pytest --cov=meu_app --cov-report=html
```

### **Variáveis de Ambiente Obrigatórias**

- `SECRET_KEY`: Chave secreta para sessões e CSRF (gerada automaticamente no .env)
- `DATABASE_URL` (produção): URL de conexão com o banco de dados
- `GOOGLE_APPLICATION_CREDENTIALS`: Caminho para credenciais do Google Vision

### **Variáveis de Ambiente Opcionais**

- `FLASK_ENV`: Ambiente de execução (development/testing/production)
- `FLASK_DEBUG`: Habilitar modo debug (True/False)
- `HOST`: Host do servidor (padrão: 0.0.0.0)
- `PORT`: Porta do servidor (padrão: 5004)
- `REDIS_URL`: URL de conexão com Redis (para cache e rate limiting)
- `OCR_MONTHLY_LIMIT`: Limite mensal de chamadas OCR (padrão: 1000)
- `LOG_LEVEL`: Nível de log (DEBUG/INFO/WARNING/ERROR/CRITICAL)

## ⚙️ Ambientes de Configuração

O sistema suporta três ambientes distintos:

- **Development**: Desenvolvimento local com debug ativo
- **Testing**: Execução de testes automatizados
- **Production**: Ambiente de produção com todas as proteções ativas

Cada ambiente possui configurações específicas em `config.py`.

---

## 🔒 Segurança

⚠️ **IMPORTANTE**: 
- Nunca commite o arquivo `.env` com credenciais reais
- Altere as credenciais padrão após o primeiro deploy
- Em produção, use HTTPS obrigatório
- Configure PostgreSQL ou MySQL ao invés de SQLite

Para instruções de desenvolvimento e seed do banco, consulte `init_db.py`.

