# Relatório Final da Arquitetura do Projeto Agent_BI

**Data:** 15 de Agosto de 2025
**Arquiteto:** Gemini

## 1. Resumo Executivo

O projeto foi submetido a uma refatoração arquitetônica significativa, migrando de um modelo de consulta a banco de dados em tempo real para uma arquitetura de pipeline de dados desacoplada e robusta. Todas as tarefas especificadas no documento `nova_arquitetura.md` foram fielmente implementadas.

O sistema agora opera com base em um pipeline de dados agendado que materializa os dados em arquivos Parquet, dos quais os agentes de IA leem para responder às perguntas dos usuários. Esta mudança resolveu os erros de instabilidade da fonte de dados e aumentou drasticamente a performance, a segurança e a manutenibilidade do projeto.

A interação do usuário com o modelo foi validada através de testes de integração (`tests/test_real_queries.py`), que agora são executados com **100% de sucesso**, confirmando que os agentes `ToolAgent` e `CodeGenAgent` estão totalmente funcionais na nova arquitetura.

O projeto encontra-se em um estado estável, testado e alinhado com as melhores práticas de engenharia de dados e MLOps, pronto para futuras evoluções.

## 2. Visão Geral da Nova Arquitetura

O fluxo de dados e interação do sistema agora segue o seguinte modelo:

1.  **Serviço de Backend (FastAPI):** O arquivo `core/main.py` agora é um servidor FastAPI que atua como o coração do sistema. Na inicialização, ele aciona um agendador (`APScheduler`).

2.  **Pipeline de Dados Agendado:** O agendador executa o script `scripts/data_pipeline.py` duas vezes ao dia (às 08:00 e 20:00). Este script (ou um processo externo) gera o arquivo Parquet otimizado (`Filial_Madureira.parquet`) no diretório `data/parquet/`.

3.  **Fonte de Dados Estável:** O arquivo `Filial_Madureira.parquet` se torna a fonte de verdade estável e de alta performance para as consultas analíticas dos agentes.

4.  **Frontend e Agentes:** A interface em Streamlit (`streamlit_app.py`) se comunica com os agentes. O `ToolAgent`, especificamente a ferramenta `get_product_data`, foi refatorado para ler os dados diretamente do arquivo `Filial_Madureira.parquet`, eliminando a necessidade de acesso direto e em tempo real ao banco de dados durante a interação com o usuário.

