"""
Data Source Manager - Acesso centralizado a Filial_Madureira.parquet
Fonte única de dados: data/parquet/Filial_Madureira.parquet
"""

import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

# Constantes: Arquivos de dados
MAIN_DATA_FILE = "data/parquet/Filial_Madureira.parquet"
CLEAN_DATA_FILE = "data/parquet/Filial_Madureira_LIMPO.parquet"


class FilialMadureiraDataSource:
    """Acesso centralizado ao arquivo Filial_Madureira.parquet."""

    def __init__(self):
        self._connected = False
        self._df_cache: Optional[pd.DataFrame] = None

        # Priorizar arquivo limpo se existir
        clean_path = Path(CLEAN_DATA_FILE)
        if clean_path.exists():
            self.file_path = clean_path
            logger.info(f"📊 Usando arquivo limpo: {CLEAN_DATA_FILE}")
        else:
            self.file_path = Path(MAIN_DATA_FILE)
            logger.info(f"📊 Usando arquivo original: {MAIN_DATA_FILE}")

    def connect(self) -> bool:
        """Verifica se arquivo Parquet existe."""
        if self.file_path.exists():
            self._connected = True
            logger.info(f"✓ Filial_Madureira conectado: {self.file_path}")
            return True

        logger.error(f"✗ Arquivo não encontrado: {self.file_path}")
        self._connected = False
        return False

    def is_connected(self) -> bool:
        """Verifica se está conectado."""
        return self._connected and self.file_path.exists()

    def _load_data(self, force_reload: bool = False) -> pd.DataFrame:
        """Carrega dados com cache."""
        if force_reload or self._df_cache is None:
            try:
                self._df_cache = pd.read_parquet(self.file_path)
                logger.info(f"✓ Dados carregados: {self._df_cache.shape}")

                # Forçar tipos de dados corretos para colunas problemáticas
                # Colunas que deveriam ser strings
                for col in ["DESCRIÇÃO", "FABRICANTE"]:
                    if col in self._df_cache.columns:
                        self._df_cache[col] = self._df_cache[col].astype(str).replace('nan', pd.NA) # Converte NaN para NA do Pandas

                # Colunas que deveriam ser datetime
                for col in ["DT CADASTRO", "DT ULTIMA COMPRA"]:
                    if col in self._df_cache.columns:
                        # Tenta converter para datetime, coercing erros para NaT (Not a Time)
                        self._df_cache[col] = pd.to_datetime(self._df_cache[col], errors='coerce')

            except Exception as e:
                logger.error(f"Erro ao carregar dados: {e}")
                self._df_cache = pd.DataFrame()

        df_copy = self._df_cache.copy() if not self._df_cache.empty else pd.DataFrame()
        return df_copy

    def get_data(self, limit: int = None) -> pd.DataFrame:
        """Obtém todos os dados ou limitados."""
        df = self._load_data()
        if limit and not df.empty:
            df = df.head(limit)
        return df

    def search(self, column: str, value: str, limit: int = 10) -> pd.DataFrame:
        """Busca em uma coluna."""
        try:
            df = self._load_data()
            if df.empty or column not in df.columns:
                return pd.DataFrame()

            # Busca case-insensitive
            mask = df[column].astype(str).str.contains(value, case=False, na=False)
            result = df[mask].head(limit)
            return result

        except Exception as e:
            logger.error(f"Erro ao buscar: {e}")
            return pd.DataFrame()

    def get_filtered_data(
        self, filters: Dict[str, Any], limit: int = None
    ) -> pd.DataFrame:
        """Busca com filtros exatos."""
        try:
            df = self._load_data()
            if df.empty:
                return pd.DataFrame()

            for col, value in filters.items():
                if col in df.columns:
                    # Tenta converter o valor para o tipo da coluna
                    col_dtype = df[col].dtype
                    try:
                        if pd.api.types.is_numeric_dtype(col_dtype) and isinstance(value, str):
                            # Tenta converter a string para o tipo numérico da coluna
                            converted_value = pd.to_numeric(value, errors='raise')
                            df = df[df[col] == converted_value]
                        elif pd.api.types.is_datetime64_any_dtype(col_dtype) and isinstance(value, str):
                            # Tenta converter a string para o tipo datetime da coluna
                            converted_value = pd.to_datetime(value, errors='raise')
                            df = df[df[col] == converted_value]
                        else:
                            # Para outros tipos ou falha na conversão, usa o valor original
                            df = df[df[col] == value]
                    except (ValueError, TypeError):
                        # Se a conversão falhar, faz a comparação como string (case-insensitive)
                        df = df[df[col].astype(str).str.lower() == str(value).lower()]
                else:
                    logger.warning(f"Coluna '{col}' não encontrada para filtragem.")
                    return pd.DataFrame()

            if limit:
                df = df.head(limit)

            return df
        except Exception as e:
            logger.error(f"Erro ao filtrar: {e}")
            return pd.DataFrame()

    def get_columns(self) -> List[str]:
        """Retorna lista de colunas."""
        df = self._load_data()
        return df.columns.tolist() if not df.empty else []

    def get_shape(self) -> tuple:
        """Retorna dimensões dos dados."""
        df = self._load_data()
        return df.shape if not df.empty else (0, 0)

    def get_info(self) -> Dict[str, Any]:
        """Retorna informações sobre os dados."""
        df = self._load_data()
        if df.empty:
            return {"status": "sem_dados"}

        return {
            "file": str(self.file_path),
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.to_dict(),
            "memory_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
        }


class DataSourceManager:
    """
    Gerenciador de fonte de dados centralizado.
    Acessa unicamente: data/parquet/Filial_Madureira.parquet
    """

    def __init__(self):
        self._source = FilialMadureiraDataSource()
        self._source.connect()

    def get_data(
        self, table_name: str = None, limit: int = None, source: str = None
    ) -> pd.DataFrame:
        """Obtém dados (table_name é ignorado)."""
        return self._source.get_data(limit)

    def search_data(
        self,
        table_name: str = None,
        column: str = None,
        value: str = None,
        limit: int = 10,
        source: str = None,
    ) -> pd.DataFrame:
        """Busca dados em coluna especificada."""
        if not column or not value:
            return pd.DataFrame()
        return self._source.search(column, value, limit)

    def get_filtered_data(
        self,
        table_name: str = None,
        filters: Dict[str, Any] = None,
        limit: int = None,
        source: str = None,
    ) -> pd.DataFrame:
        """Busca com filtros."""
        if not filters:
            return pd.DataFrame()
        return self._source.get_filtered_data(filters, limit)

    def execute_query(self, query: str, params: Dict = None) -> List[Dict]:
        """Não suportado."""
        return []

    def get_available_sources(self) -> List[str]:
        """Retorna fontes disponíveis."""
        if self._source.is_connected():
            return ["filial_madureira"]
        return []

    def get_source_info(self) -> Dict[str, Any]:
        """Retorna informações da fonte."""
        return self._source.get_info()


# Instância global singleton
_data_manager_instance: Optional[DataSourceManager] = None


def get_data_manager() -> DataSourceManager:
    """Retorna instância singleton do DataSourceManager."""
    global _data_manager_instance
    if _data_manager_instance is None:
        _data_manager_instance = DataSourceManager()
    return _data_manager_instance
