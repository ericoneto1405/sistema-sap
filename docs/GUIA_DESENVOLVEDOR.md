# GUIA DO DESENVOLVEDOR - SISTEMA DE APURAÇÃO FINANCEIRA

## 👨‍💻 **VISÃO GERAL PARA DESENVOLVEDORES**

Este guia é destinado a **desenvolvedores** que irão trabalhar com o código, implementar novas funcionalidades, corrigir bugs ou fazer manutenção no sistema.

**Nível**: Intermediário a Avançado
**Linguagem**: Python 3.8+
**Framework**: Flask 2.0+
**Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)

---

## 🚀 **CONFIGURAÇÃO DO AMBIENTE DE DESENVOLVIMENTO**

### **1. Pré-requisitos**
```bash
# Python 3.8 ou superior
python3 --version

# pip (gerenciador de pacotes)
pip3 --version

# git (controle de versão)
git --version

# Editor recomendado: VS Code com extensões Python
```

### **2. Configuração do Projeto**
```bash
# Clone o repositório
git clone <repository-url>
cd SAP

# Crie ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
# No macOS/Linux:
source venv/bin/activate
# No Windows:
venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações
```

### **3. Estrutura do Projeto**
```
📁 SAP/
├── 📁 meu_app/                 # Aplicação principal
│   ├── 📁 apuracao/           # Módulo de apuração
│   ├── 📁 estoques/            # Módulo de estoques
│   ├── 📁 pedidos/             # Módulo de pedidos
│   ├── 📁 clientes/            # Módulo de clientes
│   ├── 📁 produtos/            # Módulo de produtos
│   ├── 📁 financeiro/          # Módulo financeiro
│   ├── 📁 logistica/           # Módulo de logística
│   ├── 📁 usuarios/            # Módulo de usuários
│   ├── 📁 log_atividades/      # Módulo de logs
│   ├── 📄 __init__.py          # Inicialização da aplicação
│   ├── 📄 models.py            # Modelos de dados
│   ├── 📄 routes.py            # Rotas principais
│   └── 📄 static/              # Arquivos estáticos
├── 📁 docs/                    # Documentação
├── 📁 tests/                   # Testes
├── 📄 run.py                   # Script de execução
└── 📄 requirements.txt         # Dependências
```

---

## 🏗️ **ARQUITETURA E PADRÕES**

### **1. Princípios SOLID**
```python
# Single Responsibility Principle (SRP)
class ApuracaoService:
    def __init__(self, repository, validator, calculator):
        self.repository = repository
        self.validator = validator
        self.calculator = calculator
    
    def criar_apuracao(self, dados):
        # Apenas orquestra a criação
        self.validator.validar(dados)
        resultado = self.calculator.calcular(dados)
        return self.repository.salvar(resultado)

# Open/Closed Principle (OCP)
class IApuracaoCalculator(ABC):
    @abstractmethod
    def calcular(self, dados):
        pass

class ApuracaoCalculatorPadrao(IApuracaoCalculator):
    def calcular(self, dados):
        # Implementação padrão

class ApuracaoCalculatorAvancado(IApuracaoCalculator):
    def calcular(self, dados):
        # Implementação avançada
```

### **2. Injeção de Dependência**
```python
# Factory Pattern
class ApuracaoServiceFactory:
    @staticmethod
    def create_service(environment: str = 'production') -> IApuracaoService:
        if environment == 'test':
            return ApuracaoService(
                repository=ApuracaoRepositoryMock(),
                validator=ApuracaoValidatorMock(),
                calculator=ApuracaoCalculatorMock()
            )
        
        return ApuracaoService(
            repository=ApuracaoRepository(),
            validator=ApuracaoValidator(),
            calculator=ApuracaoCalculator()
        )

# Service Locator (opcional)
class GlobalServiceRegistry:
    _services = {}
    
    @classmethod
    def register(cls, name: str, service: Any):
        cls._services[name] = service
    
    @classmethod
    def get(cls, name: str) -> Any:
        return cls._services.get(name)
```

