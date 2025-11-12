GUIA PRÁTICO - USANDO GRÁFICOS NO AGENTE BI
============================================

## 🎯 Como o Sistema Funciona

O agente BI agora detecta automaticamente quando você quer gráficos e os gera para você!

### Exemplo Prático:

**Você diz:** "Mostrar vendas por categoria"

**O agente:**
1. Detecta a palavra "vendas" + "categoria"
2. Seleciona `gerar_grafico_vendas_por_categoria()`
3. Busca dados de estoque
4. Gera gráfico com Plotly
5. Renderiza no Streamlit
6. Apresenta insights dos dados

**Você vê:** Um gráfico bonito e interativo com informações!

---

## 📝 Frases para Usar (Exemplos)

### Análise de Vendas
- "Mostrar as vendas por categoria"
- "Quais são as categorias mais vendidas?"
- "Visualizar distribuição de vendas"
- "Gráfico de vendas top 10"

### Análise de Estoque
- "Qual é o nível de estoque?"
- "Mostrar estoque disponível"
- "Visualizar produtos em estoque"
- "Estoque por produto"

### Análise de Preços
- "Como estão os preços?"
- "Comparação de preços por categoria"
- "Analise a precificação"
- "Mostrar preços médios"

### Análise Estatística
- "Analise o estoque para mim"
- "Distribuição de estoque"
- "Estatísticas de estoque"
- "Desvio padrão e média"

### Visão Holística
- "Quero ver tudo"
- "Dashboard completo"
- "Visão geral dos dados"
- "Análise completa"

---

## 🔧 Ferramentas Disponíveis (Internamente)

### 1. Gráfico de Vendas por Categoria

```python
# Chamado automaticamente quando detecta:
# "vendas", "categoria", "distribuição"

Tipo: Barras Horizontais
Parâmetros:
  - limite: quantas categorias mostrar (padrão: 10)
  - ordenar_por: "ascendente" ou "descendente"

Exemplo de Resultado:
  ├─ Eletrônicos: 250 produtos
  ├─ Alimentos: 320 produtos
  ├─ Livros: 150 produtos
  ├─ Vestuário: 400 produtos
  └─ Outros: 80 produtos
```

### 2. Gráfico de Estoque por Produto

```python
# Chamado quando detecta:
# "estoque", "disponível", "quantidade"

Tipo: Barras Verticais
Parâmetros:
  - limite: top N produtos (padrão: 15)
  - minimo_estoque: filtro mínimo

Exemplo de Resultado:
  ├─ Estoque Total: 2.341 unidades
  ├─ Estoque Médio: 87 unidades
  ├─ Estoque Máximo: 450 unidades
  └─ Tabela interativa com cada produto
```

### 3. Comparação de Preços por Categoria

```python
# Chamado quando detecta:
# "preço", "preços", "precificação"

Tipo: Combo (Barras + Linha)
Resultado:
  ├─ Preço Médio Geral: R$ 245,50
  ├─ Preço Máximo: R$ 2.500,00
  ├─ Preço Mínimo: R$ 15,00
  └─ Gráfico interativo com categorias
```

### 4. Análise de Distribuição de Estoque

```python
# Chamado quando detecta:
# "distribuição", "análise", "estatística"

Tipo: Histograma + Box Plot
Resultado:
  ├─ Média: 87
  ├─ Mediana: 75
  ├─ Desvio Padrão: 42
  ├─ Q1 (25%): 30
  └─ Q3 (75%): 120
```

### 5. Gráfico de Pizza por Categoria

```python
# Chamado quando detecta:
# "pizza", "proporção", "percentual"

Tipo: Pie Chart
Resultado:
  ├─ Eletrônicos: 25%
  ├─ Alimentos: 32%
  ├─ Livros: 15%
  ├─ Vestuário: 20%
  └─ Outros: 8%
```

### 6. Dashboard Completo

```python
# Chamado quando detecta:
# "dashboard", "tudo", "visão completa"

Tipo: Layout 2x2
Mostra:
  ├─ [Superior Esquerdo] Pizza por Categoria
  ├─ [Superior Direito] Top 10 Estoque
  ├─ [Inferior Esquerdo] Histograma Estoque
  └─ [Inferior Direito] Preços Médios
```

---

## 💡 Dicas de Uso

### 1. Seja Específico
✅ Bom: "Mostrar as 20 categorias com mais estoque"
❌ Ruim: "Mostrar dados"

### 2. Combine Intenções
✅ "Qual é o estoque e como são os preços?"
→ Agente pode gerar 2 gráficos

### 3. Use Palavras-Chave
✅ "gráfico", "visualizar", "mostrar", "análise"
✅ "categoria", "estoque", "preço", "distribuição"

### 4. Peça Insights
✅ "Analise o estoque e recomende ações"
→ Agente gera gráfico + recomendações

