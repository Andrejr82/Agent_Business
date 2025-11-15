"""
Script de teste para validar configuração de Gemini e LLM Factory.
Execute: python scripts/test_llm_setup.py
"""

import sys
import logging
from pathlib import Path
import pytest

# Adicionar raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def config_instance():
    """Fixture para carregar a configuração uma vez por módulo."""
    print("\n" + "=" * 60)
    print("🔍 TESTANDO CONFIGURAÇÕES")
    print("=" * 60 + "\n")

    from core.config.config import Config

    config = Config()

    print(f"📦 LLM_PROVIDER: {config.LLM_PROVIDER}")
    print(
        f"📦 GEMINI_API_KEY: {'✅ Configurada' if config.GEMINI_API_KEY else '❌ Não configurada'}"
    )
    print(f"📦 GEMINI_MODEL_NAME: {config.GEMINI_MODEL_NAME}")

    return config


def test_config_pytest(config_instance):
    """Testa a configuração usando o fixture."""
    assert config_instance is not None
    assert config_instance.LLM_PROVIDER == "gemini"
    assert config_instance.GEMINI_API_KEY is not None


@pytest.fixture(scope="module")


def llm_factory_adapter(config_instance):


    """Fixture para testar o LLM Factory e retornar o adaptador."""


    print("\n" + "=" * 60)


    print("🔧 TESTANDO LLM FACTORY")


    print("=" * 60 + "\n")





    from core.llm_factory import LLMFactory





    # Verificar provedores disponíveis


    providers = LLMFactory.get_available_providers()


    print("📋 Provedores disponíveis:")


    for provider, available in providers.items():


        status = "✅" if available else "❌"


        print(f"  {status} {provider}")





    # Tentar obter adaptador


    try:


        adapter = LLMFactory.get_adapter()


        adapter_name = type(adapter).__name__


        print(f"\n✅ Adaptador LLM: {adapter_name}")


        return adapter


    except Exception as e:


        print(f"\n❌ Erro ao obter adaptador: {e}")


        return None








def test_factory_pytest(llm_factory_adapter):


    """Testa o LLM Factory usando o fixture."""


    assert llm_factory_adapter is not None


    from core.llm_gemini_adapter import GeminiLLMAdapter


    assert isinstance(llm_factory_adapter, GeminiLLMAdapter)








@pytest.fixture(scope="module")


def gemini_adapter_instance(config_instance):


    """Fixture para testar o adaptador Gemini especificamente."""


    print("\n" + "=" * 60)


    print("🌐 TESTANDO ADAPTADOR GEMINI")


    print("=" * 60 + "\n")





    if not config_instance.GEMINI_API_KEY:


        pytest.skip("GEMINI_API_KEY não configurada. Pulando este teste.")





    try:


        from core.llm_gemini_adapter import GeminiLLMAdapter





        adapter = GeminiLLMAdapter()


        print("✅ GeminiLLMAdapter inicializado com sucesso")


        return adapter


    except Exception as e:


        print(f"❌ Erro ao inicializar GeminiLLMAdapter: {e}")


        return None








def test_gemini_adapter_pytest(gemini_adapter_instance):


    """Testa o adaptador Gemini usando o fixture."""


    assert gemini_adapter_instance is not None


    from core.llm_gemini_adapter import GeminiLLMAdapter


    assert isinstance(gemini_adapter_instance, GeminiLLMAdapter)








def test_completion_pytest(gemini_adapter_instance):


    """Testa uma chamada de completion simples usando o fixture."""


    if gemini_adapter_instance is None:


        pytest.skip("Adaptador Gemini não disponível para teste de completion.")





    print("\n" + "=" * 60)


    print("💬 TESTANDO COMPLETION")


    print("=" * 60 + "\n")





    messages = [


        {"role": "user", "content": "Responda com uma única palavra: Funciona?"}


    ]





    print(f"📨 Mensagem: {messages[0]['content']}")


    print("\n⏳ Aguardando resposta...")





    try:


        response = gemini_adapter_instance.get_completion(messages)





        if "error" in response:


            print(f"❌ Erro: {response['error']}")


            assert False, f"Erro na completion: {response['error']}"





        content = response.get("content", "")


        print(f"✅ Resposta: {content}\n")


        assert content is not None and len(content) > 0


    except Exception as e:


        print(f"❌ Erro ao obter completion: {e}")


        assert False, f"Exceção durante a completion: {e}"








if __name__ == "__main__":


    print("Este script é primariamente para execução via pytest.")


    print("Para executar os testes, use: pytest scripts/test_llm_setup.py")

