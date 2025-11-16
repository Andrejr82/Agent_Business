"""
Diagnóstico completo - Identificar problemas reais
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

print("=" * 80)
print("DIAGNÓSTICO 1: Testar Parquet Diretamente")
print("=" * 80)

import pandas as pd
from pathlib import Path

parquet_dir = Path("data/parquet_cleaned")
print(f"\nArquivos Parquet em {parquet_dir}:")

for file in parquet_dir.glob("*.parquet"):
    df = pd.read_parquet(file)
    print(f"\n📄 {file.name}")
    print(f"   Registros: {len(df)}")
    print(f"   Colunas: {len(df.columns)}")
    print(f"   Colunas principais: {list(df.columns[:10])}")

print("\n" + "=" * 80)
print("DIAGNÓSTICO 2: Testar SQL Server - Listar Tabelas")
print("=" * 80)

from core.database.database import get_db_manager
from sqlalchemy import inspect

try:
    db = get_db_manager()
    success, msg = db.test_connection()
    print(f"Conexão: {msg}")

    if success:
        # Listar tabelas
        with db.get_connection() as conn:
            inspector = inspect(conn)
            schemas = inspector.get_schema_names()
            print(f"\nSchemas disponíveis: {schemas}")

            for schema in schemas:
                tables = inspector.get_table_names(schema=schema)
                if tables:
                    print(f"\nTabelas em schema '{schema}':")
                    for table in tables[:10]:  # Primeiras 10
                        print(f"  - {table}")
                    if len(tables) > 10:
                        print(f"  ... e mais {len(tables) - 10}")
except Exception as e:
    print(f"Erro ao listar tabelas: {e}")

print("\n" + "=" * 80)
print("DIAGNÓSTICO 3: Testar Colunas do Parquet")
print("=" * 80)

# Verificar colunas exatas do ADMAT
admat_file = parquet_dir / "ADMAT.parquet"
df = pd.read_parquet(admat_file)

print(f"\nColunas do {admat_file.name}:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:3d}. {col}")

print("\nPrimeira linha de dados:")
print(df.iloc[0:1].T)

print("\n" + "=" * 80)
print("DIAGNÓSTICO 4: Testar Query com Nomes Corretos")
print("=" * 80)

# Agora testar buscar no Parquet com nomes corretos
print("\nBuscando produtos com 'PARAFUSO':")
if "nome" in df.columns:
    mask = df["nome"].astype(str).str.contains("PARAFUSO", case=False, na=False)
    resultado = df[mask][["codigo", "nome", "categoria", "preco_38_percent"]].head(3)
    print(f"Encontrados: {len(df[mask])}")
    print(resultado)
else:
    print("Coluna 'nome' não encontrada!")
    print(f"Colunas disponíveis: {[c for c in df.columns if 'nom' in c.lower()]}")

print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO COMPLETO")
print("=" * 80)
