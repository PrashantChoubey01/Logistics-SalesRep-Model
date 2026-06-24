"""Shared base class and LLM configuration for all workflow agents."""

import json
import logging
import os
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # python-dotenv is optional; environment variables can also be exported directly.
    pass

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def load_config() -> Dict[str, Any]:
    """Resolve runtime LLM configuration.

    Non-secret settings (endpoint base URL and model name) are read from
    ``config/config.json`` when present and may be overridden by environment
    variables. The Databricks access token is never stored in the repository:
    it is read exclusively from the ``DATABRICKS_TOKEN`` environment variable
    (see ``.env.example``).
    """
    config_path = CONFIG_DIR / "config.json"
    file_config: Dict[str, Any] = {}

    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as fh:
            # config.json may carry `//` line comments; strip them before parsing.
            cleaned = "\n".join(
                line for line in fh.read().splitlines() if not line.strip().startswith("//")
            )
            if cleaned.strip():
                file_config = json.loads(cleaned)

    return {
        "api_key": os.getenv("DATABRICKS_TOKEN", ""),
        "base_url": os.getenv("DATABRICKS_BASE_URL", file_config.get("base_url", "")),
        "model_name": os.getenv("MODEL_ENDPOINT_ID", file_config.get("model_name", "")),
    }


_CONFIG = load_config()
DATABRICKS_TOKEN = _CONFIG["api_key"]
DATABRICKS_BASE_URL = _CONFIG["base_url"]
MODEL_ENDPOINT_ID = _CONFIG["model_name"]

if not DATABRICKS_TOKEN:
    logging.getLogger(__name__).warning(
        "DATABRICKS_TOKEN is not set. LLM calls will fail until it is provided. "
        "Copy .env.example to .env and set your Databricks token."
    )


class BaseAgent(ABC):
    """Base class for all agents.

    Provides a consistent ``load_context()`` / ``process()`` / ``run()`` interface,
    optional LLM client setup, and built-in logging. Agents work with or without
    an LLM client, which keeps them testable without LLM access.
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.agent_id = str(uuid.uuid4())[:8]
        self.client = None
        self.openai_client = None
        self.config = {
            "api_key": DATABRICKS_TOKEN,
            "base_url": DATABRICKS_BASE_URL,
            "model_name": MODEL_ENDPOINT_ID,
        }

        self.logger = logging.getLogger(agent_name)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def load_context(self) -> bool:
        """Load agent configuration and set up the LLM client.

        Returns True if the context loaded successfully (with or without an LLM
        client), False on failure.
        """
        try:
            api_key = self.config.get("api_key")
            base_url = self.config.get("base_url")
            model_name = self.config.get("model_name")

            if api_key and base_url and model_name:
                from langchain_openai import ChatOpenAI

                self.client = ChatOpenAI(
                    model=model_name, temperature=0.1, base_url=base_url, api_key=api_key
                )

                # Also keep an OpenAI client for function calling.
                try:
                    from openai import OpenAI

                    self.openai_client = OpenAI(api_key=api_key, base_url=base_url)
                except Exception:
                    self.openai_client = None

                self.logger.info(
                    f"{self.agent_name} loaded with Databricks LLM client (ChatOpenAI)"
                )
                print(f"{self.agent_name} connected to: {model_name}")
                return True
            else:
                self.logger.info(f"{self.agent_name} loaded without LLM client")
                print(f"{self.agent_name} loaded without LLM client")
                return True

        except Exception as e:
            self.logger.error(f"Failed to load context for {self.agent_name}: {e}")
            print(f"{self.agent_name} context loading failed: {e}")
            return False

    def _make_llm_call(
        self,
        prompt: str,
        function_schema: Dict,
        model_name: str = None,
        temperature: float = 0.1,
        max_tokens: int = 800,
    ) -> Dict[str, Any]:
        """Make a function-calling LLM request in Databricks format.

        Returns the parsed tool-call arguments as a dict, or a dict with an
        ``error`` key on failure.
        """
        client = self.openai_client if self.openai_client else self.client

        if not client:
            return {"error": "LLM client not available"}

        try:
            if hasattr(client, "chat") and hasattr(client.chat, "completions"):
                tools = [{"type": "function", "function": function_schema}]

                tool_choice = {"type": "function", "function": {"name": function_schema["name"]}}

                response = client.chat.completions.create(
                    model=model_name or self.config.get("model_name"),
                    messages=[{"role": "user", "content": prompt}],
                    tools=tools,
                    tool_choice=tool_choice,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                tool_calls = response.choices[0].message.tool_calls
                if tool_calls:
                    import json

                    return json.loads(tool_calls[0].function.arguments)
                else:
                    return {"error": "No tool calls in response"}
            else:
                # Fall back to ChatOpenAI with bind_tools.
                from langchain_core.messages import HumanMessage
                from langchain_core.utils.function_calling import convert_to_openai_function

                if hasattr(client, "bind_tools"):
                    openai_function = convert_to_openai_function(function_schema)
                    bound_client = client.bind_tools([openai_function])
                    response = bound_client.invoke([HumanMessage(content=prompt)])

                    if hasattr(response, "tool_calls") and response.tool_calls:
                        import json

                        return json.loads(response.tool_calls[0]["args"])
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
            if not self.client:
                self.load_context()

            result = self.process(input_data)

            if "error" in result:
                return {
                    "status": "error",
                    "error": result["error"],
                    "agent": self.agent_name,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            else:
                return {
                    "status": "success",
                    "result": result,
                    "agent": self.agent_name,
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            self.logger.error(f"Agent {self.agent_name} failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent": self.agent_name,
                "timestamp": datetime.utcnow().isoformat(),
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
            "base_url": self.config.get("base_url"),
        }

    def get_openai_client(self):
        """
        Get OpenAI client for function calling (backward compatibility).
        Returns self.openai_client if available, otherwise tries to create one.
        """
        if self.openai_client:
            return self.openai_client

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


def test_databricks_connection():
    """Test Databricks LLM connection"""
    print("Testing Databricks LLM Connection")
    print("=" * 50)

    class TestAgent(BaseAgent):
        def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
            return {"test": "success"}

    agent = TestAgent("TestAgent")

    if agent.load_context():
        print("Databricks connection successful")

        test_schema = {
            "name": "test_function",
            "description": "A test function",
            "parameters": {
                "type": "object",
                "properties": {"result": {"type": "string"}},
                "required": ["result"],
            },
        }

        result = agent._make_llm_call("Respond with 'test successful'", test_schema)

        if "error" not in result:
            print("LLM function call successful")
            print(f"   Result: {result}")
        else:
            print(f"LLM function call failed: {result['error']}")
    else:
        print("Databricks connection failed")


if __name__ == "__main__":
    test_databricks_connection()
