#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fábrica de Componentes

Este módulo implementa o padrão Factory para criar e gerenciar instâncias
dos diversos componentes do sistema, facilitando a integração entre eles
e reduzindo o acoplamento.
"""

import logging
from functools import wraps  # Movido para o nível do módulo
from typing import Any, Dict, Optional

# Importa outros componentes conforme necessário
try:
    from core.mcp.context7_adapter import Context7MCPAdapter
    from core.mcp.sqlserver_adapter import SQLServerMCPAdapter

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

try:
    from core.agents.product_agent import ProductAgent

    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

try:
    from core.web.server import WebServer
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class ComponentFactory:
    """Fábrica para criar e gerenciar componentes do sistema"""

    # Dicionário para armazenar as instâncias dos componentes (Singleton)
    _components: Dict[str, Any] = {}

    # Logger
    logger = logging.getLogger("ComponentFactory")

    @classmethod
    def get_mcp_adapter(cls, adapter_type: str = "sqlserver") -> Optional[Any]:
        """Obtém uma instância do adaptador MCP

        Args:
            adapter_type (str, optional): Tipo de adaptador MCP. Defaults to 'sqlserver'.

        Returns:
            Optional[Any]: Instância do adaptador MCP ou None se não disponível
        """
        if not MCP_AVAILABLE:
            cls.logger.warning("Componentes MCP não estão disponíveis")
            return None

        adapter_key = f"mcp_{adapter_type}"

        if adapter_key not in cls._components:
            cls.logger.info(f"Criando nova instância do adaptador MCP: {adapter_type}")

            if adapter_type == "sqlserver":
                cls._components[adapter_key] = SQLServerMCPAdapter()
            elif adapter_type == "context7":
                cls._components[adapter_key] = Context7MCPAdapter()
            else:
                cls.logger.error(f"Tipo de adaptador MCP desconhecido: {adapter_type}")
                return None

        return cls._components[adapter_key]

    @classmethod
    def get_product_agent(cls) -> Optional[Any]:
        """Obtém uma instância do agente de produtos

        Returns:
            Optional[Any]: Instância do agente de produtos ou None se não disponível
        """
        if not AGENTS_AVAILABLE:
            cls.logger.warning("Componentes de agentes não estão disponíveis")
            return None

        if "product_agent" not in cls._components:
            cls.logger.info("Criando nova instância do agente de produtos")
            cls._components["product_agent"] = ProductAgent()

        return cls._components["product_agent"]

    @classmethod
    def reset_component(cls, component_name: str) -> bool:
        """Reinicia um componente específico, removendo sua instância atual

        Args:
            component_name (str): Nome do componente a ser reiniciado

        Returns:
            bool: True se o componente foi reiniciado com sucesso, False caso contrário
        """
        if component_name in cls._components:
            del cls._components[component_name]
            cls.logger.info(f"Componente reiniciado: {component_name}")
            return True

        cls.logger.warning(
            f"Tentativa de reiniciar componente inexistente: {component_name}"
        )
        return False

    @classmethod
    def reset_all(cls) -> None:
        """Reinicia todos os componentes, removendo todas as instâncias atuais"""
        cls._components.clear()
        cls.logger.info("Todos os componentes foram reiniciados")

    @classmethod
    def get_web_server(cls) -> Optional[Any]:
        """Obtém uma instância do servidor web (Flask)"""
        if not FLASK_AVAILABLE:
            cls.logger.error(
                "Flask não está disponível. Instale com 'pip install flask'."
            )
            return None
        if "web_server" not in cls._components:
            from core.config.config_central import ConfiguracaoCentral

            config = ConfiguracaoCentral()
            host = config.web_config.get("host", "127.0.0.1")
            port = config.web_config.get("port", 5000)
            cls.logger.info(f"Criando nova instância do WebServer na porta {port}")
            cls._components["web_server"] = WebServer(host=host, port=port)
        return cls._components["web_server"]


# Exemplo de uso
if __name__ == "__main__":
    # Configura logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Obtém uma instância do adaptador MCP
    mcp = ComponentFactory.get_mcp_adapter()
    if mcp:
        print("Adaptador MCP obtido com sucesso!")

    # Reinicia todos os componentes
    ComponentFactory.reset_all()
    print("Todos os componentes foram reiniciados")
