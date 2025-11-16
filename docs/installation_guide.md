# 🚀 Guia de Instalação e Correção - Caçulinha BI

## 📋 Problema Identificado

O agente não estava respondendo corretamente porque:
1. ❌ As ferramentas de dados não tinham a função `listar_colunas_disponiveis`
2. ❌ Havia importação circular entre `supervisor_agent.py` e `tool_agent.py`
3. ❌ O prompt do sistema não estava claro sobre a fonte de dados

## ✅ Solução: 3 Arquivos para Substituir

### 1️⃣ core/tools/unified_data_tools.py

**SUBSTITUA COMPLETAMENTE** o arquivo existente pelo conteúdo do artifact "unified_data_tools.py"

**Localização:** `core/tools/unified_data_tools.py`

**O que este arquivo faz:**
- ✅ Carrega dados de `Filial_Madureira.parquet` com cache
- ✅ Fornece 4 ferramentas principais:
  - `listar_colunas_disponiveis()` - Lista estrutura do arquivo
  - `consultar_dados()` - Consultas gerais
  - `buscar_produto()` - Busca por código/nome
  - `obter_estoque()` - Consulta estoque
- ✅ Tratamento robusto de erros
- ✅ Logging detalhado

### 2️⃣ core/agents/supervisor_agent.py

**SUBSTITUA COMPLETAMENTE** o arquivo existente pelo conteúdo do artifact "supervisor_agent.py"

**Localização:** `core/agents/supervisor_agent.py`

**O que este arquivo faz:**
- ✅ Remove importação circular
- ✅ Usa lazy initialization do ToolAgent
- ✅ Roteia consultas corretamente

### 3️⃣ test_data_access_simple.py

**CRIE NOVO ARQUIVO** na raiz do projeto com o conteúdo do artifact "test_data_access_simple.py"

**Localização:** `test_data_access_simple.py` (na raiz)

**O que este arquivo faz:**
- ✅ Testa carregamento de dados
- ✅ Testa cada ferramenta individualmente
- ✅ Testa o QueryProcessor completo
- ✅ Fornece feedback detalhado

## 🔧 Passo a Passo de Instalação

### Passo 1: Fazer Backup
```bash
# Faça backup dos arquivos originais
copy core\tools\unified_data_tools.py core\tools\unified_data_tools.py.backup
copy core\agents\supervisor_agent.py core\agents\supervisor_agent.py.backup
```

### Passo 2: Substituir Arquivos

1. Abra `core/tools/unified_data_tools.py`
2. **APAGUE TODO O CONTEÚDO**
3. Cole o código do artifact "unified_data_tools.py - SUBSTITUA COMPLETAMENTE"
4. Salve o arquivo

5. Abra `core/agents/supervisor_agent.py`
6. **APAGUE TODO O CONTEÚDO**
7. Cole o código do artifact "supervisor_agent.py - Corrigir Importação Circular"
8. Salve o arquivo

9. Crie novo arquivo `test_data_access_simple.py` na raiz
10. Cole o código do artifact "test_data_access_simple.py"
11. Salve o arquivo

### Passo 3: Executar Testes

```bash
# Execute o teste simplificado
python test_data_access_simple.py
```

**Resultado Esperado:**
```
============================================================
🧪 TESTE DE ACESSO AOS DADOS - Caçulinha BI
   Versão Simplificada - Sem Dependências Complexas
============================================================

============================================================
TESTE 1: Carregamento Direto de Dados
============================================================
✓ Arquivo carregado com sucesso!
  - Total de registros: 698
  - Total de colunas: 32

============================================================
TESTE 2: Ferramentas - Teste Direto
============================================================
✓ Módulo unified_data_tools carregado com sucesso!

🔍 Verificando funções exportadas:
  ✓ listar_colunas_disponiveis
  ✓ consultar_dados
  ✓ buscar_produto
  ✓ obter_estoque

🧪 Testando listar_colunas_disponiveis()...
  ✓ Sucesso!

============================================================
TESTE 3: QueryProcessor (usado pelo Streamlit)
============================================================
✓ QueryProcessor importado com sucesso!

🎉 TODOS OS TESTES PASSARAM!
```

