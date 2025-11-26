# CLAUDE.md

Este arquivo fornece orientações para o Claude Code (claude.ai/code) ao trabalhar com código neste repositório.

## Visão Geral do Projeto

**Agente de Negócios** é um sistema de BI conversacional construído em Python que processa consultas de dados através de agentes orquestrados por LLM usando LangChain. O sistema fornece uma interface de chat interativa via Streamlit onde os usuários podem consultar dados de negócios em linguagem natural e receber respostas como texto, tabelas ou gráficos Plotly interativos.

**Stack Tecnológico:**
- **Frontend:** Streamlit (interface web interativa)
- **Backend:** Python com API Flask
- **LLM:** Google Gemini API (gemini-2.0-flash-lite) via LangChain
- **Dados:** Principalmente arquivos Parquet (Filial_Madureira.parquet), com suporte opcional a SQL Server
- **Framework de Agentes:** LangChain com agentes de chamada de ferramentas
- **Visualização:** Plotly para gráficos e dashboards

## Executando a Aplicação

```bash
# Configuração inicial
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Configurar variáveis de ambiente - criar arquivo .env com:
GEMINI_API_KEY=sua_api_key
GEMINI_MODEL_NAME=gemini-2.0-flash-lite
DB_SERVER=seu_sql_server  # Opcional
DB_DATABASE=seu_banco_de_dados
DB_USER=seu_usuario
DB_PASSWORD=sua_senha

# Executar aplicação Streamlit (interface principal)
streamlit run streamlit_app.py

# Executar servidor API (opcional)
python core/api/run_api.py

# Executar testes
pytest
pytest tests/ -v  # Detalhado
pytest tests/ --cov=core  # Com cobertura
```

## Arquitetura

### Fluxo de Processamento de Consultas

```
Entrada do Usuário (Streamlit)
  → QueryProcessor (core/query_processor.py) [camada de cache]
    → SupervisorAgent (core/agents/supervisor_agent.py) [roteia consultas]
      → ToolAgent (core/agents/tool_agent.py) [executa via LangChain]
        → Ferramentas (unified_data_tools, chart_tools, date_time_tools)
          → DataSourceManager (core/data_source_manager.py)
            → Filial_Madureira.parquet
```

**Componentes Principais:**

1. **QueryProcessor** (`core/query_processor.py`): Ponto de entrada com cache (3600s TTL)
2. **SupervisorAgent** (`core/agents/supervisor_agent.py`): Detecta intenção de gráficos via palavras-chave, roteia para ToolAgent
3. **ToolAgent** (`core/agents/tool_agent.py`): Executor de agente LangChain com capacidades de chamada de ferramentas
4. **DataSourceManager** (`core/data_source_manager.py`): Singleton que abstrai acesso aos dados do arquivo Parquet

### Arquitetura de Agentes

O sistema usa um **padrão de agentes simplificado**:
- **SupervisorAgent**: Roteamento baseado em palavras-chave (detecta "gráfico", "chart", "vendas", "produto", etc.)
- **ToolAgent**: `AgentExecutor` do LangChain com `create_tool_calling_agent`
- **Ferramentas**: Ferramentas LangChain decoradas com `@tool` que o agente pode invocar

As ferramentas são organizadas em três categorias:
- `unified_data_tools` - Consulta de dados (consultar_dados, listar_colunas_disponiveis)
- `chart_tools` - Geração de gráficos (gerar_grafico_vendas_por_categoria, etc.)
- `date_time_tools` - Utilitários de data/hora

### Arquitetura de Fonte de Dados

**Crítico:** O sistema usa primariamente **Filial_Madureira.parquet** como sua única fonte de verdade:
- Localização: `data/parquet/Filial_Madureira.parquet`
- Acesso via: `DataSourceManager` (padrão singleton)
- Referência do schema: `data/catalog_focused.json`

O DataSourceManager fornece:
- `get_data(limit)` - Recupera todos os dados ou quantidade limitada
- `search(column, value, limit)` - Busca sem distinção de maiúsculas/minúsculas
- `get_filtered_data(filters, limit)` - Filtragem com correspondência exata
- `get_columns()` - Lista colunas disponíveis
- `get_source_info()` - Metadados sobre a fonte de dados

## Padrões Críticos de Implementação

### 1. Padrão LLM Adapter (Factory + Fallback)

```python
from core.llm_factory import LLMFactory

# CORRETO: Usar factory
adapter = LLMFactory.get_adapter()  # Retorna GeminiLLMAdapter

# ERRADO: Não instanciar diretamente a menos que necessário
from core.llm_gemini_adapter import GeminiLLMAdapter
adapter = GeminiLLMAdapter()  # Desvia do padrão factory
```

O `LLMFactory` (`core/llm_factory.py`) fornece acesso singleton ao adaptador Gemini.

### 2. Padrão Tool Agent

