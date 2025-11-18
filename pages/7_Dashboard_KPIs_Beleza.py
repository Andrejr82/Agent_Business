"""
Dashboard Executivo - KPIs do Setor de Beleza
==============================================

Dashboard focado em métricas críticas para o varejo de cosméticos:
- Valor de estoque
- Margem de lucro
- Ruptura de estoque
- Sazonalidade de vendas
- Top categorias e fabricantes

Autor: Agente BI Caçulinha
Data: 2024
"""

import sys
import os
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging

from core import auth
from core.session_state import SESSION_STATE_KEYS
from core.data_source_manager import get_data_manager
from ui.filtros_interativos import (
    criar_filtros_sidebar,
    aplicar_filtros,
    mostrar_estatisticas_filtro,
    criar_filtros_rapidos
)

# Configuração da página
st.set_page_config(
    page_title="KPIs Beleza",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logging
logger = logging.getLogger(__name__)

# === AUTENTICAÇÃO ===
if not st.session_state.get(SESSION_STATE_KEYS["AUTHENTICATED"]):
    auth.login()
    st.stop()

# === CABEÇALHO ===
st.markdown("# 💄 Dashboard Executivo - Setor de Beleza")
st.markdown("Acompanhe os principais indicadores do seu negócio em tempo real")
st.divider()

# === CARREGAR DADOS ===
@st.cache_data(ttl=3600)
def load_data_limpo():
    """Carrega dados limpos (preferencial) ou originais"""
    manager = get_data_manager()

    # Tentar carregar arquivo limpo primeiro
    arquivo_limpo = project_root / 'data' / 'parquet' / 'Filial_Madureira_LIMPO.parquet'

    if arquivo_limpo.exists():
        try:
            df = pd.read_parquet(arquivo_limpo)
            st.sidebar.success("✓ Dados limpos carregados")
            return df
        except Exception as e:
            logger.warning(f"Erro ao carregar dados limpos: {e}")

    # Fallback para dados originais
    df = manager.get_data()
    st.sidebar.info("ℹ️ Usando dados originais")
    return df

try:
    df_completo = load_data_limpo()
except Exception as e:
    st.error(f"❌ Erro ao carregar dados: {e}")
    st.stop()

if df_completo.empty:
    st.warning("⚠️ Nenhum dado disponível")
    st.stop()

# === FILTROS INTERATIVOS ===
filtros = criar_filtros_sidebar(df_completo)
df = aplicar_filtros(df_completo, filtros)

# Mostrar estatísticas dos filtros
mostrar_estatisticas_filtro(df_completo, df)

# === FILTROS RÁPIDOS (BOTÕES NO TOPO) ===
st.markdown("### 🔍 Análises Rápidas")

filtros_rapidos = criar_filtros_rapidos(df_completo)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("🔴 Ruptura", help=filtros_rapidos['ruptura']['descricao'], use_container_width=True):
        df = df[df['STATUS_ESTOQUE'] == 'RUPTURA'] if 'STATUS_ESTOQUE' in df.columns else df

with col2:
    if st.button("⚠️ Estoque Baixo", help=filtros_rapidos['estoque_baixo']['descricao'], use_container_width=True):
        df = df[df['STATUS_ESTOQUE'] == 'ESTOQUE_BAIXO'] if 'STATUS_ESTOQUE' in df.columns else df

with col3:
    if st.button("💰 Alta Margem", help=filtros_rapidos.get('margem_alta', {}).get('descricao', ''), use_container_width=True):
        if 'CLASSIFICACAO_MARGEM' in df.columns:
            df = df[df['CLASSIFICACAO_MARGEM'] == 'MARGEM_ALTA']

with col4:
    if st.button("📉 Baixa Margem", help=filtros_rapidos.get('margem_baixa', {}).get('descricao', ''), use_container_width=True):
        if 'CLASSIFICACAO_MARGEM' in df.columns:
            df = df[df['CLASSIFICACAO_MARGEM'] == 'MARGEM_BAIXA']

with col5:
    if st.button("🔄 Resetar", help="Limpar todos os filtros", use_container_width=True):
        st.rerun()

st.divider()

# === SEÇÃO 1: KPIS PRINCIPAIS ===
st.markdown("### 📊 Indicadores Principais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_produtos = len(df)
    total_categorias = df['GRUPO'].nunique() if 'GRUPO' in df.columns else 0
    st.metric(
        "Total de Produtos",
        f"{total_produtos:,}",
        delta=f"{total_categorias} categorias",
        help="Total de SKUs no catálogo atual"
    )

with col2:
    if 'VLR ESTOQUE VENDA' in df.columns:
        valor_estoque = df['VLR ESTOQUE VENDA'].sum()
        valor_custo = df['VLR ESTOQUE CUSTO'].sum() if 'VLR ESTOQUE CUSTO' in df.columns else 0
        margem_estoque = ((valor_estoque - valor_custo) / valor_estoque * 100) if valor_estoque > 0 else 0

        st.metric(
            "Valor Estoque (Venda)",
            f"R$ {valor_estoque:,.2f}",
            delta=f"{margem_estoque:.1f}% margem",
            help="Valor total do estoque a preço de venda"
        )

with col3:
    if 'LUCRO TOTAL %' in df.columns:
        margem_media = df['LUCRO TOTAL %'].mean()
        margem_mediana = df['LUCRO TOTAL %'].median()
        delta_margem = margem_media - margem_mediana

        st.metric(
            "Margem Média",
            f"{margem_media:.1f}%",
            delta=f"{delta_margem:.1f}% vs mediana",
            delta_color="normal",
            help="Margem média de lucro de todos os produtos"
        )

with col4:
    if 'SALDO' in df.columns:
        produtos_ruptura = len(df[df['SALDO'] <= 0])
        pct_ruptura = (produtos_ruptura / total_produtos * 100) if total_produtos > 0 else 0

        st.metric(
            "Produtos em Ruptura",
            produtos_ruptura,
            delta=f"{pct_ruptura:.1f}%",
            delta_color="inverse",
            help="Produtos com estoque zerado ou negativo"
        )

st.divider()

# === SEÇÃO 2: ABAS DE ANÁLISE ===
tab1, tab2, tab3, tab4 = st.tabs([
    "📦 Categorias",
    "💰 Margem & Rentabilidade",
    "📈 Sazonalidade",
    "🏭 Fabricantes"
])

# === TAB 1: CATEGORIAS ===
with tab1:
    st.markdown("#### Top 10 Categorias por Valor de Estoque")

    if 'GRUPO' in df.columns and 'VLR ESTOQUE VENDA' in df.columns:
        top_categorias = df.groupby('GRUPO').agg({
            'VLR ESTOQUE VENDA': 'sum',
            'ITEM': 'count',
            'LUCRO TOTAL %': 'mean'
        }).sort_values('VLR ESTOQUE VENDA', ascending=False).head(10)

        # Renomear colunas
        top_categorias.columns = ['Valor Estoque', 'Qtd Produtos', 'Margem Média']

        # Gráfico de barras horizontais
        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=top_categorias.index,
            x=top_categorias['Valor Estoque'],
            orientation='h',
            text=top_categorias['Valor Estoque'].apply(lambda x: f'R$ {x:,.0f}'),
            textposition='auto',
            marker=dict(
                color=top_categorias['Margem Média'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Margem %")
            ),
            hovertemplate=(
                '<b>%{y}</b><br>' +
                'Valor Estoque: R$ %{x:,.2f}<br>' +
                '<extra></extra>'
            )
        ))

        fig.update_layout(
            height=500,
            xaxis_title="Valor de Estoque (R$)",
            yaxis_title="Categoria",
            template="plotly_white",
            hovermode='y unified'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tabela detalhada
        with st.expander("📋 Ver tabela detalhada"):
            st.dataframe(
                top_categorias.style.format({
                    'Valor Estoque': 'R$ {:,.2f}',
                    'Margem Média': '{:.2f}%'
                }),
                use_container_width=True
            )
    else:
        st.info("Dados de categorias não disponíveis")

# === TAB 2: MARGEM ===
with tab2:
    col_margem1, col_margem2 = st.columns(2)

    with col_margem1:
        st.markdown("#### Distribuição de Margem")

        if 'LUCRO TOTAL %' in df.columns:
            # Histograma de distribuição de margem
            fig = go.Figure()

            fig.add_trace(go.Histogram(
                x=df['LUCRO TOTAL %'],
                nbinsx=30,
                marker_color='#FF69B4',
                opacity=0.7,
                name='Distribuição'
            ))

            # Adicionar linhas de referência
            margem_media = df['LUCRO TOTAL %'].mean()
            margem_mediana = df['LUCRO TOTAL %'].median()

            fig.add_vline(
                x=margem_media,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Média: {margem_media:.1f}%",
                annotation_position="top"
            )

            fig.add_vline(
                x=margem_mediana,
                line_dash="dot",
                line_color="blue",
                annotation_text=f"Mediana: {margem_mediana:.1f}%",
                annotation_position="bottom"
            )

            fig.update_layout(
                height=400,
                xaxis_title="Margem de Lucro (%)",
                yaxis_title="Número de Produtos",
                template="plotly_white",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

    with col_margem2:
        st.markdown("#### Margem por Categoria (Top 10)")

        if 'GRUPO' in df.columns and 'LUCRO TOTAL %' in df.columns:
            # Box plot de margem por categoria
            top_10_grupos = df['GRUPO'].value_counts().head(10).index
            df_top = df[df['GRUPO'].isin(top_10_grupos)]

            fig = go.Figure()

            for grupo in top_10_grupos:
                df_grupo = df_top[df_top['GRUPO'] == grupo]
                fig.add_trace(go.Box(
                    y=df_grupo['LUCRO TOTAL %'],
                    name=grupo,
                    boxmean='sd',
                    marker_color='#FF69B4'
                ))

            fig.update_layout(
                height=400,
                yaxis_title="Margem (%)",
                xaxis_title="Categoria",
                template="plotly_white",
                showlegend=False,
                xaxis=dict(tickangle=-45)
            )

            st.plotly_chart(fig, use_container_width=True)

    # Produtos com maior e menor margem
    st.markdown("#### 🏆 Top 5 Produtos - Maior e Menor Margem")

    col_top, col_bottom = st.columns(2)

    with col_top:
        st.markdown("**✅ Maior Margem**")
        if 'LUCRO TOTAL %' in df.columns and 'DESCRIÇÃO' in df.columns:
            top_margem = df.nlargest(5, 'LUCRO TOTAL %')[['DESCRIÇÃO', 'LUCRO TOTAL %', 'VENDA UNIT R$', 'SALDO']]
            st.dataframe(
                top_margem.style.format({
                    'LUCRO TOTAL %': '{:.2f}%',
                    'VENDA UNIT R$': 'R$ {:.2f}'
                }),
                hide_index=True,
                use_container_width=True
            )

    with col_bottom:
        st.markdown("**❌ Menor Margem**")
        if 'LUCRO TOTAL %' in df.columns and 'DESCRIÇÃO' in df.columns:
            bottom_margem = df.nsmallest(5, 'LUCRO TOTAL %')[['DESCRIÇÃO', 'LUCRO TOTAL %', 'VENDA UNIT R$', 'SALDO']]
            st.dataframe(
                bottom_margem.style.format({
                    'LUCRO TOTAL %': '{:.2f}%',
                    'VENDA UNIT R$': 'R$ {:.2f}'
                }),
                hide_index=True,
                use_container_width=True
            )

# === TAB 3: SAZONALIDADE ===
with tab3:
    st.markdown("#### Vendas Mensais - Análise de Sazonalidade")

    # Verificar se temos dados de vendas mensais
    meses = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
    colunas_vendas = [f'VENDA QTD {mes}' for mes in meses]

    if all(col in df.columns for col in colunas_vendas):
        vendas_mensais = df[colunas_vendas].sum()

        # Gráfico de linha com área
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=meses,
            y=vendas_mensais.values,
            mode='lines+markers',
            name='Vendas',
            line=dict(color='#FF69B4', width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor='rgba(255, 105, 180, 0.2)',
            hovertemplate='<b>%{x}</b><br>Vendas: %{y:,.0f}<extra></extra>'
        ))

        # Linha de média
        media_vendas = vendas_mensais.mean()
        fig.add_hline(
            y=media_vendas,
            line_dash="dash",
            line_color="gray",
            annotation_text=f"Média: {media_vendas:,.0f}",
            annotation_position="right"
        )

        fig.update_layout(
            height=400,
            xaxis_title="Mês",
            yaxis_title="Quantidade Vendida",
            template="plotly_white",
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Análise de pico e baixa
        col_pico, col_baixa, col_variacao = st.columns(3)

        mes_pico_idx = vendas_mensais.argmax()
        mes_baixa_idx = vendas_mensais.argmin()
        mes_pico = meses[mes_pico_idx]
        mes_baixa = meses[mes_baixa_idx]

        with col_pico:
            st.success(f"🔥 **Pico de Vendas**\n\n{mes_pico}: {vendas_mensais.max():,.0f} unidades")

        with col_baixa:
            st.warning(f"📉 **Menor Venda**\n\n{mes_baixa}: {vendas_mensais.min():,.0f} unidades")

        with col_variacao:
            variacao = ((vendas_mensais.max() - vendas_mensais.min()) / vendas_mensais.min() * 100)
            st.info(f"📊 **Variação**\n\n{variacao:.1f}% entre pico e baixa")

        # Índice de sazonalidade
        indice_sazonalidade = (vendas_mensais.std() / vendas_mensais.mean()) * 100

        if indice_sazonalidade < 20:
            interpretacao = "Vendas estáveis ao longo do ano"
            cor = "blue"
        elif indice_sazonalidade < 40:
            interpretacao = "Sazonalidade moderada"
            cor = "orange"
        else:
            interpretacao = "Sazonalidade forte - planejar estoque com atenção"
            cor = "red"

        st.markdown(f"**Índice de Sazonalidade:** :{cor}[{indice_sazonalidade:.1f}%] - {interpretacao}")

    else:
        st.info("Dados de sazonalidade não disponíveis")

# === TAB 4: FABRICANTES ===
with tab4:
    st.markdown("#### Top Fabricantes por Valor de Estoque")

    if 'FABRICANTE' in df.columns and 'VLR ESTOQUE VENDA' in df.columns:
        top_fabricantes = df.groupby('FABRICANTE').agg({
            'VLR ESTOQUE VENDA': 'sum',
            'ITEM': 'count',
            'LUCRO TOTAL %': 'mean',
            'SALDO': 'sum'
        }).sort_values('VLR ESTOQUE VENDA', ascending=False).head(15)

        top_fabricantes.columns = ['Valor Estoque', 'Qtd Produtos', 'Margem Média', 'Estoque Total']

        # Gráfico de pizza + barras
        col_pizza, col_barras = st.columns(2)

        with col_pizza:
            st.markdown("**Participação no Valor de Estoque**")

            fig = go.Figure(data=[go.Pie(
                labels=top_fabricantes.index,
                values=top_fabricantes['Valor Estoque'],
                hole=0.4,
                marker=dict(colors=['#FF69B4', '#FF1493', '#C71585', '#DB7093', '#FFB6C1'] * 3),
                textposition='auto',
                textinfo='label+percent'
            )])

            fig.update_layout(
                height=400,
                template="plotly_white",
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

        with col_barras:
            st.markdown("**Quantidade de Produtos por Fabricante**")

            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=top_fabricantes.index,
                y=top_fabricantes['Qtd Produtos'],
                marker_color='#FF69B4',
                text=top_fabricantes['Qtd Produtos'],
                textposition='auto'
            ))

            fig.update_layout(
                height=400,
                xaxis_title="Fabricante",
                yaxis_title="Quantidade de Produtos",
                template="plotly_white",
                xaxis=dict(tickangle=-45)
            )

            st.plotly_chart(fig, use_container_width=True)

        # Tabela detalhada
        with st.expander("📋 Ver tabela completa de fabricantes"):
            st.dataframe(
                top_fabricantes.style.format({
                    'Valor Estoque': 'R$ {:,.2f}',
                    'Margem Média': '{:.2f}%',
                    'Estoque Total': '{:,.0f}'
                }),
                use_container_width=True
            )

# === FOOTER ===
st.divider()
st.markdown(
    f"<div style='text-align: center; color: gray;'>Dashboard atualizado em tempo real | "
    f"Dados: {len(df)} produtos</div>",
    unsafe_allow_html=True
)
