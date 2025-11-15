"""
Testes para ferramentas de gráficos.
Valida a geração de diferentes tipos de visualizações.
"""

import pytest
import logging
from unittest.mock import patch, MagicMock
import pandas as pd

from core.tools.chart_tools import (
    gerar_grafico_vendas_por_categoria,
    gerar_grafico_estoque_por_produto,
    gerar_comparacao_precos_categorias,
    gerar_analise_distribuicao_estoque,
    gerar_grafico_pizza_categorias,
    gerar_dashboard_analise_completa,
    gerar_grafico_vendas_por_produto,
    gerar_grafico_vendas_mensais_produto,
    gerar_grafico_automatico,
    chart_tools,
)

logger = logging.getLogger(__name__)


# Mock data para testes
@pytest.fixture
def mock_data():
    """Cria dados mock para testes."""
    return pd.DataFrame(
        {
            "categoria": [
                "Eletrônicos",
                "Eletrônicos",
                "Alimentos",
                "Alimentos",
                "Livros",
                "Livros",
                "Vestuário",
                "Vestuário",
            ],
            "nome": [
                "Notebook",
                "Mouse",
                "Arroz",
                "Feijão",
                "Python",
                "Django",
                "Camiseta",
                "Calça",
            ],
            "est_une": [10, 50, 100, 80, 5, 3, 200, 150],
            "preco_38_percent": [
                2500.00,
                50.00,
                30.00,
                35.00,
                120.00,
                150.00,
                80.00,
                120.00,
            ],
        }
    )


@patch("core.tools.chart_tools.get_data_manager")
@pytest.mark.parametrize(
    "limite,ordenar_por",
    [
        (10, "descendente"),
        (5, "ascendente"),
        (15, "descendente"),
    ],
)
def test_gerar_grafico_vendas_por_categoria(
    mock_manager, mock_data, limite, ordenar_por
):
    """Testa geração de gráfico de vendas por categoria."""
    mock_dm = MagicMock()
    mock_dm.get_data.return_value = mock_data
    mock_manager.return_value = mock_dm

    resultado = gerar_grafico_vendas_por_categoria.invoke(
        {"limite": limite, "ordenar_por": ordenar_por}
    )

    assert resultado["status"] == "success"
    assert "chart_data" in resultado
    assert "summary" in resultado
    assert resultado["chart_type"] == "donut"
    assert resultado["summary"]["total_categorias"] > 0


@patch("core.tools.chart_tools.get_data_manager")
def test_gerar_grafico_estoque_por_produto(mock_manager, mock_data):
    """Testa geração de gráfico de estoque."""
    mock_dm = MagicMock()
    mock_dm.get_data.return_value = mock_data
    mock_manager.return_value = mock_dm

    resultado = gerar_grafico_estoque_por_produto.invoke(
        {"limite": 15, "minimo_estoque": 0}
    )

    assert resultado["status"] == "success"
    assert "chart_data" in resultado
    assert "summary" in resultado
    assert resultado["chart_type"] == "bar_vertical"
    assert "estoque_total" in resultado["summary"]
    assert "estoque_medio" in resultado["summary"]


@patch("core.tools.chart_tools.get_data_manager")
def test_gerar_comparacao_precos_categorias(mock_manager, mock_data):
    """Testa geração de gráfico de comparação de preços."""
    mock_dm = MagicMock()
    mock_dm.get_data.return_value = mock_data
    mock_manager.return_value = mock_dm

    resultado = gerar_comparacao_precos_categorias.invoke({})

    assert resultado["status"] == "success"
    assert "chart_data" in resultado
    assert "summary" in resultado
    assert resultado["chart_type"] == "bar_line_combo"
    assert "preco_medio_geral" in resultado["summary"]


@patch("core.tools.chart_tools.get_data_manager")
def test_gerar_analise_distribuicao_estoque(mock_manager, mock_data):
    """Testa geração de análise de distribuição."""
    mock_dm = MagicMock()
    mock_dm.get_data.return_value = mock_data
    mock_manager.return_value = mock_dm

    resultado = gerar_analise_distribuicao_estoque.invoke({})

    assert resultado["status"] == "success"
    assert "chart_data" in resultado
    assert "summary" in resultado
    assert resultado["chart_type"] == "distribution"
    assert "media" in resultado["summary"]
    assert "mediana" in resultado["summary"]
    assert "desvio_padrao" in resultado["summary"]


@patch("core.tools.chart_tools.get_data_manager")
def test_gerar_grafico_pizza_categorias(mock_manager, mock_data):
    """Testa geração de gráfico de pizza."""
    mock_dm = MagicMock()
    mock_dm.get_data.return_value = mock_data
    mock_manager.return_value = mock_dm

    resultado = gerar_grafico_pizza_categorias.invoke({})

    assert resultado["status"] == "success"
    assert "chart_data" in resultado
    assert "summary" in resultado
    assert resultado["chart_type"] == "pie"
    assert "categorias" in resultado["summary"]


