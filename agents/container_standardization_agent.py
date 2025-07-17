"""Container type standardization agent for logistics processing"""

import os
import sys
from typing import Dict, Any, List, Optional
import re
import json

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_agent import BaseAgent

class ContainerStandardizationAgent(BaseAgent):
    """Agent for standardizing container type descriptions using LLM and comprehensive fallback logic"""

    def __init__(self):
        super().__init__("container_standardization_agent")
        
        # Supported container types
        self.supported_types = ["20DC", "40DC", "20RF", "40RF", "40HC", "20TK"]
        
        # Default container type for fallback cases
        self.default_container = "40DC"  # Most common container type
        
        # Rate fallback mapping for pricing
        self.rate_fallback_mapping = {
            "40RF": "40DC",
            "40RH": "40DC",
            "20RE": "20DC",
            "20TK": "20DC",
            "40HC": "40DC",
        }
        
        # Confidence threshold
        self.confidence_threshold = 45

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize container type descriptions.
        
        Expected input:
        - container_description: Single container description (string)
        - container_descriptions: Multiple descriptions (list)
        - container_type: Alternative key for single description
        """
        
        # Handle single container description
        if "container_description" in input_data:
            description = input_data["container_description"]
            return self._standardize_single_container(description)
        
        # Handle multiple container descriptions
        elif "container_descriptions" in input_data:
            descriptions = input_data["container_descriptions"]
            if not isinstance(descriptions, list):
                return {"error": "container_descriptions must be a list"}
            
            results = []
            for desc in descriptions:
                result = self._standardize_single_container(desc)
                results.append(result)
            return {"results": results, "total_processed": len(descriptions)}
        
        # Handle alternative key
        elif "container_type" in input_data:
            description = input_data["container_type"]
            return self._standardize_single_container(description)
        
        else:
            return {"error": "No container_description, container_descriptions, or container_type provided"}

    def _standardize_single_container(self, description: str) -> Dict[str, Any]:
        """Standardize a single container description using LLM first, then fallback"""
        
        if not description or not isinstance(description, str):
            return self._create_fallback_result(description, "Invalid container description")
        
        # Try LLM standardization first
        if self.client:
            try:
                llm_result = self._llm_standardization(description)
                if llm_result.get("success") and llm_result.get("confidence", 0) >= self.confidence_threshold:
                    return llm_result
                else:
                    self.logger.info(f"LLM result below threshold, using comprehensive fallback")
            except Exception as e:
                self.logger.warning(f"LLM standardization failed: {e}, using fallback")
        
        # Use comprehensive fallback logic
        return self._comprehensive_standardization(description)

    def _llm_standardization(self, description: str) -> Dict[str, Any]:
        """Use LLM for container standardization with function calling"""
        try:
            function_schema = {
                "name": "standardize_container",
                "description": "Standardize container type description to supported format",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "standard_type": {
                            "type": "string",
                            "enum": self.supported_types,
                            "description": "Standardized container type"
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 100.0,
                            "description": "Confidence score (0-100)"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Explanation for standardization decision"
                        },
                        "detected_size": {
                            "type": "string",
                            "enum": ["20ft", "40ft", "unknown"],
                            "description": "Detected container size"
                        },
                        "detected_type": {
                            "type": "string",
                            "enum": ["dry", "reefer", "high_cube", "tank", "unknown"],
                            "description": "Detected container type"
                        }
                    },
                    "required": ["standard_type", "confidence", "reasoning", "detected_size", "detected_type"]
                }
            }

            prompt = f"""
You are an expert in container standardization for logistics. Standardize this container description to one of the supported types.

SUPPORTED TYPES:
- 20DC: 20-foot dry container (standard)
- 40DC: 40-foot dry container (standard)
- 20RF: 20-foot refrigerated container
- 40RF: 40-foot refrigerated container
- 40HC: 40-foot high cube container
- 20TK: 20-foot tank container

CONTAINER DESCRIPTION: "{description}"

