#!/usr/bin/env python3
"""
Data Validation Agent - Specialized LLM Approach

This agent uses a dedicated LLM specifically for validating extracted information,
ensuring data quality, and identifying inconsistencies or errors.

Key Features:
1. Dedicated data validation LLM
2. Cross-field validation
3. Business rule validation
4. Data quality assessment
5. Error correction suggestions
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent


class DataValidationAgent(BaseAgent):
    """
    Data Validation Agent - Specialized LLM Design
    
    This agent uses a dedicated LLM specifically for data validation,
    separate from other agents to prevent confusion and improve accuracy.
    
    Design Philosophy:
    - Dedicated LLM for data validation only
    - Cross-field validation and consistency checks
    - Business rule validation
    - Data quality scoring
    - Error correction recommendations
    """

    def __init__(self):
        super().__init__("DataValidationAgent")
        
        # Use a different model for data validation (more focused on logic and validation)
        self.validation_model = "databricks-meta-llama-3-3-70b-instruct"
        
        # Validation categories
        self.validation_categories = {
            "format_validation": "Email format, phone format, date format",
            "business_validation": "Business rules, logical consistency",
            "cross_field_validation": "Relationships between fields",
            "completeness_validation": "Required fields, missing data",
            "accuracy_validation": "Data accuracy and plausibility"
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core data validation logic using specialized validation LLM.
        
        Args:
            input_data: Dictionary containing:
                - extracted_data: Data extracted from emails
                - validation_rules: Business rules and validation criteria
                - context_data: Additional context for validation
                - previous_validation: Previous validation results
        
        Returns:
            Dictionary containing validation results
        """
        print(f"✅ DATA_VALIDATOR: Starting specialized LLM data validation...")
        
        # Extract input data
        extracted_data = input_data.get("extracted_data", {})
        validation_rules = input_data.get("validation_rules", {})
        context_data = input_data.get("context_data", {})
        previous_validation = input_data.get("previous_validation", {})
        
        # Get data to validate
        shipment_details = extracted_data.get("shipment_details", {})
        contact_info = extracted_data.get("contact_information", {})
        rate_info = extracted_data.get("rate_information", {})
        timeline_info = extracted_data.get("timeline_information", {})
        
        print(f"📊 Validating {len(shipment_details)} shipment fields")
        print(f"👤 Validating {len(contact_info)} contact fields")
        print(f"💰 Validating {len(rate_info)} rate fields")
        print(f"⏰ Validating {len(timeline_info)} timeline fields")
        
        # Use specialized data validation LLM
        validation_result = self._specialized_data_validation(
            shipment_details, contact_info, rate_info, timeline_info,
            validation_rules, context_data, previous_validation
        )
        
        print(f"✅ DATA_VALIDATOR: Specialized LLM validation complete")
        print(f"   Overall Quality: {validation_result.get('overall_quality', 0):.2f}")
        print(f"   Validation Issues: {len(validation_result.get('validation_issues', []))}")
        print(f"   Confidence: {validation_result.get('confidence', 0):.2f}")
        
        return validation_result

    def _specialized_data_validation(self, shipment_details: Dict, contact_info: Dict,
                                   rate_info: Dict, timeline_info: Dict,
                                   validation_rules: Dict, context_data: Dict,
                                   previous_validation: Dict) -> Dict[str, Any]:
        """
        Use specialized data validation LLM for comprehensive validation.
        """
        if not self.client:
            return self._fallback_data_validation(shipment_details, contact_info, rate_info, timeline_info)
        
        # Prepare context for validation LLM
        validation_context = self._prepare_validation_context(validation_rules, context_data)
        previous_validation_summary = self._prepare_previous_validation_summary(previous_validation)
        
        # Create specialized validation prompt
        prompt = self._create_validation_prompt(
            shipment_details, contact_info, rate_info, timeline_info,
            validation_context, previous_validation_summary
        )
        
        # Define specialized function schema for data validation
        function_schema = {
            "name": "validate_data",
            "description": "Validate extracted data using specialized validation logic",
            "parameters": {
                "type": "object",
                "properties": {
                    "format_validation": {
                        "type": "object",
                        "properties": {
                            "email_validation": {
                                "type": "object",
                                "properties": {
                                    "is_valid": {"type": "boolean"},
                                    "issues": {"type": "array", "items": {"type": "string"}},
                                    "suggestions": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "phone_validation": {
                                "type": "object",
                                "properties": {
                                    "is_valid": {"type": "boolean"},
                                    "issues": {"type": "array", "items": {"type": "string"}},
                                    "suggestions": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "date_validation": {
                                "type": "object",
                                "properties": {
                                    "is_valid": {"type": "boolean"},
                                    "issues": {"type": "array", "items": {"type": "string"}},
                                    "suggestions": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        }
                    },
                    "business_validation": {
                        "type": "object",
                        "properties": {
                            "route_validation": {
                                "type": "object",
                                "properties": {
                                    "is_valid": {"type": "boolean"},
                                    "issues": {"type": "array", "items": {"type": "string"}},
                                    "suggestions": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "container_validation": {
                                "type": "object",
                                "properties": {
                                    "is_valid": {"type": "boolean"},
                                    "issues": {"type": "array", "items": {"type": "string"}},
                                    "suggestions": {"type": "array", "items": {"type": "string"}}
                                }
                            },
                            "rate_validation": {
                                "type": "object",
                                "properties": {
                                    "is_valid": {"type": "boolean"},
                                    "issues": {"type": "array", "items": {"type": "string"}},
                                    "suggestions": {"type": "array", "items": {"type": "string"}}
                                }
                            }
                        }
                    },
                    "cross_field_validation": {
                        "type": "object",
                        "properties": {
                            "consistency_issues": {"type": "array", "items": {"type": "string"}},
                            "relationship_issues": {"type": "array", "items": {"type": "string"}},
                            "suggestions": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "completeness_validation": {
                        "type": "object",
                        "properties": {
                            "missing_required_fields": {"type": "array", "items": {"type": "string"}},
                            "optional_fields_present": {"type": "array", "items": {"type": "string"}},
                            "completeness_score": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                        }
                    },
                    "overall_quality": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Overall data quality score"
                    },
                    "validation_issues": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "All validation issues found"
                    },
                    "correction_suggestions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Suggestions for data correction"
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Confidence in validation results"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of validation approach"
                    }
                },
                "required": ["overall_quality", "validation_issues", "confidence", "reasoning"]
            }
        }
        
        # Get specialized LLM data validation
        llm_result = self._generate_validation_response(prompt, function_schema)
        
        if "error" in llm_result:
            print(f"⚠️ Specialized LLM data validation failed, using fallback: {llm_result['error']}")
            return self._fallback_data_validation(shipment_details, contact_info, rate_info, timeline_info)
        
        # Enhance result with additional context
        enhanced_result = self._enhance_validation_result(
            llm_result, shipment_details, contact_info, rate_info, timeline_info
        )
        
        return enhanced_result

    def _create_validation_prompt(self, shipment_details: Dict, contact_info: Dict,
                                rate_info: Dict, timeline_info: Dict,
                                validation_context: str, previous_validation_summary: str) -> str:
        """
        Create specialized prompt for data validation LLM.
        """
        prompt = f"""
You are a specialized data validation expert for a logistics CRM system. Your ONLY job is to validate extracted data for accuracy, completeness, and consistency.

## DATA TO VALIDATE:

### SHIPMENT DETAILS:
{json.dumps(shipment_details, indent=2)}

### CONTACT INFORMATION:
{json.dumps(contact_info, indent=2)}

### RATE INFORMATION:
{json.dumps(rate_info, indent=2)}

### TIMELINE INFORMATION:
{json.dumps(timeline_info, indent=2)}

## VALIDATION CONTEXT:
{validation_context}

## PREVIOUS VALIDATION:
{previous_validation_summary}

## DATA VALIDATION TASK:

Validate this extracted data according to the following categories:

### FORMAT VALIDATION:
- Email addresses: Valid email format
- Phone numbers: Valid phone number format
- Dates: Valid date format and logical dates
- Currency: Valid currency codes
- Port codes: Valid port/airport codes

### BUSINESS VALIDATION:
- Route validation: Origin and destination make sense
- Container validation: Valid container types and sizes
- Rate validation: Reasonable rate ranges (only for forwarder emails)
- Timeline validation: Logical dates (transit time is NOT required from customers)
- Weight/volume validation: Reasonable cargo specifications

### CROSS-FIELD VALIDATION:
- Consistency between related fields
- Logical relationships between data
- No contradictory information
- Complete information sets

### COMPLETENESS VALIDATION:
- Required fields present based on email type:
  * Customer emails: Origin, destination, container type are required
  * Forwarder emails: Origin, destination, container type, rates are required
- Optional fields appropriately filled
- No critical missing information
- Sufficient data for processing

### ACCURACY VALIDATION:
- Plausible data values
- Realistic business scenarios
- Logical data combinations
- Industry-standard ranges

## IMPORTANT VALIDATION RULES:

1. **FCL vs LCL Shipment Types**:
   - **FCL (Full Container Load)**: Has container type specified (20GP, 40GP, 40HC, etc.)
   - **LCL (Less than Container Load)**: No container type, but requires weight and volume
   - **Determining Shipment Type**: If container_type is mentioned, it's FCL; if not, it's LCL

2. **Required Fields by Shipment Type**:
   - **FCL Required**: Origin port name/code, Destination port name/code, Container type, Shipment date, Commodity name, Quantity
   - **FCL Optional**: Weight, Contact details (Weight and Volume are NOT required for FCL if container type and quantity are provided)
   - **LCL Required**: Origin port name/code, Destination port name/code, Weight, Volume, Shipment date, Commodity name
   - **LCL Optional**: Contact details

3. **FCL vs LCL Determination**:
   - **FCL Indicators**: Container type specified (20GP, 40GP, 40HC, etc.) OR quantity specified (number of containers)
   - **LCL Indicators**: No container type, but weight and volume specified
   - **If customer mentions "containers" or provides quantity**: Treat as FCL shipment

4. **Customer vs Forwarder Context**: 
   - Customers typically provide: origin, destination, container type, commodity, weight/volume
   - Customers do NOT provide: transit time, rates, sailing schedules
   - Forwarders typically provide: origin, destination, container type, rates, transit time

5. **Transit Time**: 
   - Do NOT flag missing transit time for customer emails - this is normal
   - Only flag missing transit time for forwarder emails

6. **Rates**: 
   - Do NOT flag missing rates for customer emails - customers request rates, don't provide them
   - Only flag missing rates for forwarder emails

7. **Contact Information**:
   - Do NOT require customer contact details for confirmation
   - Only validate format if provided, don't flag as missing

8. **Field Requirements Summary**:
   - **FCL Shipments**: Origin port name/code, Destination port name/code, Container type, Shipment date, Commodity name, Quantity
   - **LCL Shipments**: Origin port name/code, Destination port name/code, Weight, Volume, Shipment date, Commodity name
   - **Missing any of these fields**: Flag as missing and require clarification

## VALIDATION GUIDELINES:

1. **Be thorough**: Check all aspects of the data
2. **Be specific**: Provide detailed issue descriptions
3. **Be helpful**: Suggest corrections when possible
4. **Be realistic**: Consider business context and email type
5. **Be consistent**: Apply validation rules uniformly

## YOUR TASK:
Validate this extracted data comprehensively. Provide reasoning for your validation approach and assess confidence level.
"""
        return prompt

    def _prepare_validation_context(self, validation_rules: Dict, context_data: Dict) -> str:
        """
        Prepare validation context for validation LLM.
        """
        context_parts = ["Validation Rules and Context:"]
        
        # Add validation rules
        if validation_rules:
            context_parts.append("Business Rules:")
            for rule, description in validation_rules.items():
                context_parts.append(f"  - {rule}: {description}")
        
        # Add context data
        if context_data:
            context_parts.append("Context Information:")
            for key, value in context_data.items():
                context_parts.append(f"  - {key}: {value}")
        
        if len(context_parts) == 1:
            return "No specific validation rules or context provided."
        
        return "\n".join(context_parts)

    def _prepare_previous_validation_summary(self, previous_validation: Dict) -> str:
        """
        Prepare previous validation summary for validation LLM.
        """
        if not previous_validation:
            return "No previous validation data available."
        
        summary_parts = ["Previous Validation Results:"]
        
        # Show key validation metrics
        overall_quality = previous_validation.get("overall_quality", 0)
        issues_count = len(previous_validation.get("validation_issues", []))
        
        summary_parts.append(f"  Overall Quality: {overall_quality:.2f}")
        summary_parts.append(f"  Issues Found: {issues_count}")
        
        # Show recent issues
        recent_issues = previous_validation.get("validation_issues", [])[-3:]
        if recent_issues:
            summary_parts.append("  Recent Issues:")
            for issue in recent_issues:
                summary_parts.append(f"    - {issue}")
        
        return "\n".join(summary_parts)

    def _enhance_validation_result(self, llm_result: Dict, shipment_details: Dict,
                                 contact_info: Dict, rate_info: Dict,
                                 timeline_info: Dict) -> Dict[str, Any]:
        """
        Enhance validation result with additional analysis and quality assessment.
        """
        try:
            # Extract quality factors
            quality_factors = self._extract_quality_factors(llm_result)
            
            # Calculate overall quality score
            overall_quality = self._calculate_validation_quality(llm_result, quality_factors)
            
            # Prepare validation details
            validation_details = self._prepare_validation_details(llm_result, shipment_details, contact_info, rate_info, timeline_info)
            
            # Prepare quality breakdown
            quality_breakdown = self._prepare_quality_breakdown(llm_result, quality_factors)
            
            # Extract missing fields from validation details
            # Per Rule 3.3: missing_fields must be in priority order:
            # 1. Origin & Destination
            # 2. Container Type (FCL) & Shipment Date
            # 3. Commodity, Weight/Volume
            # 4. Contact info, special requirements
            missing_fields = []
            for category, details in validation_details.items():
                if isinstance(details, dict) and "issues" in details:
                    for issue in details["issues"]:
                        if "Missing" in issue:
                            field_name = issue.replace("Missing ", "").strip()
                            missing_fields.append(field_name)
            
            # Sort missing fields by priority order (per Rule 3.3)
            missing_fields = self._prioritize_missing_fields(missing_fields)
            
            # Enhanced result
            enhanced_result = {
                "overall_quality": overall_quality,
                "validation_issues": llm_result.get("validation_issues", []),
                "validation_details": validation_details,
                "quality_breakdown": quality_breakdown,
                "confidence": llm_result.get("confidence", 0.0),
                "validation_status": llm_result.get("validation_status", "unknown"),
                "recommendations": llm_result.get("recommendations", []),
                "reasoning": llm_result.get("reasoning", "No reasoning provided"),
                "quality_factors": quality_factors,
                "missing_fields": missing_fields,
                "overall_validation": {
                    "missing_fields": missing_fields,
                    "is_complete": len(missing_fields) == 0,
                    "completeness_score": 1.0 - (len(missing_fields) / 10.0)  # Normalize to 0-1
                }
            }
            
            return enhanced_result
            
        except Exception as e:
            print(f"❌ Error enhancing validation result: {e}")
            return {
                "overall_quality": 0.5,
                "validation_issues": ["Error in validation enhancement"],
                "validation_details": {},
                "quality_breakdown": {},
                "confidence": 0.0,
                "validation_status": "error",
                "recommendations": ["Review validation process"],
                "reasoning": f"Validation enhancement failed: {str(e)}",
                "quality_factors": []
            }

    def _prepare_validation_details(self, llm_result: Dict, shipment_details: Dict,
                                  contact_info: Dict, rate_info: Dict,
                                  timeline_info: Dict) -> Dict[str, Any]:
        """
        Prepare detailed validation information for each field category.
        """
        validation_details = {}
        
        try:
            # Validate shipment details
            if shipment_details:
                validation_details["shipment_details"] = {
                    "is_valid": True,
                    "quality": 0.8,
                    "issues": []
                }
                
                # Check for required fields based on shipment type
                # Per Rule 3.3: Check in priority order:
                # 1. Origin & Destination
                # 2. Container Type (FCL) & Shipment Date
                # 3. Commodity, Weight/Volume
                container_type = shipment_details.get("container_type", "").strip()
                is_fcl = bool(container_type)  # If container type is specified, it's FCL
                
                # Priority 1: Origin & Destination (check first)
                if not shipment_details.get("origin"):
                    validation_details["shipment_details"]["issues"].append("Missing origin")
                    validation_details["shipment_details"]["is_valid"] = False
                
                if not shipment_details.get("destination"):
                    validation_details["shipment_details"]["issues"].append("Missing destination")
                    validation_details["shipment_details"]["is_valid"] = False
                
                # Priority 2: Container Type (FCL) & Shipment Date
                # (Container type check is below in FCL-specific section)
                # (Shipment date check is in timeline_info section below)
                
                # Priority 3: Commodity, Weight/Volume
                if not shipment_details.get("commodity"):
                    validation_details["shipment_details"]["issues"].append("Missing commodity")
                    validation_details["shipment_details"]["is_valid"] = False
                
                # FCL specific requirements
                if is_fcl:
                    if not container_type:
                        validation_details["shipment_details"]["issues"].append("Missing container_type")
                        validation_details["shipment_details"]["is_valid"] = False
                    
                    if not shipment_details.get("container_count"):
                        validation_details["shipment_details"]["issues"].append("Missing container_count")
                        validation_details["shipment_details"]["is_valid"] = False
                else:
                    # LCL specific requirements
                    if not shipment_details.get("weight"):
                        validation_details["shipment_details"]["issues"].append("Missing weight")
                        validation_details["shipment_details"]["is_valid"] = False
                    
                    if not shipment_details.get("volume"):
                        validation_details["shipment_details"]["issues"].append("Missing volume")
                        validation_details["shipment_details"]["is_valid"] = False
                
                # Don't penalize for missing transit time - customers don't provide this
                if not timeline_info.get("transit_time"):
                    # This is normal for customer emails, not an issue
                    pass
                
            # Validate contact information
            if contact_info:
                validation_details["contact_information"] = {
                    "is_valid": True,
                    "quality": 0.8,
                    "issues": []
                }
                
                # Check for basic contact info
                if not contact_info.get("name") and not contact_info.get("email"):
                    validation_details["contact_information"]["issues"].append("Missing customer contact information")
                    validation_details["contact_information"]["is_valid"] = False
            
            # Validate rate information (only for forwarder emails)
            if rate_info:
                validation_details["rate_information"] = {
                    "is_valid": True,
                    "quality": 0.8,
                    "issues": []
                }
                
                # Check for rate details
                if not rate_info.get("total_rate"):
                    validation_details["rate_information"]["issues"].append("Missing rate information")
                    validation_details["rate_information"]["is_valid"] = False
            
            # Validate timeline information
            if timeline_info:
                validation_details["timeline_information"] = {
                    "is_valid": True,
                    "quality": 0.8,
                    "issues": []
                }
                
                # Check for requested dates (shipment date)
                if not timeline_info.get("requested_dates"):
                    validation_details["timeline_information"]["issues"].append("Missing requested_dates")
                    validation_details["timeline_information"]["is_valid"] = False
                
                # Don't require transit time from customers - this is normal
                    
        except Exception as e:
            print(f"❌ Error preparing validation details: {e}")
            validation_details = {
                "error": f"Validation details preparation failed: {str(e)}"
            }
        
        return validation_details

    def _extract_quality_factors(self, llm_result: Dict) -> List[str]:
        """
        Extract factors that influenced data quality assessment.
        """
        factors = []
        
        if llm_result.get("overall_quality", 0) >= 0.8:
            factors.append("High overall data quality")
        elif llm_result.get("overall_quality", 0) >= 0.6:
            factors.append("Medium overall data quality")
        else:
            factors.append("Low overall data quality")
        
        validation_issues = llm_result.get("validation_issues", [])
        if validation_issues:
            factors.append(f"Validation issues found: {len(validation_issues)}")
        
        format_validation = llm_result.get("format_validation", {})
        if format_validation:
            factors.append("Format validation performed")
        
        business_validation = llm_result.get("business_validation", {})
        if business_validation:
            factors.append("Business validation performed")
        
        cross_field_validation = llm_result.get("cross_field_validation", {})
        if cross_field_validation:
            factors.append("Cross-field validation performed")
        
        return factors

    def _calculate_validation_quality(self, llm_result: Dict, quality_factors: List[str]) -> float:
        """
        Calculate overall validation quality score.
        """
        try:
            # Base quality from LLM result
            base_quality = llm_result.get("overall_quality", 0.5)
            
            # Adjust based on quality factors
            quality_adjustment = 0.0
            
            # Positive factors
            positive_factors = ["complete_data", "consistent_information", "valid_format", "business_logic_ok"]
            for factor in positive_factors:
                if factor in quality_factors:
                    quality_adjustment += 0.1
            
            # Negative factors
            negative_factors = ["missing_critical_fields", "inconsistent_data", "invalid_format", "business_logic_error"]
            for factor in negative_factors:
                if factor in quality_factors:
                    quality_adjustment -= 0.1
            
            # Calculate final quality
            final_quality = min(1.0, max(0.0, base_quality + quality_adjustment))
            
            return final_quality
            
        except Exception as e:
            print(f"❌ Error calculating validation quality: {e}")
            return 0.5

    def _prepare_quality_breakdown(self, llm_result: Dict, quality_factors: List[str]) -> Dict[str, float]:
        """
        Prepare quality breakdown by category.
        """
        try:
            breakdown = {
                "format_quality": 0.8,
                "completeness_quality": 0.8,
                "accuracy_quality": 0.8,
                "consistency_quality": 0.8,
                "business_logic_quality": 0.8
            }
            
            # Adjust based on quality factors
            if "complete_data" in quality_factors:
                breakdown["completeness_quality"] = 0.9
            if "missing_critical_fields" in quality_factors:
                breakdown["completeness_quality"] = 0.4
                
            if "consistent_information" in quality_factors:
                breakdown["consistency_quality"] = 0.9
            if "inconsistent_data" in quality_factors:
                breakdown["consistency_quality"] = 0.4
                
            if "valid_format" in quality_factors:
                breakdown["format_quality"] = 0.9
            if "invalid_format" in quality_factors:
                breakdown["format_quality"] = 0.4
                
            if "business_logic_ok" in quality_factors:
                breakdown["business_logic_quality"] = 0.9
            if "business_logic_error" in quality_factors:
                breakdown["business_logic_quality"] = 0.4
            
            return breakdown
            
        except Exception as e:
            print(f"❌ Error preparing quality breakdown: {e}")
            return {
                "format_quality": 0.5,
                "completeness_quality": 0.5,
                "accuracy_quality": 0.5,
                "consistency_quality": 0.5,
                "business_logic_quality": 0.5
            }

    def _fallback_data_validation(self, shipment_details: Dict, contact_info: Dict,
                                rate_info: Dict, timeline_info: Dict) -> Dict[str, Any]:
        """
        Fallback data validation when specialized LLM is not available.
        """
        print("⚠️ Using fallback data validation (Specialized LLM not available)")
        
        # Simple fallback validation logic
        validation_issues = []
        correction_suggestions = []
        
        # Basic format validation
        for email in contact_info.values():
            if isinstance(email, str) and "@" in email and "." in email:
                if not email.count("@") == 1:
                    validation_issues.append(f"Invalid email format: {email}")
                    correction_suggestions.append(f"Check email format for: {email}")
        
        # Basic business validation
        if shipment_details.get("origin") and shipment_details.get("destination"):
            if shipment_details["origin"] == shipment_details["destination"]:
                validation_issues.append("Origin and destination cannot be the same")
                correction_suggestions.append("Verify origin and destination are different")
        
        # Basic completeness validation
        required_fields = ["origin", "destination", "container_type"]
        missing_fields = [field for field in required_fields if not shipment_details.get(field)]
        if missing_fields:
            validation_issues.append(f"Missing required fields: {', '.join(missing_fields)}")
            correction_suggestions.append(f"Please provide: {', '.join(missing_fields)}")
        
        # Calculate quality score
        total_fields = len(shipment_details) + len(contact_info) + len(rate_info) + len(timeline_info)
        quality_score = max(0.1, 1.0 - (len(validation_issues) / max(1, total_fields)))
        
        return {
            "overall_quality": quality_score,
            "validation_issues": validation_issues,
            "correction_suggestions": correction_suggestions,
            "confidence": 0.4,  # Low confidence for fallback
            "reasoning": "Fallback data validation due to specialized LLM unavailability",
            "validation_method": "fallback"
        }

    def _prioritize_missing_fields(self, missing_fields: List[str]) -> List[str]:
        """
        Prioritize missing fields according to Rule 3.3:
        1. Origin & Destination
        2. Container Type (FCL) & Shipment Date
        3. Commodity, Weight/Volume
        4. Contact info, special requirements
        """
        # Define priority order (lower number = higher priority)
        priority_map = {
            # Priority 1: Origin & Destination
            "origin": 1,
            "destination": 1,
            # Priority 2: Container Type (FCL) & Shipment Date
            "container_type": 2,
            "container_count": 2,
            "requested_dates": 2,
            "shipment_date": 2,
            # Priority 3: Commodity, Weight/Volume
            "commodity": 3,
            "weight": 3,
            "volume": 3,
            # Priority 4: Contact info, special requirements
            "name": 4,
            "email": 4,
            "phone": 4,
            "company": 4,
            "contact_information": 4,
            "special_requirements": 4,
        }
        
        # Normalize field names for matching
        def get_priority(field_name: str) -> int:
            field_lower = field_name.lower()
            # Check exact matches first
            if field_lower in priority_map:
                return priority_map[field_lower]
            # Check partial matches
            for key, priority in priority_map.items():
                if key in field_lower or field_lower in key:
                    return priority
            # Default to lowest priority if not found
            return 99
        
        # Sort by priority, then alphabetically for same priority
        sorted_fields = sorted(missing_fields, key=lambda f: (get_priority(f), f.lower()))
        
        return sorted_fields

    def _generate_validation_response(self, prompt: str, function_schema: Dict) -> Dict[str, Any]:
        """
        Generate response using specialized data validation LLM.
        """
        return self._make_llm_call(
            prompt=prompt,
            function_schema=function_schema,
            model_name=self.validation_model,
            temperature=0.1,
            max_tokens=1000
        )


# =====================================================
#                 🧪 Test Functions
# =====================================================

def test_data_validator():
    """Test the Specialized LLM-based Data Validation Agent"""
    print("🧪 Testing Specialized LLM-based Data Validation Agent")
    print("=" * 60)
    
    # Initialize agent
    validator = DataValidationAgent()
    validator.load_context()
    
    # Test scenarios
    test_cases = [
        {
            "name": "Valid Shipment Data",
            "extracted_data": {
                "shipment_details": {
                    "origin": "Shanghai",
                    "destination": "Los Angeles",
                    "container_type": "40HC",
                    "commodity": "Electronics",
                    "weight": "15,000 kg",
                    "volume": "65 CBM"
                },
                "contact_information": {
                    "customer_name": "John Smith",
                    "customer_email": "john.smith@techsolutions.com",
                    "customer_phone": "+1-555-123-4567",
                    "customer_company": "Tech Solutions Inc."
                },
                "rate_information": {
                    "total_rate": "USD 2,800",
                    "currency": "USD",
                    "validity_period": "30 days"
                },
                "timeline_information": {
                    "requested_dates": "December 2024",
                    "transit_time": "16 days"
                }
            },
            "validation_rules": {
                "require_origin_destination": "Origin and destination are required",
                "validate_emails": "Email addresses must be valid format",
                "validate_rates": "Rates must be positive numbers"
            },
            "context_data": {
                "customer_priority": "high",
                "service_type": "ocean_freight"
            },
            "previous_validation": {}
        },
        {
            "name": "Invalid Data with Issues",
            "extracted_data": {
                "shipment_details": {
                    "origin": "Shanghai",
                    "destination": "Shanghai",  # Same as origin
                    "container_type": "40HC",
                    "commodity": "Electronics"
                },
                "contact_information": {
                    "customer_name": "Jane Doe",
                    "customer_email": "invalid-email",  # Invalid email
                    "customer_phone": "123",  # Invalid phone
                    "customer_company": "Small Business Ltd."
                },
                "rate_information": {
                    "total_rate": "USD -500",  # Negative rate
                    "currency": "INVALID"  # Invalid currency
                },
                "timeline_information": {
                    "requested_dates": "Invalid Date",  # Invalid date
                    "transit_time": "-5 days"  # Negative transit time
                }
            },
            "validation_rules": {
                "require_origin_destination": "Origin and destination are required",
                "validate_emails": "Email addresses must be valid format",
                "validate_rates": "Rates must be positive numbers"
            },
            "context_data": {
                "customer_priority": "standard",
                "service_type": "ocean_freight"
            },
            "previous_validation": {
                "overall_quality": 0.3,
                "validation_issues": ["Previous validation found format issues"]
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n✅ Test {i}: {test_case['name']}")
        print("-" * 40)
        
        result = validator.process(test_case)
        
        print(f"✅ Overall Quality: {result.get('overall_quality', 0):.2f}")
        print(f"✅ Confidence: {result.get('confidence', 0):.2f}")
        print(f"✅ Validation Issues: {len(result.get('validation_issues', []))}")
        print(f"✅ Correction Suggestions: {len(result.get('correction_suggestions', []))}")
        
        # Show validation issues
        validation_issues = result.get('validation_issues', [])
        if validation_issues:
            print(f"🚨 Validation Issues:")
            for issue in validation_issues[:5]:  # Show first 5 issues
                print(f"   - {issue}")
        
        # Show correction suggestions
        correction_suggestions = result.get('correction_suggestions', [])
        if correction_suggestions:
            print(f"💡 Correction Suggestions:")
            for suggestion in correction_suggestions[:3]:  # Show first 3 suggestions
                print(f"   - {suggestion}")
        
        # Show format validation results
        format_validation = result.get('format_validation', {})
        if format_validation:
            print(f"📝 Format Validation:")
            for field, validation in format_validation.items():
                if isinstance(validation, dict):
                    is_valid = validation.get('is_valid', False)
                    print(f"   {field}: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        # Show business validation results
        business_validation = result.get('business_validation', {})
        if business_validation:
            print(f"🏢 Business Validation:")
            for field, validation in business_validation.items():
                if isinstance(validation, dict):
                    is_valid = validation.get('is_valid', False)
                    print(f"   {field}: {'✅ Valid' if is_valid else '❌ Invalid'}")
        
        if result.get('reasoning'):
            print(f"🧠 Reasoning: {result['reasoning'][:100]}...")
    
    print(f"\n🎉 All tests completed!")


if __name__ == "__main__":
    test_data_validator() 