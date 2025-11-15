from pathlib import Path
import pandas as pd

"""
Teste simples para garantir que existem arquivos Parquet disponíveis.
Este projeto agora usa apenas arquivos Parquet como fonte de dados.
"""

base_dir = Path(__file__).resolve().parent.parent / "data" / "parquet_cleaned"
parquet_files = list(base_dir.glob("*.parquet")) if base_dir.exists() else []

if parquet_files:
    print(f"Arquivos Parquet encontrados: {len(parquet_files)}")
    # ler um arquivo rapidamente
    try:
        df = pd.read_parquet(parquet_files[0])
        print(f"Leitura de Parquet com sucesso: {parquet_files[0].name} -> {df.shape}")
    except Exception as e:
        print(f"Erro ao ler Parquet: {e}")
else:
    print(f"Nenhum arquivo Parquet encontrado em: {base_dir}")
