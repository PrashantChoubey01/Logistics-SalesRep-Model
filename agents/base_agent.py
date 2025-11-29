"""Base agent class for all AI agents - Simple and Effective"""

import json
import logging
import os
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# =====================================================
#                 LLM CONFIGURATION
# =====================================================
def load_config():
    """Load configuration from config.json file."""
    script_dir = Path(__file__).parent.parent
    config_path = script_dir / "config" / "config.json"
    
    if not config_path.exists():
        # Fallback to environment variables
        return {
            "api_key": os.getenv("DATABRICKS_TOKEN", "dapi81b45be7f09611a410fc3e5104a8cadf-3"),
            "base_url": os.getenv("DATABRICKS_BASE_URL", "https://adb-1825279086009288.8.azuredatabricks.net/serving-endpoints"),
            "model_name": os.getenv("MODEL_ENDPOINT_ID", "databricks-meta-llama-3-70b-instruct")
        }
    
    # Read and parse JSON, handling comments
    with open(config_path, 'r') as f:
        content = f.read()
        # Remove JSON comments (lines starting with //)
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped.startswith('//'):
                cleaned_lines.append(line)
        cleaned_content = '\n'.join(cleaned_lines)
        config = json.loads(cleaned_content)
        return config

# Load config once at module level
_CONFIG = load_config()
DATABRICKS_TOKEN = _CONFIG.get("api_key", os.getenv("DATABRICKS_TOKEN", "dapi81b45be7f09611a410fc3e5104a8cadf-3"))
DATABRICKS_BASE_URL = _CONFIG.get("base_url", os.getenv("DATABRICKS_BASE_URL", "https://adb-1825279086009288.8.azuredatabricks.net/serving-endpoints"))
MODEL_ENDPOINT_ID = _CONFIG.get("model_name", os.getenv("MODEL_ENDPOINT_ID", "databricks-meta-llama-3-70b-instruct"))



