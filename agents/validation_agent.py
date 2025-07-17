"""Validation agent for shipment data validation and completeness checking"""

import os
import sys
import re
from typing import Dict, Any, List
from datetime import datetime, timedelta

try:
    from .base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class ValidationAgent(BaseAgent):
    """Agent for validating extracted shipment data and checking completeness"""

    def __init__(self):
        super().__init__("validation_agent")
        self.port_codes = self._load_port_codes()
        self.container_types = self._load_container_types()
        self.commodity_codes = self._load_commodity_codes()
        self.validation_config = {
            "weight_limits": {
                "20DC": {"min": 0.1, "max": 28},
                "40DC": {"min": 0.1, "max": 29},
                "40HC": {"min": 0.1, "max": 29},
                "20RE": {"min": 0.1, "max": 25},
                "40RH": {"min": 0.1, "max": 27},
                "20TK": {"min": 0.1, "max": 26}
            },
            "volume_limits": {
                "20DC": {"min": 0.1, "max": 33},
                "40DC": {"min": 0.1, "max": 67},
                "40HC": {"min": 0.1, "max": 76},
                "20RE": {"min": 0.1, "max": 28},
                "40RH": {"min": 0.1, "max": 60},
                "20TK": {"min": 0.1, "max": 26}
            },
            "date_range": {
                "min_days_ahead": -30,
                "max_days_ahead": 365
            },
            "required_fields": {
                "logistics_request": ["origin", "destination", "shipment_type", "container_type", "quantity"],
                "confirmation_reply": ["origin", "destination"],
                "forwarder_response": ["origin", "destination", "rate"],
                "clarification_reply": []
            },
            "important_fields": {
                "logistics_request": ["weight", "volume", "shipment_date", "commodity", "dangerous_goods"],
                "lcl_shipment": ["volume", "weight", "commodity"],
                "dangerous_goods": ["documents_required", "special_requirements"]
            }
        }

    def _load_port_codes(self) -> Dict[str, Dict[str, str]]:
        # Minimal example, extend as needed
        return {
            "AEAUH": {"name": "Abu Dhabi", "country": "UAE"},
            "AEDXB": {"name": "Dubai", "country": "UAE"},
            "CNSHA": {"name": "Shanghai", "country": "China"},
            "USLAX": {"name": "Los Angeles", "country": "USA"},
            "INMUN": {"name": "Mumbai", "country": "India"},
            "INCCU": {"name": "Calcutta", "country": "India"},
        }

    def _load_container_types(self) -> Dict[str, Dict[str, Any]]:
        return {
            "20DC": {"name": "20ft Dry Container", "max_weight": 28, "max_volume": 33},
            "40DC": {"name": "40ft Dry Container", "max_weight": 29, "max_volume": 67},
            "40HC": {"name": "40ft High Cube", "max_weight": 29, "max_volume": 76},
            "20RE": {"name": "20ft Reefer", "max_weight": 25, "max_volume": 28},
            "40RH": {"name": "40ft Reefer High Cube", "max_weight": 27, "max_volume": 60},
            "20TK": {"name": "20ft Tank", "max_weight": 26, "max_volume": 26},
        }

    def _load_commodity_codes(self) -> Dict[str, Dict[str, Any]]:
        return {
            "electronics": {"category": "manufactured", "common_containers": ["20DC", "40DC", "40HC"]},
            "food": {"category": "perishable", "common_containers": ["20RE", "40RH"]},
            "chemicals": {"category": "hazardous", "common_containers": ["20TK", "40TK", "20DC", "40DC"]},
            "furniture": {"category": "manufactured", "common_containers": ["40HC", "40DC"]},
            "general cargo": {"category": "general", "common_containers": ["20DC", "40DC", "40HC"]},
        }

    def process(self, input_data: dict) -> dict:
        extraction_data = input_data.get("extraction_data", {})
        email_type = input_data.get("email_type", "logistics_request")
        if not extraction_data:
            return {"error": "No extraction data provided for validation"}

        results = {
            "overall_validity": True,
            "completeness_score": 0.0,
            "validation_details": {},
            "missing_fields": [],
            "invalid_fields": [],
            "warnings": [],
            "recommendations": [],
            "validated_data": {}
        }

        # Completeness
        completeness = self._validate_completeness(extraction_data, email_type)
        results.update(completeness)

        # Ports
        results["validation_details"]["ports"] = self._validate_ports(extraction_data)
        # Container
        results["validation_details"]["container"] = self._validate_container_type(extraction_data)
        # Weight/Volume
        results["validation_details"]["weight_volume"] = self._validate_weight_volume(extraction_data)
        # Dates
        results["validation_details"]["dates"] = self._validate_dates(extraction_data)
        # Commodity
        results["validation_details"]["commodity"] = self._validate_commodity(extraction_data)
        # Business logic
        results["validation_details"]["business_logic"] = self._validate_business_logic(extraction_data)

        self._calculate_overall_validity(results)
        self._generate_recommendations(results, extraction_data)
        results["validated_data"] = self._create_validated_data(extraction_data, results)
        return results

    def _validate_completeness(self, data: Dict[str, Any], email_type: str) -> Dict[str, Any]:
        required_fields = self.validation_config["required_fields"].get(email_type, [])
        important_fields = self.validation_config["important_fields"].get(email_type, [])
        missing_fields = []
        present_fields = []
        for field in required_fields + important_fields:
            value = data.get(field)
            if value and str(value).strip() not in ["", "None", "Unknown"]:
                present_fields.append(field)
            else:
                if field not in missing_fields:
                    missing_fields.append(field)
        completeness_score = len(present_fields) / max(1, len(required_fields) + len(important_fields))
        return {"missing_fields": missing_fields, "present_fields": present_fields, "completeness_score": round(completeness_score, 2)}

    def _validate_ports(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = {"origin": {"valid": False}, "destination": {"valid": False}, "issues": []}
        origin = str(data.get("origin", ""))
        destination = str(data.get("destination", ""))
        if origin:
            for code, info in self.port_codes.items():
                if origin.upper() == code or origin.lower() == info["name"].lower():
                    result["origin"] = {"valid": True, "code": code, "name": info["name"], "country": info["country"]}
                    break
            if not result["origin"]["valid"]:
                result["issues"].append(f"Invalid origin port: {origin}")
        if destination:
            for code, info in self.port_codes.items():
                if destination.upper() == code or destination.lower() == info["name"].lower():
                    result["destination"] = {"valid": True, "code": code, "name": info["name"], "country": info["country"]}
                    break
            if not result["destination"]["valid"]:
                result["issues"].append(f"Invalid destination port: {destination}")
        return result

    def _validate_container_type(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = {"valid": False, "container_type": None, "specifications": {}, "issues": []}
        container_type = str(data.get("container_type") or data.get("shipment_type") or "").strip().upper()
        if not container_type:
            result["issues"].append("Container type not specified")
            return result
        if container_type in self.container_types:
            result["valid"] = True
            result["container_type"] = container_type
            result["specifications"] = self.container_types[container_type]
        else:
            result["issues"].append(f"Unknown container type: {container_type}")
        return result

    def _validate_weight_volume(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = {"weight": {"valid": True, "value": None, "unit": None, "issues": []},
                  "volume": {"valid": True, "value": None, "unit": None, "issues": []},
                  "container_compatibility": True, "issues": []}
        container_type = str(data.get("container_type", "")).upper()
        weight_str = data.get("weight")
        volume_str = data.get("volume")
        # Weight
        if weight_str:
            try:
                match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|kgs|ton|tons|mt|lbs|pounds|t)?', str(weight_str).lower())
                if match:
                    value = float(match.group(1))
                    unit = match.group(2) or "kg"
                    weight_in_tons = self._convert_to_tons(value, unit)
                    result["weight"].update({"valid": True, "value": weight_in_tons, "unit": "tons"})
                    if container_type in self.validation_config["weight_limits"]:
                        limits = self.validation_config["weight_limits"][container_type]
                        if weight_in_tons < limits["min"] or weight_in_tons > limits["max"]:
                            result["weight"]["valid"] = False
                            result["issues"].append(f"Weight {weight_in_tons}t out of bounds for {container_type}")
                else:
                    result["weight"]["valid"] = False
                    result["weight"]["issues"].append(f"Cannot parse weight: {weight_str}")
            except Exception as e:
                result["weight"]["valid"] = False
                result["weight"]["issues"].append(str(e))
        # Volume
        if volume_str:
            try:
                match = re.search(r'(\d+(?:\.\d+)?)\s*(cbm|m3|cubic\s*meter|ft3|cubic\s*feet)?', str(volume_str).lower())
                if match:
                    value = float(match.group(1))
                    unit = match.group(2) or "cbm"
                    volume_in_cbm = self._convert_to_cbm(value, unit)
                    result["volume"].update({"valid": True, "value": volume_in_cbm, "unit": "cbm"})
                    if container_type in self.validation_config["volume_limits"]:
                        limits = self.validation_config["volume_limits"][container_type]
                        if volume_in_cbm < limits["min"] or volume_in_cbm > limits["max"]:
                            result["volume"]["valid"] = False
                            result["issues"].append(f"Volume {volume_in_cbm}cbm out of bounds for {container_type}")
                else:
                    result["volume"]["valid"] = False
                    result["volume"]["issues"].append(f"Cannot parse volume: {volume_str}")
            except Exception as e:
                result["volume"]["valid"] = False
                result["volume"]["issues"].append(str(e))
        if not result["weight"]["valid"] or not result["volume"]["valid"]:
            result["container_compatibility"] = False
        return result

    def _convert_to_tons(self, value: float, unit: str) -> float:
        conversion_factors = {"kg": 0.001, "kgs": 0.001, "ton": 1.0, "tons": 1.0, "mt": 1.0, "t": 1.0, "lbs": 0.000453592, "pounds": 0.000453592}
        return value * conversion_factors.get(str(unit).lower(), 1.0)

    def _convert_to_cbm(self, value: float, unit: str) -> float:
        conversion_factors = {"cbm": 1.0, "m3": 1.0, "cubic meter": 1.0, "ft3": 0.0283168, "cubic feet": 0.0283168}
        return value * conversion_factors.get(str(unit).lower().replace(" ", ""), 1.0)

    def _validate_dates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = {"shipment_date": {"valid": True, "parsed_date": None, "issues": []}}
        shipment_date_str = data.get("shipment_date")
        if shipment_date_str:
            try:
                for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d", "%B %d, %Y", "%d %B %Y", "%b %d, %Y", "%d %b %Y"]:
                    try:
                        parsed_date = datetime.strptime(str(shipment_date_str).strip(), fmt)
                        result["shipment_date"].update({"valid": True, "parsed_date": parsed_date, "formatted_date": parsed_date.strftime("%Y-%m-%d")})
                        break
                    except ValueError:
                        continue
                else:
                    result["shipment_date"]["valid"] = False
                    result["shipment_date"]["issues"].append(f"Cannot parse shipment date: {shipment_date_str}")
            except Exception as e:
                result["shipment_date"]["valid"] = False
                result["shipment_date"]["issues"].append(str(e))
        return result

    def _validate_commodity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = {"valid": True, "commodity": None, "category": None, "container_compatibility": True, "issues": []}
        commodity = str(data.get("commodity", "")).lower().strip()
        container_type = str(data.get("container_type", "")).upper()
        if not commodity:
            result["issues"].append("Commodity not specified")
            result["valid"] = False
            return result
        if commodity in self.commodity_codes:
            info = self.commodity_codes[commodity]
            result["commodity"] = commodity
            result["category"] = info["category"]
            if container_type and container_type not in info["common_containers"]:
                result["container_compatibility"] = False
                result["issues"].append(f"Container {container_type} not typical for {commodity}")
        else:
            result["issues"].append(f"Unknown commodity: {commodity}")
            result["valid"] = False
        return result

    def _validate_business_logic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = {"valid": True, "issues": [], "warnings": []}
        quantity = data.get("quantity", 1)
        try:
            quantity = int(quantity) if quantity else 1
        except (ValueError, TypeError):
            result["issues"].append(f"Invalid quantity: {quantity}")
            quantity = 1
        shipment_type = str(data.get("shipment_type", "")).upper()
        container_type = str(data.get("container_type", "")).upper()
        if shipment_type == "LCL" and quantity > 1:
            result["warnings"].append("LCL shipments typically don't specify container quantity")
        if shipment_type == "FCL" and quantity > 50:
            result["warnings"].append(f"High container quantity for FCL: {quantity}")
        return result

    def _calculate_overall_validity(self, results: Dict[str, Any]) -> None:
        all_issues = results.get("invalid_fields", [])
        for section, details in results.get("validation_details", {}).items():
            if isinstance(details, dict) and "issues" in details:
                all_issues.extend(details["issues"])
        results["overall_validity"] = len(all_issues) == 0
        results["invalid_fields"] = list(set(all_issues))
        if not results["overall_validity"]:
            results["completeness_score"] *= 0.8

    def _generate_recommendations(self, results: Dict[str, Any], extraction_data: Dict[str, Any]) -> None:
        recommendations = []
        missing_fields = results.get("missing_fields", [])
        if missing_fields:
            recommendations.append({
                "type": "missing_data",
                "priority": "high",
                "message": f"Request missing information: {', '.join(missing_fields)}",
                "action": "send_clarification_email",
                "fields": missing_fields
            })
        results["recommendations"] = recommendations

    def _create_validated_data(self, extraction_data: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        validated_data = extraction_data.copy()
        port_details = results.get("validation_details", {}).get("ports", {})
        if port_details.get("origin", {}).get("valid"):
            validated_data["origin_code"] = port_details["origin"]["code"]
            validated_data["origin_name"] = port_details["origin"]["name"]
            validated_data["origin_country"] = port_details["origin"]["country"]
        if port_details.get("destination", {}).get("valid"):
            validated_data["destination_code"] = port_details["destination"]["code"]
            validated_data["destination_name"] = port_details["destination"]["name"]
            validated_data["destination_country"] = port_details["destination"]["country"]
        container_details = results.get("validation_details", {}).get("container", {})
        if container_details.get("valid"):
            validated_data["container_type"] = container_details["container_type"]
            validated_data["container_specifications"] = container_details["specifications"]
        return validated_data

    def _llm_validate(self, extraction_data: dict, classic_results: dict) -> dict:
        """
        Use LLM to review extracted shipment data and classic validation results.
        Returns a dict with any additional issues, missing fields, and suggestions.
        """
        import json

        function_schema = {
            "name": "llm_shipment_validation_review",
            "description": "Review shipment data and classic validation results, suggest additional issues or clarifications.",
            "parameters": {
                "type": "object",
                "properties": {
                    "llm_additional_issues": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional issues or concerns found by LLM"
                    },
                    "llm_missing_fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Any missing or unclear fields the LLM detects"
                    },
                    "llm_clarification_message": {
                        "type": "string",
                        "description": "Suggested clarification message for the customer"
                    },
                    "llm_recommendations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Additional recommendations from LLM"
                    }
                },
                "required": ["llm_additional_issues", "llm_missing_fields", "llm_clarification_message", "llm_recommendations"]
            }
        }

        prompt = f"""
You are a shipment validation expert. Review the following extracted shipment data and classic validation results.
- Identify any additional issues, missing fields, or business logic concerns not already flagged.
- Suggest a clarification message for the customer if needed.
- Suggest any additional recommendations.

Shipment Data:
{json.dumps(extraction_data, indent=2)}

Classic Validation Results:
{json.dumps(classic_results, indent=2)}

Return:
- llm_additional_issues: list of new issues or concerns
- llm_missing_fields: list of missing or unclear fields
- llm_clarification_message: suggested message for the customer
- llm_recommendations: list of recommendations
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
            tool_args = json.loads(tool_args)
        return dict(tool_args)