Analyze the description and determine:
1. Container size (20ft or 40ft)
2. Container type (dry, reefer, high cube, tank)
3. Best matching standard type
4. Confidence level (0-100)
5. Reasoning for your decision

Consider common variations:
- GP/DV = Dry Container (DC)
- RF/RE/RH = Reefer
- HC/HQ = High Cube
- TK = Tank
- TEU = 20ft, FEU = 40ft
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
                max_tokens=300
            )

            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if not tool_calls:
                raise Exception("No tool_calls in LLM response")

            tool_args = tool_calls[0].function.arguments
            if isinstance(tool_args, str):
                tool_args = json.loads(tool_args)

            result = dict(tool_args)
            
            # Add metadata
            result["original_input"] = description
            result["standardization_method"] = "llm_function_call"
            result["success"] = True
            result["fallback_used"] = False
            
            # Add rate fallback
            standard_type = result.get("standard_type")
            result["rate_fallback_type"] = self.rate_fallback_mapping.get(standard_type, standard_type)
            
            return result

        except Exception as e:
            raise Exception(f"LLM standardization failed: {str(e)}")

    def _comprehensive_standardization(self, description: str) -> Dict[str, Any]:
        """Comprehensive fallback standardization using the original logic"""
        
        # Clean and validate input
        input_data = self._clean_and_normalize_input(description)
        if not input_data["valid"]:
            return self._create_fallback_result(description, "Invalid input")
        
        cleaned_text = input_data["cleaned"]
        
        # Run all detection methods
        size_data = self._detect_container_size(cleaned_text)
        type_data = self._detect_container_type(cleaned_text)
        exact_data = self._check_exact_phrases(cleaned_text)
        special_data = self._handle_special_cases(cleaned_text)
        
        # Calculate scores
        score_data = self._calculate_container_scores(size_data, type_data, exact_data, special_data)
        
        # Calculate confidence
        confidence_data = self._calculate_confidence(score_data["scores"], score_data["matched_terms"], cleaned_text)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(confidence_data["confidence"], score_data["best_match"], score_data["scores"])
        
        # Return standardized result
        return {
            "standard_type": score_data["best_match"] if confidence_data["success"] else self.default_container,
            "confidence": confidence_data["confidence"],
            "matched_terms": score_data["matched_terms"][score_data["best_match"]],
            "suggestions": suggestions,
            "success": confidence_data["success"],
            "original_input": description,
            "cleaned_input": cleaned_text,
            "all_scores": {k: round(v, 1) for k, v in score_data["scores"].items()},
            "standardization_method": "comprehensive_fallback",
            "fallback_used": not confidence_data["success"],
            "rate_fallback_type": self.rate_fallback_mapping.get(
                score_data["best_match"] if confidence_data["success"] else self.default_container,
                score_data["best_match"] if confidence_data["success"] else self.default_container
            ),
            "detection_details": {
                "size_detected": size_data["detected_size"],
                "type_detected": type_data["detected_type"],
                "has_exact_match": exact_data["has_exact_match"],
                "is_special_case": special_data["is_special_case"]
            }
        }

    def _create_fallback_result(self, original_input: str, error_msg: str) -> Dict[str, Any]:
        """Create fallback result when input is invalid"""
        return {
            "standard_type": self.default_container,
            "confidence": 30.0,
            "success": False,
            "error": error_msg,
            "original_input": original_input,
            "fallback_used": True,
            "standardization_method": "default_fallback",
            "rate_fallback_type": self.default_container,
            "suggestions": self.supported_types
        }

    def _clean_and_normalize_input(self, user_input: str) -> Dict[str, str]:
        """Clean and normalize container input for processing"""
        if not user_input or not isinstance(user_input, str):
            return {"original": "", "cleaned": "", "valid": False}
        
        original = user_input.strip()
        cleaned = user_input.strip().upper()
        cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return {"original": original, "cleaned": cleaned, "valid": True}

    def _detect_container_size(self, text: str) -> Dict[str, Any]:
        """Detect container size from text"""
        size_patterns = {
            "20ft": [
                r'\b20\s*(?:FT|FOOT|FEET|GP|DC|DV)\b',
                r'\b20\s*(?:FOOT|FEET)\b',
                r'\bTWENTY\s*(?:FOOT|FEET|FT)\b',
                r'\bTEU\b'
            ],
            "40ft": [
                r'\b40\s*(?:FT|FOOT|FEET|GP|DC|DV|HC|HQ)\b',
                r'\b40\s*(?:FOOT|FEET)\b',
                r'\bFORTY\s*(?:FOOT|FEET|FT)\b',
                r'\bFEU\b'
            ]
        }
        
        detected_size = "unknown"
        size_score = 0
        matched_patterns = []
        
        for size, patterns in size_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    detected_size = size
                    size_score += 10
                    matched_patterns.append(pattern)
        
        return {
            "detected_size": detected_size,
            "size_score": size_score,
            "matched_patterns": matched_patterns
        }

    def _detect_container_type(self, text: str) -> Dict[str, Any]:
        """Detect container type from text"""
        type_patterns = {
            "dry": [
                r'\b(?:DRY|DC|DV|GP|GENERAL)\b',
                r'\bSTANDARD\b',
                r'\bCONTAINER\b'
            ],
            "reefer": [
                r'\b(?:REEFER|RF|RE|RH|REFRIGERAT|REFRIG|COOL|COLD|FROZEN)\b',
                r'\bTEMPERATURE\s*CONTROL\b'
            ],
            "high_cube": [
                r'\b(?:HIGH\s*CUBE|HC|HQ|CUBE)\b',
                r'\bHIGH\b.*\bCUBE\b'
            ],
            "tank": [
                r'\b(?:TANK|TK|LIQUID|BULK)\b',
                r'\bTANK\s*CONTAINER\b'
            ]
        }
        
        detected_type = "unknown"
        type_score = 0
        matched_patterns = []
        
        for container_type, patterns in type_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    detected_type = container_type
                    type_score += 10
                    matched_patterns.append(pattern)
        
        return {
            "detected_type": detected_type,
            "type_score": type_score,
            "matched_patterns": matched_patterns
        }

    def _check_exact_phrases(self, text: str) -> Dict[str, Any]:
        """Check for exact container type phrases"""
        exact_mappings = {
            "20DC": [r'\b20DC\b', r'\b20\s*DC\b', r'\b20GP\b', r'\b20\s*GP\b'],
            "40DC": [r'\b40DC\b', r'\b40\s*DC\b', r'\b40GP\b', r'\b40\s*GP\b'],
            "20RF": [r'\b20RF\b', r'\b20\s*RF\b', r'\b20RE\b', r'\b20\s*RE\b'],
            "40RF": [r'\b40RF\b', r'\b40\s*RF\b', r'\b40RH\b', r'\b40\s*RH\b'],
            "40HC": [r'\b40HC\b', r'\b40\s*HC\b', r'\b40HQ\b', r'\b40\s*HQ\b'],
            "20TK": [r'\b20TK\b', r'\b20\s*TK\b']
        }
        
        exact_match = None
        has_exact_match = False
        
        for container_type, patterns in exact_mappings.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    exact_match = container_type
                    has_exact_match = True
                    break
            if has_exact_match:
                break
        
        return {
            "exact_match": exact_match,
            "has_exact_match": has_exact_match
        }

    def _handle_special_cases(self, text: str) -> Dict[str, Any]:
        """Handle special cases and edge conditions"""
        special_cases = {
            "20DC": [
                r'\bTWENTY\s*FOOT\s*DRY\b',
                r'\bTEU\s*DRY\b',
                r'\b20\s*FOOT\s*STANDARD\b'
            ],
            "40DC": [
                r'\bFORTY\s*FOOT\s*DRY\b',
                r'\bFEU\s*DRY\b',
                r'\b40\s*FOOT\s*STANDARD\b'
            ],
            "20RF": [
                r'\bTWENTY\s*FOOT\s*REEFER\b',
                r'\bTEU\s*REEFER\b',
                r'\b20\s*FOOT\s*REFRIGERAT\b'
            ],
            "40RF": [
                r'\bFORTY\s*FOOT\s*REEFER\b',
                r'\bFEU\s*REEFER\b',
                r'\b40\s*FOOT\s*REFRIGERAT\b'
            ],
            "40HC": [
                r'\bFORTY\s*FOOT\s*HIGH\s*CUBE\b',
                r'\bFEU\s*HIGH\s*CUBE\b',
                r'\b40\s*FOOT\s*CUBE\b'
            ],
            "20TK": [
                r'\bTWENTY\s*FOOT\s*TANK\b',
                r'\bTEU\s*TANK\b',
                r'\b20\s*FOOT\s*LIQUID\b'
            ]
        }
        
        special_match = None
        is_special_case = False
        
        for container_type, patterns in special_cases.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    special_match = container_type
                    is_special_case = True
                    break
            if is_special_case:
                break
        
        return {
            "special_match": special_match,
            "is_special_case": is_special_case
        }

    def _calculate_container_scores(self, size_data: Dict, type_data: Dict, exact_data: Dict, special_data: Dict) -> Dict[str, Any]:
        """Calculate scores for each container type"""
        scores = {container_type: 0 for container_type in self.supported_types}
        matched_terms = {container_type: [] for container_type in self.supported_types}
        
        # Exact match gets highest priority
        if exact_data["has_exact_match"]:
            exact_type = exact_data["exact_match"]
            scores[exact_type] += 100
            matched_terms[exact_type].append("exact_match")
        
        # Special case match gets high priority
        if special_data["is_special_case"]:
            special_type = special_data["special_match"]
            scores[special_type] += 80
            matched_terms[special_type].append("special_case")
        
        # Size-based scoring
        detected_size = size_data["detected_size"]
        if detected_size == "20ft":
            for container_type in ["20DC", "20RF", "20TK"]:
                scores[container_type] += 30
                matched_terms[container_type].extend(size_data["matched_patterns"])
        elif detected_size == "40ft":
            for container_type in ["40DC", "40RF", "40HC"]:
                scores[container_type] += 30
                matched_terms[container_type].extend(size_data["matched_patterns"])
        
        # Type-based scoring
        detected_type = type_data["detected_type"]
        type_mapping = {
            "dry": ["20DC", "40DC"],
            "reefer": ["20RF", "40RF"],
            "high_cube": ["40HC"],
            "tank": ["20TK"]
        }
        
        if detected_type in type_mapping:
            for container_type in type_mapping[detected_type]:
                scores[container_type] += 40
                matched_terms[container_type].extend(type_data["matched_patterns"])
        
        # Find best match
        best_match = max(scores, key=scores.get)
        
        return {
            "scores": scores,
            "matched_terms": matched_terms,
            "best_match": best_match
        }

    def _calculate_confidence(self, scores: Dict[str, float], matched_terms: Dict[str, List], text: str) -> Dict[str, Any]:
        """Calculate confidence level for the standardization"""
        max_score = max(scores.values())
        second_max = sorted(scores.values(), reverse=True)[1] if len(scores) > 1 else 0
        
        # Base confidence from score
        base_confidence = min(max_score, 100)
        
        # Adjust for score gap (higher gap = higher confidence)
        score_gap = max_score - second_max
        gap_bonus = min(score_gap * 0.5, 20)
        
        # Adjust for number of matched terms
        best_container = max(scores, key=scores.get)
        num_matches = len(matched_terms[best_container])
        match_bonus = min(num_matches * 5, 15)
        
        # Adjust for text length (longer text might be more ambiguous)
        text_length_penalty = max(0, (len(text.split()) - 5) * 2)
        
        # Calculate final confidence
        confidence = base_confidence + gap_bonus + match_bonus - text_length_penalty
        confidence = max(0, min(100, confidence))
        
        # Determine success based on confidence threshold
        success = confidence >= self.confidence_threshold
        
        return {
            "confidence": confidence,
            "success": success,
            "base_confidence": base_confidence,
            "gap_bonus": gap_bonus,
            "match_bonus": match_bonus,
            "text_length_penalty": text_length_penalty
        }

    def _generate_suggestions(self, confidence: float, best_match: str, scores: Dict[str, float]) -> List[str]:
        """Generate suggestions based on confidence and scores"""
        if confidence >= 80:
            return [best_match]
        elif confidence >= 60:
            # Return top 2 suggestions
            sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return [item[0] for item in sorted_types[:2]]
        elif confidence >= 40:
            # Return top 3 suggestions
            sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return [item[0] for item in sorted_types[:3]]
        else:
            # Return all supported types as suggestions
            return self.supported_types

    def get_supported_types(self) -> List[str]:
        """Get list of supported container types"""
        return self.supported_types.copy()

    def get_rate_fallback_mapping(self) -> Dict[str, str]:
        """Get rate fallback mapping for pricing"""
        return self.rate_fallback_mapping.copy()

    def validate_container_type(self, container_type: str) -> Dict[str, Any]:
        """Validate if a container type is supported"""
        if not container_type or not isinstance(container_type, str):
            return {"valid": False, "error": "Invalid container type"}
        
        cleaned_type = container_type.strip().upper()
        is_valid = cleaned_type in self.supported_types
        
        return {
            "valid": is_valid,
            "original_input": container_type,
            "cleaned_input": cleaned_type,
            "supported_types": self.supported_types,
            "rate_fallback": self.rate_fallback_mapping.get(cleaned_type, cleaned_type) if is_valid else None
        }

