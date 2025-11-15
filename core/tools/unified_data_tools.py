"""
Ferramentas unificadas para acessar dados de qualquer fonte.
Versão corrigida com nomes reais das tabelas e colunas.
"""

import logging
from typing import Dict, Any
import pandas as pd
from langchain_core.tools import tool
from core.data_source_manager import get_data_manager

logger = logging.getLogger(__name__)


def _truncate_df_for_llm(df: pd.DataFrame, max_rows: int = 10) -> Dict[str, Any]:
    """Trunca o DataFrame e prepara a resposta para o LLM."""
    if len(df) > max_rows:
        return {
            "data": df.head(max_rows).to_dict(orient="records"),
            "message": f"Mostrando as primeiras {max_rows} de {len(df)} linhas. Seja mais específico se precisar de mais detalhes.",
        }
    return {"data": df.to_dict(orient="records")}


@tool
def listar_dados_disponiveis() -> Dict[str, Any]:
    """
    Lista todas as fontes de dados disponíveis e seu status.

    Returns:
        Status de todas as fontes de dados (SQL Server, Parquet, JSON)
    """
    logger.info("Listando fontes de dados disponíveis")

    try:
        manager = get_data_manager()
        status = manager.get_status()

        available = [name for name, info in status.items() if info["connected"]]

        logger.info(f"Fontes disponíveis: {available}")

        return {
            "status": "success",
            "available_sources": available,
            "sources_detail": status,
        }
    except Exception as e:
        logger.error(f"Erro ao listar fontes: {e}", exc_info=True)
        return {"status": "error", "message": f"Erro: {str(e)}"}


@tool
def get_produtos(limit: int = 100) -> Dict[str, Any]:
    """
    Busca produtos de qualquer fonte disponível.
    Tenta SQL Server primeiro, depois Parquet, depois JSON.

    Args:
        limit: Número máximo de produtos a retornar

    Returns:
        Lista de produtos com metadados de origem
    """
    logger.info(f"Buscando {limit} produtos")

    try:
        manager = get_data_manager()

        tabelas = ["Admat_OPCOM"]

        for tabela in tabelas:
            try:
                df = manager.get_data(tabela, limit=limit)
                if not df.empty:
                    logger.info(f"Encontrados {len(df)} produtos em {tabela}")
                    response_data = _truncate_df_for_llm(df)
                    return {
                        "status": "success",
                        "source": tabela,
                        "count": len(df),
                        "columns": list(df.columns),
                        **response_data,
                    }
            except Exception as e:
                logger.debug(f"Erro ao tentar {tabela}: {e}")
                continue

        return {
            "status": "not_found",
            "message": "Nenhuma tabela de produtos encontrada",
        }
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}", exc_info=True)
        return {"status": "error", "message": f"Erro: {str(e)}"}


@tool
def buscar_produto(
    codigo: str = None, nome: str = None, limit: int = 10
) -> Dict[str, Any]:
    """
    Busca um produto específico por código ou nome.

    Args:
        codigo: Código do produto (busca em coluna 'codigo')
        nome: Nome do produto (busca em coluna 'nome')
        limit: Número máximo de resultados

    Returns:
        Dados do(s) produto(s) encontrado(s)
    """
    logger.info(f"Buscando produto: código={codigo}, nome={nome}")

    try:
        manager = get_data_manager()

        if codigo:
            column = "codigo"
            value = codigo
            logger.debug(f"Buscando por código: {codigo}")
        elif nome:
            column = "nome"
            value = nome
            logger.debug(f"Buscando por nome: {nome}")
        else:
            return {"status": "error", "message": "Informe código ou nome do produto"}

        tabelas = ["Admat_OPCOM"]

        for tabela in tabelas:
            try:
                df = manager.search_data(tabela, column, value, limit=limit)
                if not df.empty:
                    logger.info(f"Encontrados {len(df)} resultado(s) em {tabela}")
                    response_data = _truncate_df_for_llm(df)
                    return {
                        "status": "success",
                        "source": tabela,
                        "search_column": column,
                        "search_value": value,
                        "count": len(df),
                        "columns": list(df.columns),
                        **response_data,
                    }
            except Exception as e:
                logger.debug(f"Erro ao buscar em {tabela}: {e}")
                continue

        return {
            "status": "not_found",
            "message": f"Produto não encontrado com {column}='{value}'",
        }
    except Exception as e:
        logger.error(f"Erro ao buscar produto: {e}", exc_info=True)
        return {"status": "error", "message": f"Erro: {str(e)}"}


