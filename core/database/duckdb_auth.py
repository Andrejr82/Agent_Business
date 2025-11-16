import duckdb
import bcrypt
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database.models import Base, User # Import Base and User

DB_FILE = "data/users.db"
DB_DIR = "data"
SESSAO_MINUTOS = 60

# Define the engine globally or pass it around
# For simplicity, let's define it here, but a more robust solution might manage it differently.
engine = create_engine(f"duckdb:///{DB_FILE}")
Session = sessionmaker(bind=engine)

def get_connection():
    """Cria e retorna uma conexão com o banco de dados DuckDB."""
    os.makedirs(DB_DIR, exist_ok=True)
    # For SQLAlchemy, we don't directly return a duckdb connection object for ORM operations
    # but rather a session. However, some functions still use direct duckdb.connect.
    # We'll keep this for compatibility with existing direct duckdb calls.
    con = duckdb.connect(DB_FILE)
    return con

def initialize_db():
    """Cria a tabela de usuários se ela não existir e adiciona um usuário admin padrão."""
    os.makedirs(DB_DIR, exist_ok=True) # Ensure directory exists
    
    # Create tables defined in Base.metadata
    Base.metadata.create_all(engine)

    session = Session()
    try:
        # Adicionar usuário admin padrão se não existir
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        existing_admin = session.query(User).filter_by(username=admin_username).first()

        if not existing_admin:
            admin_password = os.getenv("ADMIN_PASSWORD", "admin")
            hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
            
            new_admin = User(
                username=admin_username,
                password_hash=hashed_password.decode('utf-8'),
                role="admin"
            )
            session.add(new_admin)
            session.commit()
            print(f"Usuário admin padrão '{admin_username}' criado com sucesso.")
        else:
            print(f"Usuário admin padrão '{admin_username}' já existe.")
    except Exception as e:
        session.rollback()
        print(f"Erro ao adicionar usuário admin padrão: {e}")
    finally:
        session.close()

def criar_usuario(username, password, role):
    """Cria um novo usuário no banco de dados."""
    if not username or not password or not role:
        raise ValueError("Nome de usuário, senha e papel são obrigatórios.")

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    session = Session()
    try:
        new_user = User(
            username=username,
            password_hash=hashed_password.decode('utf-8'),
            role=role
        )
        session.add(new_user)
        session.commit()
    except Exception as e: # Catching generic Exception for now, can be more specific
        session.rollback()
        if "UNIQUE constraint failed" in str(e): # DuckDB specific constraint error message
            raise ValueError(f"Usuário '{username}' já existe.")
        else:
            raise
    finally:
        session.close()

def get_user(username):
    """Busca um usuário pelo nome de usuário."""
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user:
            return {
                "id": user.id,
                "username": user.username,
                "password_hash": user.password_hash,
                "role": user.role,
                "ativo": user.ativo,
                "tentativas_invalidas": user.tentativas_invalidas,
                "bloqueado_ate": user.bloqueado_ate,
                "ultimo_login": user.ultimo_login,
                "redefinir_solicitado": user.redefinir_solicitado,
                "redefinir_aprovado": user.redefinir_aprovado,
            }
    finally:
        session.close()
    return None

def get_all_users():
    """Retorna todos os usuários do banco de dados."""
    session = Session()
    try:
        users = session.query(User).all()
        return [
            {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "ativo": user.ativo,
            }
            for user in users
        ]
    finally:
        session.close()

def update_user_role(user_id, new_role):
    """Atualiza o papel de um usuário."""
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.role = new_role
            session.commit()
    finally:
        session.close()

def set_user_status(user_id, is_active):
    """Ativa ou desativa um usuário."""
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.ativo = is_active
            session.commit()
    finally:
        session.close()

def reset_user_password(user_id, new_password):
    """Redefine a senha de um usuário."""
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            user.password_hash = hashed_password.decode('utf-8')
            session.commit()
    finally:
        session.close()

def delete_user(user_id):
    """Exclui um usuário do banco de dados."""
    session = Session()
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if user:
            session.delete(user)
            session.commit()
    finally:
        session.close()

def verify_user(username, password):
    """Verifica as credenciais de um usuário."""
    session = Session()
    try:
        user = session.query(User).filter_by(username=username).first()
        if user and user.ativo:
            hashed_password = user.password_hash.encode('utf-8')
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return {"username": user.username, "role": user.role}
    finally:
        session.close()
    return None

# Inicializar o banco de dados na primeira importação
# initialize_db() # Commented out to temporarily disable duckdb initialization