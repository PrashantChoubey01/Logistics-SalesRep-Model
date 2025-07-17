"""Clarification Agent: Generates clarification requests for missing shipment information using LLM function calling."""
import json
from typing import Dict, Any
from base_agent import BaseAgent

class ClarificationAgent(BaseAgent):
    """Agent to generate clarification requests for missing shipment fields using LLM function calling."""

    def __init__(self):
        super().__init__("clarification_agent")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate clarification requests for missing or unclear shipment information.
        
        Expected input:
        - extraction_data: Dict with extracted shipment info
        - validation: Dict with validation results
        - missing_fields: List of missing field names
        - thread_id: Optional thread identifier
        """
        extraction_data = input_data.get("extraction_data", {})
        validation = input_data.get("validation", {})
        missing_fields = input_data.get("missing_fields", []) or validation.get("missing_fields", [])
        thread_id = input_data.get("thread_id", "")

        if not missing_fields:
            return {
                "clarification_needed": False,
                "message": "No missing fields to clarify",
                "missing_fields": []
            }

        if not self.client:
            return self._fallback_clarification(missing_fields, extraction_data)

        return self._llm_clarification(extraction_data, validation, missing_fields, thread_id)

    def _llm_clarification(self, extraction_data: Dict, validation: Dict, missing_fields: list, thread_id: str) -> Dict[str, Any]:
        """Generate clarification using LLM function calling"""
        try:
            function_schema = {
                "name": "generate_clarification",
                "description": "Generate clarification request for missing shipment information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "clarification_needed": {
                            "type": "boolean",
                            "description": "True if clarification is needed"
                        },
                        "clarification_message": {
                            "type": "string",
                            "description": "Polite message asking customer for missing information"
                        },
                        "clarification_details": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "field": {"type": "string", "description": "Field name"},
                                    "prompt": {"type": "string", "description": "Specific question for this field"}
                                }
                            },
                            "description": "Detailed questions for each missing field"
                        },
                        "missing_fields": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of missing field names"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["high", "medium", "low"],
                            "description": "Priority level for clarification"
                        }
                    },
                    "required": ["clarification_needed", "clarification_message", "clarification_details", "missing_fields", "priority"]
                }
            }

            prompt = f"""
You are a logistics assistant. Generate a polite clarification request for missing shipment information.

Current extraction: {json.dumps(extraction_data, indent=2)}
Validation results: {json.dumps(validation, indent=2)}
Missing fields: {missing_fields}
Thread ID: {thread_id}

Create:
1. A polite message asking for missing information
2. Specific questions for each missing field
3. Set appropriate priority (high for critical fields like origin/destination)
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
                max_tokens=600
            )

            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if not tool_calls:
                raise Exception("No tool_calls in LLM response")

            tool_args = tool_calls[0].function.arguments
            if isinstance(tool_args, str):
                tool_args = json.loads(tool_args)

            result = dict(tool_args)
            result["clarification_method"] = "llm_function_call"
            result["thread_id"] = thread_id
            
            return result

        except Exception as e:
            self.logger.error(f"LLM clarification failed: {e}")
            return self._fallback_clarification(missing_fields, extraction_data)

    def _fallback_clarification(self, missing_fields: list, extraction_data: Dict) -> Dict[str, Any]:
        """Fallback clarification when LLM unavailable"""
        
        # Determine shipment type from container type or explicit shipment type
        shipment_type = extraction_data.get("shipment_type", "")
        container_type = extraction_data.get("container_type", "")
        
        # If container type is specified, it's FCL
        if container_type and not shipment_type:
            shipment_type = "FCL"
        
        # Smart field questions based on context
        field_questions = {
            # Critical fields (always needed)
            "origin": "What is the origin port or city for your shipment?",
            "destination": "What is the destination port or city?",
            "shipment_type": "Do you need FCL (Full Container Load) or LCL (Less than Container Load)?",
            
            # Container and quantity information
            "container_type": "What container type do you need (20GP, 40GP, 40HC, 20RF, 40RF)?",
            "quantity": "How many containers or packages do you need to ship?",
            
            # Weight and volume (context-aware)
            "weight": "What is the total weight of your shipment? Please specify the unit (tons, kg, lbs).",
            "volume": "What is the total volume (CBM - cubic meters) of your shipment? This is especially important for LCL shipments.",
            
            # Timing and cargo details
            "shipment_date": "What is the desired shipment date?",
            "commodity": "What type of goods are you shipping? (e.g., electronics, textiles, machinery, food products)",
            
            # Special requirements (only ask if commodity is provided)
            "dangerous_goods": "Are you shipping any dangerous goods, hazardous materials, or items requiring special handling?",
            "special_requirements": "Do you have any special requirements such as refrigerated containers, temperature control, urgent delivery, or other specific handling needs?",
            
            # Customer information
            "customer_name": "Could you please provide your name for our records?",
            "customer_company": "What is your company name?",
            "customer_email": "Please provide your email address for communication.",
            
            # Additional fields that might be needed
            "insurance": "Do you need cargo insurance for your shipment?",
            "packaging": "Do you need special packaging or crating services?",
            "customs_clearance": "Do you need customs clearance services at destination?",
            "delivery_address": "What is the final delivery address (if different from destination port)?",
            "pickup_address": "What is the pickup address (if different from origin port)?"
        }

        # Smart filtering of missing fields based on context
        filtered_missing_fields = []
        clarification_details = []
        
        for field in missing_fields:
            # Skip volume for FCL shipments unless explicitly needed
            if field == "volume" and shipment_type == "FCL":
                continue
                
            # Skip dangerous_goods if commodity is not provided
            if field == "dangerous_goods" and not extraction_data.get("commodity"):
                continue
                
            # Skip port validation fields (handled by port lookup agent)
            if field in ["origin", "destination"]:
                continue
                
            # Add field to clarification
            filtered_missing_fields.append(field)
            clarification_details.append({
                "field": field,
                "prompt": field_questions.get(field, f"Please provide {field} information")
            })

        # If no fields need clarification after filtering
        if not filtered_missing_fields:
            return {
                "clarification_needed": False,
                "clarification_message": "No additional information needed",
                "clarification_details": [],
                "missing_fields": [],
                "priority": "low",
                "clarification_method": "fallback",
                "extracted_info": {k: v for k, v in extraction_data.items() if v is not None}
            }

        # Generate message with extracted details listed first
        message = "Dear Customer,\n\nThank you for your logistics request. Here's what I understand from your request:\n\n"
        
        # List extracted details
        extracted_details = []
        for key, value in extraction_data.items():
            if value and str(value).strip() not in ["", "None", "Unknown"]:
                if key == "origin":
                    extracted_details.append(f"• Origin: {value}")
                elif key == "destination":
                    extracted_details.append(f"• Destination: {value}")
                elif key == "shipment_type":
                    extracted_details.append(f"• Shipment Type: {value}")
                elif key == "container_type":
                    extracted_details.append(f"• Container Type: {value}")
                elif key == "quantity":
                    extracted_details.append(f"• Quantity: {value}")
                elif key == "weight":
                    extracted_details.append(f"• Weight: {value}")
                elif key == "commodity":
                    extracted_details.append(f"• Commodity: {value}")
        
        if extracted_details:
            message += "\n".join(extracted_details) + "\n\n"
        
        # Add clarification questions
        message += "To provide you with an accurate quote, I need the following additional information:\n\n"
        for detail in clarification_details:
            message += f"• {detail['prompt']}\n"
        message += "\nThank you for your cooperation!"

        # Determine priority based on field importance
        critical_fields = ["shipment_type", "container_type", "quantity"]
        important_fields = ["weight", "volume", "shipment_date", "commodity", "dangerous_goods"]
        
        if any(field in critical_fields for field in filtered_missing_fields):
            priority = "high"
        elif any(field in important_fields for field in filtered_missing_fields):
            priority = "medium"
        else:
            priority = "low"

        return {
            "clarification_needed": True,
            "clarification_message": message,
            "clarification_details": clarification_details,
            "missing_fields": filtered_missing_fields,
            "priority": priority,
            "clarification_method": "fallback",
            "extracted_info": {k: v for k, v in extraction_data.items() if v is not None}
        }

