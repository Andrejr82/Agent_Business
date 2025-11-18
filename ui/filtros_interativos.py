"""
Componentes de Filtros Interativos - Setor de Beleza
=====================================================

Filtros visuais na sidebar do Streamlit para exploração interativa de dados.

Funcionalidades:
- Filtro de categorias (multi-select)
- Filtro de fabricantes (multi-select)
- Slider de margem mínima
- Range de estoque
- Toggles de status (em estoque, com vendas)

Uso:
    from ui.filtros_interativos import criar_filtros_sidebar, aplicar_filtros

    filtros = criar_filtros_sidebar(df)
    df_filtrado = aplicar_filtros(df, filtros)
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def criar_filtros_sidebar(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Cria filtros interativos na sidebar do Streamlit

    Args:
        df: DataFrame com dados completos

    Returns:
        dict com filtros selecionados pelo usuário
    """
    if df.empty:
        st.sidebar.warning("⚠️ Nenhum dado disponível para filtrar")
        return {}

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Filtros de Dados")
    st.sidebar.caption("Use os filtros abaixo para explorar seus dados")

    filtros = {}

    # === FILTRO 1: CATEGORIAS (GRUPO) ===
    if 'GRUPO' in df.columns:
        with st.sidebar.expander("📦 **Categorias**", expanded=False):
            # Ordenar por quantidade de produtos
            grupos_contagem = df['GRUPO'].value_counts()
            grupos_ordenados = grupos_contagem.index.tolist()

            # Mostrar top 20 por padrão (pode expandir)
            grupos_top20 = grupos_ordenados[:20]

            filtros['grupos'] = st.multiselect(
                "Selecione categorias",
                options=grupos_top20,
                default=None,
                help=f"Total de categorias disponíveis: {len(grupos_ordenados)}"
            )

            # Opção para ver todas as categorias
            if st.checkbox("Mostrar todas as categorias", key="show_all_grupos"):
                filtros['grupos'] = st.multiselect(
                    "Todas as categorias",
                    options=grupos_ordenados,
                    default=filtros['grupos'],
                    key="grupos_todos"
                )

            # Estatística
            if filtros['grupos']:
                produtos_selecionados = len(df[df['GRUPO'].isin(filtros['grupos'])])
                st.caption(f"✓ {produtos_selecionados} produtos nessas categorias")

    # === FILTRO 2: FABRICANTES ===
    if 'FABRICANTE' in df.columns:
        with st.sidebar.expander("🏭 **Fabricantes**", expanded=False):
            # Top 20 fabricantes por número de produtos
            fabricantes_contagem = df['FABRICANTE'].value_counts()
            fabricantes_top = fabricantes_contagem.head(20).index.tolist()

            filtros['fabricantes'] = st.multiselect(
                "Selecione fabricantes",
                options=fabricantes_top,
                default=None,
                help=f"Mostrando top 20 de {len(fabricantes_contagem)} fabricantes"
            )

            if filtros['fabricantes']:
                produtos_selecionados = len(df[df['FABRICANTE'].isin(filtros['fabricantes'])])
                st.caption(f"✓ {produtos_selecionados} produtos desses fabricantes")

    # === FILTRO 3: MARGEM ===
    if 'LUCRO TOTAL %' in df.columns:
        with st.sidebar.expander("💰 **Margem de Lucro**", expanded=False):
            margem_min = float(df['LUCRO TOTAL %'].min())
            margem_max = float(df['LUCRO TOTAL %'].max())
            margem_media = float(df['LUCRO TOTAL %'].mean())

            st.caption(f"Margem média atual: **{margem_media:.1f}%**")

            filtros['margem_minima'] = st.slider(
                "Margem mínima (%)",
                min_value=margem_min,
                max_value=margem_max,
                value=margem_min,
                step=1.0,
                help="Produtos com margem >= este valor"
            )

            if filtros['margem_minima'] > margem_min:
                produtos_filtrados = len(df[df['LUCRO TOTAL %'] >= filtros['margem_minima']])
                st.caption(f"✓ {produtos_filtrados} produtos com margem >= {filtros['margem_minima']:.1f}%")

    # === FILTRO 4: ESTOQUE ===
    if 'SALDO' in df.columns:
        with st.sidebar.expander("📊 **Estoque**", expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                filtros['estoque_min'] = st.number_input(
                    "Mínimo",
                    min_value=0,
                    value=0,
                    step=1,
                    help="Estoque mínimo"
                )

            with col2:
                estoque_max_total = int(df['SALDO'].max())
                filtros['estoque_max'] = st.number_input(
                    "Máximo",
                    min_value=0,
                    value=estoque_max_total,
                    step=10,
                    help="Estoque máximo"
                )

            if filtros['estoque_min'] > 0 or filtros['estoque_max'] < estoque_max_total:
                produtos_filtrados = len(df[
                    (df['SALDO'] >= filtros['estoque_min']) &
                    (df['SALDO'] <= filtros['estoque_max'])
                ])
                st.caption(f"✓ {produtos_filtrados} produtos nesse range")

    # === FILTRO 5: STATUS DO PRODUTO ===
    with st.sidebar.expander("✅ **Status**", expanded=True):
        filtros['apenas_em_estoque'] = st.checkbox(
            "Apenas em estoque (SALDO > 0)",
            value=False,
            help="Mostra apenas produtos com estoque disponível"
        )

        if 'VENDAS_TOTAL_ANO' in df.columns:
            filtros['apenas_com_vendas'] = st.checkbox(
                "Apenas com vendas no ano",
                value=False,
                help="Mostra apenas produtos que venderam"
            )

        if 'CLASSIFICACAO_MARGEM' in df.columns:
            classificacoes = df['CLASSIFICACAO_MARGEM'].unique().tolist()
            if 'SEM_DADOS' in classificacoes:
                classificacoes.remove('SEM_DADOS')

            filtros['classificacao_margem'] = st.multiselect(
                "Classificação de margem",
                options=classificacoes,
                default=None,
                help="Filtrar por classificação de margem"
            )

        if 'STATUS_ESTOQUE' in df.columns:
            status_opcoes = df['STATUS_ESTOQUE'].unique().tolist()
            filtros['status_estoque'] = st.multiselect(
                "Status do estoque",
                options=status_opcoes,
                default=None,
                help="Filtrar por status do estoque"
            )

    # === BOTÃO LIMPAR FILTROS ===
    st.sidebar.markdown("---")
    col_reset1, col_reset2 = st.sidebar.columns([2, 1])

    with col_reset1:
        if st.button("🔄 Limpar Filtros", use_container_width=True):
            st.rerun()

    with col_reset2:
        # Contador de filtros ativos
        filtros_ativos = sum([
            bool(filtros.get('grupos')),
            bool(filtros.get('fabricantes')),
            filtros.get('margem_minima', 0) > df['LUCRO TOTAL %'].min() if 'LUCRO TOTAL %' in df.columns else False,
            filtros.get('apenas_em_estoque', False),
            filtros.get('apenas_com_vendas', False),
            bool(filtros.get('classificacao_margem')),
            bool(filtros.get('status_estoque'))
        ])

        if filtros_ativos > 0:
            st.metric("Ativos", filtros_ativos)

    return filtros


def aplicar_filtros(df: pd.DataFrame, filtros: Dict[str, Any]) -> pd.DataFrame:
    """
    Aplica filtros ao DataFrame

    Args:
        df: DataFrame original
        filtros: Dicionário com filtros selecionados

    Returns:
        DataFrame filtrado
    """
    if df.empty or not filtros:
        return df

    df_filtrado = df.copy()
    total_original = len(df_filtrado)

    # Aplicar filtro de categorias
    if filtros.get('grupos'):
        df_filtrado = df_filtrado[df_filtrado['GRUPO'].isin(filtros['grupos'])]
        logger.info(f"Filtro categorias: {len(df_filtrado)} produtos")

    # Aplicar filtro de fabricantes
    if filtros.get('fabricantes'):
        df_filtrado = df_filtrado[df_filtrado['FABRICANTE'].isin(filtros['fabricantes'])]
        logger.info(f"Filtro fabricantes: {len(df_filtrado)} produtos")

    # Aplicar filtro de margem
    if 'margem_minima' in filtros and 'LUCRO TOTAL %' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['LUCRO TOTAL %'] >= filtros['margem_minima']]
        logger.info(f"Filtro margem: {len(df_filtrado)} produtos")

    # Aplicar filtro de range de estoque
    if 'estoque_min' in filtros and 'estoque_max' in filtros and 'SALDO' in df_filtrado.columns:
        df_filtrado = df_filtrado[
            (df_filtrado['SALDO'] >= filtros['estoque_min']) &
            (df_filtrado['SALDO'] <= filtros['estoque_max'])
        ]
        logger.info(f"Filtro estoque: {len(df_filtrado)} produtos")

    # Aplicar filtro de apenas em estoque
    if filtros.get('apenas_em_estoque') and 'SALDO' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['SALDO'] > 0]
        logger.info(f"Filtro em estoque: {len(df_filtrado)} produtos")

    # Aplicar filtro de apenas com vendas
    if filtros.get('apenas_com_vendas') and 'VENDAS_TOTAL_ANO' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['VENDAS_TOTAL_ANO'] > 0]
        logger.info(f"Filtro com vendas: {len(df_filtrado)} produtos")

    # Aplicar filtro de classificação de margem
    if filtros.get('classificacao_margem') and 'CLASSIFICACAO_MARGEM' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['CLASSIFICACAO_MARGEM'].isin(filtros['classificacao_margem'])]
        logger.info(f"Filtro classificação margem: {len(df_filtrado)} produtos")

    # Aplicar filtro de status de estoque
    if filtros.get('status_estoque') and 'STATUS_ESTOQUE' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['STATUS_ESTOQUE'].isin(filtros['status_estoque'])]
        logger.info(f"Filtro status estoque: {len(df_filtrado)} produtos")

    # Log do resultado final
    produtos_removidos = total_original - len(df_filtrado)
    percentual_filtrado = (produtos_removidos / total_original * 100) if total_original > 0 else 0

    logger.info(
        f"Filtros aplicados: {total_original} → {len(df_filtrado)} produtos "
        f"({percentual_filtrado:.1f}% filtrado)"
    )

    return df_filtrado


