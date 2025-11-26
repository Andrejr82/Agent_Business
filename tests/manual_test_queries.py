import asyncio
import os
import sys

# Adiciona o diretório raiz do projeto ao path para permitir importações de módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.query_processor import QueryProcessor
from core.config.logging_config import setup_logging
import logging

# Configura o logging
setup_logging()
logger = logging.getLogger(__name__)

# Perguntas de teste
TEST_QUERIES = [
    "Liste todas as colunas disponíveis",
    "Qual o preço do produto 719445?",
    "Liste os 5 produtos mais caros da categoria 'BRINQUEDOS'",
    "Qual o estoque total (soma da coluna 'ESTOQUE ATUAL') para a filial Madureira?",
    "Existe o produto com o código '12345'?",
]


async def run_tests():
    """
    Executa uma série de perguntas de teste contra o QueryProcessor.
    """
    logger.info("--- Iniciando Teste Manual do QueryProcessor ---")
    
    try:
        # Instancia o processador de consultas
        # Isso pode falhar se a GEMINI_API_KEY não estiver no ambiente
        query_processor = QueryProcessor()
        logger.info("✓ QueryProcessor inicializado com sucesso.")
    except Exception as e:
        logger.error(f"✗ Falha ao inicializar o QueryProcessor: {e}", exc_info=True)
        logger.error("Verifique se a variável de ambiente 'GEMINI_API_KEY' está configurada corretamente.")
        return

    for i, query in enumerate(TEST_QUERIES):
        logger.info(f"\n--- EXECUTANDO TESTE {i + 1}/{len(TEST_QUERIES)} ---")
        logger.info(f"Pergunta: {query}")
        
        try:
            # Processa a consulta
            response = await asyncio.to_thread(query_processor.process_query, query)
            
            # Exibe a resposta
            logger.info("Resposta do Agente:")
            if isinstance(response, dict) and 'output' in response:
                print(response['output'])
            else:
                print(response)

        except Exception as e:
            logger.error(f"✗ Erro ao processar a pergunta: '{query}'", exc_info=True)
    
    logger.info("\n--- Teste Manual Concluído ---")


if __name__ == "__main__":
    # O Streamlit usa o loop de eventos do asyncio do tornado, que não permite reentrada.
    # Para rodar de forma assíncrona em um script, usamos asyncio.run()
    # No entanto, o LangChain pode ter problemas com isso dependendo da versão.
    # Se `asyncio.run()` falhar, tentamos rodar de forma síncrona.
    try:
        asyncio.run(run_tests())
    except RuntimeError as e:
        if "cannot run loop while another loop is running" in str(e):
            print("Loop de eventos do asyncio já está em execução. Tentando uma abordagem diferente.")
            # Solução alternativa se o loop já estiver rodando (comum em notebooks)
            import nest_asyncio
            nest_asyncio.apply()
            asyncio.run(run_tests())
        else:
            raise
