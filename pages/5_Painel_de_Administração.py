import streamlit as st
from datetime import datetime
import logging
from core.database import postgres_auth as auth_db

audit_logger = logging.getLogger("audit")

# --- Verificação de Autenticação e Permissão ---
if st.session_state.get("authenticated") and st.session_state.get("role") == "admin":
    # --- Configuração da Página ---
    st.set_page_config(
        page_title="Painel de Administração", page_icon="⚙️", layout="wide"
    )

    st.markdown(
        "<h1 class='main-header'>⚙️ Painel de Administração</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='sub-header'>Gerencie usuários, configurações e monitore o sistema.</p>",
        unsafe_allow_html=True,
    )

    # --- Gerenciamento de Usuários ---
    st.subheader("👥 Gerenciamento de Usuários")

    # Adicionar Novo Usuário
    with st.expander("➕ Adicionar Novo Usuário"):
        with st.form("add_user_form"):
            new_username = st.text_input("Nome de Usuário")
            new_password = st.text_input("Senha", type="password")
            new_role = st.selectbox("Papel", ["user", "admin"])
            add_user_submitted = st.form_submit_button("Adicionar Usuário")

            if add_user_submitted:
                try:
                    auth_db.criar_usuario(new_username, new_password, new_role)
                    st.success(f"Usuário '{new_username}' adicionado com sucesso!")
                    audit_logger.info(
                        f"Admin {st.session_state.get('username')} adicionou o usuário {new_username} com papel {new_role}."
                    )
                    st.rerun()
                except ValueError as e:
                    st.error(f"Erro ao adicionar usuário: {e}")
                except Exception as e:
                    st.error(f"Ocorreu um erro inesperado: {e}")

    # Listar e Gerenciar Usuários Existentes
    st.markdown("---")
    st.subheader("Lista de Usuários")
    users = auth_db.get_all_users()
    if users:
        df_users = st.dataframe(users, width='stretch')

        st.markdown("---")
        st.subheader("Editar Usuário Existente")
        selected_username = st.selectbox(
            "Selecione o Usuário para Editar", [u["username"] for u in users]
        )

        if selected_username:
            selected_user = next(
                (u for u in users if u["username"] == selected_username), None
            )
            if selected_user:
                user_id = selected_user["id"]

                with st.form(f"edit_user_form_{user_id}"):
                    current_role = selected_user["role"]
                    current_status = selected_user["ativo"]

                    edited_role = st.selectbox(
                        "Papel",
                        ["user", "admin"],
                        index=["user", "admin"].index(current_role),
                    )
                    edited_status = st.checkbox("Ativo", value=current_status)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        update_submitted = st.form_submit_button(
                            "Atualizar Papel/Status"
                        )
                    with col2:
                        reset_password_submitted = st.form_submit_button(
                            "Redefinir Senha"
                        )
                    with col3:
                        delete_submitted = st.form_submit_button(
                            "Excluir Usuário", type="secondary"
                        )

                    if update_submitted:
                        if edited_role != current_role:
                            auth_db.update_user_role(user_id, edited_role)
                            st.success(
                                f"Papel do usuário '{selected_username}' atualizado para '{edited_role}'."
                            )
                            audit_logger.info(
                                f"Admin {st.session_state.get('username')} atualizou o papel do usuário {selected_username} para {edited_role}."
                            )
                        if edited_status != current_status:
                            auth_db.set_user_status(user_id, edited_status)
                            st.success(
                                f"Status do usuário '{selected_username}' atualizado para {'Ativo' if edited_status else 'Inativo'}."
                            )
                            audit_logger.info(
                                f"Admin {st.session_state.get('username')} atualizou o status do usuário {selected_username} para {'Ativo' if edited_status else 'Inativo'}."
                            )
                        st.rerun()

                    if reset_password_submitted:
                        new_temp_password = st.text_input(
                            "Nova Senha Temporária",
                            type="password",
                            key=f"temp_pass_{user_id}",
                        )
                        if st.form_submit_button("Confirmar Redefinição"):
                            auth_db.reset_user_password(user_id, new_temp_password)
                            st.success(
                                f"Senha do usuário '{selected_username}' redefinida com sucesso!"
                            )
                            audit_logger.info(
                                f"Admin {st.session_state.get('username')} redefiniu a senha do usuário {selected_username}."
                            )
                            st.rerun()

                    if delete_submitted:
                        if st.checkbox(
                            f"Confirmar exclusão de {selected_username}?",
                            key=f"confirm_delete_{user_id}",
                        ):
                            if st.form_submit_button(
                                "Sim, Excluir Permanentemente", type="danger"
                            ):
                                auth_db.delete_user(user_id)
                                st.success(
                                    f"Usuário '{selected_username}' excluído permanentemente."
                                )
                                audit_logger.info(
                                    f"Admin {st.session_state.get('username')} excluiu o usuário {selected_username}."
                                )
                                st.rerun()
    else:
        st.info("Nenhum usuário cadastrado ainda.")

    st.markdown(
        f"<div class='footer'>Desenvolvido para Análise de Dados © {datetime.now().year}</div>",
        unsafe_allow_html=True,
    )

# Se não for admin, mostra uma mensagem de erro e oculta o conteúdo.
elif st.session_state.get("authenticated"):
    st.error("Acesso negado. Você não tem permissão para acessar esta página.")
    st.stop()

# Se não estiver logado, redireciona para o login
else:
    st.error(
        "Acesso negado. Por favor, faça o login na página principal para acessar esta área."
    )
    st.stop()