### **3. Repository Pattern**
```python
class IApuracaoRepository(ABC):
    @abstractmethod
    def fetch_by_id(self, id: int) -> Optional[Apuracao]:
        pass
    
    @abstractmethod
    def create(self, apuracao: Apuracao) -> Apuracao:
        pass
    
    @abstractmethod
    def update(self, apuracao: Apuracao) -> Apuracao:
        pass
    
    @abstractmethod
    def delete(self, id: int) -> bool:
        pass

class ApuracaoRepository(IApuracaoRepository):
    def __init__(self, db_session):
        self.db = db_session
    
    def fetch_by_id(self, id: int) -> Optional[Apuracao]:
        return self.db.query(Apuracao).filter(Apuracao.id == id).first()
    
    def create(self, apuracao: Apuracao) -> Apuracao:
        self.db.add(apuracao)
        self.db.commit()
        return apuracao
```

---

## 🗄️ **MODELOS E BANCO DE DADOS**

### **1. Definição de Modelos**
```python
from sqlalchemy import Column, Integer, String, Decimal, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from decimal import Decimal

Base = declarative_base()

class Apuracao(Base):
    __tablename__ = 'apuracao'
    
    id = Column(Integer, primary_key=True)
    mes = Column(Integer, nullable=False)
    ano = Column(Integer, nullable=False)
    receita_total = Column(Decimal(10, 2), nullable=False)
    custo_produtos = Column(Decimal(10, 2), nullable=False)
    verba_scann = Column(Decimal(10, 2), default=0)
    outros_custos = Column(Decimal(10, 2), default=0)
    status = Column(String(20), default='pendente')
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_modificacao = Column(DateTime, onupdate=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey('usuario.id'))
    
    # Relacionamentos
    usuario = relationship("Usuario", back_populates="apuracoes")
    pedidos = relationship("Pedido", back_populates="apuracao")
    
    def __repr__(self):
        return f"<Apuracao(mes={self.mes}, ano={self.ano}, status={self.status})>"
    
    @property
    def margem_bruta(self) -> Decimal:
        """Calcula a margem bruta da apuração."""
        return self.receita_total - self.custo_produtos
    
    @property
    def margem_liquida(self) -> Decimal:
        """Calcula a margem líquida da apuração."""
        return self.margem_bruta - self.verba_scann - self.outros_custos
```

### **2. Migrações de Banco**
```python
# Exemplo de migração
from sqlalchemy import text
from meu_app import db

def migrate_estoque():
    """Migração para adicionar campo data_modificacao na tabela estoque."""
    try:
        # Adicionar coluna
        db.session.execute(text("""
            ALTER TABLE estoque 
            ADD COLUMN data_modificacao DATETIME
        """))
        
        # Atualizar registros existentes
        db.session.execute(text("""
            UPDATE estoque 
            SET data_modificacao = CURRENT_TIMESTAMP 
            WHERE data_modificacao IS NULL
        """))
        
        db.session.commit()
        print("✅ Migração concluída com sucesso!")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro na migração: {e}")
        raise
```

### **3. Índices e Performance**
```python
# Índices para otimização
class Apuracao(Base):
    __tablename__ = 'apuracao'
    __table_args__ = (
        # Índice composto para consultas por período
        Index('idx_apuracao_periodo', 'mes', 'ano'),
        # Índice para status
        Index('idx_apuracao_status', 'status'),
        # Índice para usuário
        Index('idx_apuracao_usuario', 'usuario_id'),
    )
```

---

## 🔧 **SERVIÇOS E LÓGICA DE NEGÓCIO**

### **1. Estrutura de Serviços**
```python
class ApuracaoService:
    def __init__(self, repository: IApuracaoRepository, 
                 validator: IApuracaoValidator,
                 calculator: IApuracaoCalculator,
                 cache: IApuracaoCache,
                 logger: IApuracaoLogger):
        self.repository = repository
        self.validator = validator
        self.calculator = calculator
        self.cache = cache
        self.logger = logger
    
    def criar_apuracao(self, dados: Dict[str, Any]) -> Apuracao:
        """Cria uma nova apuração com validação e cálculos automáticos."""
        try:
            # Validação
            self.validator.validar_dados_apuracao(dados)
            
            # Cálculos automáticos
            dados_calculados = self.calculator.calcular_dados_periodo(
                mes=dados['mes'],
                ano=dados['ano']
            )
            
            # Merge com dados fornecidos
            dados_finais = {**dados_calculados, **dados}
            
            # Criação da apuração
            apuracao = Apuracao(**dados_finais)
            apuracao = self.repository.create(apuracao)
            
            # Invalidação de cache
            self.cache.invalidate('apuracoes_lista')
            self.cache.invalidate(f'apuracao_{apuracao.id}')
            
            # Log de sucesso
            self.logger.info(f"Apuração criada com sucesso: ID {apuracao.id}")
            
            return apuracao
            
        except Exception as e:
            self.logger.error(f"Erro ao criar apuração: {str(e)}")
            raise
```

