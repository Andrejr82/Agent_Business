"""Gerenciamento de conexões com SQL Server com pool robusto."""

import logging
from typing import Any, Dict, Optional, Tuple
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from contextlib import contextmanager
from core.config.config import Config

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """
    Gerenciador centralizado de conexões com o SQL Server.
    Implementa pool de conexões com recuperação automática de erros.
    """

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        """Implementa singleton para garantir apenas uma instância."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa o engine e session factory."""
        try:
            config = Config()
            uri = config.SQLALCHEMY_DATABASE_URI

            logger.info("Inicializando DatabaseConnectionManager...")
            logger.debug("Usando URI: %s@***", uri.split("@")[0])

            # Criar engine com pool configurado
            self._engine = create_engine(
                uri,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
                isolation_level="READ_COMMITTED",
            )

            # Configurar listener para tentar recuperar conexões perdidas
            @event.listens_for(self._engine, "connect")
            def receive_connect(dbapi_conn, connection_record):
                """Configurações ao conectar."""
                # A configuração de decodificação foi removida pois causava
                # AttributeError com versões mais recentes do pyodbc.
                # O driver moderno geralmente lida com Unicode corretamente.
                pass

            # Criar session factory
            self._session_factory = sessionmaker(bind=self._engine)

            logger.info("DatabaseConnectionManager inicializado com sucesso")

        except (SQLAlchemyError, OSError) as exc:
            logger.error(
                "Erro ao inicializar DatabaseConnectionManager: %s", exc, exc_info=True
            )
            raise

    def get_engine(self):
        """Retorna o engine SQLAlchemy."""
        if self._engine is None:
            self._initialize()
        return self._engine

    def get_session(self) -> Session:
        """Retorna uma nova session."""
        if self._session_factory is None:
            self._initialize()
        return self._session_factory()

    @contextmanager
    def get_connection(self):
        """
        Context manager para obter uma conexão com tratamento.

        Uso:
            with manager.get_connection() as conn:
                result = conn.execute(text("SELECT * FROM tabela"))
        """
        engine = self.get_engine()
        conn = None

        try:
            conn = engine.connect()
            logger.debug("Conexão obtida do pool")
            yield conn

        except OperationalError as exc:
            logger.error("Erro operacional de banco: %s", exc)
            raise

        except SQLAlchemyError as exc:
            logger.error("Erro SQLAlchemy: %s", exc)
            raise

        except Exception as exc:
            logger.error("Erro inesperado ao obter conexão: %s", exc, exc_info=True)
            raise

        finally:
            if conn is not None:
                conn.close()
                logger.debug("Conexão retornada ao pool")

    @contextmanager
    def get_session_context(self):
        """
        Context manager para obter uma session com tratamento.

        Uso:
            with manager.get_session_context() as session:
                result = session.query(Usuario).all()
        """
        session = None

        try:
            session = self.get_session()
            logger.debug("Session criada")
            yield session
            session.commit()
            logger.debug("Session commitada com sucesso")

        except (SQLAlchemyError, OSError) as exc:
            if session:
                session.rollback()
            logger.error("Erro na session: %s", exc, exc_info=True)
            raise

        finally:
            if session:
                session.close()
                logger.debug("Session fechada")

    def test_connection(self) -> Tuple[bool, str]:
        """
        Testa a conexão com o banco de dados.

        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            engine = self.get_engine()
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            msg = "Conexao com banco de dados estabelecida"
            return True, msg

        except (SQLAlchemyError, OSError) as exc:
            msg = f"Erro ao conectar ao banco: {str(exc)}"
            logger.error(msg)
            return False, msg

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None):
        """
        Executa uma consulta e retorna os resultados.

        Args:
            query: String SQL
            params: Parâmetros para a query

        Returns:
            Lista de resultados
        """
        try:
            with self.get_connection() as conn:
                result = conn.execute(text(query), params or {})
                return result.fetchall()

        except (SQLAlchemyError, OSError) as exc:
            logger.error("Erro ao executar query: %s", exc, exc_info=True)
            raise

    def execute_query_one(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """
        Executa uma consulta e retorna o primeiro resultado.

        Args:
            query: String SQL
            params: Parâmetros para a query

        Returns:
            Primeiro resultado ou None
        """
        try:
            results = self.execute_query(query, params)
            return results[0] if results else None

        except (SQLAlchemyError, OSError) as exc:
            logger.error("Erro ao executar query: %s", exc, exc_info=True)
            raise

    def close(self):
        """Fecha o engine e libera conexões."""
        if self._engine:
            self._engine.dispose()
            logger.info("Engine SQLAlchemy fechado")


# Instância global
_db_manager: Optional[DatabaseConnectionManager] = None


def get_db_manager() -> DatabaseConnectionManager:
    """Retorna a instância do gerenciador de banco de dados."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseConnectionManager()
    return _db_manager
