# 🎯 PLANO DE MELHORIAS - CLIENTE SETOR DE BELEZA

## 📊 SITUAÇÃO ATUAL

### Análise Completa Realizada
- ✅ 698 produtos de beleza no catálogo
- ✅ 32 colunas de dados (vendas, estoque, margem, etc.)
- ✅ 11 tipos de gráficos Plotly interativos
- ✅ Chat conversacional com IA (Gemini)
- ✅ Dashboards multi-gráfico

### Gaps Críticos Identificados
- ❌ **Sem filtros interativos** (cliente não consegue filtrar categorias visualmente)
- ❌ **Tempo de resposta muito lento** (20-30 segundos)
- ❌ **Sem KPIs específicos de beleza** (validade, sazonalidade, giro)
- ❌ **Sem alertas automáticos** (ruptura, vencimento, anomalias)
- ❌ **Dados com problemas** (encoding, formatação)

---

## 🚀 ROADMAP DE IMPLEMENTAÇÃO

### 🔥 FASE 1: QUICK WINS (1-2 SEMANAS)

#### 1. Corrigir Qualidade dos Dados [CRÍTICO]

**Arquivo:** `scripts/limpar_dados_beleza.py`

```python
"""
Script para limpar e corrigir dados do Parquet
"""
import pandas as pd
from pathlib import Path

def limpar_dados_beleza():
    # Ler Parquet
    df = pd.read_parquet('data/parquet/Filial_Madureira.parquet')

    # 1. Corrigir encoding
    colunas_texto = ['DESCRIÇÃO', 'FABRICANTE', 'GRUPO']
    for col in colunas_texto:
        if col in df.columns:
            df[col] = df[col].str.encode('latin1').str.decode('utf-8', errors='ignore')

    # 2. Converter LUCRO TOTAL % para numérico
    if 'LUCRO TOTAL %' in df.columns:
        df['LUCRO TOTAL %'] = df['LUCRO TOTAL %'].str.replace('%', '').astype(float)

    # 3. Normalizar fabricantes (remover espaços extras, capitalizar)
    if 'FABRICANTE' in df.columns:
        df['FABRICANTE'] = df['FABRICANTE'].str.strip().str.upper()

    # 4. Garantir tipos corretos
    colunas_numericas = ['QTD', 'VENDA R$', 'CUSTO R$', 'LUCRO R$', 'SALDO']
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Salvar versão limpa
    df.to_parquet('data/parquet/Filial_Madureira_LIMPO.parquet', index=False)
    print(f"✓ Dados limpos: {df.shape[0]} linhas, {df.shape[1]} colunas")

if __name__ == '__main__':
    limpar_dados_beleza()
```

**Resultado esperado:** Dados consistentes, sem erros de encoding, prontos para análise.

---

#### 2. Adicionar Filtros Interativos à Interface [CRÍTICO]

**Arquivo:** `ui/filtros_interativos.py`

