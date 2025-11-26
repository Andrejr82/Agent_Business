
import sys
import os
import inspect

try:
    import langgraph
    print(f"langgraph version: {langgraph.__version__ if hasattr(langgraph, '__version__') else 'unknown'}")
    print(f"langgraph file: {langgraph.__file__}")
except ImportError:
    print("Could not import langgraph")

try:
    import langgraph.prebuilt
    print(f"langgraph.prebuilt imported: {langgraph.prebuilt}")
    print(f"dir(langgraph.prebuilt): {dir(langgraph.prebuilt)}")
except ImportError as e:
    print(f"Error importing langgraph.prebuilt: {e}")

try:
    from langgraph.prebuilt import tool_node
    print("Successfully imported langgraph.prebuilt.tool_node")
except ImportError as e:
    print(f"Error importing langgraph.prebuilt.tool_node: {e}")

try:
    import langgraph_prebuilt
    print(f"langgraph_prebuilt imported: {langgraph_prebuilt}")
    print(f"dir(langgraph_prebuilt): {dir(langgraph_prebuilt)}")
except ImportError as e:
    print(f"Error importing langgraph_prebuilt: {e}")
