"""Confirmation Agent: Detects and extracts confirmation intent from customer emails using LLM function calling."""

import json
from typing import Dict, Any, List
try:
    from .base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class ConfirmationAgent(BaseAgent):
    """Agent to detect confirmation intent in customer emails using LLM function calling only."""

    def __init__(self):
        super().__init__("confirmation_agent")
        
        # Confirmation types for logistics
        self.confirmation_types = [
            "booking_confirmation",    # Confirming a booking/reservation
            "quote_acceptance",        # Accepting a price quote
            "shipment_approval",       # Approving shipment details
            "schedule_confirmation",   # Confirming pickup/delivery schedule
            "document_approval",       # Approving documents/terms
            "no_confirmation"          # Not a confirmation
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect confirmation intent and extract confirmation details from full thread.
        
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
            return self._llm_thread_confirmation_detection(subject, message_thread, thread_id)
        elif email_text:
            return self._llm_confirmation_detection(subject, email_text, thread_id)
        else:
            return {"error": "No email text or message thread provided"}

    def _llm_confirmation_detection(self, subject: str, email_text: str, thread_id: str) -> Dict[str, Any]:
        """Detect confirmation using LLM function calling for structured output"""
        try:
            function_schema = {
                "name": "detect_confirmation",
                "description": "Detect if the email contains confirmation intent for logistics operations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "is_confirmation": {
                            "type": "boolean",
                            "description": "True if the email contains confirmation intent"
                        },
                        "confirmation_type": {
                            "type": "string",
                            "enum": self.confirmation_types,
                            "description": "Type of confirmation detected"
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence score for confirmation detection (0.0 to 1.0)"
                        },
                        "confirmation_details": {
                            "type": "string",
                            "description": "Specific details about what is being confirmed"
                        },
                        "key_phrases": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key phrases that indicate confirmation intent"
                        },
                        "next_action": {
                            "type": "string",
                            "description": "Suggested next action based on confirmation"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Explanation for confirmation detection decision"
                        }
                    },
                    "required": ["is_confirmation", "confirmation_type", "confidence", "confirmation_details", "key_phrases", "next_action", "reasoning"]
                }
            }

            prompt = f"""
You are an expert at detecting confirmation intent in logistics emails. Analyze this email to determine if the customer is confirming something.

CONFIRMATION TYPES:
1. booking_confirmation: Customer confirming a booking/reservation
   - Keywords: "confirm booking", "book it", "proceed with booking", "reserve"
   
2. quote_acceptance: Customer accepting a price quote
   - Keywords: "accept quote", "agreed price", "go with your rate", "approve quote"
   
3. shipment_approval: Customer approving shipment details/arrangements
   - Keywords: "approve shipment", "confirm details", "looks good", "proceed"
   
4. schedule_confirmation: Customer confirming pickup/delivery schedule
   - Keywords: "confirm pickup", "delivery time ok", "schedule confirmed"
   
5. document_approval: Customer approving documents/terms
   - Keywords: "approve documents", "terms accepted", "sign off"
   
6. no_confirmation: Email does not contain confirmation intent
   - Examples: Questions, requests, complaints, general information

CONFIRMATION INDICATORS:
- Affirmative words: "yes", "confirmed", "approve", "accept", "agreed", "ok", "proceed"
- Action words: "book it", "go ahead", "do it", "start", "begin"
- Agreement phrases: "looks good", "sounds good", "that works", "perfect"

THREAD RESPONSE RULES:
- If this is a response to a thread (not the first message) and contains any confirmation phrases, treat it as a confirmation
- For thread responses, be more lenient - confirmation intent is more important than specific details
- Even vague confirmations like "confirmed" or "ok" should be treated as confirmations in thread context

ANALYSIS FACTORS:
- Direct confirmation statements
- Context of agreement or approval
- Response to previous proposals
- Clear intent to move forward
- IMPORTANT: If this is a response to a thread (not the first message) and contains confirmation phrases like "confirmed", "yes", "ok", "proceed", etc., treat it as a confirmation even if details are vague
- For thread responses, prioritize confirmation intent over specific details
- Specific details being confirmed (preferred but not required for thread responses)

EMAIL TO ANALYZE:
Subject: {subject}
Body: {email_text}

Determine if this email contains confirmation intent and provide detailed analysis.
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
            result["detection_method"] = "llm_function_call"
            result["thread_id"] = thread_id
            
            # Validate result
            if result.get("confirmation_type") not in self.confirmation_types:
                self.logger.warning(f"Invalid confirmation_type: {result.get('confirmation_type')}, defaulting to no_confirmation")
                result["confirmation_type"] = "no_confirmation"
                result["is_confirmation"] = False
                result["confidence"] = 0.5

            # Ensure confidence is within bounds
            confidence = result.get("confidence", 0.5)
            if not (0.0 <= confidence <= 1.0):
                result["confidence"] = max(0.0, min(1.0, confidence))

            # Consistency check
            if result.get("confirmation_type") == "no_confirmation":
                result["is_confirmation"] = False
            elif result.get("is_confirmation") and result.get("confirmation_type") == "no_confirmation":
                result["confirmation_type"] = "booking_confirmation"  # Default fallback

            self.logger.info(f"Confirmation detection: {result['is_confirmation']} ({result['confirmation_type']}, confidence: {result['confidence']:.2f})")
            
            return result

        except Exception as e:
            self.logger.error(f"LLM confirmation detection failed: {e}")
            return {"error": f"LLM confirmation detection failed: {str(e)}"}

    def _llm_thread_confirmation_detection(self, subject: str, message_thread: List[Dict[str, Any]], thread_id: str) -> Dict[str, Any]:
        """Detect confirmation using LLM function calling for structured output with full thread analysis"""
        try:
            function_schema = {
                "name": "detect_confirmation_from_thread",
                "description": "Detect if any message in the thread contains confirmation intent for logistics operations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "is_confirmation": {
                            "type": "boolean",
                            "description": "True if any message in the thread contains confirmation intent"
                        },
                        "confirmation_type": {
                            "type": "string",
                            "enum": self.confirmation_types,
                            "description": "Type of confirmation detected"
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence score for confirmation detection (0.0 to 1.0)"
                        },
                        "confirmation_details": {
                            "type": "string",
                            "description": "Specific details about what is being confirmed"
                        },
                        "confirmation_message_index": {
                            "type": "integer",
                            "description": "Index of the message containing the confirmation (0-based)"
                        },
                        "confirmation_sender": {
                            "type": "string",
                            "description": "Email address of the sender who confirmed"
                        },
                        "key_phrases": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key phrases that indicate confirmation intent"
                        },
                        "next_action": {
                            "type": "string",
                            "description": "Suggested next action based on confirmation"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Explanation for confirmation detection decision"
                        }
                    },
                    "required": ["is_confirmation", "confirmation_type", "confidence", "confirmation_details", "confirmation_message_index", "confirmation_sender", "key_phrases", "next_action", "reasoning"]
                }
            }

            # Format thread for analysis
            thread_text = self._format_thread_for_analysis(message_thread)

            prompt = f"""