### **2. Validação de Dados**
```python
class ApuracaoValidator:
    def validar_dados_apuracao(self, dados: Dict[str, Any]) -> bool:
        """Valida os dados de entrada para criação de apuração."""
        erros = []
        
        # Validação de período
        if not self._validar_periodo(dados.get('mes'), dados.get('ano')):
            erros.append("Período inválido")
        
        # Validação de valores
        if not self._validar_valores(dados):
            erros.append("Valores inválidos")
        
        # Validação de unicidade
        if not self._validar_unicidade_periodo(dados.get('mes'), dados.get('ano')):
            erros.append("Já existe apuração para este período")
        
        if erros:
            raise ApuracaoValidationError(f"Erros de validação: {'; '.join(erros)}")
        
        return True
    
    def _validar_periodo(self, mes: int, ano: int) -> bool:
        """Valida se o período é válido."""
        if not (1 <= mes <= 12):
            return False
        if not (2020 <= ano <= 2030):
            return False
        return True
    
    def _validar_valores(self, dados: Dict[str, Any]) -> bool:
        """Valida se os valores são válidos."""
        campos_numericos = ['receita_total', 'custo_produtos', 'verba_scann', 'outros_custos']
        
        for campo in campos_numericos:
            valor = dados.get(campo, 0)
            if not isinstance(valor, (int, float, Decimal)) or valor < 0:
                return False
        
        return True
```

### **3. Cálculos Automáticos**
```python
class ApuracaoCalculator:
    def __init__(self, pedido_repository: IPedidoRepository):
        self.pedido_repository = pedido_repository
    
    def calcular_dados_periodo(self, mes: int, ano: int) -> Dict[str, Any]:
        """Calcula automaticamente os dados do período especificado."""
        # Buscar pedidos do período
        pedidos = self.pedido_repository.fetch_by_period(mes, ano)
        
        # Filtrar apenas pedidos pagos
        pedidos_pagos = [p for p in pedidos if p.status == 'pago']
        
        # Cálculos
        receita_total = self._calcular_receita_total(pedidos_pagos)
        custo_produtos = self._calcular_custo_produtos(pedidos_pagos)
        
        return {
            'receita_total': receita_total,
            'custo_produtos': custo_produtos,
            'total_pedidos': len(pedidos),
            'pedidos_pagos': len(pedidos_pagos),
            'pedidos_pendentes': len(pedidos) - len(pedidos_pagos)
        }
    
    def _calcular_receita_total(self, pedidos: List[Pedido]) -> Decimal:
        """Calcula a receita total dos pedidos."""
        return sum(pedido.total for pedido in pedidos)
    
    def _calcular_custo_produtos(self, pedidos: List[Pedido]) -> Decimal:
        """Calcula o custo total dos produtos vendidos."""
        custo_total = Decimal('0')
        
        for pedido in pedidos:
            for item in pedido.itens:
                custo_unitario = item.produto.preco_custo
                quantidade = item.quantidade
                custo_total += custo_unitario * quantidade
        
        return custo_total
```

---

## 🧪 **TESTES E QUALIDADE DE CÓDIGO**

