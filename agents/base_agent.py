"""Base agent class for all AI agents - Simple and Effective"""

import os
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime

# =====================================================
#                 LLM CONFIGURATION
# =====================================================
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "dapi81b45be7f09611a410fc3e5104a8cadf-3")
DATABRICKS_BASE_URL = os.getenv("DATABRICKS_BASE_URL", "https://adb-1825279086009288.8.azuredatabricks.net/serving-endpoints")
MODEL_ENDPOINT_ID = os.getenv("MODEL_ENDPOINT_ID", "databricks-meta-llama-3-3-70b-instruct")
# MODEL_ENDPOINT_ID = os.getenv("MODEL_ENDPOINT_ID", "databricks-claude-sonnet-4")



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
        self.client = None
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
        Load agent configuration and setup LLM client.
        
        Returns:
            bool: True if context loaded successfully, False otherwise
            
        Reason: Separating initialization from context loading allows agents
        to be created without immediately requiring LLM access, useful for testing.
        """
        try:
            api_key = self.config.get("api_key")
            base_url = self.config.get("base_url")
            
            if api_key and base_url:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key, base_url=base_url)
                
                # Test connection with minimal request
                test_response = self.client.chat.completions.create(
                    model=self.config.get("model_name"),
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1,
                    temperature=0.0
                )
                
                self.logger.info(f"{self.agent_name} loaded with Databricks LLM client")
                print(f"✓ {self.agent_name} connected to: {self.config.get('model_name')}")
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
        Make LLM call with proper Databricks format.
        
        Args:
            prompt: The prompt to send to the LLM
            function_schema: The function schema to use
            model_name: Model to use (defaults to config model)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dictionary containing the LLM response or error
        """
        if not self.client:
            return {"error": "LLM client not available"}
        
        try:
            # Convert function schema to tools format for Databricks
            tools = [{
                "type": "function",
                "function": function_schema
            }]
            
            tool_choice = {
                "type": "function",
                "function": {"name": function_schema["name"]}
            }
            
            response = self.client.chat.completions.create(
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
            "model_name": self.config.get("model_name"),
            "base_url": self.config.get("base_url")
        }


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
