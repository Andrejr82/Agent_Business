"""
Ferramentas para geração de gráficos e visualizações.
Integração com Plotly para análise visual de dados.
"""

import logging
from typing import Dict, Any
import pandas as pd
import plotly.graph_objects as go
from langchain_core.tools import tool
from core.data_source_manager import get_data_manager

logger = logging.getLogger(__name__)


def _get_theme_template() -> str:
    """Retorna o template de tema padrão."""
    return "plotly_white"


def _apply_chart_customization(
    fig: go.Figure,
    title: str = "",
    show_legend: bool = True
) -> go.Figure:
    """
    Aplica customizações padrão aos gráficos.
    
    Args:
        fig: Figura Plotly
        title: Título do gráfico
        show_legend: Se mostra legenda
        
    Returns:
        Figura com customizações aplicadas
    """
    fig.update_layout(
        template=_get_theme_template(),
        title={
            "text": title,
            "x": 0.5,
            "xanchor": "center",
            "font": {"size": 20, "color": "#1f77b4"}
        },
        hovermode="x unified",
        font=dict(size=11, family="Arial"),
        margin=dict(l=50, r=50, t=80, b=50),
        showlegend=show_legend,
        height=500,
        paper_bgcolor="rgba(240, 240, 240, 0.5)",
        plot_bgcolor="rgba(255, 255, 255, 0.9)",
    )
    return fig


def _export_chart_to_json(fig: go.Figure) -> str:
    """
    Exporta figura como JSON para Streamlit.
    
    Args:
        fig: Figura Plotly
        
    Returns:
        JSON string da figura
    """
    return fig.to_json()


@tool
def gerar_grafico_vendas_por_categoria(
    limite: int = 10,
    ordenar_por: str = "descendente"
) -> Dict[str, Any]:
    """
    Gera gráfico de barras com vendas por categoria.
    Útil para análise de categorias de produtos.
    
    Args:
        limite: Número máximo de categorias a mostrar
        ordenar_por: "ascendente" ou "descendente"
        
    Returns:
        Dicionário com gráfico Plotly e dados
    """
    logger.info(f"Gerando gráfico de vendas por categoria (limite={limite})")
    
    try:
        manager = get_data_manager()
        
        # Tentar obter dados de qualquer tabela
        df = None
        tabelas = ['admmatao', 'ADMAT', 'ADMAT_REBUILT', 'master_catalog']
        
        for tabela in tabelas:
            try:
                df = manager.get_data(tabela, limit=5000)
                if not df.empty and 'categoria' in df.columns:
                    logger.info(f"Dados carregados de {tabela}")
                    break
            except Exception as e:
                logger.debug(f"Erro ao tentar {tabela}: {e}")
                continue
        
        if df is None or df.empty:
            return {
                "status": "error",
                "message": "Não foi possível carregar dados para gerar gráfico"
            }
        
        # Normalizar nome da coluna categoria
        categoria_col = None
        for col in df.columns:
            if 'categ' in col.lower():
                categoria_col = col
                break
        
        if not categoria_col:
            return {
                "status": "error",
                "message": "Coluna de categoria não encontrada"
            }
        
        # Contar por categoria
        vendas_por_categoria = df[categoria_col].value_counts().head(limite)
        
        if ordenar_por == "ascendente":
            vendas_por_categoria = vendas_por_categoria.sort_values()
        
        # Criar gráfico
        fig = go.Figure(data=[
            go.Bar(
                y=vendas_por_categoria.index,
                x=vendas_por_categoria.values,
                orientation='h',
                marker=dict(
                    color=vendas_por_categoria.values,
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Quantidade")
                ),
                hovertemplate="<b>%{y}</b><br>Quantidade: %{x}<extra></extra>"
            )
        ])
        
        fig = _apply_chart_customization(
            fig,
            title=f"Vendas por Categoria (Top {limite})"
        )
        
        fig.update_xaxes(title_text="Quantidade de Produtos")
        fig.update_yaxes(title_text="Categoria")
        
        return {
            "status": "success",
            "chart_type": "bar_horizontal",
            "chart_data": _export_chart_to_json(fig),
            "summary": {
                "total_categorias": len(vendas_por_categoria),
                "categorias": vendas_por_categoria.to_dict(),
                "total_itens": int(vendas_por_categoria.sum())
            }
        }
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico de vendas: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro ao gerar gráfico: {str(e)}"
        }