```python
"""
Componentes de filtros interativos para Streamlit
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any

def criar_filtros_sidebar(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Cria filtros na sidebar do Streamlit

    Returns:
        dict com filtros selecionados
    """
    st.sidebar.markdown("### 🔍 Filtros")

    filtros = {}

    # 1. Filtro de Categoria (GRUPO)
    if 'GRUPO' in df.columns:
        grupos_unicos = sorted(df['GRUPO'].dropna().unique())
        filtros['grupos'] = st.sidebar.multiselect(
            "Categorias",
            options=grupos_unicos,
            default=None,
            help="Selecione uma ou mais categorias"
        )

    # 2. Filtro de Fabricante
    if 'FABRICANTE' in df.columns:
        fabricantes_top = df['FABRICANTE'].value_counts().head(20).index.tolist()
        filtros['fabricantes'] = st.sidebar.multiselect(
            "Fabricantes",
            options=fabricantes_top,
            default=None
        )

    # 3. Slider de Margem Mínima
    if 'LUCRO TOTAL %' in df.columns:
        margem_min = float(df['LUCRO TOTAL %'].min())
        margem_max = float(df['LUCRO TOTAL %'].max())
        filtros['margem_minima'] = st.sidebar.slider(
            "Margem Mínima (%)",
            min_value=margem_min,
            max_value=margem_max,
            value=margem_min,
            step=1.0
        )

    # 4. Range de Estoque
    if 'SALDO' in df.columns:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            filtros['estoque_min'] = st.number_input(
                "Estoque Mín",
                min_value=0,
                value=0,
                step=1
            )
        with col2:
            filtros['estoque_max'] = st.number_input(
                "Estoque Máx",
                min_value=0,
                value=int(df['SALDO'].max()),
                step=10
            )

    # 5. Toggle: Mostrar apenas produtos em estoque
    filtros['apenas_em_estoque'] = st.sidebar.checkbox(
        "Apenas produtos em estoque (SALDO > 0)",
        value=False
    )

    # 6. Toggle: Mostrar apenas com vendas
    filtros['apenas_com_vendas'] = st.sidebar.checkbox(
        "Apenas produtos com vendas",
        value=False
    )

    return filtros

def aplicar_filtros(df: pd.DataFrame, filtros: Dict[str, Any]) -> pd.DataFrame:
    """
    Aplica filtros ao DataFrame
    """
    df_filtrado = df.copy()

    # Filtrar por categorias
    if filtros.get('grupos'):
        df_filtrado = df_filtrado[df_filtrado['GRUPO'].isin(filtros['grupos'])]

    # Filtrar por fabricantes
    if filtros.get('fabricantes'):
        df_filtrado = df_filtrado[df_filtrado['FABRICANTE'].isin(filtros['fabricantes'])]

    # Filtrar por margem
    if 'margem_minima' in filtros:
        df_filtrado = df_filtrado[df_filtrado['LUCRO TOTAL %'] >= filtros['margem_minima']]

    # Filtrar por range de estoque
    if 'estoque_min' in filtros and 'estoque_max' in filtros:
        df_filtrado = df_filtrado[
            (df_filtrado['SALDO'] >= filtros['estoque_min']) &
            (df_filtrado['SALDO'] <= filtros['estoque_max'])
        ]

    # Apenas em estoque
    if filtros.get('apenas_em_estoque'):
        df_filtrado = df_filtrado[df_filtrado['SALDO'] > 0]

    # Apenas com vendas
    if filtros.get('apenas_com_vendas'):
        df_filtrado = df_filtrado[df_filtrado['QTD'] > 0]

    return df_filtrado
```

**Integração no streamlit_app.py:**

```python
# Adicionar no início da função show_bi_assistant()
from ui.filtros_interativos import criar_filtros_sidebar, aplicar_filtros

def show_bi_assistant():
    # ... código existente ...

    # NOVO: Adicionar filtros
    data_manager = get_data_manager()
    df_completo = data_manager.get_data()

    filtros = criar_filtros_sidebar(df_completo)
    df_filtrado = aplicar_filtros(df_completo, filtros)

    # Mostrar estatísticas de filtros aplicados
    if len(df_filtrado) < len(df_completo):
        st.info(f"📊 Mostrando {len(df_filtrado)} de {len(df_completo)} produtos")
```

---

#### 3. Dashboard de KPIs Principais [ALTO IMPACTO]

**Arquivo:** `pages/7_Dashboard_KPIs_Beleza.py`

