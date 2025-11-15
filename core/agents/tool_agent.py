# core/agents/tool_agent.py
import logging
from typing import Any, Dict, List  # Import List for chat_history type hint

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import (
    BaseMessage,
)  # Import BaseMessage for type hinting chat_history
from langchain_core.runnables import RunnableConfig

from core.llm_base import BaseLLMAdapter
from core.llm_gemini_adapter import GeminiLLMAdapter
from core.llm_langchain_adapter import CustomLangChainLLM
from core.utils.response_parser import parse_agent_response

from core.tools.unified_data_tools import unified_tools
from core.tools.date_time_tools import date_time_tools
from core.tools.chart_tools import chart_tools


class ToolAgent:
    def __init__(self, llm_adapter: BaseLLMAdapter):
        self.logger = logging.getLogger(__name__)
        self.llm_adapter = llm_adapter

        self.langchain_llm = CustomLangChainLLM(llm_adapter=self.llm_adapter)

        self.tools = unified_tools + date_time_tools + chart_tools
        self.agent_executor = self._create_agent_executor()
        self.logger.info("ToolAgent inicializado com adaptador Gemini.")

    def _create_agent_executor(self) -> AgentExecutor:
        """Cria e retorna um AgentExecutor com agente de ferramentas."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Você é um assistente de BI versátil, capaz de responder a perguntas sobre dados e gerar gráficos. "
                    "Use as ferramentas disponíveis para responder diretamente às perguntas do usuário. "
                    "Sempre que o usuário perguntar sobre um valor específico de uma coluna (como data de cadastro, fabricante, etc.) "
                    "para um item ou produto, use a ferramenta `consultar_dados` com os parâmetros `coluna`, `valor` e `coluna_retorno`."
                    "Exemplos de uso da ferramenta `consultar_dados`:"
                    "- Para 'Qual a data da última compra do item 9?': `consultar_dados(tabela='Filial_Madureira', coluna='ITEM', valor='9', coluna_retorno='DT ULTIMA COMPRA')`"
                    "- Para 'Qual o fabricante do produto com código 789?': `consultar_dados(tabela='Filial_Madureira', coluna='CODIGO', valor='789', coluna_retorno='FABRICANTE')`"
                    "REGRA: Produto específico + gráfico → gerar_grafico_vendas_mensais_produto(codigo_produto=N)",
                ),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_tool_calling_agent(
            llm=self.langchain_llm, tools=self.tools, prompt=prompt
        )

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
        )

    def process_query(
        self, query: str, chat_history: List[BaseMessage] = None
    ) -> Dict[str, Any]:
        """Processa a query do usuário usando o agente LangChain."""
        self.logger.info(f"Processando query com o Agente de Ferramentas: {query}")
        try:
            # Ensure chat_history is not None for invoke
            if chat_history is None:
                chat_history = []

            config = RunnableConfig(recursion_limit=10)

            self.logger.debug(
                f"Invocando agente com query: {query} "
                f"e chat_history: {chat_history}"
            )
            response = self.agent_executor.invoke(
                {"input": query, "chat_history": chat_history}, config=config
            )
            self.logger.debug(f"Resposta bruta do agente: {response}")

            # Adicionando log detalhado para depuração
            self.logger.info(f"CONTEÚDO COMPLETO DA RESPOSTA DO AGENTE: {response}")

            # Parse resposta para detectar gráficos
            raw_output = response.get("output", "")
            response_type, processed = parse_agent_response(raw_output)

            self.logger.info(f"Resposta processada como tipo: {response_type}")

            # Se for gráfico, retorna a figura Plotly diretamente
            if response_type == "chart":
                return {
                    "type": "chart",
                    "output": processed.get("output", "Erro ao gerar gráfico"),
                }

            return {
                "type": response_type,
                "output": processed.get(
                    "output", "Não foi possível gerar uma resposta."
                ),
            }

        except Exception as e:
            self.logger.error(f"Erro ao invocar o agente LangChain: {e}", exc_info=True)
            return {
                "type": "error",
                "output": (
                    "Desculpe, não consegui processar sua solicitação "
                    "no momento. Por favor, tente novamente ou reformule "
                    "sua pergunta."
                ),
            }


def initialize_agent_for_session():
    """Função de fábrica para inicializar o agente."""
    return ToolAgent(llm_adapter=GeminiLLMAdapter())