@tool
def gerar_grafico_estoque_por_produto(
    limite: int = 15,
    minimo_estoque: int = 0
) -> Dict[str, Any]:
    """
    Gera gráfico de estoque disponível por produto.
    Mostra produtos com mais estoque em destaque.
    
    Args:
        limite: Número máximo de produtos a mostrar
        minimo_estoque: Estoque mínimo para incluir
        
    Returns:
        Dicionário com gráfico e dados de estoque
    """
    logger.info(f"Gerando gráfico de estoque por produto (limite={limite})")
    
    try:
        manager = get_data_manager()
        
        df = None
        tabelas = ['admmatao', 'ADMAT', 'ADMAT_REBUILT', 'master_catalog']
        
        for tabela in tabelas:
            try:
                df = manager.get_data(tabela, limit=5000)
                if not df.empty:
                    logger.info(f"Dados carregados de {tabela}")
                    break
            except Exception as e:
                logger.debug(f"Erro ao tentar {tabela}: {e}")
                continue
        
        if df is None or df.empty:
            return {
                "status": "error",
                "message": "Não foi possível carregar dados"
            }
        
        # Encontrar coluna de estoque
        estoque_col = None
        for col in df.columns:
            if 'est' in col.lower() or 'stock' in col.lower() or 'quantidade' in col.lower():
                estoque_col = col
                break
        
        # Encontrar coluna de nome/produto
        nome_col = None
        for col in df.columns:
            if 'nome' in col.lower() or 'product' in col.lower() or 'descricao' in col.lower():
                nome_col = col
                break
        
        if not estoque_col or not nome_col:
            return {
                "status": "error",
                "message": "Colunas de estoque e/ou nome não encontradas"
            }
        
        # Preparar dados
        df_estoque = df[[nome_col, estoque_col]].copy()
        df_estoque = df_estoque[df_estoque[estoque_col] >= minimo_estoque]
        df_estoque = df_estoque.sort_values(estoque_col, ascending=False).head(limite)
        
        # Criar gráfico
        fig = go.Figure(data=[
            go.Bar(
                x=df_estoque[nome_col],
                y=df_estoque[estoque_col],
                marker=dict(
                    color=df_estoque[estoque_col],
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="Estoque")
                ),
                hovertemplate="<b>%{x}</b><br>Estoque: %{y}<extra></extra>"
            )
        ])
        
        fig.update_layout(
            xaxis_tickangle=-45,
            height=600,
        )
        
        fig = _apply_chart_customization(
            fig,
            title=f"Estoque Disponível por Produto (Top {limite})"
        )
        
        fig.update_xaxes(title_text="Produto")
        fig.update_yaxes(title_text="Quantidade em Estoque")
        
        return {
            "status": "success",
            "chart_type": "bar_vertical",
            "chart_data": _export_chart_to_json(fig),
            "summary": {
                "total_produtos": len(df_estoque),
                "estoque_total": int(df_estoque[estoque_col].sum()),
                "estoque_medio": float(df_estoque[estoque_col].mean()),
                "estoque_maximo": int(df_estoque[estoque_col].max())
            }
        }
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico de estoque: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro ao gerar gráfico: {str(e)}"
        }