# =====================================================
#                 🔁 Test Harness
# =====================================================
def test_container_standardization_agent():
    """Test container standardization with BaseAgent pattern"""
    print("=== Testing Container Standardization Agent (Updated) ===")
    
    agent = ContainerStandardizationAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}, Has LLM: {bool(agent.client)}")
    
    test_cases = [
        {
            "name": "Standard 20GP",
            "input": "20GP",
            "expected": "20DC"
        },
        {
            "name": "40 foot reefer",
            "input": "40 foot reefer",
            "expected": "40RF"
        },
        {
            "name": "High cube container",
            "input": "high cube",
            "expected": "40HC"
        },
        {
            "name": "Tank container",
            "input": "tank container",
            "expected": "20TK"
        },
        {
            "name": "TEU dry",
            "input": "TEU dry",
            "expected": "20DC"
        },
        {
            "name": "FEU standard",
            "input": "FEU standard",
            "expected": "40DC"
        },
        {
            "name": "20RF exact",
            "input": "20RF",
            "expected": "20RF"
        },
        {
            "name": "40HC exact",
            "input": "40HC",
            "expected": "40HC"
        },
        {
            "name": "Refrigerated 40ft",
            "input": "refrigerated 40ft",
            "expected": "40RF"
        },
        {
            "name": "Invalid input",
            "input": "invalid container",
            "expected": "40DC"  # Should default
        }
    ]
    
    results = {"correct": 0, "total": len(test_cases)}
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Input: '{test_case['input']}'")
        print(f"Expected: {test_case['expected']}")
        
        result = agent.run({"container_description": test_case["input"]})
        
        if result.get("status") == "success":
            standard_type = result.get("standard_type")
            confidence = result.get("confidence", 0)
            method = result.get("standardization_method", "unknown")
            success = result.get("success", False)
            
            print(f"✓ Standard Type: {standard_type}")
            print(f"✓ Confidence: {confidence:.1f}%")
            print(f"✓ Method: {method}")
            print(f"✓ Success: {success}")
            
            if standard_type == test_case["expected"]:
                print("✅ CORRECT")
                results["correct"] += 1
            else:
                print("❌ INCORRECT")
        else:
            print(f"✗ Error: {result.get('error')}")
    
    accuracy = results["correct"] / results["total"] * 100
    print(f"\n📊 Accuracy: {results['correct']}/{results['total']} ({accuracy:.1f}%)")

