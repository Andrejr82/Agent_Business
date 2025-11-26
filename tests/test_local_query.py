"""
Teste local do QueryProcessor
Simula consulta completa do usuário
"""
import sys
import logging
from core.query_processor import QueryProcessor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_query():
    """Testa consulta ao sistema"""
    try:
        print("="*80)
        print("TESTE LOCAL DO AGENTE BI - QUERY PROCESSOR")
        print("="*80)

        # Inicializar QueryProcessor
        print("\n1. Inicializando QueryProcessor...")
        processor = QueryProcessor()
        print("   ✓ QueryProcessor inicializado")

        # Teste 1: Lucro do produto 1
        print("\n2. Testando consulta: 'qual é o lucro do produto 1'")
        query1 = "qual é o lucro do produto 1"
        result1 = processor.process_query(query1)
        print(f"\n   Tipo de resposta: {result1.get('type')}")
        print(f"   Resposta: {result1.get('output')[:200] if isinstance(result1.get('output'), str) else result1.get('output')}")

        # Teste 2: Top 10 mais vendidos
        print("\n3. Testando consulta: 'gere um ranking dos 10 mais vendidos'")
        query2 = "gere um ranking dos 10 mais vendidos"
        result2 = processor.process_query(query2)
        print(f"\n   Tipo de resposta: {result2.get('type')}")
        if result2.get('type') == 'chart':
            print("   ✓ Gráfico gerado com sucesso!")
            print(f"   Tamanho do JSON: {len(result2.get('output')) if isinstance(result2.get('output'), str) else 'N/A'} caracteres")
        else:
            print(f"   Resposta: {result2.get('output')[:200] if isinstance(result2.get('output'), str) else result2.get('output')}")

        print("\n" + "="*80)
        print("✓ TESTE CONCLUÍDO COM SUCESSO!")
        print("="*80)

    except Exception as e:
        print(f"\n✗ ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    success = test_query()
    sys.exit(0 if success else 1)
