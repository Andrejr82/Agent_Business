"""
Script de teste para verificar se o agente está respondendo corretamente.
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.query_processor import QueryProcessor
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_agent():
    """Testa o agente com uma query simples."""
    print("=" * 80)
    print("TESTE DO AGENTE BI")
    print("=" * 80)
    
    try:
        # Inicializar o QueryProcessor
        print("\n1. Inicializando QueryProcessor...")
        processor = QueryProcessor()
        print("✓ QueryProcessor inicializado com sucesso!")
        
        # Testar uma query simples
        query = "qual é o lucro do item 9"
        print(f"\n2. Testando query: '{query}'")
        print("-" * 80)
        
        result = processor.process_query(query)
        
        print("\n3. Resultado:")
        print("-" * 80)
        print(f"Tipo: {result.get('type')}")
        print(f"Output: {result.get('output')}")
        print("-" * 80)
        
        if result.get('type') == 'text' and result.get('output'):
            print("\n✓ TESTE PASSOU: Agente respondeu com sucesso!")
        else:
            print("\n✗ TESTE FALHOU: Resposta vazia ou inválida")
            
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent()
