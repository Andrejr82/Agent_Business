"""
Exportador de usuários SQL Server -> CSV/Parquet.

Uso:
    python scripts/export_users_sql_to_parquet.py --out data/users.parquet

O script tenta, por ordem:
 - usar `DATABASE_URI` (URI SQLAlchemy),
 - ou usar `DB_SERVER`, `DB_PORT`, `DB_DATABASE`,
     `DB_USER`, `DB_PASSWORD`, `DB_DRIVER`.

Query executada (padrão):
    SELECT username, password_hash, role, ativo,
                 tentativas_invalidas, bloqueado_ate, ultimo_login
    FROM usuarios

Segurança:
 - O arquivo deve conter apenas hashes (bcrypt). Nunca senhas em texto.
 - Proteja `data/users.parquet` com permissões de filesystem.

Dependências: pandas, sqlalchemy, pyodbc (ODBC driver no sistema).

Este script é para execução manual pelo mantenedor (não é CI).
"""

import argparse
import os
import sys
from urllib.parse import quote_plus

import pandas as pd


DEFAULT_QUERY = (
    "SELECT username, password_hash, role, ativo, "
    "tentativas_invalidas, bloqueado_ate, ultimo_login FROM usuarios"
)


def build_engine_from_env():
    """Tenta criar uma SQLAlchemy engine a partir de env vars.

    Retorna (engine, used_uri) ou (None, None) se não for possível.
    """
    from sqlalchemy import create_engine

    database_uri = os.getenv("DATABASE_URI")
    if database_uri:
        return create_engine(database_uri), database_uri

    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_DATABASE")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    port = os.getenv("DB_PORT") or "1433"
    driver = os.getenv("DB_DRIVER") or "ODBC Driver 17 for SQL Server"

    if not (server and database and user and password):
        return None, None

    # Constrói a URI compatível com SQLAlchemy + pyodbc
    # Exemplo de URI (SQLAlchemy + pyodbc):
    # mssql+pyodbc://user:pass@server:1433/db?driver=ODBC+Driver+17+for+SQL+Server
    driver_quoted = quote_plus(driver)
    uri = (
        f"mssql+pyodbc://{user}:{quote_plus(password)}@{server}:"
        f"{port}/{database}?driver={driver_quoted}"
    )
    try:
        engine = create_engine(uri)
        return engine, uri
    except Exception:
        return None, uri


def export_users(out_path, csv_path=None, query=DEFAULT_QUERY):
    engine_info = build_engine_from_env()
    if engine_info[0] is None:
        print(
            "Não foi possível construir a engine a partir das variáveis" " de ambiente."
        )
        print(
            "Verifique DATABASE_URI ou DB_SERVER/DB_USER/DB_PASSWORD e DB_DRIVER"
        )
        return 2

    engine = engine_info[0]
    uri = engine_info[1]
    print(f"Conectando usando: {uri}")

    try:
        df = pd.read_sql_query(query, con=engine)
    except Exception as e:
        print("Erro ao executar a query no banco:", e)
        return 3

    if df.empty:
        print("Aviso: query retornou 0 registros. Verifique a tabela 'usuarios'.")

    # Salva CSV intermediário se solicitado
    if csv_path:
        df.to_csv(csv_path, index=False)
        print(f"Exportado CSV em: {csv_path}")

    # Forçar criação do diretório de destino
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    df.to_parquet(out_path, index=False)
    print(f"Exportado Parquet em: {out_path}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Exporta usuários SQL Server para Parquet."
    )
    parser.add_argument(
        "--out",
        required=True,
        help="Caminho de saída para o Parquet (ex: data/users.parquet)",
    )
    parser.add_argument(
        "--csv",
        help="Salvar também CSV intermediário (ex: export.csv)",
    )
    parser.add_argument(
        "--query",
        default=DEFAULT_QUERY,
        help="Query SQL a ser executada",
    )

    args = parser.parse_args()

    code = export_users(args.out, csv_path=args.csv, query=args.query)
    sys.exit(code)


if __name__ == "__main__":
    main()