@tool
def buscar_por_categoria(categoria: str, limit: int = 20) -> Dict[str, Any]:
    """
    Busca produtos por categoria.
    Tenta procurar em colunas: 'categoria', 'nome_categoria',
    'categoria_produto'

    Args:
        categoria: Nome ou parte do nome da categoria
        limit: Número máximo de produtos a retornar

    Returns:
        Produtos da categoria especificada
    """
    logger.info(f"Buscando produtos na categoria: {categoria}")

    try:
        manager = get_data_manager()

        tabelas_e_colunas = [
            ("Admat_OPCOM", "categoria"),
        ]

        for tabela, coluna in tabelas_e_colunas:
            try:
                df = manager.search_data(tabela, coluna, categoria, limit=limit)
                if not df.empty:
                    logger.info(
                        f"Encontrados {len(df)} produtos "
                        f"na categoria '{categoria}' em {tabela}"
                    )
                    response_data = _truncate_df_for_llm(df)
                    return {
                        "status": "success",
                        "source": tabela,
                        "column_used": coluna,
                        "category": categoria,
                        "count": len(df),
                        "columns": list(df.columns),
                        **response_data,
                    }
            except Exception as e:
                logger.debug(f"Erro ao buscar em {tabela} " f"coluna {coluna}: {e}")
                continue

        return {
            "status": "not_found",
            "message": f"Nenhum produto encontrado na categoria '{categoria}'",
        }

    except Exception as e:
        logger.error(f"Erro ao buscar por categoria: {e}", exc_info=True)
        return {"status": "error", "message": f"Erro: {str(e)}"}


@tool
def obter_estoque(
    codigo_produto: str = None, nome_produto: str = None
) -> Dict[str, Any]:
    """
    Obtém informações de estoque de um produto.

    Args:
        codigo_produto: Código do produto
        nome_produto: Nome do produto

    Returns:
        Dados de estoque do produto
    """
    logger.info(
        f"Consultando estoque: código={codigo_produto}, " f"nome={nome_produto}"
    )

    try:
        manager = get_data_manager()

        if codigo_produto:
            search_column = "codigo"
            search_value = codigo_produto
            logger.debug(f"Buscando estoque por código: {codigo_produto}")
        elif nome_produto:
            search_column = "nome"
            search_value = nome_produto
            logger.debug(f"Buscando estoque por nome: {nome_produto}")
        else:
            return {"status": "error", "message": "Informe código ou nome do produto"}

        tabelas = ["Admat_OPCOM"]

        for tabela in tabelas:
            try:
                df = manager.search_data(tabela, search_column, search_value, limit=1)
                if not df.empty:
                    logger.info(f"Produto encontrado em {tabela}")

                    estoque_columns = [
                        "est_une",
                        "estoque",
                        "EST# UNE",
                        "ESTOQUE",
                        "stock",
                        "STOCK",
                        "quantidade",
                        "QUANTIDADE",
                    ]

                    estoque_col = None
                    estoque_valor = None

                    for col in estoque_columns:
                        if col in df.columns:
                            estoque_col = col
                            estoque_valor = df[col].iloc[0]
                            logger.debug(
                                f"Encontrada coluna de estoque: "
                                f"{col} = {estoque_valor}"
                            )
                            break

                    produto_info = _truncate_df_for_llm(df, max_rows=1)
                    if estoque_col:
                        return {
                            "status": "success",
                            "source": tabela,
                            "search_by": search_column,
                            "estoque_column": estoque_col,
                            "estoque_value": estoque_valor,
                            "produto": produto_info.get("data", [{}])[0],
                        }
                    else:
                        logger.warning(
                            f"Produto encontrado mas sem coluna "
                            f"de estoque em {tabela}"
                        )
                        return {
                            "status": "success",
                            "source": tabela,
                            "message": (
                                "Produto encontrado mas sem " "informação de estoque"
                            ),
                            "columns_available": list(df.columns),
                            "produto": produto_info.get("data", [{}])[0],
                        }
            except Exception as e:
                logger.debug(f"Erro ao buscar em {tabela}: {e}")
                continue

        return {
            "status": "not_found",
            "message": (
                f"Produto não encontrado com " f"{search_column}='{search_value}'"
            ),
        }

    except Exception as e:
        logger.error(f"Erro ao obter estoque: {e}", exc_info=True)
        return {"status": "error", "message": f"Erro: {str(e)}"}


