import sys
from pathlib import Path
import logging

# Adiciona o diretório raiz do projeto ao sys.path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from core.query_processor import QueryProcessor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def test_user_query_fabricante_formatted():
    query_processor = QueryProcessor()
    user_query = "qual fabricante do item 9"
    
    logger.info(f"Processando a pergunta do usuário: '{user_query}'")
    response = query_processor.process_query(user_query)
    
    logger.info(f"Resposta do agente: {response}")
    
    # Verificar se a resposta está formatada como esperado
    expected_output_part = "o valor da coluna 'fabricante' para o item com item='9' é 'não disponível'."
    assert "output" in response
    assert expected_output_part in response["output"].lower()

if __name__ == "__main__":
    test_user_query_fabricante_formatted()
