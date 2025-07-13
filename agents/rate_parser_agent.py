"""Rate Parser Agent using Databricks LLM with function calling and robust test harness."""

import os
import sys
from typing import Dict, Any, Optional
import re
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from agents.base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class RateParserAgent(BaseAgent):
    """LLM-based agent for parsing rate quotes from forwarder email responses, with function calling support."""

    def __init__(self):
        super().__init__("rate_parser_agent")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        email_text = input_data.get("email_text", "")
        subject = input_data.get("subject", "")

        if not email_text:
            return {"error": "No email text provided"}

        if self.client:
            print("[INFO] Using LLM extraction (function calling if available)")
            try:
                return self._llm_function_call(subject, email_text)
            except Exception as e:
                print(f"[WARN] LLM function call failed: {e}")
                return self._llm_extract(subject, email_text)
        else:
            print("[INFO] Using regex extraction (LLM client not available)")
            return self._regex_extract(subject, email_text)

    def _llm_function_call(self, subject: str, email_text: str) -> Dict[str, Any]:
        """Use Databricks LLM function calling for structured extraction."""
        function_schema = {
            "name": "extract_rate_quote",
            "description": "Extract rate quote details from a forwarder email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "Origin port/city"},
                    "destination": {"type": "string", "description": "Destination port/city"},
                    "shipment_type": {"type": "string", "description": "FCL or LCL"},
                    "container_type": {"type": "string", "description": "e.g., 20GP, 40GP, 40HC"},
                    "quantity": {"type": "integer", "description": "Number of containers/packages"},
                    "weight": {"type": "string", "description": "Weight with unit"},
                    "volume": {"type": "string", "description": "Volume with unit"},
                    "shipment_date": {"type": "string", "description": "Departure date"},
                    "commodity": {"type": "string", "description": "Type of goods"},
                    "dangerous_goods": {"type": "boolean", "description": "Dangerous goods true/false"},
                    "special_requirements": {"type": "string", "description": "Special needs"},
                    "rates": {
                        "type": "array",
                        "description": "List of rate objects",
                        "items": {
                            "type": "object",
                            "properties": {
                                "amount": {"type": "number", "description": "Rate amount"},
                                "currency": {"type": "string", "description": "Currency code (USD, EUR, etc.)"}
                            },
                            "required": ["amount", "currency"]
                        }
                    },
                    "validity": {
                        "type": "string",
                        "description": "Validity period for the quote (e.g., 'March 31st')"
                    },
                    "terms": {
                        "type": "object",
                        "description": "Terms of the quote",
                        "properties": {
                            "incoterms": {"type": ["string", "null"], "description": "Incoterms (e.g., 'FOB', 'CIF')"},
                            "insurance_included": {"type": "boolean", "description": "Whether insurance is included"},
                            "door_to_door": {"type": "boolean", "description": "Whether door-to-door service is included"}
                        },
                        "required": ["incoterms", "insurance_included", "door_to_door"]
                    }
                },
                "required": ["rates", "validity", "terms"]
            }
        }

        prompt = f"""
Extract the following information from this email:
- origin, destination, shipment_type, container_type, quantity, weight, volume, shipment_date, commodity, dangerous_goods, special_requirements
- rates: List of objects with amount and currency (e.g., [{{"amount": 2500, "currency": "USD"}}])
- validity: Validity period for the quote (e.g., "March 31st")
- terms: Dictionary with incoterms (e.g., "FOB"), insurance_included (true/false), door_to_door (true/false)

Email:
Subject: {subject}
Body: {email_text}
"""

        response = self.client.chat.completions.create(
            model=self.config.get("model_name", "databricks-meta-llama-3-3-70b-instruct"),
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "type": "function",
                "function": function_schema
            }],
            tool_choice={"type": "function", "function": {"name": function_schema["name"]}},
            temperature=0.0,
            max_tokens=600
        )
        tool_calls = getattr(response.choices[0].message, "tool_calls", None)
        if not tool_calls:
            raise Exception("No tool_calls in LLM response")
        tool_args = tool_calls[0].function.arguments
        if isinstance(tool_args, str):
            import json
            tool_args = json.loads(tool_args)
        result = dict(tool_args)
        result["extraction_method"] = "databricks_llm_function_call"
        return result


    def _llm_extract(self, subject: str, email_text: str) -> Dict[str, Any]:
        """Classic LLM JSON extraction (no function calling)."""
        prompt = f"""
Extract the following information from this email and return ONLY valid JSON:
- origin, destination, shipment_type, container_type, quantity, weight, volume, shipment_date, commodity, dangerous_goods, special_requirements
- rates: List of objects with amount and currency (e.g., [{{"amount": 2500, "currency": "USD"}}])
- validity: Validity period for the quote (e.g., "March 31st")
- terms: Dictionary with incoterms (e.g., "FOB"), insurance_included (true/false), door_to_door (true/false)

Email:
Subject: {subject}
Body: {email_text}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.config.get("model_name", "databricks-meta-llama-3-3-70b-instruct"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=600
            )
            result_text = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                result["extraction_method"] = "databricks_llm_json"
                return result
            else:
                return {"error": "No JSON found in LLM response"}
        except Exception as e:
            return {"error": f"Databricks LLM extraction failed: {str(e)}"}

    def _regex_extract(self, subject: str, email_text: str) -> Dict[str, Any]:
        """Fallback regex-based extraction (stub)."""
        # You can implement improved regex extraction here if desired.
        return {
            "origin": None,
            "destination": None,
            "shipment_type": None,
            "container_type": None,
            "quantity": None,
            "weight": None,
            "volume": None,
            "shipment_date": None,
            "commodity": None,
            "dangerous_goods": None,
            "special_requirements": None,
            "rates": [],
            "validity": None,
            "terms": {"incoterms": None, "insurance_included": False, "door_to_door": False},
            "extraction_method": "regex"
        }

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_rate_parser_agent():
    print("=== Testing Extraction Agent (Databricks LLM + Function Calling) ===")
    agent = RateParserAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}, Has LLM client: {bool(agent.client)}")

    test_cases = [
        # 1. Standard FCL quote, USD, insurance, door-to-door
        {
            "email_text": "Our rate is $2500 USD for FCL 40ft, valid until March 31st. Includes insurance and is door-to-door.",
            "subject": "Rate Quote"
        },
        # 2. LCL quote, EUR, machinery, dangerous goods, expiry
        {
            "email_text": "LCL shipment from Hamburg to New York, 5 CBM, machinery parts, dangerous goods included. The price is €2000 per container, all-in. Expires on April 15th.",
            "subject": "LCL Quote"
        },
        # 3. FOB incoterm, USD, validity phrase variation
        {
            "email_text": "Our rate is $1800 USD per container, FOB Shanghai, valid until September 1st.",
            "subject": "FOB Rate"
        },
        # 4. DAP incoterm, EUR, insurance, expiry date
        {
            "email_text": "Price: €2200, includes insurance and is DAP. Expires on 31st December.",
            "subject": "DAP Quote"
        },
        # 5. Door-to-door, LCL, date in DD/MM/YYYY
        {
            "email_text": "LCL shipment, 5 CBM, textiles, from Singapore to Los Angeles. Valid till 15/09/2024. Door-to-door.",
            "subject": "LCL Door-to-Door"
        },
        # 6. Multiple rates, multiple currencies
        {
            "email_text": "We offer $2500 USD for FCL and €2100 EUR for LCL. Valid until May 20th.",
            "subject": "Multi-rate Offer"
        },
        # 7. Ambiguous/worded price
        {
            "email_text": "The total cost is two thousand five hundred dollars, valid until June 30th.",
            "subject": "Worded Price"
        },
        # 8. No shipment details (edge case)
        {
            "email_text": "No shipment details provided.",
            "subject": "Empty"
        },
        # 9. Insurance not included, DDP incoterm
        {
            "email_text": "Our quote is $3000 USD, DDP, valid till July 10th. Insurance not included.",
            "subject": "DDP No Insurance"
        },
        # 10. Urgent, special requirements, dangerous goods
        {
            "email_text": "Urgent shipment, 1x20GP, chemicals, dangerous goods, from Mumbai to Rotterdam. $3200 USD, valid until August 15th.",
            "subject": "Urgent Dangerous Goods"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test_case['subject']}")
        result = agent.run(test_case)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_rate_parser_agent()
