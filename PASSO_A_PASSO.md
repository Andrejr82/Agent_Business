# 📋 Passo a Passo: Conectar o Agente BI ao Banco de Dados

## ⏱️ Tempo estimado: 15-30 minutos

---

## 🎯 Objetivo
Fazer o agente conseguir responder perguntas consultando dados reais do SQL Server em vez de usar arquivos Parquet.

---

## ✅ Checklist de Pré-requisitos

- [ ] SQL Server está rodando (`FAMILIA\SQLJR`)
- [ ] Usuário `AgenteVirtual` existe no SQL Server
- [ ] Senha do usuário está correta
- [ ] Database `Projeto_Caculinha` existe
- [ ] Arquivo `.env` está preenchido corretamente
- [ ] Arquivo `core/database/database.py` foi atualizado (agora tem código)

---

## 🚀 Procedimento

### **Etapa 1: Preparar o Ambiente**

#### 1.1 - Abrir Terminal PowerShell
```powershell
cd "C:\Users\André\Documents\agente-bi-caculinha-refatoracao-jules"
```

#### 1.2 - Verificar Python
```powershell
python --version
# Deve mostrar Python 3.10+
```

#### 1.3 - Ativar Ambiente Virtual (se houver)
```powershell
# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Ou se estiver usando conda
conda activate seu_ambiente
```

---

### **Etapa 2: Testar Conectividade com Servidor**

#### 2.1 - Verificar se servidor está acessível
```powershell
# Testar ping
ping FAMILIA

# Testar porta 1433
Test-NetConnection -ComputerName "FAMILIA" -Port 1433

# Esperado: "TcpTestSucceeded : True"
```

#### 2.2 - Se falhar a conectividade:
- ✓ Verificar se rede está ativa
- ✓ Verificar se servidor SQL Server está rodando
- ✓ Verificar firewall

```powershell
# Ver services SQL Server (em FAMILIA)
# Conectar via RDP para verificar se SQL está rodando
```

---

### **Etapa 3: Validar Credenciais**

#### 3.1 - Abrir arquivo `.env`
```powershell
# PowerShell
notepad .env
```

#### 3.2 - Verificar se está assim:
```env
DB_SERVER=FAMILIA\SQLJR
DB_PORT=1433
DB_DATABASE=Projeto_Caculinha
DB_USER=AgenteVirtual
DB_PASSWORD=Cacula@2020
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUST_SERVER_CERTIFICATE=yes
```

#### 3.3 - Testar credenciais em Python
```powershell
python
```

```python
import pyodbc

# Testar conexão direta
try:
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=FAMILIA\\SQLJR;'
        'DATABASE=Projeto_Caculinha;'
        'UID=AgenteVirtual;'
        'PWD=Cacula@2020;'
        'TrustServerCertificate=yes;'
    )
    print("✓ Conexão bem-sucedida!")
    conn.close()
except Exception as e:
    print(f"✗ Erro: {e}")

exit()
```

---

### **Etapa 4: Instalar Driver ODBC (se necessário)**

#### 4.1 - Verificar drivers disponíveis
```powershell
python
```

```python
import pyodbc
drivers = pyodbc.drivers()
print(drivers)

# Procure por: "ODBC Driver 17 for SQL Server"
exit()
```

#### 4.2 - Se não encontrar, instalar
```powershell
# Via Chocolatey (requer admin)
choco install msodbcsql17 -y

# Ou baixar manualmente:
# https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

# Depois reiniciar PowerShell
```

---

### **Etapa 5: Executar Diagnóstico Completo**

#### 5.1 - Rodar script de diagnóstico
```powershell
python diagnose_connection.py
```

#### 5.2 - Analisar resultado
```
✓ CHECK_ENV_VARS: PASSOU
✓ CHECK_ODBC_DRIVER: PASSOU
✓ TEST_CONNECTION_STRING: PASSOU
✓ TEST_PYODBC_CONNECTION: PASSOU
✓ TEST_SQLALCHEMY_CONNECTION: PASSOU
✓ TEST_DB_POOL: PASSOU

Resultado: 6/6 testes passaram
✓ Tudo está configurado corretamente!
```

**Se algum falhar:**
1. Ler a mensagem de erro
2. Procurar na seção "Troubleshooting" do SOLUCAO_CONEXAO_BANCO.md
3. Corrigir o problema
4. Rodar diagnóstico novamente

---

### **Etapa 6: Setup do Agente**

