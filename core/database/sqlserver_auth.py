import logging
from typing import Dict, Optional, List, Any
from core.database.database import get_db_manager
import bcrypt
from sqlalchemy import text

logger = logging.getLogger(__name__)

SESSAO_MINUTOS = 30  # Duração da sessão em minutos

def initialize_db():
    """
    Inicializa o banco de dados para autenticação.
    Para SQL Server, isso pode significar verificar a existência da tabela de usuários.
    Por enquanto, apenas garante que o gerenciador de DB está pronto.
    """
    db_manager = get_db_manager()
    success, message = db_manager.test_connection()
    if not success:
        logger.error(f"Falha ao inicializar DB para autenticação: {message}")
        raise ConnectionError(f"Não foi possível conectar ao SQL Server: {message}")
    logger.info("SQL Server DB para autenticação inicializado e conectado.")

def verify_user(username: str, password: str) -> Optional[Dict[str, str]]:
    """
    Verifica as credenciais do usuário no SQL Server.
    """
    db_manager = get_db_manager()
    try:
        query = "SELECT id, username, password_hash, role, ativo FROM users WHERE username = :username AND ativo = 1"
        user_data = db_manager.execute_query_one(query, {"username": username})

        if user_data:
            user_id, stored_username, stored_password_hash, stored_role, ativo = user_data
            if bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                return {"id": user_id, "username": stored_username, "role": stored_role, "ativo": bool(ativo)}
            else:
                return None
        else:
            return None
    except Exception as e:
        logger.error(f"Erro ao verificar usuário no SQL Server: {e}", exc_info=True)
        return None

def criar_usuario(username: str, password: str, role: str) -> None:
    """
    Cria um novo usuário no banco de dados SQL Server.
    """
    db_manager = get_db_manager()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        with db_manager.get_session_context() as session:
            # Check if username already exists
            check_query = "SELECT COUNT(*) FROM users WHERE username = :username"
            count_result = session.execute(text(check_query), {"username": username}).scalar_one()

            if count_result > 0:
                raise ValueError(f"Usuário '{username}' já existe.")

            insert_query = "INSERT INTO users (username, password_hash, role, ativo) VALUES (:username, :password_hash, :role, 1)"
            session.execute(text(insert_query), {"username": username, "password_hash": hashed_password, "role": role})
            logger.info(f"Usuário '{username}' criado com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao criar usuário '{username}': {e}", exc_info=True)
        raise

def get_all_users() -> List[Dict[str, Any]]:
    """
    Retorna todos os usuários do banco de dados.
    """
    db_manager = get_db_manager()
    try:
        query = "SELECT id, username, role, ativo FROM users"
        users_data = db_manager.execute_query(query)
        return [{"id": user[0], "username": user[1], "role": user[2], "ativo": bool(user[3])} for user in users_data]
    except Exception as e:
        logger.error(f"Erro ao obter todos os usuários: {e}", exc_info=True)
        return []

def update_user_role(user_id: int, new_role: str) -> None:
    """
    Atualiza o papel de um usuário.
    """
    db_manager = get_db_manager()
    try:
        with db_manager.get_session_context() as session:
            update_query = "UPDATE users SET role = :new_role WHERE id = :user_id"
            session.execute(text(update_query), {"new_role": new_role, "user_id": user_id})
            logger.info(f"Papel do usuário ID '{user_id}' atualizado para '{new_role}'.")
    except Exception as e:
        logger.error(f"Erro ao atualizar papel do usuário ID '{user_id}': {e}", exc_info=True)
        raise

def set_user_status(user_id: int, is_active: bool) -> None:
    """
    Define o status (ativo/inativo) de um usuário.
    """
    db_manager = get_db_manager()
    try:
        with db_manager.get_session_context() as session:
            status_value = 1 if is_active else 0
            update_query = "UPDATE users SET ativo = :status_value WHERE id = :user_id"
            session.execute(text(update_query), {"status_value": status_value, "user_id": user_id})
            logger.info(f"Status do usuário ID '{user_id}' definido para '{'ativo' if is_active else 'inativo'}'.")
    except Exception as e:
        logger.error(f"Erro ao definir status do usuário ID '{user_id}': {e}", exc_info=True)
        raise

def reset_user_password(user_id: int, new_password: str) -> None:
    """
    Redefine a senha de um usuário.
    """
    db_manager = get_db_manager()
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        with db_manager.get_session_context() as session:
            update_query = "UPDATE users SET password_hash = :hashed_password WHERE id = :user_id"
            session.execute(text(update_query), {"hashed_password": hashed_password, "user_id": user_id})
            logger.info(f"Senha do usuário ID '{user_id}' redefinida com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao redefinir senha do usuário ID '{user_id}': {e}", exc_info=True)
        raise

def delete_user(user_id: int) -> None:
    """
    Exclui um usuário do banco de dados.
    """
    db_manager = get_db_manager()
    try:
        with db_manager.get_session_context() as session:
            delete_query = "DELETE FROM users WHERE id = :user_id"
            session.execute(text(delete_query), {"user_id": user_id})
            logger.info(f"Usuário ID '{user_id}' excluído com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao excluir usuário ID '{user_id}': {e}", exc_info=True)
        raise

# Exemplo de uso (para testes locais, não será executado em produção)
if __name__ == "__main__":
    # Este bloco seria para testar a funcionalidade diretamente
    # Em um ambiente real, as configurações viriam do .env
    # e o bcrypt estaria instalado.
    pass
