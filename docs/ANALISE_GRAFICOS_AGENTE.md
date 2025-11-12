# Análise: Implementação de Gráficos para o Agente BI

**Data:** 11 de novembro de 2025  
**Status:** 🔍 Análise Completa  
**Objetivo:** Mapear recursos necessários e criar ferramentas para o agente gerar gráficos automaticamente

---

## 📋 Sumário Executivo

O agente de BI **Caçulinha** já possui a **infraestrutura base** para criar gráficos, porém **faltam as ferramentas específicas** que permitam o agente:
- 📊 Detectar quando uma pergunta requer visualização
- 🎨 Gerar gráficos interativos (Plotly)
- 📈 Disponibilizar diferentes tipos de gráficos (barras, linhas, pizza, etc.)
- 💾 Salvar e exibir os gráficos no Streamlit

---

## 🏗️ Estado Atual da Arquitetura

### ✅ O que JÁ ESTÁ FUNCIONANDO

#### 1. **Bibliotecas Instaladas**
```
✓ plotly==6.3.0          → Gráficos interativos
✓ matplotlib==3.10.5      → Gráficos estáticos
✓ pandas==2.3.1          → Processamento de dados
✓ kaleido==1.0.0         → Exportação de gráficos para PNG/PDF
✓ streamlit              → Interface web com suporte a gráficos
```

#### 2. **Componentes de UI Existentes** (`ui/ui_components.py`)
```python
✓ get_image_download_link()      → Download de gráficos como PNG/HTML
✓ get_csv_download_link()        → Export de dados como CSV
✓ apply_chart_customization()    → Temas, cores e personalização
```

#### 3. **Integração Streamlit** (`streamlit_app.py`)
```python
✓ st.plotly_chart()    → Renderização de gráficos interativos
✓ st.dataframe()       → Exibição de tabelas
✓ Chat com histórico  → Mensagens com suporte a gráficos
```

#### 4. **Estrutura de Processamento de Gráficos** (`core/tools/graph_integration.py`)
```python
✓ processar_resposta_com_grafico()  → Middleware para gerar gráficos
✓ Detecção de termos de gráfico    → "gráfico", "visualizar", "tendência"
✓ Suporte a dados em DataFrame     → Converte dados para visualização
```

#### 5. **LangGraph para Orquestração** (`core/graph/graph_builder.py`)
```python
✓ Nós de processamento estruturados
✓ Roteamento condicional
✓ Integração com ferramentas
```

---

## ❌ O que FALTA

### 1. **Ferramentas LangChain para o Agente** (⚠️ CRÍTICO)

O agente **NÃO POSSUI** ferramentas específicas para:

```python
# ❌ Faltando:
@tool
def gerar_grafico_vendas():
    """Gera gráfico de vendas por categoria/período"""
    
@tool
def gerar_grafico_estoque():
    """Gera gráfico de estoque disponível"""
    
@tool
def gerar_grafico_comparacao():
    """Compara produtos ou categorias"""
    
@tool
def gerar_analise_temporal():
    """Série temporal de dados"""
```

### 2. **Prompt do Agente Sem Contexto de Gráficos**

O agente não está instruído a:
- ✗ Reconhecer quando usar gráficos
- ✗ Escolher o tipo de gráfico apropriado
- ✗ Interpretar dados para visualização
- ✗ Descrever insights dos gráficos

### 3. **Lógica de Roteamento de Gráficos**

O supervisor não roteia para:
- ✗ Nó específico de "chart generation"
- ✗ Ferramentas de visualização
- ✗ Processamento de dados para gráficos

### 4. **Transformação de Dados para Gráficos**

Não há mapeamento entre:
- ✗ Resultados de consultas SQL
- ✗ Estrutura de dados esperada por Plotly
- ✗ Dimensões e métricas corretas

---

## 🛠️ O que PRECISA SER CRIADO

### Fase 1: Ferramentas de Gráficos (PRIORITY 1 - ALTA)

#### 📝 Arquivo: `core/tools/chart_tools.py` (NOVO)

