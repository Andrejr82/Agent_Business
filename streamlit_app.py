import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import uuid

try:
    import plotly.graph_objects as go

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

from core import auth
from core.query_processor import QueryProcessor
from core.session_state import SESSION_STATE_KEYS
from core.config.logging_config import setup_logging
from core.utils.context import correlation_id_var
from ui.ui_components import get_image_download_link

audit_logger = logging.getLogger("audit")

# --- Constantes ---
ROLES = {"ASSISTANT": "assistant", "USER": "user"}
PAGE_CONFIG = {
    "page_title": "Agente de Negócios",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# --- Configuração da Página e Estilos ---
st.set_page_config(**PAGE_CONFIG)

# Load CSS from external file for better organization
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def initialize_session_state():
    """Inicializa o estado da sessão se não existir."""
    if SESSION_STATE_KEYS["QUERY_PROCESSOR"] not in st.session_state:
        try:
            st.session_state[SESSION_STATE_KEYS["QUERY_PROCESSOR"]] = QueryProcessor()
        except RuntimeError as e:
            # GEMINI_API_KEY não configurada, criar um objeto mock
            st.session_state[SESSION_STATE_KEYS["QUERY_PROCESSOR"]] = None
            logging.getLogger(__name__).warning(f"QueryProcessor não inicializado: {e}")

    if SESSION_STATE_KEYS["MESSAGES"] not in st.session_state:
        # Verificar se o QueryProcessor foi inicializado
        if st.session_state[SESSION_STATE_KEYS["QUERY_PROCESSOR"]] is None:
            st.session_state[SESSION_STATE_KEYS["MESSAGES"]] = [
                {
                    "role": ROLES["ASSISTANT"],
                    "output": "⚠️ **GEMINI_API_KEY não configurada!**\n\n"
                             "Para usar o agente BI, você precisa:\n\n"
                             "1. Acessar **Settings** (⋮ menu) no Streamlit Cloud\n"
                             "2. Ir na aba **Secrets**\n"
                             "3. Adicionar:\n"
                             "```\n"
                             "GEMINI_API_KEY = \"sua_chave_aqui\"\n"
                             "GEMINI_MODEL_NAME = \"gemini-2.0-flash-lite\"\n"
                             "```\n\n"
                             "4. Obter chave em: https://aistudio.google.com/app/apikey\n"
                             "5. Salvar e aguardar app reiniciar\n\n"
                             "Enquanto isso, você pode explorar os **Dashboards** no menu lateral! 📊",
                }
            ]
        else:
            st.session_state[SESSION_STATE_KEYS["MESSAGES"]] = [
                {
                    "role": ROLES["ASSISTANT"],
                    "output": "Olá! Como posso ajudar você hoje?",
                }
            ]


def handle_logout():
    """Limpa o estado da sessão e força o rerun para a tela de login."""
    username = st.session_state.get(SESSION_STATE_KEYS["USERNAME"], "N/A")
    audit_logger.info(f"Usuário {username} deslogado.")
    keys_to_clear = [
        SESSION_STATE_KEYS["AUTHENTICATED"],
        SESSION_STATE_KEYS["USERNAME"],
        SESSION_STATE_KEYS["ROLE"],
        SESSION_STATE_KEYS["LAST_LOGIN"],
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()


def handle_chart_selection(selection_data):
    """
    Callback function to handle selection events from Plotly charts.
    Stores the selected data in Streamlit's session state.
    """
    if selection_data and selection_data.get("points"):
        st.session_state["selected_chart_data"] = selection_data["points"]
        st.toast("Dados selecionados no gráfico!", icon="📊")
    else:
        if "selected_chart_data" in st.session_state:
            del st.session_state["selected_chart_data"]
        st.toast("Seleção de gráfico limpa.", icon="🗑️")

def show_bi_assistant():
    """Exibe a interface principal do assistente de BI."""
    st.markdown(
        "<h1 class='main-header'>📊 Agente de Negócios</h1>",
        unsafe_allow_html=True,
    )

    # Exibir histórico de mensagens
    for message in st.session_state[SESSION_STATE_KEYS["MESSAGES"]]:
        with st.chat_message(message["role"]):
            output = message.get("output")

            # Se é uma figura Plotly
            if HAS_PLOTLY and isinstance(output, go.Figure):
                try:
                    st.plotly_chart(output, width='stretch', on_select=handle_chart_selection)
                except Exception as e:
                    st.error(f"Erro ao renderizar gráfico: {e}")
                    st.write(output)
            # Se é DataFrame
            elif isinstance(output, pd.DataFrame):
                st.dataframe(output, width='stretch')
            # Se tem método to_json (figura Plotly antiga versão)
            elif hasattr(output, "to_json"):
                try:
                    st.plotly_chart(output, width='stretch', on_select=handle_chart_selection)
                except Exception as e:
                    st.error(f"Erro ao renderizar gráfico: {e}")
                    st.write(output)
            # Se é texto ou outro tipo
            else:
                st.markdown(str(output or ""))

    # Display selected chart data if available
    if "selected_chart_data" in st.session_state and st.session_state["selected_chart_data"]:
        st.subheader("Dados Selecionados no Gráfico:")
        selected_df = pd.DataFrame(st.session_state["selected_chart_data"])
        st.dataframe(selected_df)
        if st.button("Limpar Seleção"):
            del st.session_state["selected_chart_data"]
            st.rerun()

    # Exemplos de perguntas na barra lateral
    st.sidebar.markdown("### Exemplos de Perguntas:")
    st.sidebar.info("Qual o preço do produto 719445?")
    st.sidebar.info("Liste os produtos da categoria 'BRINQUEDOS'")
    st.sidebar.info("Mostre um gráfico de vendas para o produto 610403")

    # Entrada do usuário
    if prompt := st.chat_input("Faça uma pergunta sobre seus dados..."):
        # Input validation and sanitization
        if not prompt.strip():  # Check for empty or whitespace-only input
            st.warning("Por favor, digite uma pergunta válida.")
            return  # Stop processing if input is empty

        if len(prompt) > 500:  # Example: Limit input length to 500 characters
            st.warning(
                "Sua pergunta é muito longa. Por favor, seja mais conciso (máximo 500 caracteres)."
            )
            return  # Stop processing if input is too long

        # Adicionar mensagem do usuário ao histórico e exibir
        st.session_state[SESSION_STATE_KEYS["MESSAGES"]].append(
            {"role": ROLES["USER"], "output": prompt}
        )
        with st.chat_message(ROLES["USER"]):
            st.markdown(prompt)

        # Verificar se QueryProcessor está disponível
        query_processor = st.session_state.get(SESSION_STATE_KEYS["QUERY_PROCESSOR"])

        if query_processor is None:
            # GEMINI_API_KEY não configurada
            with st.chat_message(ROLES["ASSISTANT"]):
                st.warning(
                    "⚠️ **GEMINI_API_KEY não configurada!**\n\n"
                    "Configure a chave da API nos **Settings > Secrets** do Streamlit Cloud.\n\n"
                    "Enquanto isso, explore os **Dashboards** no menu lateral! 📊"
                )
                st.session_state[SESSION_STATE_KEYS["MESSAGES"]].append(
                    {
                        "role": ROLES["ASSISTANT"],
                        "output": "⚠️ GEMINI_API_KEY não configurada. Configure nos Settings para usar o chat."
                    }
                )
            return

        # Processar a pergunta e obter a resposta
        with st.chat_message(ROLES["ASSISTANT"]):
            loading_placeholder = st.empty()

            with loading_placeholder.container():
                st.info("⏳ Processando sua solicitação...")
                st.markdown(
                    """
                O assistente está:
                1. Analisando sua pergunta
                2. Consultando as ferramentas
                3. Gerando dados/gráficos

                **Isso pode levar 20-30 segundos...**
                """
                )

            with st.spinner("Aguarde..."):
                try:
                    response = query_processor.process_query(prompt)

                    # Limpar mensagem de carregamento
                    loading_placeholder.empty()
                except Exception as e:
                    loading_placeholder.empty()
                    st.error(f"Erro ao processar: {str(e)}")
                    st.session_state[SESSION_STATE_KEYS["MESSAGES"]].append(
                        {"role": ROLES["ASSISTANT"], "output": f"Erro: {str(e)}"}
                    )
                    return

                # Renderizar resposta (sem adicionar figura ao histórico como string)
                if response["type"] == "dataframe":
                    st.dataframe(response["output"], width='stretch')
                    # Adicionar ao histórico como string resumida
                    st.session_state[SESSION_STATE_KEYS["MESSAGES"]].append(
                        {
                            "role": ROLES["ASSISTANT"],
                            "output": (
                                f"DataFrame com " f"{len(response['output'])} linhas"
                            ),
                        }
                    )
                elif response["type"] == "chart":
                    figure = None
                    # Se a saída for uma string JSON, converter para figura
                    if isinstance(response["output"], str):
                        try:
                            figure = go.Figure(json.loads(response["output"]))
                        except Exception as e:
                            st.error(f"Erro ao decodificar o gráfico: {e}")
                    # Se já for uma figura Plotly
                    elif HAS_PLOTLY and isinstance(response["output"], go.Figure):
                        figure = response["output"]

                    if figure:
                        st.plotly_chart(figure, width='stretch', on_select=handle_chart_selection)
                        
                        # Adicionar botão de exportar como PNG
                        st.markdown(
                            get_image_download_link(
                                figure,
                                f"grafico_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                "📥 Clique aqui para baixar como PNG",
                            ),
                            unsafe_allow_html=True,
                        )

                        # Armazenar figura no histórico
                        st.session_state[SESSION_STATE_KEYS["MESSAGES"]].append(
                            {
                                "role": ROLES["ASSISTANT"],
                                "output": figure,
                                "type": "chart",
                            }
                        )
                    else:
                        # Fallback se não for figura ou JSON válido
                        st.error("Erro ao processar gráfico: formato inválido.")
                        st.session_state[SESSION_STATE_KEYS["MESSAGES"]].append(
                            {
                                "role": ROLES["ASSISTANT"],
                                "output": "Erro ao gerar gráfico: formato inválido.",
                            }
                        )
                else:
                    st.markdown(response["output"])
                    st.session_state[SESSION_STATE_KEYS["MESSAGES"]].append(
                        {"role": ROLES["ASSISTANT"], "output": response["output"]}
                    )

    st.markdown(
        f"<div class='footer'>Desenvolvido para Análise de Dados © {datetime.now().year}</div>",
        unsafe_allow_html=True,
    )


def show_admin_dashboard():
    """Exibe o painel de administração para usuários com perfil 'admin'."""
    st.markdown(
        "<h1 class='main-header'>⚙️ Painel de Administração</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p class='sub-header'>Gerencie usuários, configurações e monitore o sistema.</p>",
        unsafe_allow_html=True,
    )
    st.subheader("Funcionalidades:")
    st.write("- Gerenciamento de usuários")
    st.write("- Visualização de logs")
    st.write("- Configurações do sistema")
    st.markdown(
        f"<div class='footer'>Desenvolvido para Análise de Dados "
        f"Caçula © {datetime.now().year}</div>",
        unsafe_allow_html=True,
    )


logger = logging.getLogger(__name__)


def main():
    """Função principal que controla o fluxo da aplicação."""
    setup_logging()

    # Set correlation id
    if "correlation_id" not in st.session_state:
        st.session_state.correlation_id = str(uuid.uuid4())
    correlation_id_var.set(st.session_state.correlation_id)

    logger.info("Iniciando a aplicação Streamlit.")
    initialize_session_state()

    # --- Verificação de Autenticação e Sessão ---
    if not st.session_state.get(SESSION_STATE_KEYS["AUTHENTICATED"]):
        auth.login()
        st.stop()

    if auth.sessao_expirada():
        st.warning(
            "Sua sessão expirou por inatividade. Faça login novamente "
            "para continuar."
        )
        handle_logout()
        st.stop()

    # --- Barra Lateral e Logout ---
    username = st.session_state.get(SESSION_STATE_KEYS["USERNAME"])

    if username:
        st.sidebar.markdown(
            f"<span style='color:#2563EB;'>Bem-vindo, " f"<b>{username}</b>!</span>",
            unsafe_allow_html=True,
        )
        st.sidebar.markdown("<hr>", unsafe_allow_html=True)
        if st.sidebar.button("Sair"):
            handle_logout()

    # --- Renderização do Conteúdo Principal ---
    show_bi_assistant()


if __name__ == "__main__":
    main()
