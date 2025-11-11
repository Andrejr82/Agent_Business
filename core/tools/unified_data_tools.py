"""
Ferramentas unificadas para acessar dados de qualquer fonte.
Versão corrigida com nomes reais das tabelas e colunas.

Tabelas disponíveis:
- SQL Server: admmatao
- Parquet: ADMAT, ADMAT_REBUILT, master_catalog

Colunas principais (todas em minúsculas no Parquet):
- codigo, nome, categoria, preco_38_percent, est_une, etc.
"""

import logging
from typing import Dict, Any
from langchain_core.tools import tool
from core.data_source_manager import get_data_manager

logger = logging.getLogger(__name__)


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
        
        available = [
            name for name, info in status.items()
            if info['connected']
        ]
        
        logger.info(f"Fontes disponíveis: {available}")
        
        return {
            "status": "success",
            "available_sources": available,
            "sources_detail": status
        }
    except Exception as e:
        logger.error(f"Erro ao listar fontes: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro: {str(e)}"
        }


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
        
        # Tentar em ordem de prioridade
        tabelas = [
            'admmatao', 'ADMAT', 'master_catalog', 'ADMAT_REBUILT',
            'produtos'
        ]
        
        for tabela in tabelas:
            try:
                df = manager.get_data(tabela, limit=limit)
                if not df.empty:
                    logger.info(f"Encontrados {len(df)} produtos em {tabela}")
                    return {
                        "status": "success",
                        "source": tabela,
                        "count": len(df),
                        "columns": list(df.columns),
                        "data": df.to_dict(orient='records')
                    }
            except Exception as e:
                logger.debug(f"Erro ao tentar {tabela}: {e}")
                continue
        
        return {
            "status": "not_found",
            "message": "Nenhuma tabela de produtos encontrada"
        }
    except Exception as e:
        logger.error(f"Erro ao buscar produtos: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro: {str(e)}"
        }


