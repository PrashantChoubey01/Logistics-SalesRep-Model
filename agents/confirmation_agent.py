"""Confirmation Agent: Detects and extracts confirmation intent from customer emails using LLM function calling."""

import json
from typing import Dict, Any
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
        Detect confirmation intent and extract confirmation details.
        
        Expected input:
        - email_text: Raw email content (required)
        - subject: Email subject line (required)
        - thread_id: Optional thread identifier
        """
        email_text = input_data.get("email_text", "").strip()
        subject = input_data.get("subject", "").strip()
        thread_id = input_data.get("thread_id", "")

        if not email_text:
            return {"error": "No email text provided"}

        if not self.client:
            return {"error": "LLM client not initialized"}

        return self._llm_confirmation_detection(subject, email_text, thread_id)

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

ANALYSIS FACTORS:
- Direct confirmation statements
- Context of agreement or approval
- Response to previous proposals
- Clear intent to move forward
- Specific details being confirmed

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
