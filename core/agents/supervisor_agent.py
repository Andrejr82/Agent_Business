# core/agents/supervisor_agent.py
import logging
from typing import Dict, Any

from core.llm_adapter import OpenAILLMAdapter
from core.agents.tool_agent import ToolAgent

class SupervisorAgent:
    """
    Agente supervisor que roteia a consulta do usuário para o agente
    especialista apropriado. Detecta intenção de gráficos automaticamente.
    """
    
    CHART_KEYWORDS = [
        'gráfico', 'gráficos', 'grafico', 'graficos',
        'visualizar', 'visualização', 'visualizacao',
        'mostrar', 'chart', 'charts',
        'vendas', 'estoque', 'distribuição', 'distribuicao',
        'análise', 'analise', 'comparação', 'comparacao',
        'pizza', 'barras', 'linha', 'histograma', 'dashboard',
        'plot', 'plotar', 'desenhar',
        'temporal', 'série', 'serie', 'evolução', 'evolucao',
        'mensal', 'mês', 'mes', 'semanal', 'trend', 'tendência', 'tendencia',
        'produto', 'sku', 'código', 'codigo'
    ]
    
    def __init__(self, openai_adapter: OpenAILLMAdapter):
        """
        Inicializa o supervisor e o ToolAgent.
        """
        self.logger = logging.getLogger(__name__)
        self.tool_agent = ToolAgent(llm_adapter=openai_adapter)
        self.logger.info("SupervisorAgent inicializado com ToolAgent.")

    def _detect_chart_intent(self, query: str) -> bool:
        """
        Detecta se a consulta tem intenção de gerar gráficos.
        
        Args:
            query: Consulta do usuário
            
        Returns:
            True se detecta intenção de gráfico, False caso contrário
        """
        query_lower = query.lower()
        
        # Verificar se contém palavras-chave de gráficos
        for keyword in self.CHART_KEYWORDS:
            if keyword in query_lower:
                self.logger.info(
                    f"Intenção de gráfico detectada: '{keyword}'"
                )
                return True
        
        return False

    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Roteia a consulta para o ToolAgent.
        
        Args:
            query: Consulta do usuário
            
        Returns:
            Resposta do agente apropriado
        """
        # Detectar se é requisição de gráfico
        is_chart_request = self._detect_chart_intent(query)
        
        if is_chart_request:
            self.logger.info(
                f"Roteando consulta de gráfico para ToolAgent: '{query}'"
            )
        else:
            self.logger.info(
                f"Roteando consulta padrão para ToolAgent: '{query}'"
            )
        
        # Ambos os tipos vão para ToolAgent que decidirá qual ferramenta usar
        return self.tool_agent.process_query(query)