Ao adicionar novas ferramentas, siga este padrão:

```python
from langchain_core.tools import tool
from core.data_source_manager import get_data_manager

@tool
def minha_nova_ferramenta(param: str) -> Dict[str, Any]:
    """
    Descrição da ferramenta que o LLM verá.
    Seja explícito sobre o que a ferramenta faz.
    """
    try:
        data_manager = get_data_manager()
        # Implementação
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

Registre as ferramentas no módulo apropriado:
- `core/tools/unified_data_tools.py` para acesso a dados
- `core/tools/chart_tools.py` para visualizações
- `core/tools/date_time_tools.py` para operações de data

Depois adicione em `ToolAgent.__init__`:
```python
from core.tools.minhas_ferramentas import minhas_ferramentas
self.tools = unified_tools + date_time_tools + chart_tools + minhas_ferramentas
```

### 3. Padrão de Geração de Gráficos

Os gráficos devem retornar um formato específico para o ToolAgent reconhecê-los:

```python
@tool
def gerar_grafico(...) -> Dict[str, Any]:
    """Descrição da ferramenta de gráfico."""
    fig = go.Figure(...)

    # Aplicar customização padrão
    from core.tools.chart_tools import _apply_chart_customization
    fig = _apply_chart_customization(fig, title="Meu Gráfico")

    # CRÍTICO: Retornar este formato exato
    return {
        "status": "success",
        "chart_data": fig.to_json(),  # A chave deve ser "chart_data"
        "message": "Gráfico gerado com sucesso"
    }
```

O ToolAgent detecta gráficos verificando `observation.get("status") == "success" and "chart_data" in observation`.

### 4. Mapeamento de Nomes de Colunas

**Importante:** Usuários podem dizer "produto" mas a coluna real é "ITEM". O prompt do sistema no ToolAgent lida com isso:

```python
# De core/agents/tool_agent.py system prompt:
"Sempre que o usuário se referir a 'produto' ou 'item' em um contexto de busca
por um código ou identificador, utilize a coluna 'ITEM' no filtro da ferramenta
`consultar_dados`."
```

Mapeamentos comuns para estar ciente:
- "produto"/"item" → coluna `ITEM`
- "lucro" → coluna `LUCRO R$`
- "lucro percentual" → `LUCRO TOTAL %` ou `LUCRO UNIT %`

### 5. Padrão de Autenticação

A autenticação usa backend SQL Server:

```python
from core import auth
from core.database import sqlserver_auth as auth_db

# No Streamlit:
if not st.session_state.get(SESSION_STATE_KEYS["AUTHENTICATED"]):
    auth.login()
    st.stop()
```

A inicialização do banco de dados é preguiçosa (apenas quando o formulário de login é submetido) para evitar efeitos colaterais durante imports/testes.

## Tarefas Comuns de Desenvolvimento

### Adicionando um Novo Tipo de Gráfico

1. Criar ferramenta em `core/tools/chart_tools.py`:
```python
@tool
def gerar_novo_grafico(param: str) -> Dict[str, Any]:
    """Descrição para o LLM."""
    data_manager = get_data_manager()
    df = data_manager.get_data()

    # Criar figura Plotly
    fig = go.Figure(...)
    fig = _apply_chart_customization(fig, title="Título")

    return {
        "status": "success",
        "chart_data": fig.to_json(),
        "message": "Gráfico gerado"
    }
```

2. Adicionar à lista `chart_tools` no mesmo arquivo
3. A ferramenta é registrada automaticamente (importada em `tool_agent.py`)

### Adicionando uma Nova Ferramenta de Consulta de Dados

1. Criar em `core/tools/unified_data_tools.py`
2. Usar `get_data_manager()` para acesso aos dados
3. Retornar dict estruturado com `status` e `data`/`message`

### Modificando o Comportamento do Agente

O prompt principal do agente está em `core/agents/tool_agent.py` → `_create_agent_executor()`:
- Mensagem do sistema define o comportamento
- Usa `MessagesPlaceholder` para histórico de chat
- Ferramentas são auto-descritas para o LLM via LangChain

### Trabalhando com Dados Parquet

Sempre use o DataSourceManager:

```python
from core.data_source_manager import get_data_manager

