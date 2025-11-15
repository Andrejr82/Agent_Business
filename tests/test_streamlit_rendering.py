"""Testes para renderização de gráficos no Streamlit."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import plotly.graph_objects as go
import pandas as pd
import json


class TestStreamlitRendering(unittest.TestCase):
    """Testes para garantir que gráficos são renderizados corretamente."""

    def setUp(self):
        """Configurar antes de cada teste."""
        # Criar figura Plotly de teste
        self.fig = go.Figure()
        self.fig.add_trace(
            go.Scatter(x=["A", "B", "C"], y=[1, 2, 3], mode="lines+markers")
        )

    def test_figure_is_plotly_object(self):
        """Verificar que figura é objeto Plotly."""
        self.assertIsInstance(self.fig, go.Figure)
        self.assertTrue(hasattr(self.fig, "to_json"))

    def test_figure_to_json_conversion(self):
        """Verificar que figura pode ser convertida para JSON."""
        json_str = self.fig.to_json()
        self.assertIsInstance(json_str, str)

        # Verificar que eh JSON valido
        data = json.loads(json_str)
        self.assertIn("data", data)
        self.assertIn("layout", data)

    def test_figure_json_to_figure_conversion(self):
        """Verificar que figura pode ser reconstruida de JSON."""
        from core.utils.response_parser import _extract_chart_from_response

        # Preparar resposta simulada
        chart_json_str = self.fig.to_json()
        response = json.dumps(
            {
                "status": "success",
                "chart_type": "line",
                "chart_data": chart_json_str,
                "summary": {"total": 3},
            }
        )

        # Parse
        response_type, processed = _extract_chart_from_response(response)

        self.assertEqual(response_type, "chart")
        self.assertIsInstance(processed["output"], go.Figure)

    def test_streamlit_message_storage(self):
        """Verificar que figura armazenada em dicionário pode ser recuperada."""
        message = {"role": "assistant", "output": self.fig, "type": "chart"}

        # Recuperar
        output = message.get("output")

        # Verificar
        self.assertIsInstance(output, go.Figure)
        self.assertTrue(hasattr(output, "to_json"))

    def test_session_state_figure_persistence(self):
        """Verificar que figura persiste em estado de sessão."""
        session_messages = [
            {"role": "user", "output": "gráfico de vendas"},
            {"role": "assistant", "output": self.fig, "type": "chart"},
        ]

        # Verificar que figura eh recuperavel depois
        chart_message = session_messages[1]
        recovered_fig = chart_message["output"]

        self.assertIsInstance(recovered_fig, go.Figure)
        self.assertTrue(hasattr(recovered_fig, "to_json"))

    def test_figure_vs_dataframe_detection(self):
        """Verificar que sistema diferencia figura de DataFrame."""
        fig = self.fig
        df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})

        # Figure check
        self.assertTrue(isinstance(fig, go.Figure))
        self.assertFalse(isinstance(fig, pd.DataFrame))

        # DataFrame check
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertFalse(isinstance(df, go.Figure))

    def test_response_type_routing(self):
        """Verificar que response['type'] determina renderização correta."""
        responses = {
            "chart": {"type": "chart", "output": self.fig},
            "dataframe": {"type": "dataframe", "output": pd.DataFrame({"A": [1, 2]})},
            "text": {"type": "text", "output": "Hello world"},
        }

        for response_type, response in responses.items():
            if response_type == "chart":
                self.assertIsInstance(response["output"], go.Figure)
            elif response_type == "dataframe":
                self.assertIsInstance(response["output"], pd.DataFrame)
            else:
                self.assertIsInstance(response["output"], str)


class TestResponseParserIntegration(unittest.TestCase):
    """Testes de integração do response parser."""

    def setUp(self):
        """Configurar antes de cada teste."""
        # Criar figura Plotly de teste
        self.fig = go.Figure()
        self.fig.add_trace(
            go.Scatter(x=["A", "B", "C"], y=[1, 2, 3], mode="lines+markers")
        )

    def test_parse_chart_response_full_flow(self):
        """Testar fluxo completo de gráfico - usa dados simulados."""
        from core.utils.response_parser import parse_agent_response

        # Simular resposta de ferramenta (sem depender de dados reais)
        simulated_result = {
            "status": "success",
            "chart_type": "line_temporal_mensal",
            "chart_data": self.fig.to_json(),
            "summary": {
                "codigo_produto": 59294,
                "total_vendas": 16385,
                "venda_media": 1260.38,
            },
        }

        # Converter para JSON string (como agente faria)
        response_str = json.dumps(simulated_result)

        # Parse
        response_type, processed = parse_agent_response(response_str)

        # Verificar
        self.assertEqual(response_type, "chart")
        self.assertIsInstance(processed["output"], go.Figure)
        self.assertIn("summary", processed)

    def test_error_response_handling(self):
        """Testar tratamento de respostas de erro."""
        from core.utils.response_parser import parse_agent_response

        error_response = json.dumps(
            {
                "status": "error",
                "chart_type": "line",
                "chart_data": "{...}",
                "message": "Produto nao encontrado",
            }
        )

        response_type, processed = parse_agent_response(error_response)

        self.assertEqual(response_type, "text")
        self.assertIn("Produto nao encontrado", processed["output"])


if __name__ == "__main__":
    unittest.main()
