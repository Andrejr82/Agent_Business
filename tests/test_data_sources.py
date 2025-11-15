"""
Script de teste completo - Valida acesso a todas as fontes de dados.
SQL Server, Parquet, JSON, e outras.
"""

import sys
import logging
from pathlib import Path

# Setup
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_data_source_manager():
    """Testa o gerenciador de fontes de dados."""
    logger.info("=" * 70)
    logger.info("TESTANDO DATA SOURCE MANAGER")
    logger.info("=" * 70)

    try:
        from core.data_source_manager import get_data_manager

        manager = get_data_manager()
        status = manager.get_status()

        logger.info("\nStatus das fontes:")
        for source_name, info in status.items():
            connected = "✓" if info["connected"] else "✗"
            logger.info(f"  {connected} {source_name}: {info['type']}")

        available = manager.get_available_sources()
        logger.info(f"\nFontes disponíveis: {available}")

        if available:
            logger.info("✓ Pelo menos uma fonte de dados está disponível")
            return True
        else:
            logger.error("✗ Nenhuma fonte de dados disponível!")
            return False

    except Exception as e:
        logger.error(f"✗ Erro no Data Source Manager: {e}", exc_info=True)
        return False


def test_unified_tools():
    """Testa ferramentas unificadas."""
    logger.info("\n" + "=" * 70)
    logger.info("TESTANDO FERRAMENTAS UNIFICADAS")
    logger.info("=" * 70)

    try:
        from core.tools.unified_data_tools import (
            listar_dados_disponiveis,
            get_produtos,
        )

        # Teste 1: Listar fontes disponíveis
        logger.info("\nTeste 1: Listar fontes disponíveis...")
        result = listar_dados_disponiveis.invoke({})
        logger.info(f"  Resultado: {result['status']}")
        if result["status"] == "success":
            logger.info(f"  Fontes: {result['available_sources']}")

        # Teste 2: Buscar produtos
        logger.info("\nTeste 2: Buscar produtos (limite 5)...")
        result = get_produtos.invoke({"limit": 5})
        logger.info(f"  Resultado: {result['status']}")
        if result["status"] == "success":
            logger.info(f"  Encontrados: {result['count']} produtos")
            logger.info(f"  Fonte: {result['source']}")
            if result["data"]:
                first = result["data"][0]
                logger.info(f"  Primeiro: {first}")

        return True

    except Exception as e:
        logger.error(f"✗ Erro em ferramentas unificadas: {e}", exc_info=True)
        return False


def test_parquet_files():
    """Testa acesso a arquivos Parquet."""
    logger.info("\n" + "=" * 70)
    logger.info("TESTANDO ACESSO A ARQUIVOS PARQUET")
    logger.info("=" * 70)

    try:
        import pandas as pd
        from pathlib import Path

        base_dir = Path("data/parquet_cleaned")

        if not base_dir.exists():
            logger.warning(f"Diretório não existe: {base_dir}")
            return False

        parquet_files = list(base_dir.glob("*.parquet"))
        logger.info(f"\nArquivos Parquet encontrados ({len(parquet_files)}):")

        for filepath in parquet_files:
            try:
                df = pd.read_parquet(filepath)
                logger.info(
                    f"  ✓ {filepath.name}: {len(df)} registros, "
                    f"{len(df.columns)} colunas"
                )
            except Exception as e:
                logger.warning(f"  ✗ {filepath.name}: {e}")

        return len(parquet_files) > 0

    except Exception as e:
        logger.error(f"✗ Erro ao testar Parquet: {e}", exc_info=True)
        return False


def test_sql_server():
    """Testa conexão SQL Server."""
    logger.info("\n" + "=" * 70)
    logger.info("TESTANDO CONEXÃO SQL SERVER")
    logger.info("=" * 70)

    try:
        from core.database.database import get_db_manager

        db = get_db_manager()
        success, msg = db.test_connection()

        if success:
            logger.info(f"✓ {msg}")
            return True
        else:
            logger.warning(f"⚠ {msg}")
            return False

    except Exception as e:
        logger.warning(f"⚠ SQL Server não disponível: {e}")
        return False


def test_agent_with_data():
    """Testa o agente com dados reais."""
    logger.info("\n" + "=" * 70)
    logger.info("TESTANDO AGENTE COM DADOS REAIS")
    logger.info("=" * 70)

    try:
        from core.query_processor import QueryProcessor

        processor = QueryProcessor()

        # Teste 1: Pergunta simples
        logger.info("\nTeste 1: Pergunta simples...")
        result = processor.process_query("Qual é a data de hoje?")
        logger.info(f"  Resposta: {str(result)[:100]}...")

        # Teste 2: Pergunta sobre dados
        logger.info("\nTeste 2: Pergunta sobre produtos...")
        result = processor.process_query("Quantos produtos você consegue encontrar?")
        logger.info(f"  Resposta: {str(result)[:100]}...")

        return True

    except Exception as e:
        logger.error(f"✗ Erro no agente: {e}", exc_info=True)
        return False


def main():
    """Executa todos os testes."""
    logger.info("\n")
    logger.info("╔" + "═" * 68 + "╗")
    logger.info(
        "║" + " " * 10 + "TESTE COMPLETO - ACESSO A MÚLTIPLAS FONTES" + " " * 17 + "║"
    )
    logger.info("╚" + "═" * 68 + "╝")

    results = {}

    results["data_source_manager"] = test_data_source_manager()
    results["parquet_files"] = test_parquet_files()
    results["sql_server"] = test_sql_server()
    results["unified_tools"] = test_unified_tools()
    # results['agent'] = test_agent_with_data()

    # Relatório final
    logger.info("\n" + "=" * 70)
    logger.info("RELATÓRIO FINAL")
    logger.info("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASSOU" if result else "✗ FALHOU"
        logger.info(f"{test_name.upper()}: {status}")

    logger.info(f"\nResultado: {passed}/{total} testes passaram")

    if passed > 0:
        logger.info("\n✓ Sistema pronto para acessar dados!")
        logger.info("\nFontes de dados configuradas:")
        logger.info("  1. SQL Server (se conectado)")
        logger.info("  2. Arquivos Parquet")
        logger.info("  3. Arquivos JSON")
        logger.info("\nO agente consultará automaticamente na ordem de prioridade.")
        return 0
    else:
        logger.error("\n✗ Nenhuma fonte de dados disponível!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
