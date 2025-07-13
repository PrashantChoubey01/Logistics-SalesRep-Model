"""Logging Agent: Centralized logging for agent actions, errors, and metrics."""

import os
import sys
import json
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.base_agent import BaseAgent

class LoggingAgent(BaseAgent):
    """Agent for logging actions, errors, and metrics."""

    def __init__(self):
        super().__init__("logging_agent")
        self.log_file = os.getenv("AGENT_LOG_FILE", "agentic_system.log")
        self.logger = logging.getLogger("LoggingAgent")
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def process(self, input_data):
        """
        input_data: {
            "event_type": "info"|"error"|"metric"|"audit",
            "message": str,
            "agent_name": str,
            "details": dict (optional)
        }
        """
        event_type = input_data.get("event_type", "info")
        message = input_data.get("message", "")
        agent_name = input_data.get("agent_name", "")
        details = input_data.get("details", {})

        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "agent_name": agent_name,
            "message": message,
            "details": details
        }

        log_str = json.dumps(log_entry)
        if event_type == "error":
            self.logger.error(log_str)
        elif event_type == "metric":
            self.logger.info("[METRIC] " + log_str)
        elif event_type == "audit":
            self.logger.info("[AUDIT] " + log_str)
        else:
            self.logger.info(log_str)

        return {"status": "logged", "log_entry": log_entry}

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_logging_agent():
    print("=== Testing Logging Agent ===")
    agent = LoggingAgent()
    agent.load_context()
    test_cases = [
        {"event_type": "info", "message": "Workflow started", "agent_name": "orchestrator"},
        {"event_type": "error", "message": "Extraction failed", "agent_name": "extraction_agent", "details": {"error": "Timeout"}},
        {"event_type": "metric", "message": "Classification accuracy", "agent_name": "classification_agent", "details": {"accuracy": 0.95}},
        {"event_type": "audit", "message": "User escalated case", "agent_name": "escalation_agent", "details": {"user": "john.doe@example.com"}}
    ]
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        result = agent.run(test_case)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_logging_agent()