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
                        "conversation_stage": {
                            "type": "string",
                            "enum": self.conversation_states,
                            "description": "Current conversation stage based on thread analysis"
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
                    "required": ["conversation_stage", "latest_sender", "next_action", "sales_handoff_needed", "confidence_score", "conversation_progression", "key_indicators", "reasoning"]
                }
            }

            prompt = f"""
You are an expert conversation analyst for logistics operations. Analyze this email thread and determine the conversation state and next actions with high precision.

EMAIL TO ANALYZE:
Subject: {subject}
Content: {email_text}
Thread ID: {thread_id}
Thread Length: {len(message_thread)} previous emails

CONVERSATION STATES (Choose the most specific one):

1. new_thread: First email in conversation thread
   - Indicators: First contact, no previous emails, initial inquiry
   - Keywords: "need quote", "quotation", "shipping", "fcl", "lcl", "container", "freight", "cargo", "rate", "price"
   - Context: Customer making first contact for logistics services

2. thread_clarification: Customer responding to bot's clarification request
   - Indicators: Customer providing requested information, responding to questions, providing missing details
   - Keywords: "here are the missing details", "origin is", "destination is", "weight is", "date is", "commodity is", "container type is", "quantity is", "please provide the rates now"
   - Context: Customer filling in missing information previously requested by bot

3. thread_confirmation: Customer confirming booking details in thread
   - Indicators: Customer agreeing to proceed, confirming extracted data
   - Keywords: "yes, confirmed", "i confirm", "details are correct", "proceed with", "that's right", "correct"
   - Context: Customer validating extracted information and ready to proceed

4. thread_forwarder_interaction: Forwarder participating in conversation thread
   - Indicators: Forwarder providing rates, quotes, or responses
   - Keywords: "our rate", "quote is", "price is", "usd", "valid until", "freight rate", "transit time", "sailing schedule"
   - Context: Forwarder responding with rate information or service details

5. thread_rate_inquiry: Customer asking about rates in ongoing thread
   - Indicators: Customer following up on rate requests, asking for status
   - Keywords: "when will i get rates", "what about the rates", "status of my quote", "any update", "rates please"
   - Context: Customer seeking rate information or status update

6. thread_booking_request: Customer wants to proceed with booking in thread
   - Indicators: Customer ready to finalize, requesting booking process
   - Keywords: "i want to book", "proceed with booking", "ready to book", "confirm booking", "let's book", "go ahead"
   - Context: Customer ready to finalize the shipment booking

7. thread_followup: Customer sending follow-up in thread
   - Indicators: General follow-up without specific action needed
   - Keywords: "following up", "reminder", "update", "status", "checking in"
   - Context: Customer checking status or following up on previous communication

8. thread_escalation: Complex thread or customer frustration
   - Indicators: High urgency, frustration, or complex requirements
   - Keywords: "urgent", "asap", "immediately", "frustrated", "not getting response", "emergency", "critical"
   - Context: High-priority or complex cases requiring immediate attention

9. thread_sales_notification: Bot notifying sales team in thread
   - Indicators: Internal communication to sales team
   - Context: Bot escalating or notifying sales team about the case

10. thread_non_logistics: Not related to logistics in thread
    - Indicators: General business, personal, or marketing content
    - Context: Non-logistics related communication

11. thread_continuation: Ongoing conversation without specific action
    - Indicators: General continuation without clear next step
    - Context: Ongoing conversation that needs further analysis

12. thread_completion: Conversation reaching conclusion
    - Indicators: Thread ending, successful completion
    - Context: Conversation successfully concluded

NEXT ACTIONS (Choose the most appropriate):

- send_clarification_request: Ask customer for missing required information (origin, destination, container type, commodity, quantity for FCL; weight/volume for LCL)
- send_confirmation_request: Present extracted data for customer confirmation when all required fields are present
- assign_forwarder_and_send_rate_request: Assign forwarder and request rates when customer data is complete
- analyze_rates_and_notify_sales: Analyze forwarder rates and notify sales team when rates are received
- notify_sales_team: Send case to sales team for handling complex cases or rate inquiries
- send_status_update: Provide status update to customer about their request
- escalate_to_human: Escalate complex case to human agent when automation cannot handle
- route_to_appropriate_department: Route non-logistics emails to appropriate department

SALES HANDOFF RULES:
- Handoff when forwarder rates are received and need analysis
- Handoff when customer asks about rates or booking
- Handoff when customer expresses frustration or urgency
- Handoff when complex requirements cannot be handled by bot
- Handoff when customer requests human assistance

ANALYSIS GUIDELINES:
1. Consider the full context of the email thread
2. Look for specific keywords and phrases that indicate intent
3. Analyze the progression of the conversation
4. Consider the sender type (customer vs forwarder)
5. Evaluate the completeness of information provided
6. Assess urgency and complexity of the request
7. Determine if human intervention is needed

**SPECIAL ATTENTION TO CLARIFICATION RESPONSES:**
- If customer says "here are the missing details" or "please provide the rates now" → thread_clarification
- If customer provides specific information like "Destination: Los Angeles, USA" → thread_clarification
- If customer asks for rates after providing information → thread_clarification

Provide detailed reasoning for your analysis and identify key indicators that influenced your decision.
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
            if result.get("conversation_stage") not in self.conversation_states:
                self.logger.warning(f"Invalid conversation_stage: {result.get('conversation_stage')}, defaulting to new_thread")
                result["conversation_stage"] = "new_thread"
                result["confidence_score"] = 0.5

            # Ensure confidence is within bounds
            confidence = result.get("confidence_score", 0.5)
            if not (0.0 <= confidence <= 1.0):
                result["confidence_score"] = max(0.0, min(1.0, confidence))

            self.logger.info(f"Conversation state analysis successful: {result['conversation_stage']} (confidence: {result['confidence_score']:.2f})")
            
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
            "expected_state": "new_thread"
        },
        {
            "name": "Clarification Response",
            "subject": "Re: Clarification needed",
            "email_text": "Origin is Shanghai, destination is Long Beach. Weight is 25 tons. Commodity is electronics.",
            "expected_state": "thread_clarification"
        },
        {
            "name": "Forwarder Response",
            "subject": "Re: Rate Request - Shanghai to Long Beach",
            "email_text": "Our rate is USD 2,500 per container. Valid until January 15th. Transit time 25 days.",
            "expected_state": "thread_forwarder_interaction"
        },
        {
            "name": "Rate Inquiry",
            "subject": "Re: When will I get the rates?",
            "email_text": "Hi, I confirmed the details yesterday. When can I expect the rates?",
            "expected_state": "thread_rate_inquiry"
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
            actual_state = result.get("conversation_stage")
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