```python
"""
Dashboard executivo com KPIs principais do setor de beleza
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from core.data_source_manager import get_data_manager
from core import auth
from core.session_state import SESSION_STATE_KEYS

st.set_page_config(page_title="KPIs Beleza", page_icon="💄", layout="wide")

# Autenticação
if not st.session_state.get(SESSION_STATE_KEYS["AUTHENTICATED"]):
    auth.login()
    st.stop()

st.title("💄 Dashboard Executivo - Setor de Beleza")

# Carregar dados
@st.cache_data
def load_data():
    manager = get_data_manager()
    return manager.get_data()

df = load_data()

# Métricas principais em cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_produtos = len(df)
    st.metric(
        "Total de Produtos",
        f"{total_produtos:,}",
        help="Total de SKUs no catálogo"
    )

with col2:
    valor_estoque = df['VLR ESTOQUE VENDA'].sum()
    st.metric(
        "Valor Estoque (Venda)",
        f"R$ {valor_estoque:,.2f}",
        help="Valor total do estoque a preço de venda"
    )

with col3:
    margem_media = df['LUCRO TOTAL %'].mean()
    st.metric(
        "Margem Média",
        f"{margem_media:.1f}%",
        help="Margem média de todos os produtos"
    )

with col4:
    produtos_ruptura = len(df[df['SALDO'] <= 0])
    pct_ruptura = (produtos_ruptura / total_produtos) * 100
    st.metric(
        "Produtos em Ruptura",
        produtos_ruptura,
        delta=f"-{pct_ruptura:.1f}%",
        delta_color="inverse",
        help="Produtos com estoque zerado"
    )

st.divider()

# Gráficos principais
tab1, tab2, tab3 = st.tabs(["📊 Categorias", "💰 Margem", "📈 Sazonalidade"])

with tab1:
    st.subheader("Top 10 Categorias por Valor de Estoque")

    top_categorias = df.groupby('GRUPO').agg({
        'VLR ESTOQUE VENDA': 'sum',
        'ITEM': 'count'
    }).sort_values('VLR ESTOQUE VENDA', ascending=False).head(10)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_categorias.index,
        x=top_categorias['VLR ESTOQUE VENDA'],
        orientation='h',
        text=top_categorias['VLR ESTOQUE VENDA'].apply(lambda x: f'R$ {x:,.0f}'),
        textposition='auto',
        marker_color='#FF69B4'
    ))

    fig.update_layout(
        height=500,
        xaxis_title="Valor de Estoque (R$)",
        yaxis_title="Categoria",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Distribuição de Margem por Categoria")

    # Box plot de margem por categoria (top 10)
    top_10_grupos = df['GRUPO'].value_counts().head(10).index
    df_top = df[df['GRUPO'].isin(top_10_grupos)]

    fig = go.Figure()

    for grupo in top_10_grupos:
        df_grupo = df_top[df_top['GRUPO'] == grupo]
        fig.add_trace(go.Box(
            y=df_grupo['LUCRO TOTAL %'],
            name=grupo,
            boxmean='sd'
        ))

    fig.update_layout(
        height=500,
        yaxis_title="Margem (%)",
        xaxis_title="Categoria",
        template="plotly_white",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Vendas Mensais - Análise de Sazonalidade")

    # Somar vendas de todos os meses
    meses = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN',
             'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']

    colunas_vendas = [f'VENDA QTD {mes}' for mes in meses]
    vendas_mensais = df[colunas_vendas].sum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=meses,
        y=vendas_mensais.values,
        mode='lines+markers',
        name='Vendas',
        line=dict(color='#FF69B4', width=3),
        marker=dict(size=10),
        fill='tozeroy',
        fillcolor='rgba(255, 105, 180, 0.2)'
    ))

    # Adicionar linha de média
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

    # Identificar meses de pico e baixa
    mes_pico = meses[vendas_mensais.argmax()]
    mes_baixa = meses[vendas_mensais.argmin()]

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"🔥 **Pico de Vendas:** {mes_pico} ({vendas_mensais.max():,.0f} unidades)")
    with col2:
        st.warning(f"📉 **Menor Venda:** {mes_baixa} ({vendas_mensais.min():,.0f} unidades)")
```

---

### 🎯 FASE 2: FUNCIONALIDADES CRÍTICAS (2-4 SEMANAS)

#### 4. Sistema de Alertas Automáticos [CRÍTICO PARA BELEZA]

**Arquivo:** `core/alertas/sistema_alertas.py`

