"""
Script de diagnóstico para testar a conexão com o SQL Server.
Executa uma série de verificações para identificar problemas.
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_env_vars():
    """Verifica se as variáveis de ambiente estão configuradas."""
    logger.info("=" * 70)
    logger.info("VERIFICANDO VARIÁVEIS DE AMBIENTE")
    logger.info("=" * 70)

    required_vars = {
        "DB_SERVER": "Servidor do banco de dados",
        "DB_DATABASE": "Nome do banco de dados",
        "DB_USER": "Usuário do banco de dados",
        "DB_PASSWORD": "Senha do banco de dados",
        "DB_PORT": "Porta (padrão 1433)",
        "DB_DRIVER": "Driver ODBC",
    }

    from dotenv import load_dotenv

    dotenv_path = Path(__file__).resolve().parent / ".env"

    if dotenv_path.exists():
        logger.info(f"✓ Arquivo .env encontrado: {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path, override=True)
    else:
        logger.warning(f"✗ Arquivo .env NÃO encontrado em: {dotenv_path}")
        return False

    all_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Ocultar senha
            display_value = "***" if var == "DB_PASSWORD" else value
            logger.info(f"✓ {var}: {display_value}")
        else:
            logger.error(f"✗ {var}: NÃO CONFIGURADA ({description})")
            all_present = False

    return all_present


def check_odbc_driver():
    """Verifica se o driver ODBC está disponível."""
    logger.info("\n" + "=" * 70)
    logger.info("VERIFICANDO DRIVER ODBC")
    logger.info("=" * 70)

    try:
        import pyodbc

        logger.info("✓ pyodbc instalado")

        drivers = pyodbc.drivers()
        logger.info(f"Drivers ODBC disponíveis ({len(drivers)}):")
        for driver in drivers:
            logger.info(f"  - {driver}")

        required_driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
        if any(required_driver in driver for driver in drivers):
            logger.info(f"✓ Driver '{required_driver}' encontrado")
            return True
        else:
            logger.error(f"✗ Driver '{required_driver}' NÃO encontrado")
            return False

    except ImportError:
        logger.error("✗ pyodbc não está instalado")
        return False


def test_connection_string():
    """Testa a construção da string de conexão."""
    logger.info("\n" + "=" * 70)
    logger.info("TESTANDO CONSTRUÇÃO DA STRING DE CONEXÃO")
    logger.info("=" * 70)

    try:
        from core.config.config import Config

        config = Config()

        uri = config.SQLALCHEMY_DATABASE_URI
        logger.info("String de conexão SQLAlchemy (parcial):")
        # Ocultar partes sensíveis
        sanitized = uri.replace(config.DB_PASSWORD, "***")
        logger.info(f"  {sanitized}")

        return True
    except Exception as e:
        logger.error(f"✗ Erro ao construir string de conexão: {e}", exc_info=True)
        return False


def test_pyodbc_connection():
    """Testa conexão direta com pyodbc."""
    logger.info("\n" + "=" * 70)
    logger.info("TESTANDO CONEXÃO DIRETA COM PYODBC")
    logger.info("=" * 70)

    try:
        import pyodbc

        server = os.getenv("DB_SERVER")
        database = os.getenv("DB_DATABASE")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        driver = os.getenv("DB_DRIVER")

        connection_string = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={user};PWD={password};TrustServerCertificate=yes;"

        logger.info("Tentando conectar...")
        conn = pyodbc.connect(connection_string)
        logger.info("✓ Conexão bem-sucedida com pyodbc!")

        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        logger.info(f"✓ Consulta de teste retornou: {result}")

        conn.close()
        return True

    except Exception as e:
        logger.error(f"✗ Erro ao conectar com pyodbc: {e}", exc_info=True)
        return False


def test_sqlalchemy_connection():
    """Testa conexão via SQLAlchemy."""
    logger.info("\n" + "=" * 70)
    logger.info("TESTANDO CONEXÃO VIA SQLALCHEMY")
    logger.info("=" * 70)

    try:
        from sqlalchemy import create_engine, text
        from core.config.config import Config

        config = Config()
        uri = config.SQLALCHEMY_DATABASE_URI

        logger.info("Criando engine SQLAlchemy...")
        engine = create_engine(uri, pool_size=5, max_overflow=10, echo=True)

        logger.info("Testando conexão...")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info(f"✓ Consulta de teste retornou: {result.fetchone()}")

        logger.info("✓ Conexão bem-sucedida via SQLAlchemy!")
        return True

    except Exception as e:
        logger.error(f"✗ Erro ao conectar via SQLAlchemy: {e}", exc_info=True)
        return False


def test_db_pool():
    """Testa o pool de conexões."""
    logger.info("\n" + "=" * 70)
    logger.info("TESTANDO POOL DE CONEXÕES")
    logger.info("=" * 70)

    try:
        from core.utils.db_connection import get_db_connection

        logger.info("Obtendo conexão do pool...")
        conn = get_db_connection()
        logger.info("✓ Conexão obtida do pool")

        from sqlalchemy import text

        result = conn.execute(text("SELECT 1"))
        logger.info(f"✓ Consulta de teste retornou: {result.fetchone()}")

        conn.close()
        logger.info("✓ Pool de conexões funcionando!")
        return True

    except Exception as e:
        logger.error(f"✗ Erro com pool de conexões: {e}", exc_info=True)
        return False


def test_agent_connection():
    """Testa se o agente consegue se conectar."""
    logger.info("\n" + "=" * 70)
    logger.info("TESTANDO CONEXÃO DO AGENTE")
    logger.info("=" * 70)

    try:
        from core.query_processor import QueryProcessor

        logger.info("Inicializando QueryProcessor...")
        processor = QueryProcessor()
        logger.info("✓ QueryProcessor inicializado")

        # Tentar uma consulta simples
        logger.info("Testando uma consulta simples...")
        result = processor.process_query("Qual é a data de hoje?")
        logger.info(f"✓ Resposta do agente: {result}")

        return True

    except Exception as e:
        logger.error(f"✗ Erro ao testar agente: {e}", exc_info=True)
        return False


def main():
    """Executa todos os testes de diagnóstico."""
    logger.info("\n")
    logger.info("╔" + "═" * 68 + "╗")
    logger.info("║" + " " * 15 + "DIAGNÓSTICO DE CONEXÃO DO AGENTE BI" + " " * 18 + "║")
    logger.info("╚" + "═" * 68 + "╝")

    results = {}

    results["env_vars"] = check_env_vars()
    results["odbc_driver"] = check_odbc_driver()
    results["connection_string"] = test_connection_string()
    results["pyodbc"] = test_pyodbc_connection()
    results["sqlalchemy"] = test_sqlalchemy_connection()
    results["db_pool"] = test_db_pool()
    # results['agent'] = test_agent_connection()  # Comentado para evitar que dependa dos anteriores

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

    if passed == total:
        logger.info("\n✓ Tudo está configurado corretamente!")
        logger.info("\nPróximos passos:")
        logger.info("1. Reinicie a aplicação")
        logger.info("2. Teste o agente com uma pergunta que requer dados do banco")
        return 0
    else:
        logger.error(f"\n✗ {total - passed} teste(s) falharam. Revise os erros acima.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
