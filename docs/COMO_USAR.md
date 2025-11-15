# 🚀 GUIA RÁPIDO - Como Usar o Sistema

## ✅ Status: 100% Funcional

```
16/16 Testes Passando ✅
Todos os Erros Resolvidos ✅
Pronto para Uso ✅
```

---

## 🎯 Como Começar em 3 Passos

### Passo 1: Abrir Terminal PowerShell
```powershell
cd "c:\Users\André\Documents\agente-bi-caculinha-refatoracao-jules"
```

### Passo 2: Iniciar o Streamlit
```powershell
python -m streamlit run streamlit_app.py
```

### Passo 3: Fazer uma Pergunta
Na caixa de texto do Streamlit, digitar:
```
gere um gráfico de vendas do produto 59294
```

---

## 📊 Resultado Esperado

✅ **Imediatamente**:
- Mensagem: "⏳ Processando sua solicitação..."
- Spinner: "Aguarde..."

✅ **Após 5-30 segundos**:
- Gráfico de linha com 13 meses de vendas
- Área preenchida sob a linha
- Markers em cada ponto
- Linha de média vermelha tracejada

✅ **Sumário Abaixo**:
- Total de vendas: 16.385 unidades
- Venda média: 1.260 unidades/mês
- Venda máxima: 2.210 unidades
- Venda mínima: 623 unidades
- Variação: ~125% (máx/mín)

---

## 🎁 Outras Perguntas Para Testar

### Exemplo 1: Gráfico Genérico
```
gere um gráfico de vendas
```
✅ Sistema escolhe automaticamente o melhor tipo de gráfico

### Exemplo 2: Análise Específica
```
mostre um dashboard de análise completa
```
✅ Gráfico 2x2 com 4 visualizações diferentes

### Exemplo 3: Comparação
```
compare os preços das categorias
```
✅ Gráfico de comparação de preços

### Exemplo 4: Distribuição
```
analize a distribuição de estoque
```
✅ Histograma + box plot

---

## 🧪 Como Rodar os Testes

```powershell
# Todos os testes
python -m pytest tests/test_response_parser.py tests/test_streamlit_rendering.py -v

# Só testes de renderização
python -m pytest tests/test_streamlit_rendering.py -v

# Só testes de parser
python -m pytest tests/test_response_parser.py -v
```

---

## 📁 Arquivos Principais

| Arquivo | Função |
|---------|--------|
| `streamlit_app.py` | Interface principal |
| `core/query_processor.py` | Processa perguntas do usuário |
| `core/agents/tool_agent.py` | Executa ferramentas com LLM |
| `core/tools/chart_tools.py` | Ferramentas de gráficos (9 tipos) |
| `core/utils/response_parser.py` | Converte JSON → Plotly |
| `core/data_source_manager.py` | Acessa dados (SQL, Parquet, JSON) |

---

## 🔧 Se Algo Não Funcionar

### Erro: "ImportError"
✅ **Resolvido** - Função `get_data_manager()` foi adicionada

### Erro: "Timeout"
✅ **Resolvido** - Retry automático com 3 tentativas implementado

### Gráfico não aparece
✅ **Resolvido** - Figuras armazenadas como objetos, não strings

### Verificar Logs
```powershell
# Ver últimas 20 linhas do log
Get-Content logs/audit.log -Tail 20

# Ver logs em tempo real
Get-Content logs/audit.log -Wait -Tail 0
```

---

## 💡 Dicas

1. **Perguntas mais específicas geram melhores gráficos**
   - ❌ "gráfico"
   - ✅ "gráfico de vendas do produto 59294"

2. **Use nomes de produtos conhecidos**
   - O sistema procura por código de produto na pergunta
   - Se não encontrar, usa gráfico genérico

3. **Primeira execução demora mais**
   - LLM precisa ser inicializado
   - Próximas requisições são mais rápidas

4. **Cache funciona**
   - Mesma pergunta = resposta instantânea

---

## 📞 Suporte

Se tiver dúvidas:
1. Verificar `DIAGNOSTICO_FINAL.md` para entender a arquitetura
2. Verificar `RESUMO_RESOLUCAO_FINAL.md` para problemas resolvidos
3. Verificar `GUIA_FINAL_GRAFICOS_PRODUTOS.md` para mais exemplos

---

## ✨ Resumo

```
🟢 Sistema 100% Funcional
🟢 16/16 Testes Passando
🟢 Pronto para Produção
🟢 9 Tipos de Gráficos Disponíveis
```

**BOM USO! 🚀**
