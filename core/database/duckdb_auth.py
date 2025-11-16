import duckdb
import bcrypt
import os

DB_FILE = "data/users.db"
DB_DIR = "data"
SESSAO_MINUTOS = 60

def get_connection():
    """Cria e retorna uma conexão com o banco de dados DuckDB."""
    os.makedirs(DB_DIR, exist_ok=True)
    con = duckdb.connect(DB_FILE)
    return con

def initialize_db():
    """Cria a tabela de usuários se ela não existir e adiciona um usuário admin padrão."""
    con = get_connection()
    con.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username VARCHAR UNIQUE NOT NULL,
            hashed_password VARCHAR NOT NULL,
            role VARCHAR NOT NULL,
            ativo BOOLEAN DEFAULT TRUE
        );
    """)
    
    # Adicionar usuário admin padrão se não existir
    try:
        # Verificar se já existe algum usuário
        count = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count == 0:
            # Adicionar usuário admin padrão
            admin_username = os.getenv("ADMIN_USERNAME", "admin")
            admin_password = os.getenv("ADMIN_PASSWORD", "admin")
            hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
            con.execute(
                "INSERT INTO users (username, hashed_password, role) VALUES (?, ?, ?)",
                (admin_username, hashed_password.decode('utf-8'), "admin")
            )
            con.commit()
            print(f"Usuário admin padrão '{admin_username}' criado com sucesso.")
    except Exception as e:
        print(f"Erro ao adicionar usuário admin padrão: {e}")
    finally:
        con.close()

def criar_usuario(username, password, role):
    """Cria um novo usuário no banco de dados."""
    if not username or not password or not role:
        raise ValueError("Nome de usuário, senha e papel são obrigatórios.")

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    con = get_connection()
    try:
        con.execute(
            "INSERT INTO users (username, hashed_password, role) VALUES (?, ?, ?)",
            (username, hashed_password.decode('utf-8'), role)
        )
        con.commit()
    except duckdb.ConstraintException:
        raise ValueError(f"Usuário '{username}' já existe.")
    finally:
        con.close()

def get_user(username):
    """Busca um usuário pelo nome de usuário."""
    con = get_connection()
    # Use a try-finally para garantir que a conexão seja fechada
    try:
        result = con.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if result:
            # Obter nomes das colunas da descrição do cursor
            columns = [desc[0] for desc in con.description]
            return dict(zip(columns, result))
    finally:
        con.close()
    return None

def get_all_users():
    """Retorna todos os usuários do banco de dados."""
    con = get_connection()
    try:
        # O fetchdf retorna um DataFrame do Pandas, que é conveniente para o Streamlit
        users_df = con.execute("SELECT id, username, role, ativo FROM users").fetchdf()
        # Converter para uma lista de dicionários para consistência
        return users_df.to_dict('records')
    finally:
        con.close()

def update_user_role(user_id, new_role):
    """Atualiza o papel de um usuário."""
    con = get_connection()
    con.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
    con.commit()
    con.close()

def set_user_status(user_id, is_active):
    """Ativa ou desativa um usuário."""
    con = get_connection()
    con.execute("UPDATE users SET ativo = ? WHERE id = ?", (is_active, user_id))
    con.commit()
    con.close()

def reset_user_password(user_id, new_password):
    """Redefine a senha de um usuário."""
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    con = get_connection()
    con.execute("UPDATE users SET hashed_password = ? WHERE id = ?", (hashed_password.decode('utf-8'), user_id))
    con.commit()
    con.close()

def delete_user(user_id):
    """Exclui um usuário do banco de dados."""
    con = get_connection()
    con.execute("DELETE FROM users WHERE id = ?", (user_id,))
    con.commit()
    con.close()

def verify_user(username, password):
    """Verifica as credenciais de um usuário."""
    user = get_user(username)
    if user and user['ativo']:
        hashed_password = user['hashed_password'].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
            return {"username": user["username"], "role": user["role"]}
    return None

# Inicializar o banco de dados na primeira importação
initialize_db()