### **1. Estrutura de Testes**
```python
import unittest
from unittest.mock import Mock, patch
from decimal import Decimal
from meu_app.apuracao.services import ApuracaoService
from meu_app.apuracao.models import Apuracao
from meu_app.apuracao.exceptions import ApuracaoValidationError

class TestApuracaoService(unittest.TestCase):
    def setUp(self):
        """Configuração inicial para cada teste."""
        # Mocks das dependências
        self.mock_repository = Mock()
        self.mock_validator = Mock()
        self.mock_calculator = Mock()
        self.mock_cache = Mock()
        self.mock_logger = Mock()
        
        # Instância do serviço
        self.service = ApuracaoService(
            repository=self.mock_repository,
            validator=self.mock_validator,
            calculator=self.mock_calculator,
            cache=self.mock_cache,
            logger=self.mock_logger
        )
    
    def test_criar_apuracao_sucesso(self):
        """Testa criação bem-sucedida de apuração."""
        # Arrange
        dados = {
            'mes': 8,
            'ano': 2025,
            'receita_total': Decimal('50000.00'),
            'custo_produtos': Decimal('35000.00')
        }
        
        apuracao_criada = Apuracao(**dados)
        apuracao_criada.id = 1
        
        self.mock_validator.validar_dados_apuracao.return_value = True
        self.mock_calculator.calcular_dados_periodo.return_value = dados
        self.mock_repository.create.return_value = apuracao_criada
        
        # Act
        resultado = self.service.criar_apuracao(dados)
        
        # Assert
        self.assertEqual(resultado.id, 1)
        self.assertEqual(resultado.mes, 8)
        self.assertEqual(resultado.ano, 2025)
        self.mock_repository.create.assert_called_once()
        self.mock_cache.invalidate.assert_called()
    
    def test_criar_apuracao_validacao_falha(self):
        """Testa falha na validação de dados."""
        # Arrange
        dados = {'mes': 13, 'ano': 2025}  # Mês inválido
        self.mock_validator.validar_dados_apuracao.side_effect = ApuracaoValidationError("Mês inválido")
        
        # Act & Assert
        with self.assertRaises(ApuracaoValidationError):
            self.service.criar_apuracao(dados)
        
        self.mock_repository.create.assert_not_called()
```

### **2. Testes de Integração**
```python
class TestApuracaoIntegration(unittest.TestCase):
    def setUp(self):
        """Configuração para testes de integração."""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.db = self.app.extensions['sqlalchemy'].db
        
        with self.app.app_context():
            self.db.create_all()
            self._criar_dados_teste()
    
    def tearDown(self):
        """Limpeza após cada teste."""
        with self.app.app_context():
            self.db.drop_all()
    
    def test_fluxo_completo_apuracao(self):
        """Testa o fluxo completo de criação de apuração."""
        # 1. Criar cliente
        cliente_data = {'nome': 'Teste', 'cpf': '123.456.789-00'}
        response = self.client.post('/api/clientes', json=cliente_data)
        self.assertEqual(response.status_code, 200)
        
        # 2. Criar produto
        produto_data = {'nome': 'Produto Teste', 'preco_venda': 100.0}
        response = self.client.post('/api/produtos', json=produto_data)
        self.assertEqual(response.status_code, 200)
        
        # 3. Criar pedido
        pedido_data = {
            'cliente_id': 1,
            'itens': [{'produto_id': 1, 'quantidade': 2, 'preco_unitario': 100.0}]
        }
        response = self.client.post('/api/pedidos', json=pedido_data)
        self.assertEqual(response.status_code, 200)
        
        # 4. Registrar pagamento
        pagamento_data = {'valor': 200.0, 'forma': 'pix'}
        response = self.client.post('/api/pedidos/1/pagamento', json=pagamento_data)
        self.assertEqual(response.status_code, 200)
        
        # 5. Calcular dados para apuração
        response = self.client.post('/api/apuracao/calcular', json={'mes': 8, 'ano': 2025})
        self.assertEqual(response.status_code, 200)
        dados_calculados = response.get_json()['data']
        
        # 6. Criar apuração
        apuracao_data = {
            'mes': 8,
            'ano': 2025,
            'receita_total': dados_calculados['receita_total'],
            'custo_produtos': dados_calculados['custo_produtos']
        }
        response = self.client.post('/api/apuracao', json=apuracao_data)
        self.assertEqual(response.status_code, 200)
```

### **3. Cobertura de Testes**
```bash
# Instalar pytest-cov
pip install pytest-cov

# Executar testes com cobertura
pytest --cov=meu_app --cov-report=html

# Verificar cobertura mínima
pytest --cov=meu_app --cov-fail-under=80
```

