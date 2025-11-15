import sys
import logging
from pathlib import Path
import pandas as pd
import pytest
import re # Importar o módulo re para expressões regulares

# Adiciona o diretório raiz do projeto ao sys.path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from core.data_source_manager import get_data_manager
from core.query_processor import QueryProcessor

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Caminho para o arquivo Parquet da Filial Madureira
FILIAL_MADUREIRA_PARQUET_PATH = project_root / "data" / "parquet" / "Filial_Madureira.parquet"

@pytest.fixture(scope="module")
def data_manager():
    """Fixture para inicializar o DataSourceManager."""
    logger.info("Inicializando DataSourceManager para testes da Filial Madureira.")
    manager = get_data_manager()
    return manager

@pytest.fixture(scope="module")
def query_processor():
    """Fixture para inicializar o QueryProcessor."""
    logger.info("Inicializando QueryProcessor para testes da Filial Madureira.")
    return QueryProcessor()

def test_filial_madureira_parquet_exists_and_readable():
    """Verifica se o arquivo Filial_Madureira.parquet existe e pode ser lido."""
    logger.info(f"Verificando existência e legibilidade de: {FILIAL_MADUREIRA_PARQUET_PATH}")
    assert FILIAL_MADUREIRA_PARQUET_PATH.exists(), f"Arquivo não encontrado: {FILIAL_MADUREIRA_PARQUET_PATH}"
    
    try:
        df = pd.read_parquet(FILIAL_MADUREIRA_PARQUET_PATH)
        assert not df.empty, "O arquivo Parquet da Filial Madureira está vazio."
        logger.info(f"Arquivo {FILIAL_MADUREIRA_PARQUET_PATH.name} lido com sucesso. {len(df)} registros.")
    except Exception as e:
        pytest.fail(f"Não foi possível ler o arquivo Parquet da Filial Madureira: {e}")

def test_data_source_manager_detects_filial_madureira(data_manager):
    """Verifica se o DataSourceManager detecta a Filial Madureira como fonte de dados."""
    logger.info("Verificando se DataSourceManager detecta Filial Madureira.")
    available_sources = data_manager.get_available_sources()
    logger.info(f"Fontes disponíveis detectadas: {available_sources}")
    assert any("filial_madureira" in source.lower() for source in available_sources), \
        "DataSourceManager não detectou 'Filial_Madureira.parquet' como fonte."

def test_query_processor_can_query_all_columns_from_filial_madureira(query_processor):
    """
    Testa se o QueryProcessor consegue consultar todas as colunas da Filial Madureira
    de forma genérica.
    """
    logger.info("Testando QueryProcessor com todas as colunas da Filial Madureira.")
    
    # Obter as colunas do arquivo Parquet
    df = pd.read_parquet(FILIAL_MADUREIRA_PARQUET_PATH)
    df_columns = df.columns.tolist()
    
    # Excluir colunas que não fazem sentido para uma consulta direta de valor (ex: descrições longas, datas)
    # ou que seriam melhor consultadas com ferramentas específicas (se existissem)
    excluded_columns = ["DESCRIÇÃO", "DT CADASTRO", "DT ULTIMA COMPRA"] 
    test_columns = [col for col in df_columns if col not in excluded_columns]

    # Pegar o primeiro ITEM válido para usar como filtro
    first_item_value = df["ITEM"].iloc[0] if "ITEM" in df.columns and not df.empty else None
    if first_item_value is None:
        pytest.skip("Não foi possível encontrar um valor 'ITEM' para usar como filtro.")

    for column in test_columns:
        # Para cada coluna, tentar fazer uma pergunta genérica usando filtro por outra coluna
        # Usamos 'ITEM' como coluna de filtro para buscar um registro específico
        query = (
            f"Qual é o valor da coluna '{column}' para o item com 'ITEM' igual a "
            f"'{first_item_value}' na Filial Madureira."
        )
        logger.info(f"Processando consulta para coluna '{column}': '{query}'")
        response = query_processor.process_query(query)
        logger.info(f"Resposta do agente para '{column}': {response}")
        
        assert isinstance(response, dict), f"A resposta do agente para '{column}' não é um dicionário."
        assert "output" in response, f"A resposta do agente para '{column}' não contém a chave 'output'."
        assert "erro" not in response["output"].lower(), f"A consulta para '{column}' retornou um erro: {response['output']}"
        assert len(response["output"]) > 0, f"A resposta do agente para '{column}' está vazia."
        
        # Obter o valor esperado diretamente do DataFrame
        expected_value = df[df["ITEM"] == first_item_value][column].iloc[0]
        
        # Normalizar o valor esperado e a saída do agente para comparação
        normalized_expected_value = str(expected_value).strip('"').strip("'").lower()
        normalized_response_output = response["output"].lower()

        logger.info(f"Coluna: {column}, Expected Value: {expected_value} (Type: {type(expected_value)}), Normalized Expected: {normalized_expected_value}")
        logger.info(f"Normalized Response Output: {normalized_response_output}")

        # Lidar com a comparação de floats
        if isinstance(expected_value, (float, pd.Float64Dtype)):
            if pd.isna(expected_value): # Verifica se o valor esperado é NaN
                assert "nan" in normalized_response_output or "não disponível" in normalized_response_output or "<na>" in normalized_response_output or "desconhecido" in normalized_response_output, \
                    f"A resposta para '{column}' não contém 'nan', 'não disponível', '<NA>' ou 'desconhecido' para o valor esperado '{expected_value}'. Resposta: {response['output']}"
            else:
                try:
                    # Usar regex para extrair o último número de ponto flutuante da string
                    # Procura por um número que pode ter casas decimais, no final da string ou antes de um ponto final
                    logger.info(f"Normalized Response Output for float comparison: {normalized_response_output}")
                    match = re.findall(r"(-?\d+\.?\d*)", normalized_response_output)
                    logger.info(f"Regex matches: {match}")
                    if match:
                        response_float = float(match[-1]) # Pega o último número encontrado
                        # Comparar floats com uma pequena tolerância
                        assert abs(float(normalized_expected_value) - response_float) < 0.01, \
                            f"A resposta para '{column}' ({response_float}) não corresponde ao valor esperado '{expected_value}' com tolerância. Resposta: {response['output']}"
                    else:
                        # Se não encontrar float na resposta, volta para a comparação de string
                        assert normalized_expected_value in normalized_response_output, \
                            f"A resposta para '{column}' não contém o valor esperado '{expected_value}'. Resposta: {response['output']}"
                except ValueError:
                    # Se houver erro na conversão para float, volta para a comparação de string
                    assert normalized_expected_value in normalized_response_output, \
                        f"A resposta para '{column}' não contém o valor esperado '{expected_value}'. Resposta: {response['output']}"
        else:
            # Para outros tipos, a asserção agora verifica se o valor esperado (normalizado) está presente na resposta (normalizada)
            assert normalized_expected_value in normalized_response_output, \
                f"A resposta para '{column}' não contém o valor esperado '{expected_value}'. Resposta: {response['output']}"
    logger.info("Todos os testes de consulta genérica por coluna foram executados.")