```python
"""
Sistema de alertas automáticos para o setor de beleza
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class SistemaAlertas:
    """
    Monitora métricas críticas e gera alertas
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.alertas = []

    def verificar_ruptura_estoque(self, threshold: int = 0) -> List[Dict]:
        """
        Alerta de produtos em ruptura (estoque <= threshold)
        """
        produtos_ruptura = self.df[self.df['SALDO'] <= threshold]

        if len(produtos_ruptura) > 0:
            self.alertas.append({
                'tipo': 'RUPTURA',
                'severidade': 'ALTA',
                'quantidade': len(produtos_ruptura),
                'mensagem': f"⚠️ {len(produtos_ruptura)} produtos em ruptura de estoque",
                'produtos': produtos_ruptura[['ITEM', 'DESCRIÇÃO', 'SALDO', 'GRUPO']].to_dict('records')
            })

        return self.alertas

    def verificar_margem_baixa(self, margem_minima: float = 20.0) -> List[Dict]:
        """
        Alerta de produtos com margem abaixo do mínimo
        """
        produtos_margem_baixa = self.df[self.df['LUCRO TOTAL %'] < margem_minima]

        if len(produtos_margem_baixa) > 0:
            self.alertas.append({
                'tipo': 'MARGEM_BAIXA',
                'severidade': 'MEDIA',
                'quantidade': len(produtos_margem_baixa),
                'mensagem': f"📉 {len(produtos_margem_baixa)} produtos com margem < {margem_minima}%",
                'produtos': produtos_margem_baixa[['ITEM', 'DESCRIÇÃO', 'LUCRO TOTAL %', 'VENDA R$']].to_dict('records')
            })

        return self.alertas

    def verificar_estoque_excessivo(self, dias_cobertura: int = 90) -> List[Dict]:
        """
        Alerta de produtos com estoque excessivo
        (mais de X dias de venda em estoque)
        """
        # Calcular vendas mensais médias
        meses = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN',
                 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
        colunas_vendas = [f'VENDA QTD {mes}' for mes in meses]

        self.df['VENDAS_MENSAIS_MEDIA'] = self.df[colunas_vendas].mean(axis=1)
        self.df['DIAS_COBERTURA'] = (self.df['SALDO'] / self.df['VENDAS_MENSAIS_MEDIA']) * 30

        produtos_excesso = self.df[self.df['DIAS_COBERTURA'] > dias_cobertura]

        if len(produtos_excesso) > 0:
            self.alertas.append({
                'tipo': 'ESTOQUE_EXCESSIVO',
                'severidade': 'MEDIA',
                'quantidade': len(produtos_excesso),
                'mensagem': f"📦 {len(produtos_excesso)} produtos com estoque > {dias_cobertura} dias",
                'produtos': produtos_excesso[['ITEM', 'DESCRIÇÃO', 'SALDO', 'DIAS_COBERTURA']].to_dict('records')
            })

        return self.alertas

    def verificar_produtos_sem_venda(self, meses_sem_venda: int = 3) -> List[Dict]:
        """
        Alerta de produtos sem venda nos últimos X meses
        """
        # Verificar últimos 3 meses (assumindo DEZ, NOV, OUT)
        ultimos_meses = ['DEZ', 'NOV', 'OUT'][:meses_sem_venda]
        colunas = [f'VENDA QTD {mes}' for mes in ultimos_meses]

        self.df['VENDAS_ULTIMOS_MESES'] = self.df[colunas].sum(axis=1)
        produtos_sem_venda = self.df[self.df['VENDAS_ULTIMOS_MESES'] == 0]

        if len(produtos_sem_venda) > 0:
            self.alertas.append({
                'tipo': 'SEM_VENDAS',
                'severidade': 'BAIXA',
                'quantidade': len(produtos_sem_venda),
                'mensagem': f"🛑 {len(produtos_sem_venda)} produtos sem venda em {meses_sem_venda} meses",
                'produtos': produtos_sem_venda[['ITEM', 'DESCRIÇÃO', 'SALDO', 'GRUPO']].to_dict('records')
            })

        return self.alertas

    def gerar_relatorio_alertas(self) -> pd.DataFrame:
        """
        Gera relatório consolidado de todos os alertas
        """
        # Executar todas as verificações
        self.verificar_ruptura_estoque()
        self.verificar_margem_baixa()
        self.verificar_estoque_excessivo()
        self.verificar_produtos_sem_venda()

        # Criar DataFrame de alertas
        if self.alertas:
            df_alertas = pd.DataFrame([
                {
                    'Tipo': a['tipo'],
                    'Severidade': a['severidade'],
                    'Quantidade': a['quantidade'],
                    'Mensagem': a['mensagem']
                }
                for a in self.alertas
            ])
            return df_alertas
        else:
            return pd.DataFrame()

    def obter_alertas_prioritarios(self, limite: int = 5) -> List[Dict]:
        """
        Retorna os alertas mais prioritários
        """
        # Ordenar por severidade: ALTA > MEDIA > BAIXA
        ordem_severidade = {'ALTA': 0, 'MEDIA': 1, 'BAIXA': 2}
        alertas_ordenados = sorted(
            self.alertas,
            key=lambda x: (ordem_severidade[x['severidade']], -x['quantidade'])
        )

        return alertas_ordenados[:limite]
```

**Integração no Dashboard:**

