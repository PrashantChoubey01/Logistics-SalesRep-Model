"""Base agent class for all AI agents"""

# =====================================================
#                 LLM CONFIGURATION
# =====================================================
# Databricks Configuration
DATABRICKS_TOKEN = "dapi81b45be7f09611a410fc3e5104a8cadf-3"
DATABRICKS_BASE_URL = "https://adb-1825279086009288.8.azuredatabricks.net/serving-endpoints"
MODEL_ENDPOINT_ID = "databricks-meta-llama-3-3-70b-instruct"

LLM_CONFIG = {
    "api_key": DATABRICKS_TOKEN,
    "base_url": DATABRICKS_BASE_URL,
    "model_name": MODEL_ENDPOINT_ID
}

import os
from abc import ABC, abstractmethod
from typing import Dict, Any
import uuid
from datetime import datetime
import logging

# Optional imports with fallbacks
try:
    from utils.logger import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)



class BaseAgent(ABC):
    """Base class for all AI agents"""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.agent_id = str(uuid.uuid4())[:8]
        self.config = LLM_CONFIG
        self.client = None
        self.logger = get_logger(self.agent_name)

    def load_context(self) -> bool:
        """Load agent configuration and setup client"""
        try:
            api_key = self.config.get("api_key")
            base_url = self.config.get("base_url")
            
            if api_key and base_url:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key, base_url=base_url)
                self.logger.info(f"{self.agent_name} loaded with Databricks LLM client")
                print(f"✓ {self.agent_name} connected to: {self.config.get('model_name')}")
            else:
                self.logger.info(f"{self.agent_name} loaded without LLM (will use regex fallback)")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load {self.agent_name}: {e}")
            print(f"✗ LLM connection failed: {e}")
            return False

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input data - must be implemented by subclasses"""
        pass

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with input data"""
        try:
            result = self.process(input_data)
            result.update({
                "agent_name": self.agent_name,
                "agent_id": self.agent_id,
                "processed_at": datetime.utcnow().isoformat(),
                "status": "success"
            })
            self.logger.info("Processing completed successfully.")
            return result
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return {
                "error": str(e),
                "agent_name": self.agent_name,
                "agent_id": self.agent_id,
                "processed_at": datetime.utcnow().isoformat(),
                "status": "error"
            }

# =====================================================
#                 🔁 Test Databricks Connection
# =====================================================
def test_databricks_connection():
    print("=== Testing Databricks LLM Connection ===")
    print(f"Token: {DATABRICKS_TOKEN[:20]}...")
    print(f"Base URL: {DATABRICKS_BASE_URL}")
    print(f"Model: {MODEL_ENDPOINT_ID}")
    
    class TestAgent(BaseAgent):
        def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            return {
                "test": "success",
                "has_llm_client": bool(self.client),
                "model_name": self.config.get("model_name"),
                "input_received": bool(input_data)
            }

    agent = TestAgent("databricks_test_agent")
    
    # Test connection
    if agent.load_context():
        result = agent.run({"test_input": "hello databricks"})
        print(f"✓ Agent: {result.get('agent_name')}")
        print(f"✓ Status: {result.get('status')}")
        print(f"✓ Has LLM: {result.get('has_llm_client')}")
        print(f"✓ Model: {result.get('model_name')}")
        
        # Test actual LLM call if client exists
        if agent.client:
            print("\n--- Testing Actual LLM Call ---")
            try:
                response = agent.client.chat.completions.create(
                    model=MODEL_ENDPOINT_ID,
                    messages=[{"role": "user", "content": "Say 'Hello from Databricks!' in exactly 5 words."}],
                    max_tokens=20,
                    temperature=0.0
                )
                print(f"✓ LLM Response: {response.choices[0].message.content}")
                return True
            except Exception as e:
                print(f"✗ LLM call failed: {e}")
                return False
    else:
        print("✗ Failed to load context")
        return False

if __name__ == "__main__":
    test_databricks_connection()
