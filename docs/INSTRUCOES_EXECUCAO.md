# 🚀 INSTRUÇÕES DE EXECUÇÃO - SISTEMA 100% FUNCIONAL

## ⚡ INÍCIO RÁPIDO (2 MINUTOS)

### 1. Validar Sistema
```bash
cd c:\Users\André\Documents\agente-bi-caculinha-refatoracao-jules
python test_data_sources.py
```

**Resultado esperado:**
```
DATA_SOURCE_MANAGER: ✓ PASSOU
PARQUET_FILES: ✓ PASSOU
SQL_SERVER: ✓ PASSOU
UNIFIED_TOOLS: ✓ PASSOU

Resultado: 4/4 testes passaram ✓
```

### 2. Ver Demo Funcionando
```bash
python demo_sistema.py
```

**Resultado esperado:**
```
1. FONTES DISPONÍVEIS:
   [OK] sql_server
   [OK] parquet
   [OK] json

2. ACESSANDO SQL SERVER:
   [OK] Encontrados: 2 registros

3. ACESSANDO PARQUET:
   [OK] Encontrados: 2 registros

4. FERRAMENTAS:
   [OK] listar_dados_disponiveis
   [OK] get_produtos
   [OK] buscar_produto
   [OK] buscar_por_categoria
   [OK] obter_estoque
   [OK] consultar_dados

SISTEMA 100% FUNCIONAL!
```

---

## 📱 OPÇÃO 1: INTERFACE WEB (RECOMENDADO)

### Iniciar Streamlit
```bash
streamlit run streamlit_app.py
```

Abre automaticamente em: `http://localhost:8501`

**Funcionalidades:**
- Dashboard com dados em tempo real
- Pesquisa de produtos
- Relatórios
- Monitoramento

---

## 💻 OPÇÃO 2: PYTHON INTERATIVO

### Terminal Python
```bash
python
```

### Dentro do Python
```python
from core.agents.tool_agent import ToolAgent

# Inicializar agente
agent = ToolAgent()

# Fazer pergunta
resposta = agent.run("Quantos produtos temos?")
print(resposta)

# Mais exemplos
agent.run("Busque produtos da categoria Ferragem")
agent.run("Quais fontes de dados estão disponíveis?")
```

---

## 🔧 OPÇÃO 3: SCRIPTS DE TESTE

### Teste Completo
```bash
python test_data_sources.py
```

### Teste de Ferramentas
```bash
python test_tools.py
```

### Teste de Perguntas
```bash
python test_agent_queries.py
```

---

## 📊 VERIFICAR DADOS

### Acessar SQL Server Diretamente
```bash
python -c "
from core.data_source_manager import get_data_manager
manager = get_data_manager()
df = manager.get_data('admmatao', limit=5)
print(f'Encontrados {len(df)} registros')
print(df.head())
"
```

### Acessar Parquet Diretamente
```bash
python -c "
from core.data_source_manager import get_data_manager
manager = get_data_manager()
df = manager.get_data('ADMAT', limit=5)
print(f'Encontrados {len(df)} registros')
print(df.head())
"
```

---

## 🔍 TROUBLESHOOTING

### Erro: "SQL Server não conecta"
```bash
# Verificar conexão
python -c "
from core.database.database import DatabaseConnectionManager
manager = DatabaseConnectionManager()
try:
    engine = manager.get_engine()
    print('OK - SQL Server conectado')
except Exception as e:
    print(f'ERRO: {e}')
"
```

### Erro: "Parquet não encontrado"
```bash
# Verificar arquivos
dir data\parquet_cleaned\
```

### Erro: "Ferramenta não funciona"
```bash
# Testar ferramenta individualmente
python test_tools.py
```

---

## 📈 MONITORAR LOGS

### Ver logs em tempo real
```bash
# Windows PowerShell
Get-Content logs\application.log -Tail 50 -Wait

# Ou após execução
more logs\application.log
```

### Limpar logs antigos
```bash
del logs\*.log
```

---

## 🎯 CASOS DE USO

### 1. Listar Produtos
```python
agent.run("Quais são os primeiros 10 produtos?")
```

### 2. Buscar Produto Específico
```python
agent.run("Busque informações do produto PARAFUSO")
```

### 3. Consultar Categoria
```python
agent.run("Quantos produtos temos na categoria Ferragem?")
```

### 4. Verificar Estoque
```python
agent.run("Qual é o estoque do produto 12345?")
```

### 5. Relatório Geral
```python
agent.run("Faça um resumo dos dados disponíveis")
```

---

## ⚙️ CONFIGURAÇÕES

### Modificar limites de query
```python
# Arquivo: core/tools/unified_data_tools.py
# Linha: def get_produtos(limit: int = 100)
# Alterar 100 para outro valor
```

### Adicionar nova fonte de dados
```python
# Arquivo: core/data_source_manager.py
# Adicionar nova classe derivada de DataSource
# Registrar em _initialize_sources()
```

### Modificar ordem de fallback
```python
# Arquivo: core/tools/unified_data_tools.py
# Modificar lista de tabelas:
tabelas = ['sua_prioridade_1', 'sua_prioridade_2', ...]
```

---

## 📚 DOCUMENTAÇÃO

| Arquivo | Conteúdo |
|---------|----------|
| `SISTEMA_100_FUNCIONAL.md` | Relatório técnico completo |
| `RESUMO_EXECUCAO.md` | Resumo da execução |
| `STATUS_SISTEMA_FINAL.md` | Status final do sistema |
| `GUIA_ACESSO_DADOS.md` | Guia de acesso aos dados |
| `COMECE_AQUI.md` | Quick start |

---

## ✅ CHECKLIST ANTES DE USAR

- ✅ Python 3.10+ instalado
- ✅ Dependências instaladas (`pip install -r requirements.txt`)
- ✅ .env configurado com SQL Server credentials
- ✅ SQL Server acessível
- ✅ Parquet files em `data/parquet_cleaned/`
- ✅ Testes passando (`python test_data_sources.py`)

---

## 🎉 VOCÊ ESTÁ PRONTO!

Sistema 100% funcional e pronto para:
- ✅ Responder perguntas com dados reais
- ✅ Acessar múltiplas fontes de dados
- ✅ Fazer fallback automático
- ✅ Escalar para produção

**Escolha sua opção acima e comece a usar!**

---

**Desenvolvido com sucesso! 🚀**