---

## 🔍 **DEBUGGING E LOGGING**

### **1. Sistema de Logs Estruturado**
```python
import logging
import json
from datetime import datetime
from typing import Any, Dict

class ApuracaoLogger:
    def __init__(self, logger_name: str = 'apuracao'):
        self.logger = logging.getLogger(logger_name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Configura o logger com formato estruturado."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, **kwargs):
        """Log de informação com contexto estruturado."""
        log_data = {
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'INFO',
            **kwargs
        }
        self.logger.info(json.dumps(log_data))
    
    def error(self, message: str, error: Exception, **kwargs):
        """Log de erro com contexto estruturado."""
        log_data = {
            'message': message,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.utcnow().isoformat(),
            'level': 'ERROR',
            **kwargs
        }
        self.logger.error(json.dumps(log_data))
    
    def debug(self, message: str, **kwargs):
        """Log de debug com contexto estruturado."""
        if self.logger.isEnabledFor(logging.DEBUG):
            log_data = {
                'message': message,
                'timestamp': datetime.utcnow().isoformat(),
                'level': 'DEBUG',
                **kwargs
            }
            self.logger.debug(json.dumps(log_data))
```

### **2. Debugging Interativo**
```python
import pdb
import logging

class ApuracaoService:
    def criar_apuracao(self, dados: Dict[str, Any]) -> Apuracao:
        try:
            # Log de entrada
            self.logger.debug("Iniciando criação de apuração", dados=dados)
            
            # Validação
            self.validator.validar_dados_apuracao(dados)
            
            # Debug point (remover em produção)
            if self.app.debug:
                pdb.set_trace()
            
            # Cálculos
            dados_calculados = self.calculator.calcular_dados_periodo(
                mes=dados['mes'],
                ano=dados['ano']
            )
            
            # Log de dados calculados
            self.logger.debug("Dados calculados", dados_calculados=dados_calculados)
            
            # Criação
            apuracao = Apuracao(**dados_calculados)
            resultado = self.repository.create(apuracao)
            
            # Log de sucesso
            self.logger.info("Apuração criada com sucesso", apuracao_id=resultado.id)
            
            return resultado
            
        except Exception as e:
            # Log de erro com contexto completo
            self.logger.error(
                "Erro ao criar apuração",
                error=e,
                dados=dados,
                traceback=self._get_traceback()
            )
            raise
```

### **3. Monitoramento de Performance**
```python
import time
import functools
from typing import Callable, Any

def measure_performance(func: Callable) -> Callable:
    """Decorator para medir performance de funções."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = get_memory_usage()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            end_memory = get_memory_usage()
            
            duration = end_time - start_time
            memory_diff = end_memory - start_memory
            
            print(f"⏱️ {func.__name__}: {duration:.4f}s, "
                  f"💾 Memória: {memory_diff:+d} bytes")
    
    return wrapper

class PerformanceMonitor:
    def __init__(self, logger):
        self.logger = logger
        self.operations = {}
    
    def measure_operation(self, operation_name: str):
        """Context manager para medir operações."""
        start_time = time.time()
        start_memory = get_memory_usage()
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            memory_diff = get_memory_usage() - start_memory
            
            self.operations[operation_name] = {
                'duration': duration,
                'memory_usage': memory_diff,
                'timestamp': datetime.utcnow()
            }
            
            self.logger.info(
                f"Operação {operation_name} concluída",
                duration=f"{duration:.4f}s",
                memory_usage=f"{memory_diff:+d} bytes"
            )
```

---

## 🚀 **DEPLOYMENT E PRODUÇÃO**

### **1. Configurações por Ambiente**
```python
import os
from typing import Dict, Any

class Config:
    """Configuração base."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = 'simple'
    LOG_LEVEL = 'INFO'
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    LOG_LEVEL = 'DEBUG'
    CACHE_TYPE = 'simple'

class TestingConfig(Config):
    """Configuração para testes."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Configuração para produção."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    LOG_LEVEL = 'WARNING'
    CACHE_TYPE = 'redis'
    
    @classmethod
    def init_app(cls, app):
        # Configurações específicas de produção
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            # Log para arquivo
            file_handler = RotatingFileHandler(
                'logs/sap.log', maxBytes=10240000, backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('SAP startup')

# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

### **2. Scripts de Deployment**
```bash
#!/bin/bash
# deploy.sh

