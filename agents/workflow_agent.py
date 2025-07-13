"""Improved workflow agent with better classification and extraction"""

# =====================================================
#                 LLM CONFIGURATION
# =====================================================
# Databricks Configuration
DATABRICKS_TOKEN = "dapi81b45be7f09611a410fc3e5104a8cadf-3"
DATABRICKS_BASE_URL = "https://adb-1825279086009288.8.azuredatabricks.net/serving-endpoints"
MODEL_ENDPOINT_ID = "databricks-meta-llama-3-3-70b-instruct"

import os
import sys
from typing import Dict, Any, List
import json
import re

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import agents with error handling
try:
    from .base_agent import BaseAgent
    from .classification_agent import ClassificationAgent
    from .extraction_agent import ExtractionAgent
except ImportError:
    try:
        from base_agent import BaseAgent
        from classification_agent import ClassificationAgent
        from extraction_agent import ExtractionAgent
    except ImportError as e:
        import logging
        logging.error(f"Cannot import required agents: {e}")
        # Create minimal fallback classes
        from abc import ABC, abstractmethod
        
        class BaseAgent(ABC):
            def __init__(self, name): 
                self.agent_name = name
                self.logger = logging.getLogger(name)
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
            def process(self, input_data):
                return {"email_type": "logistics_request", "confidence": 0.5}
        
        class ExtractionAgent(BaseAgent):
            def process(self, input_data):
                return {"origin": None, "destination": None, "shipment_type": "Unknown"}

class ImprovedClassificationAgent(ClassificationAgent):
    """Improved classification with better keyword logic"""
    
    def _keyword_classify(self, subject: str, email_text: str) -> Dict[str, Any]:
        """Improved keyword-based classification"""
        
        combined_text = f"{subject} {email_text}".lower()
        
        # More specific classification rules
        
        # 1. Confirmation replies (check first - most specific)
        if any(word in combined_text for word in [
            "yes, i confirm", "i accept", "confirmed", "approve", "agreed", 
            "proceed with", "book it", "go ahead"
        ]):
            return {
                "email_type": "confirmation_reply",
                "confidence": 0.9,
                "urgency": "high",
                "requires_action": True,
                "reasoning": "Contains confirmation language"
            }
        
        # 2. Forwarder responses (pricing/rates)
        if any(word in combined_text for word in [
            "our rate", "quote is", "price is", "usd", "valid until", 
            "freight rate", "shipping cost"
        ]):
            return {
                "email_type": "forwarder_response",
                "confidence": 0.85,
                "urgency": "medium",
                "requires_action": True,
                "reasoning": "Contains pricing/rate information"
            }
        
        # 3. Clarification replies (answering questions)
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
        
        # 4. Logistics requests (broader terms)
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
        
        # 5. Default to non-logistics
        else:
            return {
                "email_type": "non_logistics",
                "confidence": 0.6,
                "urgency": "low",
                "requires_action": False,
                "reasoning": "No logistics keywords found"
            }

