# 📊 Guia de Acesso a Dados - Sistema Multi-Fonte

## 🎯 Objetivo

O agente BI pode acessar dados de **múltiplas fontes** automaticamente:
- ✅ **SQL Server** (Projeto_Caculinha)
- ✅ **Arquivos Parquet** (data/parquet_cleaned)
- ✅ **Arquivos JSON** (data/)
- ✅ **Fallback automático** entre fontes

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────┐
│         Agente BI (Query)                   │
└────────────────────┬────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │ Data Source Manager │ ◄── Camada Unificada
          └──────────┬──────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
     ▼               ▼               ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ SQL      │  │ Parquet  │  │  JSON    │
│ Server   │  │  Files   │  │  Files   │
└──────────┘  └──────────┘  └──────────┘
     │               │               │
  FAMILIA\        data/           data/
  SQLJR      parquet_cleaned     *.json
```

---

## 📂 Estrutura de Dados

### SQL Server (Prioridade 1️⃣)
```
Servidor: FAMILIA\SQLJR
Database: Projeto_Caculinha
Tabelas:
  - dbo.Admat_OPCOM (principais)
  - (outras tabelas)
```

**Como acessar:**
```python
from core.data_source_manager import get_data_manager

manager = get_data_manager()
df = manager.get_data('Admat_OPCOM', limit=100)
```

### Arquivos Parquet (Prioridade 2️⃣)
```
data/parquet_cleaned/
  ├── ADMAT.parquet
  ├── ADMAT_REBUILT.parquet
  ├── ADMAT_structured.parquet
  ├── ADMAT_SEMVENDAS.parquet
  └── master_catalog.parquet

data/parquet/
  ├── ADMAT.parquet
  ├── ADMAT_SEMVENDAS.parquet
  └── ADMMATAO.parquet
```

**Como acessar:**
```python
manager = get_data_manager()
df = manager.get_data('ADMAT', limit=50, source='parquet')
```

### Arquivos JSON (Prioridade 3️⃣)
```
data/
  ├── CATALOGO_PARA_EDICAO.json
  ├── catalog_focused.json
  ├── data_catalog.json
  ├── data_catalog_enriched.json
  ├── db_context.json
  ├── database_structure.json
  └── config.json
```

**Como acessar:**
```python
manager = get_data_manager()
df = manager.get_data('catalog_focused', limit=100, source='json')
```

---

## 🔧 Ferramentas Disponíveis

### 1. Listar Fontes Disponíveis
```python
from core.tools.unified_data_tools import listar_dados_disponiveis

result = listar_dados_disponiveis.invoke({})
# Retorna: quais fontes estão online
```

### 2. Buscar Produtos
```python
from core.tools.unified_data_tools import get_produtos

result = get_produtos.invoke({"limit": 100})
# Retorna: até 100 produtos de qualquer fonte
```

### 3. Buscar Produto Específico
```python
from core.tools.unified_data_tools import buscar_produto

# Por código
result = buscar_produto.invoke({
    "codigo": "123",
    "limit": 10
})

# Por nome
result = buscar_produto.invoke({
    "nome": "parafuso",
    "limit": 10
})
```

### 4. Buscar por Categoria
```python
from core.tools.unified_data_tools import buscar_por_categoria

result = buscar_por_categoria.invoke({
    "categoria": "Ferragens",
    "limit": 20
})
```

### 5. Obter Estoque
```python
from core.tools.unified_data_tools import obter_estoque

result = obter_estoque.invoke({
    "codigo_produto": "456"
})
```

### 6. Consulta Genérica
```python
from core.tools.unified_data_tools import consultar_dados

# Sem filtro
result = consultar_dados.invoke({
    "tabela": "Admat_OPCOM",
    "limite": 100
})

# Com filtro
result = consultar_dados.invoke({
    "tabela": "ADMAT",
    "coluna": "CATEGORIA",
    "valor": "Ferragens",
    "limite": 50
})
```

---

## 🚀 Como Usar via Agente

### Exemplos de Perguntas

**1. Consulta simples:**
```
"Quantos produtos você consegue encontrar?"
→ Agente usa: get_produtos() → busca em SQL → se falhar, tenta Parquet
```

**2. Buscar específico:**
```
"Qual é o preço do produto 123?"
→ Agente usa: buscar_produto(codigo="123") → múltiplas fontes
```

**3. Por categoria:**
```
"Mostre os produtos da categoria Ferragens"
→ Agente usa: buscar_por_categoria(categoria="Ferragens")
```

**4. Estoque:**
```
"Qual é o estoque do produto ABC?"
→ Agente usa: obter_estoque(nome_produto="ABC")
```

**5. Listar fontes:**
```
"Quais fontes de dados estão disponíveis?"
→ Agente usa: listar_dados_disponiveis()
```

---

## 📋 Fluxo de Acesso a Dados

### Quando você faz uma pergunta:

```
1. Agente recebe pergunta
   ↓
2. Agente seleciona melhor ferramenta
   ↓
3. Ferramenta chama Data Source Manager
   ↓
