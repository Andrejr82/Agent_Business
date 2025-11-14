## 🎯 GUIA FINAL - COMO USAR GRÁFICOS DE PRODUTOS

### 📋 Regra de Ouro do Sistema

Quando o usuário faz uma requisição com:
- **Produto específico** (código de produto) 
- **Pedido de gráfico/análise/visualização**

**→ Sistema DEVE chamar: `gerar_grafico_vendas_mensais_produto(codigo_produto=CODIGO)`**

---

### ✅ Exemplos que FUNCIONAM Agora

```
Usuário: "gere um gráfico de vendas do produto 59294"
Resultado: ✅ Gráfico de linha mensal (13 meses)

Usuário: "mostrar vendas mensais do produto 59294"
Resultado: ✅ Gráfico de linha com trend

Usuário: "análise mensal do produto 59294"  
Resultado: ✅ Gráfico com estatísticas (total, média, max, min)

Usuário: "vendas por mês do produto 59294"
Resultado: ✅ Gráfico de série temporal

Usuário: "gráfico temporal do produto 59294"
Resultado: ✅ Gráfico com linha e markers
```

---

### 🔍 Como o Sistema Agora DETECTA

#### 1. **SupervisorAgent**
Procura por palavras-chave:
- `gráfico`, `grafico`
- `produto`, `sku`, `código`
- `temporal`, `série`, `mensal`, `mês`
- `vendas`, `análise`, `visualizar`

Se encontra 2+ palavras-chave → **Reconhece como pedido de gráfico**

#### 2. **ToolAgent**
Recebe instrução explícita:
```
"Você é assistente de BI especializado em gráficos.
REGRA: Produto específico + gráfico → 
gerar_grafico_vendas_mensais_produto(codigo_produto=N)"
```

#### 3. **gerar_grafico_automatico**
Se chamada, detecta:
- Número na descrição → Extrai código
- Palavras como "mensal", "temporal" → Chama nova ferramenta
- Fallback automático se falhar

---

### 📊 O que a Ferramenta Retorna

```json
{
  "status": "success",
  "chart_type": "line_temporal_mensal",
  "chart_data": "...figura Plotly JSON...",
  "summary": {
    "codigo_produto": 59294,
    "total_vendas": 16385,
    "venda_media": 1260.38,
    "venda_maxima": 2210,
    "venda_minima": 623,
    "mes_maior_venda": "Mês 06",
    "mes_menor_venda": "Parcial",
    "variacao": 125.91,
    "meses_analisados": 13,
    "produto_info": {
      "nome_produto": "PAPEL CHAMEX A4 75GRS",
      "nome_categoria": "OFFICE",
      "une_nome": "ITA"
    },
    "dados_mensais": {
      "Mês 01": 1302,
      "Mês 02": 871,
      ...
      "Parcial": 623
    }
  }
}
```

---

### 🔄 Fluxo Completo

```
USUÁRIO
   ↓
"gráfico de vendas do produto 59294"
   ↓
SupervisorAgent._detect_chart_intent()
   ├─ Encontra: "gráfico" ✓
   ├─ Encontra: "vendas" ✓
   ├─ Encontra: "produto" ✓
   └─ Resultado: chart_intent = TRUE
   ↓
ToolAgent.process_query()
   ├─ Executa com prompt explícito
   ├─ Detecta produto 59294
   ├─ Detecta tipo "gráfico"
   └─ Chama: gerar_grafico_vendas_mensais_produto(59294)
   ↓
gerar_grafico_vendas_mensais_produto()
   ├─ Carrega dados de ADMAT_REBUILT.parquet
   ├─ Encontra 35 registros para código 59294
   ├─ Extrai colunas: mes_01, mes_02, ..., mes_12, mes_parcial
   ├─ Agrega vendas por mês
   ├─ Cria gráfico de linha
   ├─ Calcula estatísticas
   └─ Retorna JSON sucesso
   ↓
response_parser.parse_agent_response()
   ├─ Detecta JSON com "chart_data"
   ├─ Converte JSON → go.Figure()
   └─ Retorna: ("chart", {...})
   ↓
streamlit_app.py
   ├─ Detecta tipo "chart"
   ├─ Renderiza go.Figure() com st.plotly_chart()
   └─ USUÁRIO VÊ O GRÁFICO ✅
```

---

### 🧪 Testes Confirmam

```
✅ test_chart_tools_disponibilidade
   └─ 9 ferramentas disponíveis

✅ test_gerar_grafico_vendas_mensais_produto
   └─ Ferramenta executa com sucesso
   └─ Retorna estrutura esperada

✅ test_gerar_grafico_automatico
   └─ Detecção automática funcionando

✅ Todos 20 testes passando
```

---

### 🚨 Se Ainda Não Funcionar

1. **Limpe o cache**:
   ```bash
   # Remove cache Python
   find . -type d -name __pycache__ -exec rm -r {} +
   find . -name "*.pyc" -delete
   ```

2. **Execute diagnóstico**:
   ```bash
   python -m scripts.diagnostico_dados
   ```

3. **Verifique os logs**:
   - Procure por "gerar_grafico_vendas_mensais_produto"
   - Deve haver log: "Dados carregados de ADMAT_REBUILT"

4. **Teste direto**:
   ```python
   from core.tools.chart_tools import gerar_grafico_vendas_mensais_produto
   resultado = gerar_grafico_vendas_mensais_produto.invoke({
       "codigo_produto": 59294,
       "unidade_filtro": ""
   })
   print(resultado["status"])  # Deve ser "success"
   ```

---

### ✨ Resumo das Mudanças

| Componente | Mudança |
|-----------|---------|
| `core/tools/chart_tools.py` | Nova ferramenta +300 linhas |
| `core/agents/tool_agent.py` | Prompt com regra explícita |
| `core/agents/supervisor_agent.py` | Palavras-chave atualizadas |
| `core/prompts/chart_system_prompt.txt` | Lista nova ferramenta |
| `tests/test_chart_tools.py` | Novo teste |
| Status | ✅ 20/20 testes passando |

---

### 🎯 Resultado Final

```
ANTES: ❌ "Os dados não estão em série temporal"
DEPOIS: ✅ Gráfico renderizado com sucesso!
```

**Sistema 100% funcional para gráficos de produtos!** 🚀