@patch("core.tools.chart_tools.get_data_manager")
def test_gerar_dashboard_analise_completa(mock_manager, mock_data):
    """Testa geração de dashboard completo."""
    mock_dm = MagicMock()
    mock_dm.get_data.return_value = mock_data
    mock_manager.return_value = mock_dm

    resultado = gerar_dashboard_analise_completa.invoke({})

    assert resultado["status"] == "success"
    assert "chart_data" in resultado
    assert "summary" in resultado
    assert resultado["chart_type"] == "dashboard"
    assert "total_produtos" in resultado["summary"]


@patch("core.tools.chart_tools.get_data_manager")
def test_erro_quando_nenhum_dado_disponivel(mock_manager):
    """Testa tratamento de erro quando não há dados."""
    mock_dm = MagicMock()
    mock_dm.get_data.side_effect = Exception("Conexão falhou")
    mock_manager.return_value = mock_dm

    resultado = gerar_grafico_vendas_por_categoria.invoke(
        {"limite": 10, "ordenar_por": "descendente"}
    )

    assert resultado["status"] == "error"


def test_chart_tools_disponibilidade():
    """Verifica disponibilidade de todas as ferramentas."""
    assert len(chart_tools) == 9

    tool_names = [tool.name for tool in chart_tools]
    expected = [
        "gerar_grafico_vendas_por_categoria",
        "gerar_grafico_estoque_por_produto",
        "gerar_comparacao_precos_categorias",
        "gerar_analise_distribuicao_estoque",
        "gerar_grafico_pizza_categorias",
        "gerar_dashboard_analise_completa",
        "gerar_grafico_vendas_por_produto",
        "gerar_grafico_vendas_mensais_produto",
        "gerar_grafico_automatico",
    ]

    for tool_name in expected:
        assert tool_name in tool_names


@patch("core.tools.chart_tools.get_data_manager")
def test_gerar_grafico_vendas_por_produto(mock_manager, mock_data):
    """Testa geração de gráfico de vendas por produto."""
    mock_dm = MagicMock()
    mock_dm.get_data.return_value = mock_data
    mock_manager.return_value = mock_dm

    resultado = gerar_grafico_vendas_por_produto.invoke(
        {"codigo_produto": 1, "unidade": "SCR"}
    )

    assert resultado["status"] == "success"
    assert "chart_data" in resultado or "message" in resultado
    assert resultado["chart_type"] in ["line_temporal", "vendas_produto"]


@patch("core.tools.chart_tools.get_data_manager")
def test_gerar_grafico_automatico(mock_manager, mock_data):
    """Testa geração automática de gráficos por descrição."""
    mock_dm = MagicMock()
    mock_dm.get_data.return_value = mock_data
    mock_manager.return_value = mock_dm

    # Teste com descrição de vendas por categoria
    resultado = gerar_grafico_automatico.invoke(
        {"descricao": "gráfico de vendas por categoria"}
    )

    assert resultado["status"] == "success"
    assert "chart_data" in resultado or "message" in resultado

    # Teste com descrição de estoque
    resultado = gerar_grafico_automatico.invoke(
        {"descricao": "mostrar estoque disponível por produto"}
    )

    assert resultado["status"] == "success"

    # Teste com descrição de dashboard
    resultado = gerar_grafico_automatico.invoke(
        {"descricao": "dashbord completo da análise"}
    )

    assert resultado["status"] == "success"


@patch("core.tools.chart_tools.get_data_manager")
def test_gerar_grafico_vendas_mensais_produto(mock_manager):
    """Testa geração de gráfico de vendas mensais com dados reais."""
    # Criar dataframe com estrutura real (mes_01 até mes_12)
    mock_data = pd.DataFrame(
        {
            "codigo": [59294, 59294],
            "une_nome": ["SCR", "ITA"],
            "nome_produto": ["PAPEL CHAMEX A4 75GRS", "PAPEL CHAMEX A4 75GRS"],
            "nome_categoria": ["OFFICE", "OFFICE"],
            "mes_01": [1302, 1400],
            "mes_02": [871, 900],
            "mes_03": [1094, 1100],
            "mes_04": [1079, 1150],
            "mes_05": [1412, 1500],
            "mes_06": [2210, 2300],
            "mes_07": [1096, 1200],
            "mes_08": [1518, 1600],
            "mes_09": [1366, 1450],
            "mes_10": [1481, 1550],
            "mes_11": [1177, 1250],
            "mes_12": [1156, 1200],
            "mes_parcial": [623, 650],
        }
    )

    mock_dm = MagicMock()
    mock_dm.get_data.return_value = mock_data
    mock_manager.return_value = mock_dm

    resultado = gerar_grafico_vendas_mensais_produto.invoke(
        {"codigo_produto": 59294, "unidade_filtro": ""}
    )

    assert resultado["status"] == "success"
    assert resultado["chart_type"] == "line_temporal_mensal"
    assert "chart_data" in resultado
    assert "summary" in resultado
    assert resultado["summary"]["codigo_produto"] == 59294
    assert resultado["summary"]["total_vendas"] > 0
    assert "mes_maior_venda" in resultado["summary"]
    assert "mes_menor_venda" in resultado["summary"]
    assert "dados_mensais" in resultado["summary"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