def mostrar_estatisticas_filtro(df_original: pd.DataFrame, df_filtrado: pd.DataFrame):
    """
    Mostra estatísticas comparativas antes/depois do filtro

    Args:
        df_original: DataFrame completo
        df_filtrado: DataFrame após filtros
    """
    if df_original.empty:
        return

    total_original = len(df_original)
    total_filtrado = len(df_filtrado)
    percentual = (total_filtrado / total_original * 100) if total_original > 0 else 0

    # Mostrar apenas se houver filtros aplicados
    if total_filtrado < total_original:
        st.info(
            f"📊 **Filtros Ativos:** Mostrando {total_filtrado:,} de {total_original:,} produtos ({percentual:.1f}%)"
        )

        # Estatísticas detalhadas (opcional, em expander)
        with st.expander("📈 Ver estatísticas detalhadas"):
            col1, col2, col3 = st.columns(3)

            with col1:
                if 'VLR ESTOQUE VENDA' in df_filtrado.columns:
                    valor_original = df_original['VLR ESTOQUE VENDA'].sum()
                    valor_filtrado = df_filtrado['VLR ESTOQUE VENDA'].sum()
                    st.metric(
                        "Valor Estoque",
                        f"R$ {valor_filtrado:,.2f}",
                        delta=f"{valor_filtrado - valor_original:,.2f}",
                        delta_color="off"
                    )

            with col2:
                if 'LUCRO TOTAL %' in df_filtrado.columns:
                    margem_original = df_original['LUCRO TOTAL %'].mean()
                    margem_filtrada = df_filtrado['LUCRO TOTAL %'].mean()
                    st.metric(
                        "Margem Média",
                        f"{margem_filtrada:.1f}%",
                        delta=f"{margem_filtrada - margem_original:.1f}%",
                        delta_color="normal"
                    )

            with col3:
                if 'VENDAS_TOTAL_ANO' in df_filtrado.columns:
                    vendas_original = df_original['VENDAS_TOTAL_ANO'].sum()
                    vendas_filtrada = df_filtrado['VENDAS_TOTAL_ANO'].sum()
                    st.metric(
                        "Vendas Totais",
                        f"{vendas_filtrada:,.0f}",
                        delta=f"{vendas_filtrada - vendas_original:,.0f}",
                        delta_color="off"
                    )


