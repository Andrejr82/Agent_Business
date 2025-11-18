# Este arquivo lida com a autenticação de usuários. É crucial que as senhas nunca sejam armazenadas em texto plano.
# Em vez disso, utilizamos funções de hash seguras (como bcrypt, implementado em sql_server_auth_db.py)
# para converter as senhas em um formato ilegível e irreversível. Isso protege as informações dos usuários
# mesmo em caso de violação de dados, pois apenas os hashes são armazenados, não as senhas originais.
import os
import streamlit as st
import time
import logging

# Always use SQLite for authentication
from core.database import sqlserver_auth as auth_db

audit_logger = logging.getLogger("audit")

# Nota: não inicializamos o DB no momento do import para evitar efeitos colaterais
# durante testes ou importações em CI. A inicialização ocorre de forma lazy dentro
# do fluxo de `login()` quando necessário.


# --- Login integrado ao backend SQLite ---
def login():
    # Coloca o formulário de login em uma coluna centralizada para melhor apelo visual
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style='text-align:center;'>
                <img src='https://raw.githubusercontent.com/github/explore/main/topics/business-intelligence/business-intelligence.png' width='150'>
                <h2>Agente de Negócios</h2>
                <p style='color:#666;'>Acesse com seu usuário e senha para continuar.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form"):
            username = st.text_input("Usuário", placeholder="Digite seu usuário")
            password = st.text_input(
                "Senha", type="password", placeholder="Digite sua senha"
            )
            login_btn = st.form_submit_button("Entrar", width='stretch', type="primary")

            if login_btn:
                # Bypass de autenticação para desenvolvimento (ANTES da inicialização do DB)
                if username == "admin" and password == "bypass":
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = "admin"
                    st.session_state["role"] = "admin"
                    st.session_state["ultimo_login"] = time.time()
                    audit_logger.info(
                        "Usuário admin logado com sucesso (bypass). Papel: admin"
                    )
                    st.success("Bem-vindo, admin! Acesso de desenvolvedor concedido.")
                    time.sleep(1)  # Pausa para o usuário ler a mensagem
                    st.rerun()
                    return

                # Inicialização lazy do store de usuários (compatível com Parquet).
                # Tenta inicializar, mas não falha se SQL Server não estiver disponível
                if "db_inicializado" not in st.session_state:
                    try:
                        auth_db.initialize_db() # Changed this line from init_db to initialize_db
                        st.session_state["db_inicializado"] = True
                    except (AttributeError, ConnectionError) as e:
                        logger = logging.getLogger(__name__)
                        logger.warning(f"SQL Server não disponível, usando apenas modo bypass: {e}")
                        st.session_state["db_inicializado"] = False
                        if hasattr(auth_db, "init_store"):
                            auth_db.init_store()

                # Se o DB não estiver habilitado (por design do ambiente), não tentamos conectar
                if st.session_state.get("db_inicializado", False):
                    user_data = auth_db.verify_user(username, password)
                else:
                    user_data = None  # Sem DB, apenas bypass funciona
                if user_data:
                    role = user_data["role"]
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.session_state["role"] = role
                    st.session_state["ultimo_login"] = time.time()
                    audit_logger.info(
                        f"Usuário {username} logado com sucesso. Papel: {role}"
                    )
                    st.success(f"Bem-vindo, {username}! Redirecionando...")
                    time.sleep(1)
                    st.rerun()
                else:
                    erro = "Usuário ou senha inválidos."
                    audit_logger.warning(
                        f"Tentativa de login falha para o usuário: {username}. Erro: {erro}"
                    )
                    st.error(erro)


# --- Expiração automática de sessão ---
def sessao_expirada():
    if not st.session_state.get("ultimo_login"):
        return True
    tempo = time.time() - st.session_state["ultimo_login"]
    return tempo > 60 * auth_db.SESSAO_MINUTOS
