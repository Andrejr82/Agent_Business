# 🔧 Solução: Conexão do Agente BI com Banco de Dados

## 📌 Problemas Identificados

1. ❌ **Arquivo `core/database/database.py` vazio** - Classe de conexão não implementada
2. ❌ **Ferramentas apontam para Parquet** - Não consultam SQL Server
3. ❌ **Sem tratamento robusto de erros** - Conexões não recuperáveis
4. ❌ **Pool de conexões não otimizado** - Conexões podem exaurir
5. ❌ **Falta validação de credenciais** - Erros não claros

---

## ✅ Solução Implementada

### 1️⃣ **Novo Gerenciador de Conexão** (`core/database/database.py`)

**O que foi criado:**
- Classe `DatabaseConnectionManager` (singleton)
- Pool de conexões robusto com `pool_pre_ping` e reciclagem
- Context managers para gerenciar conexões automaticamente
- Tratamento abrangente de erros
- Testes de conexão

**Benefícios:**
- ✓ Uma única instância gerencia todas as conexões
- ✓ Conexões são testadas antes de usar
- ✓ Recuperação automática de conexões perdidas
- ✓ Logs detalhados de operações

**Como usar:**
```python
from core.database.database import get_db_manager

db_manager = get_db_manager()

# Para executar uma query
with db_manager.get_connection() as conn:
    result = conn.execute(text("SELECT * FROM dbo.Admat_OPCOM"))
    
# Para usar sessions ORM
with db_manager.get_session_context() as session:
    produtos = session.query(Produto).all()
```

---

### 2️⃣ **Ferramentas SQL Server** (`core/tools/sql_server_tools.py`)

**Ferramentas implementadas:**

| Ferramenta | Descrição |
|-----------|-----------|
| `query_database` | Executa queries SQL customizadas |
| `get_product_by_code` | Busca produto por código |
| `search_products_by_name` | Busca produtos por nome |
| `get_products_by_category` | Lista produtos de uma categoria |
| `get_top_selling_products` | Top 10 produtos mais vendidos |
| `get_product_stock` | Consulta estoque de um produto |

**Todas conectam ao banco SQL Server real!**

---

### 3️⃣ **Scripts de Diagnóstico**

#### A. `diagnose_connection.py`
Executa 7 testes completos:
```bash
python diagnose_connection.py
```

Verifica:
- ✓ Variáveis de ambiente
- ✓ Driver ODBC disponível
- ✓ String de conexão
- ✓ Conexão pyodbc
- ✓ Conexão SQLAlchemy
- ✓ Pool de conexões
- ✓ Agente funcionando

#### B. `setup_agent.py`
Prepara o ambiente:
```bash
python setup_agent.py
```

Executa:
- ✓ Configuração do ambiente
- ✓ Teste de banco de dados
- ✓ Carregamento de ferramentas
- ✓ Inicialização do agente

---

## 🚀 Passos para Resolver o Problema

### Passo 1: Validar Credenciais do Banco

Editar `.env` e verificar:

```env
DB_SERVER=FAMILIA\SQLJR           # Servidor correto?
DB_PORT=1433                       # Porta correta?
DB_DATABASE=Projeto_Caculinha      # Database correto?
DB_USER=AgenteVirtual              # Usuário existe?
DB_PASSWORD=Cacula@2020            # Senha correta?
DB_DRIVER=ODBC Driver 17 for SQL Server  # Driver instalado?
```

### Passo 2: Instalar Driver ODBC (se necessário)

```powershell
# Windows - via chocolatey
choco install msodbcsql17

# Ou verificar drivers disponíveis:
python -c "import pyodbc; print(pyodbc.drivers())"
```

### Passo 3: Executar Diagnóstico

```powershell
cd "C:\Users\André\Documents\agente-bi-caculinha-refatoracao-jules"
python diagnose_connection.py
```

**Esperado: Todos os testes passarem (✓)**

### Passo 4: Setup do Agente

```powershell
python setup_agent.py
```

### Passo 5: Iniciar Streamlit

```powershell
streamlit run streamlit_app.py
```

---

## 🧪 Teste Rápido

### Teste 1: Verificar conexão
```python
from core.database.database import get_db_manager

db = get_db_manager()
success, msg = db.test_connection()
print(msg)
# Esperado: ✓ Conexão com banco de dados estabelecida
```

### Teste 2: Consultar banco
```python
from core.database.database import get_db_manager
from sqlalchemy import text

db = get_db_manager()
with db.get_connection() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM dbo.Admat_OPCOM"))
    print(f"Total de produtos: {result.fetchone()[0]}")
```

### Teste 3: Usar ferramenta diretamente
```python
from core.tools.sql_server_tools import get_product_by_code

result = get_product_by_code.invoke({"product_code": "123"})
print(result)
```

### Teste 4: Fazer pergunta ao agente
```python
from core.query_processor import QueryProcessor

processor = QueryProcessor()
result = processor.process_query("Qual é o estoque do produto 123?")
print(result)
```

---

## 🔍 Troubleshooting

### ❌ Erro: "Driver not found"
**Solução:**
```powershell
# Verificar drivers
python -c "import pyodbc; print(pyodbc.drivers())"

# Instalar driver (Windows)
choco install msodbcsql17 -y

# Ou instalar via Microsoft:
# https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

### ❌ Erro: "Login failed"
**Verificações:**
1. Usuário `AgenteVirtual` existe no SQL Server?
2. Senha está correta?
3. Usuário tem permissão de SELECT na database?

```sql
-- Executar no SQL Server como admin:
USE Projeto_Caculinha;
GRANT SELECT ON SCHEMA::dbo TO AgenteVirtual;
```

### ❌ Erro: "Connection timeout"
**Soluções:**
1. Servidor está acessível? `ping FAMILIA`
2. Porta 1433 está aberta? `Test-NetConnection -ComputerName FAMILIA -Port 1433`
3. Firewall bloqueando?

```powershell
# Testar conectividade
Test-NetConnection -ComputerName "FAMILIA" -Port 1433
```

### ❌ Erro: "Connection pool exhausted"
**Solução:** Reiniciar a aplicação
```powershell
# Se usar em produção, aumentar pool_size em database.py:
# pool_size=20, max_overflow=40  # Aumentar valores
```

---

## 📊 Fluxo de Funcionamento Agora

```
Usuário faz pergunta
    ↓
Streamlit → QueryProcessor
    ↓
SupervisorAgent → ToolAgent
    ↓
LLM (GPT-4o) avalia qual ferramenta usar
    ↓
Ferramentas SQL Server (novas!)
    ↓
DatabaseConnectionManager
    ↓
SQLAlchemy + pyodbc
    ↓
SQL Server (FAMILIA\SQLJR)
    ↓
Dados retornam ao LLM
    ↓
LLM formata resposta
    ↓
Usuário vê resposta com dados reais
```

---

## 📝 Próximas Melhorias (Opcional)

1. **Cache Redis** - Cachear consultas frequentes
2. **Query Optimizer** - Verificar e otimizar queries lentas
3. **Audit Trail** - Registrar todas as consultas feitas
4. **Rate Limiting** - Limitar queries por usuário
5. **Data Validation** - Validar dados antes de retornar
6. **Query Builder** - Interface para construir queries

---

## 📞 Suporte

Se os testes ainda falharem:

1. Execute `diagnose_connection.py` e salve a saída
2. Verifique o arquivo de log: `logs/agent_setup.log`
3. Procure por padrões de erro específicos
4. Valide credenciais SQL Server manualmente

**Logs disponíveis em:**
- `logs/agent_setup.log` - Setup do agente
- SQLAlchemy logs - Conexões e queries