You are an expert at detecting confirmation intent in logistics email threads. Analyze the entire conversation thread to determine if the customer has confirmed something.

CONFIRMATION TYPES:
1. booking_confirmation: Customer confirming a booking/reservation
   - Keywords: "confirm booking", "book it", "proceed with booking", "reserve"
   
2. quote_acceptance: Customer accepting a price quote
   - Keywords: "accept quote", "agreed price", "go with your rate", "approve quote"
   
3. shipment_approval: Customer approving shipment details/arrangements
   - Keywords: "approve shipment", "confirm details", "looks good", "proceed"
   
4. schedule_confirmation: Customer confirming pickup/delivery schedule
   - Keywords: "confirm pickup", "delivery time ok", "schedule confirmed"
   
5. document_approval: Customer approving documents/terms
   - Keywords: "approve documents", "terms accepted", "sign off"
   
6. no_confirmation: Thread does not contain confirmation intent
   - Examples: Questions, requests, complaints, general information

CONFIRMATION INDICATORS:
- Affirmative words: "yes", "confirmed", "approve", "accept", "agreed", "ok", "proceed"
- Action words: "book it", "go ahead", "do it", "start", "begin"
- Agreement phrases: "looks good", "sounds good", "that works", "perfect"

THREAD RESPONSE RULES:
- If this is a response to a thread (not the first message) and contains any confirmation phrases, treat it as a confirmation
- For thread responses, be more lenient - confirmation intent is more important than specific details
- Even vague confirmations like "confirmed" or "ok" should be treated as confirmations in thread context

ANALYSIS FACTORS:
- Look through ALL messages in the thread, not just the latest
- Consider quoted replies and conversation context
- Direct confirmation statements
- Context of agreement or approval
- Response to previous proposals
- Clear intent to move forward
- IMPORTANT: If this is a response to a thread (not the first message) and contains confirmation phrases like "confirmed", "yes", "ok", "proceed", etc., treat it as a confirmation even if details are vague
- For thread responses, prioritize confirmation intent over specific details
- Specific details being confirmed (preferred but not required for thread responses)

EMAIL THREAD TO ANALYZE:
Subject: {subject}

{thread_text}