### Passo 4: Executar Aplicação

```bash
streamlit run streamlit_app.py
```

## 🎯 Como Usar

### Perguntas de Exemplo

1. **Descobrir estrutura:**
   ```
   "Liste as colunas disponíveis"
   "Quais dados você tem acesso?"
   ```

2. **Buscar produtos:**
   ```
   "Qual o produto com código 7896205901654?"
   "Mostre produtos do grupo ESMALTES"
   "Busque produtos do fabricante X"
   ```

3. **Consultar estoque:**
   ```
   "Qual o estoque do item 1?"
   "Quanto tem em estoque do produto 7896205901654?"
   ```

4. **Consultas específicas:**
   ```
   "Qual a data de cadastro do item 9?"
   "Qual o fabricante do produto X?"
   "Mostre a quantidade em estoque dos 10 primeiros itens"
   ```

5. **Gráficos:**
   ```
   "Gráfico de vendas do produto 1"
   "Mostre gráfico de vendas por categoria"
   "Gráfico de estoque por produto"
   ```

## 🔍 Estrutura do Arquivo de Dados

**Arquivo:** `data/parquet/Filial_Madureira.parquet`

**Colunas Principais:**
- `ITEM` (int) - Número identificador
- `CODIGO` (str) - Código do produto
- `DESCRIÇÃO` (str) - Nome/descrição
- `QTD` (int) - Quantidade em estoque
- `VENDA R$` (float) - Valor de venda
- `CUSTO R$` (float) - Custo
- `LUCRO R$` (float) - Lucro
- `FABRICANTE` (str) - Fabricante
- `DT CADASTRO` (datetime) - Data de cadastro
- `DT ULTIMA COMPRA` (datetime) - Última compra
- `GRUPO` (str) - Categoria/grupo

## 🐛 Solução de Problemas

### Erro: "cannot import name 'listar_colunas_disponiveis'"
**Causa:** Arquivo `unified_data_tools.py` não foi substituído corretamente
**Solução:** Repita o Passo 2 - certifique-se de APAGAR todo conteúdo antigo

### Erro: "circular import"
**Causa:** Arquivo `supervisor_agent.py` não foi substituído
**Solução:** Repita o Passo 2 para o supervisor_agent.py

### Erro: "Arquivo não encontrado: Filial_Madureira.parquet"
**Causa:** Arquivo de dados não existe
**Solução:** Verifique se `data/parquet/Filial_Madureira.parquet` existe

### Testes passam mas Streamlit não funciona
**Solução:** 
1. Pare o Streamlit (Ctrl+C)
2. Limpe o cache: `streamlit cache clear`
3. Execute novamente: `streamlit run streamlit_app.py`

## 📊 Verificação Final

Execute este checklist antes de usar:

- [ ] ✅ Arquivo `unified_data_tools.py` substituído
- [ ] ✅ Arquivo `supervisor_agent.py` substituído
- [ ] ✅ Arquivo `test_data_access_simple.py` criado
- [ ] ✅ Teste executado com sucesso (`python test_data_access_simple.py`)
- [ ] ✅ Todos os 3 testes passaram
- [ ] ✅ Arquivo `Filial_Madureira.parquet` existe em `data/parquet/`

## 💡 Próximos Passos

Após a instalação bem-sucedida:

1. ✅ **Execute o Streamlit:** `streamlit run streamlit_app.py`
2. ✅ **Faça login** (se necessário)
3. ✅ **Teste perguntas simples** primeiro:
   - "Liste as colunas disponíveis"
   - "Qual o produto do item 1?"
4. ✅ **Evolua para perguntas complexas:**
   - "Mostre produtos do grupo ESMALTES"
   - "Gráfico de vendas por categoria"

## 🎉 Sucesso!

Se todos os testes passaram, seu agente Caçulinha BI está pronto para uso! 

O agente agora:
- ✅ Acessa dados de `Filial_Madureira.parquet`
- ✅ Lista colunas disponíveis
- ✅ Busca produtos por código/nome
- ✅ Consulta estoque
- ✅ Gera gráficos
- ✅ Responde perguntas em linguagem natural

---

**Desenvolvido para Caçula © 2025**
