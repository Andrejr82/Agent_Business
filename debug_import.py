
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

print("Attempting to import core.query_processor...")
try:
    from core.query_processor import QueryProcessor
    print("Successfully imported QueryProcessor")
except Exception as e:
    print(f"Error importing QueryProcessor: {e}")
    import traceback
    traceback.print_exc()

print("\nAttempting to import core.agents.tool_agent directly...")
try:
    from core.agents.tool_agent import ToolAgent
    print("Successfully imported ToolAgent")
except Exception as e:
    print(f"Error importing ToolAgent: {e}")
    import traceback
    traceback.print_exc()