echo "🚀 Iniciando deployment..."

# 1. Backup do banco atual
echo "📦 Fazendo backup do banco..."
cp instance/sistema.db instance/sistema_backup_$(date +%Y-%m-%d_%H-%M-%S).db

# 2. Atualizar código
echo "📥 Atualizando código..."
git pull origin main

# 3. Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# 4. Executar migrações
echo "🗄️ Executando migrações..."
python3 migrate_estoque.py

# 5. Reiniciar aplicação
echo "🔄 Reiniciando aplicação..."
pkill -f "python3 run.py"
sleep 2
python3 run.py &

echo "✅ Deployment concluído!"
```

### **3. Monitoramento em Produção**
```python
# health_check.py
from flask import Flask, jsonify
import psutil
import sqlite3
from datetime import datetime

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Endpoint para verificação de saúde do sistema."""
    try:
        # Verificar uso de memória
        memory = psutil.virtual_memory()
        
        # Verificar uso de disco
        disk = psutil.disk_usage('/')
        
        # Verificar banco de dados
        db_status = check_database()
        
        # Verificar conectividade
        connectivity = check_connectivity()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'system': {
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'cpu_percent': psutil.cpu_percent(interval=1)
            },
            'database': db_status,
            'connectivity': connectivity
        })
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def check_database():
    """Verifica status do banco de dados."""
    try:
        conn = sqlite3.connect('instance/sistema.db')
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        conn.close()
        return {'status': 'connected', 'tables': get_table_count()}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def check_connectivity():
    """Verifica conectividade com serviços externos."""
    # Implementar verificações específicas
    return {'status': 'ok'}
```

---

## 📚 **RECURSOS E REFERÊNCIAS**

### **1. Documentação Oficial**
- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Python**: https://docs.python.org/3/

### **2. Padrões e Boas Práticas**
- **Clean Code**: Robert C. Martin
- **Design Patterns**: Gang of Four
- **SOLID Principles**: Robert C. Martin

### **3. Ferramentas de Desenvolvimento**
- **VS Code**: Editor recomendado
- **Postman**: Teste de APIs
- **SQLite Browser**: Visualização do banco
- **Git**: Controle de versão

### **4. Bibliotecas Python Úteis**
```bash
# Desenvolvimento
pip install black          # Formatação de código
pip install flake8         # Linting
pip install mypy           # Verificação de tipos
pip install pre-commit     # Hooks de pré-commit

# Testes
pip install pytest         # Framework de testes
pip install pytest-cov     # Cobertura de testes
pip install pytest-mock    # Mocking para testes

# Debugging
pip install ipdb           # Debugger interativo
pip install memory-profiler # Profiler de memória
```

---

## 🎯 **PRÓXIMOS PASSOS PARA DESENVOLVEDORES**

### **Curto Prazo (1-2 semanas)**
1. **Familiarizar-se** com a arquitetura existente
2. **Executar testes** para entender funcionalidades
3. **Revisar código** para identificar melhorias
4. **Implementar** funcionalidades menores

### **Médio Prazo (1-2 meses)**
1. **Refatorar** código legado
2. **Implementar** novos módulos
3. **Melhorar** cobertura de testes
4. **Otimizar** performance

### **Longo Prazo (3+ meses)**
1. **Migrar** para PostgreSQL
2. **Implementar** cache Redis
3. **Adicionar** autenticação JWT
4. **Criar** APIs RESTful completas

---

## 📞 **SUPORTE E COMUNIDADE**

### **Canais de Suporte**
- **Email**: dev@sistema.com
- **Slack**: #sap-dev
- **GitHub Issues**: Sistema de tickets
- **Documentação**: docs/ (pasta do projeto)

### **Code Review**
- **Pull Requests**: Sempre criar PRs para mudanças
- **Code Review**: Mínimo 2 aprovações
- **Testes**: 100% de cobertura para novas funcionalidades
- **Documentação**: Atualizar docs/ conforme necessário

---

**© 2025 Sistema de Apuração Financeira - Guia do Desenvolvedor**
