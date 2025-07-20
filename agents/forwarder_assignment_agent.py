"""Forwarder Assignment Agent: Assigns forwarders based on country presence and capabilities."""

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

class ForwarderAssignmentAgent(BaseAgent):
    """Agent for assigning forwarders based on country presence and shipment requirements."""

    def __init__(self):
        super().__init__("forwarder_assignment_agent")
        
        # Forwarder database with country presence
        self.forwarders = {
            "DHL Global Forwarding": {
                "countries": ["AE", "IN", "CN", "US", "DE", "GB", "FR", "NL", "SG", "HK"],
                "specialties": ["electronics", "machinery", "textiles", "general"],
                "service_levels": ["premium", "standard", "economy"],
                "email": "rates@dhl.com",
                "contact": "DHL Rate Team"
            },
            "Kuehne + Nagel": {
                "countries": ["AE", "IN", "CN", "US", "DE", "GB", "FR", "NL", "SG", "HK", "AU"],
                "specialties": ["machinery", "electronics", "automotive", "general"],
                "service_levels": ["premium", "standard"],
                "email": "quotes@kuehne-nagel.com",
                "contact": "KN Rate Team"
            },
            "DB Schenker": {
                "countries": ["AE", "IN", "CN", "US", "DE", "GB", "FR", "NL", "SG", "HK", "JP"],
                "specialties": ["electronics", "machinery", "general"],
                "service_levels": ["premium", "standard"],
                "email": "rates@dbschenker.com",
                "contact": "DB Schenker Rate Team"
            },
            "Expeditors": {
                "countries": ["AE", "IN", "CN", "US", "DE", "GB", "FR", "NL", "SG", "HK"],
                "specialties": ["electronics", "machinery", "textiles", "general"],
                "service_levels": ["premium", "standard"],
                "email": "quotes@expeditors.com",
                "contact": "Expeditors Rate Team"
            },
            "Panalpina": {
                "countries": ["AE", "IN", "CN", "US", "DE", "GB", "FR", "NL", "SG", "HK"],
                "specialties": ["machinery", "electronics", "general"],
                "service_levels": ["premium", "standard"],
                "email": "rates@panalpina.com",
                "contact": "Panalpina Rate Team"
            }
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assign forwarders based on origin/destination countries and shipment requirements.
        
        Expected input:
        - origin_country: Origin country code (e.g., "AE")
        - destination_country: Destination country code (e.g., "IN")
        - commodity: Shipment commodity type
        - container_type: Container type
        - quantity: Number of containers
        - weight: Shipment weight
        - volume: Shipment volume
        - shipment_date: Ready date
        - thread_id: Thread identifier
        """
        origin_country = input_data.get("origin_country", "").upper()
        destination_country = input_data.get("destination_country", "").upper()
        commodity = input_data.get("commodity", "").lower()
        container_type = input_data.get("container_type", "")
        quantity = input_data.get("quantity", 1)
        weight = input_data.get("weight", "")
        volume = input_data.get("volume", "")
        shipment_date = input_data.get("shipment_date", "")
        thread_id = input_data.get("thread_id", "")

        if not origin_country or not destination_country:
            return {"error": "Origin and destination countries are required"}

        if not self.client:
            return {"error": "LLM client not initialized"}

        return self._assign_forwarders(origin_country, destination_country, commodity, container_type, quantity, weight, volume, shipment_date, thread_id)

    def _assign_forwarders(self, origin_country: str, destination_country: str, commodity: str, container_type: str, quantity: int, weight: str, volume: str, shipment_date: str, thread_id: str) -> Dict[str, Any]:
        """Assign forwarders using LLM function calling."""
        try:
            function_schema = {
                "name": "assign_forwarders",
                "description": "Assign forwarders based on country presence and shipment requirements",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "assigned_forwarders": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "forwarder_name": {"type": "string"},
                                    "email": {"type": "string"},
                                    "contact": {"type": "string"},
                                    "assignment_reason": {"type": "string"},
                                    "priority": {"type": "string", "enum": ["primary", "secondary", "backup"]},
                                    "specialty_match": {"type": "boolean"},
                                    "country_coverage": {"type": "string"}
                                },
                                "required": ["forwarder_name", "email", "contact", "assignment_reason", "priority", "specialty_match", "country_coverage"]
                            },
                            "description": "List of assigned forwarders"
                        },
                        "total_forwarders_assigned": {
                            "type": "integer",
                            "description": "Total number of forwarders assigned"
                        },
                        "assignment_strategy": {
                            "type": "string",
                            "description": "Strategy used for forwarder assignment"
                        },
                        "confidence_score": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence in forwarder assignment"
                        }
                    },
                    "required": ["assigned_forwarders", "total_forwarders_assigned", "assignment_strategy", "confidence_score"]
                }
            }

            # Create forwarder database for LLM
            forwarder_db = []
            for name, details in self.forwarders.items():
                forwarder_db.append({
                    "name": name,
                    "countries": details["countries"],
                    "specialties": details["specialties"],
                    "service_levels": details["service_levels"],
                    "email": details["email"],
                    "contact": details["contact"]
                })

            prompt = f"""
You are an expert logistics forwarder assignment specialist. Assign forwarders based on country presence and shipment requirements.

AVAILABLE FORWARDERS:
{json.dumps(forwarder_db, indent=2)}

SHIPMENT DETAILS:
- Origin Country: {origin_country}
- Destination Country: {destination_country}
- Commodity: {commodity}
- Container Type: {container_type}
- Quantity: {quantity}
- Weight: {weight}
- Volume: {volume}
- Shipment Date: {shipment_date}

ASSIGNMENT RULES:
1. Only assign forwarders that have presence in BOTH origin and destination countries
2. Prioritize forwarders with specialty matching the commodity
3. Assign 2-3 forwarders maximum (1 primary, 1-2 secondary/backup)
4. Consider service levels and capabilities
5. Ensure geographic coverage for the route

ASSIGNMENT STRATEGY:
- Primary: Best match for commodity and route
- Secondary: Good coverage with competitive rates
- Backup: Reliable coverage as fallback

Determine the best forwarders for this shipment and provide assignment reasoning.
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
            result["assignment_method"] = "llm_function_call"
            result["thread_id"] = thread_id
            result["origin_country"] = origin_country
            result["destination_country"] = destination_country
            
            # Validate and correct result if needed
            if not result.get("assigned_forwarders"):
                result["assigned_forwarders"] = []
                result["total_forwarders_assigned"] = 0
                result["confidence_score"] = 0.0

            # Ensure confidence is within bounds
            confidence = result.get("confidence_score", 0.5)
            if not (0.0 <= confidence <= 1.0):
                result["confidence_score"] = max(0.0, min(1.0, confidence))

            self.logger.info(f"Forwarder assignment successful: {result['total_forwarders_assigned']} forwarders assigned (confidence: {result['confidence_score']:.2f})")
            
            return result

        except Exception as e:
            self.logger.error(f"Forwarder assignment failed: {e}")
            return {"error": f"Forwarder assignment failed: {str(e)}"}

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_forwarder_assignment_agent():
    print("=== Testing Forwarder Assignment Agent ===")
    agent = ForwarderAssignmentAgent()
    
    if not agent.load_context():
        print("✗ Failed to load context")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "AE to IN Electronics",
            "origin_country": "AE",
            "destination_country": "IN",
            "commodity": "electronics",
            "container_type": "40HC",
            "quantity": 2,
            "weight": "25,000 kg",
            "volume": "35 CBM",
            "shipment_date": "2024-04-20"
        },
        {
            "name": "CN to US Machinery",
            "origin_country": "CN",
            "destination_country": "US",
            "commodity": "machinery",
            "container_type": "40GP",
            "quantity": 1,
            "weight": "15,000 kg",
            "volume": "25 CBM",
            "shipment_date": "2024-05-15"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        result = agent.run(test_case)
        
        if result.get("status") == "success":
            assigned_forwarders = result.get("assigned_forwarders", [])
            total_assigned = result.get("total_forwarders_assigned", 0)
            confidence = result.get("confidence_score", 0.0)
            strategy = result.get("assignment_strategy", "")
            
            print(f"✓ Forwarders Assigned: {total_assigned}")
            print(f"✓ Confidence: {confidence:.2f}")
            print(f"✓ Strategy: {strategy}")
            
            for i, forwarder in enumerate(assigned_forwarders, 1):
                print(f"  {i}. {forwarder.get('forwarder_name')} ({forwarder.get('priority')})")
                print(f"     Email: {forwarder.get('email')}")
                print(f"     Reason: {forwarder.get('assignment_reason')}")
                print(f"     Specialty Match: {forwarder.get('specialty_match')}")
                print(f"     Country Coverage: {forwarder.get('country_coverage')}")
            
            if total_assigned > 0:
                print("✓ Forwarder assignment successful!")
            else:
                print("✗ No forwarders assigned")
        else:
            print(f"✗ Test failed: {result.get('error')}")

if __name__ == "__main__":
    test_forwarder_assignment_agent() 