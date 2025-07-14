"""Response Generator Agent: Generates responses for customer, forwarder, or sales using LLM function calling."""

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from agents.base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class ResponseGeneratorAgent(BaseAgent):
    """Agent to generate context-aware responses for customer, forwarder, or sales using LLM function calling."""

    def __init__(self):
        super().__init__("response_generator_agent")

    def process(self, input_data):
        """
        input_data: {
            "recipient_type": "customer"|"forwarder"|"sales",
            "context": dict,  # e.g., extracted shipment info, classification, etc.
            "previous_messages": [str],  # optional, for threading/context
            "custom_instructions": str,  # optional, e.g., "be very polite"
            "indicative_rate": str,      # optional, e.g., "$919 - $1249"
        }
        """
        recipient_type = input_data.get("recipient_type", "customer")
        context = input_data.get("context", {})
        previous_messages = input_data.get("previous_messages", [])
        custom_instructions = input_data.get("custom_instructions", "")
        indicative_rate = input_data.get("indicative_rate")

        if not context:
            return {"error": "No context provided for response generation"}

        if self.client:
            print("[INFO] Using LLM function calling for response generation")
            try:
                return self._llm_function_call(
                    recipient_type, context, previous_messages, custom_instructions, indicative_rate
                )
            except Exception as e:
                print(f"[WARN] LLM function call failed: {e}")
                return {"error": f"LLM function call failed: {e}"}
        else:
            print("[INFO] LLM client not available, cannot generate response")
            return {"error": "LLM client not available"}

    def _llm_function_call(self, recipient_type, context, previous_messages, custom_instructions, indicative_rate):
        function_schema = {
            "name": "generate_response",
            "description": "Generate a context-aware response for customer, forwarder, or sales.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recipient_type": {
                        "type": "string",
                        "description": "Who the response is for (customer, forwarder, sales)"
                    },
                    "response_subject": {
                        "type": "string",
                        "description": "Suggested subject line for the response"
                    },
                    "response_body": {
                        "type": "string",
                        "description": "The main response message"
                    },
                    "tone": {
                        "type": "string",
                        "description": "Tone of the message (e.g., polite, formal, friendly, urgent)"
                    },
                    "attachments_needed": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of any suggested attachments (e.g., quote.pdf, booking_confirmation.pdf)"
                    },
                    "next_steps": {
                        "type": "string",
                        "description": "Recommended next steps for the recipient"
                    },
                    "indicative_rate": {
                        "type": "string",
                        "description": "Indicative rate range for the shipment (e.g., \"$919 - $1249\"), if available"
                    }
                },
                "required": ["recipient_type", "response_subject", "response_body", "tone", "attachments_needed", "next_steps"]
            }
        }

        prompt = f"""
You are an expert assistant for a logistics company. Generate a response for the specified recipient (customer, forwarder, or sales).
- Use the provided context (shipment info, classification, etc.).
- If previous messages are provided, maintain thread continuity.
- Adapt tone and content to the recipient.
- If custom instructions are provided, follow them (e.g., "be very polite").
{"- If indicative_rate is provided, clearly mention this indicative rate range (e.g., 'Indicative rate: $919 - $1249') in the response body and/or subject." if indicative_rate else ""}
Recipient: {recipient_type}
Context: {json.dumps(context, indent=2)}
Previous messages: {json.dumps(previous_messages, indent=2)}
Custom instructions: {custom_instructions}
Indicative rate: {indicative_rate if indicative_rate else "None"}
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
        # Always include indicative_rate in the output if present
        if indicative_rate:
            result["indicative_rate"] = indicative_rate
        return result

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_response_generator_agent():
    print("=== Testing Response Generator Agent (Databricks LLM Function Calling) ===")
    agent = ResponseGeneratorAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}, Has LLM client: {bool(agent.client)}")

    test_cases = [
        # Customer response with indicative rate
        {
            "recipient_type": "customer",
            "context": {
                "classification": {"email_type": "logistics_request", "confidence": 0.95},
                "extraction": {"origin": "Shanghai", "destination": "Long Beach", "shipment_type": "FCL", "container_type": "40GP", "quantity": 2}
            },
            "previous_messages": ["Customer: Need quote for 2x40ft FCL from Shanghai to Long Beach."],
            "custom_instructions": "Be very polite and thank the customer for their inquiry.",
            "indicative_rate": "$1,100 - $1,300"
        },
        # Customer response without indicative rate
        {
            "recipient_type": "customer",
            "context": {
                "classification": {"email_type": "confirmation_reply", "confidence": 0.99},
                "extraction": {"origin": "Singapore", "destination": "Los Angeles", "shipment_type": "FCL", "container_type": "40GP", "quantity": 1}
            },
            "custom_instructions": "Send a booking confirmation and next steps."
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Recipient: {test_case['recipient_type']}")
        result = agent.run(test_case)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_response_generator_agent()