```python
"""
Ferramentas LangChain para geração de gráficos interativos.
Integra dados do agente com visualizações Plotly.
"""

from langchain_core.tools import tool
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List
import pandas as pd

@tool
def gerar_grafico_vendas(
    dimensao: str,
    metrica: str = "quantidade",
    titulo: str = None
) -> Dict[str, Any]:
    """
    Gera gráfico de vendas segmentado por dimensão.
    
    Args:
        dimensao: "categoria", "produto", "periodo" ou "regiao"
        metrica: "quantidade", "valor" ou "margem"
        titulo: Título customizado do gráfico
        
    Returns:
        Dict com figura Plotly serializada
    """
    # 1. Buscar dados usando unified_data_tools
    # 2. Preparar DataFrame
    # 3. Gerar gráfico Plotly
    # 4. Retornar figura

@tool
def gerar_grafico_estoque(
    tipo: str = "disponivel",
    limite_superior: int = None
) -> Dict[str, Any]:
    """
    Gera gráfico de estoque disponível.
    
    Args:
        tipo: "disponivel", "minimo", "critico"
        limite_superior: Filtrar apenas produtos com estoque > limite
        
    Returns:
        Dict com figura Plotly
    """

@tool
def gerar_serie_temporal(
    metrica: str,
    periodo: str = "mes",
    dados: List[Dict] = None
) -> Dict[str, Any]:
    """
    Gera série temporal de métrica.
    
    Args:
        metrica: "vendas", "estoque", "margem"
        periodo: "dia", "semana", "mes", "trimestre"
        dados: Dados opcionais para processar
        
    Returns:
        Gráfico de linha com série temporal
    """

@tool
def gerar_comparacao(
    tipo_comparacao: str,
    categorias: List[str] = None,
    metrica: str = "quantidade"
) -> Dict[str, Any]:
    """
    Compara valores entre múltiplas dimensões.
    
    Args:
        tipo_comparacao: "produtos", "categorias", "periodos"
        categorias: Lista específica para filtrar
        metrica: Métrica a comparar
        
    Returns:
        Gráfico comparativo (barras, radar, etc)
    """

@tool
def gerar_analise_distribuicao(
    coluna: str,
    tipo: str = "histograma"
) -> Dict[str, Any]:
    """
    Analisa distribuição de dados.
    
    Args:
        coluna: Coluna a analisar (preco, estoque, etc)
        tipo: "histograma", "box", "violino", "scatter"
        
    Returns:
        Gráfico de distribuição
    """

@tool
def gerar_dashboard_produto(codigo_produto: str) -> Dict[str, Any]:
    """
    Gera dashboard completo de um produto.
    
    Args:
        codigo_produto: Código do produto
        
    Returns:
        Subgráficos: preço, estoque, categoria, tendência
    """
```

**Funções Utilitárias Necessárias:**
```python
def to_plotly_figure(fig) -> Dict[str, Any]:
    """Serializa figura Plotly para enviar ao frontend"""
    
def apply_theme(fig, theme: str = "default"):
    """Aplica tema visual consistente"""
    
def format_chart_labels(df: pd.DataFrame, labels_map: Dict):
    """Formata rótulos em português"""
    
def validate_data_for_chart(df: pd.DataFrame, chart_type: str):
    """Valida se dados são apropriados para tipo de gráfico"""
```

---

### Fase 2: Instruções do Agente (PRIORITY 2 - ALTA)

#### 📝 Arquivo: `core/prompts/chart_generation_prompt.txt` (NOVO)

```
Você é um assistente de BI especializado em gerar visualizações de dados.

QUANDO GERAR GRÁFICOS:
- Usuário pede: "mostrar", "visualizar", "gráfico", "comparar"
- Dados têm múltiplos registros (>5)
- Há dimensões e métricas claras
- Padrões ou tendências são visíveis

TIPOS DE GRÁFICO A USAR:
- Vendas por categoria → Gráfico de barras
- Evolução temporal → Gráfico de linhas
- Composição → Gráfico de pizza
- Comparação entre produtos → Gráfico de barras
- Distribuição de preços → Histograma
- Múltiplas métricas → Dashboard

FERRAMENTAS DISPONÍVEIS:
- gerar_grafico_vendas: Segmenta vendas
- gerar_grafico_estoque: Mostra disponibilidade
- gerar_serie_temporal: Tendências ao longo do tempo
- gerar_comparacao: Compara múltiplos itens
- gerar_analise_distribuicao: Mostra padrões
- gerar_dashboard_produto: Visão completa

SEMPRE:
1. Entenda o que usuário quer visualizar
2. Identifique as dimensões (categoria, periodo, produto)
3. Escolha a métrica correta (quantidade, valor, estoque)
4. Use ferramenta apropriada
5. Interprete o gráfico para o usuário
```

