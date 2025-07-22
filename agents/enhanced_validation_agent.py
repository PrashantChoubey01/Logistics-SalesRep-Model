"""Enhanced Validation Agent: Comprehensive validation using LLM for port codes, container types, dates, and business logic."""

import json
import sys
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta

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

class EnhancedValidationAgent(BaseAgent):
    """Agent for comprehensive validation using LLM."""

    def __init__(self):
        super().__init__("enhanced_validation_agent")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate extracted data comprehensively using LLM.
        
        Expected input:
        - validation_data: Validation data from previous agents
        - extracted_data: Extracted shipment data (fallback)
        - enriched_data: Enriched data with port codes and standardized values
        - thread_id: Thread identifier
        - validation_context: Additional context for validation
        """
        # Get all data sources
        validation_data = input_data.get("validation_data", {})
        extracted_data = input_data.get("extracted_data", {})
        enriched_data = input_data.get("enriched_data", {})
        thread_id = input_data.get("thread_id", "")
        validation_context = input_data.get("validation_context", {})

        # Combine data from extracted_data and enriched_data (rate_data)
        data_to_validate = {}
        
        # Start with extracted_data
        if extracted_data:
            data_to_validate.update(extracted_data)
        
        # Use enriched data if provided (from data enrichment node)
        enriched_data_result = {}
        if enriched_data and "rate_data" in enriched_data:
            rate_data = enriched_data["rate_data"]
            if rate_data.get("origin_code"):
                data_to_validate["origin"] = rate_data["origin_code"]
            if rate_data.get("destination_code"):
                data_to_validate["destination"] = rate_data["destination_code"]
            if rate_data.get("container_type"):
                data_to_validate["container_type"] = rate_data["container_type"]
            enriched_data_result = enriched_data
            print("🔍 VALIDATION: Using enriched data from data enrichment node")
        else:
            print("⚠️ VALIDATION: No enriched data provided - port lookup should happen in data enrichment node")
        
        # Use validation_data if available and no other data
        if not data_to_validate and validation_data:
            data_to_validate = validation_data
        
        # If still no data, check if input_data itself contains the data
        if not data_to_validate:
            # Remove known keys and use the rest as data
            known_keys = {"validation_data", "extracted_data", "enriched_data", "thread_id", "validation_context"}
            data_to_validate = {k: v for k, v in input_data.items() if k not in known_keys and v is not None}

        if not data_to_validate:
            return {"error": "No data provided for validation"}

        if not self.client:
            return {"error": "LLM client not initialized"}

        return self._validate_data(data_to_validate, validation_context, thread_id, enriched_data)



    def _validate_data(self, extracted_data: Dict[str, Any], validation_context: Dict[str, Any], thread_id: str, enriched_data: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Validate data using LLM function calling."""
        try:
            function_schema = {
                "name": "validate_shipment_data",
                "description": "Comprehensive validation of shipment data",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "validation_results": {
                            "type": "object",
                            "properties": {
                                "origin_port": {
                                    "type": "object",
                                    "properties": {
                                        "input_value": {"type": "string", "description": "The original input value for origin port"},
                                        "is_valid": {"type": "boolean"},
                                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                        "suggested_correction": {"type": "string"},
                                        "validation_notes": {"type": "string"}
                                    }
                                },
                                "destination_port": {
                                    "type": "object",
                                    "properties": {
                                        "input_value": {"type": "string", "description": "The original input value for destination port"},
                                        "is_valid": {"type": "boolean"},
                                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                        "suggested_correction": {"type": "string"},
                                        "validation_notes": {"type": "string"}
                                    }
                                },
                                "container_type": {
                                    "type": "object",
                                    "properties": {
                                        "input_value": {"type": "string", "description": "The original input value for container type"},
                                        "is_valid": {"type": "boolean"},
                                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                        "suggested_correction": {"type": "string"},
                                        "validation_notes": {"type": "string"}
                                    }
                                },
                                "shipment_date": {
                                    "type": "object",
                                    "properties": {
                                        "input_value": {"type": "string", "description": "The original input value for shipment date"},
                                        "is_valid": {"type": "boolean"},
                                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                        "suggested_correction": {"type": "string"},
                                        "validation_notes": {"type": "string"}
                                    }
                                },
                                "weight": {
                                    "type": "object",
                                    "properties": {
                                        "input_value": {"type": "string", "description": "The original input value for weight"},
                                        "is_valid": {"type": "boolean"},
                                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                        "suggested_correction": {"type": "string"},
                                        "validation_notes": {"type": "string"}
                                    }
                                },
                                "volume": {
                                    "type": "object",
                                    "properties": {
                                        "input_value": {"type": "string", "description": "The original input value for volume"},
                                        "is_valid": {"type": "boolean"},
                                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                        "suggested_correction": {"type": "string"},
                                        "validation_notes": {"type": "string"}
                                    }
                                }
                            },
                            "description": "Validation results for each field including input values"
                        },
                        "overall_validation": {
                            "type": "object",
                            "properties": {
                                "is_complete": {"type": "boolean"},
                                "completeness_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "confidence_score": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                                "missing_fields": {"type": "array", "items": {"type": "string"}},
                                "critical_issues": {"type": "array", "items": {"type": "string"}},
                                "warnings": {"type": "array", "items": {"type": "string"}},
                                "business_logic_validation": {"type": "object"}
                            },
                            "description": "Overall validation summary"
                        },
                        "recommendations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Recommendations for data improvement"
                        },
                        "validation_confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Overall confidence in validation"
                        },
                        "confirmation_prompt": {
                            "type": "string",
                            "description": "Customer confirmation prompt asking to verify shipment details"
                        }
                    },
                    "required": ["validation_results", "overall_validation", "recommendations", "validation_confidence"]
                }
            }

            # Format data for validation
            data_summary = self._format_data_for_validation(extracted_data)

            prompt = f"""
You are an expert logistics data validator. Perform comprehensive validation of shipment data.

EXTRACTED DATA:
{data_summary}

VALIDATION REQUIREMENTS:
1. Validate port codes (origin and destination)
2. Validate container types and standardization
3. Validate shipment dates and feasibility
4. Validate weight and volume data
5. Check data completeness
6. Validate business logic
7. Provide confidence scores
8. Suggest corrections where needed

IMPORTANT: For each field you validate, you MUST include the original input_value in your response. This shows what was actually provided for validation. DO NOT generate fake or example values - only validate what was actually provided.

PORT CODE VALIDATION:
- ONLY validate the port codes that were actually provided in the input data
- DO NOT generate or suggest port codes if none were provided
- If no port code is provided, mark as invalid with "No value provided"
- Validate port names and locations only if provided
- Check for common port code variations only if provided
- Include the original input value in the validation result

CONTAINER TYPE VALIDATION:
- Validate standard container types (20GP, 40GP, 40HC, 20RF, 40RF)
- Check for common variations and abbreviations
- Standardize container type format
- Validate container type compatibility
- Include the original input value in the validation result

DATE VALIDATION:
- Check if dates are in the future
- Validate date formats and parsing
- Check for reasonable shipment timelines
- Identify potential date conflicts
- Include the original input value in the validation result

WEIGHT AND VOLUME VALIDATION:
- Validate weight ranges for container types
- Check volume calculations
- Validate units and conversions
- Check for reasonable values
- Include the original input value in the validation result

BUSINESS LOGIC VALIDATION:
- Check origin-destination feasibility
- Validate container type vs commodity compatibility
- Check weight-volume ratios
- Validate dangerous goods requirements

FCL/LCL BUSINESS RULES:
- If container type provided (20GP, 40GP, 40HC, 20DC, 40DC, etc.) → automatically FCL, volume NOT needed
- If volume provided without container type → automatically LCL, weight+volume required
- FCL: Container type mandatory, volume not needed (container type determines volume), weight optional
- LCL: Weight+volume mandatory, no container type allowed
- IMPORTANT: For FCL shipments with container type, NEVER ask for volume - it's determined by container type
- IMPORTANT: For LCL shipments, ALWAYS require both weight and volume

DANGEROUS GOODS DETECTION:
- Check commodity for dangerous goods keywords (battery, chemical, flammable, explosive, toxic, corrosive)
- If dangerous goods detected → require specific documents (MSDS, DG Declaration, UN Number, IMDG Certificate)

CUSTOMER CONFIRMATION:
- Always generate a confirmation prompt asking customer to verify details
- Use actual port names and container types in confirmation
- Professional, business-appropriate tone

COMPLETENESS CHECK:
- Identify missing critical fields
- Assess data quality
- Determine if data is sufficient for processing

For each validation field, include:
- input_value: The exact value that was provided for validation
- is_valid: Whether the value is valid
- confidence: Confidence score (0.0 to 1.0)
- suggested_correction: Any suggested corrections
- validation_notes: Detailed validation notes

Provide detailed validation results with confidence scores and specific recommendations.
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
                max_tokens=800
            )

            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if not tool_calls:
                raise Exception("No tool_calls in LLM response")

            tool_args = tool_calls[0].function.arguments
            if isinstance(tool_args, str):
                tool_args = json.loads(tool_args)

            result = dict(tool_args)
            result["validation_method"] = "llm_function_call"
            result["thread_id"] = thread_id
            
            # Ensure input values are included in validation results
            self._ensure_input_values_in_result(result, extracted_data)
            
            # Apply FCL/LCL business rules to filter missing fields
            self._apply_fcl_lcl_rules(result, extracted_data)
            
            # Add enriched data to the result for rate recommendation (from input)
            if enriched_data and "rate_data" in enriched_data:
                result["enriched_data"] = enriched_data
                
                # Update validation results to use port names instead of codes for LLM validation
                rate_data = enriched_data["rate_data"]
                if "validation_results" in result:
                    validation_results = result["validation_results"]
                    
                    # Update origin port validation to use port name
                    if "origin_port" in validation_results and rate_data.get("origin_name"):
                        validation_results["origin_port"]["input_value"] = rate_data["origin_name"]
                        
                    # Update destination port validation to use port name  
                    if "destination_port" in validation_results and rate_data.get("destination_name"):
                        validation_results["destination_port"]["input_value"] = rate_data["destination_name"]
            
            # Validate and correct result if needed
            validation_confidence = result.get("validation_confidence", 0.5)
            if not (0.0 <= validation_confidence <= 1.0):
                result["validation_confidence"] = max(0.0, min(1.0, validation_confidence))

            # Ensure completeness score is within bounds
            if "overall_validation" in result:
                completeness_score = result["overall_validation"].get("completeness_score", 0.5)
                if not (0.0 <= completeness_score <= 1.0):
                    result["overall_validation"]["completeness_score"] = max(0.0, min(1.0, completeness_score))

            self.logger.info(f"Enhanced validation completed successfully (confidence: {result['validation_confidence']:.2f})")
            
            return result

        except Exception as e:
            self.logger.error(f"Enhanced validation failed: {e}")
            return {"error": f"Enhanced validation failed: {str(e)}"}

    def _format_data_for_validation(self, extracted_data: Dict[str, Any]) -> str:
        """Format extracted data for validation."""
        if not extracted_data:
            return "No data to validate"
        
        summary_parts = []
        for key, value in extracted_data.items():
            # Only include non-null, non-empty values
            if value is not None and str(value).strip() and str(value).lower() not in ['null', 'none', '']:
                summary_parts.append(f"- {key}: {value}")
        
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "No valid data to validate"

    def _ensure_input_values_in_result(self, result: Dict[str, Any], extracted_data: Dict[str, Any]) -> None:
        """Ensure input values are included in validation results."""
        if "validation_results" not in result:
            return
            
        validation_results = result["validation_results"]
        
        # Map extracted data keys to validation result keys
        field_mapping = {
            "origin": "origin_port",
            "destination": "destination_port", 
            "container_type": "container_type",
            "shipment_date": "shipment_date",
            "weight": "weight",
            "volume": "volume"
        }
        
        # Add input values to validation results
        for extracted_key, validation_key in field_mapping.items():
            if extracted_key in extracted_data and validation_key in validation_results:
                input_value = extracted_data[extracted_key]
                # Only set input_value if it's not null/empty
                if input_value is not None and str(input_value).strip() and str(input_value).lower() not in ['null', 'none', '']:
                    # Ensure the validation result has the input_value field
                    if "input_value" not in validation_results[validation_key]:
                        validation_results[validation_key]["input_value"] = str(input_value)
                    elif not validation_results[validation_key]["input_value"]:
                        validation_results[validation_key]["input_value"] = str(input_value)
                else:
                    # Mark as invalid if input is null/empty
                    validation_results[validation_key]["input_value"] = ""
                    validation_results[validation_key]["is_valid"] = False
                    validation_results[validation_key]["validation_notes"] = "No value provided"
                    validation_results[validation_key]["confidence"] = 0.0

    def _apply_fcl_lcl_rules(self, result: Dict[str, Any], extracted_data: Dict[str, Any]) -> None:
        """Apply FCL/LCL business rules to filter missing fields."""
        if "validation_results" not in result or "overall_validation" not in result:
            return
            
        validation_results = result["validation_results"]
        overall_validation = result["overall_validation"]
        
        # Check if this is an FCL shipment (has container type)
        container_type = extracted_data.get("container_type", "")
        has_container_type = container_type and str(container_type).strip().upper() in [
            "20GP", "40GP", "40HC", "20RF", "40RF", "20DC", "40DC", "20FT", "40FT"
        ]
        
        if has_container_type:
            # This is an FCL shipment - volume should NOT be required
            missing_fields = overall_validation.get("missing_fields", [])
            
            # Remove volume from missing fields for FCL shipments
            if "volume" in missing_fields:
                missing_fields.remove("volume")
                print(f"✅ VALIDATION: Removed volume from missing fields (FCL shipment with container type: {container_type})")
            
            # Update the overall validation
            overall_validation["missing_fields"] = missing_fields
            
            # Also update validation results to mark volume as not required
            if "volume" in validation_results:
                validation_results["volume"]["is_valid"] = True
                validation_results["volume"]["validation_notes"] = "Volume not required for FCL shipments - determined by container type"
                validation_results["volume"]["confidence"] = 1.0

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_enhanced_validation_agent():
    print("=== Testing Enhanced Validation Agent ===")
    agent = EnhancedValidationAgent()
    
    if not agent.load_context():
        print("✗ Failed to load context")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "Valid Data",
            "extracted_data": {
                "origin": "CNSHA",
                "destination": "USNYC",
                "container_type": "40GP",
                "quantity": 2,
                "shipment_date": "2024-02-15",
                "weight": "25 tons",
                "commodity": "electronics"
            }
        },
        {
            "name": "Invalid Port Codes",
            "extracted_data": {
                "origin": "Shanghai",
                "destination": "New York",
                "container_type": "40ft",
                "quantity": 1,
                "shipment_date": "2024-01-15",
                "weight": "15 tons"
            }
        },
        {
            "name": "Incomplete Data",
            "extracted_data": {
                "origin": "CNSHA",
                "destination": "USNYC"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        result = agent.run({
            "extracted_data": test_case["extracted_data"],
            "thread_id": "test-thread-1",
            "validation_context": {}
        })
        
        if result.get("status") == "success":
            confidence = result.get("validation_confidence", 0.0)
            overall_validation = result.get("overall_validation", {})
            completeness = overall_validation.get("completeness_score", 0.0)
            missing_fields = overall_validation.get("missing_fields", [])
            critical_issues = overall_validation.get("critical_issues", [])
            
            print(f"✓ Validation Confidence: {confidence:.2f}")
            print(f"✓ Completeness Score: {completeness:.2f}")
            print(f"✓ Missing Fields: {len(missing_fields)}")
            print(f"✓ Critical Issues: {len(critical_issues)}")
            print(f"✓ Recommendations: {len(result.get('recommendations', []))}")
        else:
            print(f"✗ Test failed: {result.get('error')}")

if __name__ == "__main__":
    test_enhanced_validation_agent() 