Determine if any message in this thread contains confirmation intent and provide detailed analysis.
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
            result["detection_method"] = "llm_thread_function_call"
            result["thread_id"] = thread_id
            
            # Validate result
            if result.get("confirmation_type") not in self.confirmation_types:
                self.logger.warning(f"Invalid confirmation_type: {result.get('confirmation_type')}, defaulting to no_confirmation")
                result["confirmation_type"] = "no_confirmation"
                result["is_confirmation"] = False
                result["confidence"] = 0.5

            # Ensure confidence is within bounds
            confidence = result.get("confidence", 0.5)
            if not (0.0 <= confidence <= 1.0):
                result["confidence"] = max(0.0, min(1.0, confidence))

            # Validate message index
            message_index = result.get("confirmation_message_index", 0)
            if not (0 <= message_index < len(message_thread)):
                result["confirmation_message_index"] = 0

            # Consistency check
            if result.get("confirmation_type") == "no_confirmation":
                result["is_confirmation"] = False
            elif result.get("is_confirmation") and result.get("confirmation_type") == "no_confirmation":
                result["confirmation_type"] = "booking_confirmation"  # Default fallback

            self.logger.info(f"Thread confirmation detection: {result['is_confirmation']} ({result['confirmation_type']}, confidence: {result['confidence']:.2f}, message index: {result['confirmation_message_index']})")
            
            return result

        except Exception as e:
            self.logger.error(f"LLM thread confirmation detection failed: {e}")
            return {"error": f"LLM thread confirmation detection failed: {str(e)}"}

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
def test_confirmation_agent():
    """Test confirmation agent with various email scenarios"""
    print("=== Testing Confirmation Agent (LLM Only) ===")
    
    agent = ConfirmationAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}, Has LLM: {bool(agent.client)}")

    test_cases = [
        {
            "name": "Clear Booking Confirmation",
            "email_text": "Yes, I confirm the booking for 2x40ft containers from Shanghai to Long Beach.",
            "subject": "Booking Confirmation",
            "expected": True
        },
        {
            "name": "Quote Acceptance",
            "email_text": "We accept your quote of $2500 for the FCL shipment. Please proceed.",
            "subject": "Quote Acceptance",
            "expected": True
        },
        {
            "name": "Simple Yes Confirmation",
            "email_text": "Yes, confirmed. Please arrange the pickup for next week.",
            "subject": "Re: Pickup Arrangement",
            "expected": True
        },
        {
            "name": "Approval with Details",
            "email_text": "The shipment details look good. Please proceed with the booking.",
            "subject": "Shipment Approval",
            "expected": True
        },
        {
            "name": "Schedule Confirmation",
            "email_text": "The pickup time of 10 AM on Friday works for us. Confirmed.",
            "subject": "Pickup Schedule",
            "expected": True
        },
        {
            "name": "Not a Confirmation - Question",
            "email_text": "Can you please clarify the insurance terms?",
            "subject": "Clarification Needed",
            "expected": False
        },
        {
            "name": "Not a Confirmation - Request",
            "email_text": "Need quote for FCL shipment from Mumbai to Rotterdam",
            "subject": "Quote Request",
            "expected": False
        },
        {
            "name": "Not a Confirmation - Complaint",
            "email_text": "The delivery was delayed. This is unacceptable.",
            "subject": "Delivery Issue",
            "expected": False
        },
        {
            "name": "Ambiguous Response",
            "email_text": "Thank you for your offer. We will get back to you soon.",
            "subject": "Re: Your Offer",
            "expected": False
        },
        {
            "name": "Conditional Acceptance",
            "email_text": "I can accept the quote if you can guarantee delivery by Friday.",
            "subject": "Conditional Acceptance",
            "expected": False
        }
    ]

    results = {"correct": 0, "total": len(test_cases)}
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Expected confirmation: {test_case['expected']}")
        
        result = agent.run({
            "email_text": test_case["email_text"],
            "subject": test_case["subject"],
            "thread_id": f"test-{i}"
        })
        
        if result.get("status") == "success":
            is_confirmation = result.get("is_confirmation", False)
            confirmation_type = result.get("confirmation_type", "unknown")
            confidence = result.get("confidence", 0.0)
            key_phrases = result.get("key_phrases", [])
            next_action = result.get("next_action", "N/A")
            
            print(f"✓ Is Confirmation: {is_confirmation}")
            print(f"✓ Type: {confirmation_type}")
            print(f"✓ Confidence: {confidence:.2f}")
            print(f"✓ Key phrases: {key_phrases[:3]}")  # Show first 3
            print(f"✓ Next action: {next_action}")
            print(f"✓ Details: {result.get('confirmation_details', 'N/A')[:50]}...")
            
            if is_confirmation == test_case["expected"]:
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
    
    agent = ConfirmationAgent()
    agent.load_context()
    
    edge_cases = [
        {
            "name": "Empty Email",
            "input": {"email_text": "", "subject": "Test"}
        },
        {
            "name": "Single Word",
            "input": {"email_text": "Confirmed", "subject": "Re: Booking"}
        },
        {
            "name": "Mixed Languages",
            "input": {
                "email_text": "Sí, confirmado. Yes, I confirm the booking.",
                "subject": "Confirmación"
            }
        },
        {
            "name": "Multiple Confirmations",
            "input": {
                "email_text": "Yes, I confirm the booking. Also, I accept the quote. Please proceed with both.",
                "subject": "Multiple Confirmations"
            }
        }
    ]
    
    for case in edge_cases:
        print(f"\n--- {case['name']} ---")
        result = agent.run(case["input"])
        
        if result.get("status") == "success":
            print(f"✓ Confirmation: {result.get('is_confirmation')}")
            print(f"✓ Type: {result.get('confirmation_type')}")
            print(f"✓ Confidence: {result.get('confidence', 0):.2f}")
        else:
            print(f"✗ Error: {result.get('error')}")

if __name__ == "__main__":
    test_confirmation_agent()
    test_edge_cases()
