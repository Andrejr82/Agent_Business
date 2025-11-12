# 📐 Arquitetura Visual: Gráficos no Agente BI

---

## 🏗️ Arquitetura Completa

```
┌──────────────────────────────────────────────────────────────────┐
│                    USUARIO NO STREAMLIT                          │
│              "Mostre estoque por categoria"                      │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                  STREAMLIT APP (streamlit_app.py)               │
│              - Captura pergunta                                  │
│              - Envia para QueryProcessor                         │
│              - Renderiza resultado (tabela/gráfico)            │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│              QUERY PROCESSOR (core/query_processor.py)           │
│              - Cache de resultados                              │
│              - Delega ao SupervisorAgent                         │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│           SUPERVISOR AGENT (core/agents/supervisor_agent.py)    │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ detect_chart_intent("Mostre estoque por categoria")     │   │
│  │ → True, então roteamento para CHART GENERATION NODE     │   │
│  └──────────────────────────────────────────────────────────┘   │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│          CACULINHA BI AGENT (core/agents/caculinha_bi_agent.py)  │
│                                                                   │
│  Ferramenta selecionada:                                         │
│  gerar_grafico_estoque(                                          │
│      tipo="disponivel",                                          │
│      categoria=None                                              │
│  )                                                               │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│         CHART TOOLS (core/tools/chart_tools.py) ⭐ NOVO          │
│                                                                   │
│  gerar_grafico_estoque():                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. get_produtos() → Busca dados SQL/Parquet            │   │
│  │ 2. df.groupby("categoria").sum("est_une")              │   │
│  │ 3. px.bar() → Cria figura Plotly                       │   │
│  │ 4. apply_theme() → Aplica estilos                      │   │
│  │ 5. Retorna figura serializada                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────────┐
│       UNIFIED DATA TOOLS (core/tools/unified_data_tools.py)      │
│                                                                   │
│  get_produtos() → Busca de múltiplas fontes:                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Tenta SQL Server (admmatao)                            │   │
│  │ → Se falhar, tenta Parquet (ADMAT.parquet)             │   │
│  │ → Se falhar, tenta JSON (fallback.json)                │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────┬─────────────────────────────────────────────────┘
                 │
        ┌────────┼────────┐
        │        │        │
        ▼        ▼        ▼
    ┌─────┐  ┌────────┐  ┌────┐
    │ SQL │  │Parquet │  │JSON│
    │ SRV │  │ Files  │  │Data│
    └─────┘  └────────┘  └────┘
        │        │        │
        └────────┼────────┘
                 │
                 ▼
          ┌────────────────┐
          │ DataFrame ✓    │
          │ com dados      │
          │ reais          │
          └────────────────┘
```

---

## 🔄 Ciclo de Processamento de Gráficos

```
USER INPUT
    │
    └─→ [Contém "gráfico", "mostrar", "visualizar"?]
        ├─ SIM: Ir para CHART GENERATION
        └─ NÃO: Ir para STANDARD QUERY
            │
            ▼
    ╔═══════════════════════════════════╗
    ║   CHART GENERATION NODE (NOVO)   ║
    ╚═══════════════════════════════════╝
            │
            ├─→ [Que tipo de visualização?]
            │   ├─ Estoque? → gerar_grafico_estoque()
            │   ├─ Vendas? → gerar_grafico_vendas()
            │   ├─ Comparação? → gerar_comparacao()
            │   ├─ Distribuição? → gerar_analise_distribuicao()
            │   ├─ Composição? → gerar_pizza()
            │   └─ Dashboard? → gerar_dashboard_produto()
            │
            └─→ [Executar ferramenta selecionada]
                │
                ├─→ Buscar dados
                ├─→ Estruturar DataFrame
                ├─→ Gerar figura Plotly
                ├─→ Aplicar tema
                └─→ Retornar ao agente
                    │
                    ▼
            ╔═══════════════════════════════════╗
            ║  STREAMLIT RENDERIZA GRÁFICO    ║
            ║  (Interativo, exportável)        ║
            ╚═══════════════════════════════════╝
```

---

## 🎯 Mapeamento de Ferramentas

```
PERGUNTA DO USUÁRIO              FERRAMENTA A USAR              RESULTADO
───────────────────────────────────────────────────────────────────────────

"Estoque por categoria"    →  gerar_grafico_estoque()    →  Bar horizontal

"Produtos mais vendidos"   →  gerar_grafico_vendas()     →  Bar vertical

"Compare categorias"       →  gerar_comparacao()         →  Bar agrupado

"Distribuição de preços"   →  gerar_analise_distribuicao() → Histograma

"Composição de produtos"   →  gerar_pizza()              →  Pizza/Donut

"Dashboard do produto X"   →  gerar_dashboard_produto()  →  4 subgráficos

"Estoque em risco"         →  gerar_grafico_estoque()    →  Apenas <10 un
                               (tipo="critico")

"Evolução temporal"        →  [FUTURO] serie_temporal()  →  Linhas
```

