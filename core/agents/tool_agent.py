# core/agents/tool_agent.py
import logging
import sys
from typing import Any, Dict, List  # Import List for chat_history type hint

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import (
    BaseMessage,
)  # Import BaseMessage for type hinting chat_history
from langchain_core.runnables import RunnableConfig
from langchain_core.agents import AgentAction, AgentFinish # Importar AgentAction e AgentFinish

from core.llm_base import BaseLLMAdapter
from core.llm_gemini_adapter import GeminiLLMAdapter
from core.llm_langchain_adapter import CustomLangChainLLM
from core.utils.response_parser import parse_agent_response
from core.utils.chart_saver import save_chart

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
                    "Você é um Agente de Negócios versátil, capaz de responder a perguntas sobre dados e gerar gráficos. "
                    "Sua principal função é usar as ferramentas disponíveis para responder diretamente às perguntas do usuário, sem adicionar comentários desnecessários. "
                    "Sempre que o usuário se referir a 'produto' ou 'item' em um contexto de busca por um código ou identificador, utilize a coluna 'ITEM' no filtro da ferramenta `consultar_dados`."
                    "Se o usuário perguntar sobre 'lucro', 'margem' ou 'rentabilidade', utilize a coluna 'LUCRO R$' na ferramenta `consultar_dados`."
                    "Se o usuário perguntar sobre 'lucro percentual', utilize a coluna 'LUCRO TOTAL %' ou 'LUCRO UNIT %' conforme o contexto."
                    "Sempre que o usuário perguntar sobre um valor específico de qualquer coluna (como data de cadastro, fabricante, quantidade, etc.) "
                    "para um item ou produto, use a ferramenta `consultar_dados` com os parâmetros `coluna` (para o filtro), `valor` (do filtro) e `coluna_retorno` (a coluna cujo valor se deseja obter). "
                    "No entanto, se o usuário fizer uma pergunta geral sobre um produto ou item (ex: 'Quais os dados do produto 9?', 'Me fale sobre o item 10?'), utilize a ferramenta `consultar_dados` apenas com os parâmetros `coluna` e `valor`, sem especificar `coluna_retorno`. Isso fará com que a ferramenta retorne todas as colunas disponíveis para aquele item."
                    "É importante que você use `consultar_dados` mesmo que a coluna usada para filtrar seja a mesma que a coluna que se deseja retornar."
                    "Quando o usuário perguntar sobre as colunas disponíveis, a estrutura dos dados, ou informações gerais sobre o dataset, use a ferramenta `listar_colunas_disponiveis`."
                    "Exemplos de uso da ferramenta `consultar_dados`:"
                    "- Para 'Qual a data da última compra do item 9?': `consultar_dados(coluna='ITEM', valor='9', coluna_retorno='DT ULTIMA COMPRA')`"
                    "- Para 'Qual o fabricante do produto com código 789?': `consultar_dados(coluna='CODIGO', valor='789', coluna_retorno='FABRICANTE')`"
                    "- Para 'Qual o ITEM do produto com ITEM 1?': `consultar_dados(coluna='ITEM', valor='1', coluna_retorno='ITEM')`"
                    "Para criar um ranking dos produtos mais vendidos, use a ferramenta `gerar_ranking_produtos_mais_vendidos`. Você pode especificar o número de produtos no ranking com o parâmetro `top_n`."
                    "Para criar um dashboard com múltiplos gráficos, use a ferramenta `gerar_dashboard_dinamico`. Forneça uma lista dos nomes das ferramentas de gráfico que você deseja incluir no argumento `graficos`."
                    "REGRA: Produto específico + gráfico → gerar_grafico_vendas_mensais_produto(codigo_produto=N)"
                    "IMPORTANTE: Quando uma ferramenta retornar uma resposta, repasse essa resposta DIRETAMENTE ao usuário. Não adicione comentários, resumos ou frases como 'Compreendi.'. Se a ferramenta retornar uma mensagem de erro ou indicar que não encontrou dados, repasse essa mensagem ao usuário."
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
            return_intermediate_steps=True, # Adicionado para obter os passos intermediários
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

            final_output = response.get("output", "Não foi possível gerar uma resposta.")
            response_type = "text" # Padrão

            # Verificar se há passos intermediários e extrair a saída da ferramenta se aplicável
            if "intermediate_steps" in response and response["intermediate_steps"]:
                for step in reversed(response["intermediate_steps"]):
                    if isinstance(step, tuple) and len(step) == 2:
                        action, observation = step
                        
                        # Se a observação for um dicionário de uma ferramenta de gráfico bem-sucedida
                        if isinstance(observation, dict) and observation.get("status") == "success" and "chart_data" in observation:
                            self.logger.info(f"Extraindo dados do gráfico da ferramenta: {action.tool}")
                            final_output = observation["chart_data"]
                            response_type = "chart"
                            save_chart(final_output)  # Salvar o gráfico
                            break
                        
                        # Lógica existente para ferramentas que retornam string
                        elif isinstance(action, AgentAction) and isinstance(observation, str):
                            if action.tool == "consultar_dados":
                                final_output = observation
                                self.logger.info(f"Usando saída direta da ferramenta consultar_dados: {final_output}")
                                break

            # Se o tipo de resposta for gráfico, retorna diretamente
            if response_type == "chart":
                return {
                    "type": "chart",
                    "output": final_output,
                }

            # Processamento legado para texto
            response_type, processed = parse_agent_response(final_output)
            return {
                "type": "text", # Changed from response_type to "text" to ensure text output for general queries
                "output": processed.get("output", final_output),
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
