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
            except Exception as e:
                print(f"Aviso: Erro ao carregar secrets.toml: {e}")
        
        cls._initialized = True

    @classmethod
    def _get_secret(cls, key: str, default: str = None) -> str:
        """Busca a configuração do st.secrets, secrets.toml ou do ambiente."""
        # Garantir que setup foi chamado
        if not cls._initialized:
            cls.setup()
            
        if IS_STREAMLIT_CLOUD:
            try:
                import streamlit as st
                return st.secrets.get(key, default)
            except Exception:
                pass
        
        # Tentar obter do cache de secrets.toml primeiro
        if key in cls._secrets_cache:
            return str(cls._secrets_cache[key])
            
        # Fallback para variáveis de ambiente
        return os.getenv(key, default)

    # Configurações do banco de dados
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

    # String de conexão para SQLAlchemy, construída dinamicamente
    @classmethod
    @property
    def SQLALCHEMY_DATABASE_URI(cls) -> str:
        """
        Gera a string de conexão do SQLAlchemy a partir das variáveis de ambiente.
        A senha é escapada para garantir que a URL seja válida.
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

    # Modo de demonstração (sem acesso ao banco de dados)
    @classmethod
    @property
    def DEMO_MODE(cls) -> bool:
        return cls._get_secret("DEMO_MODE", "False").lower() == "true"

    # Configurações da aplicação
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

    # Gemini API Key and Model Name
    @classmethod
    @property
    def GEMINI_API_KEY(cls) -> str:
        return cls._get_secret("GEMINI_API_KEY")
    
    @classmethod
    @property
    def GEMINI_MODEL_NAME(cls) -> str:
        return cls._get_secret("GEMINI_MODEL_NAME", "gemini-2.5-flash")

    # LLM Provider Selection
    @classmethod
    @property
    def LLM_PROVIDER(cls) -> str:
        return cls._get_secret("LLM_PROVIDER", "gemini").lower()

    # Configurações de log
    @classmethod
    @property
    def LOG_LEVEL(cls) -> str:
        return cls._get_secret("LOG_LEVEL", "INFO")

    # LangSmith Tracing
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
