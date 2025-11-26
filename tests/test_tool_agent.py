# tests/test_tool_agent.py
import sys
import os
import pytest
import unicodedata  # Adicionado para normalização de strings
from unittest.mock import MagicMock
from langchain_core.agents import AgentAction # Adicionado para o novo teste

# Adicionar o diretório raiz ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.agents.tool_agent import ToolAgent
from core.llm_gemini_adapter import GeminiLLMAdapter


def normalize_string(s):
    # Remove acentos e caracteres especiais, e converte para minúsculas
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    ).lower()


@pytest.fixture
def agent():
    """
    Cria uma instância do ToolAgent para os testes, com o LLM mockado.
    """
    llm_adapter = MagicMock(spec=GeminiLLMAdapter)
    llm_adapter.get_completion.return_value = {"content": "Mocked LLM response"}
    agent_instance = ToolAgent(llm_adapter=llm_adapter)
    agent_instance.agent_executor = MagicMock()
    agent_instance.agent_executor.invoke.return_value = {
        "output": "Mocked executor output"
    }
    yield agent_instance


def test_tool_agent_process_query(agent):
    """
    Testa se o ToolAgent chama corretamente o seu executor com a consulta do usuário.
    """
    query = "Qual o esquema do banco de dados?"
    response = agent.process_query(query)

    # Verificamos se a resposta do 'process_query' está no formato correto
    assert response is not None
    assert response["type"] == "text"
    assert response["output"] == "Mocked executor output"

def test_tool_agent_handles_consultar_dados_output(agent):
    """
    Testa se o ToolAgent processa corretamente a saída da ferramenta consultar_dados
    quando ela retorna uma string nos passos intermediários.
    """
    # Simular a saída do AgentExecutor.invoke para o cenário de consultar_dados
    tool_output_string = "O valor da coluna 'LUCRO R$' para o item com ITEM='8' é '1.0'."
    mock_invoke_return_value = {
        "output": "Não foi possível determinar o lucro do produto 8.", # Esta é a saída "ruim" do LLM que queremos sobrescrever
        "intermediate_steps": [
            (
                AgentAction(
                    tool="consultar_dados",
                    tool_input={"coluna": "ITEM", "valor": "8", "coluna_retorno": "LUCRO R$"},
                    log="Invoking: `consultar_dados` with `{'coluna': 'ITEM', 'coluna_retorno': 'LUCRO R$', 'valor': '8'}`",
                ),
                tool_output_string,
            )
        ],
    }
    agent.agent_executor.invoke.return_value = mock_invoke_return_value

    query = "qual é o lucro do produto 8"
    response = agent.process_query(query)

    # Verifica se a resposta contém a saída correta da ferramenta
    assert response is not None
    assert response["type"] == "text"
    assert response["output"] == tool_output_string

if __name__ == "__main__":
    pytest.main([__file__])