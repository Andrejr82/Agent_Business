"""Teste de conexão com LLM — migrado de OpenAI para Gemini.

Este teste será pulado se `GEMINI_API_KEY` não estiver configurada no ambiente.
"""
import os
import pytest
from core.config.config import Config
from core.llm_gemini_adapter import GeminiLLMAdapter


# Garante que as variáveis de ambiente sejam carregadas
_ = Config()


@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY não configurada"
)
def test_gemini_connection():
    adapter = GeminiLLMAdapter()
    # Faz uma chamada simples e verifica que retorna sem exceção
    resp = adapter.get_completion([
        {"role": "user", "content": "Olá"}
    ])
    assert resp is not None
