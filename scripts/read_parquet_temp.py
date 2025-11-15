import pandas as pd
import os

parquet_file = os.path.join(
    os.path.dirname(__file__), "..", "data", "parquet", "Filial_Madureira.parquet"
)

try:
    df = pd.read_parquet(parquet_file)
    print(df.head().to_string())
except Exception as e:
    print(f"Erro ao ler o arquivo parquet: {e}")
