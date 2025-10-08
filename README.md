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

### Desenvolvimento local

O script `init_db.py` respeita as variáveis de ambiente `INITIAL_ADMIN_USERNAME`
e `INITIAL_ADMIN_PASSWORD`. Configure **apenas** em ambientes de teste:

```bash
export INITIAL_ADMIN_USERNAME=admin
export INITIAL_ADMIN_PASSWORD=admin123
python init_db.py
```

⚠️ **ATENÇÃO**
- Use estas credenciais apenas para desenvolvimento local.
- Remova as variáveis após a seed para evitar vazamentos.
- Troque a senha no primeiro acesso.

### Produção

```bash
export INITIAL_ADMIN_USERNAME="admin_producao"
export INITIAL_ADMIN_PASSWORD="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
python init_db.py
```

Armazene as credenciais em um cofre (1Password, Vault, etc.) e force troca periódica.

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
│   ├── security.py      # CSRF, rate limit, headers
│   ├── clientes/        # Módulo de clientes
│   ├── produtos/        # Módulo de produtos
│   ├── pedidos/         # Módulo de pedidos
│   ├── financeiro/      # Módulo financeiro (OCR)
│   ├── vendedor/        # Painel do vendedor
│   ├── apuracao/        # Apuração mensal
│   ├── coletas/         # Coletas e logística
│   └── ...
├── scripts/             # Scripts utilitários
│   └── phase2_smoke.sh  # Smoke test da Fase 2
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

## 🔐 Segurança Base (Fase 2)

A aplicação implementa os controles mínimos de endurecimento definidos na Fase 2:

- **CSRF global** com Flask-WTF/CSRFProtect (exceções podem ser aplicadas via `csrf.exempt`).
- **Headers seguros** via Flask-Talisman: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`,
  `Referrer-Policy: no-referrer`, CSP com nonce automático e HSTS habilitado apenas em produção.
- **Cookies de sessão protegidos** (`HttpOnly`, `SameSite=Lax`, `Secure` em produção) com expiração padrão de 8h.
- **Rate limiting** com Flask-Limiter: `/login` limitado a **10 requisições/minuto por IP** e limite padrão de 200/hora para rotas sensíveis.

> Em DEV/TESTE o redirecionamento HTTPS/HSTS fica desativado automaticamente.
> Caso precise ajustar manualmente, utilize as flags `TALISMAN_FORCE_HTTPS=False`
> e `TALISMAN_STRICT_TRANSPORT_SECURITY=False` nas variáveis de ambiente.

### Smoke test da Fase 2

Após iniciar o servidor em desenvolvimento (`python run.py`), execute:

```bash
bash scripts/phase2_smoke.sh http://127.0.0.1:5004
```

O script valida CSRF, headers obrigatórios, flags de cookie e o rate limit do login.

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