# =====================================================
#                 🔁 Test Harness
# =====================================================
def test_clarification_agent():
    """Test clarification agent with various scenarios"""
    print("=== Testing Clarification Agent ===")
    
    agent = ClarificationAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}, Has LLM: {bool(agent.client)}")

    test_cases = [
        {
            "name": "Missing Critical Fields",
            "input": {
                "extraction_data": {
                    "origin": None,
                    "destination": None,
                    "shipment_type": "FCL",
                    "container_type": "40HC",
                    "quantity": 2,
                    "weight": "25 tons",
                    "commodity": "electronics"
                },
                "missing_fields": ["origin", "destination", "shipment_date"],
                "thread_id": "test-001"
            }
        },
        {
            "name": "Missing Optional Fields",
            "input": {
                "extraction_data": {
                    "origin": "Shanghai",
                    "destination": "Long Beach",
                    "shipment_type": "FCL",
                    "weight": None,
                    "volume": None
                },
                "missing_fields": ["weight", "volume", "commodity"],
                "thread_id": "test-002"
            }
        },
        {
            "name": "No Missing Fields",
            "input": {
                "extraction_data": {
                    "origin": "Shanghai",
                    "destination": "Long Beach",
                    "shipment_type": "FCL",
                    "container_type": "40HC"
                },
                "missing_fields": [],
                "thread_id": "test-003"
            }
        },
        {
            "name": "Validation Results",
            "input": {
                "extraction_data": {
                    "origin": "Shanghai",
                    "destination": None,
                    "shipment_type": "FCL"
                },
                "validation": {
                    "overall_validity": False,
                    "missing_fields": ["destination", "quantity"]
                },
                "thread_id": "test-004"
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        
        result = agent.run(test_case["input"])
        
        if result.get("status") == "success":
            print(f"✓ Clarification needed: {result.get('clarification_needed')}")
            
            if result.get("clarification_needed"):
                print(f"✓ Priority: {result.get('priority', 'unknown')}")
                print(f"✓ Missing fields: {result.get('missing_fields', [])}")
                print(f"✓ Method: {result.get('clarification_method', 'unknown')}")
                
                # Show clarification details
                details = result.get("clarification_details", [])
                print(f"✓ Questions ({len(details)}):")
                for detail in details[:3]:  # Show first 3
                    print(f"   - {detail.get('field')}: {detail.get('prompt')}")
                
                # Show message preview
                message = result.get("clarification_message", "")
                print(f"✓ Message preview: {message[:100]}...")
            else:
                print("✓ No clarification needed")
        else:
            print(f"✗ Error: {result.get('error')}")

if __name__ == "__main__":
    test_clarification_agent()