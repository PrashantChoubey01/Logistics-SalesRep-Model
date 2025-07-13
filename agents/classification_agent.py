"""Classification agent for email categorization"""

# =====================================================
#                 LLM CONFIGURATION
# =====================================================
# Databricks Configuration
DATABRICKS_TOKEN = "dapi81b45be7f09611a410fc3e5104a8cadf-3"
DATABRICKS_BASE_URL = "https://adb-1825279086009288.8.azuredatabricks.net/serving-endpoints"
MODEL_ENDPOINT_ID = "databricks-meta-llama-3-3-70b-instruct"

import os
import sys
from typing import Dict, Any
import re

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import base agent with error handling
try:
    from agents.base_agent import BaseAgent
except ImportError:
    try:
        from base_agent import BaseAgent
    except ImportError as e:
        import logging
        logging.error(f"Cannot import BaseAgent: {e}")
        # Create a minimal BaseAgent fallback
        from abc import ABC, abstractmethod
        class BaseAgent(ABC):
            def __init__(self, name): 
                self.agent_name = name
                import logging
                self.logger = logging.getLogger(self.agent_name)
                self.client = None
                self.config = {
                    "api_key": DATABRICKS_TOKEN,
                    "base_url": DATABRICKS_BASE_URL,
                    "model_name": MODEL_ENDPOINT_ID
                }
            def load_context(self): 
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=self.config["api_key"], base_url=self.config["base_url"])
                    return True
                except:
                    return True
            @abstractmethod
            def process(self, input_data): pass
            def run(self, input_data): 
                try:
                    result = self.process(input_data)
                    result["status"] = "success"
                    return result
                except Exception as e:
                    return {"error": str(e), "status": "error"}

