"""Memory Agent: Maintains conversation context and history."""

import os
import sys
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from agents.base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class MemoryAgent(BaseAgent):
    """Agent for storing and retrieving conversation context and history."""

    def __init__(self):
        super().__init__("memory_agent")
        # In-memory store: {thread_id: [history]}
        self.memory_store = {}

    def process(self, input_data):
        """
        input_data: {
            "action": "store"|"retrieve"|"clear",
            "thread_id": str,
            "message": dict (for store),
            "limit": int (for retrieve, optional)
        }
        """
        action = input_data.get("action")
        thread_id = input_data.get("thread_id")
        if not thread_id:
            return {"error": "thread_id is required"}

        if action == "store":
            message = input_data.get("message")
            if not message:
                return {"error": "No message to store"}
            entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "message": message
            }
            self.memory_store.setdefault(thread_id, []).append(entry)
            return {"status": "stored", "thread_id": thread_id, "entry": entry}

        elif action == "retrieve":
            limit = input_data.get("limit", 10)
            history = self.memory_store.get(thread_id, [])[-limit:]
            return {"status": "retrieved", "thread_id": thread_id, "history": history}

        elif action == "clear":
            self.memory_store.pop(thread_id, None)
            return {"status": "cleared", "thread_id": thread_id}

        else:
            return {"error": f"Unknown action: {action}"}

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_memory_agent():
    print("=== Testing Memory Agent ===")
    agent = MemoryAgent()
    agent.load_context()
    thread_id = "thread-123"
    # Store messages
    for i in range(3):
        msg = {"from": "customer", "text": f"Message {i+1}"}
        result = agent.run({"action": "store", "thread_id": thread_id, "message": msg})
        print(result)
    # Retrieve history
    result = agent.run({"action": "retrieve", "thread_id": thread_id, "limit": 2})
    print(json.dumps(result, indent=2))
    # Clear history
    result = agent.run({"action": "clear", "thread_id": thread_id})
    print(result)
    # Retrieve after clear
    result = agent.run({"action": "retrieve", "thread_id": thread_id})
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_memory_agent()