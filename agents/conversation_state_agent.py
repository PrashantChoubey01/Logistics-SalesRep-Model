"""Conversation State Agent: Analyzes email threads to determine conversation state and next actions using LLM."""

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

class ConversationStateAgent(BaseAgent):
    """Agent for analyzing email thread conversation state and determining next actions."""

    def __init__(self):
        super().__init__("conversation_state_agent")
        
        # Conversation states - Focus on THREAD PROGRESSION
        self.conversation_states = [
            "new_thread",                    # First email in conversation
            "thread_continuation",           # Ongoing conversation
            "thread_clarification",          # Customer responding to bot questions
            "thread_confirmation",           # Customer confirming bot's extracted data
            "thread_forwarder_interaction",  # Forwarder participating in conversation
            "thread_rate_inquiry",           # Customer asking about rates in thread
            "thread_booking_request",        # Customer wants to proceed with booking
            "thread_followup",               # Customer following up in thread
            "thread_escalation",             # Complex thread needing human
            "thread_completion",             # Conversation reaching conclusion
            "thread_sales_notification",     # Bot notifying sales in thread
            "thread_non_logistics"           # Non-logistics thread
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze email thread and determine conversation state and next actions.
        
        Expected input:
        - email_text: Full email thread content
        - subject: Email subject
        - thread_id: Thread identifier
        - message_thread: List of message dictionaries (optional)
        """
        email_text = input_data.get("email_text", "").strip()
        subject = input_data.get("subject", "").strip()
        thread_id = input_data.get("thread_id", "")
        message_thread = input_data.get("message_thread", [])

        if not email_text:
            return {"error": "No email text provided"}

        if not self.client:
            return {"error": "LLM client not initialized"}

        return self._analyze_conversation_state(subject, email_text, message_thread, thread_id)

    def _analyze_conversation_state(self, subject: str, email_text: str, message_thread: List[Dict[str, Any]], thread_id: str) -> Dict[str, Any]:
        """Analyze conversation state using LLM function calling."""
        try:
            function_schema = {
                "name": "analyze_conversation_state",
                "description": "Analyze email thread conversation state and determine next actions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "conversation_state": {
                            "type": "string",
                            "enum": self.conversation_states,
                            "description": "Current conversation state based on thread analysis"
                        },
                        "thread_context": {
                            "type": "object",
                            "properties": {
                                "is_thread": {"type": "boolean", "description": "Whether this is part of an email thread"},
                                "email_count": {"type": "integer", "description": "Number of emails in the thread"},
                                "has_bot_response": {"type": "boolean", "description": "Whether bot has already responded in this thread"},
                                "conversation_progression": {"type": "string", "description": "How the conversation has progressed (new request, clarification, confirmation, etc.)"},
                                "missing_information": {"type": "array", "items": {"type": "string"}, "description": "Information still missing from customer"},
                                "previous_topics": {"type": "array", "items": {"type": "string"}, "description": "Topics discussed in previous emails"}
                            },
                            "description": "Analysis of email thread context and progression"
                        },
                        "latest_sender": {
                            "type": "string",
                            "enum": ["customer", "forwarder", "sales_team", "bot", "unknown"],
                            "description": "Who sent the latest email in the thread"
                        },
                        "next_action": {
                            "type": "string",
                            "enum": [
                                "send_clarification_request",
                                "send_confirmation_request", 
                                "assign_forwarder_and_send_rate_request",
                                "analyze_rates_and_notify_sales",
                                "notify_sales_team",
                                "send_status_update",
                                "escalate_to_human",
                                "route_to_appropriate_department"
                            ],
                            "description": "Next action to take based on current state"
                        },
                        "sales_handoff_needed": {
                            "type": "boolean",
                            "description": "Whether this case needs to be handed off to sales team"
                        },
                        "confidence_score": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence in the analysis (0.0 to 1.0)"
                        },
                        "conversation_progression": {
                            "type": "string",
                            "description": "Brief description of conversation progression"
                        },
                        "key_indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key phrases/words that influenced the analysis"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Detailed reasoning for the analysis"
                        }
                    },
                    "required": ["conversation_state", "latest_sender", "next_action", "sales_handoff_needed", "confidence_score", "conversation_progression", "key_indicators", "reasoning"]
                }
            }

            prompt = f"""
You are an expert conversation analyst for logistics operations. Analyze this email thread and determine the conversation state and next actions.

CONVERSATION STATES:
1. new_thread: First email in conversation thread
   - Keywords: "need quote", "quotation", "shipping", "fcl", "lcl", "container", "freight", "cargo"
   - First contact in thread

2. thread_clarification: Customer responding to bot's clarification request
   - Keywords: "origin is", "destination is", "weight is", "date is", "commodity is"
   - Providing requested information in thread context

3. thread_confirmation: Customer confirming booking details in thread
   - Keywords: "yes, confirmed", "i confirm", "details are correct", "proceed with"
   - Confirming extracted information in thread context

4. thread_forwarder_interaction: Forwarder participating in conversation thread
   - Keywords: "our rate", "quote is", "price is", "usd", "valid until", "freight rate"
   - From forwarder email addresses in thread

5. thread_rate_inquiry: Customer asking about rates in ongoing thread
   - Keywords: "when will i get rates", "what about the rates", "status of my quote"
   - Customer following up on rates in thread

6. thread_booking_request: Customer wants to proceed with booking in thread
   - Keywords: "i want to book", "proceed with booking", "ready to book", "confirm booking"
   - Customer ready to finalize in thread context

7. thread_followup: Customer sending follow-up in thread
   - Keywords: "following up", "reminder", "update", "status"
   - General follow-up messages in thread

8. thread_escalation: Complex thread or customer frustration
   - Keywords: "urgent", "asap", "immediately", "frustrated", "not getting response"
   - High urgency or frustration indicators in thread

9. thread_sales_notification: Bot notifying sales team in thread
   - Internal communication to sales team in thread context

10. thread_non_logistics: Not related to logistics in thread
    - General business, personal, or marketing emails in thread

11. thread_continuation: Ongoing conversation without specific action
    - General continuation of thread conversation

12. thread_completion: Conversation reaching conclusion
    - Thread ending or completing successfully

NEXT ACTIONS:
- send_clarification_request: Ask customer for missing information
- send_confirmation_request: Present extracted data for customer confirmation
- assign_forwarder_and_send_rate_request: Assign forwarder and request rates
- analyze_rates_and_notify_sales: Analyze forwarder rates and notify sales team
- notify_sales_team: Send case to sales team for handling
- send_status_update: Provide status update to customer
- escalate_to_human: Escalate complex case to human agent
- route_to_appropriate_department: Route non-logistics emails

SALES HANDOFF RULES:
- Always handoff when forwarder rates are received
- Handoff when customer asks about rates or booking
- Handoff for complex cases or escalations
- Handoff when customer wants to proceed with booking

EMAIL THREAD ANALYSIS INSTRUCTIONS:
1. **Thread Detection**: Look for email separators (---, "Previous Conversation:", "From:", timestamps)
2. **Conversation Flow**: Analyze how the conversation has progressed
3. **Context Extraction**: Identify what information has been exchanged
4. **Missing Information**: Determine what details are still needed
5. **Bot Interaction**: Check if bot has already responded and what was said
6. **Customer Intent**: Understand what the customer wants to achieve

ANALYSIS FACTORS:
- Email thread content and progression
- Sender identification (customer/forwarder/sales)
- Keywords and phrases used
- Urgency indicators
- Conversation flow patterns
- Response patterns (Re:, answering questions)
- Thread length and complexity

EMAIL TO ANALYZE:
Subject: {subject}
Thread Content: {email_text}

IMPORTANT: Analyze the ENTIRE email thread, not just the latest email. Consider the conversation history and progression to make intelligent decisions about the current state and next action.

Analyze this email thread and determine the conversation state, next action, and whether sales handoff is needed.
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
            result["analysis_method"] = "llm_function_call"
            result["thread_id"] = thread_id
            
            # Validate and correct result if needed
            if result.get("conversation_state") not in self.conversation_states:
                self.logger.warning(f"Invalid conversation_state: {result.get('conversation_state')}, defaulting to new_request")
                result["conversation_state"] = "new_request"
                result["confidence_score"] = 0.5

            # Ensure confidence is within bounds
            confidence = result.get("confidence_score", 0.5)
            if not (0.0 <= confidence <= 1.0):
                result["confidence_score"] = max(0.0, min(1.0, confidence))

            self.logger.info(f"Conversation state analysis successful: {result['conversation_state']} (confidence: {result['confidence_score']:.2f})")
            
            return result

        except Exception as e:
            self.logger.error(f"Conversation state analysis failed: {e}")
            return {"error": f"Conversation state analysis failed: {str(e)}"}

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_conversation_state_agent():
    print("=== Testing Conversation State Agent ===")
    agent = ConversationStateAgent()
    
    if not agent.load_context():
        print("✗ Failed to load context")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "New Logistics Request",
            "subject": "Need quote for FCL shipment",
            "email_text": "Hi, I need to ship 2x40ft containers from Shanghai to Long Beach. Ready date is February 15th. Please provide rates.",
            "expected_state": "new_request"
        },
        {
            "name": "Clarification Response",
            "subject": "Re: Clarification needed",
            "email_text": "Origin is Shanghai, destination is Long Beach. Weight is 25 tons. Commodity is electronics.",
            "expected_state": "clarification_response"
        },
        {
            "name": "Forwarder Response",
            "subject": "Re: Rate Request - Shanghai to Long Beach",
            "email_text": "Our rate is USD 2,500 per container. Valid until January 15th. Transit time 25 days.",
            "expected_state": "forwarder_response"
        },
        {
            "name": "Rate Inquiry",
            "subject": "Re: When will I get the rates?",
            "email_text": "Hi, I confirmed the details yesterday. When can I expect the rates?",
            "expected_state": "rate_inquiry"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        result = agent.run({
            "email_text": test_case["email_text"],
            "subject": test_case["subject"],
            "thread_id": "test-thread-1"
        })
        
        if result.get("status") == "success":
            actual_state = result.get("conversation_state")
            expected_state = test_case["expected_state"]
            confidence = result.get("confidence_score", 0.0)
            next_action = result.get("next_action")
            sales_handoff = result.get("sales_handoff_needed")
            
            print(f"✓ State: {actual_state} (expected: {expected_state})")
            print(f"✓ Confidence: {confidence:.2f}")
            print(f"✓ Next Action: {next_action}")
            print(f"✓ Sales Handoff: {sales_handoff}")
            
            if actual_state == expected_state:
                print("✓ State prediction correct!")
            else:
                print("✗ State prediction incorrect")
        else:
            print(f"✗ Test failed: {result.get('error')}")

if __name__ == "__main__":
    test_conversation_state_agent() 