class ClassificationAgent(BaseAgent):
    """Agent for classifying email types and determining urgency"""

    def __init__(self):
        super().__init__("classification_agent")
        self.classification_types = [
            "logistics_request",
            "confirmation_reply", 
            "forwarder_response",
            "clarification_reply",
            "non_logistics"
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify email type and determine urgency"""
        email_text = input_data.get("email_text", "")
        subject = input_data.get("subject", "")
        
        if not email_text:
            return {"error": "No email text provided"}

        # Try keyword-based classification first
        result = self._keyword_classify(subject, email_text)
        
        # If confidence is low and we have OpenAI client, try AI classification
        if result.get("confidence", 0) < 0.8 and self.client:
            ai_result = self._ai_classify(subject, email_text)
            if ai_result.get("confidence", 0) > result.get("confidence", 0):
                result = ai_result

        return result

    def _keyword_classify(self, subject: str, email_text: str) -> Dict[str, Any]:
        """Classify using keyword matching"""
        combined_text = f"{subject} {email_text}".lower()

        # Confirmation replies (highest priority)
        if any(phrase in combined_text for phrase in [
            "yes, i confirm", "i accept", "confirmed", "approve", "agreed",
            "proceed with", "book it", "go ahead", "yes please"
        ]):
            return {
                "email_type": "confirmation_reply",
                "confidence": 0.9,
                "urgency": "high",
                "requires_action": True,
                "reasoning": "Contains confirmation language"
            }

        # Forwarder responses (pricing/rates)
        if any(phrase in combined_text for phrase in [
            "our rate", "quote is", "price is", "usd", "valid until",
            "freight rate", "shipping cost", "quotation attached"
        ]):
            return {
                "email_type": "forwarder_response", 
                "confidence": 0.85,
                "urgency": "medium",
                "requires_action": True,
                "reasoning": "Contains pricing/rate information"
            }

        # Clarification replies
        if any(phrase in combined_text for phrase in [
            "the origin", "the destination", "port is", "date is",
            "weight is", "volume is", "commodity is"
        ]) or re.search(r'\b(origin|destination).*(is|port)\b', combined_text):
            return {
                "email_type": "clarification_reply",
                "confidence": 0.8,
                "urgency": "medium", 
                "requires_action": True,
                "reasoning": "Providing specific information/answers"
            }

        # Logistics requests
        if any(word in combined_text for word in [
            "need quote", "quotation", "shipping", "fcl", "lcl", "container",
            "freight", "cargo", "shipment", "need", "require", "request"
        ]):
            return {
                "email_type": "logistics_request",
                "confidence": 0.75,
                "urgency": "medium",
                "requires_action": True,
                "reasoning": "Contains shipping/quote keywords"
            }

        # Default to non-logistics
        return {
            "email_type": "non_logistics",
            "confidence": 0.6,
            "urgency": "low", 
            "requires_action": False,
            "reasoning": "No logistics keywords found"
        }

    def _ai_classify(self, subject: str, email_text: str) -> Dict[str, Any]:
        """Use Databricks LLM for classification when available"""
        if not self.client:
            return {"error": "LLM client not available"}

        try:
            prompt = f"""
            Classify this email into one of these categories:
            - logistics_request: Customer requesting shipping quote/service
            - confirmation_reply: Customer confirming/accepting a proposal
            - forwarder_response: Freight forwarder providing rates/quotes
            - clarification_reply: Customer providing requested information
            - non_logistics: Not related to shipping/logistics

            Subject: {subject}
            Email: {email_text}

            Respond with JSON format:
            {{
                "email_type": "category",
                "confidence": 0.0-1.0,
                "urgency": "low/medium/high",
                "requires_action": true/false,
                "reasoning": "explanation"
            }}
            """

            response = self.client.chat.completions.create(
                model=MODEL_ENDPOINT_ID,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200
            )

            import json
            result = json.loads(response.choices[0].message.content)
            result["classification_method"] = "databricks_llm"
            return result

        except Exception as e:
            self.logger.error(f"Databricks LLM classification failed: {e}")
            return {"error": f"LLM classification failed: {e}"}

# =====================================================
#                 🔁 Local Test Harness
# =====================================================

def test_classification_agent():
    print("=== Testing Classification Agent with Databricks ===")
    
    agent = ClassificationAgent()
    
    test_cases = [
        {
            "email_text": "Need quote for FCL shipment from Shanghai to Long Beach",
            "subject": "Shipping Quote Request",
            "expected": "logistics_request"
        },
        {
            "email_text": "Yes, I confirm the booking for the containers",
            "subject": "Re: Booking Confirmation", 
            "expected": "confirmation_reply"
        },
        {
            "email_text": "Our rate is $2500 USD for FCL 40ft",
            "subject": "Rate Quote",
            "expected": "forwarder_response"
        },
        {
            "email_text": "The origin port is Shanghai",
            "subject": "Re: Missing Information",
            "expected": "clarification_reply"
        }
    ]
    
    if agent.load_context():
        print(f"✓ LLM Client: {'Connected' if agent.client else 'Not available'}")
        correct = 0
        for i, test_data in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i} ---")
            print(f"Input: {test_data['subject']}")
            print(f"Expected: {test_data['expected']}")
            
            result = agent.run(test_data)
            if result.get("status") == "success":
                actual = result.get("email_type")
                confidence = result.get("confidence")
                method = result.get("classification_method", "keyword")
                print(f"✓ Actual: {actual}")
                print(f"✓ Confidence: {confidence}")
                print(f"✓ Method: {method}")
                print(f"✓ Reasoning: {result.get('reasoning')}")
                
                if actual == test_data['expected']:
                    print("✅ CORRECT")
                    correct += 1
                else:
                    print("❌ WRONG")
            else:
                print(f"✗ Error: {result.get('error')}")
        
        print(f"\n=== SUMMARY ===")
        print(f"Accuracy: {correct}/{len(test_cases)} ({correct/len(test_cases)*100:.1f}%)")
    else:
        print("✗ Failed to load context")

if __name__ == "__main__":
    test_classification_agent()
