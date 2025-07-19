"""Sales Notification Agent: Generates sales team notifications and deal summaries using LLM."""

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

class SalesNotificationAgent(BaseAgent):
    """Agent for generating sales team notifications and deal summaries."""

    def __init__(self):
        super().__init__("sales_notification_agent")
        
        # Notification types
        self.notification_types = [
            "rates_received",
            "customer_rate_inquiry",
            "customer_booking_request",
            "escalation",
            "deal_update",
            "deal_closure"
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate sales team notification based on case details.
        
        Expected input:
        - notification_type: Type of notification
        - customer_details: Customer information
        - shipment_details: Shipment information
        - forwarder_rates: Forwarder rates (if available)
        - conversation_state: Current conversation state
        - thread_id: Thread identifier
        - urgency: Urgency level
        """
        notification_type = input_data.get("notification_type", "")
        customer_details = input_data.get("customer_details", {})
        shipment_details = input_data.get("shipment_details", {})
        forwarder_rates = input_data.get("forwarder_rates", [])
        conversation_state = input_data.get("conversation_state", "")
        thread_id = input_data.get("thread_id", "")
        urgency = input_data.get("urgency", "medium")

        if not notification_type:
            return {"error": "No notification type provided"}

        if not self.client:
            return {"error": "LLM client not initialized"}

        return self._generate_sales_notification(notification_type, customer_details, shipment_details, forwarder_rates, conversation_state, thread_id, urgency)

    def _generate_sales_notification(self, notification_type: str, customer_details: Dict[str, Any], shipment_details: Dict[str, Any], forwarder_rates: List[Dict[str, Any]], conversation_state: str, thread_id: str, urgency: str) -> Dict[str, Any]:
        """Generate sales notification using LLM function calling."""
        try:
            function_schema = {
                "name": "generate_sales_notification",
                "description": "Generate sales team notification with deal summary and recommendations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subject": {
                            "type": "string",
                            "description": "Email subject line for sales notification"
                        },
                        "body": {
                            "type": "string",
                            "description": "Email body content for sales notification"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Priority level for the notification"
                        },
                        "deal_value_estimate": {
                            "type": "number",
                            "description": "Estimated deal value in USD"
                        },
                        "next_action_required": {
                            "type": "string",
                            "description": "Specific action required from sales team"
                        },
                        "customer_contact_info": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "email": {"type": "string"},
                                "company": {"type": "string"},
                                "phone": {"type": "string"}
                            },
                            "description": "Customer contact information"
                        },
                        "key_highlights": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key points to highlight for sales team"
                        },
                        "risk_factors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Risk factors or concerns to consider"
                        },
                        "recommendations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Recommendations for sales team"
                        }
                    },
                    "required": ["subject", "body", "priority", "deal_value_estimate", "next_action_required", "customer_contact_info", "key_highlights", "risk_factors", "recommendations"]
                }
            }

            # Format data for analysis
            customer_summary = self._format_customer_summary(customer_details)
            shipment_summary = self._format_shipment_summary(shipment_details)
            rates_summary = self._format_rates_summary(forwarder_rates)

            prompt = f"""
You are an expert sales coordinator for logistics operations. Generate a comprehensive sales team notification.

NOTIFICATION TYPE: {notification_type}
CONVERSATION STATE: {conversation_state}
URGENCY: {urgency}

CUSTOMER DETAILS:
{customer_summary}

SHIPMENT DETAILS:
{shipment_summary}

FORWARDER RATES:
{rates_summary}

NOTIFICATION TYPES:
1. rates_received: Forwarder has sent rates, ready for customer presentation
2. customer_rate_inquiry: Customer is asking about rates or status
3. customer_booking_request: Customer wants to proceed with booking
4. escalation: Complex case or customer frustration
5. deal_update: General update on deal progress
6. deal_closure: Deal has been closed or finalized

PRIORITY LEVELS:
- urgent: Customer frustration, high-value deals, immediate action needed
- high: Rate inquiries, booking requests, forwarder responses
- medium: Deal updates, general inquiries
- low: Follow-ups, status updates

GENERATE:
- Professional subject line
- Comprehensive email body with all relevant details
- Priority level based on urgency and deal value
- Estimated deal value
- Specific next action required
- Customer contact information
- Key highlights for sales team
- Risk factors to consider
- Recommendations for handling

Make the notification actionable and provide all necessary information for the sales team to take immediate action.
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
            result["notification_method"] = "llm_function_call"
            result["thread_id"] = thread_id
            result["notification_type"] = notification_type
            result["conversation_state"] = conversation_state
            
            # Validate and correct result if needed
            if result.get("priority") not in ["low", "medium", "high", "urgent"]:
                result["priority"] = "medium"

            # Ensure deal value is reasonable
            deal_value = result.get("deal_value_estimate", 0)
            if deal_value < 0:
                result["deal_value_estimate"] = 0

            self.logger.info(f"Sales notification generated successfully: {notification_type} (priority: {result['priority']})")
            
            return result

        except Exception as e:
            self.logger.error(f"Sales notification generation failed: {e}")
            return {"error": f"Sales notification generation failed: {str(e)}"}

    def _format_customer_summary(self, customer_details: Dict[str, Any]) -> str:
        """Format customer details for analysis."""
        if not customer_details:
            return "No customer details available"
        
        summary_parts = []
        for key, value in customer_details.items():
            if value and str(value).strip():
                summary_parts.append(f"- {key}: {value}")
        
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "No customer details available"

    def _format_shipment_summary(self, shipment_details: Dict[str, Any]) -> str:
        """Format shipment details for analysis."""
        if not shipment_details:
            return "No shipment details available"
        
        summary_parts = []
        for key, value in shipment_details.items():
            if value and str(value).strip():
                summary_parts.append(f"- {key}: {value}")
        
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "No shipment details available"

    def _format_rates_summary(self, forwarder_rates: List[Dict[str, Any]]) -> str:
        """Format forwarder rates for analysis."""
        if not forwarder_rates:
            return "No forwarder rates available"
        
        summary_parts = []
        for i, rate in enumerate(forwarder_rates, 1):
            rate_parts = []
            for key, value in rate.items():
                if value and str(value).strip():
                    rate_parts.append(f"{key}: {value}")
            if rate_parts:
                summary_parts.append(f"Rate {i}: {', '.join(rate_parts)}")
        
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "No forwarder rates available"

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_sales_notification_agent():
    print("=== Testing Sales Notification Agent ===")
    agent = SalesNotificationAgent()
    
    if not agent.load_context():
        print("✗ Failed to load context")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "Rates Received",
            "notification_type": "rates_received",
            "customer_details": {
                "name": "John Smith",
                "email": "john@abc.com",
                "company": "ABC Electronics"
            },
            "shipment_details": {
                "origin": "Shanghai",
                "destination": "Long Beach",
                "container_type": "40GP",
                "quantity": 2
            },
            "forwarder_rates": [
                {
                    "forwarder": "DHL Global Forwarding",
                    "rate": 2500,
                    "currency": "USD",
                    "valid_until": "2024-01-15"
                }
            ],
            "conversation_state": "forwarder_response",
            "urgency": "high"
        },
        {
            "name": "Customer Rate Inquiry",
            "notification_type": "customer_rate_inquiry",
            "customer_details": {
                "name": "Sarah Johnson",
                "email": "sarah@xyz.com",
                "company": "XYZ Trading"
            },
            "shipment_details": {
                "origin": "Hamburg",
                "destination": "New York",
                "container_type": "20GP",
                "quantity": 1
            },
            "forwarder_rates": [],
            "conversation_state": "rate_inquiry",
            "urgency": "medium"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        result = agent.run({
            "notification_type": test_case["notification_type"],
            "customer_details": test_case["customer_details"],
            "shipment_details": test_case["shipment_details"],
            "forwarder_rates": test_case["forwarder_rates"],
            "conversation_state": test_case["conversation_state"],
            "thread_id": "test-thread-1",
            "urgency": test_case["urgency"]
        })
        
        if result.get("status") == "success":
            subject = result.get("subject")
            priority = result.get("priority")
            deal_value = result.get("deal_value_estimate")
            next_action = result.get("next_action_required")
            
            print(f"✓ Subject: {subject}")
            print(f"✓ Priority: {priority}")
            print(f"✓ Deal Value: ${deal_value}")
            print(f"✓ Next Action: {next_action}")
            print(f"✓ Body Length: {len(result.get('body', ''))} characters")
        else:
            print(f"✗ Test failed: {result.get('error')}")

if __name__ == "__main__":
    test_sales_notification_agent() 