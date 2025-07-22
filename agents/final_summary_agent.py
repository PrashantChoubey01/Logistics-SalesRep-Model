"""Rate Collation Agent: Collates forwarder rates and sends summary to sales personnel."""

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

class RateCollationAgent(BaseAgent):
    """Agent for collating forwarder rates and sending summary to sales personnel."""

    def __init__(self):
        super().__init__("rate_collation_agent")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate and send forwarder rates summary to sales personnel.
        
        Expected input:
        - booking_details: Confirmed booking information
        - forwarder_rates: Rates received from forwarders
        - customer_info: Customer details
        - shipment_details: Final shipment specifications
        - thread_id: Thread identifier
        """
        booking_details = input_data.get("booking_details", {})
        forwarder_rates = input_data.get("forwarder_rates", [])
        customer_info = input_data.get("customer_info", {})
        shipment_details = input_data.get("shipment_details", {})
        thread_id = input_data.get("thread_id", "")

        if not booking_details:
            return {"error": "No booking details provided"}

        if not self.client:
            return {"error": "LLM client not initialized"}

        return self._generate_final_summary(booking_details, forwarder_rates, customer_info, shipment_details, thread_id)

    def _generate_final_summary(self, booking_details: Dict[str, Any], forwarder_rates: List[Dict[str, Any]], customer_info: Dict[str, Any], shipment_details: Dict[str, Any], thread_id: str) -> Dict[str, Any]:
        """Generate final summary using LLM function calling."""
        try:
            function_schema = {
                "name": "generate_forwarder_rates_summary",
                "description": "Generate forwarder rates summary with customer booking details for sales personnel",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "summary_email": {
                            "type": "object",
                            "properties": {
                                "subject": {"type": "string"},
                                "body": {"type": "string"},
                                "priority": {"type": "string"},
                                "recipients": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                },
                                "attachments_needed": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        },
                        "booking_summary": {
                            "type": "object",
                            "properties": {
                                "total_value": {"type": "string"},
                                "profit_margin": {"type": "string"},
                                "recommended_action": {"type": "string"},
                                "risk_factors": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        },
                        "forwarder_comparison": {
                            "type": "object",
                            "properties": {
                                "best_rate": {"type": "string"},
                                "recommended_forwarder": {"type": "string"},
                                "rate_analysis": {"type": "string"}
                            }
                        }
                    }
                }
            }

            # Ensure client and config are available
            if not self.client:
                raise Exception("LLM client not initialized")
            
            model_name = self.config.get("model_name")
            if not model_name:
                raise Exception("Model name not configured")

            prompt = f"""
Generate a forwarder rates summary for sales personnel with customer booking details.

Booking Details: {json.dumps(booking_details, indent=2)}

Forwarder Rates: {json.dumps(forwarder_rates, indent=2)}

Customer Info: {json.dumps(customer_info, indent=2)}

Shipment Details: {json.dumps(shipment_details, indent=2)}

Create a professional summary email with:
- Customer booking details
- Forwarder rate comparison
- Best rate recommendation
- Customer contact information
- Shipment specifications
"""

            response = self.client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "function",
                    "function": function_schema
                }],
                tool_choice={"type": "function", "function": {"name": function_schema["name"]}},
                temperature=0.1,
                max_tokens=1000
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
            
            # Validate and correct result if needed
            if not result.get("summary_email"):
                result["summary_email"] = {
                    "subject": "Booking Summary - Action Required",
                    "body": "Summary generation failed",
                    "priority": "high",
                    "recipients": ["sales@company.com"],
                    "attachments_needed": []
                }

            self.logger.info(f"Final summary generation successful for thread: {thread_id}")
            
            return result

        except Exception as e:
            self.logger.error(f"Final summary generation failed: {e}")
            return {"error": f"Final summary generation failed: {str(e)}"}

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_rate_collation_agent():
    print("=== Testing Rate Collation Agent ===")
    agent = RateCollationAgent()
    
    if not agent.load_context():
        print("✗ Failed to load context")
        return
    
    # Test case
    test_input = {
        "booking_details": {
            "booking_id": "BK-2024-001",
            "booking_date": "2024-04-20",
            "customer_confirmed": True,
            "total_value": "$15,000",
            "payment_terms": "30 days"
        },
        "forwarder_rates": [
            {
                "forwarder_name": "DHL Global Forwarding",
                "rate": "$2,500",
                "transit_time": "15 days",
                "service_level": "premium"
            },
            {
                "forwarder_name": "Kuehne + Nagel",
                "rate": "$2,300",
                "transit_time": "18 days",
                "service_level": "standard"
            }
        ],
        "customer_info": {
            "name": "ABC Electronics",
            "email": "logistics@abcelectronics.com",
            "phone": "+1-555-0123",
            "credit_rating": "A+"
        },
        "shipment_details": {
            "origin": "Jebel Ali",
            "destination": "Mundra",
            "commodity": "electronics",
            "container_type": "40HC",
            "quantity": 2,
            "weight": "25,000 kg",
            "volume": "35 CBM"
        },
        "thread_id": "test-thread-1"
    }
    
    print(f"\n--- Testing Final Summary Generation ---")
    result = agent.run(test_input)
    
    if result.get("status") == "success":
        summary_email = result.get("summary_email", {})
        booking_summary = result.get("booking_summary", {})
        forwarder_comparison = result.get("forwarder_comparison", {})
        
        print(f"✓ Summary Email Generated:")
        print(f"   - Subject: {summary_email.get('subject')}")
        print(f"   - Priority: {summary_email.get('priority')}")
        print(f"   - Recipients: {summary_email.get('recipients')}")
        print(f"   - Body Preview: {summary_email.get('body', '')[:100]}...")
        
        print(f"\n✓ Booking Summary:")
        print(f"   - Total Value: {booking_summary.get('total_value')}")
        print(f"   - Profit Margin: {booking_summary.get('profit_margin')}")
        print(f"   - Recommended Action: {booking_summary.get('recommended_action')}")
        
        print(f"\n✓ Forwarder Comparison:")
        print(f"   - Best Rate: {forwarder_comparison.get('best_rate')}")
        print(f"   - Recommended: {forwarder_comparison.get('recommended_forwarder')}")
        
        print("✓ Final summary generation successful!")
    else:
        print(f"✗ Test failed: {result.get('error')}")

if __name__ == "__main__":
    test_rate_collation_agent() 