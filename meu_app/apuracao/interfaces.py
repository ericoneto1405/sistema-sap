"""
Interfaces para o módulo de apuração financeira.

Este módulo define as interfaces (contratos) que devem ser implementadas
pelos serviços de apuração, garantindo consistência e testabilidade.

**Padrões Implementados:**
- Interface Segregation Principle (ISP)
- Dependency Inversion Principle (DIP)
- Strategy Pattern para diferentes implementações
- Factory Pattern para criação de serviços

**Interfaces Definidas:**
- IApuracaoService: Contrato principal do serviço
- IApuracaoRepository: Contrato para acesso a dados
- IApuracaoValidator: Contrato para validações
- IApuracaoCache: Contrato para sistema de cache
- IApuracaoLogger: Contrato para sistema de logs

**Benefícios:**
- Melhor testabilidade com mocks
- Facilita injeção de dependência
- Permite múltiplas implementações
- Código mais modular e extensível

**Exemplo de Uso:**
    >>> from meu_app.apuracao.interfaces import IApuracaoService
    >>> from meu_app.apuracao.services import ApuracaoService
    >>> 
    >>> # Verificar se implementa a interface
    >>> isinstance(ApuracaoService(), IApuracaoService)
    True
    
    >>> # Usar com injeção de dependência
    >>> service: IApuracaoService = ApuracaoService()
    >>> dados = service.calcular_dados_periodo(8, 2025)

**Autor:** Sistema de Apuração Financeira
**Versão:** 1.0.0
**Data:** 2025-08-13
**Licença:** Proprietária
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

# ✅ FASE 4.1 - Interface principal do serviço de apuração
class IApuracaoService(ABC):
    """
    Interface principal para o serviço de apuração financeira.
    
    Esta interface define todos os métodos que devem ser implementados
    pelo serviço de apuração, garantindo consistência e testabilidade.
    
    **Responsabilidades:**
    - Cálculo de dados financeiros por período
    - CRUD de apurações
    - Validação de dados de entrada
    - Gestão de cache
    - Tratamento de erros
    - Logs de operações
    
    **Implementações Esperadas:**
    - ApuracaoService: Implementação padrão
    - ApuracaoServiceMock: Para testes
    - ApuracaoServiceLegacy: Para compatibilidade
    
    **Exemplo de Implementação:**
        class ApuracaoService(IApuracaoService):
            def calcular_dados_periodo(self, mes: int, ano: int) -> Dict:
                # Implementação específica
                pass
    """
    
    @abstractmethod
    def calcular_dados_periodo(self, mes: int, ano: int) -> Dict[str, Any]:
        """
        Calcula dados financeiros do período para apuração.
        
        Args:
            mes (int): Mês do período (1-12)
            ano (int): Ano do período (1900-2100)
            
        Returns:
            Dict[str, Any]: Dicionário com dados calculados:
                - receita_calculada (float): Receita bruta do período
                - cpv_calculado (float): Custo dos produtos vendidos
                - pedidos_periodo (int): Total de pedidos no período
                
        Raises:
            ApuracaoValidationError: Se período for inválido
            ApuracaoDatabaseError: Se houver erro de banco
        """
        pass
    
    @abstractmethod
    def criar_apuracao(self, mes: int, ano: int, dados: Dict[str, Any]) -> Tuple[bool, str, Optional[Any]]:
        """
        Cria uma nova apuração para o período especificado.
        
        Args:
            mes (int): Mês da apuração (1-12)
            ano (int): Ano da apuração (1900-2100)
            dados (Dict[str, Any]): Dados da apuração
            
        Returns:
            Tuple[bool, str, Optional[Any]]: 
                - sucesso (bool): True se criada com sucesso
                - mensagem (str): Mensagem descritiva do resultado
                - apuracao (Optional[Any]): Apuração criada ou None
        """
        pass
    
    @abstractmethod
    def tornar_definitiva(self, apuracao_id: int) -> Tuple[bool, str]:
        """
        Torna uma apuração definitiva.
        
        Args:
            apuracao_id (int): ID da apuração
            
        Returns:
            Tuple[bool, str]: 
                - sucesso (bool): True se tornada definitiva
                - mensagem (str): Mensagem descritiva do resultado
        """
        pass
    
    @abstractmethod
    def excluir_apuracao(self, apuracao_id: int) -> Tuple[bool, str]:
        """
        Exclui uma apuração do sistema.
        
        Args:
            apuracao_id (int): ID da apuração
            
        Returns:
            Tuple[bool, str]: 
                - sucesso (bool): True se excluída com sucesso
                - mensagem (str): Mensagem descritiva do resultado
        """
        pass
    
    @abstractmethod
    def buscar_apuracao(self, apuracao_id: int) -> Optional[Any]:
        """
        Busca uma apuração específica por ID.
        
        Args:
            apuracao_id (int): ID da apuração
            
        Returns:
            Optional[Any]: Apuração encontrada ou None
        """
        pass
    
    @abstractmethod
    def listar_apuracoes(self, mes: Optional[int] = None, ano: Optional[int] = None) -> List[Any]:
        """
        Lista apurações com filtros opcionais.
        
        Args:
            mes (Optional[int]): Mês para filtrar (1-12)
            ano (Optional[int]): Ano para filtrar (1900-2100)
            
        Returns:
            List[Any]: Lista de apurações
        """
        pass
    
    @abstractmethod
    def calcular_estatisticas_gerais(self) -> Dict[str, Any]:
        """
        Calcula estatísticas gerais de todas as apurações.
        
        Returns:
            Dict[str, Any]: Dicionário com estatísticas calculadas
        """
        pass

# ✅ FASE 4.2 - Interface para repositório de dados
class IApuracaoRepository(ABC):
    """
    Interface para repositório de dados de apuração.
    
    Esta interface define os métodos de acesso a dados,
    permitindo diferentes implementações (SQLAlchemy, Mock, etc.).
    
    **Responsabilidades:**
    - CRUD de apurações no banco de dados
    - Queries otimizadas
    - Transações e rollback
    - Cache de dados
    
    **Implementações Esperadas:**
    - ApuracaoRepository: Implementação SQLAlchemy
    - ApuracaoRepositoryMock: Para testes
    - ApuracaoRepositoryLegacy: Para compatibilidade
    """
    
    @abstractmethod
    def buscar_por_id(self, apuracao_id: int) -> Optional[Any]:
        """Busca apuração por ID"""
        pass
    
    @abstractmethod
    def buscar_por_periodo(self, mes: int, ano: int) -> Optional[Any]:
        """Busca apuração por período"""
        pass
    
    @abstractmethod
    def listar_todas(self) -> List[Any]:
        """Lista todas as apurações"""
        pass
    
    @abstractmethod
    def listar_por_filtros(self, mes: Optional[int] = None, ano: Optional[int] = None) -> List[Any]:
        """Lista apurações com filtros"""
        pass
    
    @abstractmethod
    def criar(self, dados: Dict[str, Any]) -> Any:
        """Cria nova apuração"""
        pass
    
    @abstractmethod
    def atualizar(self, apuracao_id: int, dados: Dict[str, Any]) -> bool:
        """Atualiza apuração existente"""
        pass
    
    @abstractmethod
    def excluir(self, apuracao_id: int) -> bool:
        """Exclui apuração"""
        pass
    
    @abstractmethod
    def buscar_pedidos_periodo(self, mes: int, ano: int) -> List[Any]:
        """Busca pedidos de um período"""
        pass
    
    @abstractmethod
    def calcular_estatisticas(self) -> Dict[str, Any]:
        """Calcula estatísticas agregadas"""
        pass

# ✅ FASE 4.3 - Interface para validações
class IApuracaoValidator(ABC):
    """
    Interface para validações de apuração.
    
    Esta interface define os métodos de validação,
    permitindo diferentes estratégias de validação.
    
    **Responsabilidades:**
    - Validação de período (mês/ano)
    - Validação de dados financeiros
    - Validação de IDs
    - Validação de regras de negócio
    
    **Implementações Esperadas:**
    - ApuracaoValidator: Implementação padrão
    - ApuracaoValidatorMock: Para testes
    - ApuracaoValidatorLegacy: Para compatibilidade
    """
    
    @abstractmethod
    def validar_periodo(self, mes: int, ano: int) -> None:
        """Valida período (mês/ano)"""
        pass
    
    @abstractmethod
    def validar_dados_apuracao(self, dados: Dict[str, Any]) -> None:
        """Valida dados da apuração"""
        pass
    
    @abstractmethod
    def validar_id_apuracao(self, apuracao_id: int) -> None:
        """Valida ID da apuração"""
        pass
    
    @abstractmethod
    def validar_regras_negocio(self, apuracao: Any, operacao: str) -> None:
        """Valida regras de negócio"""
        pass

# ✅ FASE 4.4 - Interface para sistema de cache
class IApuracaoCache(ABC):
    """
    Interface para sistema de cache de apuração.
    
    Esta interface define os métodos de cache,
    permitindo diferentes implementações (memória, Redis, etc.).
    
    **Responsabilidades:**
    - Armazenamento de dados em cache
    - Controle de TTL (Time To Live)
    - Limpeza automática
    - Invalidação seletiva
    
    **Implementações Esperadas:**
    - ApuracaoCache: Implementação em memória
    - ApuracaoCacheRedis: Implementação Redis
    - ApuracaoCacheMock: Para testes
    """
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Recupera valor do cache"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Armazena valor no cache"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Limpa todo o cache"""
        pass
    
    @abstractmethod
    def is_valid(self, key: str) -> bool:
        """Verifica se cache ainda é válido"""
        pass
    
    @abstractmethod
    def get_ttl(self, key: str) -> Optional[int]:
        """Retorna TTL restante de uma chave"""
        pass