@tool
def consultar_dados(
    tabela: str,
    limite: int = 100,
    coluna: str = None,  # type: ignore
    valor: str = None,  # type: ignore
    coluna_retorno: str = None, # Novo parâmetro para a coluna a ser retornada
) -> Dict[str, Any]:
    """
    Consulta genérica de dados na tabela 'Filial_Madureira'.
    Esta tabela contém informações detalhadas sobre produtos, vendas, custos e lucros.

    Colunas disponíveis na tabela 'Filial_Madureira':
    - 'ITEM' (int): Número identificador do item/produto.
    - 'CODIGO' (str): Código de barras ou identificador único do produto.
    - 'DESCRIÇÃO' (str): Descrição detalhada do produto.
    - 'QTD' (int): Quantidade atual em estoque.
    - 'VENDA R$' (float): Valor total de venda em Reais.
    - 'DESC. R$' (float): Valor de desconto em Reais.
    - 'CUSTO R$' (float): Custo total em Reais.
    - 'LUCRO R$' (float): Lucro total em Reais.
    - 'LUCRO TOTAL %' (float): Lucro total em porcentagem.
    - 'CUSTO UNIT R$' (float): Custo unitário em Reais.
    - 'VENDA UNIT R$' (float): Valor de venda unitário em Reais.
    - 'LUCRO UNIT %' (float): Lucro unitário em porcentagem.
    - 'SALDO' (int): Saldo de estoque.
    - 'VENDA QTD JAN' (int): Quantidade vendida em Janeiro.
    - 'VENDA QTD FEV' (int): Quantidade vendida em Fevereiro.
    - 'VENDA QTD MAR' (int): Quantidade vendida em Março.
    - 'VENDA QTD ABR' (int): Quantidade vendida em Abril.
    - 'VENDA QTD MAI' (int): Quantidade vendida em Maio.
    - 'VENDA QTD JUN' (int): Quantidade vendida em Junho.
    - 'VENDA QTD JUL' (int): Quantidade vendida em Julho.
    - 'VENDA QTD AGO' (int): Quantidade vendida em Agosto.
    - 'VENDA QTD SET' (int): Quantidade vendida em Setembro.
    - 'VENDA QTD OUT' (int): Quantidade vendida em Outubro.
    - 'VENDA QTD NOV' (int): Quantidade vendida em Novembro.
    - 'VENDA QTD DEZ' (int): Quantidade vendida em Dezembro.
    - 'VLR ESTOQUE VENDA' (float): Valor do estoque para venda.
    - 'VLR ESTOQUE CUSTO' (float): Valor do estoque ao custo.
    - 'FABRICANTE' (str): Nome do fabricante do produto.
    - 'DT CADASTRO' (datetime): Data de cadastro do produto.
    - 'DT ULTIMA COMPRA' (datetime): Data da última compra do produto.
    - 'GRUPO' (str): Grupo ou categoria do produto.
    - 'QTD ULTIMA COMPRA' (int): Quantidade da última compra.

    Args:
        tabela: Nome da tabela (atualmente apenas 'Filial_Madureira' é suportada para esta ferramenta).
        limite: Limite de registros a retornar.
        coluna: Nome da coluna para filtrar (opcional).
        valor: Valor a buscar na coluna (opcional).
        coluna_retorno: Nome da coluna cujo valor deve ser retornado para o primeiro registro encontrado (opcional).
                        Pode ser a mesma coluna usada para filtrar (`coluna`).

    Returns:
        Dados consultados com metadados. Se `coluna_retorno` for especificado, retorna apenas o valor dessa coluna.

    Exemplo de uso:
    - Para obter o 'CODIGO' do item com 'ITEM' igual a 1:
      `consultar_dados(tabela='Filial_Madureira', coluna='ITEM', valor='1', coluna_retorno='CODIGO')`
    - Para obter o 'ITEM' do item com 'ITEM' igual a 1 (coluna de filtro e retorno são as mesmas):
      `consultar_dados(tabela='Filial_Madureira', coluna='ITEM', valor='1', coluna_retorno='ITEM')`
    """
    logger.info(
        f"Consultando {tabela}: coluna={coluna}, "
        f"valor={valor}, limite={limite}, coluna_retorno={coluna_retorno}"
    )

    try:
        manager = get_data_manager()

        if coluna and valor:
            logger.debug(f"Executando busca com filtro: {coluna}='{valor}'")
            df = manager.search_data(tabela, coluna, valor, limit=limite)
        else:
            logger.debug(f"Executando busca sem filtro, limite={limite}")
            df = manager.get_data(tabela, limit=limite)

        if df.empty:
            return {
                "status": "not_found",
                "message": f"Nenhum dado encontrado em {tabela}",
            }

        # Se coluna_retorno for especificado e existir no DataFrame, retorna o valor
        if coluna_retorno and coluna_retorno in df.columns:
            return {
                "status": "success",
                "tabela": tabela,
                "filtro_aplicado": (
                    f"{coluna}='{valor}'" if coluna and valor else "nenhum"
                ),
                "coluna_retornada": coluna_retorno,
                "valor_retornado": df[coluna_retorno].iloc[0],
            }
        # Se coluna_retorno não for especificado, ou não existir, retorna o DataFrame completo (truncado)
        else:
            logger.info(f"Consulta retornou {len(df)} registros")
            response_data = _truncate_df_for_llm(df)
            return {
                "status": "success",
                "tabela": tabela,
                "filtro_aplicado": (
                    f"{coluna}='{valor}'" if coluna and valor else "nenhum"
                ),
                "total_registros": len(df),
                "colunas": list(df.columns),
                **response_data,
            }

    except Exception as e:
        logger.error(f"Erro ao consultar dados: {e}", exc_info=True)
        return {"status": "error", "message": f"Erro: {str(e)}"}


# Lista de ferramentas unificadas para o agente
unified_tools = [
    listar_dados_disponiveis,
    get_produtos,
    buscar_produto,
    buscar_por_categoria,
    obter_estoque,
    consultar_dados,
]
