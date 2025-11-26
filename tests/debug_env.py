import os

def read_env():
    try:
        with open(".env", "r", encoding="utf-8") as f:
            content = f.read()
            print("--- Conteúdo do .env (Mascarado) ---")
            for line in content.splitlines():
                if "SQLALCHEMY_DATABASE_URI" in line:
                    if "postgres" in line:
                        print("SQLALCHEMY_DATABASE_URI=postgresql://... (OK - PostgreSQL detectado)")
                    elif "mssql" in line:
                        print("SQLALCHEMY_DATABASE_URI=mssql://... (ERRO - Ainda é MSSQL)")
                    else:
                        print(f"SQLALCHEMY_DATABASE_URI={line[:20]}...")
                elif "KEY" in line or "PASSWORD" in line:
                    print(f"{line.split('=')[0]}=****")
                else:
                    print(line)
    except Exception as e:
        print(f"Erro ao ler .env: {e}")

if __name__ == "__main__":
    read_env()