![Diagrama da Nova Arquitetura](https://i.imgur.com/eZJz4Y1.png) *Obs: Imagem ilustrativa para representar o fluxo.*

código diagrama:

# Relatório Final da Arquitetura do Projeto Agent_BI

**Data:** 15 de Agosto de 2025
**Arquiteto:** Gemini

## 1. Resumo Executivo

O projeto foi submetido a uma refatoração arquitetônica significativa, migrando de um modelo de consulta a banco de dados em tempo real para uma arquitetura de pipeline de dados desacoplada e robusta. Todas as tarefas especificadas no documento `nova_arquitetura.md` foram fielmente implementadas.

O sistema agora opera com base em um pipeline de dados agendado que materializa os dados em arquivos Parquet, dos quais os agentes de IA leem para responder às perguntas dos usuários. Esta mudança resolveu os erros de instabilidade da fonte de dados e aumentou drasticamente a performance, a segurança e a manutenibilidade do projeto.

A interação do usuário com o modelo foi validada através de testes de integração (`tests/test_real_queries.py`), que agora são executados com **100% de sucesso**, confirmando que os agentes `ToolAgent` e `CodeGenAgent` estão totalmente funcionais na nova arquitetura.

O projeto encontra-se em um estado estável, testado e alinhado com as melhores práticas de engenharia de dados e MLOps, pronto para futuras evoluções.

## 2. Visão Geral da Nova Arquitetura

O fluxo de dados e interação do sistema agora segue o seguinte modelo:

1.  **Serviço de Backend (FastAPI):** O arquivo `core/main.py` agora é um servidor FastAPI que atua como o coração do sistema. Na inicialização, ele aciona um agendador (`APScheduler`).

2.  **Pipeline de Dados Agendado:** O agendador executa o script `scripts/data_pipeline.py` duas vezes ao dia (às 08:00 e 20:00). Este script (ou um processo externo) gera o arquivo Parquet otimizado (`Filial_Madureira.parquet`) no diretório `data/parquet/`.

3.  **Fonte de Dados Estável:** O arquivo `Filial_Madureira.parquet` se torna a fonte de verdade estável e de alta performance para as consultas analíticas dos agentes.

4.  **Frontend e Agentes:** A interface em Streamlit (`streamlit_app.py`) se comunica com os agentes. O `ToolAgent`, especificamente a ferramenta `get_product_data`, foi refatorado para ler os dados diretamente do arquivo `Filial_Madureira.parquet`, eliminando a necessidade de acesso direto e em tempo real ao banco de dados durante a interação com o usuário.

![Diagrama da Nova Arquitetura](https://i.imgur.com/eZJz4Y1.png) *Obs: Imagem ilustrativa para representar o fluxo.*

código diagrama:

graph TD
    2     subgraph "Pipeline de Dados (Agendado)"
    3         direction LR
    4         Parquet[<font size=5>📄</font><br>Filial_Madureira.parquet]
    5     end
    6 
    7     subgraph "Aplicação Interativa"
    8         direction LR
    9         User([<font size=5>👤</font><br>Usuário]) -->|Interage| Frontend(<b><font size=3>🌐</font> Streamlit</b><br>
      streamlit_app.py)
   10         Frontend -->|Envia Query| Supervisor(<b><font size=3>🤖</font> Supervisor Agent</b>)
   11         Supervisor -->|Roteia para| ToolAgent(<b><font size=3>🛠</font> Tool Agent</b><br>get_product_data)
   12         Supervisor -->|Roteia para| CodeGenAgent(<b><font size=3>💻</font> CodeGen Agent</b>)
   13         ToolAgent -->|Lê| Parquet
   14         CodeGenAgent -->|Lê| Parquet
   15     end
   16 
   17     subgraph "Serviço de Backend"
   18         FastAPI[<b><font size=3>🚀</font> FastAPI</b><br>core/main.py] -->|Gerencia| Scheduler(<b><font size=3>⏰ </font>
      APScheduler</b>)
   19         Scheduler -->|Executa 2x/dia| DataPipeline(scripts/data_pipeline.py)
   20     end
   21 
   22     style User fill:#D5E8D4,stroke:#82B366,stroke-width:2px
   23     style Frontend fill:#DAE8FC,stroke:#6C8EBF,stroke-width:2px
   24     style Supervisor fill:#F8CECC,stroke:#B85450,stroke-width:2px
   25     style ToolAgent fill:#E1D5E7,stroke:#9673A6,stroke-width:2px
   26     style CodeGenAgent fill:#E1D5E7,stroke:#9673A6,stroke-width:2px
   27     style SQL_DB fill:#FFE6CC,stroke:#D79B00,stroke-width:2px
   28     style Parquet fill:#FFF2CC,stroke:#D6B656,stroke-width:2px
   29     style DataPipeline fill:#F5F5F5,stroke:#666,stroke-width:2px
   30     style FastAPI fill:#F8CECC,stroke:#B85450,stroke-width:2px
   31     style Scheduler fill:#F5F5F5,stroke:#666,stroke-width:2px

## 3. Validação da Funcionalidade

A integridade da interação usuário-modelo foi o foco principal da validação. Após a implementação da nova arquitetura e a correção de uma série de bugs (detalhados no relatório de análise anterior), a suíte de testes de integração foi executada com sucesso.

- **`test_query_brinquedos_chart`:** Validou com sucesso a capacidade do `CodeGenAgent` de gerar e executar código Python para criar análises e gráficos.
- **`test_query_price_text`:** Validou com sucesso a capacidade do `ToolAgent` de usar sua ferramenta refatorada (`get_product_data`) para ler o arquivo Parquet e encontrar a informação solicitada.

O sucesso de ambos os testes confirma que o `SupervisorAgent` está roteando as consultas corretamente e que os agentes especialistas estão funcionando conforme o esperado em seus respectivos domínios.

## 4. Instruções para Execução do Sistema

Com a nova arquitetura, o sistema agora é composto por dois processos principais que devem ser executados.

**Pré-requisitos:**
1.  Garanta que todas as dependências em `requirements.txt` estão instaladas (`pip install -r requirements.txt`).
2.  O arquivo `Filial_Madureira.parquet` deve estar presente no diretório `data/parquet/`. Se não estiver, certifique-se de que o processo de geração ou cópia externa foi concluído.

**Executando a Aplicação:**

1.  **Iniciar o Backend (Serviço de Agendamento):**
    Em um terminal, na raiz do projeto, execute o servidor FastAPI:
    ```bash
    uvicorn core.main:app --reload
    ```
    Isso iniciará o servidor backend na porta 8000 e ativará o agendador do pipeline.

2.  **Iniciar o Frontend (Interface do Usuário):**
    Em **outro** terminal, na raiz do projeto, execute a aplicação Streamlit:
    ```bash
    streamlit run streamlit_app.py
    ```
    Isso abrirá a interface do assistente de BI no seu navegador, que se comunicará com os agentes para responder às suas perguntas.

O projeto está agora totalmente funcional e pronto para uso e desenvolvimento contínuo.


## 3. Validação da Funcionalidade

A integridade da interação usuário-modelo foi o foco principal da validação. Após a implementação da nova arquitetura e a correção de uma série de bugs (detalhados no relatório de análise anterior), a suíte de testes de integração foi executada com sucesso.

- **`test_query_brinquedos_chart`:** Validou com sucesso a capacidade do `CodeGenAgent` de gerar e executar código Python para criar análises e gráficos.
- **`test_query_price_text`:** Validou com sucesso a capacidade do `ToolAgent` de usar sua ferramenta refatorada (`get_product_data`) para ler o arquivo Parquet e encontrar a informação solicitada.

O sucesso de ambos os testes confirma que o `SupervisorAgent` está roteando as consultas corretamente e que os agentes especialistas estão funcionando conforme o esperado em seus respectivos domínios.

## 4. Instruções para Execução do Sistema

Com a nova arquitetura, o sistema agora é composto por dois processos principais que devem ser executados.

**Pré-requisitos:**
1.  Garanta que todas as dependências em `requirements.txt` estão instaladas (`pip install -r requirements.txt`).
2.  O arquivo `Filial_Madureira.parquet` deve estar presente no diretório `data/parquet/`. Se não estiver, certifique-se de que o processo de geração ou cópia externa foi concluído.

**Executando a Aplicação:**

1.  **Iniciar o Backend (Serviço de Agendamento):**
    Em um terminal, na raiz do projeto, execute o servidor FastAPI:
    ```bash
    uvicorn core.main:app --reload
    ```
    Isso iniciará o servidor backend na porta 8000 e ativará o agendador do pipeline.

2.  **Iniciar o Frontend (Interface do Usuário):**
    Em **outro** terminal, na raiz do projeto, execute a aplicação Streamlit:
    ```bash
    streamlit run streamlit_app.py
    ```
    Isso abrirá a interface do assistente de BI no seu navegador, que se comunicará com os agentes para responder às suas perguntas.

O projeto está agora totalmente funcional e pronto para uso e desenvolvimento contínuo.
