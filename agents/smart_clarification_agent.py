"""Smart Clarification Agent: Intelligent clarification requests based on shipment context and extracted data."""

import json
from typing import Dict, Any, List
try:
    from .base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class SmartClarificationAgent(BaseAgent):
    """Smart agent that generates context-aware clarification requests."""

    def __init__(self):
        super().__init__("smart_clarification_agent")
        
        # Dangerous goods assessment
        self.dangerous_commodities = {
            "chemicals": ["chemicals", "chemical", "acid", "alkali", "solvent", "paint", "adhesive", "resin"],
            "batteries": ["battery", "batteries", "lithium", "lead-acid", "nickel"],
            "flammable": ["fuel", "gasoline", "diesel", "oil", "lubricant", "alcohol", "perfume"],
            "explosives": ["fireworks", "ammunition", "gunpowder", "explosive"],
            "toxic": ["pesticide", "herbicide", "insecticide", "poison", "toxic"],
            "corrosive": ["corrosive", "caustic", "bleach", "cleaning_chemical"],
            "radioactive": ["radioactive", "nuclear", "uranium", "plutonium"],
            "medical": ["medical_waste", "biological", "pathogen", "virus", "bacteria"]
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate smart clarification requests based on context.
        
        Expected input:
        - extraction_data: Dict with extracted shipment info
        - validation_data: Dict with validation results
        - container_standardization_data: Dict with container info
        - port_lookup_data: Dict with port lookup results
        - missing_fields: List of missing field names
        - thread_id: Optional thread identifier
        """
        extraction_data = input_data.get("extraction_data", {})
        validation_data = input_data.get("validation_data", {})
        container_standardization_data = input_data.get("container_standardization_data", {})
        port_lookup_data = input_data.get("port_lookup_data", {})
        missing_fields = input_data.get("missing_fields", [])
        thread_id = input_data.get("thread_id", "")

        # Determine shipment context
        context = self._analyze_shipment_context(extraction_data, container_standardization_data)
        
        # Generate smart clarification fields
        smart_missing_fields = self._generate_smart_missing_fields(
            missing_fields, extraction_data, context
        )
        
        if not smart_missing_fields:
            return {
                "clarification_needed": False,
                "message": "No additional information needed",
                "missing_fields": [],
                "extracted_summary": self._generate_extracted_summary(extraction_data, port_lookup_data, container_standardization_data)
            }

        # Generate clarification message
        clarification_message = self._generate_clarification_message(
            smart_missing_fields, extraction_data, context, port_lookup_data, container_standardization_data
        )

        return {
            "clarification_needed": True,
            "clarification_message": clarification_message,
            "missing_fields": smart_missing_fields,
            "context": context,
            "extracted_summary": self._generate_extracted_summary(extraction_data, port_lookup_data, container_standardization_data),
            "thread_id": thread_id
        }

    def _analyze_shipment_context(self, extraction_data: Dict, container_standardization_data: Dict) -> Dict[str, Any]:
        """Analyze shipment context to determine what type of clarification is needed."""
        
        shipment_type = extraction_data.get("shipment_type", "")
        container_type = extraction_data.get("container_type", "")
        standardized_container = container_standardization_data.get("standard_type", "")
        
        # Determine actual shipment type
        if container_type or standardized_container:
            actual_shipment_type = "FCL"
        elif shipment_type == "LCL":
            actual_shipment_type = "LCL"
        else:
            actual_shipment_type = shipment_type or "UNKNOWN"
        
        # Determine if FCL needs container preference
        needs_container_preference = (
            shipment_type == "FCL" and 
            not container_type and 
            not standardized_container
        )
        
        return {
            "actual_shipment_type": actual_shipment_type,
            "needs_container_preference": needs_container_preference,
            "has_container_type": bool(container_type or standardized_container),
            "is_lcl": actual_shipment_type == "LCL",
            "is_fcl": actual_shipment_type == "FCL"
        }

    def _generate_smart_missing_fields(self, missing_fields: List[str], extraction_data: Dict, context: Dict) -> List[str]:
        """Generate smart missing fields based on context."""
        
        smart_fields = []
        commodity = str(extraction_data.get("commodity", "")).lower()
        
        for field in missing_fields:
            # Skip volume and weight for FCL shipments
            if field in ("volume", "weight") and context["is_fcl"]:
                continue
            # Skip dangerous_goods if commodity is not provided or not potentially dangerous
            if field == "dangerous_goods":
                if not commodity or not self._is_potentially_dangerous(commodity):
                    continue
            # Skip port validation (handled by port lookup)
            if field in ["origin", "destination"]:
                continue
            # Add container preference for FCL without container type
            if field == "container_type" and context["needs_container_preference"]:
                smart_fields.append("container_preference")
                continue
            smart_fields.append(field)
        return smart_fields

    def _is_potentially_dangerous(self, commodity: str) -> bool:
        """Check if commodity is potentially dangerous."""
        commodity_lower = str(commodity).lower()
        
        for category, keywords in self.dangerous_commodities.items():
            for keyword in keywords:
                if keyword in commodity_lower:
                    return True
        return False

    def _generate_extracted_summary(self, extraction_data: Dict, port_lookup_data: Dict, container_standardization_data: Dict) -> str:
        """Generate a summary of extracted and standardized details."""
        
        summary_parts = []
        
        # Origin and destination (use port lookup results if available)
        origin = self._get_port_display_name(extraction_data.get("origin", ""), port_lookup_data, "origin")
        destination = self._get_port_display_name(extraction_data.get("destination", ""), port_lookup_data, "destination")
        
        if origin:
            summary_parts.append(f"• Origin: {origin}")
        if destination:
            summary_parts.append(f"• Destination: {destination}")
            
        # Shipment type
        shipment_type = extraction_data.get("shipment_type")
        if shipment_type:
            summary_parts.append(f"• Shipment Type: {shipment_type}")
            
        # Container type (use standardized if available)
        container_type = container_standardization_data.get("standard_type") or extraction_data.get("container_type")
        if container_type:
            summary_parts.append(f"• Container Type: {container_type}")
            
        # Quantity
        quantity = extraction_data.get("quantity")
        if quantity:
            summary_parts.append(f"• Quantity: {quantity}")
            
        # Weight (only for LCL or if provided)
        weight = extraction_data.get("weight")
        if weight:
            summary_parts.append(f"• Weight: {weight}")
            
        # Volume (only for LCL or if provided)
        volume = extraction_data.get("volume")
        if volume:
            summary_parts.append(f"• Volume: {volume}")
            
        # Commodity
        commodity = extraction_data.get("commodity")
        if commodity:
            summary_parts.append(f"• Commodity: {commodity}")
            
        # Customer info
        customer_name = extraction_data.get("customer_name")
        customer_company = extraction_data.get("customer_company")
        if customer_name:
            summary_parts.append(f"• Customer: {customer_name}")
        if customer_company:
            summary_parts.append(f"• Company: {customer_company}")
            
        return "\n".join(summary_parts)

    def _get_port_display_name(self, port_input: str, port_lookup_data: Dict, port_type: str) -> str:
        """Get display name for port using port lookup results."""
        if not port_input:
            return ""
            
        # Check port lookup results
        results = port_lookup_data.get("results", [])
        for result in results:
            port_name = result.get("port_name", "")
            # Match by port name containing the input or vice versa
            if (str(port_input).lower() in str(port_name).lower() or 
                str(port_name).lower() in str(port_input).lower() or
                result.get("method") == "exact_name_match" or 
                result.get("confidence", 0) > 0.8):
                return port_name
                
        return port_input

    def _generate_clarification_message(self, missing_fields: List[str], extraction_data: Dict, 
                                      context: Dict, port_lookup_data: Dict, container_standardization_data: Dict) -> str:
        """Generate a comprehensive clarification message."""
        
        # Start with extracted summary
        message = "Dear Customer,\n\nThank you for your logistics request. Here's what I understand from your request:\n\n"
        
        extracted_summary = self._generate_extracted_summary(extraction_data, port_lookup_data, container_standardization_data)
        if extracted_summary:
            message += extracted_summary + "\n\n"
        
        # Add clarification questions
        message += "To provide you with the most accurate quote and service, I need the following additional information:\n\n"
        
        # Generate smart questions
        questions = self._generate_smart_questions(missing_fields, context, extraction_data)
        for question in questions:
            message += f"• {question}\n"
            
        message += "\nOnce you provide these details, I'll be able to give you a comprehensive quote and arrange everything for you.\n\nThank you for your cooperation!"
        
        return message

    def _generate_smart_questions(self, missing_fields: List[str], context: Dict, extraction_data: Dict) -> List[str]:
        """Generate smart questions based on context."""
        questions = []
        commodity = str(extraction_data.get("commodity", "")).lower()
        for field in missing_fields:
            if field == "shipment_date":
                questions.append("Could you please let us know when you'd like to ship this cargo?")
            elif field == "commodity":
                questions.append("Could you please specify the type of goods you wish to ship?")
            elif field == "volume" and context["is_lcl"]:
                questions.append("Could you please provide the total volume (in cubic meters) of your shipment? This helps us provide an accurate LCL quote.")
            elif field == "weight" and context["is_lcl"]:
                questions.append("Could you please provide the total weight of your shipment? Please specify the unit (tons, kg, lbs). This is important for LCL shipments.")
            elif field == "container_preference":
                questions.append("For your FCL shipment, could you let us know if you prefer 20ft or 40ft containers?")
            elif field == "dangerous_goods" and self._is_potentially_dangerous(commodity):
                questions.append(f"Could you please confirm if any of the goods are classified as hazardous or require special handling? (We noticed you mentioned '{commodity}', which may require special attention.)")
            elif field == "quantity":
                questions.append("Could you please let us know how many containers or packages you need to ship?")
            elif field == "special_requirements":
                questions.append("Do you have any special requirements such as refrigerated containers, temperature control, urgent delivery, or other specific handling needs?")
            else:
                questions.append(f"Could you please provide {field} information?")
        return questions

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_smart_clarification_agent():
    """Test the smart clarification agent with various scenarios."""
    print("=== Testing Smart Clarification Agent ===")
    
    agent = SmartClarificationAgent()
    
    test_cases = [
        {
            "name": "FCL with Container Type - No Volume/Weight",
            "input": {
                "extraction_data": {
                    "origin": "Jebel Ali",
                    "destination": "Mundra",
                    "shipment_type": "FCL",
                    "container_type": "20DC",
                    "quantity": 50,
                    "weight": "15 metric tons",
                    "volume": "",
                    "shipment_date": "",
                    "commodity": "",
                    "customer_name": "John Smith"
                },
                "container_standardization_data": {"standard_type": "20DC"},
                "port_lookup_data": {"results": []},
                "missing_fields": ["volume", "shipment_date", "commodity"],
                "thread_id": "test-001"
            }
        },
        {
            "name": "LCL Shipment - Ask for Volume/Weight",
            "input": {
                "extraction_data": {
                    "origin": "Shanghai",
                    "destination": "Los Angeles",
                    "shipment_type": "LCL",
                    "container_type": "",
                    "quantity": 5,
                    "weight": "",
                    "volume": "",
                    "shipment_date": "",
                    "commodity": "Electronics",
                    "customer_name": "Jane Doe"
                },
                "container_standardization_data": {},
                "port_lookup_data": {"results": []},
                "missing_fields": ["weight", "volume", "shipment_date"],
                "thread_id": "test-002"
            }
        },
        {
            "name": "FCL without Container - Ask for Preference",
            "input": {
                "extraction_data": {
                    "origin": "Rotterdam",
                    "destination": "New York",
                    "shipment_type": "FCL",
                    "container_type": "",
                    "quantity": 10,
                    "weight": "25 tons",
                    "shipment_date": "",
                    "commodity": "Machinery",
                    "customer_name": "Bob Wilson"
                },
                "container_standardization_data": {},
                "port_lookup_data": {"results": []},
                "missing_fields": ["container_type", "shipment_date"],
                "thread_id": "test-003"
            }
        },
        {
            "name": "Dangerous Goods Assessment",
            "input": {
                "extraction_data": {
                    "origin": "Dubai",
                    "destination": "Singapore",
                    "shipment_type": "FCL",
                    "container_type": "20DC",
                    "quantity": 2,
                    "weight": "5 tons",
                    "shipment_date": "",
                    "commodity": "chemicals",
                    "customer_name": "Alice Brown"
                },
                "container_standardization_data": {"standard_type": "20DC"},
                "port_lookup_data": {"results": []},
                "missing_fields": ["shipment_date", "dangerous_goods"],
                "thread_id": "test-004"
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        
        result = agent.process(test_case["input"])
        
        print(f"✓ Clarification needed: {result.get('clarification_needed')}")
        print(f"✓ Missing fields: {result.get('missing_fields', [])}")
        print(f"✓ Context: {result.get('context', {})}")
        
        if result.get("clarification_needed"):
            print(f"✓ Extracted summary:")
            print(result.get("extracted_summary", ""))
            print(f"✓ Message preview: {result.get('clarification_message', '')[:200]}...")
        else:
            print("✓ No clarification needed")

if __name__ == "__main__":
    test_smart_clarification_agent() 