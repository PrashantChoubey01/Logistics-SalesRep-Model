"""Escalation Agent: Decides if a case should be escalated to a human using LLM function calling."""

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from agents.base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class EscalationAgent(BaseAgent):
    """Agent to decide if escalation to a human is needed using LLM function calling."""

    def __init__(self):
        super().__init__("escalation_agent")

    def process(self, input_data):
        email_text = input_data.get("email_text", "")
        subject = input_data.get("subject", "")
        prior_results = input_data.get("prior_results", {})  # e.g., classification, extraction, validation, etc.

        if not email_text:
            return {"error": "No email text provided"}

        if self.client:
            print("[INFO] Using LLM function calling for escalation decision")
            try:
                return self._llm_function_call(subject, email_text, prior_results)
            except Exception as e:
                print(f"[WARN] LLM function call failed: {e}")
                return {"error": f"LLM function call failed: {e}"}
        else:
            print("[INFO] LLM client not available, cannot check escalation")
            return {"error": "LLM client not available"}

    def _llm_function_call(self, subject, email_text, prior_results):
        function_schema = {
            "name": "decide_escalation",
            "description": "Decide if escalation to a human is needed based on email and prior agent results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "escalate": {
                        "type": "boolean",
                        "description": "True if escalation to a human is needed"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for escalation decision"
                    },
                    "escalation_type": {
                        "type": "string",
                        "description": "Type of escalation (e.g., low_confidence, anomaly, customer_request, error, other)"
                    },
                    "escalation_message": {
                        "type": "string",
                        "description": "Suggested message to the human operator"
                    },
                    "suggested_next_action": {
                        "type": "string",
                        "description": "Recommended next action for the human"
                    }
                },
                "required": ["escalate", "reason", "escalation_type", "escalation_message", "suggested_next_action"]
            }
        }

        prompt = f"""
You are an expert workflow assistant. Review the following email and prior agent results (classification, extraction, validation, etc.).
Decide if this case should be escalated to a human. Reasons for escalation may include: low confidence, missing/ambiguous data, customer request, anomaly, error, or other business logic.

Return:
- escalate: true/false
- reason: reason for escalation
- escalation_type: low_confidence/anomaly/customer_request/error/other
- escalation_message: suggested message to the human operator
- suggested_next_action: recommended next action for the human

Email:
Subject: {subject}
Body: {email_text}

Prior Agent Results:
{json.dumps(prior_results, indent=2)}
"""

        response = self.client.chat.completions.create(
            model=self.config.get("model_name", "databricks-meta-llama-3-3-70b-instruct"),
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "type": "function",
                "function": function_schema
            }],
            tool_choice={"type": "function", "function": {"name": function_schema["name"]}},
            temperature=0.0,
            max_tokens=600
        )
        tool_calls = getattr(response.choices[0].message, "tool_calls", None)
        if not tool_calls:
            raise Exception("No tool_calls in LLM response")
        tool_args = tool_calls[0].function.arguments
        if isinstance(tool_args, str):
            tool_args = json.loads(tool_args)
        result = dict(tool_args)
        result["extraction_method"] = "databricks_llm_function_call"
        return result

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_escalation_agent():
    print("=== Testing Escalation Agent (Databricks LLM Function Calling) ===")
    agent = EscalationAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}, Has LLM client: {bool(agent.client)}")

    test_cases = [
        # Low confidence case
        {
            "email_text": "Need quote for shipping, but no details provided.",
            "subject": "Vague Request",
            "prior_results": {
                "classification": {"email_type": "logistics_request", "confidence": 0.55},
                "validation": {"overall_validity": False, "missing_fields": ["origin", "destination", "shipment_type"]}
            }
        },
        # Customer requests escalation
        {
            "email_text": "Please have someone call me, I need to discuss this urgently.",
            "subject": "Escalation Request",
            "prior_results": {
                "classification": {"email_type": "logistics_request", "confidence": 0.95}
            }
        },
        # Anomaly detected
        {
            "email_text": "I want to ship 10000 tons of gold from Atlantis to El Dorado.",
            "subject": "Suspicious Shipment",
            "prior_results": {
                "classification": {"email_type": "logistics_request", "confidence": 0.9},
                "validation": {"overall_validity": False, "warnings": ["Unrealistic shipment volume"]}
            }
        },
        # No escalation needed
        {
            "email_text": "Yes, I confirm the booking for 2x40ft containers from Shanghai to Long Beach.",
            "subject": "Booking Confirmation",
            "prior_results": {
                "classification": {"email_type": "confirmation_reply", "confidence": 0.98},
                "validation": {"overall_validity": True}
            }
        },
        # Error in extraction
        {
            "email_text": "Need quote for FCL shipment.",
            "subject": "Shipping Quote",
            "prior_results": {
                "classification": {"email_type": "logistics_request", "confidence": 0.8},
                "extraction": {"error": "Extraction failed: Model timeout"}
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test_case['subject']}")
        result = agent.run(test_case)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_escalation_agent()