"""
Data Source Manager - Camada de abstração para acessar dados de múltiplas fontes.
Suporta: SQL Server, Parquet, JSON, CSV, SQLite, etc.

Prioridade de acesso:
1. SQL Server (se conectado)
2. Parquet files (fallback)
3. JSON/CSV (fallback)
4. SQLite (fallback)
"""

import os
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class DataSource(ABC):
    """Interface abstrata para fontes de dados."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Tenta conectar à fonte de dados."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Verifica se está conectado."""
        pass
    
    @abstractmethod
    def query(self, query: str, params: Dict = None) -> List[Dict]:
        """Executa uma query e retorna resultados."""
        pass
    
    @abstractmethod
    def get_table(self, table_name: str, limit: int = None) -> pd.DataFrame:
        """Obtém uma tabela inteira ou parcial."""
        pass
    
    @abstractmethod
    def search(
        self,
        table_name: str,
        column: str,
        value: str,
        limit: int = 10
    ) -> pd.DataFrame:
        """Busca registros."""
        pass


class SQLServerDataSource(DataSource):
    """Acesso a dados SQL Server."""
    
    def __init__(self):
        self._connected = False
        self._manager = None
    
    def connect(self) -> bool:
        """Tenta conectar ao SQL Server."""
        try:
            from core.database.database import get_db_manager
            self._manager = get_db_manager()
            success, msg = self._manager.test_connection()
            self._connected = success
            if success:
                logger.info(f"✓ SQL Server conectado")
            else:
                logger.warning(f"✗ SQL Server: {msg}")
            return success
        except Exception as e:
            logger.warning(f"SQL Server não disponível: {e}")
            self._connected = False
            return False
    
    def is_connected(self) -> bool:
        """Verifica conexão."""
        return self._connected
    
    def query(self, query: str, params: Dict = None) -> List[Dict]:
        """Executa query SQL."""
        if not self._connected or not self._manager:
            return []
        
        try:
            from sqlalchemy import text
            with self._manager.get_connection() as conn:
                result = conn.execute(text(query), params or {})
                rows = result.fetchall()
                columns = result.keys() if rows else []
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logger.error(f"Erro ao executar query SQL: {e}")
            return []
    
    def get_table(
        self,
        table_name: str,
        limit: int = None
    ) -> pd.DataFrame:
        """Obtém tabela do SQL Server."""
        if not self._connected:
            return pd.DataFrame()
        
        try:
            limit_clause = f"TOP {limit}" if limit else ""
            query = f"SELECT {limit_clause} * FROM dbo.{table_name}"
            results = self.query(query)
            return pd.DataFrame(results) if results else pd.DataFrame()
        except Exception as e:
            logger.error(f"Erro ao obter tabela {table_name}: {e}")
            return pd.DataFrame()
    
    def search(
        self,
        table_name: str,
        column: str,
        value: str,
        limit: int = 10
    ) -> pd.DataFrame:
        """Busca registros no SQL Server."""
        if not self._connected:
            return pd.DataFrame()
        
        try:
            query = f"""
            SELECT TOP {limit} * FROM dbo.{table_name}
            WHERE {column} LIKE :search_value
            """
            results = self.query(query, {"search_value": f"%{value}%"})
            return pd.DataFrame(results) if results else pd.DataFrame()
        except Exception as e:
            logger.error(f"Erro ao buscar em {table_name}: {e}")
            return pd.DataFrame()


