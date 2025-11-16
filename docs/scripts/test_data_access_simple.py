"""
Script de teste simplificado para verificar acesso aos dados.
Execute: python test_data_access_simple.py
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_data_loading():
    """Testa carregamento direto dos dados."""
    print("\n" + "="*60)
    print("TESTE 1: Carregamento Direto de Dados")
    print("="*60)
    
    try:
        import pandas as pd
        
        parquet_path = "data/parquet/Filial_Madureira.parquet"
        
        if not os.path.exists(parquet_path):
            print(f"❌ ERRO: Arquivo não encontrado: {parquet_path}")
            return False
        
        df = pd.read_parquet(parquet_path)
        
        print(f"✓ Arquivo carregado com sucesso!")
        print(f"  - Total de registros: {len(df)}")
        print(f"  - Total de colunas: {len(df.columns)}")
        print(f"\n📋 Todas as colunas disponíveis:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col:30s} ({df[col].dtype})")
        
        print(f"\n📊 Primeiro registro de exemplo:")
        primeiro = df.iloc[0]
        for col in df.columns[:10]:  # Mostrar apenas primeiras 10 colunas
            valor = primeiro[col]
            print(f"  {col:20s}: {valor}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao carregar dados: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tools_direct():
    """Testa as ferramentas diretamente sem imports complexos."""
    print("\n" + "="*60)
    print("TESTE 2: Ferramentas - Teste Direto")
    print("="*60)
    
    try:
        # Testar carregamento direto do módulo
        import importlib.util
        
        # Caminho para o arquivo de ferramentas
        tools_path = os.path.join("core", "tools", "unified_data_tools.py")
        
        if not os.path.exists(tools_path):
            print(f"❌ Arquivo não encontrado: {tools_path}")
            return False
        
        # Carregar módulo diretamente
        spec = importlib.util.spec_from_file_location("unified_tools", tools_path)
        unified_tools_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(unified_tools_module)
        
        print("✓ Módulo unified_data_tools carregado com sucesso!")
        
        # Verificar se as funções existem
        required_functions = [
            'listar_colunas_disponiveis',
            'consultar_dados',
            'buscar_produto',
            'obter_estoque'
        ]
        
        print("\n🔍 Verificando funções exportadas:")
        for func_name in required_functions:
            if hasattr(unified_tools_module, func_name):
                print(f"  ✓ {func_name}")
            else:
                print(f"  ❌ {func_name} - NÃO ENCONTRADA")
                return False
        
        # Testar listar_colunas_disponiveis diretamente
        print("\n🧪 Testando listar_colunas_disponiveis()...")
        listar_func = unified_tools_module.listar_colunas_disponiveis
        
        # Invocar a ferramenta
        result = listar_func.invoke({})
        
        if result.get("status") == "success":
            print(f"  ✓ Sucesso!")
            print(f"    - Total de colunas: {result['total_colunas']}")
            print(f"    - Total de registros: {result['total_registros']}")
            print(f"\n  📋 Primeiras 5 colunas:")
            for col in result['colunas'][:5]:
                print(f"    * {col['nome']:20s} ({col['tipo']})")
        else:
            print(f"  ❌ Erro: {result.get('message')}")
            return False
        
        # Testar consultar_dados
        print("\n🧪 Testando consultar_dados()...")
        consultar_func = unified_tools_module.consultar_dados
        
        result = consultar_func.invoke({
            "coluna": "ITEM",
            "valor": "1",
            "limite": 1
        })
        
        if result.get("status") == "success":
            print(f"  ✓ Consulta bem-sucedida!")
            print(f"    - Registros: {result.get('total_records', 0)}")
            if result.get('data'):
                print(f"    - Primeiro registro encontrado")
        else:
            print(f"  ⚠️ Status: {result.get('status')}")
            print(f"    - Mensagem: {result.get('message')}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao testar ferramentas: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_processor():
    """Testa o QueryProcessor que é usado pelo Streamlit."""
    print("\n" + "="*60)
    print("TESTE 3: QueryProcessor (usado pelo Streamlit)")
    print("="*60)
    
    try:
        from core.query_processor import QueryProcessor
        
        print("✓ QueryProcessor importado com sucesso!")
        
        print("\n🤖 Inicializando QueryProcessor...")
        processor = QueryProcessor()
        print("  ✓ QueryProcessor inicializado!")
        
        print("\n🧪 Testando query simples...")
        query = "Liste as colunas disponíveis"
        print(f"  Query: '{query}'")
        
        response = processor.process_query(query)
        
        print(f"\n📤 Resposta:")
        print(f"  - Tipo: {response.get('type')}")
        
        output = response.get('output', '')
        if isinstance(output, str):
            # Truncar output longo
            output_preview = output[:300] + "..." if len(output) > 300 else output
            print(f"  - Output: {output_preview}")
        else:
            print(f"  - Output: {type(output)}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO ao testar QueryProcessor: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes."""
    print("\n" + "="*60)
    print("🧪 TESTE DE ACESSO AOS DADOS - Caçulinha BI")
    print("   Versão Simplificada - Sem Dependências Complexas")
    print("="*60)
    
    results = {
        "1. Carregamento de Dados": test_data_loading(),
        "2. Ferramentas Unificadas": test_tools_direct(),
        "3. QueryProcessor": test_query_processor(),
    }
    
    print("\n" + "="*60)
    print("📊 RESUMO DOS TESTES")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓ PASSOU" if result else "❌ FALHOU"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("\n💡 Próximos passos:")
        print("  1. Execute: streamlit run streamlit_app.py")
        print("  2. Faça perguntas como:")
        print("     - 'Liste as colunas disponíveis'")
        print("     - 'Qual o produto com código 7896205901654?'")
        print("     - 'Mostre produtos do grupo ESMALTES'")
        print("     - 'Qual o estoque do item 1?'")
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM")
        print("  Verifique os erros acima.")
        print("\n🔧 Ações corretivas:")
        print("  1. Verifique se o arquivo data/parquet/Filial_Madureira.parquet existe")
        print("  2. Substitua o arquivo core/tools/unified_data_tools.py pelo código fornecido")
        print("  3. Substitua o arquivo core/agents/supervisor_agent.py pelo código fornecido")
    
    print("="*60 + "\n")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)