manager = get_data_manager()
df = manager.get_data(limit=100)
columns = manager.get_columns()
info = manager.get_source_info()
```

NÃO leia arquivos parquet diretamente com `pd.read_parquet()` fora do DataSourceManager.

## Testes

Estrutura de testes:
- `tests/conftest.py` - Fixtures e configuração
- `tests/test_*_agent.py` - Testes específicos de agentes
- `tests/test_tools.py` - Testes de funcionalidade de ferramentas
- `tests/test_data_sources.py` - Testes da camada de dados

Executar teste específico:
```bash
pytest tests/test_tool_agent.py -v
pytest tests/test_chart_tools.py -k "test_specific_function"
```

## Variáveis de Ambiente

Obrigatórias:
- `GEMINI_API_KEY` - Chave de API do Google Gemini
- `GEMINI_MODEL_NAME` - Nome do modelo (padrão: gemini-2.0-flash-lite)

Opcionais (para SQL Server):
- `DB_SERVER`, `DB_DATABASE`, `DB_USER`, `DB_PASSWORD`
- `DB_DRIVER` - Padrão: "ODBC Driver 17 for SQL Server"

Opcionais (para recursos):
- `LANGCHAIN_TRACING_V2=true` - Ativar rastreamento LangSmith
- `LANGCHAIN_API_KEY` - Chave de API LangSmith
- `LANGCHAIN_PROJECT` - Nome do projeto para rastreamento
- `DEBUG=true` - Ativar modo de depuração
- `SECRET_KEY` - Segredo da sessão (padrão é inseguro)

## Localizações Importantes de Arquivos

**Lógica Principal:**
- `streamlit_app.py` - Ponto de entrada principal da UI
- `core/query_processor.py` - Orquestração de consultas com cache
- `core/agents/supervisor_agent.py` - Lógica de roteamento de consultas
- `core/agents/tool_agent.py` - Agente LangChain com ferramentas
- `core/data_source_manager.py` - Abstração de acesso aos dados

**Configuração:**
- `core/config/config.py` - Carregamento centralizado de config do .env
- `core/llm_factory.py` - Factory de adaptador LLM
- `core/session_state.py` - Chaves de sessão Streamlit

**Ferramentas:**
- `core/tools/unified_data_tools.py` - Ferramentas de consulta de dados
- `core/tools/chart_tools.py` - Ferramentas de visualização
- `core/tools/date_time_tools.py` - Utilitários de data/hora

**Dados:**
- `data/parquet/Filial_Madureira.parquet` - Fonte principal de dados
- `data/catalog_focused.json` - Documentação do schema

**UI:**
- `ui/ui_components.py` - Componentes UI reutilizáveis
- `style.css` - Estilização customizada Streamlit

## Convenções de Código

1. **Imports:** Imports absolutos da raiz do projeto (ex: `from core.agents.tool_agent import ToolAgent`)
2. **Logging:** Usar `logging.getLogger(__name__)` em cada módulo
3. **Type Hints:** Usar para assinaturas de funções, especialmente em ferramentas
4. **Docstrings:** Obrigatório para todas as funções decoradas com `@tool` (o LLM vê estas)
5. **Tratamento de Erros:** Ferramentas devem retornar `{"status": "error", "message": str}` em caso de falha
6. **Tipos de Dados:**
   - Retornar `pd.DataFrame` para dados tabulares
   - Retornar `go.Figure` (como JSON) para gráficos
   - Retornar `dict` para respostas estruturadas

## Gerenciamento de Estado de Sessão

Chaves de sessão do Streamlit definidas em `core/session_state.py`:

```python
SESSION_STATE_KEYS = {
    "AUTHENTICATED": "authenticated",
    "USERNAME": "username",
    "ROLE": "role",
    "MESSAGES": "messages",
    "QUERY_PROCESSOR": "query_processor",
    # etc...
}
```

Sempre use estas constantes, nunca codifique strings de chaves de sessão diretamente.

## Notas de Deployment

O projeto inclui guias de deployment:
- `Deploy_Supabase.md` - Guia para deploy no Supabase + Render
- Suporta migração de Parquet para PostgreSQL/Supabase

Ao fazer deploy:
1. Garantir que todas as variáveis de ambiente estejam configuradas
2. Usar `requirements.txt` para dependências
3. Streamlit requer flags `--server.port` e `--server.address`
4. API requer servidor WSGI (gunicorn recomendado)

## Problemas Conhecidos & Padrões

1. **Prevenção de Importação Circular:** SupervisorAgent usa carregamento preguiçoso para ToolAgent:
   ```python
   @property
   def tool_agent(self):
       if self._tool_agent is None:
           from core.agents.tool_agent import ToolAgent
           self._tool_agent = ToolAgent(...)
       return self._tool_agent
   ```

2. **Renderização de Gráficos:** Streamlit renderiza gráficos Plotly via `st.plotly_chart()`. Gráficos são armazenados nas mensagens de sessão como objetos `go.Figure`, não strings JSON.

3. **Detecção de Tipo de Resposta:** ToolAgent verifica passos intermediários para extrair saídas das ferramentas. Ferramentas de gráfico devem retornar `{"status": "success", "chart_data": json_string}`.

4. **Invalidação de Cache:** O cache do QueryProcessor é apenas em memória (não persistido). Reiniciar limpa o cache.

5. **Coerção de Tipo de Dados:** DataSourceManager converte automaticamente dtypes no carregamento para prevenir incompatibilidades de tipo.
