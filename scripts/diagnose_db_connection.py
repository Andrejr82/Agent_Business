"""
Script de diagnóstico para testar a conexão com o banco de dados.
"""

import sys
import os
import logging

# Adicionar o diretório raiz ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database.database import get_db_manager
from core.config.config import Config

# Configurar logging básico para ver a saída
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def diagnose_database_connection():
    """
    Tenta conectar ao banco de dados e relata o status.
    """
    logger = logging.getLogger(__name__)
    logger.info("Iniciando diagnóstico de conexão com o banco de dados...")

    try:
        # Carregar configuração para garantir que as variáveis de ambiente estão lidas
        config = Config()
        logger.info("Configurações carregadas.")
        logger.info(f"Driver: {config.DB_DRIVER}")
        logger.info(f"Servidor: {config.DB_SERVER}")
        logger.info(f"Banco de Dados: {config.DB_DATABASE}")
        logger.info(f"Usuário: {config.DB_USER}")

        # Obter o gerenciador de banco de dados
        db_manager = get_db_manager()
        logger.info("Obtendo gerenciador de banco de dados...")

        # Testar a conexão
        success, message = db_manager.test_connection()

        if success:
            logger.info("=" * 50)
            logger.info(
                "✅ SUCESSO: A conexão com o banco de dados foi estabelecida com êxito."
            )
            logger.info(f"Mensagem do sistema: {message}")
            logger.info("=" * 50)
        else:
            logger.error("=" * 50)
            logger.error("❌ FALHA: Não foi possível conectar ao banco de dados.")
            logger.error(f"Mensagem de erro: {message}")
            logger.error(
                "Por favor, verifique as seguintes variáveis no seu arquivo .env:"
            )
            logger.error("- MSSQL_SERVER")
            logger.error("- MSSQL_DATABASE")
            logger.error("- MSSQL_USER")
            logger.error("- MSSQL_PASSWORD")
            logger.error("- DB_DRIVER")
            logger.error("=" * 50)

    except Exception as e:
        logger.error("=" * 50)
        logger.error(
            f"Ocorreu um erro inesperado durante o diagnóstico: {e}", exc_info=True
        )
        logger.error("=" * 50)


if __name__ == "__main__":
    diagnose_database_connection()
