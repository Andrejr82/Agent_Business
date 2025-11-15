# core/query_processor.py
import logging
from core.agents.supervisor_agent import SupervisorAgent
from core.factory.component_factory import ComponentFactory
from core.llm_factory import LLMFactory
from core.cache import Cache


class QueryProcessor:
    """
    Ponto de entrada principal para o processamento de consultas.
    Delega a tarefa para o SupervisorAgent para orquestração.
    """

    def __init__(self):
        """
        Inicializa o processador de consultas e o agente supervisor.
        """
        self.logger = logging.getLogger(__name__)
        # Usar factory para obter adapter com fallback automático
        self.llm_adapter = LLMFactory.get_adapter()
        self.supervisor = SupervisorAgent(gemini_adapter=self.llm_adapter)
        self.cache = Cache()
        self.logger.info(
            "QueryProcessor inicializado e pronto para delegar ao SupervisorAgent."
        )

    def process_query(self, query: str) -> dict:
        """
        Processa a consulta do usuário, delegando-a diretamente ao SupervisorAgent.

        Args:
            query (str): A consulta do usuário.

        Returns:
            dict: O resultado do processamento pelo agente especialista apropriado.
        """
        cached_result = self.cache.get(query)
        if cached_result:
            self.logger.info(
                f'Resultado recuperado do cache para a consulta: "{query}"'
            )
            return cached_result

        self.logger.info(f'Delegando a consulta para o Supervisor: "{query}"')
        result = self.supervisor.route_query(query)
        self.cache.set(query, result)
        return result
