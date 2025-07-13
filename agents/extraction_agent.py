"""Shipment information extraction agent"""

# =====================================================
#                 LLM CONFIGURATION
# =====================================================
# Databricks Configuration
DATABRICKS_TOKEN = "dapi81b45be7f09611a410fc3e5104a8cadf-3"
DATABRICKS_BASE_URL = "https://adb-1825279086009288.8.azuredatabricks.net/serving-endpoints"
MODEL_ENDPOINT_ID = "databricks-meta-llama-3-3-70b-instruct"

import os
import sys
from typing import Dict, Any, Optional
import re

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import base agent with error handling
from agents.base_agent import BaseAgent

class ExtractionAgent(BaseAgent):
    """Agent for extracting structured shipment information from emails"""

    def __init__(self):
        super().__init__("extraction_agent")
        # Common patterns for extraction
        self.container_patterns = {
            'fcl': r'\b(fcl|full\s*container|40ft|20ft|40hc|20gp)\b',
            'lcl': r'\b(lcl|less\s*container|consolidation)\b'
        }
        self.date_patterns = r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b'
        self.weight_patterns = r'\b(\d+(?:\.\d+)?)\s*(kg|kgs|ton|tons|mt|lbs|pounds)\b'
        self.volume_patterns = r'\b(\d+(?:\.\d+)?)\s*(cbm|m3|cubic\s*meter|ft3|cubic\s*feet)\b'

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract shipment information from email content"""
        email_text = input_data.get("email_text", "")
        subject = input_data.get("subject", "")

        if not email_text:
            return {"error": "No email text provided"}

        # Try LLM extraction first, then fallback
        if self.client:
            llm_result = self._llm_extract(subject, email_text)
            if llm_result and "error" not in llm_result:
                # Enhance with regex extraction
                enhanced_result = self._enhance_with_regex(email_text, llm_result)
                return enhanced_result

        # Fallback to regex extraction
        return self._regex_extract(subject, email_text)

    def _llm_extract(self, subject: str, email_text: str) -> Dict[str, Any]:
        """Databricks LLM-based extraction"""
        try:
            prompt = f"""Extract shipment information from this email. Return ONLY valid JSON:

Subject: {subject}
Body: {email_text}

Extract these fields:
- origin: Port/city of departure
- destination: Port/city of arrival  
- shipment_type: "FCL" or "LCL"
- container_type: "20GP", "40GP", "40HC", etc.
- quantity: Number of containers/packages
- weight: Weight with unit
- volume: Volume with unit
- shipment_date: Departure date
- commodity: Type of goods
- dangerous_goods: true/false
- special_requirements: Any special needs

