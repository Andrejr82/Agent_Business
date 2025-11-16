import pandas as pd
import os

# Ler com header na linha 2 (depois de metadados)
df = pd.read_excel("Filial_Madureira.xlsx", header=0)

print(f"Shape original: {df.shape}")
print(f"Colunas: {list(df.columns)[:10]}...")

# Remover linhas com NaN completas
df = df.dropna(how="all")
df = df.reset_index(drop=True)

print(f"Shape após limpeza: {df.shape}")
print("Primeiros registros:")
print(df.head(10))

# Converter tipos - preencher NaN e converter para string
df = df.fillna("")
df = df.astype(str)

# Salvar como parquet
output_path = "data/parquet/Filial_Madureira.parquet"
os.makedirs("data/parquet", exist_ok=True)
df.to_parquet(output_path, index=False, compression="snappy")

print(f"\n✓ Arquivo salvo: {output_path}")
print(f"Tamanho: {os.path.getsize(output_path) / 1024:.2f} KB")
print(f"Registros: {len(df)}")
print(f"Colunas: {len(df.columns)}")
print("\nColunas disponíveis:")
for i, col in enumerate(df.columns):
    print(f"  {i+1}. {col}")