class BaseAgent(ABC):
    """
    Simple and effective base class for all AI agents.
    
    Design Principles:
    1. Minimal overhead - agents should focus on their core logic
    2. Consistent interface - all agents have load_context() and process()
    3. Flexible LLM integration - works with or without LLM client
    4. Clear error handling - predictable error responses
    5. Logging support - built-in logging for debugging
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.agent_id = str(uuid.uuid4())[:8]
        self.client = None  # ChatOpenAI client
        self.openai_client = None  # OpenAI client for backward compatibility
        self.config = {
            "api_key": DATABRICKS_TOKEN,
            "base_url": DATABRICKS_BASE_URL,
            "model_name": MODEL_ENDPOINT_ID
        }
        
        # Setup logging
        self.logger = logging.getLogger(agent_name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def load_context(self) -> bool:
        """
        Load agent configuration and setup LLM client using ChatOpenAI.
        
        Returns:
            bool: True if context loaded successfully, False otherwise
            
        Reason: Separating initialization from context loading allows agents
        to be created without immediately requiring LLM access, useful for testing.
        """
        try:
            api_key = self.config.get("api_key")
            base_url = self.config.get("base_url")
            model_name = self.config.get("model_name")
            
            if api_key and base_url and model_name:
                from langchain_openai import ChatOpenAI
                
                # Initialize ChatOpenAI client (same pattern as quick_llm_client.py)
                self.client = ChatOpenAI(
                    model=model_name,
                    temperature=0.1,
                    base_url=base_url,
                    api_key=api_key
                )
                
                # Also keep OpenAI client for backward compatibility with function calling
                try:
                    from openai import OpenAI
                    self.openai_client = OpenAI(api_key=api_key, base_url=base_url)
                except Exception:
                    self.openai_client = None
                
                self.logger.info(f"{self.agent_name} loaded with Databricks LLM client (ChatOpenAI)")
                print(f"✓ {self.agent_name} connected to: {model_name}")
                return True
            else:
                self.logger.info(f"{self.agent_name} loaded without LLM client")
                print(f"⚠️ {self.agent_name} loaded without LLM client")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to load context for {self.agent_name}: {e}")
            print(f"✗ {self.agent_name} context loading failed: {e}")
            return False

    def _make_llm_call(self, prompt: str, function_schema: Dict, model_name: str = None, 
                      temperature: float = 0.1, max_tokens: int = 800) -> Dict[str, Any]:
        """
        Make LLM call with proper Databricks format using OpenAI client for function calling.
        
        Args:
            prompt: The prompt to send to the LLM
            function_schema: The function schema to use
            model_name: Model to use (defaults to config model)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dictionary containing the LLM response or error
        """
        # Use OpenAI client for function calling (backward compatibility)
        client = self.openai_client if self.openai_client else self.client
        
        if not client:
            return {"error": "LLM client not available"}
        
        try:
            # If using OpenAI client directly
            if hasattr(client, 'chat') and hasattr(client.chat, 'completions'):
                # Convert function schema to tools format for Databricks
                tools = [{
                    "type": "function",
                    "function": function_schema
                }]
                
                tool_choice = {
                    "type": "function",
                    "function": {"name": function_schema["name"]}
                }
                
                response = client.chat.completions.create(
                model=model_name or self.config.get("model_name"),
                messages=[{"role": "user", "content": prompt}],
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
                tool_calls = response.choices[0].message.tool_calls
                if tool_calls:
                    import json
                    return json.loads(tool_calls[0].function.arguments)
                else:
                    return {"error": "No tool calls in response"}
            else:
                # Fallback: try to use ChatOpenAI with bind_tools
                from langchain_core.messages import HumanMessage
                from langchain_core.utils.function_calling import convert_to_openai_function
                
                if hasattr(client, 'bind_tools'):
                    openai_function = convert_to_openai_function(function_schema)
                    bound_client = client.bind_tools([openai_function])
                    response = bound_client.invoke([HumanMessage(content=prompt)])
                    
                    if hasattr(response, 'tool_calls') and response.tool_calls:
                        import json
                        return json.loads(response.tool_calls[0]['args'])
                    else:
                        return {"error": "No tool calls in response"}
                else:
                    return {"error": "Client does not support function calling"}
                
        except Exception as e:
            return {"error": f"LLM call failed: {str(e)}"}

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core processing logic - must be implemented by subclasses.
        
        Args:
            input_data: Dictionary containing input parameters
            
        Returns:
            Dictionary containing processing results
        """
        pass

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent with input data and return results.
        
        Args:
            input_data: Dictionary containing input parameters
            
        Returns:
            Dictionary containing processing results with status
        """
        try:
            # Load context if not already loaded
            if not self.client:
                self.load_context()
            
            # Process the input data
            result = self.process(input_data)
            
            # Add status information
            if "error" in result:
                return {
                    "status": "error",
                    "error": result["error"],
                    "agent": self.agent_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "success",
                    "result": result,
                    "agent": self.agent_name,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Agent {self.agent_name} failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.agent_name,
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status information.
        
        Returns:
            Dictionary containing agent status
        """
        return {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "llm_connected": self.client is not None,
            "openai_client_connected": self.openai_client is not None,
            "model_name": self.config.get("model_name"),
            "base_url": self.config.get("base_url")
        }
    
    def get_openai_client(self):
        """
        Get OpenAI client for function calling (backward compatibility).
        Returns self.openai_client if available, otherwise tries to create one.
        """
        if self.openai_client:
            return self.openai_client
        
        # Try to create OpenAI client if we have config
        try:
            from openai import OpenAI
            api_key = self.config.get("api_key")
            base_url = self.config.get("base_url")
            if api_key and base_url:
                self.openai_client = OpenAI(api_key=api_key, base_url=base_url)
                return self.openai_client
        except Exception as e:
            self.logger.warning(f"Could not create OpenAI client: {e}")
        
        return None


# =====================================================
#                 🔧 Test Functions
# =====================================================

def test_databricks_connection():
    """Test Databricks LLM connection"""
    print("🧪 Testing Databricks LLM Connection")
    print("=" * 50)
    
    class TestAgent(BaseAgent):
        def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            return {"test": "success"}
    
    agent = TestAgent("TestAgent")
    
    if agent.load_context():
        print("✅ Databricks connection successful")
        
        # Test LLM call
        test_schema = {
            "name": "test_function",
            "description": "A test function",
            "parameters": {
                "type": "object",
                "properties": {
                    "result": {"type": "string"}
                },
                "required": ["result"]
            }
        }
        
        result = agent._make_llm_call(
            "Respond with 'test successful'",
            test_schema
        )
        
        if "error" not in result:
            print("✅ LLM function call successful")
            print(f"   Result: {result}")
        else:
            print(f"❌ LLM function call failed: {result['error']}")
    else:
        print("❌ Databricks connection failed")


if __name__ == "__main__":
    test_databricks_connection()
