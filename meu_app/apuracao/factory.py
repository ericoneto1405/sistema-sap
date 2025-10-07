"""
Factory Pattern para criação de serviços de apuração financeira.

Este módulo implementa o padrão Factory para criar instâncias
de serviços e suas dependências, facilitando injeção de dependência
e configuração de diferentes implementações.

**Padrões Implementados:**
- Factory Pattern
- Dependency Injection
- Configuration Management
- Service Locator (opcional)

**Funcionalidades:**
- Criação de serviços com dependências injetadas
- Configuração de implementações (produção, teste, mock)
- Gerenciamento de ciclo de vida dos serviços
- Configuração centralizada

**Exemplo de Uso:**
    >>> from meu_app.apuracao.factory import ApuracaoServiceFactory
    >>> 
    >>> # Criar serviço padrão
    >>> factory = ApuracaoServiceFactory()
    >>> service = factory.create_service()
    >>> 
    >>> # Criar serviço para testes
    >>> factory = ApuracaoServiceFactory(environment='test')
    >>> service = factory.create_service()
    >>> 
    >>> # Criar serviço com configuração customizada
    >>> factory = ApuracaoServiceFactory()
    >>> factory.configure_repository('mock')
    >>> service = factory.create_service()

**Autor:** Sistema de Apuração Financeira
**Versão:** 1.0.0
**Data:** 2025-08-13
**Licença:** Proprietária
"""

from typing import Dict, Any, Optional, Type, List
from enum import Enum

from .interfaces import (
    IApuracaoService, 
    IApuracaoRepository, 
    IApuracaoValidator,
    IApuracaoCache,
    IApuracaoLogger,
    IApuracaoCalculator,
    IApuracaoTransaction
)
from .repositories import ApuracaoRepository, ApuracaoRepositoryMock
from .validators import ApuracaoValidator
from .cache import ApuracaoCache
from .logger import ApuracaoLogger
from .calculator import ApuracaoCalculator
from .transaction import ApuracaoTransaction
from .services import ApuracaoService

# ✅ FASE 4.10 - Enum para tipos de ambiente
class Environment(Enum):
    """Tipos de ambiente disponíveis"""
    PRODUCTION = "production"
    TEST = "test"
    DEVELOPMENT = "development"
    MOCK = "mock"

# ✅ FASE 4.11 - Enum para tipos de implementação
class ImplementationType(Enum):
    """Tipos de implementação disponíveis"""
    DEFAULT = "default"
    MOCK = "mock"
    LEGACY = "legacy"
    CUSTOM = "custom"

# ✅ FASE 4.12 - Configuração padrão dos serviços
class ServiceConfig:
    """
    Configuração para criação de serviços.
    
    Esta classe centraliza as configurações de criação
    de serviços, permitindo fácil customização.
    """
    
    def __init__(self, environment: Environment = Environment.PRODUCTION):
        """
        Inicializa configuração de serviço.
        
        Args:
            environment (Environment): Ambiente de execução
        """
        self.environment = environment
        self._configs = self._get_default_configs()
    
    def _get_default_configs(self) -> Dict[str, Any]:
        """Retorna configurações padrão baseadas no ambiente"""
        configs = {
            Environment.PRODUCTION: {
                'repository': 'default',
                'validator': 'default',
                'cache': 'default',
                'logger': 'default',
                'calculator': 'default',
                'transaction': 'default'
            },
            Environment.TEST: {
                'repository': 'mock',
                'validator': 'default',
                'cache': 'mock',
                'logger': 'mock',
                'calculator': 'default',
                'transaction': 'mock'
            },
            Environment.DEVELOPMENT: {
                'repository': 'default',
                'validator': 'default',
                'cache': 'default',
                'logger': 'default',
                'calculator': 'default',
                'transaction': 'default'
            },
            Environment.MOCK: {
                'repository': 'mock',
                'validator': 'mock',
                'cache': 'mock',
                'logger': 'mock',
                'calculator': 'mock',
                'transaction': 'mock'
            }
        }
        return configs.get(self.environment, configs[Environment.PRODUCTION])
    
    def get_config(self, service_type: str) -> str:
        """
        Obtém configuração para um tipo de serviço.
        
        Args:
            service_type (str): Tipo de serviço
            
        Returns:
            str: Tipo de implementação configurado
        """
        return self._configs.get(service_type, 'default')
    
    def set_config(self, service_type: str, implementation: str) -> None:
        """
        Define configuração para um tipo de serviço.
        
        Args:
            service_type (str): Tipo de serviço
            implementation (str): Tipo de implementação
        """
        self._configs[service_type] = implementation

