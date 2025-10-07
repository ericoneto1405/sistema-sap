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
