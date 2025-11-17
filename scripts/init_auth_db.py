import sys
import os
import bcrypt
from core.database.database import get_db_manager
from core.config.config import Config

# Ensure environment variables are loaded
# In a real application, Config() would handle this.
# For this script, we explicitly load it if not already loaded.
if not os.environ.get("DB_SERVER"):
    from dotenv import load_dotenv
    # Assuming .env is in the project root
    dotenv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path, override=True)
    else:
        print("Aviso: Arquivo .env não encontrado. As configurações dependerão das variáveis de ambiente do sistema.")

# Initialize Config to ensure all environment variables are processed
Config()

def create_users_table():
    """Cria a tabela 'users' no SQL Server."""
    db_manager = get_db_manager()
    create_table_sql = """
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' and xtype='U')
    CREATE TABLE users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL,
        ativo BIT NOT NULL DEFAULT 1
    );
    """
    try:
        print("Tentando criar a tabela 'users'...")
        db_manager.execute_query(create_table_sql)
        print("Tabela 'users' criada ou já existente.")
    except Exception as e:
        print(f"Erro ao criar a tabela 'users': {e}", file=sys.stderr)
        sys.exit(1)

def add_initial_admin_user(username="admin", password="admin_password", role="admin"):
    """Adiciona um usuário administrador inicial se ele não existir."""
    db_manager = get_db_manager()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        # Check if user already exists
        check_user_sql = "SELECT COUNT(*) FROM users WHERE username = :username"
        count = db_manager.execute_query_one(check_user_sql, {"username": username})[0]

        if count == 0:
            print(f"Adicionando usuário administrador inicial '{username}'...")
            insert_user_sql = """
            INSERT INTO users (username, password_hash, role, ativo)
            VALUES (:username, :password_hash, :role, 1);
            """
            db_manager.execute_query(insert_user_sql, {
                "username": username,
                "password_hash": hashed_password,
                "role": role
            })
            print(f"Usuário '{username}' adicionado com sucesso.")
        else:
            print(f"Usuário '{username}' já existe. Pulando a adição.")
    except Exception as e:
        print(f"Erro ao adicionar usuário inicial '{username}': {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    print("Iniciando script de inicialização do banco de dados de autenticação...")
    create_users_table()
    add_initial_admin_user()
    print("Script de inicialização do banco de dados de autenticação concluído.")
    sys.exit(0)
