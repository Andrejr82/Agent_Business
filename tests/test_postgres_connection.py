import sys
import os
import logging

# Add project root to path
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from core.config.config import Config
from core.database.database import get_db_manager
from sqlalchemy import text

def test_connection():
    print("--- Testando Conexão com Supabase (PostgreSQL) ---")
    
    # Forçar recarregamento do .env
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    # Forçar recarregamento da config para pegar o novo .env
    Config._initialized = False
    Config.setup()
    
    uri = Config.SQLALCHEMY_DATABASE_URI
    # Mascarar senha para log
    safe_uri = uri.split("@")[-1] if "@" in uri else "URI Inválida"
    print(f"URI Configurada (host): ...@{safe_uri}")
    
    if "postgresql" not in uri and "postgres" not in uri:
        print("ERRO: URI não parece ser de PostgreSQL!")
        return

    manager = get_db_manager()
    
    try:
        # Teste 1: Conexão básica
        print("\n1. Tentando conectar...")
        success, msg = manager.test_connection()
        if success:
            print(f"   SUCESSO: {msg}")
        else:
            print(f"   FALHA: {msg}")
            return

        # Teste 2: Verificar tabela users
        print("\n2. Verificando tabela 'users'...")
        with manager.get_connection() as conn:
            result = conn.execute(text("SELECT count(*) FROM users"))
            count = result.scalar()
            print(f"   SUCESSO: Tabela 'users' encontrada com {count} registros.")
            
            # Listar usuários (sem senhas)
            users = conn.execute(text("SELECT id, username, role, ativo FROM users")).fetchall()
            print("\n   Usuários encontrados:")
            for u in users:
                print(f"   - ID: {u[0]}, User: {u[1]}, Role: {u[2]}, Ativo: {u[3]}")

    except Exception as e:
        print(f"\nERRO DURANTE O TESTE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()