@tool
def gerar_comparacao_precos_categorias() -> Dict[str, Any]:
    """
    Gera gráfico de comparação de preços médios por categoria.
    Útil para análise de precificação.
    
    Returns:
        Dicionário com gráfico comparativo de preços
    """
    logger.info("Gerando gráfico de comparação de preços")
    
    try:
        manager = get_data_manager()
        
        df = None
        tabelas = ['admmatao', 'ADMAT', 'ADMAT_REBUILT', 'master_catalog']
        
        for tabela in tabelas:
            try:
                df = manager.get_data(tabela, limit=5000)
                if not df.empty:
                    logger.info(f"Dados carregados de {tabela}")
                    break
            except Exception as e:
                logger.debug(f"Erro ao tentar {tabela}: {e}")
                continue
        
        if df is None or df.empty:
            return {
                "status": "error",
                "message": "Não foi possível carregar dados"
            }
        
        # Encontrar colunas
        categoria_col = None
        preco_col = None
        
        for col in df.columns:
            if 'categ' in col.lower():
                categoria_col = col
            if 'preco' in col.lower() or 'price' in col.lower():
                preco_col = col
        
        if not categoria_col or not preco_col:
            return {
                "status": "error",
                "message": "Colunas de categoria e/ou preço não encontradas"
            }
        
        # Calcular preço médio por categoria
        preco_medio = df.groupby(categoria_col)[preco_col].agg(['mean', 'min', 'max', 'count']).reset_index()
        preco_medio = preco_medio.sort_values('mean', ascending=False)
        
        # Criar gráfico com múltiplas séries
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=preco_medio[categoria_col],
            y=preco_medio['mean'],
            name='Preço Médio',
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Scatter(
            x=preco_medio[categoria_col],
            y=preco_medio['max'],
            mode='markers+lines',
            name='Preço Máximo',
            line=dict(dash='dash', color='red'),
            marker=dict(size=8)
        ))
        
        fig = _apply_chart_customization(
            fig,
            title="Comparação de Preços por Categoria",
            show_legend=True
        )
        
        fig.update_xaxes(title_text="Categoria")
        fig.update_yaxes(title_text="Preço (R$)")
        fig.update_layout(xaxis_tickangle=-45, height=500)
        
        return {
            "status": "success",
            "chart_type": "bar_line_combo",
            "chart_data": _export_chart_to_json(fig),
            "summary": {
                "categorias": len(preco_medio),
                "preco_medio_geral": float(df[preco_col].mean()),
                "preco_maximo": float(preco_medio['max'].max()),
                "preco_minimo": float(preco_medio['min'].min()),
                "categorias_data": preco_medio.to_dict('records')
            }
        }
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico de comparação: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro ao gerar gráfico: {str(e)}"
        }


@tool
def gerar_analise_distribuicao_estoque() -> Dict[str, Any]:
    """
    Gera histograma e box plot da distribuição de estoque.
    Útil para análise estatística de níveis de estoque.
    
    Returns:
        Dicionário com gráficos de distribuição
    """
    logger.info("Gerando análise de distribuição de estoque")
    
    try:
        manager = get_data_manager()
        
        df = None
        tabelas = ['admmatao', 'ADMAT', 'ADMAT_REBUILT', 'master_catalog']
        
        for tabela in tabelas:
            try:
                df = manager.get_data(tabela, limit=5000)
                if not df.empty:
                    logger.info(f"Dados carregados de {tabela}")
                    break
            except Exception as e:
                logger.debug(f"Erro ao tentar {tabela}: {e}")
                continue
        
        if df is None or df.empty:
            return {
                "status": "error",
                "message": "Não foi possível carregar dados"
            }
        
        # Encontrar coluna de estoque
        estoque_col = None
        for col in df.columns:
            if 'est' in col.lower() or 'stock' in col.lower():
                estoque_col = col
                break
        
        if not estoque_col:
            return {
                "status": "error",
                "message": "Coluna de estoque não encontrada"
            }
        
        # Converter para numérico
        df[estoque_col] = pd.to_numeric(df[estoque_col], errors='coerce')
        df = df.dropna(subset=[estoque_col])
        
        # Criar subplots
        from plotly.subplots import make_subplots
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Distribuição de Estoque", "Box Plot"),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Histograma
        fig.add_trace(
            go.Histogram(
                x=df[estoque_col],
                nbinsx=30,
                name="Estoque",
                marker_color='rgba(31, 119, 180, 0.7)',
                hovertemplate="Faixa: %{x}<br>Frequência: %{y}<extra></extra>"
            ),
            row=1, col=1
        )
        
        # Box plot
        fig.add_trace(
            go.Box(
                y=df[estoque_col],
                name="Estoque",
                marker_color='rgba(31, 119, 180, 0.7)',
                boxmean='sd'
            ),
            row=1, col=2
        )
        
        fig.update_xaxes(title_text="Nível de Estoque", row=1, col=1)
        fig.update_yaxes(title_text="Frequência", row=1, col=1)
        fig.update_yaxes(title_text="Quantidade", row=1, col=2)
        
        fig = _apply_chart_customization(fig, title="Análise de Distribuição de Estoque")
        
        # Calcular estatísticas
        stats = {
            "media": float(df[estoque_col].mean()),
            "mediana": float(df[estoque_col].median()),
            "desvio_padrao": float(df[estoque_col].std()),
            "minimo": float(df[estoque_col].min()),
            "maximo": float(df[estoque_col].max()),
            "q1": float(df[estoque_col].quantile(0.25)),
            "q3": float(df[estoque_col].quantile(0.75))
        }
        
        return {
            "status": "success",
            "chart_type": "distribution",
            "chart_data": _export_chart_to_json(fig),
            "summary": stats
        }
    except Exception as e:
        logger.error(f"Erro ao gerar análise de distribuição: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro ao gerar gráfico: {str(e)}"
        }


