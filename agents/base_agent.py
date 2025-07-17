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

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core processing logic - must be implemented by subclasses.
        
        Args:
            input_data: Dictionary containing input parameters
            
        Returns:
            Dictionary containing processing results
            
        Reason: Abstract method ensures all agents implement core logic
        while allowing flexibility in implementation approach.
        """
        pass

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent with input data and handle errors consistently.
        
        Args:
            input_data: Dictionary containing input parameters
            
        Returns:
            Dictionary containing results with metadata
            
        Reason: Provides consistent error handling and metadata injection
        across all agents without requiring each agent to implement it.
        """
        start_time = datetime.utcnow()
        
        try:
            # Validate input
            if not isinstance(input_data, dict):
                raise ValueError("Input data must be a dictionary")
            
            # Execute core processing
            result = self.process(input_data)
            
            # Ensure result is a dictionary
            if not isinstance(result, dict):
                raise ValueError("Agent process() must return a dictionary")
            
            # Add metadata only if not already present
            if "agent_name" not in result:
                result["agent_name"] = self.agent_name
            if "agent_id" not in result:
                result["agent_id"] = self.agent_id
            if "processed_at" not in result:
                result["processed_at"] = datetime.utcnow().isoformat()
            
            # Set status to success only if not already set
            if "status" not in result:
                result["status"] = "success"
            
            # Log successful processing
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.info(f"Processing completed successfully in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            # Log the error
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.logger.error(f"Processing failed after {processing_time:.2f}s: {e}")
            
            # Return consistent error format
            return {
                "status": "error",
                "error": str(e),
                "agent_name": self.agent_name,
                "agent_id": self.agent_id,
                "processed_at": datetime.utcnow().isoformat(),
                "processing_time": processing_time
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Get current agent status and configuration.
        
        Returns:
            Dictionary containing agent status information
            
        Reason: Useful for debugging and monitoring agent health.
        """
        return {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "has_llm_client": bool(self.client),
            "model_name": self.config.get("model_name"),
            "status": "ready" if self.client else "no_llm"
        }

# =====================================================
#                 🔁 Test Connection
# =====================================================
def test_databricks_connection():
    """Test Databricks LLM connection with minimal overhead"""
    print("=== Testing Databricks LLM Connection ===")
    print(f"Token: {DATABRICKS_TOKEN[:20]}...")
    print(f"Base URL: {DATABRICKS_BASE_URL}")
    print(f"Model: {MODEL_ENDPOINT_ID}")
    
    class TestAgent(BaseAgent):
        def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "test_result": "success",
                "has_llm_client": bool(self.client),
                "model_name": self.config.get("model_name"),
                "input_received": bool(input_data)
            }

    agent = TestAgent("test_agent")
    
    # Test context loading
    if agent.load_context():
        result = agent.run({"test_input": "hello"})
        
        print(f"✓ Agent Status: {result.get('status')}")
        print(f"✓ Has LLM: {result.get('has_llm_client')}")
        print(f"✓ Model: {result.get('model_name')}")
        
        # Test actual LLM call if available
        if agent.client:
            print("\n--- Testing LLM Call ---")
            try:
                response = agent.client.chat.completions.create(
                    model=MODEL_ENDPOINT_ID,
                    messages=[{"role": "user", "content": "Say 'Hello from Databricks!'"}],
                    max_tokens=10,
                    temperature=0.0
                )
                print(f"✓ LLM Response: {response.choices[0].message.content}")
                return True
            except Exception as e:
                print(f"✗ LLM call failed: {e}")
                return False
        else:
            print("⚠️ No LLM client available")
            return True
    else:
        print("✗ Context loading failed")
        return False

if __name__ == "__main__":
    test_databricks_connection()