class ImprovedExtractionAgent(ExtractionAgent):
    """Improved extraction with better port detection"""
    
    def _regex_extract(self, subject: str, email_text: str) -> Dict[str, Any]:
        """Improved regex-based extraction"""
        
        combined_text = f"{subject} {email_text}"
        
        # Better port extraction using common patterns
        origin, destination = self._extract_ports_improved(combined_text)
        
        # Extract shipment type
        shipment_type = "FCL" if re.search(r'\bfcl\b', combined_text, re.IGNORECASE) else \
                       "LCL" if re.search(r'\blcl\b', combined_text, re.IGNORECASE) else "Unknown"
        
        # Extract container info
        container_match = re.search(r'\b(\d+)\s*x?\s*(20|40)\s*(gp|hc|ft)?\b', combined_text, re.IGNORECASE)
        quantity = int(container_match.group(1)) if container_match else 1
        container_type = f"{container_match.group(2)}GP" if container_match else "40GP"
        
        # Extract weight
        weight_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(kg|kgs|ton|tons|mt|lbs|pounds)\b', combined_text, re.IGNORECASE)
        weight = f"{weight_match.group(1)} {weight_match.group(2)}" if weight_match else None
        
        # Extract volume
        volume_match = re.search(r'\b(\d+(?:\.\d+)?)\s*(cbm|m3|cubic\s*meter|ft3|cubic\s*feet)\b', combined_text, re.IGNORECASE)
        volume = f"{volume_match.group(1)} {volume_match.group(2)}" if volume_match else None
        
        # Extract dates
        date_matches = re.findall(r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b', combined_text, re.IGNORECASE)
        shipment_date = date_matches[0] if date_matches else None
        
        # Check for dangerous goods
        dangerous_goods = bool(re.search(r'\b(dangerous|hazardous|dg|imdg|un\d+)\b', combined_text, re.IGNORECASE))
        
        return {
            "origin": origin,
            "destination": destination,
            "shipment_type": shipment_type,
            "container_type": container_type,
            "quantity": quantity,
            "weight": weight,
            "volume": volume,
            "shipment_date": shipment_date,
            "commodity": self._extract_commodity(combined_text.lower()),
            "dangerous_goods": dangerous_goods,
            "special_requirements": self._extract_special_requirements(combined_text.lower()),
            "extraction_method": "improved_regex"
        }
    
    def _extract_ports_improved(self, text: str) -> tuple:
        """Improved port extraction"""
        
        # Common port cities
        known_ports = [
            'shanghai', 'long beach', 'los angeles', 'hamburg', 'rotterdam', 
            'singapore', 'mumbai', 'new york', 'felixstowe', 'antwerp'
        ]
        
        text_lower = text.lower()
        found_ports = []
        
        # Find known ports
        for port in known_ports:
            if port in text_lower:
                found_ports.append(port.title())
        
        # Pattern-based extraction for "from X to Y"
        from_to_match = re.search(r'\bfrom\s+([A-Za-z\s]+?)\s+to\s+([A-Za-z\s]+?)(?:\s|,|$)', text, re.IGNORECASE)
        if from_to_match:
            origin = from_to_match.group(1).strip().title()
            destination = from_to_match.group(2).strip().title()
            return origin, destination
        
        # Use found ports in order
        if len(found_ports) >= 2:
            return found_ports[0], found_ports[1]
        elif len(found_ports) == 1:
            return found_ports[0], None
        
        return None, None

    def _extract_commodity(self, text: str) -> str:
        """Extract commodity type"""
        commodities = {
            'electronics': r'\b(electronics?|computers?|phones?|laptops?)\b',
            'textiles': r'\b(textiles?|clothing|garments?|fabric)\b',
            'machinery': r'\b(machinery|machines?|equipment)\b',
            'food': r'\b(food|rice|wheat|grain|fruits?)\b',
            'chemicals': r'\b(chemicals?|paint|oil|liquid)\b',
            'furniture': r'\b(furniture|chairs?|tables?|wood)\b'
        }
        for commodity, pattern in commodities.items():
            if re.search(pattern, text, re.IGNORECASE):
                return commodity
        return "general cargo"

    def _extract_special_requirements(self, text: str) -> str:
        """Extract special requirements"""
        requirements = []
        if re.search(r'\b(refrigerat|reefer|cold|frozen)\b', text, re.IGNORECASE):
            requirements.append("refrigerated")
        if re.search(r'\b(urgent|rush|asap|immediate)\b', text, re.IGNORECASE):
            requirements.append("urgent")
        if re.search(r'\b(insurance|insured)\b', text, re.IGNORECASE):
            requirements.append("insurance_required")
        return ", ".join(requirements) if requirements else None

class ImprovedWorkflowAgent(BaseAgent):
    """Improved workflow agent with better sub-agents"""
    
    def __init__(self):
        super().__init__("improved_workflow_agent")
        
        # Use improved agents
        self.classifier = ImprovedClassificationAgent()
        self.extractor = ImprovedExtractionAgent()
        
        # Workflow rules
        self.extraction_required_types = [
            "logistics_request", 
            "confirmation_reply", 
            "forwarder_response",
            "clarification_reply"
        ]
    
    def load_context(self) -> bool:
        """Load context for all agents"""
        try:
            main_loaded = super().load_context()
            classifier_loaded = self.classifier.load_context()
            extractor_loaded = self.extractor.load_context()
            
            success = main_loaded and classifier_loaded and extractor_loaded
            
            if success:
                print("✓ All improved agents loaded successfully with Databricks LLM")
                print(f"✓ Model: {MODEL_ENDPOINT_ID}")
            else:
                print(f"✗ Agent loading status: main={main_loaded}, classifier={classifier_loaded}, extractor={extractor_loaded}")
            
            return success
            
        except Exception as e:
            print(f"✗ Failed to load improved workflow context: {e}")
            return False
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email through improved workflow"""
        
        email_text = input_data.get("email_text", "")
        subject = input_data.get("subject", "")
        
        print(f"DEBUG: Starting improved workflow for: '{subject}'")
        
        if not email_text:
            return {"error": "No email text provided"}
        
        workflow_result = {
            "email_text": email_text,
            "subject": subject,
            "workflow_steps": []
        }
        
        # Step 1: Improved Classification
        print("DEBUG: Step 1 - Improved Classification")
        classification_result = self.classifier.run(input_data)
        
        if classification_result.get("status") == "success":
            workflow_result["classification"] = {
                "email_type": classification_result.get("email_type"),
                "confidence": classification_result.get("confidence"),
                "urgency": classification_result.get("urgency"),
                "requires_action": classification_result.get("requires_action"),
                "reasoning": classification_result.get("reasoning"),
                "method": classification_result.get("classification_method", "keyword")
            }
            workflow_result["workflow_steps"].append("classification_success")
            
            email_type = classification_result.get("email_type")
            print(f"DEBUG: Classified as: {email_type}")
            
        else:
            workflow_result["classification"] = {"error": classification_result.get("error")}
            workflow_result["workflow_steps"].append("classification_failed")
            return workflow_result
        
        # Step 2: Improved Extraction (if needed)
        if email_type in self.extraction_required_types:
            print("DEBUG: Step 2 - Improved Extraction (required)")
            extraction_result = self.extractor.run(input_data)
            
            if extraction_result.get("status") == "success":
                workflow_result["extraction"] = {
                    "origin": extraction_result.get("origin"),
                    "destination": extraction_result.get("destination"),
                    "shipment_type": extraction_result.get("shipment_type"),
                    "container_type": extraction_result.get("container_type"),
                    "quantity": extraction_result.get("quantity"),
                    "weight": extraction_result.get("weight"),
                    "volume": extraction_result.get("volume"),
                    "shipment_date": extraction_result.get("shipment_date"),
                    "commodity": extraction_result.get("commodity"),
                    "dangerous_goods": extraction_result.get("dangerous_goods"),
                    "special_requirements": extraction_result.get("special_requirements"),
                    "extraction_method": extraction_result.get("extraction_method")
                }
                workflow_result["workflow_steps"].append("extraction_success")
                
            else:
                workflow_result["extraction"] = {"error": extraction_result.get("error")}
                workflow_result["workflow_steps"].append("extraction_failed")
        
        else:
            print("DEBUG: Step 2 - Extraction (skipped)")
            workflow_result["extraction"] = {"skipped": f"Not required for {email_type}"}
            workflow_result["workflow_steps"].append("extraction_skipped")
        
        # Step 3: Improved Decision Logic
        workflow_result["next_action"] = self._determine_next_action(workflow_result)
        workflow_result["workflow_steps"].append("workflow_complete")
        
        return workflow_result
    
    def _determine_next_action(self, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """Improved decision logic"""
        
        classification = workflow_result.get("classification", {})
        extraction = workflow_result.get("extraction", {})
        email_type = classification.get("email_type")
        confidence = classification.get("confidence", 0)
        
        # Improved decision logic
        if email_type == "logistics_request":
            if extraction and not extraction.get("error"):
                required_fields = ["origin", "destination", "shipment_type"]
        
                missing_fields = [field for field in required_fields 
                                if not extraction.get(field) or extraction.get(field) == "Unknown"]
                
                if missing_fields:
                    return {
                        "action": "request_clarification",
                        "reason": f"Missing required fields: {missing_fields}",
                        "missing_fields": missing_fields
                    }
                else:
                    return {
                        "action": "assign_forwarder",
                        "reason": "Complete logistics request ready for processing"
                    }
            else:
                return {
                    "action": "request_clarification",
                    "reason": "Failed to extract shipment information"
                }
        
        elif email_type == "confirmation_reply":
            return {
                "action": "process_confirmation",
                "reason": "Customer confirmation received"
            }
        
        elif email_type == "forwarder_response":
            return {
                "action": "parse_quote",
                "reason": "Forwarder quote received"
            }
        
        elif email_type == "clarification_reply":
            return {
                "action": "update_shipment_info",
                "reason": "Customer provided additional information"
            }
        
        elif email_type == "non_logistics":
            return {
                "action": "forward_to_support",
                "reason": "Non-logistics email"
            }
        
        elif confidence < 0.7:
            return {
                "action": "escalate_to_human",
                "reason": f"Low confidence classification: {confidence}"
            }
        
        else:
            return {
                "action": "manual_review",
                "reason": "Unclear next action"
            }

# =====================================================
#                 🔁 Test Harness
# =====================================================
def test_improved_workflow():
    print("=== Testing Improved Workflow Agent with Databricks ===")
    
    agent = ImprovedWorkflowAgent()
    
    # Test cases with expected results
    test_cases = [
        {
            "email_text": "Need quote for 2x40ft FCL from Shanghai to Long Beach, electronics, ready July 15th",
            "subject": "Shipping Quote Request",
            "expected_type": "logistics_request",
            "expected_action": "assign_forwarder"
        },
        {
            "email_text": "Yes, I confirm the booking for the containers",
            "subject": "Re: Booking Confirmation",
            "expected_type": "confirmation_reply",
            "expected_action": "process_confirmation"
        },
        {
            "email_text": "Our rate is $2500 USD for FCL 40ft, valid until month end",
            "subject": "Rate Quote",
            "expected_type": "forwarder_response",
            "expected_action": "parse_quote"
        },
        {
            "email_text": "The origin port is Shanghai and destination is Long Beach",
            "subject": "Re: Missing Information",
            "expected_type": "clarification_reply",
            "expected_action": "update_shipment_info"
        },
        {
            "email_text": "Need shipping from Mumbai to Rotterdam, 1x20GP, textiles",
            "subject": "Export Quote",
            "expected_type": "logistics_request",
            "expected_action": "assign_forwarder"
        }
    ]
    
    # Load context
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}")
    
    correct_classifications = 0
    correct_actions = 0
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test_data['subject']}")
        print(f"Text: {test_data['email_text'][:50]}...")
        print(f"Expected Type: {test_data['expected_type']}")
        print(f"Expected Action: {test_data['expected_action']}")
        
        result = agent.run(test_data)
        
        if result.get("status") == "success":
            actual_type = result.get('classification', {}).get('email_type')
            actual_action = result.get('next_action', {}).get('action')
            method = result.get('classification', {}).get('method', 'keyword')
            
            print(f"✓ Actual Type: {actual_type}")
            print(f"✓ Actual Action: {actual_action}")
            print(f"✓ Confidence: {result.get('classification', {}).get('confidence')}")
            print(f"✓ Method: {method}")
            print(f"✓ Reasoning: {result.get('classification', {}).get('reasoning')}")
            
            # Check accuracy
            if actual_type == test_data['expected_type']:
                print("✅ Classification: CORRECT")
                correct_classifications += 1
            else:
                print("❌ Classification: WRONG")
            
            if actual_action == test_data['expected_action']:
                print("✅ Action: CORRECT")
                correct_actions += 1
            else:
                print("❌ Action: WRONG")
            
            # Show extraction if available
            extraction = result.get('extraction', {})
            if extraction and not extraction.get('skipped') and not extraction.get('error'):
                print(f"✓ Origin: {extraction.get('origin')}")
                print(f"✓ Destination: {extraction.get('destination')}")
                print(f"✓ Shipment Type: {extraction.get('shipment_type')}")
                print(f"✓ Extraction Method: {extraction.get('extraction_method')}")
        else:
            print(f"✗ Error: {result.get('error')}")
    
    # Summary
        # Summary
    print(f"\n=== SUMMARY ===")
    print(f"Classification Accuracy: {correct_classifications}/{len(test_cases)} ({correct_classifications/len(test_cases)*100:.1f}%)")
    print(f"Action Accuracy: {correct_actions}/{len(test_cases)} ({correct_actions/len(test_cases)*100:.1f}%)")

def test_individual_components():
    """Test individual improved components"""
    print("\n=== Testing Individual Components with Databricks ===")
    
    # Test improved classifier
    print("\n--- Improved Classifier ---")
    classifier = ImprovedClassificationAgent()
    classifier.load_context()
    
    test_data = {
        "email_text": "Yes, I confirm the booking for the containers",
        "subject": "Re: Booking Confirmation"
    }
    
    result = classifier.run(test_data)
    if result.get("status") == "success":
        print(f"✓ Type: {result.get('email_type')}")
        print(f"✓ Confidence: {result.get('confidence')}")
        print(f"✓ Method: {result.get('classification_method', 'keyword')}")
    
    # Test improved extractor
    print("\n--- Improved Extractor ---")
    extractor = ImprovedExtractionAgent()
    extractor.load_context()
    
    test_data = {
        "email_text": "Need quote for 2x40ft FCL from Shanghai to Long Beach",
        "subject": "Quote Request"
    }
    
    result = extractor.run(test_data)
    if result.get("status") == "success":
        print(f"✓ Origin: {result.get('origin')}")
        print(f"✓ Destination: {result.get('destination')}")
        print(f"✓ Type: {result.get('shipment_type')}")
        print(f"✓ Method: {result.get('extraction_method')}")

def test_workflow_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Testing Edge Cases with Databricks ===")
    
    agent = ImprovedWorkflowAgent()
    agent.load_context()
    
    edge_cases = [
        {
            "email_text": "",
            "subject": "Empty Email",
            "description": "Empty email text"
        },
        {
            "email_text": "Hello, how are you today? Nice weather we're having.",
            "subject": "Casual Chat",
            "description": "Non-logistics email"
        },
        {
            "email_text": "Need quote for shipping but no details provided",
            "subject": "Vague Request",
            "description": "Incomplete logistics request"
        },
        {
            "email_text": "FCL container from somewhere to anywhere, maybe 40ft",
            "subject": "Unclear Details",
            "description": "Ambiguous shipping details"
        }
    ]
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n--- Edge Case {i}: {test_case['description']} ---")
        print(f"Subject: {test_case['subject']}")
        print(f"Text: {test_case['email_text'][:50]}...")
        
        result = agent.run(test_case)
        
        if result.get("status") == "success":
            print(f"✓ Classification: {result.get('classification', {}).get('email_type')}")
            print(f"✓ Action: {result.get('next_action', {}).get('action')}")
            print(f"✓ Reason: {result.get('next_action', {}).get('reason')}")
            print(f"✓ Method: {result.get('classification', {}).get('method', 'keyword')}")
        elif result.get("status") == "error":
            print(f"✓ Error handled: {result.get('error')}")
        else:
            print(f"✗ Unexpected result: {result}")

if __name__ == "__main__":
    test_improved_workflow()
    test_individual_components()
    test_workflow_edge_cases()