4. Manager tenta SQL Server primeiro
   ├─ ✓ Se encontra → retorna dados
   └─ ✗ Se falha → tenta Parquet
       ├─ ✓ Se encontra → retorna dados
       └─ ✗ Se falha → tenta JSON
           ├─ ✓ Se encontra → retorna dados
           └─ ✗ Se falha → retorna erro
   ↓
5. Dados retornam ao agente
   ↓
6. Agente formata resposta legível
   ↓
7. Usuário recebe resposta
```

---

## ⚙️ Configuração Manual

### SQL Server
Editar `.env`:
```env
DB_SERVER=FAMILIA\SQLJR
DB_PORT=1433
DB_DATABASE=Projeto_Caculinha
DB_USER=AgenteVirtual
DB_PASSWORD=Cacula@2020
DB_DRIVER=ODBC Driver 17 for SQL Server
```

### Parquet
Arquivos já estão em:
- `data/parquet_cleaned/` ← Prioritário
- `data/parquet/`

### JSON
Arquivos já estão em:
- `data/`

---

## 🔍 Verificar Quais Dados Estão Disponíveis

### Via Python:
```python
from core.data_source_manager import get_data_manager

manager = get_data_manager()

# Ver status
print(manager.get_status())

# Ver quais estão disponíveis
print(manager.get_available_sources())

# Testar cada fonte
for source_name in manager.get_available_sources():
    df = manager.get_data('Admat_OPCOM', limit=1, source=source_name)
    if not df.empty:
        print(f"✓ {source_name} tem dados")
    else:
        print(f"✗ {source_name} vazio")
```

### Via Terminal:
```powershell
python test_data_sources.py
```

---

## 🧪 Testes Rápidos

### Teste 1: Todas as fontes
```powershell
python test_data_sources.py
```
**Esperado:** Relatório completo de acesso

### Teste 2: Data Source Manager
```powershell
python
>>> from core.data_source_manager import get_data_manager
>>> manager = get_data_manager()
>>> print(manager.get_status())
>>> df = manager.get_data('Admat_OPCOM', limit=5)
>>> print(df)
```

### Teste 3: Ferramentas Unificadas
```powershell
python
>>> from core.tools.unified_data_tools import get_produtos
>>> result = get_produtos.invoke({"limit": 10})
>>> print(result)
```

### Teste 4: Agente Completo
```powershell
streamlit run streamlit_app.py
# Faça perguntas sobre dados
```

---

## 🚨 Troubleshooting

### ❌ "Nenhuma fonte de dados disponível"
**Solução:**
1. Verificar se SQL Server está acessível: `Test-NetConnection FAMILIA -Port 1433`
2. Verificar se arquivos Parquet existem: `dir data/parquet_cleaned/`
3. Verificar se arquivo `.env` está correto

### ❌ "Dados não encontrados"
**Solução:**
1. Executar `python test_data_sources.py` para diagnosticar
2. Verificar se tabela/arquivo existe
3. Verificar nomes de colunas (case-sensitive em Parquet)

### ❌ "Connection timeout"
**Solução:**
1. Verificar conectividade: `ping FAMILIA`
2. Aumentar timeout em `core/database/database.py`
3. Usar fallback (Parquet/JSON) manualmente

### ✅ "Dados carregados com sucesso"
**Próximas ações:**
1. Usar agente normalmente
2. Fazer perguntas sobre dados
3. Deixar sistema usar fallback automático

---

## 📊 Prioridade de Acesso (importante!)

| Prioridade | Fonte | Velocidade | Disponibilidade |
|-----------|-------|-----------|-----------------|
| 1️⃣ | SQL Server | Rápida | Se conectado |
| 2️⃣ | Parquet | Muito Rápida | Sempre |
| 3️⃣ | JSON | Rápida | Sempre |

**Estratégia:** Sistema tenta SQL Server; se falhar, usa Parquet; se falhar, usa JSON.

---

## 💡 Dicas de Performance

### Para consultas grandes:
```python
# Usar limit para reduzir dados
df = manager.get_data('Admat_OPCOM', limit=1000)
```

### Para buscas específicas:
```python
# Usar search em vez de get_data
df = manager.search_data('Admat_OPCOM', 'NOME', 'parafuso')
```

### Para dados em cache:
```python
# Primeira busca (lenta)
df1 = manager.get_data('ADMAT', limit=100)

# Segunda busca (rápida, dados em cache)
df2 = manager.get_data('ADMAT', limit=100)
```

---

## 📝 Resumo Rápido

| Ação | Comando |
|------|---------|
| Testar todas as fontes | `python test_data_sources.py` |
| Ver status das fontes | `python -c "from core.data_source_manager import get_data_manager; print(get_data_manager().get_status())"` |
| Iniciar agente | `streamlit run streamlit_app.py` |
| Fazer pergunta | Digite na interface Streamlit |
| Forçar source específico | `manager.get_data('tabela', source='sql_server')` |

---

**Data:** 10 de novembro de 2025  
**Status:** ✅ Multi-fonte configurado e pronto

