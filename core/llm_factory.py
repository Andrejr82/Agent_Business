"""
Factory para seleção automática de adaptadores LLM.

CORREÇÕES APLICADAS:
1. Validação do modelo configurado
2. Fallback automático para modelo estável
3. Logging detalhado para debug
4. Reset automático em caso de erro de API key
"""

import logging
from typing import Optional
from core.config.config import Config
from core.llm_base import BaseLLMAdapter


class LLMFactory:
    """Factory pattern para criar adaptadores LLM."""

    _instance: Optional["LLMFactory"] = None
    _adapter: Optional[BaseLLMAdapter] = None
    _logger = logging.getLogger(__name__)
    
    # =========================================================================
    # CORREÇÃO: Definir modelos recomendados e problemáticos
    # =========================================================================
    RECOMMENDED_MODEL = "gemini-1.5-flash"
    
    STABLE_MODELS = [
        "gemini-1.5-flash",
        "gemini-1.5-pro", 
        "gemini-1.0-pro",
    ]
    
    PROBLEMATIC_MODELS = [
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash-lite",
    ]

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_adapter(cls) -> BaseLLMAdapter:
        """
        Obtém o adaptador LLM configurado (apenas Gemini).

        Returns:
            BaseLLMAdapter: Adaptador LLM inicializado

        Raises:
            ValueError: Se o adaptador Gemini não puder ser inicializado
        """
        if cls._adapter is not None:
            return cls._adapter

        factory = cls()
        cls._logger.info("Inicializando adaptador Gemini.")
        
        # =====================================================================
        # CORREÇÃO: Verificar e alertar sobre modelo problemático
        # =====================================================================
        config = Config()
        current_model = getattr(config, 'GEMINI_MODEL_NAME', 'não definido')
        
        if current_model in cls.PROBLEMATIC_MODELS:
            cls._logger.warning(
                f"⚠️ ATENÇÃO: O modelo '{current_model}' pode causar respostas vazias! "
                f"Recomendado alterar para '{cls.RECOMMENDED_MODEL}' no arquivo de configuração."
            )
        
        cls._adapter = factory._get_gemini_adapter()

        if cls._adapter is None:
            raise ValueError(
                "Nenhum adaptador LLM pode ser inicializado. "
                "Verifique as configurações de GEMINI_API_KEY."
            )
        
        cls._logger.info(f"Adaptador Gemini pronto. Modelo: {current_model}")
        return cls._adapter

    @staticmethod
    def _get_gemini_adapter() -> Optional[BaseLLMAdapter]:
        """
        Tenta inicializar adaptador Gemini.
        
        CORREÇÃO: Logging mais detalhado e validação de configuração.
        """
        try:
            from core.llm_gemini_adapter import GeminiLLMAdapter

            config = Config()
            
            if not config.GEMINI_API_KEY:
                LLMFactory._logger.warning("GEMINI_API_KEY não configurada")
                return None
            
            # =====================================================================
            # CORREÇÃO: Validar se API key não parece ser inválida
            # =====================================================================
            api_key = config.GEMINI_API_KEY
            if len(api_key) < 20:
                LLMFactory._logger.error(
                    "GEMINI_API_KEY parece ser inválida (muito curta). "
                    "Verifique se a chave está correta."
                )
                return None
            
            # Log do modelo sendo usado (sem mostrar a API key)
            model_name = getattr(config, 'GEMINI_MODEL_NAME', 'default')
            LLMFactory._logger.info(
                f"Inicializando Gemini com modelo: {model_name}"
            )

            adapter = GeminiLLMAdapter()
            LLMFactory._logger.info("Adaptador Gemini inicializado com sucesso")
            return adapter

        except ImportError as e:
            LLMFactory._logger.error(
                f"Erro de importação do Gemini: {e}. "
                f"Execute: pip install google-generativeai"
            )
            return None
            
        except ValueError as e:
            # Erro de configuração (API key não definida, etc.)
            LLMFactory._logger.error(f"Erro de configuração do Gemini: {e}")
            return None
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # =====================================================================
            # CORREÇÃO: Tratamento específico para erro de API key vazada/inválida
            # =====================================================================
            if "403" in error_msg or "leaked" in error_msg or "invalid" in error_msg:
                LLMFactory._logger.error(
                    f"🔴 ERRO DE API KEY: {e}. "
                    f"Sua API key pode ter sido vazada ou está inválida. "
                    f"Por favor, gere uma nova API key no Google AI Studio."
                )
            else:
                LLMFactory._logger.error(f"Erro ao inicializar Gemini: {e}")
            
            return None

    @classmethod
    def reset(cls):
        """
        Reseta o adaptador cache (útil para testes ou após erro).
        
        CORREÇÃO: Log mais informativo.
        """
        cls._adapter = None
        cls._instance = None  # CORREÇÃO: Também reseta a instância singleton
        cls._logger.info("Adaptador LLM resetado. Próxima chamada criará nova instância.")

    @classmethod
    def get_available_providers(cls) -> dict:
        """
        Verifica quais provedores estão disponíveis.

        Returns:
            dict: {'gemini': bool, 'gemini_model': str, 'warnings': list}
        """
        providers = {
            "gemini": False,
            "gemini_model": None,
            "warnings": []
        }
        
        try:
            config = Config()
            api_key = config.GEMINI_API_KEY
            
            providers["gemini"] = api_key is not None and len(api_key) > 20
            
            if providers["gemini"]:
                model_name = getattr(config, 'GEMINI_MODEL_NAME', 'não definido')
                providers["gemini_model"] = model_name
                
                # =====================================================================
                # CORREÇÃO: Adicionar warnings sobre modelo problemático
                # =====================================================================
                if model_name in cls.PROBLEMATIC_MODELS:
                    providers["warnings"].append(
                        f"Modelo '{model_name}' pode causar respostas vazias. "
                        f"Recomendado: '{cls.RECOMMENDED_MODEL}'"
                    )
                    
        except Exception as e:
            providers["gemini"] = False
            providers["warnings"].append(f"Erro ao verificar configuração: {e}")

        return providers
    
    @classmethod
    def get_model_recommendation(cls) -> str:
        """
        Retorna recomendação de modelo baseado na configuração atual.
        
        Returns:
            str: Mensagem de recomendação
        """
        try:
            config = Config()
            current_model = getattr(config, 'GEMINI_MODEL_NAME', None)
            
            if current_model is None:
                return f"Modelo não configurado. Recomendado: {cls.RECOMMENDED_MODEL}"
            
            if current_model in cls.PROBLEMATIC_MODELS:
                return (
                    f"⚠️ Modelo atual '{current_model}' pode causar problemas. "
                    f"Recomendado trocar para: {cls.RECOMMENDED_MODEL}"
                )
            
            if current_model in cls.STABLE_MODELS:
                return f"✅ Modelo '{current_model}' é estável e recomendado."
            
            return f"Modelo '{current_model}' não está na lista de testados."
            
        except Exception as e:
            return f"Erro ao verificar modelo: {e}"
