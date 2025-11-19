import os
import os
from typing import Optional
from pathlib import Path
from urllib.parse import quote_plus
import streamlit as st
from dotenv import load_dotenv

# Determina se está em ambiente Streamlit Cloud
IS_STREAMLIT_CLOUD = os.getenv("IS_STREAMLIT_CLOUD", "false").lower() == "true"

class Config:
    """
    Classe central de configuração para o projeto.
    Carrega variáveis de ambiente de um arquivo .env para desenvolvimento local
    e utiliza st.secrets em produção (Streamlit Cloud).
    """

    @classmethod
    def setup(cls, dotenv_path: Optional[Path] = None):
        """Carrega as variáveis de ambiente a partir de um arquivo .env."""
        if IS_STREAMLIT_CLOUD:
            return

        if dotenv_path is None:
            dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"

        if dotenv_path.exists():
            load_dotenv(dotenv_path=dotenv_path, override=True)
        else:
            print(
                f"Aviso: Arquivo .env não encontrado em '{dotenv_path}'. As configurações dependerão das variáveis de ambiente do sistema."
            )

    @staticmethod
    def _get_secret(key: str, default: str = None) -> str:
        """Busca a configuração do st.secrets ou do ambiente."""
        if IS_STREAMLIT_CLOUD:
            return st.secrets.get(key, default)
        return os.getenv(key, default)

    # O restante da classe permanece o mesmo...
    # Configurações do banco de dados
    DB_SERVER = _get_secret("DB_SERVER", "localhost")
    DB_DATABASE = _get_secret("DB_DATABASE", "nome_do_banco")
    DB_USER = _get_secret("DB_USER", "usuario")
    DB_PASSWORD = _get_secret("DB_PASSWORD", "senha")
    DB_PORT = _get_secret("DB_PORT", "1433")
    DB_DRIVER = _get_secret("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    DB_TRUST_SERVER_CERTIFICATE = _get_secret("DB_TRUST_SERVER_CERTIFICATE", "yes")
    DB_ENCRYPT = _get_secret("DB_ENCRYPT", "no")


    # String de conexão para SQLAlchemy, construída dinamicamente
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """
        Gera a string de conexão do SQLAlchemy a partir das variáveis de ambiente.
        A senha é escapada para garantir que a URL seja válida.
        """
        password_quoted = quote_plus(self.DB_PASSWORD) if self.DB_PASSWORD else ""
        driver_quoted = quote_plus(self.DB_DRIVER)

        uri = (
            f"mssql+pyodbc://{self.DB_USER}:{password_quoted}@{self.DB_SERVER}:{self.DB_PORT}/{self.DB_DATABASE}?"
            f"driver={driver_quoted}&TrustServerCertificate={self.DB_TRUST_SERVER_CERTIFICATE}"
            + (
                f"&Encrypt={self.DB_ENCRYPT}"
                if self.DB_ENCRYPT.lower() == "yes"
                else ""
            )
        )
        return uri

    # Modo de demonstração (sem acesso ao banco de dados)
    DEMO_MODE = _get_secret("DEMO_MODE", "False").lower() == "true"

    # Configurações da aplicação
    DEBUG = _get_secret("DEBUG", "False").lower() == "true"
    SECRET_KEY = _get_secret("SECRET_KEY", "chave_secreta_padrao")
    SESSION_COOKIE_PATH = "/"

    # Gemini API Key and Model Name
    GEMINI_API_KEY = _get_secret("GEMINI_API_KEY")
    GEMINI_MODEL_NAME = _get_secret("GEMINI_MODEL_NAME", "gemini-2.0-flash-lite")

    # LLM Provider Selection
    LLM_PROVIDER = _get_secret("LLM_PROVIDER", "gemini").lower()

    # Configurações de log
    LOG_LEVEL = _get_secret("LOG_LEVEL", "INFO")

    # LangSmith Tracing
    LANGCHAIN_TRACING_V2 = _get_secret("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_API_KEY = _get_secret("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT = _get_secret("LANGCHAIN_PROJECT", "caculinha-bi-project")

# Carrega a configuração na importação do módulo
Config.setup()
