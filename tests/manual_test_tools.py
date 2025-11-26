"""
Script de teste rápido das ferramentas
"""

from core.tools.unified_data_tools import buscar_produto, obter_estoque, get_produtos

print("=" * 70)
print("TESTE 1: Buscar Produtos por Nome (PARAFUSO)")
print("=" * 70)
result = buscar_produto.invoke({"nome": "PARAFUSO", "limit": 3})
print(f"Status: {result['status']}")
print(f"Encontrados: {result.get('count', 0)}")
print(f"Fonte: {result.get('source', 'N/A')}")
if result.get("data"):
    print(f"Primeiro produto: {result['data'][0].get('nome', 'N/A')}")

print("\n" + "=" * 70)
print("TESTE 2: Buscar 10 Produtos")
print("=" * 70)
result2 = get_produtos.invoke({"limit": 10})
print(f"Status: {result2['status']}")
print(f"Total encontrado: {result2.get('count', 0)}")
print(f"Fonte: {result2.get('source', 'N/A')}")

print("\n" + "=" * 70)
print("TESTE 3: Buscar Estoque")
print("=" * 70)
result3 = obter_estoque.invoke({"nome_produto": "PARAFUSO"})
print(f"Status: {result3['status']}")
if result3["status"] == "success":
    print(f"Estoque encontrado: {result3.get('estoque', 'N/A')}")

print("\n✅ TODOS OS TESTES COMPLETADOS")