---

### Fase 3: Roteamento de Gráficos (PRIORITY 2 - MÉDIA)

#### 📝 Modificar: `core/agents/supervisor_agent.py`

```python
# Adicionar ao roteamento do supervisor:

def detect_chart_intent(query: str) -> bool:
    """Detecta se consulta requer visualização"""
    chart_keywords = [
        "gráfico", "visualizar", "mostrar", "comparar",
        "tendem", "evolução", "série", "dashboard",
        "tendência", "distribuição", "padrão"
    ]
    return any(kw in query.lower() for kw in chart_keywords)

# No roteamento:
if detect_chart_intent(query):
    route = "chart_generation"  # Novo nó de roteamento
else:
    route = "standard_query"
```

---

### Fase 4: Integração End-to-End (PRIORITY 3 - MÉDIA)

#### 📝 Modificar: `core/graph/graph_builder.py`

```python
# Adicionar nó novo:

def chart_generation_node_func(state: AgentState) -> dict:
    """Nó especializado para geração de gráficos"""
    logger.info("--- Chart Generation Node ---")
    
    # 1. Extrair intenção do usuário
    # 2. Chamar ferramentas de gráfico apropriadas
    # 3. Retornar figura Plotly
    # 4. Adicionar interpretação em texto

# Adicionar ao grafo:
workflow.add_node("chart_generation", chart_generation_node_func)
workflow.add_conditional_edges(
    "supervisor",
    route_to_chart_or_standard
)
```

---

### Fase 5: Componentes UI Aprimorados (PRIORITY 3 - BAIXA)

#### 📝 Modificar: `ui/ui_components.py`

```python
# Adicionar funções:

def create_chart_controls(fig):
    """Cria controles para personalizar gráfico"""
    col1, col2, col3 = st.columns(3)
    with col1:
        theme = st.selectbox("Tema", ["light", "dark", "plotly"])
    with col2:
        show_legend = st.checkbox("Mostrar legenda")
    with col3:
        export_format = st.selectbox("Exportar como", ["PNG", "HTML", "SVG"])
    return apply_chart_customization(fig, theme, show_legend)

def display_chart_insights(fig, data):
    """Exibe insights extraídos do gráfico"""
    st.subheader("📊 Insights")
    # Estatísticas, média, máximo, mínimo, etc
```

---

## 📊 Fluxo de Dados Completo (End-to-End)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USUÁRIO faz pergunta no chat Streamlit                   │
│    "Mostre estoque por categoria"                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. QUERY PROCESSOR recebe a pergunta                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. SUPERVISOR AGENT detecta intenção de gráfico             │
│    ✓ Identifica: tipo="chart", dimensão="categoria"        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. ROTEAMENTO envia para CHART GENERATION NODE              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. AGENTE chama FERRAMENTA: gerar_grafico_estoque()        │
│    Parâmetros: tipo="categoria"                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. FERRAMENTA executa:                                      │
│    a) Busca dados via unified_data_tools.get_produtos()   │
│    b) Agrupa por categoria                                  │
│    c) Cria DataFrame com colunas: categoria, estoque       │
│    d) Gera figura Plotly (barras)                          │
│    e) Serializa para dicionário JSON                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. AGENTE retorna interpretação + figura                    │
│    {"tipo": "chart", "figura": {...}, "texto": "..."}      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. STREAMLIT renderiza:                                     │
│    - Texto da interpretação                                 │
│    - Gráfico interativo (Plotly)                           │
│    - Botões para exportar (PNG, HTML, CSV)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Checklist de Implementação

