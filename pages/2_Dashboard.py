import streamlit as st
import os
import json
import plotly.graph_objects as go
from datetime import datetime

# Adiciona o diretório raiz do projeto ao sys.path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DASHBOARD_DIR = "data/dashboards"

st.markdown("<h1 class='main-header'>Dashboard</h1>", unsafe_allow_html=True)
st.markdown(
    "<div class='info-box'>Visualize todos os gráficos gerados pelo agente.</div>",
    unsafe_allow_html=True,
)

# Garantir que o diretório de dashboards exista
os.makedirs(DASHBOARD_DIR, exist_ok=True)

# Listar os arquivos de gráficos salvos
try:
    chart_files = [f for f in os.listdir(DASHBOARD_DIR) if f.endswith(".json")]
    # Ordenar por data de criação (do mais novo para o mais antigo)
    chart_files.sort(reverse=True)
except FileNotFoundError:
    chart_files = []

if not chart_files:
    st.warning(
        "Nenhum gráfico gerado ainda. Use o Agente de Negócios para gerar gráficos e eles aparecerão aqui."
    )
else:
    st.success(f"Encontrados {len(chart_files)} gráficos gerados.")

    # Opções de layout
    layout = st.radio("Layout", ["1 coluna", "2 colunas"], index=1)
    num_cols = 1 if layout == "1 coluna" else 2
    cols = st.columns(num_cols)

    # Exibir gráficos
    for i, filename in enumerate(chart_files):
        filepath = os.path.join(DASHBOARD_DIR, filename)
        with cols[i % num_cols]:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    chart_json = f.read()
                    figure = go.Figure(json.loads(chart_json))
                
                with st.container():
                    st.plotly_chart(figure, width='stretch')
                    
                    # Botão de exclusão
                    if st.button("Excluir Gráfico", key=f"delete_{filename}"):
                        os.remove(filepath)
                        st.rerun()

            except Exception as e:
                st.error(f"Erro ao carregar o gráfico {filename}: {e}")