def test_batch_processing():
    """Test batch processing of multiple container descriptions"""
    print("\n=== Testing Batch Processing ===")
    
    agent = ContainerStandardizationAgent()
    agent.load_context()
    
    descriptions = [
        "20GP", "40HC", "reefer 40ft", "tank", "high cube",
        "TEU", "FEU", "20RF", "40DC", "standard container"
    ]
    
    print(f"Processing {len(descriptions)} container descriptions...")
    
    result = agent.run({"container_descriptions": descriptions})
    
    if result.get("status") == "success":
        results = result.get("results", [])
        total_processed = result.get("total_processed", 0)
        
        print(f"✓ Total processed: {total_processed}")
        print("\n📊 Batch Results:")
        
        for i, (desc, res) in enumerate(zip(descriptions, results), 1):
            standard_type = res.get("standard_type", "Unknown")
            confidence = res.get("confidence", 0)
            method = res.get("standardization_method", "unknown")
            
            print(f"  {i:2d}. '{desc:15}' -> {standard_type} ({confidence:.1f}%, {method})")
    else:
        print(f"✗ Error: {result.get('error')}")

def test_llm_vs_fallback():
    """Test LLM vs fallback performance"""
    print("\n=== Testing LLM vs Fallback Performance ===")
    
    agent = ContainerStandardizationAgent()
    agent.load_context()
    
    if not agent.client:
        print("✗ Cannot compare - LLM client not available")
        return
    
    test_descriptions = [
        "20GP", "40 foot reefer", "high cube", "tank container",
        "TEU dry", "FEU standard", "refrigerated container"
    ]
    
    print("Description | LLM Result | Fallback Result | LLM Conf | FB Conf | Match")
    print("-" * 80)
    
    for desc in test_descriptions:
        # Test with LLM
        llm_result = agent.run({"container_description": desc})
        
        # Simulate fallback by temporarily disabling LLM
        original_client = agent.client
        agent.client = None
        fallback_result = agent.run({"container_description": desc})
        agent.client = original_client
        
        llm_type = llm_result.get("standard_type", "Error") if llm_result.get("status") == "success" else "Error"
        fallback_type = fallback_result.get("standard_type", "Error") if fallback_result.get("status") == "success" else "Error"
        
        llm_conf = llm_result.get("confidence", 0) if llm_result.get("status") == "success" else 0
        fb_conf = fallback_result.get("confidence", 0) if fallback_result.get("status") == "success" else 0
        
        match = "✓" if llm_type == fallback_type else "✗"
        
        print(f"{desc:11} | {llm_type:10} | {fallback_type:15} | {llm_conf:7.1f} | {fb_conf:6.1f} | {match}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Testing Edge Cases ===")
    
    agent = ContainerStandardizationAgent()
    agent.load_context()
    
    edge_cases = [
        {"name": "Empty string", "input": ""},
        {"name": "None input", "input": None},
        {"name": "Numbers only", "input": "12345"},
        {"name": "Special characters", "input": "@#$%^&*()"},
        {"name": "Very long description", "input": "This is a very long container description that contains many words but no clear container type information"},
        {"name": "Mixed case", "input": "TwEnTy FoOt ReEfEr"},
        {"name": "Multiple types", "input": "20GP 40HC reefer tank"},
        {"name": "Whitespace only", "input": "   "},
        {"name": "Foreign language", "input": "contenedor de veinte pies"},
        {"name": "Ambiguous", "input": "container"}
    ]
    
    for case in edge_cases:
        print(f"\n--- {case['name']}: '{case['input']}' ---")
        result = agent.run({"container_description": case["input"]})
        
        if result.get("status") == "success":
            standard_type = result.get("standard_type")
            confidence = result.get("confidence", 0)
            success = result.get("success", False)
            method = result.get("standardization_method", "unknown")
            
            print(f"✓ Standard Type: {standard_type}")
            print(f"✓ Confidence: {confidence:.1f}%")
            print(f"✓ Success: {success}")
            print(f"✓ Method: {method}")
            
            if not success:
                print(f"✓ Fallback used (as expected)")
        else:
            print(f"✓ Error handled: {result.get('error')}")

