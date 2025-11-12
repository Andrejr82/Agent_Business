# Implementação Prática: Chart Tools para o Agente

**Status:** 🟢 Pronto para Implementação  
**Tempo Estimado:** 2-3 dias  
**Complexidade:** Média

---

## 📌 Arquivo 1: `core/tools/chart_tools.py` (NOVO - 400+ linhas)

```python
"""
Ferramentas de geração de gráficos para o agente BI.
Integra dados do unified_data_tools com visualizações Plotly.

Uso:
    from core.tools.chart_tools import gerar_grafico_vendas
    fig = gerar_grafico_vendas(dimensao="categoria")
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.data_source_manager import get_data_manager
from core.tools.unified_data_tools import get_produtos, buscar_por_categoria
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


# ============================================================================
# UTILITÁRIOS DE SERIALIZAÇÃO E TEMA
# ============================================================================


def to_plotly_dict(fig: go.Figure) -> Dict[str, Any]:
    """
    Serializa figura Plotly para enviar ao frontend.
    Retorna dicionário que pode ser serializado em JSON.
    
    Args:
        fig: Figura Plotly
        
    Returns:
        Dict com dados do gráfico prontos para st.plotly_chart()
    """
    try:
        # Streamlit trabalha diretamente com objetos Plotly
        return fig
    except Exception as e:
        logger.error(f"Erro ao serializar figura Plotly: {e}")
        return {"error": str(e)}


def apply_theme(fig: go.Figure, theme: str = "plotly_white") -> go.Figure:
    """
    Aplica tema visual consistente a todos os gráficos.
    
    Args:
        fig: Figura Plotly
        theme: Tema desejado
        
    Returns:
        Figura com tema aplicado
    """
    fig.update_layout(
        template=theme,
        font=dict(family="Arial, sans-serif", size=12, color="#2c3e50"),
        title_font_size=16,
        title_font_color="#2c3e50",
        hovermode="closest",
        margin=dict(l=50, r=50, t=80, b=50),
    )
    
    # Aplicar cores da paleta Plotly
    if theme == "plotly_white":
        fig.update_layout(plot_bgcolor="rgba(240, 240, 240, 0.5)")
    
    return fig


def format_large_numbers(value: float) -> str:
    """
    Formata números grandes com notação abreviada.
    Exemplo: 1500000 → "1.5M"
    """
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.1f}K"
    else:
        return f"{value:.0f}"


def validate_dataframe_for_chart(
    df: pd.DataFrame,
    required_columns: List[str],
    min_rows: int = 2
) -> tuple[bool, str]:
    """
    Valida se DataFrame é adequado para gerar gráfico.
    
    Args:
        df: DataFrame a validar
        required_columns: Colunas obrigatórias
        min_rows: Mínimo de linhas necessárias
        
    Returns:
        (is_valid, message)
    """
    if df is None or df.empty:
        return False, "DataFrame vazio ou nulo"
    
    if len(df) < min_rows:
        return False, f"Insuficientes dados ({len(df)} linhas, mínimo {min_rows})"
    
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        return False, f"Colunas faltando: {missing_cols}"
    
    return True, "OK"


# ============================================================================
# FERRAMENTAS PARA GERAR GRÁFICOS
# ============================================================================


@tool
def gerar_grafico_vendas(
    dimensao: str = "categoria",
    metrica: str = "quantidade",
    titulo: Optional[str] = None,
    limite: int = 100
) -> Dict[str, Any]:
    """
    Gera gráfico de vendas/produtos segmentado por dimensão.
    
    Args:
        dimensao: "categoria", "produto" (filtro por categoria)
        metrica: "quantidade" ou "valor" (quando disponível)
        titulo: Título customizado
        limite: Máximo de registros
        
    Returns:
        Dict com figura Plotly e metadados
        
    Example:
        >>> result = gerar_grafico_vendas(dimensao="categoria")
        >>> # Retorna gráfico de barras com produtos por categoria
    """
    logger.info(f"Gerando gráfico de vendas: dimensao={dimensao}, metrica={metrica}")
    
    try:
        # 1. Buscar dados
        resultado = get_produtos(limit=limite)
        
        if resultado["status"] != "success" or not resultado.get("produtos"):
            return {
                "status": "error",
                "message": "Não há dados disponíveis para gerar gráfico",
                "chart": None
            }
        
        # 2. Converter para DataFrame
        df = pd.DataFrame(resultado["produtos"])
        
        # 3. Preparar dados por dimensão
        if dimensao == "categoria":
            # Agrupar por categoria e contar produtos
            if "categoria" in df.columns:
                dados = df.groupby("categoria").size().reset_index(name="quantidade")
                eixo_x = "categoria"
                eixo_y = "quantidade"
                titulo_padrao = "Produtos por Categoria"
            else:
                return {
                    "status": "error",
                    "message": "Coluna 'categoria' não encontrada nos dados",
                    "chart": None
                }
        
        elif dimensao == "produto":
            # Top 10 produtos
            dados = df.head(10).copy()
            dados = dados[["nome", "codigo"]].copy()
            eixo_x = "nome"
            eixo_y = "codigo"
            titulo_padrao = "Top Produtos"
        
        else:
            return {
                "status": "error",
                "message": f"Dimensão '{dimensao}' não suportada",
                "chart": None
            }
        
        # 4. Validar dados
        is_valid, msg = validate_dataframe_for_chart(dados, [eixo_x, eixo_y])
        if not is_valid:
            return {"status": "error", "message": msg, "chart": None}
        
        # 5. Criar gráfico
        fig = px.bar(
            dados,
            x=eixo_x,
            y=eixo_y,
            title=titulo or titulo_padrao,
            labels={eixo_x: "Categoria" if dimensao == "categoria" else "Produto",
                    eixo_y: "Quantidade"},
            text_auto=True,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        
        fig.update_traces(textposition='outside')
        fig = apply_theme(fig)
        
        logger.info(f"Gráfico de vendas gerado com sucesso: {len(dados)} registros")
        
        return {
            "status": "success",
            "chart": fig,
            "type": "bar",
            "records": len(dados),
            "dimensao": dimensao,
            "source": "SQL Server / Parquet"
        }
    
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico de vendas: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro: {str(e)}",
            "chart": None
        }


@tool
def gerar_grafico_estoque(
    tipo: str = "disponivel",
    categoria: Optional[str] = None,
    limite_superior: Optional[int] = None,
    top_n: int = 15
) -> Dict[str, Any]:
    """
    Gera gráfico de estoque disponível por produto.
    
    Args:
        tipo: "disponivel", "minimo", "critico", "todos"
        categoria: Filtrar por categoria específica (opcional)
        limite_superior: Mostrar apenas produtos com estoque > limite
        top_n: Quantos top produtos mostrar
        
    Returns:
        Dict com figura Plotly de barras horizontal
        
    Example:
        >>> result = gerar_grafico_estoque(tipo="disponivel", categoria="BRINQUEDOS")
        >>> # Retorna top 15 produtos em estoque
    """
    logger.info(f"Gerando gráfico de estoque: tipo={tipo}, categoria={categoria}")
    
    try:
        # 1. Buscar dados
        if categoria:
            resultado = buscar_por_categoria(categoria, limit=1000)
            if resultado["status"] != "success":
                return {
                    "status": "error",
                    "message": f"Categoria '{categoria}' não encontrada",
                    "chart": None
                }
            df = pd.DataFrame(resultado.get("resultados", []))
        else:
            resultado = get_produtos(limit=1000)
            if resultado["status"] != "success":
                return {
                    "status": "error",
                    "message": "Não há dados de estoque disponíveis",
                    "chart": None
                }
            df = pd.DataFrame(resultado["produtos"])
        
        # 2. Preparar coluna de estoque
        # Tentar diferentes nomes de coluna possíveis
        coluna_estoque = None
        for col_name in ["est_une", "estoque", "quantidade", "stock"]:
            if col_name in df.columns:
                coluna_estoque = col_name
                break
        
        if not coluna_estoque:
            logger.warning(f"Colunas disponíveis: {df.columns.tolist()}")
            return {
                "status": "error",
                "message": "Coluna de estoque não encontrada",
                "chart": None
            }
        
        # 3. Filtrar por tipo
        if tipo == "disponivel":
            df = df[df[coluna_estoque] > 0]
        elif tipo == "minimo":
            df = df[(df[coluna_estoque] > 0) & (df[coluna_estoque] < 50)]
        elif tipo == "critico":
            df = df[df[coluna_estoque] < 10]
        
        # 4. Aplicar limite superior se especificado
        if limite_superior:
            df = df[df[coluna_estoque] <= limite_superior]
        
        # 5. Top N produtos por estoque
        df = df.nlargest(top_n, coluna_estoque)
        
        # 6. Validar dados
        is_valid, msg = validate_dataframe_for_chart(
            df, 
            ["nome", coluna_estoque],
            min_rows=1
        )
        if not is_valid:
            return {"status": "error", "message": msg, "chart": None}
        
        # 7. Criar gráfico horizontal (barras mais legíveis)
        fig = px.bar(
            df,
            y="nome",
            x=coluna_estoque,
            orientation="h",
            title=f"Top {len(df)} Produtos - Estoque {tipo.capitalize()}",
            labels={coluna_estoque: "Estoque (UN)", "nome": "Produto"},
            text_auto=True,
            color=coluna_estoque,
            color_continuous_scale="Viridis"
        )
        
        fig.update_traces(textposition='outside')
        fig = apply_theme(fig)
        
        logger.info(f"Gráfico de estoque gerado: {len(df)} produtos")
        
        return {
            "status": "success",
            "chart": fig,
            "type": "bar_horizontal",
            "records": len(df),
            "tipo": tipo,
            "categoria": categoria or "Todas"
        }
    
    except Exception as e:
        logger.error(f"Erro ao gerar gráfico de estoque: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro: {str(e)}",
            "chart": None
        }


@tool
def gerar_comparacao(
    tipo_comparacao: str = "produtos",
    categorias: Optional[List[str]] = None,
    metrica: str = "quantidade",
    top_n: int = 10
) -> Dict[str, Any]:
    """
    Compara valores entre múltiplas dimensões.
    
    Args:
        tipo_comparacao: "produtos", "categorias"
        categorias: Lista de categorias para comparar
        metrica: "quantidade", "estoque"
        top_n: Quantos top itens mostrar
        
    Returns:
        Dict com figura Plotly comparativa
        
    Example:
        >>> result = gerar_comparacao(
        ...     tipo_comparacao="categorias",
        ...     metrica="quantidade"
        ... )
    """
    logger.info(f"Gerando comparação: tipo={tipo_comparacao}")
    
    try:
        resultado = get_produtos(limit=500)
        if resultado["status"] != "success":
            return {"status": "error", "message": "Sem dados", "chart": None}
        
        df = pd.DataFrame(resultado["produtos"])
        
        # Agrupar dados para comparação
        if tipo_comparacao == "categorias":
            # Contar produtos por categoria
            dados = df.groupby("categoria").size().reset_index(name="quantidade")
            dados = dados.nlargest(top_n, "quantidade")
            
            fig = px.bar(
                dados,
                x="categoria",
                y="quantidade",
                title="Comparação de Produtos por Categoria",
                labels={"categoria": "Categoria", "quantidade": "Quantidade"},
                color="quantidade",
                color_continuous_scale="Blues"
            )
        
        else:
            # Top produtos
            dados = df.head(top_n).copy()
            
            fig = px.bar(
                dados,
                x="nome",
                y="codigo",
                title=f"Top {top_n} Produtos",
                labels={"nome": "Produto", "codigo": "Código"},
                color_discrete_sequence=px.colors.qualitative.Set1
            )
        
        fig = apply_theme(fig)
        
        return {
            "status": "success",
            "chart": fig,
            "type": "comparison",
            "records": len(dados)
        }
    
    except Exception as e:
        logger.error(f"Erro ao gerar comparação: {e}")
        return {
            "status": "error",
            "message": f"Erro: {str(e)}",
            "chart": None
        }


@tool
def gerar_analise_distribuicao(
    coluna: str = "preco_38_percent",
    tipo: str = "histograma",
    bins: int = 30
) -> Dict[str, Any]:
    """
    Analisa distribuição de dados (histograma, box, violino).
    
    Args:
        coluna: Coluna a analisar
        tipo: "histograma", "box", "violino"
        bins: Número de bins para histograma
        
    Returns:
        Dict com figura de distribuição
    """
    logger.info(f"Analisando distribuição: coluna={coluna}, tipo={tipo}")
    
    try:
        resultado = get_produtos(limit=500)
        df = pd.DataFrame(resultado["produtos"])
        
        # Filtrar valores nulos e negativos
        dados = df[df[coluna].notna()].copy()
        dados = dados[dados[coluna] > 0]
        
        if tipo == "histograma":
            fig = px.histogram(
                dados,
                x=coluna,
                nbins=bins,
                title=f"Distribuição de {coluna}",
                labels={coluna: coluna},
                color_discrete_sequence=px.colors.qualitative.Set2
            )
        
        elif tipo == "box":
            fig = px.box(
                dados,
                y=coluna,
                title=f"Box Plot de {coluna}",
                labels={coluna: coluna}
            )
        
        else:  # violino
            fig = px.violin(
                dados,
                y=coluna,
                title=f"Distribuição (Violino) de {coluna}",
                labels={coluna: coluna},
                box=True,
                points="outliers"
            )
        
        fig = apply_theme(fig)
        
        return {
            "status": "success",
            "chart": fig,
            "type": "distribution",
            "records": len(dados),
            "coluna": coluna
        }
    
    except Exception as e:
        logger.error(f"Erro ao analisar distribuição: {e}")
        return {
            "status": "error",
            "message": f"Erro: {str(e)}",
            "chart": None
        }


@tool
def gerar_pizza(
    dimensao: str = "categoria",
    limite: int = 100
) -> Dict[str, Any]:
    """
    Gera gráfico de pizza mostrando composição.
    
    Args:
        dimensao: "categoria" ou outro campo
        limite: Máximo de registros
        
    Returns:
        Dict com figura Plotly
    """
    logger.info(f"Gerando gráfico de pizza: dimensao={dimensao}")
    
    try:
        resultado = get_produtos(limit=limite)
        df = pd.DataFrame(resultado["produtos"])
        
        # Contar por dimensão
        dados = df.groupby(dimensao).size().reset_index(name="quantidade")
        dados = dados.nlargest(8, "quantidade")  # Máx 8 fatias
        
        fig = px.pie(
            dados,
            values="quantidade",
            names=dimensao,
            title=f"Composição por {dimensao}",
            hole=0.3,  # Donut chart
        )
        
        fig = apply_theme(fig)
        
        return {
            "status": "success",
            "chart": fig,
            "type": "pie",
            "records": len(dados)
        }
    
    except Exception as e:
        logger.error(f"Erro ao gerar pizza: {e}")
        return {
            "status": "error",
            "message": f"Erro: {str(e)}",
            "chart": None
        }


# ============================================================================
# FERRAMENTA PARA DASHBOARD
# ============================================================================


@tool
def gerar_dashboard_produto(codigo_produto: str) -> Dict[str, Any]:
    """
    Gera dashboard completo de um produto com 4 gráficos/painéis.
    
    Args:
        codigo_produto: Código único do produto
        
    Returns:
        Dict com figura com subgráficos (2x2)
    """
    logger.info(f"Gerando dashboard para produto: {codigo_produto}")
    
    try:
        # Buscar dados do produto
        resultado = get_produtos(limit=1000)
        df = pd.DataFrame(resultado["produtos"])
        
        # Filtrar produto específico
        produto = df[df["codigo"].astype(str) == str(codigo_produto)]
        
        if produto.empty:
            return {
                "status": "error",
                "message": f"Produto {codigo_produto} não encontrado",
                "chart": None
            }
        
        produto = produto.iloc[0]
        
        # Criar subgráficos (2x2)
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                f"Detalhes do Produto",
                f"Categoria: {produto.get('categoria', 'N/A')}",
                f"Estoque",
                f"Preço"
            ),
            specs=[
                [{"type": "indicator"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "gauge"}]
            ]
        )
        
        # Painel 1: Indicador
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=float(produto.get("codigo", 0)),
                title={"text": "Código"},
            ),
            row=1, col=1
        )
        
        # Painel 2: Categoria
        fig.add_trace(
            go.Bar(y=[produto.get("categoria", "N/A")], x=[1]),
            row=1, col=2
        )
        
        # Painel 3: Estoque
        estoque = float(produto.get("est_une", 0))
        fig.add_trace(
            go.Bar(x=["Estoque"], y=[estoque], marker_color="green"),
            row=2, col=1
        )
        
        # Painel 4: Preço (Gauge)
        preco = float(produto.get("preco_38_percent", 0))
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=preco,
                title={"text": "Preço"},
                gauge={"axis": {"range": [0, preco * 1.5]}}
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            title_text=f"Dashboard - Produto {produto.get('nome', 'N/A')}"
        )
        
        fig = apply_theme(fig)
        
        return {
            "status": "success",
            "chart": fig,
            "type": "dashboard",
            "produto": {
                "codigo": produto.get("codigo"),
                "nome": produto.get("nome"),
                "categoria": produto.get("categoria"),
                "estoque": estoque,
                "preco": preco
            }
        }
    
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro: {str(e)}",
            "chart": None
        }


# ============================================================================
# EXPORTAÇÃO DE FERRAMENTAS
# ============================================================================

# Lista de todas as ferramentas para registro no agente
CHART_TOOLS = [
    gerar_grafico_vendas,
    gerar_grafico_estoque,
    gerar_comparacao,
    gerar_analise_distribuicao,
    gerar_pizza,
    gerar_dashboard_produto,
]

if __name__ == "__main__":
    # Teste local
    print("Testando ferramentas de gráficos...")
    
    result = gerar_grafico_vendas(dimensao="categoria")
    print(f"✓ Gráfico de vendas: {result['status']}")
    
    result = gerar_grafico_estoque(tipo="disponivel")
    print(f"✓ Gráfico de estoque: {result['status']}")
    
    result = gerar_pizza(dimensao="categoria")
    print(f"✓ Gráfico de pizza: {result['status']}")
```