# ✅ FASE 4.13 - Factory principal para serviços
class ApuracaoServiceFactory:
    """
    Factory para criação de serviços de apuração.
    
    Esta classe centraliza a criação de todos os serviços
    e suas dependências, implementando injeção de dependência.
    
    **Responsabilidades:**
    - Criação de serviços com dependências injetadas
    - Configuração de implementações
    - Gerenciamento de ciclo de vida
    - Configuração centralizada
    
    **Exemplo de Uso:**
        >>> factory = ApuracaoServiceFactory()
        >>> service = factory.create_service()
        >>> 
        >>> # Para testes
        >>> factory = ApuracaoServiceFactory(Environment.TEST)
        >>> service = factory.create_service()
    """
    
    def __init__(self, environment: Environment = Environment.PRODUCTION):
        """
        Inicializa factory de serviços.
        
        Args:
            environment (Environment): Ambiente de execução
        """
        self.config = ServiceConfig(environment)
        self._service_cache = {}
    
    def create_service(self) -> IApuracaoService:
        """
        Cria instância do serviço principal com dependências injetadas.
        
        Returns:
            IApuracaoService: Serviço configurado
            
        Note:
            - Dependências são criadas automaticamente
            - Cache de instâncias para reutilização
            - Configuração baseada no ambiente
        """
        # Verificar cache
        cache_key = f"service_{self.config.environment.value}"
        if cache_key in self._service_cache:
            return self._service_cache[cache_key]
        
        # Criar dependências
        repository = self._create_repository()
        validator = self._create_validator()
        cache = self._create_cache()
        logger = self._create_logger()
        calculator = self._create_calculator()
        transaction = self._create_transaction()
        
        # Criar serviço principal
        service = ApuracaoService(
            repository=repository,
            validator=validator,
            cache=cache,
            logger=logger,
            calculator=calculator,
            transaction=transaction
        )
        
        # Armazenar no cache
        self._service_cache[cache_key] = service
        
        return service
    
    def _create_repository(self) -> IApuracaoRepository:
        """Cria instância do repositório"""
        repo_type = self.config.get_config('repository')
        
        if repo_type == 'mock':
            return ApuracaoRepositoryMock()
        elif repo_type == 'legacy':
            # Implementação legacy (futura)
            return ApuracaoRepository()
        else:
            return ApuracaoRepository()
    
    def _create_validator(self) -> IApuracaoValidator:
        """Cria instância do validador"""
        validator_type = self.config.get_config('validator')
        
        if validator_type == 'mock':
            # Implementação mock (futura)
            return ApuracaoValidator()
        else:
            return ApuracaoValidator()
    
    def _create_cache(self) -> IApuracaoCache:
        """Cria instância do cache"""
        cache_type = self.config.get_config('cache')
        
        if cache_type == 'mock':
            # Implementação mock (futura)
            return ApuracaoCache()
        else:
            return ApuracaoCache()
    
    def _create_logger(self) -> IApuracaoLogger:
        """Cria instância do logger"""
        logger_type = self.config.get_config('logger')
        
        if logger_type == 'mock':
            # Implementação mock (futura)
            return ApuracaoLogger()
        else:
            return ApuracaoLogger()
    
    def _create_calculator(self) -> IApuracaoCalculator:
        """Cria instância do calculador"""
        calculator_type = self.config.get_config('calculator')
        
        if calculator_type == 'mock':
            # Implementação mock (futura)
            return ApuracaoCalculator()
        else:
            return ApuracaoCalculator()
    
    def _create_transaction(self) -> IApuracaoTransaction:
        """Cria instância do gerenciador de transações"""
        transaction_type = self.config.get_config('transaction')
        
        if transaction_type == 'mock':
            # Implementação mock (futura)
            return ApuracaoTransaction()
        else:
            return ApuracaoTransaction()
    
    def configure_repository(self, implementation: str) -> None:
        """
        Configura tipo de implementação do repositório.
        
        Args:
            implementation (str): Tipo de implementação
        """
        self.config.set_config('repository', implementation)
    
    def configure_validator(self, implementation: str) -> None:
        """
        Configura tipo de implementação do validador.
        
        Args:
            implementation (str): Tipo de implementação
        """
        self.config.set_config('validator', implementation)
    
    def configure_cache(self, implementation: str) -> None:
        """
        Configura tipo de implementação do cache.
        
        Args:
            implementation (str): Tipo de implementação
        """
        self.config.set_config('cache', implementation)
    
    def clear_cache(self) -> None:
        """Limpa cache de serviços"""
        self._service_cache.clear()
    
    def get_available_implementations(self) -> Dict[str, List[str]]:
        """
        Retorna implementações disponíveis para cada tipo de serviço.
        
        Returns:
            Dict[str, List[str]]: Mapeamento de tipos para implementações
        """
        return {
            'repository': ['default', 'mock', 'legacy'],
            'validator': ['default', 'mock'],
            'cache': ['default', 'mock', 'redis'],
            'logger': ['default', 'mock', 'file'],
            'calculator': ['default', 'mock'],
            'transaction': ['default', 'mock']
        }

