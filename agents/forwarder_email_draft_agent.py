"""Forwarder Email Draft Agent: Generates rate request emails to forwarders without customer details."""

import json
import sys
import os
from typing import Dict, Any, List

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.base_agent import BaseAgent
except ImportError:
    try:
        from base_agent import BaseAgent
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from agents.base_agent import BaseAgent

class ForwarderEmailDraftAgent(BaseAgent):
    """Agent for drafting professional rate request emails to forwarders."""

    def __init__(self):
        super().__init__("forwarder_email_draft_agent")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate rate request email drafts for assigned forwarders.
        
        Expected input:
        - assigned_forwarders: List of assigned forwarders
        - shipment_details: Shipment information (without customer details)
        - origin_country: Origin country code
        - destination_country: Destination country code
        - thread_id: Thread identifier
        """
        assigned_forwarders = input_data.get("assigned_forwarders", [])
        shipment_details = input_data.get("shipment_details", {})
        origin_country = input_data.get("origin_country", "")
        destination_country = input_data.get("destination_country", "")
        thread_id = input_data.get("thread_id", "")

        if not assigned_forwarders:
            return {"error": "No forwarders assigned"}

        if not self.client:
            return {"error": "LLM client not initialized"}

        return self._generate_email_drafts(assigned_forwarders, shipment_details, origin_country, destination_country, thread_id)

    def _generate_email_drafts(self, assigned_forwarders: List[Dict[str, Any]], shipment_details: Dict[str, Any], origin_country: str, destination_country: str, thread_id: str) -> Dict[str, Any]:
        """Generate email drafts using LLM function calling."""
        try:
            function_schema = {
                "name": "generate_forwarder_emails",
                "description": "Generate professional rate request emails for forwarders",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_drafts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "forwarder_name": {"type": "string"},
                                    "to_email": {"type": "string"},
                                    "subject": {"type": "string"},
                                    "body": {"type": "string"},
                                    "priority": {"type": "string"},
                                    "urgency_level": {"type": "string"},
                                    "expected_response_time": {"type": "string"}
                                }
                            }
                        },
                        "total_emails_generated": {
                            "type": "integer"
                        },
                        "email_strategy": {
                            "type": "string"
                        },
                        "confidentiality_level": {
                            "type": "string"
                        }
                    }
                }
            }

            # Prepare shipment details for email (without customer info)
            shipment_info = {
                "origin_country": origin_country,
                "destination_country": destination_country,
                "commodity": shipment_details.get("commodity", ""),
                "container_type": shipment_details.get("container_type", ""),
                "quantity": shipment_details.get("quantity", ""),
                "weight": shipment_details.get("weight", ""),
                "volume": shipment_details.get("volume", ""),
                "shipment_date": shipment_details.get("shipment_date", ""),
                "shipment_type": shipment_details.get("shipment_type", "FCL")
            }

            prompt = f"""
Generate professional rate request emails for forwarders.

Forwarders: {json.dumps(assigned_forwarders, indent=2)}

Shipment: {json.dumps(shipment_info, indent=2)}

Rules:
- Professional tone
- Clear shipment details
- Request competitive rates
- NO customer information
- Request all-inclusive rates

Generate one email per forwarder with subject, body, priority, urgency, and response time.
"""

            response = self.client.chat.completions.create(
                model=self.config.get("model_name"),
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "function",
                    "function": function_schema
                }],
                tool_choice={"type": "function", "function": {"name": function_schema["name"]}},
                temperature=0.1,
                max_tokens=800
            )

            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if not tool_calls:
                raise Exception("No tool_calls in LLM response")

            tool_args = tool_calls[0].function.arguments
            if isinstance(tool_args, str):
                tool_args = json.loads(tool_args)

            result = dict(tool_args)
            result["generation_method"] = "llm_function_call"
            result["thread_id"] = thread_id
            result["origin_country"] = origin_country
            result["destination_country"] = destination_country
            
            # Validate and correct result if needed
            if not result.get("email_drafts"):
                result["email_drafts"] = []
                result["total_emails_generated"] = 0
                result["confidentiality_level"] = "high"

            # Ensure confidentiality level is set
            if not result.get("confidentiality_level"):
                result["confidentiality_level"] = "high"

            self.logger.info(f"Email draft generation successful: {result['total_emails_generated']} emails generated (confidentiality: {result['confidentiality_level']})")
            
            return result

        except Exception as e:
            self.logger.error(f"Email draft generation failed: {e}")
            return {"error": f"Email draft generation failed: {str(e)}"}

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_forwarder_email_draft_agent():
    print("=== Testing Forwarder Email Draft Agent ===")
    agent = ForwarderEmailDraftAgent()
    
    if not agent.load_context():
        print("✗ Failed to load context")
        return
    
    # Test case
    test_input = {
        "assigned_forwarders": [
            {
                "forwarder_name": "DHL Global Forwarding",
                "email": "rates@dhl.com",
                "contact": "DHL Rate Team",
                "priority": "primary",
                "assignment_reason": "Strong presence in both countries with electronics specialty",
                "specialty_match": True,
                "country_coverage": "Full coverage"
            },
            {
                "forwarder_name": "Kuehne + Nagel",
                "email": "quotes@kuehne-nagel.com",
                "contact": "KN Rate Team",
                "priority": "secondary",
                "assignment_reason": "Good coverage with competitive rates",
                "specialty_match": True,
                "country_coverage": "Full coverage"
            }
        ],
        "shipment_details": {
            "commodity": "electronics",
            "container_type": "40HC",
            "quantity": 2,
            "weight": "25,000 kg",
            "volume": "35 CBM",
            "shipment_date": "2024-04-20",
            "shipment_type": "FCL"
        },
        "origin_country": "AE",
        "destination_country": "IN",
        "thread_id": "test-thread-1"
    }
    
    print(f"\n--- Testing Email Draft Generation ---")
    result = agent.run(test_input)
    
    if result.get("status") == "success":
        email_drafts = result.get("email_drafts", [])
        total_emails = result.get("total_emails_generated", 0)
        strategy = result.get("email_strategy", "")
        confidentiality = result.get("confidentiality_level", "")
        
        print(f"✓ Emails Generated: {total_emails}")
        print(f"✓ Strategy: {strategy}")
        print(f"✓ Confidentiality: {confidentiality}")
        
        for i, email in enumerate(email_drafts, 1):
            print(f"\n  {i}. {email.get('forwarder_name')} ({email.get('priority')})")
            print(f"     To: {email.get('to_email')}")
            print(f"     Subject: {email.get('subject')}")
            print(f"     Urgency: {email.get('urgency_level')}")
            print(f"     Response Time: {email.get('expected_response_time')}")
            print(f"     Body Preview: {email.get('body', '')[:100]}...")
        
        if total_emails > 0:
            print("✓ Email draft generation successful!")
        else:
            print("✗ No email drafts generated")
    else:
        print(f"✗ Test failed: {result.get('error')}")

if __name__ == "__main__":
    test_forwarder_email_draft_agent() 