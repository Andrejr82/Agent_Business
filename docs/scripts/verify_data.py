import pandas as pd

df = pd.read_parquet("data/parquet/Filial_Madureira.parquet")

print("=== VERIFICAÇÃO DE DADOS ===")
print(f"Total de produtos: {len(df)}")
print("\nColunas disponíveis:")
for i, col in enumerate(df.columns):
    print(f"  {i}: {col}")

# Buscar produto 1
produto_1 = df[df["ITEM"] == 1.0]
if not produto_1.empty:
    print("\nPRODUTO 1 ENCONTRADO!")
    print(f'  Item: {produto_1["ITEM"].values[0]}')
    print(f'  Código: {produto_1["CODIGO"].values[0]}')
    print(f'  Descrição: {produto_1["DESCRIÇÃO"].values[0]}')
    lucro_col = "LUCRO R$"
    if lucro_col in df.columns:
        print(f"  Lucro Total: {produto_1[lucro_col].values[0]}")
    print(f'  Lucro Unit %: {produto_1["LUCRO UNIT %"].values[0]}')
    print(f'  Venda Unit R$: {produto_1["VENDA UNIT R$"].values[0]}')
    print(f'  Custo Unit R$: {produto_1["CUSTO UNIT R$"].values[0]}')
else:
    print("\n✗ Produto 1 não encontrado")

print("\n=== PRIMEIROS 3 PRODUTOS ===")
print(df[["ITEM", "CODIGO", "DESCRIÇÃO"]].head(3))
