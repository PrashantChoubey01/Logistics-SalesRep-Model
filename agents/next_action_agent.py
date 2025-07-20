"""Next Action Agent: Determines next actions based on conversation state and extracted data using LLM."""

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

class NextActionAgent(BaseAgent):
    """Agent for determining next actions based on conversation state and data analysis."""

    def __init__(self):
        super().__init__("next_action_agent")
        
        # Available actions
        self.available_actions = [
            "send_clarification_request",
            "send_confirmation_request", 
            "assign_forwarder_and_send_rate_request",
            "collate_rates_and_send_to_sales",
            "notify_sales_team",
            "send_status_update",
            "escalate_to_human",
            "route_to_appropriate_department",
            "wait_for_forwarder_response",
            "wait_for_customer_response",
            "booking_details_confirmed_assign_forwarders"
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine next action based on conversation state and extracted data.
        
        Expected input:
        - conversation_state: Current conversation state
        - extracted_data: Extracted shipment data
        - confidence_score: Confidence in extraction/analysis
        - missing_fields: List of missing fields
        - thread_id: Thread identifier
        - latest_sender: Who sent the latest email
        """
        conversation_state = input_data.get("conversation_state", "")
        extracted_data = input_data.get("extracted_data", {})
        confidence_score = input_data.get("confidence_score", 0.0)
        missing_fields = input_data.get("missing_fields", [])
        thread_id = input_data.get("thread_id", "")
        latest_sender = input_data.get("latest_sender", "unknown")

        if not conversation_state:
            return {"error": "No conversation state provided"}

        if not self.client:
            return {"error": "LLM client not initialized"}

        return self._determine_next_action(conversation_state, extracted_data, confidence_score, missing_fields, latest_sender, thread_id)

    def _determine_next_action(self, conversation_state: str, extracted_data: Dict[str, Any], confidence_score: float, missing_fields: List[str], latest_sender: str, thread_id: str) -> Dict[str, Any]:
        """Determine next action using LLM function calling."""
        try:
            function_schema = {
                "name": "determine_next_action",
                "description": "Determine the next action based on conversation state and data analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "next_action": {
                            "type": "string",
                            "enum": self.available_actions,
                            "description": "Next action to take"
                        },
                        "action_priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Priority level for the action"
                        },
                        "escalation_needed": {
                            "type": "boolean",
                            "description": "Whether this case needs human escalation"
                        },
                        "sales_handoff_needed": {
                            "type": "boolean",
                            "description": "Whether sales team should be notified"
                        },
                        "response_type": {
                            "type": "string",
                            "enum": ["clarification", "confirmation", "status_update", "sales_notification", "escalation", "none"],
                            "description": "Type of response to generate"
                        },
                        "wait_time": {
                            "type": "integer",
                            "description": "Expected wait time in hours before next action",
                            "minimum": 0
                        },
                        "confidence_threshold": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence threshold for this action"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Detailed reasoning for the action decision"
                        },
                        "risk_factors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Risk factors that influenced the decision"
                        }
                    },
                    "required": ["next_action", "action_priority", "escalation_needed", "sales_handoff_needed", "response_type", "wait_time", "confidence_threshold", "reasoning", "risk_factors"]
                }
            }

            # Format extracted data for analysis
            data_summary = self._format_data_summary(extracted_data, missing_fields)

            prompt = f"""
You are an expert logistics workflow coordinator. Determine the next action based on the current conversation state and data analysis.

CONVERSATION STATE: {conversation_state}
LATEST SENDER: {latest_sender}
CONFIDENCE SCORE: {confidence_score:.2f}

EXTRACTED DATA SUMMARY:
{data_summary}

MISSING FIELDS: {missing_fields}

AVAILABLE ACTIONS:
1. send_clarification_request: Ask customer for missing information
2. send_confirmation_request: Present extracted data for customer confirmation
3. assign_forwarder_and_send_rate_request: Assign forwarder and request rates
4. collate_rates_and_send_to_sales: Collate forwarder rates and send to sales
5. notify_sales_team: Send case to sales team for handling
6. send_status_update: Provide status update to customer
7. escalate_to_human: Escalate complex case to human agent
8. route_to_appropriate_department: Route non-logistics emails
9. wait_for_forwarder_response: Wait for forwarder to respond
10. wait_for_customer_response: Wait for customer to respond

WORKFLOW RULES:
1. **LOW CONFIDENCE (< 0.6)**: Escalate to human immediately
2. **INCOMPLETE DATA (> 3 missing fields)**: Send clarification request to customer
3. **COMPLETE DATA (new request)**: Send confirmation request to customer
4. **CUSTOMER CONFIRMS**: Assign forwarders and send rate request emails
5. **FORWARDER RESPONDS**: Collate rates and send summary to sales
6. **UNCLEAR SITUATION**: Escalate to human

SPECIFIC DECISIONS:
- If customer gives incomplete details → send_clarification_request
- If customer gives complete details → send_confirmation_request  
- If customer confirms details → booking_details_confirmed_assign_forwarders
- If forwarder rates received → collate_rates_and_send_to_sales
- If confidence < 0.6 or unclear → escalate_to_human

PRIORITY LEVELS:
- urgent: Customer frustration, high-value deals, immediate action needed
- high: Rate inquiries, booking requests, forwarder responses
- medium: Clarification responses, confirmation replies
- low: Follow-ups, status updates

SALES HANDOFF RULES:
- Only handoff when confidence < 0.6 (low confidence requires human intervention)
- Only handoff when forwarder rates are received (forwarder_response conversation state)
- Do NOT handoff for normal confirmation replies or new requests
- Do NOT handoff for clarification responses
- Do NOT handoff for rate inquiries (unless confidence is low)

Determine the next action, priority, and whether escalation or sales handoff is needed.
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
                max_tokens=500
            )

            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if not tool_calls:
                raise Exception("No tool_calls in LLM response")

            tool_args = tool_calls[0].function.arguments
            if isinstance(tool_args, str):
                tool_args = json.loads(tool_args)

            result = dict(tool_args)
            result["decision_method"] = "llm_function_call"
            result["thread_id"] = thread_id
            result["conversation_state"] = conversation_state
            result["confidence_score"] = confidence_score
            
            # Validate and correct result if needed
            if result.get("next_action") not in self.available_actions:
                self.logger.warning(f"Invalid next_action: {result.get('next_action')}, defaulting to escalate_to_human")
                result["next_action"] = "escalate_to_human"
                result["escalation_needed"] = True

            # Ensure confidence threshold is within bounds
            confidence_threshold = result.get("confidence_threshold", 0.7)
            if not (0.0 <= confidence_threshold <= 1.0):
                result["confidence_threshold"] = max(0.0, min(1.0, confidence_threshold))

            # Ensure wait time is reasonable
            wait_time = result.get("wait_time", 24)
            if wait_time < 0:
                result["wait_time"] = 24

            self.logger.info(f"Next action determination successful: {result['next_action']} (priority: {result['action_priority']})")
            
            return result

        except Exception as e:
            self.logger.error(f"Next action determination failed: {e}")
            return {"error": f"Next action determination failed: {str(e)}"}

    def _format_data_summary(self, extracted_data: Dict[str, Any], missing_fields: List[str]) -> str:
        """Format extracted data for analysis."""
        if not extracted_data:
            return "No data extracted"
        
        summary_parts = []
        for key, value in extracted_data.items():
            if value and str(value).strip():
                summary_parts.append(f"- {key}: {value}")
        
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "No valid data extracted"

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_next_action_agent():
    print("=== Testing Next Action Agent ===")
    agent = NextActionAgent()
    
    if not agent.load_context():
        print("✗ Failed to load context")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "New Request - Complete Data",
            "conversation_state": "new_request",
            "extracted_data": {
                "origin": "Shanghai",
                "destination": "Long Beach",
                "container_type": "40GP",
                "quantity": 2,
                "ready_date": "2024-02-15"
            },
            "confidence_score": 0.85,
            "missing_fields": [],
            "latest_sender": "customer",
            "expected_action": "send_confirmation_request"
        },
        {
            "name": "New Request - Incomplete Data",
            "conversation_state": "new_request",
            "extracted_data": {
                "origin": "Shanghai",
                "destination": "Long Beach"
            },
            "confidence_score": 0.75,
            "missing_fields": ["container_type", "quantity", "ready_date"],
            "latest_sender": "customer",
            "expected_action": "send_clarification_request"
        },
        {
            "name": "Forwarder Response",
            "conversation_state": "forwarder_response",
            "extracted_data": {
                "rate_amount": 2500,
                "currency": "USD",
                "valid_until": "2024-01-15"
            },
            "confidence_score": 0.90,
            "missing_fields": [],
            "latest_sender": "forwarder",
            "expected_action": "analyze_rates_and_notify_sales"
        },
        {
            "name": "Low Confidence",
            "conversation_state": "new_request",
            "extracted_data": {},
            "confidence_score": 0.45,
            "missing_fields": ["origin", "destination", "container_type"],
            "latest_sender": "customer",
            "expected_action": "escalate_to_human"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        result = agent.run({
            "conversation_state": test_case["conversation_state"],
            "extracted_data": test_case["extracted_data"],
            "confidence_score": test_case["confidence_score"],
            "missing_fields": test_case["missing_fields"],
            "latest_sender": test_case["latest_sender"],
            "thread_id": "test-thread-1"
        })
        
        if result.get("status") == "success":
            actual_action = result.get("next_action")
            expected_action = test_case["expected_action"]
            priority = result.get("action_priority")
            escalation = result.get("escalation_needed")
            sales_handoff = result.get("sales_handoff_needed")
            
            print(f"✓ Action: {actual_action} (expected: {expected_action})")
            print(f"✓ Priority: {priority}")
            print(f"✓ Escalation: {escalation}")
            print(f"✓ Sales Handoff: {sales_handoff}")
            
            if actual_action == expected_action:
                print("✓ Action prediction correct!")
            else:
                print("✗ Action prediction incorrect")
        else:
            print(f"✗ Test failed: {result.get('error')}")

if __name__ == "__main__":
    test_next_action_agent() 