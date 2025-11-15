import os
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Cache para armazenar DataFrames carregados
_df_cache = {}


def get_table_df(table_name, filters=None, parquet_dir="data/parquet"):
    """Carrega Filial_Madureira.parquet com cache."""
    main_file_name = "Filial_Madureira.parquet"
    file_path = os.path.join(parquet_dir, main_file_name)

    # Verifica cache
    if file_path in _df_cache:
        logger.info("Carregando DataFrame do cache.")
        df = _df_cache[file_path].copy()
    else:
        logger.info(f"Tentando ler: {file_path}")
        if not os.path.exists(file_path):
            logger.error(f"Arquivo não encontrado: {file_path}")
            return None
        try:
            df = pd.read_parquet(file_path)
            _df_cache[file_path] = df.copy()
            logger.info(f"Arquivo lido. {len(df)} linhas.")
        except Exception as e:
            logger.error(f"Erro ao ler Parquet: {e}")
            return None

    if filters:
        for col, val in filters.items():
            if col in df.columns:
                df = df[df[col] == val]
        logger.info(f"Filtros aplicados. {len(df)} linhas.")

    return df


def prepare_chart_data(df, x_col, y_col, chart_type="bar", title=None):
    """Prepara dados para gráfico."""
    if df is None or x_col not in df.columns or y_col not in df.columns:
        return {
            "data": [],
            "layout": {"title": title or "Gráfico"},
            "error": (f"Colunas {x_col} ou {y_col} não encontradas."),
        }
    try:
        data = [
            {
                "x": df[x_col].tolist(),
                "y": df[y_col].tolist(),
                "type": chart_type,
                "name": y_col,
            }
        ]
        layout = {"title": title or f"{y_col} por {x_col}"}
        return {"data": data, "layout": layout}
    except Exception as e:
        logger.error(f"Erro ao preparar dados do gráfico: {e}")
        return {"data": [], "layout": {"title": title or "Gráfico"}, "error": str(e)}