# ✅ FASE 4.5 - Interface para sistema de logs
class IApuracaoLogger(ABC):
    """
    Interface para sistema de logs de apuração.
    
    Esta interface define os métodos de logging,
    permitindo diferentes implementações (Flask, Python, etc.).
    
    **Responsabilidades:**
    - Logs de operações
    - Logs de erros
    - Logs de auditoria
    - Logs de performance
    
    **Implementações Esperadas:**
    - ApuracaoLogger: Implementação Flask
    - ApuracaoLoggerMock: Para testes
    - ApuracaoLoggerFile: Implementação em arquivo
    """
    
    @abstractmethod
    def info(self, message: str, **kwargs) -> None:
        """Log de informação"""
        pass
    
    @abstractmethod
    def warning(self, message: str, **kwargs) -> None:
        """Log de aviso"""
        pass
    
    @abstractmethod
    def error(self, message: str, **kwargs) -> None:
        """Log de erro"""
        pass
    
    @abstractmethod
    def debug(self, message: str, **kwargs) -> None:
        """Log de debug"""
        pass
    
    @abstractmethod
    def log_operacao(self, operacao: str, dados: Dict[str, Any]) -> None:
        """Log de operação específica"""
        pass
    
    @abstractmethod
    def log_erro(self, erro: Exception, contexto: Dict[str, Any]) -> None:
        """Log de erro com contexto"""
        pass

