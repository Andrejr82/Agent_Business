"""
Funções utilitárias para renderização de conteúdo no Streamlit.
Suporta gráficos Plotly, DataFrames e textos.
"""

import logging
import streamlit as st
import pandas as pd

try:
    import plotly.graph_objects as go

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

logger = logging.getLogger(__name__)


def render_output(output, message_type: str = "text"):
    """
    Renderiza diferentes tipos de output no Streamlit.

    Args:
        output: Conteúdo a renderizar (DataFrame, Figure Plotly, texto, etc)
        message_type: Tipo da mensagem ('text', 'chart', 'dataframe')
    """
    try:
        # Se é DataFrame
        if isinstance(output, pd.DataFrame):
            st.dataframe(output, use_container_width=True)
            return

        # Se é figura Plotly
        if HAS_PLOTLY and isinstance(output, go.Figure):
            st.plotly_chart(output, use_container_width=True)
            return

        # Se é dicionário Plotly JSON (estrutura com 'data' e 'layout')
        if isinstance(output, dict) and "data" in output and "layout" in output:
            try:
                if HAS_PLOTLY:
                    fig = go.Figure(output)
                    st.plotly_chart(fig, use_container_width=True)
                    return
            except Exception as e:
                logger.warning(f"Erro ao renderizar dicionário Plotly: {e}")
                st.json(output)
                return

        # Se é texto ou string
        if isinstance(output, str):
            st.markdown(output)
            return

        # Fallback: tentar renderizar como está
        if hasattr(output, "to_json"):
            # Provavelmente é uma figura Plotly
            st.plotly_chart(output, use_container_width=True)
            return

        # Último recurso: renderizar como JSON
        st.json(output)

    except Exception as e:
        logger.error(f"Erro ao renderizar output: {e}", exc_info=True)
        st.error(f"Erro ao renderizar conteúdo: {str(e)}")
        try:
            st.write(str(output))
        except Exception as e2:
            logger.error(f"Erro ao escrever output como texto: {e2}")
            st.error("Não foi possível renderizar o conteúdo.")


def render_message_history(messages, session_key: str):
    """
    Renderiza o histórico de mensagens.

    Args:
        messages: Lista de mensagens com 'role' e 'output'
        session_key: Chave de sessão para referência
    """
    for message in messages:
        role = message.get("role", "assistant")
        output = message.get("output")

        with st.chat_message(role):
            render_output(output)