@tool
def gerar_grafico_pizza_categorias() -> Dict[str, Any]:
    """
    Gera gráfico de pizza mostrando proporção de produtos por categoria.
    Útil para visualizar distribuição percentual.
    
    Returns:
        Dicionário com gráfico de pizza e proporções
    """
    logger.info("Gerando gráfico de pizza")
    
    try:
        manager = get_data_manager()
        
        df = None
        tabelas = ['admmatao', 'ADMAT', 'ADMAT_REBUILT', 'master_catalog']
        
        for tabela in tabelas:
            try:
                df = manager.get_data(tabela, limit=5000)
                if not df.empty:
                    logger.info(f"Dados carregados de {tabela}")
                    break
            except Exception as e:
                logger.debug(f"Erro ao tentar {tabela}: {e}")
                continue
        
        if df is None or df.empty:
            return {
                "status": "error",
                "message": "Não foi possível carregar dados"
            }
        
        # Encontrar coluna de categoria
        categoria_col = None
        for col in df.columns:
            if 'categ' in col.lower():
                categoria_col = col
                break
        
        if not categoria_col:
            return {
                "status": "error",
                "message": "Coluna de categoria não encontrada"
            }
        
        # Contar por categoria
        categorias = df[categoria_col].value_counts()
        
        # Criar gráfico
        fig = go.Figure(data=[
            go.Pie(
                labels=categorias.index,
                values=categorias.values,
                hovertemplate="<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>"
            )
        ])
        
        fig = _apply_chart_customization(
            fig,
            title="Distribuição de Produtos por Categoria"
        )
        
        fig.update_layout(height=600)
        
        return {
            "status": "success",
            "chart_type": "pie",
            "chart_data": _export_chart_to_json(fig),
            "summary": {
                "total_categorias": len(categorias),
                "total_produtos": int(categorias.sum()),
                "categorias": categorias.to_dict()
            }
        }
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico de pizza: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro ao gerar gráfico: {str(e)}"
        }


@tool
def gerar_dashboard_analise_completa() -> Dict[str, Any]:
    """
    Gera dashboard completo com múltiplas visualizações em um único lugar.
    Combina 4 gráficos em um layout 2x2.
    
    Returns:
        Dicionário com dashboard e múltiplos gráficos
    """
    logger.info("Gerando dashboard completo")
    
    try:
        manager = get_data_manager()
        
        df = None
        tabelas = ['admmatao', 'ADMAT', 'ADMAT_REBUILT', 'master_catalog']
        
        for tabela in tabelas:
            try:
                df = manager.get_data(tabela, limit=5000)
                if not df.empty:
                    logger.info(f"Dados carregados de {tabela}")
                    break
            except Exception as e:
                logger.debug(f"Erro ao tentar {tabela}: {e}")
                continue
        
        if df is None or df.empty:
            return {
                "status": "error",
                "message": "Não foi possível carregar dados"
            }
        
        from plotly.subplots import make_subplots
        
        # Encontrar colunas
        categoria_col = None
        estoque_col = None
        preco_col = None
        
        for col in df.columns:
            if 'categ' in col.lower():
                categoria_col = col
            elif 'est' in col.lower():
                estoque_col = col
            elif 'preco' in col.lower():
                preco_col = col
        
        if not all([categoria_col, estoque_col]):
            return {
                "status": "error",
                "message": "Colunas necessárias não encontradas"
            }
        
        # Preparar dados
        df_conv = df.copy()
        if estoque_col:
            df_conv[estoque_col] = pd.to_numeric(df_conv[estoque_col], errors='coerce')
        if preco_col:
            df_conv[preco_col] = pd.to_numeric(df_conv[preco_col], errors='coerce')
        
        # Criar subplots 2x2
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Produtos por Categoria",
                "Top 10 Produtos - Estoque",
                "Distribuição de Estoque",
                "Preço Médio por Categoria"
            ),
            specs=[
                [{"type": "pie"}, {"type": "bar"}],
                [{"type": "histogram"}, {"type": "bar"}]
            ]
        )
        
        # Gráfico 1: Pizza
        cat_counts = df_conv[categoria_col].value_counts()
        fig.add_trace(
            go.Pie(labels=cat_counts.index, values=cat_counts.values, name="Categorias"),
            row=1, col=1
        )
        
        # Gráfico 2: Top 10 Estoque
        top_estoque = df_conv.nlargest(10, estoque_col)
        nome_col = next((c for c in df_conv.columns if 'nome' in c.lower()), estoque_col)
        fig.add_trace(
            go.Bar(x=top_estoque[nome_col], y=top_estoque[estoque_col], name="Estoque", marker_color='lightblue'),
            row=1, col=2
        )
        
        # Gráfico 3: Histograma
        fig.add_trace(
            go.Histogram(x=df_conv[estoque_col], nbinsx=20, name="Distribuição", marker_color='lightgreen'),
            row=2, col=1
        )
        
        # Gráfico 4: Preço médio (se disponível)
        if preco_col:
            preco_med = df_conv.groupby(categoria_col)[preco_col].mean().sort_values(ascending=False)
            fig.add_trace(
                go.Bar(x=preco_med.index, y=preco_med.values, name="Preço Médio", marker_color='lightyellow'),
                row=2, col=2
            )
        
        # Atualizar layout
        fig.update_layout(
            title_text="Dashboard de Análise - Visão Geral",
            height=900,
            showlegend=False,
            template=_get_theme_template()
        )
        
        fig.update_xaxes(title_text="Categoria", row=1, col=2)
        fig.update_xaxes(title_text="Estoque", row=2, col=1)
        fig.update_yaxes(title_text="Quantidade", row=1, col=2)
        fig.update_yaxes(title_text="Frequência", row=2, col=1)
        
        return {
            "status": "success",
            "chart_type": "dashboard",
            "chart_data": _export_chart_to_json(fig),
            "summary": {
                "total_produtos": len(df_conv),
                "total_categorias": df_conv[categoria_col].nunique(),
                "estoque_total": float(df_conv[estoque_col].sum()),
                "estoque_medio": float(df_conv[estoque_col].mean())
            }
        }
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro ao gerar dashboard: {str(e)}"
        }