class ParquetDataSource(DataSource):
    """Acesso a dados em arquivos Parquet."""
    
    def __init__(self, base_dir: str = "data/parquet_cleaned"):
        self._connected = False
        self.base_dir = Path(base_dir)
        self._cache = {}
    
    def connect(self) -> bool:
        """Verifica se diretório Parquet existe."""
        if self.base_dir.exists():
            self._connected = True
            logger.info(f"✓ Parquet conectado: {self.base_dir}")
            return True
        
        logger.warning(f"Diretório Parquet não encontrado: {self.base_dir}")
        self._connected = False
        return False
    
    def is_connected(self) -> bool:
        """Verifica conexão."""
        return self._connected and self.base_dir.exists()
    
    def query(self, query: str, params: Dict = None) -> List[Dict]:
        """Não suporta SQL direto em Parquet."""
        logger.warning("Parquet não suporta SQL direto")
        return []
    
    def get_table(
        self,
        table_name: str,
        limit: int = None
    ) -> pd.DataFrame:
        """Obtém tabela Parquet."""
        if not self._connected:
            return pd.DataFrame()
        
        try:
            # Tentar variações do nome
            possible_names = [
                f"{table_name}.parquet",
                f"{table_name}.parquet.gzip",
                f"{table_name}_cleaned.parquet",
            ]
            
            for filename in possible_names:
                filepath = self.base_dir / filename
                if filepath.exists():
                    df = pd.read_parquet(filepath)
                    if limit:
                        df = df.head(limit)
                    logger.info(f"✓ Lido: {filename}")
                    return df
            
            logger.warning(
                f"Arquivo Parquet não encontrado: {table_name}"
            )
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Erro ao ler Parquet {table_name}: {e}")
            return pd.DataFrame()
    
    def search(
        self,
        table_name: str,
        column: str,
        value: str,
        limit: int = 10
    ) -> pd.DataFrame:
        """Busca em arquivo Parquet."""
        try:
            df = self.get_table(table_name)
            if df.empty or column not in df.columns:
                return pd.DataFrame()
            
            # Busca case-insensitive
            mask = df[column].astype(str).str.contains(
                value,
                case=False,
                na=False
            )
            result = df[mask].head(limit)
            return result
            
        except Exception as e:
            logger.error(f"Erro ao buscar em Parquet: {e}")
            return pd.DataFrame()


class JSONDataSource(DataSource):
    """Acesso a dados em arquivos JSON."""
    
    def __init__(self, base_dir: str = "data"):
        self._connected = False
        self.base_dir = Path(base_dir)
    
    def connect(self) -> bool:
        """Verifica se diretório JSON existe."""
        if self.base_dir.exists():
            self._connected = True
            logger.info(f"✓ JSON conectado: {self.base_dir}")
            return True
        
        logger.warning(f"Diretório JSON não encontrado: {self.base_dir}")
        self._connected = False
        return False
    
    def is_connected(self) -> bool:
        """Verifica conexão."""
        return self._connected and self.base_dir.exists()
    
    def query(self, query: str, params: Dict = None) -> List[Dict]:
        """Não suporta SQL direto em JSON."""
        return []
    
    def get_table(
        self,
        table_name: str,
        limit: int = None
    ) -> pd.DataFrame:
        """Obtém dados de JSON."""
        if not self._connected:
            return pd.DataFrame()
        
        try:
            filepath = self.base_dir / f"{table_name}.json"
            
            if not filepath.exists():
                logger.warning(f"JSON não encontrado: {filepath}")
                return pd.DataFrame()
            
            data = pd.read_json(filepath)
            if limit:
                data = data.head(limit)
            
            logger.info(f"✓ Lido: {table_name}.json")
            return data
            
        except Exception as e:
            logger.error(f"Erro ao ler JSON {table_name}: {e}")
            return pd.DataFrame()
    
    def search(
        self,
        table_name: str,
        column: str,
        value: str,
        limit: int = 10
    ) -> pd.DataFrame:
        """Busca em JSON."""
        try:
            df = self.get_table(table_name)
            if df.empty or column not in df.columns:
                return pd.DataFrame()
            
            mask = df[column].astype(str).str.contains(
                value,
                case=False,
                na=False
            )
            return df[mask].head(limit)
            
        except Exception as e:
            logger.error(f"Erro ao buscar em JSON: {e}")
            return pd.DataFrame()


