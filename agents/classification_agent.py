"""Classification Agent: Categorizes email types for logistics workflow routing using LLM function calling."""

import json
import sys
import os
from typing import Dict, Any, List

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class ClassificationAgent(BaseAgent):
    """Agent for classifying email types and determining workflow routing using LLM only."""

    def __init__(self):
        super().__init__("classification_agent")
        
        # Email classification categories - Focus on EMAIL CONTENT
        self.email_types = [
            "customer_quote_request",     # Customer asking for shipping rates/quote
            "customer_confirmation",      # Customer saying yes/confirming details
            "customer_clarification",     # Customer providing missing information
            "customer_rate_inquiry",      # Customer asking about rates status
            "customer_booking_request",   # Customer wants to proceed with booking
            "customer_followup",          # Customer following up or reminder
            "forwarder_rate_quote",       # Forwarder providing rates/quote
            "forwarder_inquiry",          # Forwarder asking for more details
            "forwarder_acknowledgment",   # Forwarder acknowledging request
            "sales_notification",         # Internal sales team communication
            "confusing_email",            # Unclear, ambiguous, or mixed intent email
            "non_logistics"               # Not related to shipping/logistics
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify email type and determine urgency for workflow routing with thread support.
        
        Expected input:
        - message_thread: List of message dictionaries (preferred)
        - email_text: Raw email content (fallback for backward compatibility)
        - subject: Email subject line (required)
        - thread_id: Optional thread identifier
        """
        message_thread = input_data.get("message_thread", [])
        email_text = input_data.get("email_text", "").strip()
        subject = input_data.get("subject", "").strip()
        thread_id = input_data.get("thread_id", "")

        if not self.client:
            return {"error": "LLM client not initialized"}

        # Use thread if available, otherwise fall back to single email
        if message_thread:
            return self._llm_thread_classification(subject, message_thread, thread_id)
        elif email_text:
            return self._llm_classification(subject, email_text, thread_id)
        else:
            return {"error": "No email text or message thread provided"}

    def _llm_classification(self, subject: str, email_text: str, thread_id: str) -> Dict[str, Any]:
        """Classify using LLM function calling for guaranteed structured output"""
        try:
            function_schema = {
                "name": "classify_email",
                "description": "Classify email into logistics categories and determine workflow routing",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_type": {
                            "type": "string",
                            "enum": self.email_types,
                            "description": "Primary email category"
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Classification confidence score (0.0 to 1.0)"
                        },
                        "urgency": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Processing urgency level"
                        },
                        "requires_action": {
                            "type": "boolean",
                            "description": "Whether email requires immediate processing"
                        },
                        "key_indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key phrases/words that influenced classification"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Brief explanation for classification decision"
                        }
                    },
                    "required": ["email_type", "confidence", "urgency", "requires_action", "key_indicators", "reasoning"]
                }
            }

            prompt = f"""
You are an expert email classifier for logistics operations. Analyze this email and classify it accurately.

EMAIL CATEGORIES:
1. customer_quote_request: Customer requesting shipping quote, service, or logistics information
   - Keywords: "need quote", "quotation", "shipping", "fcl", "lcl", "container", "freight", "cargo", "rate", "price", "cost", "shipment", "transport", "logistics"
   - Examples: "Need quote for FCL", "Shipping request", "Rate for container", "How much for shipping", "Cost for freight"
   - Context: First-time requests, new inquiries, asking for pricing

2. customer_confirmation: Customer confirming/accepting a proposal, booking, or agreement
   - Keywords: "yes", "confirm", "confirmed", "accept", "approved", "agreed", "proceed", "go ahead", "okay", "fine", "good", "perfect", "correct", "right"
   - Examples: "Yes, confirmed", "I accept the quote", "Proceed with booking", "All details are correct", "Please proceed"
   - Context: Responding to confirmation requests, accepting proposals, agreeing to terms

3. customer_clarification: Customer providing requested information or answering questions
   - Keywords: "origin is", "destination is", "port is", "date is", "weight is", "container is", "commodity is", "the origin", "the destination", "shipment date", "ready date"
   - Examples: "Origin is Shanghai", "The weight is 25 tons", "Departure date is...", "Container type is 40HC", "Commodity is electronics"
   - Context: Providing missing information, answering specific questions, filling gaps

4. customer_rate_inquiry: Customer asking about rates or booking status
   - Keywords: "when will i get rates", "what about the rates", "status of my quote", "any update", "when can i expect"
   - Examples: "When will I get the rates?", "Any update on my quote?", "Status of my booking request"
   - Context: Following up on previous requests, checking status

5. customer_booking_request: Customer wants to proceed with booking
   - Keywords: "i want to book", "proceed with booking", "ready to book", "confirm booking", "let's book", "go ahead with booking"
   - Examples: "I want to proceed with the booking", "Ready to book the shipment", "Let's confirm the booking"
   - Context: Customer ready to finalize transaction

6. customer_followup: Customer sending follow-up or reminder
   - Keywords: "following up", "reminder", "update", "status", "checking in", "touch base"
   - Examples: "Following up on my request", "Just checking the status", "Any updates?"
   - Context: General follow-up messages

7. forwarder_rate_quote: Freight forwarder providing rates, quotes, or shipping information
   - Keywords: "our rate", "quote is", "price is", "usd", "valid until", "freight rate", "attached", "please find", "as requested", "quotation", "offer", "proposal"
   - Examples: "Our rate is $2500", "Quote attached", "Valid until Friday", "Please find our quotation", "As requested, here is our offer"
   - Context: Professional responses with pricing, quotes, or shipping information from logistics companies

8. forwarder_inquiry: Forwarder asking for more details or clarification
   - Keywords: "need more details", "additional information", "clarification needed", "please provide", "missing information"
   - Examples: "Need more details about the shipment", "Please provide additional information", "Clarification needed on commodity"
   - Context: Forwarder requesting more information

9. forwarder_acknowledgment: Forwarder acknowledging request
   - Keywords: "received your request", "acknowledging", "thank you for", "we have received", "processing your request"
   - Examples: "Received your rate request", "Thank you for your inquiry", "We are processing your request"
   - Context: Forwarder acknowledging receipt of request

10. sales_notification: Internal sales team communication
    - Keywords: "sales team", "internal", "notify", "handoff", "escalation"
    - Examples: "Notifying sales team", "Internal handoff", "Sales escalation"
    - Context: Internal communication to sales team

11. confusing_email: Unclear, ambiguous, or mixed intent email that needs human review
    - Vague responses: "ok", "thanks", "will check", "let me see", "maybe", "not sure", "thinking", "considering"
    - Mixed signals: Both confirmation and new requests in same email
    - Unclear context: Missing key information, ambiguous language
    - Examples: "Ok, thanks", "Will check and get back", "Let me think about it", "Maybe later", "Not sure yet"

12. non_logistics: Not related to shipping, logistics, or freight operations
    - Examples: Meeting invites, general business, personal messages, marketing emails, newsletters
    - Context: No logistics keywords, unrelated business content

THREAD-AWARE ANALYSIS FACTORS:
- **Intent and Context**: Analyze the message within the conversation flow
- **Keywords and Phrases**: Look for logistics terms across the entire thread
- **Urgency Indicators**: "urgent", "ASAP", "deadline", "immediate", "rush", "priority"
- **Action Requirements**: "confirm", "book", "proceed", "quote", "approve", "accept"
- **Response Patterns**: "Re:", "answering questions", "providing information", "responding to"
- **Conversation Progression**: What was discussed before and what the customer is responding to
- **Sender Identification**: Customer vs Forwarder vs Sales team vs System
- **Previous Bot Interactions**: What the bot asked for and how the customer is responding
- **Email Structure**: Subject line patterns, quoted text, thread history
- **Confirmation Context**: If bot asked for confirmation, customer's response should be classified accordingly

IMPORTANT CLASSIFICATION RULES:
- **Confirmation Priority**: If the bot previously asked for confirmation and customer responds with "yes", "confirm", "correct", "proceed", classify as "confirmation_reply"
- **Context Matters**: Consider the entire email thread, not just the latest message
- **Forwarder Detection**: Look for professional language, pricing, quotes, and logistics company signatures
- **Clarification Detection**: If customer is providing specific information (ports, dates, weights) in response to bot questions, classify as "clarification_reply"
- **Vague Responses**: If email contains only "ok", "thanks", "will check", "maybe" without clear intent, classify as "confusing_email"
- **Logistics Keywords**: Must contain logistics-related terms for "logistics_request" classification
- **Subject vs Content**: Subject line can provide context but content is primary
- **Thread History**: Previous messages in the thread provide crucial context for classification
- **Response Patterns**: "Re:" emails often indicate responses to previous questions or requests

EMAIL TO CLASSIFY:
Subject: {subject}
Body: {email_text}

Classify this email accurately, determine urgency level, and provide your reasoning with key indicators.
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
            result["classification_method"] = "llm_function_call"
            result["thread_id"] = thread_id
            
            # Validate and correct result if needed
            if result.get("email_type") not in self.email_types:
                self.logger.warning(f"Invalid email_type: {result.get('email_type')}, defaulting to non_logistics")
                result["email_type"] = "non_logistics"
                result["confidence"] = 0.5
                result["reasoning"] += " (corrected invalid type)"

            # Ensure confidence is within bounds
            confidence = result.get("confidence", 0.5)
            if not (0.0 <= confidence <= 1.0):
                result["confidence"] = max(0.0, min(1.0, confidence))

            self.logger.info(f"LLM function calling successful: {result['email_type']} (confidence: {result['confidence']:.2f})")
            
            return result

        except Exception as e:
            self.logger.error(f"LLM classification failed: {e}")
            return {"error": f"LLM classification failed: {str(e)}"}

    def _llm_thread_classification(self, subject: str, message_thread: List[Dict[str, Any]], thread_id: str) -> Dict[str, Any]:
        """Classify using LLM function calling with full thread analysis"""
        try:
            function_schema = {
                "name": "classify_email_thread",
                "description": "Classify email thread into logistics categories and determine workflow routing",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_type": {
                            "type": "string",
                            "enum": self.email_types,
                            "description": "Primary email category based on thread analysis"
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Classification confidence score (0.0 to 1.0)"
                        },
                        "urgency": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Processing urgency level"
                        },
                        "requires_action": {
                            "type": "boolean",
                            "description": "Whether email requires immediate processing"
                        },
                        "key_indicators": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key phrases/words that influenced classification"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Brief explanation for classification decision"
                        },
                        "classification_message_index": {
                            "type": "integer",
                            "description": "Index of the message that most influenced classification (0-based)"
                        }
                    },
                    "required": ["email_type", "confidence", "urgency", "requires_action", "key_indicators", "reasoning", "classification_message_index"]
                }
            }

            # Format thread for analysis
            thread_text = self._format_thread_for_analysis(message_thread)

            prompt = f"""
You are an expert email classifier for logistics operations. Analyze this entire email thread and classify it accurately.

EMAIL CATEGORIES:
1. customer_quote_request: Customer requesting shipping quote, service, or logistics information
   - Keywords: "need quote", "quotation", "shipping", "fcl", "lcl", "container", "freight", "cargo", "rate", "price", "cost", "shipment", "transport", "logistics"
   - Examples: "Need quote for FCL", "Shipping request", "Rate for container", "How much for shipping", "Cost for freight"
   - Context: First-time requests, new inquiries, asking for pricing

2. customer_confirmation: Customer confirming/accepting a proposal, booking, or agreement
   - Keywords: "yes", "confirm", "confirmed", "accept", "approved", "agreed", "proceed", "go ahead", "okay", "fine", "good", "perfect", "correct", "right"
   - Examples: "Yes, confirmed", "I accept the quote", "Proceed with booking", "All details are correct", "Please proceed"
   - Context: Responding to confirmation requests, accepting proposals, agreeing to terms

3. customer_clarification: Customer providing requested information or answering questions
   - Keywords: "origin is", "destination is", "port is", "date is", "weight is", "container is", "commodity is", "the origin", "the destination", "shipment date", "ready date"
   - Examples: "Origin is Shanghai", "The weight is 25 tons", "Departure date is...", "Container type is 40HC", "Commodity is electronics"
   - Context: Providing missing information, answering specific questions, filling gaps

4. customer_rate_inquiry: Customer asking about rates or booking status
   - Keywords: "when will i get rates", "what about the rates", "status of my quote", "any update", "when can i expect"
   - Examples: "When will I get the rates?", "Any update on my quote?", "Status of my booking request"
   - Context: Following up on previous requests, checking status

5. customer_booking_request: Customer wants to proceed with booking
   - Keywords: "i want to book", "proceed with booking", "ready to book", "confirm booking", "let's book", "go ahead with booking"
   - Examples: "I want to proceed with the booking", "Ready to book the shipment", "Let's confirm the booking"
   - Context: Customer ready to finalize transaction

6. customer_followup: Customer sending follow-up or reminder
   - Keywords: "following up", "reminder", "update", "status", "checking in", "touch base"
   - Examples: "Following up on my request", "Just checking the status", "Any updates?"
   - Context: General follow-up messages

7. forwarder_rate_quote: Freight forwarder providing rates, quotes, or shipping information
   - Keywords: "our rate", "quote is", "price is", "usd", "valid until", "freight rate", "attached", "please find", "as requested", "quotation", "offer", "proposal"
   - Examples: "Our rate is $2500", "Quote attached", "Valid until Friday", "Please find our quotation", "As requested, here is our offer"
   - Context: Professional responses with pricing, quotes, or shipping information from logistics companies

8. forwarder_inquiry: Forwarder asking for more details or clarification
   - Keywords: "need more details", "additional information", "clarification needed", "please provide", "missing information"
   - Examples: "Need more details about the shipment", "Please provide additional information", "Clarification needed on commodity"
   - Context: Forwarder requesting more information

9. forwarder_acknowledgment: Forwarder acknowledging request
   - Keywords: "received your request", "acknowledging", "thank you for", "we have received", "processing your request"
   - Examples: "Received your rate request", "Thank you for your inquiry", "We are processing your request"
   - Context: Forwarder acknowledging receipt of request

10. sales_notification: Internal sales team communication
    - Keywords: "sales team", "internal", "notify", "handoff", "escalation"
    - Examples: "Notifying sales team", "Internal handoff", "Sales escalation"
    - Context: Internal communication to sales team

11. confusing_email: Unclear, ambiguous, or mixed intent email that needs human review
    - Vague responses: "ok", "thanks", "will check", "let me see", "maybe", "not sure", "thinking", "considering"
    - Mixed signals: Both confirmation and new requests in same email
    - Unclear context: Missing key information, ambiguous language
    - Examples: "Ok, thanks", "Will check and get back", "Let me think about it", "Maybe later", "Not sure yet"

12. non_logistics: Not related to shipping, logistics, or freight operations
    - Examples: Meeting invites, general business, personal messages, marketing emails, newsletters
    - Context: No logistics keywords, unrelated business content

ANALYSIS FACTORS:
- **Full Thread Analysis**: Analyze ALL messages in the thread, not just the latest
- **Conversation Flow**: Consider the progression and context of the entire conversation
- **Confirmation Detection**: Look for confirmations in quoted replies or earlier messages
- **Intent Analysis**: Understand the intent and context of the entire conversation
- **Keyword Search**: Look for logistics keywords and phrases across all messages
- **Urgency Indicators**: "urgent", "ASAP", "deadline", "immediate", "rush", "priority"
- **Action Requirements**: "confirm", "book", "proceed", "quote", "approve", "accept"
- **Response Patterns**: "Re:", "answering questions", "providing information", "responding to"
- **Sender Analysis**: Identify if sender is customer, forwarder, or sales team
- **Bot Interaction Context**: What the bot previously asked for and how customer is responding

IMPORTANT CLASSIFICATION RULES:
- **Confirmation Priority**: If bot asked for confirmation and customer responds with "yes", "confirm", "correct", "proceed", classify as "confirmation_reply"
- **Context Matters**: Consider the entire email thread, not just the latest message
- **Forwarder Detection**: Look for professional language, pricing, quotes, and logistics company signatures
- **Clarification Detection**: If customer is providing specific information (ports, dates, weights) in response to bot questions, classify as "clarification_reply"
- **Vague Responses**: If email contains only "ok", "thanks", "will check", "maybe" without clear intent, classify as "confusing_email"
- **Logistics Keywords**: Must contain logistics-related terms for "logistics_request" classification
- **Thread History**: Previous messages in the thread provide crucial context for classification

EMAIL THREAD TO CLASSIFY:
Subject: {subject}

{thread_text}

Classify this email thread accurately, determine urgency level, and provide your reasoning with key indicators. Consider the entire conversation context.
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
            result["classification_method"] = "llm_thread_function_call"
            result["thread_id"] = thread_id
            
            # Validate and correct result if needed
            if result.get("email_type") not in self.email_types:
                self.logger.warning(f"Invalid email_type: {result.get('email_type')}, defaulting to non_logistics")
                result["email_type"] = "non_logistics"
                result["confidence"] = 0.5
                result["reasoning"] += " (corrected invalid type)"

            # Ensure confidence is within bounds
            confidence = result.get("confidence", 0.5)
            if not (0.0 <= confidence <= 1.0):
                result["confidence"] = max(0.0, min(1.0, confidence))

            # Validate message index
            message_index = result.get("classification_message_index", 0)
            if not (0 <= message_index < len(message_thread)):
                result["classification_message_index"] = 0

            self.logger.info(f"Thread classification successful: {result['email_type']} (confidence: {result['confidence']:.2f}, message index: {result['classification_message_index']})")
            
            return result

        except Exception as e:
            self.logger.error(f"LLM thread classification failed: {e}")
            return {"error": f"LLM thread classification failed: {str(e)}"}

    def _format_thread_for_analysis(self, message_thread: List[Dict[str, Any]]) -> str:
        """Format message thread for LLM analysis"""
        formatted_thread = []
        
        for i, message in enumerate(message_thread):
            sender = message.get("sender", "Unknown")
            timestamp = message.get("timestamp", "Unknown time")
            body = message.get("body", "")
            
            formatted_message = f"--- Message {i+1} from {sender} at {timestamp} ---\n{body}\n"
            formatted_thread.append(formatted_message)
        
        return "\n".join(formatted_thread)

# =====================================================
#                 🔁 Test Harness
# =====================================================
def test_classification_agent():
    """Test classification agent with various email scenarios"""
    print("=== Testing Classification Agent (LLM Only) ===")
    
    agent = ClassificationAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}, Has LLM: {bool(agent.client)}")

    test_cases = [
        {
            "name": "Customer Quote Request",
            "email_text": "Need quote for 2x40ft FCL from Shanghai to Long Beach, electronics, ready July 15th",
            "subject": "Shipping Quote Request",
            "expected": "logistics_request"
        },
        {
            "name": "Customer Confirmation",
            "email_text": "Yes, I confirm the booking for the containers",
            "subject": "Re: Booking Confirmation",
            "expected": "confirmation_reply"
        },
        {
            "name": "Forwarder Rate Quote",
            "email_text": "Our rate is $2500 USD for FCL 40ft, valid until Friday",
            "subject": "Rate Quote",
            "expected": "forwarder_response"
        },
        {
            "name": "Customer Clarification",
            "email_text": "The origin port is Shanghai, destination is Long Beach",
            "subject": "Re: Missing Information",
            "expected": "clarification_reply"
        },
        {
            "name": "Urgent Request",
            "email_text": "URGENT: Need immediate quote for 20DC container from AEAUH to AUBNE",
            "subject": "URGENT - Rate Request",
            "expected": "logistics_request"
        },
        {
            "name": "Non-Logistics Email",
            "email_text": "Meeting scheduled for tomorrow at 2 PM in conference room A",
            "subject": "Team Meeting",
            "expected": "non_logistics"
        },
        {
            "name": "Vague Request",
            "email_text": "I need help with shipping",
            "subject": "Help",
            "expected": "logistics_request"
        },
        {
            "name": "Complex Forwarder Response",
            "email_text": "Dear Customer, our quotation for your FCL shipment is as follows: 40HC $2800, 20DC $1500. Valid until end of month. Transit time 12-14 days.",
            "subject": "Re: Your Shipping Inquiry",
            "expected": "forwarder_response"
        },
        {
            "name": "Detailed Clarification Reply",
            "email_text": "Thank you for your inquiry. The origin is Shanghai port, destination is Long Beach. The commodity is electronics, weight approximately 25 tons.",
            "subject": "Re: Additional Information Required",
            "expected": "clarification_reply"
        },
        {
            "name": "Acceptance with Details",
            "email_text": "I accept your quote of $2500 for the FCL container. Please proceed with the booking.",
            "subject": "Quote Acceptance",
            "expected": "confirmation_reply"
        }
    ]

    results = {"correct": 0, "total": len(test_cases)}
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Subject: {test_case['subject']}")
        print(f"Expected: {test_case['expected']}")
        
        result = agent.run({
            "email_text": test_case["email_text"],
            "subject": test_case["subject"],
            "thread_id": f"test-{i}"
        })
        
        if result.get("status") == "success":
            email_type = result.get("email_type")
            confidence = result.get("confidence", 0.0)
            urgency = result.get("urgency", "unknown")
            requires_action = result.get("requires_action", False)
            key_indicators = result.get("key_indicators", [])
            reasoning = result.get("reasoning", "N/A")
            
            print(f"✓ Classified: {email_type}")
            print(f"✓ Confidence: {confidence:.2f}")
            print(f"✓ Urgency: {urgency}")
            print(f"✓ Requires Action: {requires_action}")
            print(f"✓ Key indicators: {key_indicators[:3]}")  # Show first 3
            print(f"✓ Reasoning: {reasoning[:100]}...")  # Show first 100 chars
            
            if email_type == test_case["expected"]:
                print("✅ CORRECT")
                results["correct"] += 1
            else:
                print("❌ INCORRECT")
        else:
            print(f"✗ Error: {result.get('error')}")
    
    accuracy = results["correct"] / results["total"] * 100
    print(f"\n📊 Accuracy: {results['correct']}/{results['total']} ({accuracy:.1f}%)")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Testing Edge Cases ===")
    
    agent = ClassificationAgent()
    agent.load_context()
    
    edge_cases = [
        {
            "name": "Empty Email",
            "input": {"email_text": "", "subject": "Test"}
        },
        {
            "name": "Only Subject",
            "input": {"email_text": " ", "subject": "Need shipping quote"}
        },
        {
            "name": "Special Characters",
            "input": {
                "email_text": "Need quote for FCL 40' container from 上海 to Rotterdam €2500",
                "subject": "Quote with Special Chars"
            }
        },
        {
            "name": "Very Long Email",
            "input": {
                "email_text": "Need quote for shipping containers from various ports including Shanghai, Shenzhen, Ningbo to multiple destinations in Europe and North America. " * 10,
                "subject": "Complex Multi-Port Request"
            }
        },
        {
            "name": "Mixed Languages",
            "input": {
                "email_text": "Hello, necesito cotización para envío FCL desde Shanghai to Mexico City. Gracias.",
                "subject": "Shipping Quote - Mixed Language"
            }
        }
    ]
    
    for case in edge_cases:
        print(f"\n--- {case['name']} ---")
        result = agent.run(case["input"])
        
        if result.get("status") == "success":
            print(f"✓ Type: {result.get('email_type')}")
            print(f"✓ Confidence: {result.get('confidence', 0):.2f}")
            print(f"✓ Urgency: {result.get('urgency')}")
        else:
            print(f"✗ Error: {result.get('error')}")

def test_performance():
    """Test classification performance with batch processing"""
    print("\n=== Testing Performance ===")
    
    agent = ClassificationAgent()
    agent.load_context()
    
    if not agent.client:
        print("✗ Cannot run performance test - LLM client not available")
        return
    
    import time
    
    test_emails = [
        {"email_text": "Need FCL quote Shanghai to Long Beach", "subject": "Quote Request"},
        {"email_text": "Yes, confirmed", "subject": "Confirmation"},
        {"email_text": "Our rate is $2500", "subject": "Rate Quote"},
        {"email_text": "Origin is Shanghai port", "subject": "Clarification"},
        {"email_text": "LCL shipment needed", "subject": "Shipping Request"}
    ] * 5  # 25 total requests
    
    print(f"Processing {len(test_emails)} classification requests...")
    
    start_time = time.time()
    successful = 0
    failed = 0
    
    for i, email in enumerate(test_emails, 1):
        result = agent.run(email)
        if result.get("status") == "success":
            successful += 1
        else:
            failed += 1
        
        # Show progress every 5 requests
        if i % 5 == 0:
            print(f"  Processed {i}/{len(test_emails)}...")
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / len(test_emails)
    
    print(f"\n📊 Performance Results:")
    print(f"✓ Total time: {total_time:.2f}s")
    print(f"✓ Average per request: {avg_time:.2f}s")   
    print(f"✓ Successful: {successful}/{len(test_emails)}")
    print(f"✗ Failed: {failed}/{len(test_emails)}")
    print(f"✓ Success rate: {successful/len(test_emails)*100:.1f}%")

def test_confidence_levels():
    """Test confidence scoring accuracy"""
    print("\n=== Testing Confidence Levels ===")
    
    agent = ClassificationAgent()
    agent.load_context()
    
    if not agent.client:
        print("✗ Cannot run confidence test - LLM client not available")
        return
    
    confidence_tests = [
        {
            "name": "Clear Logistics Request",
            "email_text": "Need quote for 2x40ft FCL from Shanghai to Long Beach",
            "subject": "FCL Quote Request",
            "expected_confidence": "> 0.8"
        },
        {
            "name": "Clear Confirmation",
            "email_text": "Yes, I confirm the booking",
            "subject": "Booking Confirmation",
            "expected_confidence": "> 0.8"
        },
        {
            "name": "Ambiguous Request",
            "email_text": "I need help",
            "subject": "Help",
            "expected_confidence": "< 0.7"
        },
        {
            "name": "Mixed Content",
            "email_text": "Thanks for the meeting. Also, do you handle shipping?",
            "subject": "Follow up",
            "expected_confidence": "< 0.7"
        }
    ]
    
    for test in confidence_tests:
        print(f"\n--- {test['name']} ---")
        result = agent.run({
            "email_text": test["email_text"],
            "subject": test["subject"]
        })
        
        if result.get("status") == "success":
            confidence = result.get("confidence", 0.0)
            print(f"✓ Confidence: {confidence:.2f} (expected {test['expected_confidence']})")
            print(f"✓ Type: {result.get('email_type')}")
        else:
            print(f"✗ Error: {result.get('error')}")

if __name__ == "__main__":
    test_classification_agent()
    test_edge_cases()
    test_performance()
    test_confidence_levels()

