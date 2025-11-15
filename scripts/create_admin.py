import getpass
import os

# Usa o adapter Parquet quando presente; falls back para SQL adapter se necessário
try:
    from core.database import parquet_auth_db as auth_db
except Exception:
    from core.database import sql_server_auth_db as auth_db


if __name__ == "__main__":
    username = input("Usuário admin: ").strip()
    password = getpass.getpass("Senha: ").strip()
    auth_db.init_db()
    auth_db.criar_usuario(username, password, role="admin")
    print("Admin criado com sucesso.")
