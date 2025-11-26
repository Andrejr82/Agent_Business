
import sys
import os

try:
    import langchain
    print(f"langchain version: {langchain.__version__}")
except ImportError:
    print("Could not import langchain")

try:
    import langchain.agents
    print(f"langchain.agents imported: {langchain.agents}")
    print(f"dir(langchain.agents): {dir(langchain.agents)}")
except ImportError as e:
    print(f"Error importing langchain.agents: {e}")

try:
    from langchain.agents import AgentExecutor
    print("Successfully imported AgentExecutor")
except ImportError as e:
    print(f"Error importing AgentExecutor: {e}")
