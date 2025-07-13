"""Confirmation Agent: Detects and extracts confirmation intent from customer emails using LLM function calling."""

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from agents.base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class ConfirmationAgent(BaseAgent):
    """Agent to detect confirmation intent in customer emails using LLM function calling."""

    def __init__(self):
        super().__init__("confirmation_agent")

    def process(self, input_data):
        email_text = input_data.get("email_text", "")
        subject = input_data.get("subject", "")
        if not email_text:
            return {"error": "No email text provided"}

        if self.client:
            print("[INFO] Using LLM function calling for confirmation detection")
            try:
                return self._llm_function_call(subject, email_text)
            except Exception as e:
                print(f"[WARN] LLM function call failed: {e}")
                return {"error": f"LLM function call failed: {e}"}
        else:
            print("[INFO] LLM client not available, cannot check confirmation")
            return {"error": "LLM client not available"}

    def _llm_function_call(self, subject, email_text):
        function_schema = {
            "name": "detect_confirmation",
            "description": "Detect if the email is a confirmation and extract confirmation details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "is_confirmation": {
                        "type": "boolean",
                        "description": "True if the email is a confirmation"
                    },
                    "confirmation_type": {
                        "type": "string",
                        "description": "Type of confirmation (e.g., booking, quote acceptance, shipment, other)"
                    },
                    "confirmation_details": {
                        "type": "string",
                        "description": "Details about what is being confirmed (e.g., number of containers, route, etc.)"
                    },
                    "confirmation_message": {
                        "type": "string",
                        "description": "Suggested message to acknowledge the confirmation"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Explanation for why the email is or is not a confirmation"
                    }
                },
                "required": ["is_confirmation", "confirmation_type", "confirmation_details", "confirmation_message", "reasoning"]
            }
        }

        prompt = f"""
You are an assistant that detects if a customer email is a confirmation (e.g., confirming a booking, accepting a quote).
If so, extract the type of confirmation and any relevant details (e.g., number of containers, route, etc.).
Return:
- is_confirmation: true/false
- confirmation_type: booking/quote acceptance/shipment/other
- confirmation_details: details about what is being confirmed
- confirmation_message: suggested message to acknowledge the confirmation
- reasoning: explanation

Email:
Subject: {subject}
Body: {email_text}
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

def test_confirmation_agent():
    print("=== Testing Confirmation Agent (Databricks LLM Function Calling) ===")
    agent = ConfirmationAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}, Has LLM client: {bool(agent.client)}")

    test_cases = [
        {
            "email_text": "Yes, I confirm the booking for 2x40ft containers from Shanghai to Long Beach.",
            "subject": "Booking Confirmation"
        },
        {
            "email_text": "We accept your quote for the LCL shipment to Rotterdam.",
            "subject": "Quote Acceptance"
        },
        {
            "email_text": "Please proceed with the shipment as discussed.",
            "subject": "Proceed"
        },
        {
            "email_text": "Thank you for your offer. We will get back to you.",
            "subject": "Re: Offer"
        },
        {
            "email_text": "Confirmed. Please arrange the pickup for next week.",
            "subject": "Pickup Confirmation"
        },
        {
            "email_text": "Can you please clarify the insurance terms?",
            "subject": "Clarification Needed"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test_case['subject']}")
        result = agent.run(test_case)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_confirmation_agent()