def test_validation_functionality():
    """Test container type validation functionality"""
    print("\n=== Testing Validation Functionality ===")
    
    agent = ContainerStandardizationAgent()
    agent.load_context()
    
    validation_tests = [
        {"input": "20DC", "should_be_valid": True},
        {"input": "40RF", "should_be_valid": True},
        {"input": "40HC", "should_be_valid": True},
        {"input": "20TK", "should_be_valid": True},
        {"input": "30DC", "should_be_valid": False},
        {"input": "40XX", "should_be_valid": False},
        {"input": "", "should_be_valid": False},
        {"input": None, "should_be_valid": False}
    ]
    
    print("Testing container type validation...")
    
    for test in validation_tests:
        validation_result = agent.validate_container_type(test["input"])
        is_valid = validation_result.get("valid", False)
        
        status = "✓" if is_valid == test["should_be_valid"] else "✗"
        print(f"{status} '{test['input']}' -> Valid: {is_valid} (Expected: {test['should_be_valid']})")

def test_supported_types():
    """Test supported types and rate fallback mapping"""
    print("\n=== Testing Supported Types and Rate Fallback ===")
    
    agent = ContainerStandardizationAgent()
    agent.load_context()
    
    supported_types = agent.get_supported_types()
    rate_mapping = agent.get_rate_fallback_mapping()
    
    print(f"✓ Supported Types: {supported_types}")
    print(f"✓ Rate Fallback Mapping:")
    
    for original, fallback in rate_mapping.items():
        print(f"  {original} -> {fallback}")
    
    # Test that all supported types have rate fallbacks
    print(f"\n✓ Rate fallback coverage:")
    for container_type in supported_types:
        fallback = rate_mapping.get(container_type, container_type)
        print(f"  {container_type} -> {fallback}")

