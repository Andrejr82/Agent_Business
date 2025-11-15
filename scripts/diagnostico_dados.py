"""
Script de diagnóstico para verificar acesso aos dados e estrutura.
Ajuda a identificar por que os gráficos não estão sendo gerados.
"""

import logging
from core.data_source_manager import get_data_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def diagnosticar_dados():
    """Executa diagnóstico completo dos dados."""

    print("\n" + "=" * 80)
    print("DIAGNÓSTICO DE ACESSO AOS DADOS")
    print("=" * 80 + "\n")

    try:
        manager = get_data_manager()
        print("✅ DataSourceManager inicializado")
    except Exception as e:
        print(f"❌ Erro ao inicializar DataSourceManager: {e}")
        return

    # Testar diferentes tabelas
    tabelas_teste = ["ADMAT_REBUILT", "admmatao", "ADMAT", "master_catalog"]

    for tabela in tabelas_teste:
        print(f"\n--- Testando tabela: {tabela} ---")
        try:
            df = manager.get_data(tabela, limit=10)

            if df.empty:
                print("  ⚠️  Tabela vazia ou não encontrada")
                continue

            print(f"  ✅ Dados carregados: {df.shape[0]} linhas, {df.shape[1]} colunas")

            # Verificar colunas importantes
            print(f"  Colunas: {list(df.columns[:15])}")

            # Procurar colunas de mês
            mes_cols = [c for c in df.columns if c.lower().startswith("mes_")]
            if mes_cols:
                print(f"  ✅ Colunas de mês encontradas: {len(mes_cols)}")
                print(f"    Exemplos: {mes_cols[:5]}")
            else:
                print("  ⚠️  Nenhuma coluna de mês encontrada")

            # Procurar produto 59294
            codigo_cols = [c for c in df.columns if "codigo" in c.lower()]
            if codigo_cols:
                col = codigo_cols[0]
                produto_59294 = df[df[col] == 59294]
                if not produto_59294.empty:
                    print(
                        f"  ✅ Produto 59294 encontrado: {len(produto_59294)} registros"
                    )

                    # Mostrar dados do produto
                    print("    Primeiras colunas do produto:")
                    for col_info in df.columns[:10]:
                        valor = produto_59294[col_info].iloc[0]
                        print(f"      - {col_info}: {valor}")

                    # Mostrar vendas mensais se disponível
                    if mes_cols:
                        print("    Vendas mensais:")
                        for mes_col in mes_cols[:6]:
                            valor = produto_59294[mes_col].iloc[0]
                            print(f"      - {mes_col}: {valor}")
                else:
                    print("  ⚠️  Produto 59294 não encontrado nessa tabela")

        except Exception as e:
            print(f"  ❌ Erro ao acessar: {e}")

    # Teste específico da ferramenta
    print("\n" + "=" * 80)
    print("TESTE DA FERRAMENTA gerar_grafico_vendas_mensais_produto")
    print("=" * 80 + "\n")

    try:
        from core.tools.chart_tools import gerar_grafico_vendas_mensais_produto

        resultado = gerar_grafico_vendas_mensais_produto.invoke(
            {"codigo_produto": 59294, "unidade_filtro": ""}
        )

        if resultado.get("status") == "success":
            print("✅ Ferramenta executada com sucesso!")
            print(f"   Tipo de gráfico: {resultado.get('chart_type')}")
            print("   Resumo:")
            for key, value in resultado.get("summary", {}).items():
                if not isinstance(value, dict):
                    print(f"     - {key}: {value}")
        else:
            print(f"❌ Erro na ferramenta: {resultado.get('message')}")

    except Exception as e:
        print(f"❌ Erro ao executar ferramenta: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 80)
    print("FIM DO DIAGNÓSTICO")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    diagnosticar_dados()