@tool
def gerar_grafico_vendas_por_produto(
    codigo_produto: int = 59294,
    unidade: str = "SCR"
) -> Dict[str, Any]:
    """
    Gera gráfico de série temporal de vendas de um produto específico.
    Mostra evolução de vendas mensais com linha e markers.
    
    Args:
        codigo_produto: Código do produto (padrão: 59294)
        unidade: Unidade de venda (padrão: SCR)
        
    Returns:
        Dicionário com gráfico de série temporal e análise
    """
    logger.info(
        f"Gerando gráfico de vendas do produto {codigo_produto} "
        f"na unidade {unidade}"
    )

    try:
        manager = get_data_manager()

        # Tentar obter dados
        df = None
        tabelas = ['admmatao', 'ADMAT', 'ADMAT_REBUILT', 'master_catalog']

        for tabela in tabelas:
            try:
                df = manager.get_data(tabela, limit=10000)
                if not df.empty:
                    logger.info(f"Dados carregados de {tabela}")
                    break
            except Exception as e:
                logger.debug(f"Erro ao tentar {tabela}: {e}")
                continue

        if df is None or df.empty:
            return {
                "status": "error",
                "message": "Não foi possível carregar dados"
            }

        # Normalizar nomes de colunas para lowercase
        df.columns = df.columns.str.lower()

        # Procurar colunas de código e dados de vendas
        codigo_col = None
        data_col = None
        quantidade_col = None

        for col in df.columns:
            if 'codigo' in col or 'product' in col or 'sku' in col:
                codigo_col = col
            if 'data' in col or 'mes' in col or 'month' in col:
                data_col = col
            if 'venda' in col or 'quantidade' in col or 'sales' in col:
                quantidade_col = col

        # Se não encontrar, usar padrões conhecidos
        if not codigo_col:
            codigo_col = next(
                (c for c in df.columns if 'codigo' in c),
                None
            )
        if not data_col:
            data_col = next(
                (c for c in df.columns if 'data' in c or 'date' in c),
                None
            )
        if not quantidade_col:
            quantidade_col = next(
                (c for c in df.columns if 'quant' in c or 'sales' in c),
                None
            )

        if not all([codigo_col, data_col, quantidade_col]):
            # Retornar sumário do produto com dados disponíveis
            return {
                "status": "success",
                "chart_type": "vendas_produto",
                "message": (
                    f"Dados do produto {codigo_produto} encontrados, "
                    "mas estrutura não está em série temporal. "
                    "Dados brutos fornecidos para análise."
                ),
                "summary": {
                    "codigo_produto": codigo_produto,
                    "unidade": unidade,
                    "dados_disponiveis": len(df),
                    "colunas": list(df.columns)
                }
            }

        # Filtrar por código de produto
        df_produto = df[df[codigo_col] == codigo_produto].copy()

        if df_produto.empty:
            return {
                "status": "error",
                "message": f"Produto {codigo_produto} não encontrado"
            }

        # Converter data para datetime
        try:
            df_produto[data_col] = pd.to_datetime(df_produto[data_col])
        except Exception as e:
            logger.warning(f"Erro ao converter data: {e}")

        # Converter quantidade para numérico
        df_produto[quantidade_col] = pd.to_numeric(
            df_produto[quantidade_col],
            errors='coerce'
        )
        df_produto = df_produto.dropna(subset=[quantidade_col])

        # Agrupar por data se necessário
        if len(df_produto) > 1:
            df_vendas = df_produto.groupby(data_col)[
                quantidade_col
            ].sum().reset_index()
            df_vendas = df_vendas.sort_values(data_col)
        else:
            df_vendas = df_produto[[data_col, quantidade_col]].copy()

        # Criar gráfico de linha
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_vendas[data_col],
            y=df_vendas[quantidade_col],
            mode='lines+markers',
            name='Vendas',
            line=dict(
                color='#1f77b4',
                width=3
            ),
            marker=dict(
                size=8,
                color='#1f77b4',
                line=dict(width=2, color='white')
            ),
            hovertemplate=(
                "<b>Data</b>: %{x|%d/%m/%Y}<br>"
                "<b>Quantidade</b>: %{y} unidades<extra></extra>"
            ),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 180, 0.2)'
        ))

        fig = _apply_chart_customization(
            fig,
            title=(
                f"Vendas do Produto {codigo_produto} "
                f"na Unidade {unidade}"
            )
        )

        fig.update_xaxes(
            title_text="Data",
            type="date",
            tickformat="%d/%m/%Y"
        )
        fig.update_yaxes(title_text="Quantidade (unidades)")

        fig.update_layout(height=600)

        # Calcular estatísticas
        total_vendas = df_vendas[quantidade_col].sum()
        venda_media = df_vendas[quantidade_col].mean()
        venda_max = df_vendas[quantidade_col].max()
        venda_min = df_vendas[quantidade_col].min()

        return {
            "status": "success",
            "chart_type": "line_temporal",
            "chart_data": _export_chart_to_json(fig),
            "summary": {
                "codigo_produto": codigo_produto,
                "unidade": unidade,
                "periodos": len(df_vendas),
                "total_vendas": int(total_vendas),
                "venda_media": float(venda_media),
                "venda_maxima": int(venda_max),
                "venda_minima": int(venda_min),
                "primeira_data": str(df_vendas[data_col].min()),
                "ultima_data": str(df_vendas[data_col].max())
            }
        }
    except Exception as e:
        logger.error(
            f"Erro ao gerar gráfico de vendas: {e}",
            exc_info=True
        )
        return {
            "status": "error",
            "message": f"Erro ao gerar gráfico: {str(e)}"
        }