def test_confidence_scoring():
    """Test confidence scoring mechanism"""
    print("\n=== Testing Confidence Scoring ===")
    
    agent = ContainerStandardizationAgent()
    agent.load_context()
    
    confidence_tests = [
        {"input": "20DC", "expected_high": True},  # Exact match
        {"input": "40 foot reefer", "expected_high": True},  # Clear description
        {"input": "container", "expected_high": False},  # Ambiguous
        {"input": "box", "expected_high": False},  # Unclear
        {"input": "20GP dry standard", "expected_high": True},  # Multiple indicators
    ]
    
    print("Testing confidence scoring...")
    
    for test in confidence_tests:
        result = agent.run({"container_description": test["input"]})
        
        if result.get("status") == "success":
            confidence = result.get("confidence", 0)
            is_high_confidence = confidence >= agent.confidence_threshold
            
            status = "✓" if is_high_confidence == test["expected_high"] else "✗"
            print(f"{status} '{test['input']}' -> Confidence: {confidence:.1f}% (Expected high: {test['expected_high']})")
        else:
            print(f"✗ Error for '{test['input']}': {result.get('error')}")

def test_detailed_analysis():
    """Test detailed analysis output"""
    print("\n=== Testing Detailed Analysis Output ===")
    
    agent = ContainerStandardizationAgent()
    agent.load_context()
    
    test_input = "40 foot high cube reefer container"
    
    print(f"Analyzing: '{test_input}'")
    result = agent.run({"container_description": test_input})
    
    if result.get("status") == "success":
        print(f"\n📊 Detailed Analysis:")
        print(f"✓ Standard Type: {result.get('standard_type')}")
        print(f"✓ Confidence: {result.get('confidence', 0):.1f}%")
        print(f"✓ Success: {result.get('success', False)}")
        print(f"✓ Method: {result.get('standardization_method', 'unknown')}")
        print(f"✓ Rate Fallback: {result.get('rate_fallback_type')}")
        
        # Show all scores if available
        all_scores = result.get("all_scores", {})
        if all_scores:
            print(f"✓ All Scores:")
            for container_type, score in sorted(all_scores.items(), key=lambda x: x[1], reverse=True):
                print(f"  {container_type}: {score}")
        
        # Show detection details if available
        detection_details = result.get("detection_details", {})
        if detection_details:
            print(f"✓ Detection Details:")
            for key, value in detection_details.items():
                print(f"  {key}: {value}")
        
        # Show matched terms if available
        matched_terms = result.get("matched_terms", [])
        if matched_terms:
            print(f"✓ Matched Terms: {matched_terms}")
        
        # Show suggestions if available
        suggestions = result.get("suggestions", [])
        if suggestions:
            print(f"✓ Suggestions: {suggestions}")
    else:
        print(f"✗ Error: {result.get('error')}")