```python
# Adicionar em pages/7_Dashboard_KPIs_Beleza.py

from core.alertas.sistema_alertas import SistemaAlertas

# Após carregar dados
sistema_alertas = SistemaAlertas(df)
alertas_prioritarios = sistema_alertas.obter_alertas_prioritarios(limite=5)

# Exibir alertas no topo da página
if alertas_prioritarios:
    st.warning("### ⚠️ Alertas Importantes")

    for alerta in alertas_prioritarios:
        with st.expander(f"{alerta['mensagem']} - {alerta['severidade']}", expanded=True):
            if 'produtos' in alerta and len(alerta['produtos']) > 0:
                st.dataframe(pd.DataFrame(alerta['produtos']))
```

---

#### 5. Otimizar Performance (Reduzir de 30s para <5s) [CRÍTICO]

**Estratégias:**

**5.1 Cache Inteligente**

```python
# Arquivo: core/cache_otimizado.py

import streamlit as st
import pandas as pd
from functools import lru_cache

@st.cache_data(ttl=3600)  # Cache por 1 hora
def carregar_dados_completos():
    """
    Carrega dados uma vez e mantém em cache
    """
    from core.data_source_manager import get_data_manager
    manager = get_data_manager()
    return manager.get_data()

@st.cache_data(ttl=3600)
def calcular_metricas_agregadas(df: pd.DataFrame):
    """
    Calcula métricas agregadas uma vez
    """
    return {
        'total_produtos': len(df),
        'valor_estoque_total': df['VLR ESTOQUE VENDA'].sum(),
        'margem_media': df['LUCRO TOTAL %'].mean(),
        'produtos_ruptura': len(df[df['SALDO'] <= 0]),
        'categorias_unicas': df['GRUPO'].nunique(),
        'fabricantes_unicos': df['FABRICANTE'].nunique()
    }

@lru_cache(maxsize=128)
def get_top_categorias(n: int = 10):
    """
    Cache de top categorias
    """
    df = carregar_dados_completos()
    return df.groupby('GRUPO').agg({
        'VLR ESTOQUE VENDA': 'sum',
        'ITEM': 'count'
    }).sort_values('VLR ESTOQUE VENDA', ascending=False).head(n)
```

**5.2 Pré-processamento de Gráficos**

```python
# Arquivo: core/tools/chart_tools_optimized.py

from functools import wraps
import hashlib
import json

def cache_grafico(func):
    """
    Decorator para cachear gráficos gerados
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Criar hash dos parâmetros
        params_str = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        cache_key = hashlib.md5(params_str.encode()).hexdigest()

        # Verificar se gráfico já foi gerado
        if cache_key in st.session_state.get('grafico_cache', {}):
            return st.session_state['grafico_cache'][cache_key]

        # Gerar gráfico
        resultado = func(*args, **kwargs)

        # Armazenar em cache
        if 'grafico_cache' not in st.session_state:
            st.session_state['grafico_cache'] = {}
        st.session_state['grafico_cache'][cache_key] = resultado

        return resultado

    return wrapper

@cache_grafico
@tool
def gerar_grafico_vendas_por_categoria_otimizado(limite: int = 10):
    """
    Versão otimizada com cache
    """
    # ... código do gráfico ...
```

**5.3 Lazy Loading de Ferramentas**

```python
# Modificar core/agents/tool_agent.py

class ToolAgent:
    def __init__(self, llm_adapter: BaseLLMAdapter):
        self.llm_adapter = llm_adapter
        self.langchain_llm = CustomLangChainLLM(llm_adapter=self.llm_adapter)

        # NOVO: Carregar ferramentas sob demanda
        self._tools = None
        self._agent_executor = None

    @property
    def tools(self):
        """Lazy loading de ferramentas"""
        if self._tools is None:
            from core.tools.unified_data_tools import unified_tools
            from core.tools.date_time_tools import date_time_tools
            from core.tools.chart_tools import chart_tools
            self._tools = unified_tools + date_time_tools + chart_tools
        return self._tools

    @property
    def agent_executor(self):
        """Lazy loading do executor"""
        if self._agent_executor is None:
            self._agent_executor = self._create_agent_executor()
        return self._agent_executor
```

---

### 💎 FASE 3: DIFERENCIAIS COMPETITIVOS (4-8 SEMANAS)

#### 6. Dashboard de Validade de Produtos [EXCLUSIVO PARA BELEZA]

