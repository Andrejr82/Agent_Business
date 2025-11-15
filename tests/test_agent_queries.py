"""
Script para testar o agente BI com perguntas reais sobre produtos.
"""

import logging
from core.agents.tool_agent import ToolAgent

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_agent_queries():
    """Testa o agente com perguntas reais."""

    print("\n" + "=" * 70)
    print("TESTE DO AGENTE BI COM PERGUNTAS REAIS")
    print("=" * 70 + "\n")

    try:
        agent = ToolAgent()
        logger.info("✓ Agente ToolAgent inicializado com sucesso")

        # Teste 1: Listar produtos disponíveis
        print("TESTE 1: Consultar dados disponíveis")
        print("-" * 70)
        result = agent.run(
            "Quais fontes de dados estão disponíveis? " "Quantos produtos temos?"
        )
        print(f"Resultado: {result}\n")

        # Teste 2: Buscar produto específico
        print("TESTE 2: Buscar produto específico")
        print("-" * 70)
        result = agent.run("Busque informações de produtos da categoria Armarinho")
        print(f"Resultado: {result}\n")

        # Teste 3: Consulta com fallback
        print("TESTE 3: Consulta com fallback de fontes")
        print("-" * 70)
        result = agent.run(
            "Quantos produtos diferentes temos no SQL Server e em Parquet?"
        )
        print(f"Resultado: {result}\n")

        print("=" * 70)
        print("✓ TODOS OS TESTES DO AGENTE CONCLUÍDOS")
        print("=" * 70 + "\n")

    except Exception as e:
        logger.error(f"Erro ao testar agente: {e}", exc_info=True)
        print(f"✗ Erro: {e}\n")


if __name__ == "__main__":
    test_agent_queries()