def test_performance():
    """Test performance with multiple requests"""
    print("\n=== Testing Performance ===")
    
    agent = ContainerStandardizationAgent()
    agent.load_context()
    
    import time
    
    # Generate test data
    test_descriptions = [
        "20GP", "40HC", "reefer", "tank", "high cube",
        "TEU", "FEU", "20RF", "40DC", "standard",
        "dry container", "refrigerated", "cube", "liquid",
        "twenty foot", "forty foot", "GP", "HC"
    ] * 5  # 90 total tests
    
    print(f"Running performance test with {len(test_descriptions)} requests...")
    
    start_time = time.time()
    successful = 0
    failed = 0
    
    for desc in test_descriptions:
        result = agent.run({"container_description": desc})
        if result.get("status") == "success":
            successful += 1
        else:
            failed += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / len(test_descriptions) * 1000  # Convert to ms
    
    print(f"✓ Performance Results:")
    print(f"  Total time: {total_time:.2f}s")
    print(f"  Average per request: {avg_time:.2f}ms")
    print(f"  Successful: {successful}/{len(test_descriptions)}")
    print(f"  Failed: {failed}/{len(test_descriptions)}")
    print(f"  Success rate: {successful/len(test_descriptions)*100:.1f}%")

def run_comprehensive_tests():
    """Run all test suites"""
    print("🚀 Starting Comprehensive Container Standardization Tests")
    print("=" * 60)
    
    try:
        # Basic functionality tests
        test_container_standardization_agent()
        
        # Batch processing tests
        test_batch_processing()
        
        # LLM vs fallback comparison
        test_llm_vs_fallback()
        
        # Edge case tests
        test_edge_cases()
        
        # Validation functionality
        test_validation_functionality()
        
        # Supported types and mappings
        test_supported_types()
        
        # Confidence scoring
        test_confidence_scoring()
        
        # Detailed analysis
        test_detailed_analysis()
        
        # Performance tests
        test_performance()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

def quick_test():
    """Quick test with a few key scenarios"""
    print("=== Quick Container Standardization Test ===")
    
    agent = ContainerStandardizationAgent()
    agent.load_context()
    
    quick_tests = [
        "20GP",
        "40 foot reefer",
        "high cube",
        "tank container",
        "invalid input"
    ]
    
    for test in quick_tests:
        print(f"\n'{test}' ->", end=" ")
        result = agent.run({"container_description": test})
        
        if result.get("status") == "success":
            standard_type = result.get("standard_type")
            confidence = result.get("confidence", 0)
            print(f"{standard_type} ({confidence:.1f}%)")
        else:
            print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            quick_test()
        elif sys.argv[1] == "comprehensive":
            run_comprehensive_tests()
        else:
            print("Usage: python container_standardization_agent.py [quick|comprehensive]")
    else:
        # Run comprehensive tests by default
        run_comprehensive_tests()