class DataSourceManager:
    """
    Gerenciador centralizado de fontes de dados.
    Tenta acessar em ordem de prioridade.
    """
    
    def __init__(self):
        self.sources: Dict[str, DataSource] = {}
        self._primary_source: Optional[DataSource] = None
        self._initialize_sources()
    
    def _initialize_sources(self):
        """Inicializa todas as fontes de dados."""
        logger.info("Inicializando Data Source Manager...")
        
        # Adicionar fontes em ordem de prioridade
        self.sources['sql_server'] = SQLServerDataSource()
        self.sources['parquet'] = ParquetDataSource()
        self.sources['json'] = JSONDataSource()
        
        # Tentar conectar a cada fonte
        for name, source in self.sources.items():
            try:
                if source.connect():
                    logger.info(f"✓ {name} disponível")
                    if self._primary_source is None:
                        self._primary_source = source
                        logger.info(
                            f"✓ Fonte primária: {name}"
                        )
                else:
                    logger.info(f"⚠ {name} não disponível")
            except Exception as e:
                logger.warning(f"Erro ao conectar {name}: {e}")
    
    def get_available_sources(self) -> List[str]:
        """Retorna lista de fontes disponíveis."""
        return [
            name for name, source in self.sources.items()
            if source.is_connected()
        ]
    
    def get_data(
        self,
        table_name: str,
        limit: int = None,
        source: str = None
    ) -> pd.DataFrame:
        """
        Obtém dados de uma tabela.
        
        Args:
            table_name: Nome da tabela
            limit: Limite de registros
            source: Fonte específica (opcional)
        
        Returns:
            DataFrame com os dados
        """
        # Se fonte específica foi pedida
        if source and source in self.sources:
            return self.sources[source].get_table(table_name, limit)
        
        # Tentar na ordem de prioridade
        for src in self.sources.values():
            if src.is_connected():
                df = src.get_table(table_name, limit)
                if not df.empty:
                    return df
        
        logger.error(f"Dados não encontrados: {table_name}")
        return pd.DataFrame()
    
    def search_data(
        self,
        table_name: str,
        column: str,
        value: str,
        limit: int = 10,
        source: str = None
    ) -> pd.DataFrame:
        """
        Busca dados em uma tabela.
        
        Args:
            table_name: Nome da tabela
            column: Coluna para buscar
            value: Valor a buscar
            limit: Limite de resultados
            source: Fonte específica (opcional)
        
        Returns:
            DataFrame com resultados
        """
        # Se fonte específica foi pedida
        if source and source in self.sources:
            return self.sources[source].search(
                table_name,
                column,
                value,
                limit
            )
        
        # Tentar na ordem de prioridade
        for src in self.sources.values():
            if src.is_connected():
                df = src.search(table_name, column, value, limit)
                if not df.empty:
                    return df
        
        logger.warning(
            f"Nenhum resultado: {table_name}.{column} = {value}"
        )
        return pd.DataFrame()
    
    def execute_query(
        self,
        query: str,
        params: Dict = None
    ) -> List[Dict]:
        """
        Executa uma query SQL (apenas SQL Server).
        
        Args:
            query: Query SQL
            params: Parâmetros
        
        Returns:
            Lista de resultados
        """
        if 'sql_server' in self.sources:
            source = self.sources['sql_server']
            if source.is_connected():
                return source.query(query, params)
        
        logger.error("SQL Server não disponível para queries")
        return []
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status de todas as fontes."""
        return {
            name: {
                "connected": source.is_connected(),
                "type": source.__class__.__name__
            }
            for name, source in self.sources.items()
        }


# Instância global
_manager: Optional[DataSourceManager] = None


def get_data_manager() -> DataSourceManager:
    """Retorna a instância global do gerenciador de dados."""
    global _manager
    if _manager is None:
        _manager = DataSourceManager()
    return _manager