### ✅ Fase 1: Ferramentas Base (1-2 dias)
- [ ] Criar `core/tools/chart_tools.py` com 6 ferramentas principais
- [ ] Implementar `gerar_grafico_vendas()` com dados reais
- [ ] Implementar `gerar_grafico_estoque()` com estoque real
- [ ] Implementar `gerar_serie_temporal()` com dados históricos
- [ ] Testar cada ferramenta isoladamente
- [ ] Validar serializações Plotly

### ✅ Fase 2: Integração com Agente (1 dia)
- [ ] Atualizar prompt do agente
- [ ] Registrar ferramentas em `core/agents/caculinha_bi_agent.py`
- [ ] Adicionar ferramentas ao LangChain ToolNode
- [ ] Testar detecção de intenção de gráfico

### ✅ Fase 3: Roteamento (1 dia)
- [ ] Modificar supervisor para detectar gráficos
- [ ] Criar nó novo em graph_builder.py
- [ ] Adicionar condicional routing
- [ ] Testar fluxo completo

### ✅ Fase 4: UI e Frontend (1 dia)
- [ ] Aprimorar renderização em Streamlit
- [ ] Adicionar controles de personalização
- [ ] Implementar insights automáticos
- [ ] Adicionar botões de export

### ✅ Fase 5: Testes e Polimento (1-2 dias)
- [ ] Teste end-to-end com perguntas reais
- [ ] Validar diferentes tipos de gráficos
- [ ] Testar com diferentes tamanhos de dados
- [ ] Otimizar performance
- [ ] Documentação

---

## 💡 Exemplos de Consultas Esperadas

```
USUÁRIO: "Qual é o estoque de cada categoria?"
ESPERADO: Gráfico de barras: Categoria vs Estoque

USUÁRIO: "Mostre a evolução de vendas nos últimos 6 meses"
ESPERADO: Gráfico de linhas com série temporal

USUÁRIO: "Compare os 10 produtos mais vendidos"
ESPERADO: Top 10 em gráfico de barras

USUÁRIO: "Dashboard do produto 719445"
ESPERADO: 4 subgráficos: Preço, Estoque, Categoria, Tendência

USUÁRIO: "Como está distribuído o preço dos produtos?"
ESPERADO: Histograma de distribuição de preços

USUÁRIO: "Qual a composição por categoria?"
ESPERADO: Gráfico de pizza com percentuais
```

---

## 🎯 Requisitos Técnicos Finais

| Componente | Status | Dependência | Prioridade |
|-----------|--------|-------------|-----------|
| Plotly | ✅ Instalado | - | - |
| Matplotlib | ✅ Instalado | - | - |
| Kaleido | ✅ Instalado | - | - |
| Pandas | ✅ Instalado | - | - |
| Streamlit | ✅ Instalado | - | - |
| chart_tools.py | ❌ Faltando | Plotly, Pandas | 🔴 ALTA |
| chart_prompt.txt | ❌ Faltando | - | 🔴 ALTA |
| chart_routing | ❌ Faltando | supervisor_agent | 🟡 MÉDIA |
| chart_node | ❌ Faltando | graph_builder | 🟡 MÉDIA |
| UI components | ⚠️ Parcial | chart_tools | 🟢 BAIXA |

---

## 📈 Impacto Esperado

### Antes (Atual)
❌ Agente só retorna tabelas/texto  
❌ Usuário precisa pedir explicitamente "em formato de tabela"  
❌ Insights não são visuales  
❌ Comparações são difíceis de entender  

### Depois (Com Implementação)
✅ Agente reconhece quando usar gráficos automaticamente  
✅ Gráficos interativos e personalizáveis  
✅ Insights visuais imediatos  
✅ Exportação em múltiplos formatos  
✅ Dashboard de produtos  
✅ Análises de distribuição e séries temporais  

---

## 🚀 Próximos Passos

1. **Validar esta análise** com stakeholders
2. **Iniciar Fase 1** criando `core/tools/chart_tools.py`
3. **Testar isoladamente** cada ferramenta
4. **Integrar com agente** uma de cada vez
5. **Realizar testes end-to-end** antes de deploy

---

## 📚 Referências

- Plotly Documentation: https://plotly.com/python/
- Streamlit Charts: https://docs.streamlit.io/library/api-reference/charts
- LangChain Tools: https://python.langchain.com/docs/modules/tools/
- Pandas for Data: https://pandas.pydata.org/docs/