@tool
def gerar_grafico_automatico(descricao: str) -> Dict[str, Any]:
    """
    Gera qualquer tipo de gráfico baseado na descrição do usuário.
    O LLM interpreta a descrição e seleciona o gráfico mais apropriado.
    
    Args:
        descricao: Descrição do gráfico desejado em linguagem natural
        
    Returns:
        Gráfico Plotly JSON correspondente ao tipo solicitado
        
    Exemplos de uso:
      - "gráfico de vendas por categoria"
      - "mostrar estoque disponível por produto"
      - "análise de distribuição de estoque"
      - "comparar preços entre categorias"
      - "vendas do produto 59294"
      - "dashboard completo"
    """
    logger.info(f"Gerando gráfico automático: {descricao}")

    descricao_lower = descricao.lower()

    # Detectar tipo de gráfico pela descrição
    if any(
        word in descricao_lower
        for word in [
            'vendas', 'venda', 'sales', 'categoria',
            'categor', 'top', 'ranking'
        ]
    ):
        logger.info("Detectado: Gráfico de vendas por categoria")
        return gerar_grafico_vendas_por_categoria.invoke({
            "limite": 10,
            "ordenar_por": "descendente"
        })

    elif any(
        word in descricao_lower
        for word in [
            'estoque', 'stock', 'disponível', 'quantidade',
            'quantidade', 'inv', 'por produto'
        ]
    ):
        logger.info("Detectado: Gráfico de estoque por produto")
        return gerar_grafico_estoque_por_produto.invoke({
            "limite": 15,
            "minimo_estoque": 0
        })

    elif any(
        word in descricao_lower
        for word in [
            'preço', 'preco', 'price', 'preços',
            'comparação', 'comparar', 'pricing'
        ]
    ):
        logger.info("Detectado: Gráfico de comparação de preços")
        return gerar_comparacao_precos_categorias.invoke({})

    elif any(
        word in descricao_lower
        for word in [
            'distribuição', 'distribuicao', 'distribuição',
            'análise', 'analise', 'histograma', 'box plot'
        ]
    ):
        logger.info("Detectado: Análise de distribuição")
        return gerar_analise_distribuicao_estoque.invoke({})

    elif any(
        word in descricao_lower
        for word in ['pizza', 'pie', 'propor', 'percent', 'proporção']
    ):
        logger.info("Detectado: Gráfico de pizza")
        return gerar_grafico_pizza_categorias.invoke({})

    elif any(
        word in descricao_lower
        for word in [
            'dashboard', 'tudo', 'visão', 'visao', 'completo',
            'overview', 'resumo'
        ]
    ):
        logger.info("Detectado: Dashboard completo")
        return gerar_dashboard_analise_completa.invoke({})

    elif any(
        word in descricao_lower
        for word in [
            'produto', 'temporal', 'série', 'serie',
            'evolução', 'evolucao', 'sku', 'mensal',
            'mês', 'mes', 'vendas produto'
        ]
    ):
        logger.info("Detectado: Gráfico de vendas por produto")
        # Extrair código do produto se presente
        import re
        match = re.search(r'\d+', descricao)
        codigo = int(match.group()) if match else 59294

        # Tentar usar a versão com dados mensais pivotados (estrutura real)
        resultado = gerar_grafico_vendas_mensais_produto.invoke({
            "codigo_produto": codigo,
            "unidade_filtro": None
        })

        # Se falhar, retornar gráfico de série temporal alternativo
        if resultado.get('status') == 'error':
            logger.info("Gráfico mensal falhou, tentando série temporal")
            return gerar_grafico_vendas_por_produto.invoke({
                "codigo_produto": codigo,
                "unidade": "SCR"
            })

        return resultado

    else:
        # Por padrão, gera dashboard completo
        logger.info("Tipo não reconhecido, gerando dashboard padrão")
        return gerar_dashboard_analise_completa.invoke({})


