"""Validation agent for shipment data validation and completeness checking"""

import os
import sys
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import json

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import base agent
try:
    from .base_agent import BaseAgent
except ImportError:
    try:
        from base_agent import BaseAgent
    except ImportError as e:
        import logging
        logging.error(f"Cannot import BaseAgent: {e}")
        # Create minimal fallback
        from abc import ABC, abstractmethod
        class BaseAgent(ABC):
            def __init__(self, name): 
                self.agent_name = name
                self.logger = logging.getLogger(name)
                self.client = None
                self.config = {}
            def load_context(self): return True
            @abstractmethod
            def process(self, input_data): pass
            def run(self, input_data): 
                try:
                    result = self.process(input_data)
                    result["status"] = "success"
                    return result
                except Exception as e:
                    return {"error": str(e), "status": "error"}

class ValidationAgent(BaseAgent):
    """Agent for validating extracted shipment data and checking completeness"""

    def __init__(self):
        super().__init__("validation_agent")
        
        # Validation rules and data
        self.port_codes = self._load_port_codes()
        self.container_types = self._load_container_types()
        self.commodity_codes = self._load_commodity_codes()
        
        # Validation thresholds
        self.validation_config = {
            "weight_limits": {
                "20DC": {"min": 0.1, "max": 28},  # tons
                "40DC": {"min": 0.1, "max": 29},
                "40HC": {"min": 0.1, "max": 29},
                "20RE": {"min": 0.1, "max": 25},
                "40RH": {"min": 0.1, "max": 27},
                "20TK": {"min": 0.1, "max": 26}
            },
            "volume_limits": {
                "20DC": {"min": 0.1, "max": 33},  # CBM
                "40DC": {"min": 0.1, "max": 67},
                "40HC": {"min": 0.1, "max": 76},
                "20RE": {"min": 0.1, "max": 28},
                "40RH": {"min": 0.1, "max": 60},
                "20TK": {"min": 0.1, "max": 26}
            },
            "date_range": {
                "min_days_ahead": -30,  # Can be 30 days in past
                "max_days_ahead": 365   # Max 1 year in future
            },
            "required_fields": {
                "logistics_request": ["origin", "destination", "shipment_type"],
                "confirmation_reply": ["origin", "destination"],
                "forwarder_response": ["origin", "destination", "rate"],
                "clarification_reply": []  # Flexible
            }
        }

    def _load_port_codes(self) -> Dict[str, Dict[str, str]]:
        """Load port codes database (UNLOCODE format)"""
        # In production, this would load from a comprehensive database
        # For now, using common ports from your data
        return {
            # UAE Ports
            "AEAUH": {"name": "Abu Dhabi", "country": "UAE", "region": "Middle East"},
            "AEDXB": {"name": "Dubai", "country": "UAE", "region": "Middle East"},
            "AESHJ": {"name": "Sharjah", "country": "UAE", "region": "Middle East"},
            
            # Australia Ports
            "AUBNE": {"name": "Brisbane", "country": "Australia", "region": "Oceania"},
            "AUMEL": {"name": "Melbourne", "country": "Australia", "region": "Oceania"},
            "AUSYD": {"name": "Sydney", "country": "Australia", "region": "Oceania"},
            "AUPER": {"name": "Perth", "country": "Australia", "region": "Oceania"},
            
            # Bangladesh Ports
            "BDCGP": {"name": "Chittagong", "country": "Bangladesh", "region": "Asia"},
            "BDMGL": {"name": "Mongla", "country": "Bangladesh", "region": "Asia"},
            
            # Belgium Ports
            "BEANR": {"name": "Antwerpen", "country": "Belgium", "region": "Europe"},
            "BEZEE": {"name": "Zeebrugge", "country": "Belgium", "region": "Europe"},
            
            # Major Global Ports
            "CNSHA": {"name": "Shanghai", "country": "China", "region": "Asia"},
            "CNYTN": {"name": "Yantian", "country": "China", "region": "Asia"},
            "SGSIN": {"name": "Singapore", "country": "Singapore", "region": "Asia"},
            "NLRTM": {"name": "Rotterdam", "country": "Netherlands", "region": "Europe"},
            "DEHAM": {"name": "Hamburg", "country": "Germany", "region": "Europe"},
            "USNYC": {"name": "New York", "country": "USA", "region": "North America"},
            "USLAX": {"name": "Los Angeles", "country": "USA", "region": "North America"},
            "USLGB": {"name": "Long Beach", "country": "USA", "region": "North America"},
            "INMUN": {"name": "Mumbai", "country": "India", "region": "Asia"},
            "INCCU": {"name": "Calcutta", "country": "India", "region": "Asia"},
            "GBFXT": {"name": "Felixstowe", "country": "UK", "region": "Europe"}
        }

    def _load_container_types(self) -> Dict[str, Dict[str, Any]]:
        """Load container type specifications"""
        return {
            "20DC": {
                "name": "20ft Dry Container",
                "category": "dry",
                "length": 20,
                "max_weight": 28,
                "max_volume": 33,
                "common": True
            },
            "40DC": {
                "name": "40ft Dry Container", 
                "category": "dry",
                "length": 40,
                "max_weight": 29,
                "max_volume": 67,
                "common": True
            },
            "40HC": {
                "name": "40ft High Cube Container",
                "category": "dry",
                "length": 40,
                "max_weight": 29,
                "max_volume": 76,
                "common": True
            },
            "20RE": {
                "name": "20ft Reefer Container",
                "category": "reefer",
                "length": 20,
                "max_weight": 25,
                "max_volume": 28,
                "common": False,
                "special_requirements": ["temperature_control", "power_supply"]
            },
            "40RH": {
                "name": "40ft Reefer High Cube",
                "category": "reefer", 
                "length": 40,
                "max_weight": 27,
                "max_volume": 60,
                "common": False,
                "special_requirements": ["temperature_control", "power_supply"]
            },
            "20TK": {
                "name": "20ft Tank Container",
                "category": "tank",
                "length": 20,
                "max_weight": 26,
                "max_volume": 26,
                "common": False,
                "special_requirements": ["hazmat_certification", "cleaning"]
            },
            "40TK": {
                "name": "40ft Tank Container",
                "category": "tank",
                "length": 40,
                "max_weight": 30,
                "max_volume": 35,
                "common": False,
                "special_requirements": ["hazmat_certification", "cleaning"]
            }
        }

    def _load_commodity_codes(self) -> Dict[str, Dict[str, Any]]:
        """Load commodity classification codes"""
        return {
            "electronics": {
                "hs_code_prefix": "85",
                "category": "manufactured",
                "special_handling": ["fragile", "moisture_sensitive"],
                "common_containers": ["20DC", "40DC", "40HC"]
            },
            "textiles": {
                "hs_code_prefix": "50-63",
                "category": "manufactured", 
                "special_handling": ["moisture_sensitive"],
                "common_containers": ["20DC", "40DC", "40HC"]
            },
            "machinery": {
                "hs_code_prefix": "84",
                "category": "manufactured",
                "special_handling": ["heavy_lift", "fragile"],
                "common_containers": ["20DC", "40DC", "40HC"]
            },
            "food": {
                "hs_code_prefix": "01-24",
                "category": "perishable",
                "special_handling": ["temperature_control", "expiry_sensitive"],
                "common_containers": ["20RE", "40RH"]
            },
            "chemicals": {
                "hs_code_prefix": "28-38",
                "category": "hazardous",
                "special_handling": ["hazmat", "msds_required"],
                "common_containers": ["20TK", "40TK", "20DC", "40DC"]
            },
            "furniture": {
                "hs_code_prefix": "94",
                "category": "manufactured",
                "special_handling": ["fragile", "volume_heavy"],
                "common_containers": ["40HC", "40DC"]
            },
            "general cargo": {
                "hs_code_prefix": "99",
                "category": "general",
                "special_handling": [],
                "common_containers": ["20DC", "40DC", "40HC"]
            }
        }

    def process(self, input_data: dict) -> dict:
        """
        Validate extracted shipment data using classic logic and LLM review.
        """
        extraction_data = input_data.get("extraction_data", {})
        email_type = input_data.get("email_type", "logistics_request")

        if not extraction_data:
            return {"error": "No extraction data provided for validation"}

        # --- Step 1: Classic Validation ---
        classic_results = {
            "overall_validity": True,
            "completeness_score": 0.0,
            "validation_details": {},
            "missing_fields": [],
            "invalid_fields": [],
            "warnings": [],
            "recommendations": [],
            "validated_data": {}
        }

        # 1. Field completeness validation
        completeness_result = self._validate_completeness(extraction_data, email_type)
        classic_results.update(completeness_result)

        # 2. Port code validation
        port_result = self._validate_ports(extraction_data)
        classic_results["validation_details"]["ports"] = port_result

        # 3. Container type validation
        container_result = self._validate_container_type(extraction_data)
        classic_results["validation_details"]["container"] = container_result

        # 4. Weight and volume validation
        weight_volume_result = self._validate_weight_volume(extraction_data)
        classic_results["validation_details"]["weight_volume"] = weight_volume_result

        # 5. Date validation
        date_result = self._validate_dates(extraction_data)
        classic_results["validation_details"]["dates"] = date_result

        # 6. Commodity validation
        commodity_result = self._validate_commodity(extraction_data)
        classic_results["validation_details"]["commodity"] = commodity_result

        # 7. Business logic validation
        business_result = self._validate_business_logic(extraction_data)
        classic_results["validation_details"]["business_logic"] = business_result

        # 8. Calculate overall validity and scores
        self._calculate_overall_validity(classic_results)

        # 9. Generate recommendations
        self._generate_recommendations(classic_results, extraction_data)

        # 10. Create validated/normalized data
        classic_results["validated_data"] = self._create_validated_data(extraction_data, classic_results)

        # --- Step 2: LLM Validation (if available) ---
        if self.client:
            try:
                llm_review = self._llm_validate(extraction_data, classic_results)
                # Merge LLM findings into results
                classic_results["llm_additional_issues"] = llm_review.get("llm_additional_issues", [])
                classic_results["llm_missing_fields"] = llm_review.get("llm_missing_fields", [])
                classic_results["llm_clarification_message"] = llm_review.get("llm_clarification_message", "")
                classic_results["llm_recommendations"] = llm_review.get("llm_recommendations", [])
            except Exception as e:
                classic_results["llm_error"] = f"LLM validation failed: {e}"

        return classic_results

    def _validate_completeness(self, data: Dict[str, Any], email_type: str) -> Dict[str, Any]:
        """Validate field completeness based on email type"""
        
        required_fields = self.validation_config["required_fields"].get(email_type, [])
        
        # Map extraction fields to validation fields
        field_mapping = {
            "origin": ["origin", "origin_port", "from_port"],
            "destination": ["destination", "destination_port", "to_port"],
            "shipment_type": ["shipment_type", "container_type"],
            "rate": ["rate", "price", "cost", "quote"]
        }
        
        missing_fields = []
        present_fields = []
        
        for required_field in required_fields:
            field_found = False
            possible_keys = field_mapping.get(required_field, [required_field])
            
            for key in possible_keys:
                if key in data and data[key] and str(data[key]).strip() not in ["", "None", "Unknown"]:
                    field_found = True
                    present_fields.append(required_field)
                    break
            
            if not field_found:
                missing_fields.append(required_field)
        
        # Calculate completeness score
        total_important_fields = ["origin", "destination", "shipment_type", "container_type", "quantity"]
        present_important = 0
        
        for field in total_important_fields:
            possible_keys = field_mapping.get(field, [field])
            for key in possible_keys:
                if key in data and data[key] and str(data[key]).strip() not in ["", "None", "Unknown"]:
                    present_important += 1
                    break
        
        completeness_score = present_important / len(total_important_fields)
        
        return {
            "missing_fields": missing_fields,
            "present_fields": present_fields,
            "completeness_score": round(completeness_score, 2)
        }

    def _validate_ports(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate origin and destination port codes"""
        
        result = {
            "origin": {"valid": False, "code": None, "name": None, "country": None},
            "destination": {"valid": False, "code": None, "name": None, "country": None},
            "issues": []
        }
        
        # Validate origin
        origin = data.get("origin")
        if origin:
            origin_validation = self._validate_single_port(origin)
            result["origin"] = origin_validation
            if not origin_validation["valid"]:
                result["issues"].append(f"Invalid origin port: {origin}")
        
        # Validate destination
        destination = data.get("destination")
        if destination:
            destination_validation = self._validate_single_port(destination)
            result["destination"] = destination_validation
            if not destination_validation["valid"]:
                result["issues"].append(f"Invalid destination port: {destination}")
        
        # Check for same origin and destination
        if (result["origin"]["valid"] and result["destination"]["valid"] and 
            result["origin"]["code"] == result["destination"]["code"]):
            result["issues"].append("Origin and destination cannot be the same")
        
        return result

    def _validate_single_port(self, port_input: str) -> Dict[str, Any]:
        """Validate a single port code or name"""
        
        if not port_input or not isinstance(port_input, str):
            return {"valid": False, "code": None, "name": None, "country": None, "reason": "Empty or invalid input"}
        
        port_input = port_input.strip().upper()
        
        # Direct code match
        if port_input in self.port_codes:
            port_info = self.port_codes[port_input]
            return {
                "valid": True,
                "code": port_input,
                "name": port_info["name"],
                "country": port_info["country"],
                "region": port_info["region"]
            }
        
        # Name-based search
        for code, info in self.port_codes.items():
            if info["name"].upper() == port_input:
                return {
                    "valid": True,
                    "code": code,
                    "name": info["name"],
                    "country": info["country"],
                    "region": info["region"]
                }
        
        # Partial name match
        matches = []
        for code, info in self.port_codes.items():
            if port_input in info["name"].upper() or info["name"].upper() in port_input:
                matches.append({
                    "code": code,
                    "name": info["name"],
                    "country": info["country"]
                })
        
        if matches:
            return {
                "valid": False,
                "code": None,
                "name": None,
                "country": None,
                "reason": f"Ambiguous port name. Possible matches: {matches[:3]}"
            }
        
        # UNLOCODE format validation
        if len(port_input) == 5 and port_input[:2].isalpha() and port_input[2:].isalpha():
            return {
                "valid": False,
                "code": port_input,
                "name": None,
                "country": port_input[:2],
                "reason": "Valid UNLOCODE format but not in database"
            }
        
        return {
            "valid": False,
            "code": None,
            "name": None,
            "country": None,
            "reason": "Invalid port code or name format"
        }

    def _validate_container_type(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate container type and specifications"""
        
        result = {
            "valid": False,
            "container_type": None,
            "specifications": {},
            "issues": []
        }
        
        container_type = data.get("container_type") or data.get("shipment_type")
        
        if not container_type:
            result["issues"].append("Container type not specified")
            return result
        
        # Normalize container type
        container_type = str(container_type).strip().upper()
        
        # Handle common variations
        container_mapping = {
            "FCL": "40DC",  # Default FCL to 40DC
            "LCL": "LCL",   # LCL is not a container type
            "20GP": "20DC",
            "40GP": "40DC",
            "40HQ": "40HC",
            "20RF": "20RE",
            "40RF": "40RH"
        }
        
        normalized_type = container_mapping.get(container_type, container_type)
        
        if normalized_type == "LCL":
            result.update({
                "valid": True,
                "container_type": "LCL",
                "specifications": {
                    "name": "Less than Container Load",
                    "category": "consolidation",
                    "note": "Shared container space"
                }
            })
            return result
        
        if normalized_type in self.container_types:
            container_info = self.container_types[normalized_type]
            result.update({
                "valid": True,
                "container_type": normalized_type,
                "specifications": container_info
            })
        else:
            result["issues"].append(f"Unknown container type: {container_type}")
            # Suggest similar types
            suggestions = self._suggest_container_types(container_type)
            if suggestions:
                result["suggestions"] = suggestions
        
        return result

    def _suggest_container_types(self, invalid_type: str) -> List[str]:
        """Suggest similar container types"""
        suggestions = []
        invalid_type = invalid_type.upper()
        
        # Simple similarity matching
        for container_type in self.container_types.keys():
            if (invalid_type in container_type or 
                container_type in invalid_type or
                self._calculate_similarity(invalid_type, container_type) > 0.6):
                suggestions.append(container_type)
        
        return suggestions[:3]  # Return top 3 suggestions

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate simple string similarity"""
        if not str1 or not str2:
            return 0.0
        
        # Simple character overlap ratio
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0

    def _validate_weight_volume(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate weight and volume against container limits"""
        
        result = {
            "weight": {"valid": True, "value": None, "unit": None, "issues": []},
            "volume": {"valid": True, "value": None, "unit": None, "issues": []},
            "container_compatibility": True,
            "issues": []
        }
        
        container_type = data.get("container_type", "").upper()
        weight_str = data.get("weight")
        volume_str = data.get("volume")
        
        # Validate weight
        if weight_str:
            weight_validation = self._parse_and_validate_weight(weight_str, container_type)
            result["weight"] = weight_validation
        
        # Validate volume
        if volume_str:
            volume_validation = self._parse_and_validate_volume(volume_str, container_type)
            result["volume"] = volume_validation
        
        # Check container compatibility
        if not result["weight"]["valid"] or not result["volume"]["valid"]:
            result["container_compatibility"] = False
        
        return result

    def _convert_to_tons(self, value: float, unit: str) -> float:
        """Convert weight to tons"""
        conversion_factors = {
            "kg": 0.001,
            "kgs": 0.001,
            "ton": 1.0,
            "tons": 1.0,
            "mt": 1.0,
            "t": 1.0,
            "lbs": 0.000453592,
            "pounds": 0.000453592
        }
        
        factor = conversion_factors.get(unit.lower(), 1.0)
        return value * factor

    def _convert_to_cbm(self, value: float, unit: str) -> float:
        """Convert volume to CBM"""
        conversion_factors = {
            "cbm": 1.0,
            "m3": 1.0,
            "cubic meter": 1.0,
            "ft3": 0.0283168,
            "cubic feet": 0.0283168
        }
        
        unit_clean = unit.lower().replace(" ", "")
        factor = conversion_factors.get(unit_clean, 1.0)
        return value * factor

    def _validate_dates(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate shipment dates"""
        
        result = {
            "shipment_date": {"valid": True, "parsed_date": None, "issues": []},
            "delivery_date": {"valid": True, "parsed_date": None, "issues": []},
            "date_logic": {"valid": True, "issues": []}
        }
        
        shipment_date_str = data.get("shipment_date")
        delivery_date_str = data.get("delivery_date")
        
        # Validate shipment date
        if shipment_date_str:
            shipment_validation = self._parse_and_validate_date(shipment_date_str, "shipment")
            result["shipment_date"] = shipment_validation
        
        # Validate delivery date
        if delivery_date_str:
            delivery_validation = self._parse_and_validate_date(delivery_date_str, "delivery")
            result["delivery_date"] = delivery_validation
        
        # Validate date logic
        if (result["shipment_date"]["parsed_date"] and result["delivery_date"]["parsed_date"]):
            if result["shipment_date"]["parsed_date"] >= result["delivery_date"]["parsed_date"]:
                result["date_logic"]["valid"] = False
                result["date_logic"]["issues"].append("Shipment date must be before delivery date")
        
        return result

    def _parse_and_validate_date(self, date_str: str, date_type: str) -> Dict[str, Any]:
        """Parse and validate a date string"""
        
        result = {"valid": False, "parsed_date": None, "issues": []}
        
        if not date_str:
            return result
        
        # Try multiple date formats
        date_formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%B %d, %Y",
            "%d %B %Y",
            "%b %d, %Y",
            "%d %b %Y"
        ]
        
        parsed_date = None
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(str(date_str).strip(), fmt)
                break
            except ValueError:
                continue
        
        if not parsed_date:
            result["issues"].append(f"Cannot parse {date_type} date: {date_str}")
            return result
        
        result.update({
            "valid": True,
            "parsed_date": parsed_date,
            "formatted_date": parsed_date.strftime("%Y-%m-%d")
        })
        
        # Validate date range
        today = datetime.now()
        min_date = today + timedelta(days=self.validation_config["date_range"]["min_days_ahead"])
        max_date = today + timedelta(days=self.validation_config["date_range"]["max_days_ahead"])
        
        if parsed_date < min_date:
            result["issues"].append(f"{date_type.title()} date too far in past: {parsed_date.strftime('%Y-%m-%d')}")
        elif parsed_date > max_date:
            result["issues"].append(f"{date_type.title()} date too far in future: {parsed_date.strftime('%Y-%m-%d')}")
        
        return result

    def _validate_commodity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate commodity information"""
        
        result = {
            "valid": True,
            "commodity": None,
            "category": None,
            "special_handling": [],
            "container_compatibility": True,
            "issues": []
        }
        
        commodity = data.get("commodity")
        container_type = data.get("container_type", "").upper()
        
        if not commodity:
            result["issues"].append("Commodity not specified")
            return result
        
        commodity = str(commodity).lower().strip()
        
        # Find commodity in database
        if commodity in self.commodity_codes:
            commodity_info = self.commodity_codes[commodity]
            result.update({
                "valid": True,
                "commodity": commodity,
                "category": commodity_info["category"],
                "hs_code_prefix": commodity_info["hs_code_prefix"],
                "special_handling": commodity_info["special_handling"],
                "recommended_containers": commodity_info["common_containers"]
            })
            
            # Check container compatibility
            if container_type and container_type not in commodity_info["common_containers"]:
                result["container_compatibility"] = False
                result["issues"].append(
                    f"Container {container_type} not typically used for {commodity}. "
                    f"Recommended: {commodity_info['common_containers']}"
                )
        else:
            # Try partial matching
            matches = []
            for comm_code, comm_info in self.commodity_codes.items():
                if commodity in comm_code or comm_code in commodity:
                    matches.append(comm_code)
            
            if matches:
                result["issues"].append(f"Commodity '{commodity}' not found. Similar: {matches}")
            else:
                result["issues"].append(f"Unknown commodity: {commodity}")
                # Default to general cargo
                result.update({
                    "commodity": "general cargo",
                    "category": "general",
                    "special_handling": [],
                    "recommended_containers": ["20DC", "40DC", "40HC"]
                })
        
        return result

    def _validate_business_logic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate business logic and cross-field consistency"""
        
        result = {
            "valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check quantity vs container type
        quantity = data.get("quantity", 1)
        container_type = data.get("container_type", "").upper()
        shipment_type = data.get("shipment_type", "").upper()
        
        try:
            quantity = int(quantity) if quantity else 1
        except (ValueError, TypeError):
            result["issues"].append(f"Invalid quantity: {quantity}")
            quantity = 1
        
        # LCL should not have multiple containers
        if shipment_type == "LCL" and quantity > 1:
            result["warnings"].append("LCL shipments typically don't specify container quantity")
        
        # FCL should have reasonable quantity
        if shipment_type == "FCL" and quantity > 50:
            result["warnings"].append(f"High container quantity for FCL: {quantity}")
        
        # Check dangerous goods vs container type
        dangerous_goods = data.get("dangerous_goods", False)
        if dangerous_goods and container_type in ["20RE", "40RH"]:
            result["issues"].append("Dangerous goods typically not allowed in reefer containers")
        
        # Check special requirements consistency
        special_requirements = data.get("special_requirements", "")
        if special_requirements:
            if "refrigerated" in special_requirements.lower():
                if container_type not in ["20RE", "40RH"]:
                    result["warnings"].append(
                        f"Refrigerated requirement but container type is {container_type}. "
                        "Consider 20RE or 40RH"
                    )
            
            if "urgent" in special_requirements.lower():
                result["warnings"].append("Urgent shipment - consider air freight alternative")
        
        # Validate weight vs quantity
        weight_str = data.get("weight")
        if weight_str and quantity:
            try:
                # Extract numeric weight
                weight_match = re.search(r'(\d+(?:\.\d+)?)', str(weight_str))
                if weight_match:
                    total_weight = float(weight_match.group(1))
                    if "kg" in str(weight_str).lower():
                        total_weight = total_weight / 1000  # Convert to tons
                    
                    weight_per_container = total_weight / quantity
                    
                    if container_type in self.validation_config["weight_limits"]:
                        max_weight = self.validation_config["weight_limits"][container_type]["max"]
                        if weight_per_container > max_weight:
                            result["issues"].append(
                                f"Weight per container ({weight_per_container:.1f}t) exceeds "
                                f"{container_type} limit ({max_weight}t)"
                            )
            except (ValueError, TypeError):
                pass  # Skip weight validation if parsing fails
        
        return result

    def _calculate_overall_validity(self, validation_results: Dict[str, Any]) -> None:
        """Calculate overall validity and update results"""
        
        # Collect all issues
        all_issues = validation_results.get("invalid_fields", [])
        all_warnings = validation_results.get("warnings", [])
        
        for section, details in validation_results.get("validation_details", {}).items():
            if isinstance(details, dict):
                if "issues" in details:
                    all_issues.extend(details["issues"])
                
                # Check nested structures
                for key, value in details.items():
                    if isinstance(value, dict) and "issues" in value:
                        all_issues.extend(value["issues"])
        
        # Update overall validity
        validation_results["overall_validity"] = len(all_issues) == 0
        validation_results["invalid_fields"] = list(set(all_issues))  # Remove duplicates
        
        # Adjust completeness score based on validity
        if not validation_results["overall_validity"]:
            validation_results["completeness_score"] *= 0.8  # Penalize for invalid data

    def _generate_recommendations(self, validation_results: Dict[str, Any], 
                                extraction_data: Dict[str, Any]) -> None:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        # Missing field recommendations
        missing_fields = validation_results.get("missing_fields", [])
        if missing_fields:
            recommendations.append({
                "type": "missing_data",
                "priority": "high",
                "message": f"Request missing information: {', '.join(missing_fields)}",
                "action": "send_clarification_email",
                "fields": missing_fields
            })
        
        # Port validation recommendations
        port_details = validation_results.get("validation_details", {}).get("ports", {})
        if port_details.get("issues"):
            recommendations.append({
                "type": "port_validation",
                "priority": "high",
                "message": "Clarify port information",
                "action": "request_port_clarification",
                "issues": port_details["issues"]
            })
        
        # Container type recommendations
        container_details = validation_results.get("validation_details", {}).get("container", {})
        if not container_details.get("valid") and container_details.get("suggestions"):
            recommendations.append({
                "type": "container_suggestion",
                "priority": "medium",
                "message": f"Suggest container types: {container_details['suggestions']}",
                "action": "suggest_alternatives",
                "suggestions": container_details["suggestions"]
            })
        
        # Weight/volume recommendations
        weight_volume = validation_results.get("validation_details", {}).get("weight_volume", {})
        if not weight_volume.get("container_compatibility"):
            recommendations.append({
                "type": "container_capacity",
                "priority": "high",
                "message": "Weight/volume exceeds container capacity",
                "action": "suggest_larger_container",
                "current_container": extraction_data.get("container_type")
            })
        
        # Commodity recommendations
        commodity_details = validation_results.get("validation_details", {}).get("commodity", {})
        if not commodity_details.get("container_compatibility"):
            recommendations.append({
                "type": "commodity_container",
                "priority": "medium",
                "message": "Container type not optimal for commodity",
                "action": "suggest_suitable_container",
                "recommended_containers": commodity_details.get("recommended_containers", [])
            })
        
        # Business logic recommendations
        business_details = validation_results.get("validation_details", {}).get("business_logic", {})
        if business_details.get("warnings"):
            for warning in business_details["warnings"]:
                recommendations.append({
                    "type": "business_logic",
                    "priority": "low",
                    "message": warning,
                    "action": "review_requirements"
                })
        
        validation_results["recommendations"] = recommendations

    def _create_validated_data(self, extraction_data: Dict[str, Any], 
                             validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create normalized and validated data structure"""
        
        validated_data = extraction_data.copy()
        
        # Normalize port codes
        port_details = validation_results.get("validation_details", {}).get("ports", {})
        if port_details.get("origin", {}).get("valid"):
            origin_info = port_details["origin"]
            validated_data.update({
                "origin_code": origin_info["code"],
                "origin_name": origin_info["name"],
                "origin_country": origin_info["country"]
            })
        
        if port_details.get("destination", {}).get("valid"):
            dest_info = port_details["destination"]
            validated_data.update({
                "destination_code": dest_info["code"],
                "destination_name": dest_info["name"],
                "destination_country": dest_info["country"]
            })
        
        # Normalize container type
        container_details = validation_results.get("validation_details", {}).get("container", {})
        if container_details.get("valid"):
            validated_data["container_type"] = container_details["container_type"]
            validated_data["container_specifications"] = container_details["specifications"]
        
        # Normalize weight and volume - FIX: Check for keys before accessing
        weight_volume = validation_results.get("validation_details", {}).get("weight_volume", {})
        if weight_volume.get("weight", {}).get("valid"):
            weight_info = weight_volume["weight"]
            validated_data["weight_tons"] = weight_info["value"]
            # FIX: Only add original if keys exist
            if "original_value" in weight_info and "original_unit" in weight_info:
                validated_data["weight_original"] = f"{weight_info['original_value']} {weight_info['original_unit']}"
        
        if weight_volume.get("volume", {}).get("valid"):
            volume_info = weight_volume["volume"]
            validated_data["volume_cbm"] = volume_info["value"]
            # FIX: Only add original if keys exist
            if "original_value" in volume_info and "original_unit" in volume_info:
                validated_data["volume_original"] = f"{volume_info['original_value']} {volume_info['original_unit']}"
        
        # Normalize dates - FIX: Check for formatted_date key
        date_details = validation_results.get("validation_details", {}).get("dates", {})
        if date_details.get("shipment_date", {}).get("valid"):
            shipment_date_info = date_details["shipment_date"]
            if "formatted_date" in shipment_date_info:
                validated_data["shipment_date_normalized"] = shipment_date_info["formatted_date"]
        
        if date_details.get("delivery_date", {}).get("valid"):
            delivery_date_info = date_details["delivery_date"]
            if "formatted_date" in delivery_date_info:
                validated_data["delivery_date_normalized"] = delivery_date_info["formatted_date"]
        
        # Add validation metadata
        validated_data["validation_metadata"] = {
            "validated_at": datetime.utcnow().isoformat(),
            "overall_validity": validation_results["overall_validity"],
            "completeness_score": validation_results["completeness_score"],
            "validation_agent_version": "1.0"
        }
        
        return validated_data

    def _parse_and_validate_weight(self, weight_str: str, container_type: str) -> Dict[str, Any]:
        """Parse and validate weight string"""
        
        result = {"valid": False, "value": None, "unit": None, "issues": []}
        
        if not weight_str:
            return result
        
        # Extract number and unit using regex
        weight_pattern = r'(\d+(?:\.\d+)?)\s*(kg|kgs|ton|tons|mt|lbs|pounds|t)?'
        match = re.search(weight_pattern, str(weight_str).lower())
        
        if not match:
            result["issues"].append(f"Cannot parse weight: {weight_str}")
            return result
        
        value = float(match.group(1))
        unit = match.group(2) or "kg"  # Default to kg
        
        # Normalize to tons
        weight_in_tons = self._convert_to_tons(value, unit)
        
        result.update({
            "valid": True,
            "value": weight_in_tons,
            "unit": "tons",
            "original_value": value,  # FIX: Always include these
            "original_unit": unit
        })
        
        # Validate against container limits
        if container_type in self.validation_config["weight_limits"]:
            limits = self.validation_config["weight_limits"][container_type]
            
            if weight_in_tons < limits["min"]:
                result["issues"].append(f"Weight too low for {container_type}: {weight_in_tons}t < {limits['min']}t")
            elif weight_in_tons > limits["max"]:
                result["issues"].append(f"Weight exceeds {container_type} limit: {weight_in_tons}t > {limits['max']}t")
                result["valid"] = False
        
        return result

    def _parse_and_validate_volume(self, volume_str: str, container_type: str) -> Dict[str, Any]:
        """Parse and validate volume string"""
        
        result = {"valid": False, "value": None, "unit": None, "issues": []}
        
        if not volume_str:
            return result
        
        # Extract number and unit using regex
        volume_pattern = r'(\d+(?:\.\d+)?)\s*(cbm|m3|cubic\s*meter|ft3|cubic\s*feet)?'
        match = re.search(volume_pattern, str(volume_str).lower())
        
        if not match:
            result["issues"].append(f"Cannot parse volume: {volume_str}")
            return result
        
        value = float(match.group(1))
        unit = match.group(2) or "cbm"  # Default to CBM
        
        # Normalize to CBM
        volume_in_cbm = self._convert_to_cbm(value, unit)
        
        result.update({
            "valid": True,
            "value": volume_in_cbm,
            "unit": "cbm",
            "original_value": value,  # FIX: Always include these
            "original_unit": unit
        })
        
        # Validate against container limits
        if container_type in self.validation_config["volume_limits"]:
            limits = self.validation_config["volume_limits"][container_type]
            
            if volume_in_cbm < limits["min"]:
                result["issues"].append(f"Volume too low for {container_type}: {volume_in_cbm}cbm < {limits['min']}cbm")
            elif volume_in_cbm > limits["max"]:
                result["issues"].append(f"Volume exceeds {container_type} limit: {volume_in_cbm}cbm > {limits['max']}cbm")
                result["valid"] = False
        
        return result

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation capabilities"""
        return {
            "supported_ports": len(self.port_codes),
            "supported_containers": list(self.container_types.keys()),
            "supported_commodities": list(self.commodity_codes.keys()),
            "validation_rules": {
                "port_validation": "UNLOCODE format and database lookup",
                "container_validation": "Type specifications and capacity limits",
                "weight_validation": "Container capacity limits",
                "volume_validation": "Container capacity limits",
                "date_validation": "Format parsing and business date ranges",
                "commodity_validation": "HS code classification and container compatibility",
                "business_logic": "Cross-field consistency checks"
            },
            "completeness_scoring": "Based on presence of critical fields",
            "recommendation_engine": "Actionable suggestions for data improvement"
        }

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_validation_agent():
    """Test the validation agent with various scenarios"""
    print("=== Testing Validation Agent ===")
    
    agent = ValidationAgent()
    
    # Test cases with different validation scenarios
    test_cases = [
        {
            "name": "Complete Valid Data",
            "input": {
                "extraction_data": {
                    "origin": "AEAUH",
                    "destination": "AUBNE",
                    "shipment_type": "FCL",
                    "container_type": "40DC",
                    "quantity": 2,
                    "weight": "25 tons",
                    "volume": "60 CBM",
                    "shipment_date": "2024-03-15",
                    "commodity": "electronics"
                },
                "email_type": "logistics_request"
            }
        },
        {
            "name": "Missing Required Fields",
            "input": {
                "extraction_data": {
                    "origin": "AEAUH",
                    "container_type": "20DC",
                    "commodity": "textiles"
                },
                "email_type": "logistics_request"
            }
        },
        {
            "name": "Invalid Port Codes",
            "input": {
                "extraction_data": {
                    "origin": "INVALID",
                    "destination": "NOTFOUND",
                    "container_type": "40HC",
                    "commodity": "machinery"
                },
                "email_type": "logistics_request"
            }
        },
        {
            "name": "Weight Exceeds Container Limit",
            "input": {
                "extraction_data": {
                    "origin": "CNSHA",
                    "destination": "USLAX",
                    "container_type": "20DC",
                    "weight": "35 tons",
                    "commodity": "machinery"
                },
                "email_type": "logistics_request"
            }
        },
        {
            "name": "Container-Commodity Mismatch",
            "input": {
                "extraction_data": {
                    "origin": "SGSIN",
                    "destination": "NLRTM",
                    "container_type": "20DC",
                    "commodity": "food",
                    "special_requirements": "refrigerated"
                },
                "email_type": "logistics_request"
            }
        },
        {
            "name": "Date Validation Issues",
            "input": {
                "extraction_data": {
                    "origin": "INMUN",
                    "destination": "DEHAM",
                    "container_type": "40HC",
                    "shipment_date": "2023-01-01",  # Past date
                    "delivery_date": "2023-01-01",  # Same as shipment
                    "commodity": "textiles"
                },
                "email_type": "logistics_request"
            }
        },
        {
            "name": "LCL Shipment",
            "input": {
                "extraction_data": {
                    "origin": "BEANR",
                    "destination": "USNYC",
                    "shipment_type": "LCL",
                    "volume": "5 CBM",
                    "weight": "2 tons",
                    "commodity": "furniture"
                },
                "email_type": "logistics_request"
            }
        },
        {
            "name": "Dangerous Goods",
            "input": {
                "extraction_data": {
                    "origin": "DEHAM",
                    "destination": "CNSHA",
                    "container_type": "20TK",
                    "commodity": "chemicals",
                    "dangerous_goods": True,
                    "special_requirements": "hazmat certification"
                },
                "email_type": "logistics_request"
            }
        }
    ]
    
    # Load context
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}")
    
    # Run test cases
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        
        result = agent.run(test_case["input"])
        
        if result.get("status") == "success":
            print(f"✓ Overall Valid: {result.get('overall_validity')}")
            print(f"✓ Completeness Score: {result.get('completeness_score')}")
            
            # Show missing fields
            missing = result.get("missing_fields", [])
            if missing:
                print(f"⚠ Missing Fields: {missing}")
            
            # Show invalid fields
            invalid = result.get("invalid_fields", [])
            if invalid:
                print(f"❌ Invalid Fields: {invalid}")
            
            # Show recommendations
            recommendations = result.get("recommendations", [])
            if recommendations:
                print(f"💡 Recommendations ({len(recommendations)}):")
                for rec in recommendations[:3]:  # Show first 3
                    print(f"   - {rec['type']}: {rec['message']}")
            
            # Show validated data summary
            validated_data = result.get("validated_data", {})
            if "origin_code" in validated_data:
                print(f"✓ Normalized Origin: {validated_data['origin_code']} ({validated_data.get('origin_name')})")
            if "destination_code" in validated_data:
                print(f"✓ Normalized Destination: {validated_data['destination_code']} ({validated_data.get('destination_name')})")
            
        else:
            print(f"✗ Error: {result.get('error')}")

def test_port_validation():
    """Test port validation specifically"""
    print("\n=== Testing Port Validation ===")
    
    agent = ValidationAgent()
    agent.load_context()
    
    port_test_cases = [
        "AEAUH",           # Valid code
        "Abu Dhabi",       # Valid name
        "SHANGHAI",        # Valid name (should find CNSHA)
        "INVALID",         # Invalid code
        "Unknown Port",    # Unknown name
        "USXXX",          # Valid format but not in DB
        "",               # Empty
        None              # None
    ]
    
    for port in port_test_cases:
        print(f"\nTesting port: '{port}'")
        result = agent._validate_single_port(port)
        print(f"  Valid: {result['valid']}")
        if result['valid']:
            print(f"  Code: {result['code']}, Name: {result['name']}, Country: {result['country']}")
        else:
            print(f"  Reason: {result.get('reason', 'Unknown')}")

def test_container_validation():
    """Test container type validation"""
    print("\n=== Testing Container Validation ===")
    
    agent = ValidationAgent()
    agent.load_context()
    
    container_test_cases = [
        "20DC",           # Valid
        "40HC",           # Valid
        "FCL",            # Should map to 40DC
        "20GP",           # Should map to 20DC
        "40RF",           # Should map to 40RH
        "LCL",            # Special case
        "INVALID",        # Invalid
        "20XX",           # Invalid but similar
        "",               # Empty
    ]
    
    for container in container_test_cases:
        print(f"\nTesting container: '{container}'")
        test_data = {"container_type": container}
        result = agent._validate_container_type(test_data)
        print(f"  Valid: {result['valid']}")
        if result['valid']:
            print(f"  Type: {result['container_type']}")
            print(f"  Category: {result['specifications'].get('category')}")
        else:
            print(f"  Issues: {result.get('issues', [])}")
            if result.get('suggestions'):
                print(f"  Suggestions: {result['suggestions']}")

def test_weight_volume_validation():
    """Test weight and volume validation"""
    print("\n=== Testing Weight/Volume Validation ===")
    
    agent = ValidationAgent()
    agent.load_context()
    
    weight_volume_test_cases = [
        {
            "container_type": "20DC",
            "weight": "25 tons",
            "volume": "30 CBM"
        },
        {
            "container_type": "20DC", 
            "weight": "35 tons",  # Exceeds limit
            "volume": "40 CBM"    # Exceeds limit
        },
        {
            "container_type": "40HC",
            "weight": "2500 kg",  # Should convert to tons
            "volume": "50 m3"     # Should convert to CBM
        },
        {
            "container_type": "LCL",
            "weight": "invalid weight",
            "volume": "5 CBM"
        }
    ]
    
    for i, test_data in enumerate(weight_volume_test_cases, 1):
        print(f"\n--- Weight/Volume Test {i} ---")
        print(f"Container: {test_data['container_type']}")
        print(f"Weight: {test_data.get('weight')}")
        print(f"Volume: {test_data.get('volume')}")
        
        result = agent._validate_weight_volume(test_data)
        
        weight_result = result.get("weight", {})
        volume_result = result.get("volume", {})
        
        print(f"Weight Valid: {weight_result.get('valid')}")
        if weight_result.get('valid'):
            print(f"  Normalized: {weight_result.get('value')} {weight_result.get('unit')}")
        if weight_result.get('issues'):
            print(f"  Issues: {weight_result['issues']}")
        
        print(f"Volume Valid: {volume_result.get('valid')}")
        if volume_result.get('valid'):
            print(f"  Normalized: {volume_result.get('value')} {volume_result.get('unit')}")
        if volume_result.get('issues'):
            print(f"  Issues: {volume_result['issues']}")

def test_date_validation():
    """Test date validation"""
    print("\n=== Testing Date Validation ===")
    
    agent = ValidationAgent()
    agent.load_context()
    
    date_test_cases = [
        "2024-03-15",      # Valid future date
        "15/03/2024",      # Valid DD/MM/YYYY
        "03/15/2024",      # Valid MM/DD/YYYY
        "March 15, 2024",  # Valid text format
        "2023-01-01",      # Past date
        "2025-12-31",      # Far future
        "invalid date",    # Invalid format
        "",                # Empty
    ]
    
    for date_str in date_test_cases:
        print(f"\nTesting date: '{date_str}'")
        result = agent._parse_and_validate_date(date_str, "shipment")
        print(f"  Valid: {result['valid']}")
        if result['valid']:
            print(f"  Parsed: {result['formatted_date']}")

        if result.get('issues'):
            print(f"  Issues: {result['issues']}")

def test_business_logic_validation():
    """Test business logic validation"""
    print("\n=== Testing Business Logic Validation ===")
    
    agent = ValidationAgent()
    agent.load_context()
    
    business_logic_test_cases = [
        {
            "name": "Normal FCL",
            "data": {
                "shipment_type": "FCL",
                "container_type": "40DC",
                "quantity": 2,
                "weight": "25 tons",
                "commodity": "electronics"
            }
        },
        {
            "name": "LCL with Multiple Containers",
            "data": {
                "shipment_type": "LCL",
                "quantity": 5,  # Should warn
                "volume": "10 CBM",
                "commodity": "textiles"
            }
        },
        {
            "name": "Dangerous Goods in Reefer",
            "data": {
                "container_type": "20RE",
                "dangerous_goods": True,  # Should flag issue
                "commodity": "chemicals"
            }
        },
        {
            "name": "Refrigerated Food in Dry Container",
            "data": {
                "container_type": "40DC",
                "commodity": "food",
                "special_requirements": "refrigerated"  # Should warn
            }
        },
        {
            "name": "High Container Quantity",
            "data": {
                "shipment_type": "FCL",
                "quantity": 100,  # Should warn
                "container_type": "20DC"
            }
        }
    ]
    
    for test_case in business_logic_test_cases:
        print(f"\n--- {test_case['name']} ---")
        result = agent._validate_business_logic(test_case['data'])
        
        print(f"Valid: {result['valid']}")
        if result.get('issues'):
            print(f"Issues: {result['issues']}")
        if result.get('warnings'):
            print(f"Warnings: {result['warnings']}")

def test_validation_summary():
    """Test validation summary functionality"""
    print("\n=== Testing Validation Summary ===")
    
    agent = ValidationAgent()
    summary = agent.get_validation_summary()
    
    print(f"Supported Ports: {summary['supported_ports']}")
    print(f"Supported Containers: {summary['supported_containers']}")
    print(f"Supported Commodities: {summary['supported_commodities']}")
    print("\nValidation Rules:")
    for rule, description in summary['validation_rules'].items():
        print(f"  {rule}: {description}")

def test_integration_with_extraction():
    """Test integration with extraction agent output"""
    print("\n=== Testing Integration with Extraction Agent ===")
    
    # Simulate extraction agent output
    extraction_output = {
        "origin": "Shanghai",  # Name instead of code
        "destination": "Long Beach",  # Name instead of code
        "shipment_type": "FCL",
        "container_type": "40GP",  # Non-standard format
        "quantity": "2",  # String instead of int
        "weight": "25000 kg",  # Different unit
        "volume": "60 m3",  # Different unit
        "shipment_date": "15/03/2024",  # DD/MM/YYYY format
        "commodity": "electronics",
        "dangerous_goods": False,
        "special_requirements": None,
        "extraction_method": "regex_fallback"
    }
    
    agent = ValidationAgent()
    agent.load_context()
    
    input_data = {
        "extraction_data": extraction_output,
        "email_type": "logistics_request"
    }
    
    print("Input extraction data:")
    for key, value in extraction_output.items():
        print(f"  {key}: {value}")
    
    result = agent.run(input_data)
    
    if result.get("status") == "success":
        print(f"\n✓ Validation completed")
        print(f"✓ Overall Valid: {result['overall_validity']}")
        print(f"✓ Completeness Score: {result['completeness_score']}")
        
        validated_data = result.get("validated_data", {})
        print(f"\nNormalized data:")
        
        # Show key normalized fields
        normalized_fields = [
            "origin_code", "origin_name", "origin_country",
            "destination_code", "destination_name", "destination_country",
            "container_type", "weight_tons", "volume_cbm",
            "shipment_date_normalized"
        ]
        
        for field in normalized_fields:
            if field in validated_data:
                print(f"  {field}: {validated_data[field]}")
        
        # Show recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            print(f"\nRecommendations:")
            for rec in recommendations:
                print(f"  [{rec['priority']}] {rec['type']}: {rec['message']}")
    
    else:
        print(f"✗ Validation failed: {result.get('error')}")

def run_comprehensive_tests():
    """Run all validation tests"""
    print("🧪 COMPREHENSIVE VALIDATION AGENT TESTS")
    print("=" * 50)
    
    try:
        test_validation_agent()
        test_port_validation()
        test_container_validation()
        test_weight_volume_validation()
        test_date_validation()
        test_business_logic_validation()
        test_validation_summary()
        test_integration_with_extraction()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

# =====================================================
#                 🚀 Main Execution
# =====================================================

if __name__ == "__main__":
    # Run individual test or comprehensive tests
    import sys
    
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        
        test_functions = {
            "basic": test_validation_agent,
            "ports": test_port_validation,
            "containers": test_container_validation,
            "weights": test_weight_volume_validation,
            "dates": test_date_validation,
            "business": test_business_logic_validation,
            "summary": test_validation_summary,
            "integration": test_integration_with_extraction,
            "all": run_comprehensive_tests
        }
        
        if test_name in test_functions:
            test_functions[test_name]()
        else:
            print(f"Available tests: {list(test_functions.keys())}")
    else:
        # Default to comprehensive tests
        run_comprehensive_tests()
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