**Arquivo:** `pages/8_Dashboard_Validade.py`

```python
"""
Dashboard de controle de validade - CRÍTICO para cosméticos
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Validade de Produtos", page_icon="📅", layout="wide")

st.title("📅 Controle de Validade - Produtos de Beleza")

# NOTA: Este é um exemplo. Dados reais de validade precisam ser adicionados ao Parquet
# Colunas necessárias: DATA_FABRICACAO, DATA_VALIDADE, LOTE

st.warning("""
⚠️ **Implementação Necessária:**

Para ativar este dashboard, adicione estas colunas ao seu Parquet:
- `DATA_FABRICACAO` (data)
- `DATA_VALIDADE` (data)
- `LOTE` (texto)
- `SHELF_LIFE_MESES` (número)

**Prioridade:** CRÍTICA para setor de beleza
""")

# Simulação de dados (SUBSTITUIR por dados reais)
st.info("📊 **Dashboard simulado** - Aguardando dados de validade reais")

# Criar dados de exemplo
exemplo_df = pd.DataFrame({
    'Produto': ['Esmalte Vermelho', 'Creme Facial', 'Shampoo Keratina', 'Batom Rosa'],
    'Lote': ['L2024-001', 'L2024-002', 'L2024-003', 'L2024-004'],
    'Qtd_Estoque': [50, 120, 80, 45],
    'Data_Validade': pd.to_datetime(['2025-03-15', '2025-02-10', '2025-12-30', '2025-01-25']),
    'Dias_Restantes': [120, 55, 380, 40]
})

# Cards de alertas
col1, col2, col3 = st.columns(3)

with col1:
    vencendo_30 = len(exemplo_df[exemplo_df['Dias_Restantes'] <= 30])
    st.metric("Vencendo em 30 dias", vencendo_30, delta="Urgente", delta_color="inverse")

with col2:
    vencendo_60 = len(exemplo_df[(exemplo_df['Dias_Restantes'] > 30) & (exemplo_df['Dias_Restantes'] <= 60)])
    st.metric("Vencendo em 60 dias", vencendo_60, delta="Atenção", delta_color="off")

with col3:
    valor_risco = 15000  # Exemplo
    st.metric("Valor em Risco (30d)", f"R$ {valor_risco:,.2f}", delta="Alta prioridade", delta_color="inverse")

st.divider()

# Tabela de produtos críticos
st.subheader("🚨 Produtos Críticos (Vencimento < 60 dias)")
produtos_criticos = exemplo_df[exemplo_df['Dias_Restantes'] <= 60].copy()

if not produtos_criticos.empty:
    # Adicionar coluna de status
    def get_status(dias):
        if dias <= 30:
            return '🔴 URGENTE'
        elif dias <= 60:
            return '🟡 ATENÇÃO'
        else:
            return '🟢 OK'

    produtos_criticos['Status'] = produtos_criticos['Dias_Restantes'].apply(get_status)

    st.dataframe(
        produtos_criticos,
        column_config={
            "Status": st.column_config.TextColumn("Status", width="small"),
            "Data_Validade": st.column_config.DateColumn("Validade", format="DD/MM/YYYY"),
            "Dias_Restantes": st.column_config.ProgressColumn(
                "Dias Restantes",
                min_value=0,
                max_value=90,
                format="%d dias"
            )
        },
        use_container_width=True,
        hide_index=True
    )

    # Ações recomendadas
    st.subheader("💡 Ações Recomendadas")

    for idx, row in produtos_criticos.iterrows():
        if row['Dias_Restantes'] <= 30:
            st.error(f"**{row['Produto']}** (Lote: {row['Lote']}) - Vence em {row['Dias_Restantes']} dias")
            st.markdown(f"➡️ **Ação:** Promoção urgente de {row['Qtd_Estoque']} unidades")
        elif row['Dias_Restantes'] <= 60:
            st.warning(f"**{row['Produto']}** (Lote: {row['Lote']}) - Vence em {row['Dias_Restantes']} dias")
            st.markdown(f"➡️ **Ação:** Considere desconto progressivo para {row['Qtd_Estoque']} unidades")
else:
    st.success("✅ Nenhum produto crítico no momento")

# Gráfico de timeline
st.subheader("📊 Timeline de Vencimentos")

fig = go.Figure()

cores = {
    'URGENTE': '#FF4444',
    'ATENÇÃO': '#FFAA00',
    'OK': '#00CC66'
}

for idx, row in exemplo_df.iterrows():
    status = 'URGENTE' if row['Dias_Restantes'] <= 30 else 'ATENÇÃO' if row['Dias_Restantes'] <= 60 else 'OK'

    fig.add_trace(go.Scatter(
        x=[row['Data_Validade']],
        y=[row['Produto']],
        mode='markers+text',
        marker=dict(size=15, color=cores[status]),
        text=f"{row['Dias_Restantes']}d",
        textposition="middle right",
        name=status,
        showlegend=False
    ))

# Linha do hoje
hoje = datetime.now()
fig.add_vline(x=hoje, line_dash="dash", line_color="gray", annotation_text="Hoje")

fig.update_layout(
    height=400,
    xaxis_title="Data de Validade",
    yaxis_title="Produto",
    template="plotly_white",
    hovermode='closest'
)

st.plotly_chart(fig, use_container_width=True)
```

