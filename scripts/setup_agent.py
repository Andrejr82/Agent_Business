"""
Script de configuração e teste do agente com banco de dados.
Valida e inicializa a conexão antes de usar o agente.
"""

import logging
import os
import sys
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(project_root / 'logs' / 'agent_setup.log')
    ]
)
logger = logging.getLogger(__name__)


def setup_environment():
    """Configura o ambiente da aplicação."""
    logger.info("=" * 70)
    logger.info("CONFIGURANDO AMBIENTE DO AGENTE")
    logger.info("=" * 70)
    
    # Criar diretório de logs se não existir
    logs_dir = project_root / 'logs'
    logs_dir.mkdir(exist_ok=True)
    logger.info(f"✓ Diretório de logs: {logs_dir}")
    
    # Validar arquivo .env
    env_file = project_root / '.env'
    if not env_file.exists():
        logger.error("✗ Arquivo .env não encontrado!")
        return False
    logger.info(f"✓ Arquivo .env encontrado: {env_file}")
    
    return True


def test_database_connection():
    """Testa a conexão com o banco de dados."""
    logger.info("\n" + "=" * 70)
    logger.info("TESTANDO CONEXÃO COM BANCO DE DADOS")
    logger.info("=" * 70)
    
    try:
        from core.database.database import get_db_manager
        
        db_manager = get_db_manager()
        success, message = db_manager.test_connection()
        
        if success:
            logger.info(message)
            return True
        else:
            logger.error(message)
            return False
            
    except Exception as e:
        logger.error(f"✗ Erro ao testar conexão: {e}", exc_info=True)
        return False


def test_agent_tools():
    """Testa se as ferramentas SQL Server estão disponíveis."""
    logger.info("\n" + "=" * 70)
    logger.info("TESTANDO FERRAMENTAS DO AGENTE")
    logger.info("=" * 70)
    
    try:
        from core.tools.sql_server_tools import sql_server_tools
        
        logger.info(f"Ferramentas disponíveis ({len(sql_server_tools)}):")
        for tool in sql_server_tools:
            logger.info(f"  ✓ {tool.name}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erro ao carregar ferramentas: {e}", exc_info=True)
        return False


def test_agent_initialization():
    """Testa a inicialização do agente."""
    logger.info("\n" + "=" * 70)
    logger.info("TESTANDO INICIALIZAÇÃO DO AGENTE")
    logger.info("=" * 70)
    
    try:
        from core.query_processor import QueryProcessor
        
        logger.info("Inicializando QueryProcessor...")
        processor = QueryProcessor()
        logger.info("✓ QueryProcessor inicializado com sucesso")
        
        return True
        
    except Exception as e:
        logger.error(
            f"✗ Erro ao inicializar QueryProcessor: {e}",
            exc_info=True
        )
        return False


def test_simple_query():
    """Testa uma consulta simples com o agente."""
    logger.info("\n" + "=" * 70)
    logger.info("TESTANDO CONSULTA SIMPLES")
    logger.info("=" * 70)
    
    try:
        from core.query_processor import QueryProcessor
        
        processor = QueryProcessor()
        
        # Teste 1: Pergunta que não requer banco
        logger.info("Teste 1: Pergunta simples (sem banco)...")
        result = processor.process_query("Qual é a data de hoje?")
        logger.info(f"Resultado: {result.get('output', 'N/A')[:100]}...")
        
        # Teste 2: Pergunta que requer banco
        logger.info("\nTeste 2: Pergunta que requer banco...")
        result = processor.process_query(
            "Qual é o estoque do produto com código 12345?"
        )
        logger.info(f"Resultado: {result.get('output', 'N/A')[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Erro ao executar consultas: {e}", exc_info=True)
        return False


def main():
    """Executa toda a sequência de setup e testes."""
    logger.info("\n")
    logger.info("╔" + "═" * 68 + "╗")
    logger.info("║" + " " * 13 + "SETUP E TESTE DO AGENTE BI COM BANCO" + " " * 20 + "║")
    logger.info("╚" + "═" * 68 + "╝")
    
    results = {}
    
    # Executar testes
    results['environment'] = setup_environment()
    if not results['environment']:
        logger.error("✗ Falha na configuração do ambiente")
        return 1
    
    results['database'] = test_database_connection()
    results['tools'] = test_agent_tools()
    results['agent'] = test_agent_initialization()
    # results['query'] = test_simple_query()
    
    # Relatório final
    logger.info("\n" + "=" * 70)
    logger.info("RELATÓRIO FINAL")
    logger.info("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ OK" if result else "✗ FALHOU"
        logger.info(f"{test_name.upper()}: {status}")
    
    logger.info(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        logger.info("\n✓ Agente pronto para usar!")
        logger.info("\nPróximos passos:")
        logger.info("1. Inicie a aplicação Streamlit")
        logger.info("2. Faça perguntas sobre os dados")
        logger.info("3. O agente consultará o banco de dados automaticamente")
        return 0
    else:
        logger.error(f"\n✗ {total - passed} teste(s) falharam")
        logger.error("Revise os erros acima antes de usar o agente")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
