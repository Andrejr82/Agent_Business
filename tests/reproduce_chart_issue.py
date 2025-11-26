import sys
import os
import logging

# Add project root to path
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO)

from core.agents.tool_agent import ToolAgent
from core.llm_gemini_adapter import GeminiLLMAdapter
from core.config.config import Config

def test_chart_generation():
    print("Initializing ToolAgent...")
    try:
        # Initialize adapter and agent
        llm_adapter = GeminiLLMAdapter()
        agent = ToolAgent(llm_adapter=llm_adapter)
        
        query = "gere um gráfico de vendas da categoria esmaltes"
        print(f"Processing query: '{query}'")
        
        response = agent.process_query(query)
        
        print("\n--- Response Analysis ---")
        print(f"Response Type: {response.get('type')}")
        
        if response.get('type') == 'chart':
            print("SUCCESS: Chart generated!")
            output = response.get('output')
            if isinstance(output, dict):
                print(f"Chart Data Keys: {output.keys()}")
            else:
                print(f"Chart Output Type: {type(output)}")
        else:
            print("FAILURE: Chart NOT generated.")
            print(f"Output: {response.get('output')}")
            
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    with open("reproduce_output.txt", "w", encoding="utf-8") as f:
        sys.stdout = f
        test_chart_generation()
        sys.stdout = sys.__stdout__
    
    with open("reproduce_output.txt", "r", encoding="utf-8") as f:
        print(f.read())