---

## 📦 Estrutura de Dados (DataFrame → Gráfico)

### Exemplo 1: Estoque por Categoria

```
INPUT SQL QUERY:
┌─────────────────┬──────────┐
│ categoria       │ est_une  │
├─────────────────┼──────────┤
│ BRINQUEDOS      │ 5423.12  │
│ TECIDOS         │ 8934.56  │
│ ELETRONICOS     │ 1245.89  │
│ LIVROS          │ 3456.78  │
└─────────────────┴──────────┘
         ↓ (groupby)
AFTER AGGREGATION:
┌─────────────────┬──────────┐
│ categoria       │ estoque  │
├─────────────────┼──────────┤
│ TECIDOS         │ 8934.56  │
│ BRINQUEDOS      │ 5423.12  │
│ LIVROS          │ 3456.78  │
│ ELETRONICOS     │ 1245.89  │
└─────────────────┴──────────┘
         ↓ (plotly.bar)
OUTPUT GRAPH:
┌────────────────────────────────────────┐
│  📊 Estoque por Categoria              │
├────────────────────────────────────────┤
│                                        │
│  TECIDOS    ████████████ 8934.56      │
│  BRINQUEDOS ███████░░░░░ 5423.12      │
│  LIVROS     █████░░░░░░░ 3456.78      │
│  ELETRÔN.   ███░░░░░░░░░ 1245.89      │
│                                        │
└────────────────────────────────────────┘
         ↓ (renderiza no Streamlit)
USUARIO VÊ:
✓ Gráfico interativo (hover, zoom)
✓ Legenda com valores exatos
✓ Botões para exportar (PNG, HTML)
```

### Exemplo 2: Dashboard de Produto

```
INPUT PRODUTO:
Código: 719445
Nome: TNT 40GRS 100%O LG 1.40
Categoria: TECIDOS
Estoque: 2543.85 UNE
Preço: R$ 45.50

         ↓ (subplots 2x2)

OUTPUT:
┌─────────────────────────────────────┐
│        Dashboard - Produto 719445   │
├──────────────────┬──────────────────┤
│ Código: 719445   │ Categoria:       │
│ 🔹 Indicador     │ TECIDOS  [■]    │
│                  │                  │
├──────────────────┼──────────────────┤
│ Estoque: 2543.85 │ Preço: R$ 45.50 │
│ [████████] GREEN │ [████░░░░░] 🔴  │
│                  │ Gauge/Agulha     │
└──────────────────┴──────────────────┘
```

---

## 🔌 Integração com Arquivos Existentes

```
ARQUIVOS JÁ EXISTENTES:
├─ streamlit_app.py              ✅ (já renderiza gráficos)
├─ core/query_processor.py       ✅ (ja delega queries)
├─ core/agents/supervisor_agent.py  ⚠️ (precisa add detector de charts)
├─ core/agents/caculinha_bi_agent.py ⚠️ (registrar chart_tools)
├─ core/tools/unified_data_tools.py  ✅ (busca dados)
├─ core/data_source_manager.py    ✅ (gerencia fontes)
├─ ui/ui_components.py            ✅ (componentes UI)
└─ core/graph/graph_builder.py     ⚠️ (opcional: add nó chart)

ARQUIVOS NOVOS A CRIAR:
├─ core/tools/chart_tools.py       🆕 (ferramentas)
├─ core/prompts/chart_system.txt   🆕 (instruções)
└─ tests/test_chart_tools.py       🆕 (testes)

MODIFICAÇÕES MÍNIMAS:
├─ core/agents/caculinha_bi_agent.py (import + register)
└─ core/agents/supervisor_agent.py   (add detector)
```

---

## 🎛️ Componentes Principais de chart_tools.py

```python
chart_tools.py (400+ linhas)
│
├─ IMPORTS
│  ├─ plotly.express (gráficos rápidos)
│  ├─ plotly.graph_objects (customização)
│  ├─ pandas (dados)
│  └─ langchain_core.tools (@tool decorator)
│
├─ UTILITÁRIOS
│  ├─ to_plotly_dict() - Serializa figura
│  ├─ apply_theme() - Aplica tema visual
│  ├─ format_large_numbers() - Formata 1500000 → 1.5M
│  └─ validate_dataframe() - Valida dados
│
├─ FERRAMENTAS (@tool)
│  ├─ gerar_grafico_vendas()
│  ├─ gerar_grafico_estoque()
│  ├─ gerar_comparacao()
│  ├─ gerar_analise_distribuicao()
│  ├─ gerar_pizza()
│  └─ gerar_dashboard_produto()
│
└─ EXPORT
   └─ CHART_TOOLS = [lista de todas]
```

---

## 📊 Tabela de Referência Rápida