# ✅ FASE 4.6 - Interface para cálculo financeiro
class IApuracaoCalculator(ABC):
    """
    Interface para cálculos financeiros de apuração.
    
    Esta interface define os métodos de cálculo,
    permitindo diferentes algoritmos e estratégias.
    
    **Responsabilidades:**
    - Cálculo de receita
    - Cálculo de CPV
    - Cálculo de margem
    - Cálculo de estatísticas
    
    **Implementações Esperadas:**
    - ApuracaoCalculator: Implementação padrão
    - ApuracaoCalculatorMock: Para testes
    - ApuracaoCalculatorLegacy: Para compatibilidade
    """
    
    @abstractmethod
    def calcular_receita_periodo(self, pedidos: List[Any]) -> float:
        """Calcula receita de um período"""
        pass
    
    @abstractmethod
    def calcular_cpv_periodo(self, pedidos: List[Any]) -> float:
        """Calcula CPV de um período"""
        pass
    
    @abstractmethod
    def calcular_margem(self, receita: float, cpv: float) -> float:
        """Calcula margem bruta"""
        pass
    
    @abstractmethod
    def calcular_percentual_margem(self, receita: float, margem: float) -> float:
        """Calcula percentual de margem"""
        pass
    
    @abstractmethod
    def calcular_estatisticas_agregadas(self, apuracoes: List[Any]) -> Dict[str, Any]:
        """Calcula estatísticas agregadas"""
        pass

# ✅ FASE 4.7 - Interface para transações
class IApuracaoTransaction(ABC):
    """
    Interface para gerenciamento de transações.
    
    Esta interface define os métodos de transação,
    permitindo diferentes estratégias de commit/rollback.
    
    **Responsabilidades:**
    - Início de transação
    - Commit de transação
    - Rollback de transação
    - Verificação de status
    
    **Implementações Esperadas:**
    - ApuracaoTransaction: Implementação SQLAlchemy
    - ApuracaoTransactionMock: Para testes
    - ApuracaoTransactionLegacy: Para compatibilidade
    """
    
    @abstractmethod
    def begin(self) -> None:
        """Inicia transação"""
        pass
    
    @abstractmethod
    def commit(self) -> None:
        """Confirma transação"""
        pass
    
    @abstractmethod
    def rollback(self) -> None:
        """Desfaz transação"""
        pass
    
    @abstractmethod
    def is_active(self) -> bool:
        """Verifica se transação está ativa"""
        pass
    
    @abstractmethod
    def execute_with_rollback(self, operacao: str, callback, *args, **kwargs) -> Any:
        """Executa operação com rollback automático"""
        pass