### 5. Filtros Naturais
✅ "Mostrar estoque apenas de eletrônicos"
✅ "Categorias com mais de 100 unidades"

---

## 🎨 Características dos Gráficos

Todos os gráficos incluem:

### Interatividade
- 🖱️ Hover com informações detalhadas
- 📌 Zoom e pan
- 👁️ Toggle de séries (mostrar/esconder)
- 📊 Diferentes vistas

### Estilo
- 🎨 Cores profissionais
- 📏 Escalas e fontes otimizadas
- 🌍 Template limpo e moderno
- 📝 Títulos e legendas claros

### Dados
- 📊 Resumo estatístico
- 🔢 Números precisos
- 📈 Tendências identificadas
- 💡 Insights incluídos

---

## ⚠️ Limitações e Notas

### Dados Requeridos
- O agente precisa que hajam **dados disponíveis** no sistema
- Verifica SQL Server, Parquet e JSON automaticamente
- Se nenhuma fonte tiver dados, retorna erro

### Colunas Esperadas
O sistema busca por:
- **Categoria:** "categoria"
- **Estoque:** "est_une" (Caculinha) ou similar
- **Preço:** "preco_38_percent" (Caculinha) ou similar
- **Nome:** "nome" ou "produto"

Se uma coluna não for encontrada, o gráfico não é gerado.

### Performance
- Gráficos processam até 5.000 linhas de dados
- Para grandes volumes, use filtros
- Limite padrão: 10-15 registros por gráfico

---

## 🔍 Diagnosticando Problemas

### "Erro: Coluna não encontrada"
```
Causa: Sistema não identificou coluna de categoria/estoque
Solução: Verifique nomes de colunas no banco de dados
```

### "Erro: Nenhuma tabela encontrada"
```
Causa: SQL Server ou Parquet indisponível
Solução: Verifique conexão com fontes de dados
```

### "Nenhum dado disponível"
```
Causa: Tabelas vazias ou dados insuficientes
Solução: Carregue dados primeiro via scripts de ETL
```

---

## 📚 Arquivos de Referência

Arquivo | Conteúdo
--------|----------
`core/tools/chart_tools.py` | Implementação das 6 ferramentas
`core/agents/tool_agent.py` | Agente com chart_tools registrado
`core/agents/supervisor_agent.py` | Detecção automática de intenção
`core/prompts/chart_system_prompt.txt` | Instruções para o LLM
`tests/test_chart_tools.py` | 10 testes - 100% sucesso
`docs/IMPLEMENTACAO_COMPLETA_GRAFICOS.md` | Documentação técnica completa

---

## 🚀 Integrando em sua Aplicação

### No Streamlit

```python
from streamlit_app import run_agent

# Seu código:
user_input = st.text_input("Sua pergunta:")
response = run_agent(user_input)

# Se for gráfico:
if response.get("chart_data"):
    st.plotly_chart(response["chart_data"], use_container_width=True)

# Se for texto:
if response.get("text"):
    st.write(response["text"])
```

### No Seu Código Python

```python
from core.agents.supervisor_agent import SupervisorAgent
from core.llm_adapter import OpenAILLMAdapter

# Inicializar
adapter = OpenAILLMAdapter()
supervisor = SupervisorAgent(adapter)

# Usar
resultado = supervisor.route_query("Mostrar vendas por categoria")

# Resultado contém:
# - chart_data: JSON Plotly
# - summary: Dados estatísticos
# - message: Resposta textual
```

---

## 📊 Exemplo Completo de Fluxo

```
Usuário digita no Streamlit:
"Mostre o estoque e analise a distribuição"
    ↓
SupervisorAgent detecta 2 requisições
    ↓
ToolAgent.process_query() é chamado
    ↓
LLM seleciona:
  1) gerar_grafico_estoque_por_produto()
  2) gerar_analise_distribuicao_estoque()
    ↓
Ambas as ferramentas executam
    ↓
Dois gráficos são gerados (JSON)
    ↓
Streamlit renderiza lado a lado
    ↓
Usuário vê:
  [Gráfico 1: Estoque]  |  [Gráfico 2: Distribuição]
  
  Com insights:
  "Estoque total de 2.341 unidades"
  "Distribuição normal com média 87"
```

---

## ✅ Checklist de Pronto para Uso

- [x] Ferramentas implementadas
- [x] Testes passando (10/10)
- [x] Integração completa
- [x] Detecção automática
- [x] Documentação pronta
- [x] Exemplos disponíveis
- [x] Pronto para produção

---

## 🎓 Conclusão

O sistema de gráficos está **totalmente funcional e integrado**!

Você agora pode:
✅ Fazer perguntas naturais sobre dados
✅ Receber gráficos bonitos e interativos
✅ Ter insights automáticos
✅ Exportar e compartilhar visualizações

**Basta pedir!** O agente BI faz o resto! 🎉

---

Criado em: 11 de Novembro de 2025
Status: ✅ Pronto para Produção