def salvar_filtros_favoritos(filtros: Dict[str, Any], nome: str):
    """
    Salva combinação de filtros como favorito

    Args:
        filtros: Dicionário de filtros
        nome: Nome do filtro favorito
    """
    if 'filtros_favoritos' not in st.session_state:
        st.session_state['filtros_favoritos'] = {}

    st.session_state['filtros_favoritos'][nome] = filtros
    st.success(f"✓ Filtro '{nome}' salvo nos favoritos!")


def carregar_filtro_favorito(nome: str) -> Dict[str, Any]:
    """
    Carrega filtro favorito salvo

    Args:
        nome: Nome do filtro favorito

    Returns:
        Dicionário com filtros
    """
    if 'filtros_favoritos' not in st.session_state:
        st.session_state['filtros_favoritos'] = {}

    return st.session_state['filtros_favoritos'].get(nome, {})


def criar_filtros_rapidos(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Cria filtros pré-configurados para análises comuns

    Args:
        df: DataFrame completo

    Returns:
        Dicionário com filtros rápidos
    """
    filtros_rapidos = {}

    # Filtro: Produtos em ruptura
    filtros_rapidos['ruptura'] = {
        'status_estoque': ['RUPTURA'],
        'nome': '🔴 Produtos em Ruptura',
        'descricao': 'Produtos com estoque zerado'
    }

    # Filtro: Margem alta
    if 'LUCRO TOTAL %' in df.columns:
        margem_alta = df['LUCRO TOTAL %'].quantile(0.75)
        filtros_rapidos['margem_alta'] = {
            'margem_minima': margem_alta,
            'nome': '💰 Margem Alta',
            'descricao': f'Produtos com margem >= {margem_alta:.1f}%'
        }

    # Filtro: Margem baixa
    if 'LUCRO TOTAL %' in df.columns:
        margem_baixa = df['LUCRO TOTAL %'].quantile(0.25)
        filtros_rapidos['margem_baixa'] = {
            'margem_minima': 0,
            'classificacao_margem': ['MARGEM_BAIXA'],
            'nome': '📉 Margem Baixa',
            'descricao': 'Produtos com margem abaixo da média'
        }

    # Filtro: Estoque baixo
    filtros_rapidos['estoque_baixo'] = {
        'status_estoque': ['ESTOQUE_BAIXO'],
        'nome': '⚠️ Estoque Baixo',
        'descricao': 'Produtos com estoque crítico'
    }

    # Filtro: Produtos sem venda
    if 'VENDAS_TOTAL_ANO' in df.columns:
        filtros_rapidos['sem_vendas'] = {
            'apenas_em_estoque': True,
            'nome': '🛑 Sem Vendas',
            'descricao': 'Produtos em estoque mas sem venda no ano'
        }

    return filtros_rapidos


# Exemplo de uso
if __name__ == '__main__':
    print("Componente de Filtros Interativos")
    print("Use em streamlit_app.py:")
    print()
    print("  from ui.filtros_interativos import criar_filtros_sidebar, aplicar_filtros")
    print()
    print("  filtros = criar_filtros_sidebar(df)")
    print("  df_filtrado = aplicar_filtros(df, filtros)")
