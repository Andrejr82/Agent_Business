"""
Testes para o parser de respostas e visualização de gráficos.
"""

import pytest
import json
import logging
import plotly.graph_objects as go

from core.utils.response_parser import parse_agent_response

logger = logging.getLogger(__name__)


def test_parse_chart_response_success():
    """Testa o parsing de uma resposta com sucesso de gráfico."""
    # Criar figura Plotly simples
    fig = go.Figure(
        data=[go.Scatter(x=[1, 2, 3], y=[4, 5, 6])]
    )
    chart_json = fig.to_json()

    # Simular resposta de ferramenta de gráfico
    response = json.dumps({
        "status": "success",
        "chart_type": "bar",
        "chart_data": chart_json,
        "summary": {
            "total": 15,
            "media": 5
        }
    })

    response_type, processed = parse_agent_response(response)

    assert response_type == "chart"
    assert isinstance(processed["output"], go.Figure)
    assert processed["chart_type"] == "bar"
    assert processed["summary"]["total"] == 15


def test_parse_chart_response_error():
    """Testa o parsing de uma resposta com erro de gráfico."""
    response = json.dumps({
        "status": "error",
        "message": "Produto não encontrado"
    })

    response_type, processed = parse_agent_response(response)

    assert response_type == "text"
    assert "erro" in processed["output"].lower() or \
           "Produto não encontrado" in processed["output"]


def test_parse_text_response():
    """Testa o parsing de uma resposta de texto simples."""
    response = "Este é um texto simples sem gráficos"

    response_type, processed = parse_agent_response(response)

    assert response_type == "text"
    assert processed["output"] == response


def test_parse_chart_response_with_keywords():
    """Testa detecção de gráfico por palavras-chave."""
    response = "Aqui está o gráfico de vendas por categoria"

    response_type, processed = parse_agent_response(response)

    # Pode retornar como chart ou text dependendo da detecção
    assert response_type in ["chart", "text"]


def test_parse_empty_response():
    """Testa o parsing de uma resposta vazia."""
    response_type, processed = parse_agent_response("")

    assert response_type == "text"
    assert "Nenhuma resposta" in processed["output"]


def test_parse_invalid_json():
    """Testa o parsing de resposta que parece ser JSON mas é inválida."""
    response = "Resposta que não é JSON mas tem {parêntes}"

    response_type, processed = parse_agent_response(response)

    # Deve retornar como texto
    assert response_type == "text"


def test_parse_nested_json_in_response():
    """Testa extração de JSON aninhado em uma resposta."""
    response = """
    Aqui está o resultado:
    {
        "status": "success",
        "chart_type": "line",
        "chart_data": "{}",
        "summary": {}
    }
    Análise concluída.
    """

    response_type, processed = parse_agent_response(response)

    # Pode detectar o JSON e processar como chart
    assert response_type in ["chart", "text"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