---

## 📝 Arquivo 2: Modificar `core/agents/caculinha_bi_agent.py`

```python
# Adicionar importação:
from core.tools.chart_tools import CHART_TOOLS

# No código de inicialização do agente, adicionar ferramentas:
def create_agent():
    # ... código existente ...
    
    # Combinar ferramentas de dados + ferramentas de gráficos
    from core.tools.unified_data_tools import DATA_TOOLS
    
    all_tools = DATA_TOOLS + CHART_TOOLS
    
    agent = create_tool_calling_agent(
        llm=llm,
        tools=all_tools,
        prompt=prompt
    )
    
    return agent
```

---

## 🎯 Arquivo 3: Adicionar ao `core/prompts/chart_generation_system.txt`

```
Você é um assistente de BI especializado em criar visualizações de dados.

REGRAS PARA GRÁFICOS:

1. DETECTAR INTENÇÃO
   - Usuário quer: "mostrar", "visualizar", "gráfico", "comparar", "tendência"?
   - Há múltiplos dados? (>5 registros)
   - Há dimensões e métricas claras?

2. ESCOLHER FERRAMENTA CORRETA
   - Produtos por categoria? → gerar_grafico_vendas(dimensao="categoria")
   - Estoque disponível? → gerar_grafico_estoque(tipo="disponivel")
   - Comparar produtos? → gerar_comparacao(tipo_comparacao="produtos")
   - Distribuição de preços? → gerar_analise_distribuicao(coluna="preco")
   - Composição? → gerar_pizza(dimensao="categoria")
   - Dashboard completo? → gerar_dashboard_produto(codigo_produto="...")

3. INTERPRETAR RESULTADOS
   - Descrever o que o gráfico mostra
   - Highlight insights: valores máximos, mínimos, tendências
   - Sugerir ações baseadas nos dados

4. MELHOR PRÁTICA
   - Sempre confirmar o tipo de gráfico apropriado
   - Oferecer alternativas se houver múltiplas opções
   - Explicar por que esse gráfico foi escolhido
```