#### 6.1 - Executar setup
```powershell
python setup_agent.py
```

#### 6.2 - Esperado
```
ENVIRONMENT: ✓ OK
DATABASE: ✓ OK
TOOLS: ✓ OK
AGENT: ✓ OK

Resultado: 4/4 testes passaram
✓ Agente pronto para usar!
```

---

### **Etapa 7: Testar Agente com Banco de Dados**

#### 7.1 - Teste rápido em Python
```powershell
python
```

```python
from core.database.database import get_db_manager
from sqlalchemy import text

# Teste 1: Conexão
db = get_db_manager()
success, msg = db.test_connection()
print(msg)
# Esperado: ✓ Conexão com banco de dados estabelecida

# Teste 2: Contar produtos
with db.get_connection() as conn:
    result = conn.execute(
        text("SELECT COUNT(*) FROM dbo.Admat_OPCOM")
    )
    count = result.fetchone()[0]
    print(f"Total de produtos: {count}")

exit()
```

#### 7.2 - Teste com Ferramenta
```powershell
python
```

```python
from core.tools.sql_server_tools import get_product_by_code

# Substitua "12345" por um código real de produto
result = get_product_by_code.invoke({"product_code": "12345"})
print(result)

exit()
```

---

### **Etapa 8: Iniciar Aplicação**

#### 8.1 - Iniciar Streamlit
```powershell
streamlit run streamlit_app.py
```

#### 8.2 - Abrirá navegador automático
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

#### 8.3 - Fazer perguntas ao agente!
```
"Qual é o estoque do produto 123?"
"Quais são os 10 produtos mais vendidos?"
"Qual é a categoria do produto ABC?"
"Quanto custa o produto XYZ?"
```

---

## 🔍 Se Ainda Não Funcionar

### Verificação A: Logs

```powershell
# Ver logs do setup
tail -f logs/agent_setup.log

# Ver logs da Streamlit (terminal)
# Procure por "error" ou "exception"
```

### Verificação B: Teste Isolado

```powershell
python
```

```python
# Teste cada componente isoladamente

# 1. Config
from core.config.config import Config
c = Config()
print(f"Server: {c.DB_SERVER}")
print(f"Database: {c.DB_DATABASE}")

# 2. Connection
from core.database.database import get_db_manager
db = get_db_manager()
print(db.test_connection())

# 3. Tools
from core.tools.sql_server_tools import sql_server_tools
print(f"Tools: {[t.name for t in sql_server_tools]}")

exit()
```

### Verificação C: Banco de Dados

```sql
/* Executar no SQL Server Management Studio */

-- Verificar se tabela existe
SELECT * FROM Projeto_Caculinha.dbo.Admat_OPCOM WHERE 1=0;

-- Contar registros
SELECT COUNT(*) FROM Projeto_Caculinha.dbo.Admat_OPCOM;

-- Verificar permissões do usuário
SELECT * FROM sys.database_principals 
WHERE name = 'AgenteVirtual';

-- Garantir permissões
USE Projeto_Caculinha;
GRANT SELECT ON SCHEMA::dbo TO AgenteVirtual;
GRANT VIEW DEFINITION ON SCHEMA::dbo TO AgenteVirtual;
```

---

## ✨ Próximas Melhorias (Opcional)

1. **Adicionar mais ferramentas:**
   - Buscar vendas por período
   - Calcular ticket médio
   - Listar clientes
   - Ver histórico de compras

2. **Melhorar respostas:**
   - Formatar dados em tabelas
   - Gerar gráficos
   - Agrupar resultados

3. **Performance:**
   - Cachear consultas
   - Otimizar índices do banco
   - Usar materialized views

---

## 📞 Erros Comuns

| Erro | Solução |
|------|---------|
| "ConnectionError" | Verificar se servidor está acessível: `ping FAMILIA` |
| "Login failed" | Verificar credenciais em .env e permissões SQL |
| "ODBC driver not found" | Instalar driver: `choco install msodbcsql17` |
| "Database not found" | Verificar nome da database em .env |
| "Connection timeout" | Aumentar timeout, verificar firewall |
| "Cannot allocate connection" | Reiniciar aplicação, verificar pool_size |

---

## 🎉 Sucesso!

Se chegou aqui e tudo funcionou:

✅ Agente consultando banco de dados  
✅ Ferramentas SQL Server funcionando  
✅ Respostas com dados reais  
✅ Aplicação Streamlit operacional  

**Parabéns! 🎊**