JSON format:
{{"origin": "Shanghai", "destination": "Long Beach", "shipment_type": "FCL", "container_type": "40HC", "quantity": 2, "weight": "25 tons", "volume": "67 CBM", "shipment_date": "2024-02-15", "commodity": "electronics", "dangerous_goods": false, "special_requirements": "none"}}"""

            response = self.client.chat.completions.create(
                model=MODEL_ENDPOINT_ID,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=400
            )

            result_text = response.choices[0].message.content

            result_text = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                import json
                json_str = json_match.group(0)
                extracted_data = json.loads(json_str)
                extracted_data["extraction_method"] = "databricks_llm"
                return extracted_data
            else:
                return {"error": "No JSON found in LLM response"}

        except Exception as e:
            return {"error": f"Databricks LLM extraction failed: {str(e)}"}

    def _regex_extract(self, subject: str, email_text: str) -> Dict[str, Any]:
        """Regex-based fallback extraction"""
        combined_text = f"{subject} {email_text}".lower()

        # Extract shipment type
        shipment_type = "FCL" if re.search(self.container_patterns['fcl'], combined_text, re.IGNORECASE) else \
                       "LCL" if re.search(self.container_patterns['lcl'], combined_text, re.IGNORECASE) else "Unknown"

        # Extract container info
        container_match = re.search(r'\b(\d+)\s*x?\s*(20|40)\s*(gp|hc|ft)?\b', combined_text, re.IGNORECASE)
        quantity = int(container_match.group(1)) if container_match else 1
        container_type = f"{container_match.group(2)}GP" if container_match else "40GP"

        # Extract weight
        weight_match = re.search(self.weight_patterns, combined_text, re.IGNORECASE)
        weight = f"{weight_match.group(1)} {weight_match.group(2)}" if weight_match else None

        # Extract volume
        volume_match = re.search(self.volume_patterns, combined_text, re.IGNORECASE)
        volume = f"{volume_match.group(1)} {volume_match.group(2)}" if volume_match else None

        # Extract ports (simple heuristic)
        ports = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', email_text)
        origin = ports[0] if len(ports) > 0 else None
        destination = ports[1] if len(ports) > 1 else None

        # Extract dates
        date_matches = re.findall(self.date_patterns, combined_text, re.IGNORECASE)
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
            "commodity": self._extract_commodity(combined_text),
            "dangerous_goods": dangerous_goods,
            "special_requirements": self._extract_special_requirements(combined_text),
            "extraction_method": "regex_fallback"
        }

    def _enhance_with_regex(self, email_text: str, llm_result: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance LLM results with regex extraction"""
        regex_result = self._regex_extract("", email_text)
        for key, value in regex_result.items():
            if key not in llm_result or not llm_result[key]:
                llm_result[key] = value
        llm_result["extraction_method"] = "databricks_llm_enhanced"
        return llm_result

    def _extract_commodity(self, text: str) -> Optional[str]:
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

    def _extract_special_requirements(self, text: str) -> Optional[str]:
        """Extract special requirements"""
        requirements = []
        if re.search(r'\b(refrigerat|reefer|cold|frozen)\b', text, re.IGNORECASE):
            requirements.append("refrigerated")
        if re.search(r'\b(urgent|rush|asap|immediate)\b', text, re.IGNORECASE):
            requirements.append("urgent")
        if re.search(r'\b(insurance|insured)\b', text, re.IGNORECASE):
            requirements.append("insurance_required")
        return ", ".join(requirements) if requirements else None

# =====================================================
#                 🔁 Local Test Harness
# =====================================================
def test_extraction_agent():
    print("=== Testing Extraction Agent with Databricks ===")
    agent = ExtractionAgent()
    
    test_cases = [
        {
            "email_text": "Need quote for 2x40ft FCL Shanghai to Long Beach, ready July 15th, electronics cargo, 25 tons total",
            "subject": "Shipping Quote Request"
        },
        {
            "email_text": "LCL shipment from Hamburg to New York, 5 CBM, machinery parts, dangerous goods included",
            "subject": "LCL Quote"
        },
        {
            "email_text": "1x20GP container from Mumbai to Rotterdam, textiles, 15 tons, urgent delivery required",
            "subject": "Container Booking"
        },
        {
            "email_text": "FCL 40HC from Singapore to Los Angeles, food products, refrigerated container needed",
            "subject": "Reefer Shipment"
        }
    ]
    
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}")
    print(f"✓ LLM Client: {'Connected' if agent.client else 'Not available'}")
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test_data['subject']} - {test_data['email_text'][:40]}...")
        
        result = agent.run(test_data)
        if result.get("status") == "success":
            print(f"✓ Origin: {result.get('origin', 'MISSING')}")
            print(f"✓ Destination: {result.get('destination', 'MISSING')}")
            print(f"✓ Shipment Type: {result.get('shipment_type', 'MISSING')}")
            print(f"✓ Container: {result.get('container_type', 'MISSING')}")
            print(f"✓ Quantity: {result.get('quantity', 'MISSING')}")
            print(f"✓ Weight: {result.get('weight', 'MISSING')}")
            print(f"✓ Volume: {result.get('volume', 'MISSING')}")
            print(f"✓ Date: {result.get('shipment_date', 'MISSING')}")
            print(f"✓ Commodity: {result.get('commodity', 'MISSING')}")
            print(f"✓ Dangerous Goods: {result.get('dangerous_goods', 'MISSING')}")
            print(f"✓ Special Req: {result.get('special_requirements', 'MISSING')}")
            print(f"✓ Method: {result.get('extraction_method', 'MISSING')}")
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_extraction_agent()
