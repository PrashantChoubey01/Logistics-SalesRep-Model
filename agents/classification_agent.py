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
        
        # Email classification categories
        self.email_types = [
            "logistics_request",      # Customer requesting shipping quote/service
            "confirmation_reply",     # Customer confirming/accepting a proposal
            "forwarder_response",     # Freight forwarder providing rates/quotes
            "clarification_reply",    # Customer providing requested information
            "non_logistics"           # Not related to shipping/logistics
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
1. logistics_request: Customer requesting shipping quote, service, or logistics information
   - Keywords: "need quote", "quotation", "shipping", "fcl", "lcl", "container", "freight", "cargo"
   - Examples: "Need quote for FCL", "Shipping request", "Rate for container"

2. confirmation_reply: Customer confirming/accepting a proposal, booking, or agreement
   - Keywords: "yes, i confirm", "i accept", "confirmed", "approve", "agreed", "proceed with"
   - Examples: "Yes, confirmed", "I accept the quote", "Proceed with booking"

3. forwarder_response: Freight forwarder providing rates, quotes, or shipping information
   - Keywords: "our rate", "quote is", "price is", "usd", "valid until", "freight rate"
   - Examples: "Our rate is $2500", "Quote attached", "Valid until Friday"

4. clarification_reply: Customer providing requested information or answering questions
   - Keywords: "the origin", "the destination", "port is", "date is", "weight is"
   - Examples: "Origin is Shanghai", "The weight is 25 tons", "Departure date is..."

5. non_logistics: Not related to shipping, logistics, or freight operations
   - Examples: Meeting invites, general business, personal messages

ANALYSIS FACTORS:
- Intent and context of the message
- Keywords and phrases used
- Urgency indicators (urgent, ASAP, deadline, immediate)
- Action requirements (confirm, book, proceed, quote)
- Response patterns (Re:, answering questions)

IMPORTANT CLASSIFICATION RULES:
- If the email body contains only vague content (like "hi", "hello", "thanks", "ok") without specific logistics keywords, classify as "non_logistics"
- The subject line should NOT override clear non-logistics content in the email body
- For very short or vague messages, prioritize the actual content over the subject line
- Messages with no logistics-specific content should be classified as "non_logistics" regardless of subject

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
1. logistics_request: Customer requesting shipping quote, service, or logistics information
   - Keywords: "need quote", "quotation", "shipping", "fcl", "lcl", "container", "freight", "cargo"
   - Examples: "Need quote for FCL", "Shipping request", "Rate for container"

2. confirmation_reply: Customer confirming/accepting a proposal, booking, or agreement
   - Keywords: "yes, i confirm", "i accept", "confirmed", "approve", "agreed", "proceed with"
   - Examples: "Yes, confirmed", "I accept the quote", "Proceed with booking"

3. forwarder_response: Freight forwarder providing rates, quotes, or shipping information
   - Keywords: "our rate", "quote is", "price is", "usd", "valid until", "freight rate"
   - Examples: "Our rate is $2500", "Quote attached", "Valid until Friday"

4. clarification_reply: Customer providing requested information or answering questions
   - Keywords: "the origin", "the destination", "port is", "date is", "weight is"
   - Examples: "Origin is Shanghai", "The weight is 25 tons", "Departure date is..."

5. non_logistics: Not related to shipping, logistics, or freight operations
   - Examples: Meeting invites, general business, personal messages

ANALYSIS FACTORS:
- Analyze ALL messages in the thread, not just the latest
- Consider conversation flow and context
- Look for confirmations in quoted replies or earlier messages
- Intent and context of the entire conversation
- Keywords and phrases used across all messages
- Urgency indicators (urgent, ASAP, deadline, immediate)
- Action requirements (confirm, book, proceed, quote)
- Response patterns (Re:, answering questions)

IMPORTANT CLASSIFICATION RULES:
- If the email body contains only vague content (like "hi", "hello", "thanks", "ok") without specific logistics keywords, classify as "non_logistics"
- The subject line should NOT override clear non-logistics content in the email body
- For very short or vague messages, prioritize the actual content over the subject line
- Messages with no logistics-specific content should be classified as "non_logistics" regardless of subject

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