@tool
def gerar_grafico_vendas_mensais_produto(
    codigo_produto: int = 59294,
    unidade_filtro: str = ""
) -> Dict[str, Any]:
    """
    Gera gráfico de vendas mensais para um produto específico.
    Trabalha com estrutura pivotada de dados (mes_01 até mes_12).
    
    Args:
        codigo_produto: Código do produto (padrão: 59294)
        unidade_filtro: Unidade para filtrar (default: vazio)
        
    Returns:
        Dicionário com gráfico de vendas mensais
    """
    logger.info(
        f"Gerando gráfico de vendas mensais do produto {codigo_produto}"
    )

    try:
        manager = get_data_manager()

        # Tentar carregar dados
        df = None
        for tabela in ['ADMAT_REBUILT', 'admmatao', 'ADMAT', 'master_catalog']:
            try:
                df = manager.get_data(tabela, limit=50000)
                if not df.empty:
                    logger.info(f"Dados carregados de {tabela}")
                    break
            except Exception as e:
                logger.debug(f"Erro ao tentar {tabela}: {e}")
                continue

        if df is None or df.empty:
            return {
                "status": "error",
                "message": "Não foi possível carregar dados"
            }

        # Normalizar nomes de colunas
        df.columns = df.columns.str.lower()

        # Procurar coluna de código
        codigo_col = next(
            (c for c in df.columns if 'codigo' in c or 'code' in c),
            None
        )

        if not codigo_col:
            return {
                "status": "error",
                "message": "Coluna de código de produto não encontrada"
            }

        # Filtrar por código do produto
        df_produto = df[df[codigo_col] == codigo_produto].copy()

        if df_produto.empty:
            return {
                "status": "error",
                "message": (
                    f"Produto {codigo_produto} não encontrado. "
                    "Verifique o código informado."
                )
            }

        # Se houver filtro de unidade, aplicar
        if unidade_filtro:
            une_cols = [c for c in df_produto.columns if 'une' in c]
            if une_cols:
                df_produto = df_produto[
                    df_produto[une_cols[0]].astype(str).str.contains(
                        unidade_filtro,
                        case=False,
                        na=False
                    )
                ]

        if df_produto.empty:
            return {
                "status": "error",
                "message": (
                    f"Nenhum registro encontrado para produto "
                    f"{codigo_produto} na unidade {unidade_filtro}"
                )
            }

        # Extrair colunas de meses
        mes_cols = sorted(
            [c for c in df_produto.columns if c.startswith('mes_')]
        )

        if not mes_cols:
            return {
                "status": "error",
                "message": (
                    "Colunas de meses não encontradas na "
                    "estrutura de dados"
                )
            }

        # Preparar dados para gráfico
        mes_labels = []
        mes_numeros = []
        
        for col in mes_cols:
            mes_num = col.replace('mes_', '')
            if mes_num == 'parcial':
                mes_labels.append('Parcial')
            else:
                mes_labels.append(f'Mês {mes_num}')
            mes_numeros.append(mes_num)

        # Agregar vendas por mês (caso tenha múltiplas unidades)
        vendas_mensais = []
        for col in mes_cols:
            valores = pd.to_numeric(
                df_produto[col],
                errors='coerce'
            ).fillna(0)
            vendas_mensais.append(valores.sum())

        # Criar gráfico
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=mes_labels,
            y=vendas_mensais,
            mode='lines+markers',
            name='Vendas',
            line=dict(
                color='#2563EB',
                width=3
            ),
            marker=dict(
                size=10,
                color='#2563EB',
                line=dict(width=2, color='white'),
                symbol='circle'
            ),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Quantidade: %{y:,.0f} unidades<extra></extra>"
            ),
            fill='tozeroy',
            fillcolor='rgba(37, 99, 235, 0.2)'
        ))

        # Adicionar linha de média
        media_vendas = sum(vendas_mensais) / len(vendas_mensais)
        fig.add_hline(
            y=media_vendas,
            line_dash="dash",
            line_color="red",
            annotation_text="Média",
            annotation_position="right"
        )

        fig = _apply_chart_customization(
            fig,
            title=(
                f"Vendas Mensais - Produto {codigo_produto}"
            )
        )

        fig.update_xaxes(title_text="Mês")
        fig.update_yaxes(title_text="Quantidade (unidades)")
        fig.update_layout(height=600, hovermode='x unified')

        # Calcular estatísticas
        total_vendas = sum(vendas_mensais)
        venda_media = total_vendas / len(vendas_mensais)
        venda_max = max(vendas_mensais)
        venda_min = min(vendas_mensais)
        venda_max_mes = mes_labels[vendas_mensais.index(venda_max)]
        venda_min_mes = mes_labels[vendas_mensais.index(venda_min)]

        # Extrair informações adicionais do produto
        produto_info = {}
        for col in ['nome_produto', 'nome_categoria', 'une_nome']:
            if col in df_produto.columns:
                valor = df_produto[col].iloc[0]
                produto_info[col] = str(valor)

        return {
            "status": "success",
            "chart_type": "line_temporal_mensal",
            "chart_data": _export_chart_to_json(fig),
            "summary": {
                "codigo_produto": codigo_produto,
                "total_vendas": int(total_vendas),
                "venda_media": float(venda_media),
                "venda_maxima": int(venda_max),
                "venda_minima": int(venda_min),
                "mes_maior_venda": venda_max_mes,
                "mes_menor_venda": venda_min_mes,
                "variacao": float(
                    (venda_max - venda_min) / venda_media * 100
                    if venda_media > 0 else 0
                ),
                "meses_analisados": len(mes_cols),
                "produto_info": produto_info,
                "dados_mensais": {
                    mes_labels[i]: int(vendas_mensais[i])
                    for i in range(len(mes_labels))
                }
            }
        }

    except Exception as e:
        logger.error(
            f"Erro ao gerar gráfico de vendas mensais: {e}",
            exc_info=True
        )
        return {
            "status": "error",
            "message": f"Erro ao gerar gráfico: {str(e)}"
        }


# Lista de todas as ferramentas de gráficos disponíveis
chart_tools = [
    gerar_grafico_vendas_por_categoria,
    gerar_grafico_estoque_por_produto,
    gerar_comparacao_precos_categorias,
    gerar_analise_distribuicao_estoque,
    gerar_grafico_pizza_categorias,
    gerar_dashboard_analise_completa,
    gerar_grafico_vendas_por_produto,
    gerar_grafico_vendas_mensais_produto,
    gerar_grafico_automatico,
]