---

## 🧪 Arquivo 4: `tests/test_chart_tools.py` (NOVO)

```python
import pytest
from core.tools.chart_tools import (
    gerar_grafico_vendas,
    gerar_grafico_estoque,
    gerar_comparacao,
    gerar_pizza,
)


def test_gerar_grafico_vendas_categoria():
    """Testa geração de gráfico de vendas por categoria"""
    result = gerar_grafico_vendas(dimensao="categoria")
    
    assert result["status"] == "success"
    assert result["chart"] is not None
    assert result["type"] == "bar"
    assert result["records"] > 0


def test_gerar_grafico_estoque_disponivel():
    """Testa geração de gráfico de estoque disponível"""
    result = gerar_grafico_estoque(tipo="disponivel")
    
    assert result["status"] == "success"
    assert result["chart"] is not None
    assert result["type"] == "bar_horizontal"


def test_gerar_comparacao_categorias():
    """Testa comparação entre categorias"""
    result = gerar_comparacao(tipo_comparacao="categorias")
    
    assert result["status"] == "success"
    assert result["chart"] is not None
    assert result["records"] > 0


def test_gerar_pizza():
    """Testa gráfico de pizza de composição"""
    result = gerar_pizza(dimensao="categoria")
    
    assert result["status"] == "success"
    assert result["chart"] is not None
    assert result["type"] == "pie"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## ✅ Checklist de Implementação Imediata

1. **Criar `core/tools/chart_tools.py`**
   - [ ] Copiar código acima
   - [ ] Validar imports
   - [ ] Testar cada função isoladamente

2. **Registrar ferramentas no agente**
   - [ ] Modificar `core/agents/caculinha_bi_agent.py`
   - [ ] Adicionar `CHART_TOOLS` à lista de ferramentas

3. **Testar integração**
   - [ ] Executar `python -m pytest tests/test_chart_tools.py`
   - [ ] Verificar se ferramentas aparecem quando consultar agente

4. **Integrar com Streamlit**
   - [ ] Testar se gráficos são renderizados corretamente
   - [ ] Validar interatividade (hover, zoom, etc)

5. **Refinar prompts**
   - [ ] Ajustar instruções do agente se necessário
   - [ ] Testar com diferentes perguntas sobre gráficos

---

## 🚀 Próximos Passos Recomendados

1. Implementar `chart_tools.py` conforme código acima
2. Testar ferramentas isoladamente
3. Registrar com agente e testar integração
4. Iterar com feedback do usuário
5. Documentar exemplos de uso

