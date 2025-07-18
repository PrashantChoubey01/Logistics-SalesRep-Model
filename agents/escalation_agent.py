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
                        "description": "Type of escalation (e.g., poor_classification, low_confidence, anomaly, customer_request, error, other, non_logistics_inquiry)"
                    },
                    "customer_intent": {
                        "type": "string",
                        "description": "Brief description of what the customer is asking for or needs"
                    },
                    "escalation_message": {
                        "type": "string",
                        "description": "Suggested message to the human operator"
                    },
                    "suggested_next_action": {
                        "type": "string",
                        "description": "Recommended next action for the human"
                    },
                    "acknowledgment_response": {
                        "type": "string",
                        "description": "Professional acknowledgment response to send to customer with SeaRates information"
                    },
                    "is_non_logistics_inquiry": {
                        "type": "boolean",
                        "description": "True if this is a non-logistics inquiry that can be answered with SeaRates information"
                    }
                },
                "required": ["escalate", "reason", "escalation_type", "customer_intent", "escalation_message", "suggested_next_action", "acknowledgment_response", "is_non_logistics_inquiry"]
            }
        }

        prompt = f"""
You are an expert workflow assistant for SeaRates by DP World, a leading global logistics and supply chain solutions provider.

Review the following email and prior agent results (classification, extraction, validation, etc.).
Decide if this case should be escalated to a human. Reasons for escalation may include: poor classification, low confidence, missing/ambiguous data, customer request, anomaly, error, or other business logic.

IMPORTANT: Always provide a professional acknowledgment response that includes:
1. Thank the customer for contacting SeaRates by DP World
2. Briefly mention our services (international shipping, freight forwarding, container shipping, supply chain solutions, customs clearance, real-time tracking)
3. Inform them a human agent will contact them shortly
4. Include our contact information (phone, WhatsApp, email, website)
5. Keep it professional and welcoming
6. MUST include the word "logistics" and "www.searates.com" in the response

FOR NON-LOGISTICS INQUIRIES: If the customer is asking about general services, company information, or non-logistics topics, provide comprehensive information about SeaRates including:
- Our global presence and expertise (DP World, 40+ countries, 78 terminals, 190+ countries served)
- Complete service portfolio (FCL/LCL shipping, air freight, land transport, warehousing, customs clearance, insurance, project cargo, dangerous goods, temperature-controlled shipping)
- Digital solutions (online booking, real-time tracking, rate comparison, documentation management)
- Industry expertise (automotive, electronics, pharmaceuticals, fashion, food & beverage, chemicals)
- Sustainability initiatives
- Customer support and account management
- Visit www.searates.com for detailed information and online services

IMPORTANT: For non-logistics inquiries, set escalate to false and provide a comprehensive response that answers their question directly with detailed SeaRates information.

Return:
- escalate: true/false
- reason: reason for escalation
- escalation_type: poor_classification/low_confidence/anomaly/customer_request/error/other
- customer_intent: brief description of what customer needs
- escalation_message: suggested message to the human operator
- suggested_next_action: recommended next action for the human
- acknowledgment_response: professional response to send to customer with SeaRates information

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
        # Poor classification case
        {
            "email_text": "Hello, I need some help with something.",
            "subject": "Vague Request",
            "prior_results": {
                "classification": {"email_type": "unknown", "confidence": 0.3}
                
            }
        },
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
        # Non-logistics inquiry
        {
            "email_text": "What services do you offer? I'm looking for general information.",
            "subject": "General Inquiry",
            "prior_results": {
                "classification": {"email_type": "non_logistics", "confidence": 0.8}
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
        # No escalation needed (for comparison)
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