---

#### 7. Análise Preditiva com Prophet [DIFERENCIAL]

**Arquivo:** `core/forecasting/previsao_vendas.py`

```python
"""
Previsão de vendas usando Facebook Prophet
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False
    logging.warning("Prophet não instalado. Instale com: pip install prophet")

logger = logging.getLogger(__name__)

class PrevisaoVendas:
    """
    Previsão de vendas para produtos de beleza
    Considera sazonalidade e tendências
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df

        if not HAS_PROPHET:
            raise ImportError("Prophet não está instalado")

    def preparar_dados_mensais(self, codigo_produto: int = None) -> pd.DataFrame:
        """
        Prepara dados no formato do Prophet (ds, y)
        """
        meses = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN',
                 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']

        # Criar datas (assumindo ano 2024)
        datas = pd.date_range(start='2024-01-01', periods=12, freq='MS')

        if codigo_produto:
            # Vendas de produto específico
            produto = self.df[self.df['ITEM'] == codigo_produto]
            if produto.empty:
                raise ValueError(f"Produto {codigo_produto} não encontrado")

            colunas_vendas = [f'VENDA QTD {mes}' for mes in meses]
            vendas = produto[colunas_vendas].values[0]
        else:
            # Vendas totais
            colunas_vendas = [f'VENDA QTD {mes}' for mes in meses]
            vendas = self.df[colunas_vendas].sum().values

        # Criar DataFrame para Prophet
        df_prophet = pd.DataFrame({
            'ds': datas,
            'y': vendas
        })

        return df_prophet

    def prever_proximo_trimestre(
        self,
        codigo_produto: int = None,
        incluir_sazonalidade: bool = True
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Prevê vendas para os próximos 3 meses

        Returns:
            (previsoes, metricas)
        """
        # Preparar dados
        df_prophet = self.preparar_dados_mensais(codigo_produto)

        # Configurar modelo
        model = Prophet(
            yearly_seasonality=incluir_sazonalidade,
            weekly_seasonality=False,
            daily_seasonality=False,
            changepoint_prior_scale=0.05  # Flexibilidade para tendências
        )

        # Treinar modelo
        model.fit(df_prophet)

        # Criar dataframe futuro (próximos 3 meses)
        future = model.make_future_dataframe(periods=3, freq='MS')

        # Fazer previsão
        forecast = model.predict(future)

        # Extrair previsões dos próximos 3 meses
        previsoes_futuras = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(3)

        # Calcular métricas
        metricas = {
            'media_prevista': previsoes_futuras['yhat'].mean(),
            'total_previsto': previsoes_futuras['yhat'].sum(),
            'intervalo_confianca_min': previsoes_futuras['yhat_lower'].sum(),
            'intervalo_confianca_max': previsoes_futuras['yhat_upper'].sum(),
            'tendencia': 'crescimento' if forecast['trend'].iloc[-1] > forecast['trend'].iloc[0] else 'declínio'
        }

        return previsoes_futuras, metricas

    def identificar_sazonalidade(self, codigo_produto: int = None) -> Dict:
        """
        Identifica padrões sazonais
        """
        df_prophet = self.preparar_dados_mensais(codigo_produto)

        # Identificar mês de pico e baixa
        mes_pico = df_prophet.loc[df_prophet['y'].idxmax(), 'ds'].strftime('%B')
        mes_baixa = df_prophet.loc[df_prophet['y'].idxmin(), 'ds'].strftime('%B')

        # Calcular índice de sazonalidade
        media_vendas = df_prophet['y'].mean()
        indice_sazonalidade = (df_prophet['y'].std() / media_vendas) * 100

        return {
            'mes_pico': mes_pico,
            'vendas_pico': df_prophet['y'].max(),
            'mes_baixa': mes_baixa,
            'vendas_baixa': df_prophet['y'].min(),
            'indice_sazonalidade': indice_sazonalidade,
            'interpretacao': self._interpretar_sazonalidade(indice_sazonalidade)
        }

    def _interpretar_sazonalidade(self, indice: float) -> str:
        """
        Interpreta o índice de sazonalidade
        """
        if indice < 20:
            return "Vendas estáveis ao longo do ano"
        elif indice < 40:
            return "Sazonalidade moderada"
        else:
            return "Sazonalidade forte - planejar estoque com atenção"
```