@tool
def buscar_produto(
    codigo: str = None,
    nome: str = None,
    limit: int = 10
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
            column = 'codigo'
            value = codigo
            logger.debug(f"Buscando por código: {codigo}")
        elif nome:
            column = 'nome'
            value = nome
            logger.debug(f"Buscando por nome: {nome}")
        else:
            return {
                "status": "error",
                "message": "Informe código ou nome do produto"
            }
        
        # Tentar em cada tabela
        tabelas = [
            'ADMAT', 'admmatao', 'master_catalog', 'ADMAT_REBUILT',
            'produtos'
        ]
        
        for tabela in tabelas:
            try:
                df = manager.search_data(tabela, column, value, limit=limit)
                if not df.empty:
                    logger.info(
                        f"Encontrados {len(df)} resultado(s) em {tabela}"
                    )
                    return {
                        "status": "success",
                        "source": tabela,
                        "search_column": column,
                        "search_value": value,
                        "count": len(df),
                        "columns": list(df.columns),
                        "data": df.to_dict(orient='records')
                    }
            except Exception as e:
                logger.debug(f"Erro ao buscar em {tabela}: {e}")
                continue
        
        return {
            "status": "not_found",
            "message": f"Produto não encontrado com {column}='{value}'"
        }
    except Exception as e:
        logger.error(f"Erro ao buscar produto: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro: {str(e)}"
        }


@tool
def buscar_por_categoria(
    categoria: str,
    limit: int = 20
) -> Dict[str, Any]:
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
        
        # Tabelas e colunas possíveis para categoria
        tabelas_e_colunas = [
            ('ADMAT', 'categoria'),
            ('ADMAT_REBUILT', 'nome_categoria'),
            ('master_catalog', 'nome_categoria'),
            ('admmatao', 'categoria'),
        ]
        
        for tabela, coluna in tabelas_e_colunas:
            try:
                df = manager.search_data(
                    tabela, coluna, categoria, limit=limit
                )
                if not df.empty:
                    logger.info(
                        f"Encontrados {len(df)} produtos "
                        f"na categoria '{categoria}' em {tabela}"
                    )
                    return {
                        "status": "success",
                        "source": tabela,
                        "column_used": coluna,
                        "category": categoria,
                        "count": len(df),
                        "columns": list(df.columns),
                        "data": df.to_dict(orient='records')
                    }
            except Exception as e:
                logger.debug(
                    f"Erro ao buscar em {tabela} "
                    f"coluna {coluna}: {e}"
                )
                continue
        
        return {
            "status": "not_found",
            "message": f"Nenhum produto encontrado na categoria '{categoria}'"
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar por categoria: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro: {str(e)}"
        }


@tool
def obter_estoque(
    codigo_produto: str = None,
    nome_produto: str = None
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
        f"Consultando estoque: código={codigo_produto}, "
        f"nome={nome_produto}"
    )
    
    try:
        manager = get_data_manager()
        
        # Determinar coluna e valor de busca
        if codigo_produto:
            search_column = 'codigo'
            search_value = codigo_produto
            logger.debug(f"Buscando estoque por código: {codigo_produto}")
        elif nome_produto:
            search_column = 'nome'
            search_value = nome_produto
            logger.debug(f"Buscando estoque por nome: {nome_produto}")
        else:
            return {
                "status": "error",
                "message": "Informe código ou nome do produto"
            }
        
        # Tabelas onde procurar
        tabelas = ['ADMAT', 'admmatao', 'master_catalog', 'ADMAT_REBUILT']
        
        for tabela in tabelas:
            try:
                df = manager.search_data(
                    tabela, search_column, search_value, limit=1
                )
                if not df.empty:
                    logger.info(f"Produto encontrado em {tabela}")
                    
                    # Procurar coluna de estoque possível
                    estoque_columns = [
                        'est_une',
                        'estoque',
                        'EST# UNE',
                        'ESTOQUE',
                        'stock',
                        'STOCK',
                        'quantidade',
                        'QUANTIDADE'
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
                    
                    if estoque_col:
                        return {
                            "status": "success",
                            "source": tabela,
                            "search_by": search_column,
                            "estoque_column": estoque_col,
                            "estoque_value": estoque_valor,
                            "produto": df.iloc[0].to_dict()
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
                                "Produto encontrado mas sem "
                                "informação de estoque"
                            ),
                            "columns_available": list(df.columns),
                            "produto": df.iloc[0].to_dict()
                        }
            except Exception as e:
                logger.debug(f"Erro ao buscar em {tabela}: {e}")
                continue
        
        return {
            "status": "not_found",
            "message": (
                f"Produto não encontrado com "
                f"{search_column}='{search_value}'"
            )
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estoque: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro: {str(e)}"
        }


@tool
def consultar_dados(
    tabela: str,
    limite: int = 100,
    coluna: str = None,  # type: ignore
    valor: str = None  # type: ignore
) -> Dict[str, Any]:
    """
    Consulta genérica de dados em qualquer tabela disponível.
    Útil para queries customizadas.
    
    Args:
        tabela: Nome da tabela (ADMAT, admmatao, master_catalog, etc)
        limite: Limite de registros a retornar
        coluna: Nome da coluna para filtrar (opcional)
        valor: Valor a buscar na coluna (opcional)
        
    Returns:
        Dados consultados com metadados
    """
    logger.info(
        f"Consultando {tabela}: coluna={coluna}, "
        f"valor={valor}, limite={limite}"
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
                "message": f"Nenhum dado encontrado em {tabela}"
            }
        
        logger.info(f"Consulta retornou {len(df)} registros")
        
        return {
            "status": "success",
            "tabela": tabela,
            "filtro_aplicado": (
                f"{coluna}='{valor}'"
                if coluna and valor
                else "nenhum"
            ),
            "total_registros": len(df),
            "colunas": list(df.columns),
            "data": df.to_dict(orient='records')
        }
        
    except Exception as e:
        logger.error(f"Erro ao consultar dados: {e}", exc_info=True)
        return {
            "status": "error",
            "message": f"Erro: {str(e)}"
        }


# Lista de ferramentas unificadas para o agente
unified_tools = [
    listar_dados_disponiveis,
    get_produtos,
    buscar_produto,
    buscar_por_categoria,
    obter_estoque,
    consultar_dados,
]
