# core/config/config.py
"""
Classe central de configuração para o projeto.

CORREÇÕES APLICADAS:
1. Suporte a seções aninhadas do secrets.toml (ex: [gemini])
2. Modelo padrão alterado para gemini-1.5-flash
3. Melhor tratamento do st.secrets do Streamlit Cloud
4. Logging para debug de configurações
"""

import os
from typing import Optional
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Determina se está em ambiente Streamlit Cloud
IS_STREAMLIT_CLOUD = os.getenv("IS_STREAMLIT_CLOUD", "false").lower() == "true"


class Config:
    """
    Classe central de configuração para o projeto.
    Carrega variáveis de ambiente de um arquivo .env para desenvolvimento local
    e utiliza st.secrets em produção (Streamlit Cloud).
    """
    
    _initialized = False
    _secrets_cache = {}

    # =========================================================================
    # CORREÇÃO: Mapeamento de chaves para seções aninhadas
    # =========================================================================
    # Formato: "CHAVE_ESPERADA": ("seção", "chave_na_seção")
    _KEY_MAPPING = {
        "GEMINI_API_KEY": [("gemini", "api_key"), ("gemini", "GEMINI_API_KEY")],
        "GEMINI_MODEL_NAME": [("gemini", "model_name"), ("gemini", "GEMINI_MODEL_NAME")],
    }

    @classmethod
    def setup(cls, dotenv_path: Optional[Path] = None):
        """Carrega as variáveis de ambiente a partir de um arquivo .env."""
        if cls._initialized:
            return
            
        if IS_STREAMLIT_CLOUD:
            cls._initialized = True
            return

        if dotenv_path is None:
            dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"

        if dotenv_path.exists():
            load_dotenv(dotenv_path=dotenv_path, override=True)
        else:
            print(
                f"Aviso: Arquivo .env não encontrado em '{dotenv_path}'. "
                "Tentando carregar de secrets.toml..."
            )
        
        # Tentar carregar secrets.toml se existir
        secrets_path = Path(__file__).resolve().parent.parent.parent / ".streamlit" / "secrets.toml"
        if secrets_path.exists():
            try:
                import toml
                cls._secrets_cache = toml.load(secrets_path)
                print(f"✓ Secrets carregados de {secrets_path}")
                # Debug: mostrar estrutura (sem valores sensíveis)
                cls._debug_secrets_structure()
            except Exception as e:
                print(f"Aviso: Erro ao carregar secrets.toml: {e}")
        
        cls._initialized = True

    @classmethod
    def _debug_secrets_structure(cls):
        """Mostra a estrutura do secrets.toml para debug (sem valores sensíveis)."""
        print("  Estrutura do secrets.toml:")
        for key, value in cls._secrets_cache.items():
            if isinstance(value, dict):
                print(f"    [{key}]")
                for subkey in value.keys():
                    # Não mostrar valores de API keys
                    if "key" in subkey.lower() or "password" in subkey.lower():
                        print(f"      {subkey} = ****")
                    else:
                        print(f"      {subkey} = {value[subkey]}")
            else:
                if "key" in key.lower() or "password" in key.lower():
                    print(f"    {key} = ****")
                else:
                    print(f"    {key} = {value}")

    @classmethod
    def _get_from_nested(cls, secrets_dict: dict, key: str) -> Optional[str]:
        """
        Busca uma chave em estrutura aninhada.
        
        Tenta:
        1. Busca direta na raiz
        2. Busca usando o mapeamento de seções
        3. Busca automática em todas as seções
        """
        # 1. Busca direta na raiz
        if key in secrets_dict:
            value = secrets_dict[key]
            if not isinstance(value, dict):
                return str(value)
        
        # 2. Busca usando mapeamento definido
        if key in cls._KEY_MAPPING:
            for section, subkey in cls._KEY_MAPPING[key]:
                if section in secrets_dict and isinstance(secrets_dict[section], dict):
                    if subkey in secrets_dict[section]:
                        return str(secrets_dict[section][subkey])
        
        # 3. Busca automática em seções (para chaves não mapeadas)
        # Ex: DB_SERVER pode estar em [database] como "server" ou "DB_SERVER"
        key_lower = key.lower()
        key_parts = key.lower().split("_")
        
        for section, values in secrets_dict.items():
            if isinstance(values, dict):
                # Busca exata
                if key in values:
                    return str(values[key])
                # Busca case-insensitive
                for k, v in values.items():
                    if k.lower() == key_lower:
                        return str(v)
        
        return None

    @classmethod
    def _get_secret(cls, key: str, default: str = None) -> str:
        """
        Busca a configuração do st.secrets, secrets.toml ou do ambiente.
        
        CORREÇÃO: Agora suporta seções aninhadas como [gemini].
        """
        # Garantir que setup foi chamado
        if not cls._initialized:
            cls.setup()
            
        # =====================================================================
        # CORREÇÃO: Suporte ao Streamlit Cloud com seções aninhadas
        # =====================================================================
        if IS_STREAMLIT_CLOUD:
            try:
                import streamlit as st
                
                # Tentar busca direta primeiro
                if key in st.secrets:
                    return str(st.secrets[key])
                
                # Buscar usando mapeamento
                if key in cls._KEY_MAPPING:
                    for section, subkey in cls._KEY_MAPPING[key]:
                        try:
                            if section in st.secrets:
                                if subkey in st.secrets[section]:
                                    return str(st.secrets[section][subkey])
                        except Exception:
                            pass
                
                # Busca automática em seções
                for section_name in st.secrets:
                    try:
                        section = st.secrets[section_name]
                        if hasattr(section, '__contains__') and key in section:
                            return str(section[key])
                    except Exception:
                        pass
                
                return default
            except Exception as e:
                print(f"Aviso: Erro ao acessar st.secrets: {e}")
        
        # =====================================================================
        # CORREÇÃO: Busca no cache do secrets.toml com suporte a seções
        # =====================================================================
        if cls._secrets_cache:
            result = cls._get_from_nested(cls._secrets_cache, key)
            if result is not None:
                return result
            
        # Fallback para variáveis de ambiente
        env_value = os.getenv(key)
        if env_value is not None:
            return env_value
            
        return default

    # =========================================================================
    # Configurações do banco de dados
    # =========================================================================
    @classmethod
    @property
    def DB_SERVER(cls) -> str:
        return cls._get_secret("DB_SERVER", "localhost")
    
    @classmethod
    @property
    def DB_DATABASE(cls) -> str:
        return cls._get_secret("DB_DATABASE", "nome_do_banco")
    
    @classmethod
    @property
    def DB_USER(cls) -> str:
        return cls._get_secret("DB_USER", "usuario")
    
    @classmethod
    @property
    def DB_PASSWORD(cls) -> str:
        return cls._get_secret("DB_PASSWORD", "senha")
    
    @classmethod
    @property
    def DB_PORT(cls) -> str:
        return cls._get_secret("DB_PORT", "1433")
    
    @classmethod
    @property
    def DB_DRIVER(cls) -> str:
        return cls._get_secret("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    
    @classmethod
    @property
    def DB_TRUST_SERVER_CERTIFICATE(cls) -> str:
        return cls._get_secret("DB_TRUST_SERVER_CERTIFICATE", "yes")
    
    @classmethod
    @property
    def DB_ENCRYPT(cls) -> str:
        return cls._get_secret("DB_ENCRYPT", "no")

    @classmethod
    @property
    def SQLALCHEMY_DATABASE_URI(cls) -> str:
        """
        Gera a string de conexão do SQLAlchemy a partir das variáveis de ambiente.
        """
        password_quoted = quote_plus(cls.DB_PASSWORD) if cls.DB_PASSWORD else ""
        driver_quoted = quote_plus(cls.DB_DRIVER)

        uri = (
            f"mssql+pyodbc://{cls.DB_USER}:{password_quoted}@{cls.DB_SERVER}:{cls.DB_PORT}/{cls.DB_DATABASE}?"
            f"driver={driver_quoted}&TrustServerCertificate={cls.DB_TRUST_SERVER_CERTIFICATE}"
            + (
                f"&Encrypt={cls.DB_ENCRYPT}"
                if cls.DB_ENCRYPT.lower() == "yes"
                else ""
            )
        )
        return uri

    # =========================================================================
    # Modo de demonstração
    # =========================================================================
    @classmethod
    @property
    def DEMO_MODE(cls) -> bool:
        return cls._get_secret("DEMO_MODE", "False").lower() == "true"

    # =========================================================================
    # Configurações da aplicação
    # =========================================================================
    @classmethod
    @property
    def DEBUG(cls) -> bool:
        return cls._get_secret("DEBUG", "False").lower() == "true"
    
    @classmethod
    @property
    def SECRET_KEY(cls) -> str:
        return cls._get_secret("SECRET_KEY", "chave_secreta_padrao")
    
    @classmethod
    @property
    def SESSION_COOKIE_PATH(cls) -> str:
        return "/"

    # =========================================================================
    # CORREÇÃO: Gemini API Key and Model Name
    # Modelo padrão alterado para gemini-1.5-flash-latest (mais estável)
    # =========================================================================
    @classmethod
    @property
    def GEMINI_API_KEY(cls) -> str:
        return cls._get_secret("GEMINI_API_KEY")
    
    @classmethod
    @property
    def GEMINI_MODEL_NAME(cls) -> str:
        # CORREÇÃO: Modelo padrão alterado de gemini-2.5-flash-lite para gemini-2.0-flash
        return cls._get_secret("GEMINI_MODEL_NAME", "gemini-2.0-flash")

    # =========================================================================
    # LLM Provider Selection
    # =========================================================================
    @classmethod
    @property
    def LLM_PROVIDER(cls) -> str:
        return cls._get_secret("LLM_PROVIDER", "gemini").lower()

    # =========================================================================
    # Configurações de log
    # =========================================================================
    @classmethod
    @property
    def LOG_LEVEL(cls) -> str:
        return cls._get_secret("LOG_LEVEL", "INFO")

    # =========================================================================
    # LangSmith Tracing
    # =========================================================================
    @classmethod
    @property
    def LANGCHAIN_TRACING_V2(cls) -> bool:
        return cls._get_secret("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    
    @classmethod
    @property
    def LANGCHAIN_API_KEY(cls) -> str:
        return cls._get_secret("LANGCHAIN_API_KEY")
    
    @classmethod
    @property
    def LANGCHAIN_PROJECT(cls) -> str:
        return cls._get_secret("LANGCHAIN_PROJECT", "caculinha-bi-project")


# Carrega a configuração na importação do módulo
Config.setup()
