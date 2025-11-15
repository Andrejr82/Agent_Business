import importlib
from pathlib import Path


def test_parquet_auth_basic(tmp_path, monkeypatch):
    users_file = tmp_path / "users.parquet"
    monkeypatch.setenv("USERS_PARQUET_PATH", str(users_file))

    # Import module after definir USERS_PARQUET_PATH
    from core.database import parquet_auth_db as pdb

    importlib.reload(pdb)

    pdb.init_db()
    pdb.criar_usuario("testuser", "senha123", role="user")
    role, err = pdb.autenticar_usuario("testuser", "senha123")
    assert role == "user" and err is None
