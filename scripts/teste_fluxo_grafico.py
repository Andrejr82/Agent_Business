#!/usr/bin/env python
"""Script teste do fluxo de gráficos. Simula requisição de gráfico."""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.query_processor import QueryProcessor

# Setup logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    print("\n" + "=" * 80)
    print("🧪 TESTE COMPLETO DO FLUXO DE GRÁFICOS")
    print("=" * 80 + "\n")

    # Teste 1: Inicializar QueryProcessor
    print("📍 PASSO 1: Inicializar QueryProcessor")
    print("-" * 80)
    try:
        processor = QueryProcessor()
        print("✅ QueryProcessor inicializado com sucesso\n")
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}\n")
        return

    # Teste 2: Processar query de gráfico
    print("📍 PASSO 2: Processar query de gráfico")
    print("-" * 80)
    query = "gere um gráfico de vendas do produto 59294"
    print(f"Query: '{query}'")
    print()

    try:
        response = processor.process_query(query)
        print("✅ Query processada com sucesso")
        print(f"   Type: {response['type']}")
        print(f"   Output type: {type(response['output'])}")
        print(f"   Output: {str(response['output'])[:100]}...")
        print()
    except Exception as e:
        print(f"❌ Erro ao processar query: {e}\n")
        import traceback

        traceback.print_exc()
        return

    # Teste 3: Verificar se é gráfico
    print("📍 PASSO 3: Verificar tipo de resposta")
    print("-" * 80)
    if response["type"] == "chart":
        print("✅ Tipo de resposta é 'chart'")
        print(
            f"   Output é uma figura Plotly: {hasattr(response['output'], 'to_json')}"
        )
        print()
    else:
        print(f"⚠️  Tipo de resposta é '{response['type']}' (esperado: 'chart')")
        print(f"   Output: {response['output']}")
        print()

    # Teste 4: Tentar converter para JSON (simulando renderização)
    print("📍 PASSO 4: Simular renderização Streamlit")
    print("-" * 80)
    try:
        if response["type"] == "chart":
            output = response["output"]
            if hasattr(output, "to_json"):
                json_str = output.to_json()
                print("✅ Figura Plotly convertida para JSON")
                print(f"   JSON length: {len(json_str)} caracteres")
                print(f"   Primeiros 200 chars: {json_str[:200]}...")
            else:
                print("⚠️  Output não tem método 'to_json'")
                print(f"   Type: {type(output)}")
                print(f"   Valor: {str(output)[:200]}...")
        else:
            print(f"⚠️  Não é gráfico, tipo: {response['type']}")
        print()
    except Exception as e:
        print(f"❌ Erro ao converter para JSON: {e}\n")
        import traceback

        traceback.print_exc()

    # Teste 5: Verificar dados de vendas
    print("📍 PASSO 5: Verificar dados de vendas do produto")
    print("-" * 80)
    try:
        import pandas as pd

        df = pd.read_parquet("data/parquet_cleaned/ADMAT_REBUILT.parquet")
        produto_59294 = df[df["codigo_produto"] == 59294]
        print(f"✅ Dados carregados: {len(df)} linhas totais")
        print(f"   Registros para produto 59294: {len(produto_59294)}")
        print(f"   Colunas: {list(df.columns)[:10]}...")

        # Verificar colunas de mês
        mes_cols = [c for c in df.columns if c.startswith("mes_")]
        print(f"   Colunas de mês: {mes_cols}")
        print()
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}\n")

    print("=" * 80)
    print("🎯 TESTE CONCLUÍDO")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
