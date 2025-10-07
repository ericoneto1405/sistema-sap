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

## 🚀 Início Rápido

### **Desenvolvimento (DEV)**

```bash
# 1. Clone e prepare o ambiente
git clone https://github.com/ericoneto1405/sistema-sap.git
cd sistema-sap
python3 -m venv venv
source venv/bin/activate

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure variáveis de ambiente
cp .env.example .env
# Edite .env se necessário (SECRET_KEY já foi gerada)

# 4. Inicialize o banco de dados
python init_db.py

# 5. Execute o servidor de desenvolvimento
python run.py
```

**Acesse:** `http://127.0.0.1:5004`

### **Produção (PROD)**

```bash
# 1. Configure variáveis de ambiente
export FLASK_ENV=production
export SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
export DATABASE_URL="postgresql://usuario:senha@localhost:5432/sistema_sap"
export REDIS_URL="redis://localhost:6379/0"

# 2. Instale dependências
pip install -r requirements.txt

# 3. Inicialize o banco
python init_db.py

# 4. Execute com Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

# 5. (Recomendado) Com systemd/supervisor
gunicorn -w 4 -b 127.0.0.1:8000 --access-logfile - --error-logfile - wsgi:app
```

⚠️ **IMPORTANTE:**
- Use PostgreSQL ou MySQL em produção (não SQLite)
- Configure HTTPS via Nginx/Apache
- Use Redis para cache e rate limiting
- Configure firewall e backups automáticos

---

## 🔑 Credenciais (Apenas DEV/Seed)

### **Para Desenvolvimento Local**

O script `init_db.py` pode criar um usuário administrador de teste:

```bash
# Opção 1: Usuário de seed para DEV (APENAS TESTES LOCAIS)
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=admin123
python init_db.py
```

⚠️ **ATENÇÃO:**
- Estas credenciais são **APENAS para desenvolvimento local**
- **NUNCA** use `admin:admin123` em produção
- **NUNCA** commite estas credenciais
- Troque imediatamente após criar

### **Para Produção**

```bash
# Gerar senha forte aleatória
export ADMIN_USERNAME="admin_producao"
export ADMIN_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
python init_db.py

# Anote as credenciais em gerenciador de senhas (LastPass, 1Password, etc.)
```

---

## 📂 Estrutura do Projeto

```
sistema-sap/
├── config.py            # Configurações por ambiente
├── wsgi.py              # Entry point produção (Gunicorn)
├── run.py               # Entry point desenvolvimento
├── .env.example         # Template de variáveis
├── meu_app/             # Aplicação principal
│   ├── __init__.py      # App Factory
│   ├── clientes/        # Módulo de clientes
│   ├── produtos/        # Módulo de produtos
│   ├── pedidos/         # Módulo de pedidos
│   ├── financeiro/      # Módulo financeiro (OCR)
│   ├── vendedor/        # Painel do vendedor
│   ├── apuracao/        # Apuração mensal
│   ├── coletas/         # Coletas e logística
│   └── ...
├── app/                 # Utilitários compartilhados
│   └── security.py      # CSRF, Rate Limiting, Talisman
├── docs/                # Documentação completa
├── tests/               # Testes automatizados
└── instance/            # Dados (não versionado)
```

---

## 🛠 Tecnologias

- **Backend:** Flask 3.0, SQLAlchemy 2.0
- **Banco de Dados:** SQLite (dev) / PostgreSQL (prod)
- **Frontend:** HTML5, CSS3, JavaScript
- **Segurança:** Flask-WTF, Flask-Limiter, Flask-Talisman
- **APIs:** Google Cloud Vision (OCR)
- **PDF:** ReportLab
- **WSGI:** Gunicorn

---

## 🔧 Comandos Úteis

### Desenvolvimento

```bash
# Iniciar servidor dev
python run.py

# Iniciar com Flask CLI
export FLASK_APP=run:app
flask run --host=127.0.0.1 --port=5004

# Criar backup do banco
python -c "from meu_app.routes import backup_banco; backup_banco()"
```

### Produção

```bash
# Iniciar com Gunicorn (4 workers)
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

# Com reload (staging)
gunicorn -w 4 -b 0.0.0.0:8000 --reload wsgi:app

# Health check
curl http://localhost:8000/health
```

### Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=meu_app --cov-report=html

# Apenas testes de integração
pytest -m integration
```

---

## 📚 Documentação Completa

- [Guia do Usuário](docs/GUIA_USUARIO.md)
- [Guia do Desenvolvedor](docs/GUIA_DESENVOLVEDOR.md)
- [Arquitetura do Sistema](docs/ARQUITETURA_SISTEMA.md)
- [API Reference](docs/API_REFERENCE.md)
- [Relatório de Discovery](RELATORIO_DISCOVERY.md)
- [Migração App Factory](MIGRACAO_APP_FACTORY.md)

---

## ⚙️ Configuração por Ambiente

O sistema usa **App Factory pattern** com configurações separadas:

| Ambiente | Config | Entry Point | Uso |
|----------|--------|-------------|-----|
| **Development** | `DevelopmentConfig` | `run.py` | `python run.py` |
| **Testing** | `TestingConfig` | - | `pytest` |
| **Production** | `ProductionConfig` | `wsgi.py` | `gunicorn wsgi:app` |

Configurações em `config.py`:
- **BaseConfig**: Configuração base compartilhada
- **DevelopmentConfig**: Debug ativo, SQLite, cookies inseguros
- **TestingConfig**: Banco em memória, CSRF desabilitado
- **ProductionConfig**: HTTPS obrigatório, PostgreSQL, security headers

---

## 🔒 Segurança

### **NUNCA faça:**
- ❌ Commitar credenciais no código
- ❌ Usar `admin:admin123` em produção
- ❌ Usar SQLite em produção
- ❌ Desabilitar HTTPS em produção
- ❌ Expor SECRET_KEY

### **SEMPRE faça:**
- ✅ Use senhas fortes (16+ caracteres)
- ✅ Configure HTTPS em produção
- ✅ Use PostgreSQL/MySQL em produção
- ✅ Habilite rate limiting
- ✅ Mantenha dependências atualizadas
- ✅ Revise logs regularmente

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
