import os
from sqlalchemy import create_engine
from core.config.config import Config

# Try to obtain DATABASE_URI from Config or environment. If not provided, fall back to
# an in-memory sqlite database so tests and local runs that don't use SQL Server won't
# fail at import time.
cfg = Config()
DATABASE_URI = getattr(cfg, "SQLALCHEMY_DATABASE_URI", None) or os.getenv("DATABASE_URI", "")
DATABASE_URI = DATABASE_URI.strip() if isinstance(DATABASE_URI, str) else ""

if not DATABASE_URI:
    # Parquet-only mode / tests: use lightweight sqlite in-memory DB as a safe fallback.
    DATABASE_URI = "sqlite:///:memory:"

# Create the SQLAlchemy engine with connection pooling
# pool_size: number of connections to keep open in the pool
# max_overflow: number of connections that can be opened beyond the pool_size
engine = create_engine(DATABASE_URI, pool_size=10, max_overflow=20)


def get_db_connection():
    """Return a SQLAlchemy Connection from the engine's pool.

    This function intentionally uses a fallback sqlite engine when no DATABASE_URI is
    configured so imports that trigger DB initialization (e.g. during tests) don't
    crash the process when SQL Server is intentionally disabled.
    """
    return engine.connect()
