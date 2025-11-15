# Instruções para Agentes de Código - Caçulinha BI

Sistema BI conversacional em Python que processa consultas de dados através de agentes LLM orquestrados com LangGraph.

## Arquitetura Core

**Entrada → Orquestração → Saída**

1. **Streamlit App** (`streamlit_app.py`) → Interface principal para chat com usuário
2. **QueryProcessor** (`core/query_processor.py`) → Delegador que cacheiza requisições
3. **SupervisorAgent** (`core/agents/supervisor_agent.py`) → Orquestra fluxo com LangGraph
4. **Agentes Especializados** (`core/agents/`) → ToolAgent, CodeGenAgent executam tarefas específicas
5. **Adaptadores LLM** (`core/llm_adapter.py`, `core/llm_base.py`) → Fallback OpenAI→Gemini→DeepSeek
6. **Conectores de Dados** (`core/database/`, `core/adapters/`) → SQL Server, Parquet, Hybrid Engine

Estado compartilhado: `AgentState` (`core/agent_state.py`) com campos `messages`, `retrieved_data`, `chart_code`, `plotly_fig`, `route_decision`.

## Padrões Críticos do Projeto

### 1. Factory Pattern para LLM Adapters
```python
from core.factory.component_factory import ComponentFactory
adapter = ComponentFactory.get_llm_adapter()  # Obtém com fallback automático
# NÃO: instanciar OpenAI/Gemini diretamente se factory estiver disponível
```

### 2. Fluxo de Cache de Respostas
- **TTL padrão**: 3600s em `core/cache.py`
- **Uso**: `QueryProcessor.process_query()` cacheiza antes de delegar
- **Ao modificar**: preserve os parâmetros `cache_context` em `core/llm_adapter.py`

### 3. Lazy Loading & Inicialização
- Imports pesados carregados sob demanda (reduz tempo de startup)
- Dados em `data/` (catálogos JSON, patterns) carregados apenas quando necessário
- Atualize timing/imports se mudar configurações de inicialização

### 4. Acesso a Dados: Adaptadores vs Queries Ad-hoc
- **Use**: `ParquetAdapter`, `DirectQueryEngine`, `HybridQueryEngine` em `core/database/`
- **Evite**: SQL disperso espalhado pelo código
- Exemplos em `core/database/database.py` e `core/adapters/database_adapter.py`

## Comandos Essenciais (Windows PowerShell)

```powershell
# Setup inicial
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Dev/Demo - Streamlit (entrada principal para testes UI)
streamlit run streamlit_app.py

# API FastAPI (documentação em http://localhost:8000/docs)
python core/main.py
# ou: uvicorn core.main:app --reload

# Testes
pytest
pytest tests/ -v  # verbose
pytest tests/ --cov=core  # com cobertura
```

## Tratamento de Erros & Fallbacks

**Mecanismo crítico em `core/llm_adapter.py`**:
- Detecta rate limits / quota exceeded
- Chama `ComponentFactory.set_gemini_unavailable(True)` para fallback
- Implementa retry automático com backoff exponencial
- **Ao alterar fluxos LLM**: preserve a lógica de fallback e logging estruturado

## Onde Procurar Exemplos

| Componente | Local | Notas |
|---|---|---|
| **Fluxo LangGraph** | `core/graph/graph_builder.py` | Nós: `classify_intent`, `generate_parquet_query`, `execute_query`, `generate_plotly_spec` |
| **UI Streamlit** | `streamlit_app.py` | Chat, CSS em `style.css`, gerenciamento de sessão em `SESSION_STATE_KEYS` |
| **Integração LLM** | `core/llm_adapter.py`, `core/llm_base.py` | Base abstrata + OpenAI concreto |
| **Estado do Agente** | `core/agent_state.py` | TypedDict com `messages`, `plotly_fig`, `final_response` |
| **Agentes Especializados** | `core/agents/` | `tool_agent.py`, `code_gen_agent.py`, `supervisor_agent.py` |
| **Autenticação** | `core/auth.py`, `core/database/sql_server_auth_db.py` | Login + RBAC básico |

## Convenções & Estilo

- **PEP8**: Projeto usa `ruff`/`black` (verificar em CI se implementado)
- **Testes**: Unitários + mocks para adapters LLM e query engines
- **Persistência**: Dados de teste em `data/` (JSON, Parquet)
- **Logging**: Use `logging.getLogger(__name__)` com níveis apropriados

## Notas Práticas ao Gerar Código

1. **Prompts & Pré/Pós-processamento**
   - Templates em `data/` (JSON, prompts em `core/prompts/`)
   - Preserve formato de saída que alimenta `plotly_spec`

2. **Mudanças de Cache**
   - Documente impacto em `core/utils/response_cache.py`
   - Justifique alterações de TTL com custo/latência

3. **Novos Agentes/Nós**
   - Siga padrão: função que recebe `state: AgentState` e retorna estado modificado
   - Registre em `core/graph/graph_builder.py` via `workflow.add_node()`

4. **Integração com Dados**
   - Consulte `data/catalog_focused.json` para esquema disponível
   - Use RAG com `CodeGenAgent.pattern_matcher` para exemplos similares

## Estrutura de Diretórios Chave

```
core/
  ├── agents/          # Agentes especializados (Tool, CodeGen, Supervisor)
  ├── llm_adapter.py   # Adaptador OpenAI com fallback
  ├── llm_base.py      # Interface abstrata para LLM
  ├── cache.py         # Cache em memória com TTL
  ├── query_processor.py # Ponto de entrada (delegador)
  ├── agent_state.py   # Estado compartilhado (TypedDict)
  ├── session_state.py # Chaves de estado Streamlit
  ├── database/        # Conectores SQL Server, Parquet
  ├── adapters/        # Database adapter abstrato
  ├── factory/         # ComponentFactory (singleton LLM)
  ├── graph/           # LangGraph builder e compilação
  ├── prompts/         # Templates de prompt
  └── utils/           # Utilidades (context, logging, etc.)

data/
  ├── catalog_focused.json      # Esquema de tabelas/colunas
  ├── query_patterns.json       # Padrões few-shot para CodeGen
  └── vector_store.pkl          # Embeddings FAISS (RAG)
```

## Checklist Antes de Commitar

- [ ] Código segue PEP8 (rode `ruff check .` localmente)
- [ ] Testes passam: `pytest`
- [ ] Cache não foi quebrado: TTL e contexto preservados
- [ ] Fallback LLM testado (simule rate limit)
- [ ] Novo agente/nó registrado em `graph_builder.py`
- [ ] Logging estruturado em DEBUG/INFO
- [ ] Documentação inline em funções críticas

---

**Última atualização**: 14 de novembro de 2025  
**Versão do projeto**: Refatoração Jules (em andamento)  
**Contato para dúvidas**: Consulte `docs/COMECE_AQUI.md` ou `README.md`