| Função | Entrada | Saída | Caso de Uso |
|--------|---------|-------|-----------|
| `gerar_grafico_vendas()` | dimensão, métrica | Bar chart | Produtos por categoria |
| `gerar_grafico_estoque()` | tipo, categoria | Bar horizontal | Estoque disponível |
| `gerar_comparacao()` | tipo, top_n | Bar comparativo | Comparar múltiplos itens |
| `gerar_analise_distribuicao()` | coluna, tipo | Histograma/Box/Violino | Ver padrões |
| `gerar_pizza()` | dimensão | Donut chart | Composição percentual |
| `gerar_dashboard_produto()` | código | 4 subgráficos | Visão completa produto |

---

## 🔄 Fluxo de Dados Detalhado

```
┌─ REQUEST PHASE ─────────────────────┐
│ "Mostre estoque por categoria"     │
│ dimensao="categoria", tipo="disp"  │
└────────────────────────────────────┘
              │
              ▼
┌─ FETCH DATA PHASE ──────────────────┐
│ get_produtos(limit=1000)            │
│   ├─ Tenta SQL Server               │
│   ├─ Fallback: Parquet              │
│   └─ Fallback: JSON                 │
│ Result: DataFrame 1000 linhas       │
└────────────────────────────────────┘
              │
              ▼
┌─ PREPARE DATA PHASE ────────────────┐
│ df.groupby("categoria").sum(...)   │
│ Filter: est_une > 0                │
│ Sort: desc                          │
│ Result: 5 categorias com total     │
└────────────────────────────────────┘
              │
              ▼
┌─ VALIDATE PHASE ────────────────────┐
│ validate_dataframe_for_chart()      │
│ Check: >0 rows, required columns   │
│ Pass ✓ or Fail ✗                   │
└────────────────────────────────────┘
              │
              ▼
┌─ CREATE VISUALIZATION ──────────────┐
│ px.bar(                             │
│   x="categoria",                    │
│   y="estoque",                      │
│   title="Estoque por Categoria"    │
│ )                                   │
│ Result: Plotly Figure object       │
└────────────────────────────────────┘
              │
              ▼
┌─ APPLY STYLING ─────────────────────┐
│ apply_theme(fig)                    │
│ ├─ Font: Arial                      │
│ ├─ Template: plotly_white           │
│ ├─ Colors: Palette padrão           │
│ └─ Margins: Ajustados               │
│ Result: Styled Figure               │
└────────────────────────────────────┘
              │
              ▼
┌─ RETURN RESULT ─────────────────────┐
│ {                                   │
│   "status": "success",              │
│   "chart": <Figure object>,         │
│   "type": "bar_horizontal",         │
│   "records": 5,                     │
│   "categoria": "Todas"              │
│ }                                   │
└────────────────────────────────────┘
              │
              ▼
┌─ RENDER IN STREAMLIT ───────────────┐
│ st.plotly_chart(fig)               │
│ ├─ Interativo (hover, zoom)        │
│ ├─ Exportar (PNG, SVG, HTML)       │
│ ├─ Download de dados               │
│ └─ Responsivo                       │
└────────────────────────────────────┘
```

---

## 🚀 Sequência de Implementação

```
SEMANA 1: Foundation
├─ Segunda: Criar chart_tools.py + testes
├─ Terça: Registrar com agente
├─ Quarta: Testar integração
└─ Status: ✓ Ferramentas prontas

SEMANA 2: Integration
├─ Quinta: Ajustar prompts do agente
├─ Sexta: Adicionar roteamento supervisor
├─ Sábado: Testes end-to-end
└─ Status: ✓ Agente cria gráficos

SEMANA 3: Polish
├─ Domingo: Otimizar performance
├─ Segunda: Melhorar UX no Streamlit
└─ Status: ✓ Production-ready

RESULTADO FINAL:
✅ Agente cria gráficos automaticamente
✅ Múltiplos tipos de visualização
✅ Dados reais do SQL/Parquet
✅ Interativo e exportável
✅ Pronto para produção
```

---

## 🎓 Referência de Prompts para o Agente

```
Quando agente receber perguntas assim:

"Quantos produtos tem em cada categoria?"
→ Interpretar como: visualizar distribuição
→ Chamar: gerar_grafico_vendas(dimensao="categoria")

"Qual categoria tem mais estoque?"
→ Interpretar como: comparar estoque por categoria
→ Chamar: gerar_grafico_estoque()

"Mostre os 10 produtos mais em estoque"
→ Interpretar como: ranking/top N
→ Chamar: gerar_comparacao(tipo_comparacao="produtos")

"Como fica a distribuição de preços?"
→ Interpretar como: análise de distribuição
→ Chamar: gerar_analise_distribuicao(coluna="preco")

"Qual a composição por categoria?"
→ Interpretar como: percentual/pizza
→ Chamar: gerar_pizza(dimensao="categoria")

"Me mostre tudo sobre o produto 719445"
→ Interpretar como: dashboard completo
→ Chamar: gerar_dashboard_produto("719445")
```