# ✅ FASE 4.14 - Factory simplificado para uso rápido
class SimpleApuracaoFactory:
    """
    Factory simplificado para criação rápida de serviços.
    
    Esta classe fornece métodos estáticos para criação
    rápida de serviços comuns.
    """
    
    @staticmethod
    def create_production_service() -> IApuracaoService:
        """Cria serviço para produção"""
        factory = ApuracaoServiceFactory(Environment.PRODUCTION)
        return factory.create_service()
    
    @staticmethod
    def create_test_service() -> IApuracaoService:
        """Cria serviço para testes"""
        factory = ApuracaoServiceFactory(Environment.TEST)
        return factory.create_service()
    
    @staticmethod
    def create_mock_service() -> IApuracaoService:
        """Cria serviço com implementações mock"""
        factory = ApuracaoServiceFactory(Environment.MOCK)
        return factory.create_service()
    
    @staticmethod
    def create_custom_service(**configs) -> IApuracaoService:
        """
        Cria serviço com configuração customizada.
        
        Args:
            **configs: Configurações customizadas
            
        Returns:
            IApuracaoService: Serviço configurado
        """
        factory = ApuracaoServiceFactory()
        
        for service_type, implementation in configs.items():
            if hasattr(factory, f'configure_{service_type}'):
                getattr(factory, f'configure_{service_type}')(implementation)
        
        return factory.create_service()

# ✅ FASE 4.15 - Função de conveniência para criação rápida
def create_apuracao_service(environment: str = 'production', **configs) -> IApuracaoService:
    """
    Função de conveniência para criação rápida de serviços.
    
    Args:
        environment (str): Ambiente de execução
        **configs: Configurações customizadas
        
    Returns:
        IApuracaoService: Serviço configurado
        
    Example:
        >>> # Serviço padrão para produção
        >>> service = create_apuracao_service()
        >>> 
        >>> # Serviço para testes
        >>> service = create_apuracao_service('test')
        >>> 
        >>> # Serviço customizado
        >>> service = create_apuracao_service(
        ...     environment='production',
        ...     repository='mock',
        ...     cache='redis'
        ... )
    """
    try:
        env = Environment(environment.lower())
    except ValueError:
        env = Environment.PRODUCTION
    
    factory = ApuracaoServiceFactory(env)
    
    # Aplicar configurações customizadas
    for service_type, implementation in configs.items():
        if hasattr(factory, f'configure_{service_type}'):
            getattr(factory, f'configure_{service_type}')(implementation)
    
    return factory.create_service()

# ✅ FASE 4.16 - Configuração global de serviços
class GlobalServiceRegistry:
    """
    Registro global de serviços para uso em toda a aplicação.
    
    Esta classe mantém instâncias globais de serviços,
    permitindo acesso centralizado e configuração global.
    """
    
    _instance = None
    _services = {}
    _factory = None
    
    def __new__(cls):
        """Implementa Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa registro global"""
        if not hasattr(self, '_initialized'):
            self._factory = ApuracaoServiceFactory()
            self._initialized = True
    
    def get_service(self, service_name: str = 'default') -> IApuracaoService:
        """
        Obtém serviço do registro global.
        
        Args:
            service_name (str): Nome do serviço
            
        Returns:
            IApuracaoService: Serviço registrado
        """
        if service_name not in self._services:
            self._services[service_name] = self._factory.create_service()
        
        return self._services[service_name]
    
    def register_service(self, service_name: str, service: IApuracaoService) -> None:
        """
        Registra serviço no registro global.
        
        Args:
            service_name (str): Nome do serviço
            service (IApuracaoService): Instância do serviço
        """
        self._services[service_name] = service
    
    def clear_services(self) -> None:
        """Limpa todos os serviços registrados"""
        self._services.clear()
    
    def get_factory(self) -> ApuracaoServiceFactory:
        """Retorna factory configurado"""
        return self._factory

# Função de conveniência para acesso global
def get_global_service(service_name: str = 'default') -> IApuracaoService:
    """
    Obtém serviço do registro global.
    
    Args:
        service_name (str): Nome do serviço
        
    Returns:
        IApuracaoService: Serviço registrado
        
    Example:
        >>> # Obter serviço padrão
        >>> service = get_global_service()
        >>> 
        >>> # Obter serviço específico
        >>> service = get_global_service('test')
    """
    registry = GlobalServiceRegistry()
    return registry.get_service(service_name)