**Adicionar em requirements.txt:**
```
prophet
pystan==2.19.1.1
```

---

## 📋 CHECKLIST DE IMPLEMENTAÇÃO

### Semana 1-2: Quick Wins
- [ ] Script de limpeza de dados (`scripts/limpar_dados_beleza.py`)
- [ ] Filtros interativos na UI (`ui/filtros_interativos.py`)
- [ ] Dashboard de KPIs principais (`pages/7_Dashboard_KPIs_Beleza.py`)

### Semana 3-4: Funcionalidades Críticas
- [ ] Sistema de alertas automáticos (`core/alertas/sistema_alertas.py`)
- [ ] Otimização de performance (cache, lazy loading)
- [ ] Integração de alertas no dashboard

### Semana 5-8: Diferenciais
- [ ] Dashboard de validade (`pages/8_Dashboard_Validade.py`)
- [ ] Sistema de previsão com Prophet (`core/forecasting/previsao_vendas.py`)
- [ ] Adicionar colunas de validade ao Parquet

---

## 💰 RETORNO ESPERADO PARA O CLIENTE

### Ganhos Quantificáveis

1. **Redução de Perdas por Validade:**
   - Atual: ~5-10% de produtos vencidos (estimativa)
   - Meta: <2% com dashboard de validade
   - **Economia:** R$ 5.000 - R$ 10.000/mês

2. **Otimização de Estoque:**
   - Redução de 20% em capital parado
   - Melhoria de 15% no giro de estoque
   - **Economia:** R$ 15.000 - R$ 30.000/mês

3. **Aumento de Margem:**
   - Identificação de produtos com margem baixa
   - Ajuste de preços baseado em dados
   - **Ganho:** +2-3% na margem média = R$ 10.000/mês

4. **Redução de Ruptura:**
   - Alertas automáticos previnem perda de vendas
   - **Ganho:** R$ 5.000 - R$ 15.000/mês

**TOTAL ESTIMADO: R$ 35.000 - R$ 65.000/mês**

### Ganhos Qualitativos

- ✅ Decisões baseadas em dados, não intuição
- ✅ Tempo economizado (horas de análise manual → minutos)
- ✅ Visibilidade total do negócio em tempo real
- ✅ Vantagem competitiva sobre concorrentes

---

## 🎯 PRÓXIMOS PASSOS IMEDIATOS

1. **Validar com o cliente:**
   - Mostrar esta análise
   - Confirmar prioridades
   - Alinhar expectativas de prazo

2. **Coletar dados adicionais:**
   - Data de fabricação/validade dos produtos
   - Lote de produtos
   - Metas de margem por categoria

3. **Começar Fase 1:**
   - Limpar dados (Dia 1)
   - Adicionar filtros (Dias 2-3)
   - Dashboard de KPIs (Dias 4-7)

4. **Apresentar MVP:**
   - Após 2 semanas, mostrar ao cliente
   - Coletar feedback
   - Ajustar roadmap

---

## 📞 SUPORTE TÉCNICO

Para questões técnicas sobre implementação:
- Documentação completa em `CLAUDE.md`
- Guias específicos em `docs/`
- Deployment em `Deploy_Supabase.md`

**Objetivo:** Entregar a melhor solução de BI conversacional do mercado para o setor de beleza! 💄✨
