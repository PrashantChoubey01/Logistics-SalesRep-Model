"""Container type standardization agent for logistics processing"""

import os
import sys
from typing import Dict, Any, List, Optional
import re

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

class ContainerStandardizationAgent(BaseAgent):
    """Agent for standardizing container type descriptions using comprehensive logic"""

    def __init__(self):
        super().__init__("container_standardization_agent")
        
        # Supported container types (enhanced from your code)
        self.supported_types = ["20DC", "40DC", "20RF", "40RF", "40HC", "20TK"]
        
        # Default container type for fallback cases
        self.default_container = "40DC"  # Most common container type
        
        # Rate fallback mapping for pricing
        self.rate_fallback_mapping = {
            "40RF": "40DC",  # 40RF falls back to 40DC rates
            "40RH": "40DC",  # 40RH falls back to 40DC rates
            "20RE": "20DC",  # 20RE falls back to 20DC rates
            "20TK": "20DC",  # 20TK falls back to 20DC rates
            "40HC": "40DC",  # 40HC falls back to 40DC rates (if HC rates not available)
        }
        
        # Confidence threshold
        self.confidence_threshold = 45

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize container type descriptions
        
        Input formats:
        - {"container_description": "20 footer"}
        - {"container_descriptions": ["20 footer", "40 reefer"]}
        - {"container_type": "20ft dry"}  # Alternative key
        """
        
        # Handle single container description
        if "container_description" in input_data:
            description = input_data["container_description"]
            return self._standardize_single_container(description)
        
        # Handle multiple container descriptions
        elif "container_descriptions" in input_data:
            descriptions = input_data["container_descriptions"]
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
        """Standardize a single container description using your comprehensive logic"""
        
        if not description or not isinstance(description, str):
            return {
                "standard_type": self.default_container,
                "confidence": 30.0,  # Low confidence for fallback
                "success": False,
                "error": "Invalid container description - using default",
                "original_input": description,
                "fallback_used": True
            }
        
        # Use your comprehensive standardization logic
        result = self._convert_container_description(description)
        
        # If conversion failed, use default
        if not result.get("success") or not result.get("standard_type"):
            result["standard_type"] = self.default_container
            result["confidence"] = 30.0
            result["success"] = False
            result["fallback_used"] = True
            result["error"] = "Could not determine container type - using default"
        
        # Add rate fallback information
        if result.get("standard_type") and result["standard_type"] in self.rate_fallback_mapping:
            result["rate_fallback_type"] = self.rate_fallback_mapping[result["standard_type"]]
        else:
            result["rate_fallback_type"] = result.get("standard_type")
        
        # Add agent metadata
        result["agent_method"] = "comprehensive_analysis"
        result["supported_types"] = self.supported_types
        
        return result

    def _convert_container_description(self, user_input: str) -> Dict[str, Any]:
        """
        Main conversion logic adapted from your comprehensive system
        """
        
        # Step 1: Clean and validate input
        input_data = self._clean_and_normalize_input(user_input)
        if not input_data["valid"]:
            return {
                "standard_type": None,
                "confidence": 0,
                "matched_terms": [],
                "suggestions": ["20DC", "40DC", "20RF", "40RF", "40HC", "20TK"],
                "success": False,
                "error": "Invalid input",
                "original_input": user_input
            }
        
        cleaned_text = input_data["cleaned"]
        
        # Step 2: Run all detection methods
        size_data = self._detect_container_size(cleaned_text)
        type_data = self._detect_container_type(cleaned_text)
        exact_data = self._check_exact_phrases(cleaned_text)
        special_data = self._handle_special_cases(cleaned_text)
        
        # Step 3: Calculate scores
        score_data = self._calculate_container_scores(size_data, type_data, exact_data, special_data)
        
        # Step 4: Calculate confidence
        confidence_data = self._calculate_confidence(score_data["scores"], score_data["matched_terms"], cleaned_text)
        
        # Step 5: Generate suggestions
        suggestions = self._generate_suggestions(confidence_data["confidence"], score_data["best_match"], score_data["scores"])
        
        # Step 6: Return standardized result
        return {
            "standard_type": score_data["best_match"] if confidence_data["success"] else None,
            "confidence": confidence_data["confidence"],
            "matched_terms": score_data["matched_terms"][score_data["best_match"]],
            "suggestions": suggestions,
            "success": confidence_data["success"],
            "original_input": input_data["original"],
            "cleaned_input": cleaned_text,
            "all_scores": {k: round(v, 1) for k, v in score_data["scores"].items()},
            "method": "comprehensive_analysis",
            "detection_details": {
                "size_detected": size_data["detected_size"],
                "type_detected": type_data["detected_type"],
                "has_exact_match": exact_data["has_exact_match"],
                "is_special_case": special_data["is_special_case"]
            }
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

    def _detect_container_size(self, cleaned_text: str) -> Dict[str, Any]:
        """Detect if container is 20ft or 40ft based on text patterns"""
        
        # 20-foot indicators
        size_20_patterns = [
            r'\b20\b', r'\bTWENTY\b', r'\b20FT\b', r'\b20 FT\b', r'\b20FOOT\b', r'\b20 FOOT\b',
            r'\b20FEET\b', r'\b20 FEET\b', r'\b20\'\b', r'\b20"\b',
            r'\b20 FOOTER\b', r'\bTWENTY FOOTER\b', r'\b20FOOTER\b',
            r'\bSMALL\b', r'\bSHORT\b', r'\bSHORTER\b', r'\bCOMPACT\b', r'\bMINI\b', r'\bTEU\b'
        ]
        
        # 40-foot indicators
        size_40_patterns = [
            r'\b40\b', r'\bFORTY\b', r'\b40FT\b', r'\b40 FT\b', r'\b40FOOT\b', r'\b40 FOOT\b',
            r'\b40FEET\b', r'\b40 FEET\b', r'\b40\'\b', r'\b40"\b',
            r'\b40 FOOTER\b', r'\bFORTY FOOTER\b', r'\b40FOOTER\b',
            r'\bLARGE\b', r'\bBIG\b', r'\bLONG\b', r'\bLONGER\b', r'\bEXTENDED\b', r'\bFEU\b'
        ]
        
        size_20_matches = [pattern.strip(r'\b') for pattern in size_20_patterns if re.search(pattern, cleaned_text)]
        size_40_matches = [pattern.strip(r'\b') for pattern in size_40_patterns if re.search(pattern, cleaned_text)]
        
        return {
            "size_20_score": len(size_20_matches),
            "size_40_score": len(size_40_matches),
            "size_20_matches": size_20_matches,
            "size_40_matches": size_40_matches,
            "detected_size": "20ft" if len(size_20_matches) > len(size_40_matches)
                             else "40ft" if len(size_40_matches) > 0 else "unknown"
        }

    def _detect_container_type(self, cleaned_text: str) -> Dict[str, Any]:
        """Detect container type: dry, reefer, high cube, or tank"""
        
        # Dry container indicators
        dry_patterns = [
            r'\bDRY\b', r'\bSTANDARD\b', r'\bGENERAL\b', r'\bNORMAL\b', r'\bREGULAR\b',
            r'\bBASIC\b', r'\bCOMMON\b', r'\bTYPICAL\b', r'\bDC\b', r'\bDV\b', r'\bGP\b',
            r'\bCARGO\b', r'\bFREIGHT\b', r'\bSHIPPING\b', r'\bSTORAGE\b', r'\bGOODS\b'
        ]
        
        # Refrigerated container indicators
        reefer_patterns = [
            r'\bREEFER\b', r'\bREFRIGERAT\w*\b', r'\bCOLD\b', r'\bFROZEN\b', r'\bFREEZ\w*\b',
            r'\bCHILL\w*\b', r'\bICE\b', r'\bCOOL\w*\b', r'\bTEMP\w*\b', r'\bTHERMAL\b',
            r'\bCLIMATE\b', r'\bCONTROLLED\b', r'\bINSULAT\w*\b', r'\bRF\b', r'\bRE\b', r'\bRH\b',
            r'\bFOOD\b', r'\bPERISHABLE\b', r'\bFRESH\b', r'\bDAIRY\b', r'\bMEAT\b'
        ]
        
        # High cube indicators
        high_cube_patterns = [
            r'\bHIGH\b', r'\bCUBE\b', r'\bTALL\b', r'\bHEIGHT\b', r'\bELEVATED\b',
            r'\bEXTRA\b', r'\bEXTENDED\b', r'\bSUPER\b', r'\bHIGH CUBE\b', r'\bHI CUBE\b',
            r'\bHICUBE\b', r'\bHI-CUBE\b', r'\bHC\b', r'\bHQ\b', r'\bHI\b'
        ]
        
        # Tank container indicators
        tank_patterns = [
            r'\bTANK\b', r'\bTK\b', r'\bLIQUID\b', r'\bFLUID\b', r'\bCHEMICAL\b',
            r'\bOIL\b', r'\bGAS\b', r'\bFUEL\b', r'\bPETROL\b', r'\bDIESEL\b'
        ]
        
        # Check patterns
        dry_matches = [p.strip(r'\b') for p in dry_patterns if re.search(p, cleaned_text)]
        reefer_matches = [p.strip(r'\b') for p in reefer_patterns if re.search(p, cleaned_text)]
        hc_matches = [p.strip(r'\b') for p in high_cube_patterns if re.search(p, cleaned_text)]
        tank_matches = [p.strip(r'\b') for p in tank_patterns if re.search(p, cleaned_text)]
        
        return {
            "dry_score": len(dry_matches),
            "reefer_score": len(reefer_matches),
            "high_cube_score": len(hc_matches),
            "tank_score": len(tank_matches),
            "dry_matches": dry_matches,
            "reefer_matches": reefer_matches,
            "high_cube_matches": hc_matches,
            "tank_matches": tank_matches,
            "detected_type": "reefer" if len(reefer_matches) > 0
                             else "tank" if len(tank_matches) > 0
                             else "high_cube" if len(hc_matches) > 0
                             else "dry" if len(dry_matches) > 0
                             else "unknown"
        }

    def _check_exact_phrases(self, cleaned_text: str) -> Dict[str, Any]:
        """Check for exact container type phrases"""
        
        exact_phrases = {
            "20DC": [
                "20GP", "20DV", "20DC", "20 GP", "20 DV", "20 DC",
                "20 FOOT DRY", "TWENTY FOOT DRY", "20 DRY CONTAINER", "SMALL DRY",
                "20 STANDARD", "20 GENERAL PURPOSE", "20GP", "20DV", "20DC",
                "SMALL CONTAINER", "TEU CONTAINER"
            ],
            "40DC": [
                "40GP", "40DV", "40DC", "40 GP", "40 DV", "40 DC",
                "40 FOOT DRY", "FORTY FOOT DRY", "40 DRY CONTAINER", "LARGE DRY",
                "40 STANDARD", "40 GENERAL PURPOSE", "40GP", "40DV", "40DC",
                "BIG CONTAINER", "LARGE CONTAINER", "FEU CONTAINER"
            ],
            "20RF": [
                "20RF", "20RE", "20RH", "20 RF", "20 RE", "20 RH",
                "20 REEFER", "TWENTY REEFER", "20REEFER", "20 FT REEFER", "20FT REEFER",
                "20 REFRIGERATED", "20 COLD", "20 FROZEN", "SMALL REEFER",
                "20 FOOT COLD", "TWENTY FOOT REEFER"
            ],
            "40RF": [
                "40RF", "40RE", "40RH", "40 RF", "40 RE", "40 RH",
                "40 REEFER", "FORTY REEFER", "40REEFER", "40 FT REEFER", "40FT REEFER",
                "40 REFRIGERATED", "40 COLD", "40 FROZEN", "LARGE REEFER",
                "40 FOOT COLD", "FORTY FOOT REEFER", "BIG REEFER", "LARGE REFRIGERATED"
            ],
            "40HC": [
                "40HC", "40HQ", "40 HC", "40 HQ", "40 HIGH CUBE", "FORTY HIGH CUBE",
                "40 FT HIGH", "40FT HIGH", "40 FOOT HIGH", "FORTY FOOT HIGH",
                "40 HIGH CONTAINER", "LARGE HIGH CUBE", "BIG HIGH CUBE",
                "40 CUBE", "TALL CONTAINER", "HIGH CONTAINER"
            ],
            "20TK": [
                "20TK", "20 TK", "20 TANK", "TWENTY TANK", "20TANK", "20 FT TANK", "20FT TANK",
                "20 LIQUID", "SMALL TANK", "20 FOOT TANK"
            ]
        }
        
        exact_matches = {"20DC": [], "40DC": [], "20RF": [], "40RF": [], "40HC": [], "20TK": []}
        
        for container_type, phrases in exact_phrases.items():
            for phrase in phrases:
                if phrase in cleaned_text:
                    exact_matches[container_type].append(phrase)
        
        return {
            "exact_matches": exact_matches,
            "has_exact_match": any(len(matches) > 0 for matches in exact_matches.values()),
            "best_exact_match": max(exact_matches.keys(), key=lambda k: len(exact_matches[k]))
                                if any(len(matches) > 0 for matches in exact_matches.values()) else None
        }

    def _handle_special_cases(self, cleaned_text: str) -> Dict[str, Any]:
        """Handle special standalone terms and edge cases"""
        
        special_cases = {
            # Ambiguous terms
            "FOOTER": {"20DC": 30, "40DC": 30},
            "CONTAINER": {"20DC": 15, "40DC": 15, "20RF": 15, "40RF": 15, "40HC": 15, "20TK": 15},
            "BOX": {"20DC": 20, "40DC": 20},
            "UNIT": {"20DC": 15, "40DC": 15, "20RF": 15, "40RF": 15, "40HC": 15, "20TK": 15},
            
            # Size only
            "20": {"20DC": 60, "20RF": 20, "20TK": 20},
            "TWENTY": {"20DC": 60, "20RF": 20, "20TK": 20},
            "40": {"40DC": 50, "40RF": 30, "40HC": 50},
            "FORTY": {"40DC": 50, "40RF": 30, "40HC": 50},
            
            # Type only - Enhanced for 40RF support
            "REEFER": {"20RF": 60, "40RF": 70},  # Prefer 40RF slightly
            "REFRIGERATED": {"20RF": 60, "40RF": 70},
            "COLD": {"20RF": 60, "40RF": 70},
            "HIGH CUBE": {"40HC": 80},
            "HC": {"40HC": 80},
            "TALL": {"40HC": 80},
            "TANK": {"20TK": 80},
            "TK": {"20TK": 80},
            "DRY": {"20DC": 45, "40DC": 45},
            "STANDARD": {"20DC": 45, "40DC": 45},
            "GENERAL": {"20DC": 45, "40DC": 45},
            
            # Industry terms
            "TEU": {"20DC": 80},
            "FEU": {"40DC": 80},
            "RF": {"20RF": 65, "40RF": 75},  # Prefer 40RF
            "RE": {"20RF": 65, "40RF": 75},
            "RH": {"20RF": 65, "40RF": 75},
            "OPEN": {"20DC": 30, "40DC": 30},
            "FLAT": {"20DC": 30, "40DC": 30},
            "PLATFORM": {"20DC": 30, "40DC": 30}
        }
        
        matched_special_cases = {}
        special_scores = {"20DC": 0, "40DC": 0, "20RF": 0, "40RF": 0, "40HC": 0, "20TK": 0}
        
        text_stripped = cleaned_text.strip()
        
        # Check for exact special case matches
        if text_stripped in special_cases:
            matched_special_cases[text_stripped] = special_cases[text_stripped]
            for container_type, score in special_cases[text_stripped].items():
                special_scores[container_type] += score
        
        # Check for partial matches in longer text
        for special_term, scores in special_cases.items():
            if special_term in cleaned_text and special_term != text_stripped:
                matched_special_cases[special_term] = scores
                for container_type, score in scores.items():
                    special_scores[container_type] += score // 2
        
        return {
            "special_scores": special_scores,
            "matched_cases": matched_special_cases,
            "is_special_case": len(matched_special_cases) > 0
        }

    def _calculate_container_scores(self, size_data: Dict, type_data: Dict, exact_data: Dict, special_data: Dict) -> Dict[str, Any]:
        """Calculate final scores for each container type"""
        
        scores = {"20DC": 0, "40DC": 0, "20RF": 0, "40RF": 0, "40HC": 0, "20TK": 0}
        all_matched_terms = {"20DC": [], "40DC": [], "20RF": [], "40RF": [], "40HC": [], "20TK": []}
        
        # === SIZE SCORING ===
        if size_data["size_20_score"] > 0:
            scores["20DC"] += 40
            scores["20RF"] += 40
            scores["20TK"] += 40
            all_matched_terms["20DC"].extend([f"size:{term}" for term in size_data["size_20_matches"]])
            all_matched_terms["20RF"].extend([f"size:{term}" for term in size_data["size_20_matches"]])
            all_matched_terms["20TK"].extend([f"size:{term}" for term in size_data["size_20_matches"]])
        
        if size_data["size_40_score"] > 0:
            scores["40DC"] += 40
            scores["40RF"] += 40
            scores["40HC"] += 40
            all_matched_terms["40DC"].extend([f"size:{term}" for term in size_data["size_40_matches"]])
            all_matched_terms["40RF"].extend([f"size:{term}" for term in size_data["size_40_matches"]])
            all_matched_terms["40HC"].extend([f"size:{term}" for term in size_data["size_40_matches"]])
        
        # === TYPE SCORING ===
        if type_data["dry_score"] > 0:
            scores["20DC"] += 30
            scores["40DC"] += 30
            all_matched_terms["20DC"].extend([f"type:{term}" for term in type_data["dry_matches"]])
            all_matched_terms["40DC"].extend([f"type:{term}" for term in type_data["dry_matches"]])
        
        if type_data["reefer_score"] > 0:
            scores["20RF"] += 50
            scores["40RF"] += 50
            all_matched_terms["20RF"].extend([f"type:{term}" for term in type_data["reefer_matches"]])
            all_matched_terms["40RF"].extend([f"type:{term}" for term in type_data["reefer_matches"]])
        
        if type_data["high_cube_score"] > 0:
            scores["40HC"] += 50
            all_matched_terms["40HC"].extend([f"type:{term}" for term in type_data["high_cube_matches"]])
        
        if type_data["tank_score"] > 0:
            scores["20TK"] += 50
            all_matched_terms["20TK"].extend([f"type:{term}" for term in type_data["tank_matches"]])
        
        # === EXACT PHRASE SCORING ===
        for container_type, exact_matches in exact_data["exact_matches"].items():
            if exact_matches:
                scores[container_type] += 60
                all_matched_terms[container_type].extend([f"exact:{term}" for term in exact_matches])
        
        # === SPECIAL CASE SCORING ===
        for container_type, special_score in special_data["special_scores"].items():
            scores[container_type] += special_score
            if special_score > 0:
                all_matched_terms[container_type].extend([f"special:{case}" for case in special_data["matched_cases"].keys()])
        
        # === ENHANCED COMBINATION LOGIC ===
        
        # If size is specified but no type, boost dry containers
        if (size_data["size_20_score"] > 0 or size_data["size_40_score"] > 0) and \
           type_data["reefer_score"] == 0 and type_data["high_cube_score"] == 0 and type_data["tank_score"] == 0:
            if size_data["size_20_score"] > 0:
                scores["20DC"] += 20
            if size_data["size_40_score"] > 0:
                scores["40DC"] += 20
        
        # If reefer is mentioned without size, prefer 40RF (industry standard)
        if type_data["reefer_score"] > 0 and size_data["size_20_score"] == 0 and size_data["size_40_score"] == 0:
            scores["40RF"] += 15  # Prefer 40RF when no size specified
            scores["20RF"] += 10
        
        # High cube is always 40ft
        if type_data["high_cube_score"] > 0:
            scores["40HC"] += 30
            if type_data["high_cube_score"] >= 2:
                scores["40DC"] = max(0, scores["40DC"] - 20)
        
        # Tank containers default to 20ft unless 40ft is explicitly mentioned
        if type_data["tank_score"] > 0 and size_data["size_40_score"] == 0:
            scores["20TK"] += 20
        
        # Remove duplicates from matched terms
        for container_type in all_matched_terms:
            all_matched_terms[container_type] = list(set(all_matched_terms[container_type]))
        
        return {
            "scores": scores,
            "matched_terms": all_matched_terms,
            "best_match": max(scores.keys(), key=lambda k: scores[k]),
            "best_score": max(scores.values())
        }

    def _calculate_confidence(self, scores: Dict[str, float], matched_terms: Dict[str, List], cleaned_text: str) -> Dict[str, Any]:
        """Calculate confidence score and adjust based on various factors"""
        
        best_container = max(scores.keys(), key=lambda k: scores[k])
        best_score = scores[best_container]
        best_matches = matched_terms[best_container]
        
        # Start with base score
        confidence = best_score
        
        # === CONFIDENCE ADJUSTMENTS ===
        
        # Boost confidence for multiple matching terms
        term_count = len(best_matches)
        if term_count >= 3:
            confidence += 15
        elif term_count >= 2:
            confidence += 10
        
        # Reduce confidence for very short inputs
        word_count = len(cleaned_text.split())
        if word_count == 1 and len(cleaned_text) <= 4:
            confidence = max(0, confidence - 10)
        
        # Boost confidence for longer, more descriptive inputs
        if word_count >= 3:
            confidence += 5
        
        # Boost confidence for exact matches
        exact_match_count = len([term for term in best_matches if term.startswith("exact:")])
        if exact_match_count > 0:
            confidence += 10
        
        # Reduce confidence if scores are very close (ambiguous)
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) >= 2:
            score_gap = sorted_scores[0] - sorted_scores[1]
            if score_gap < 10:
                confidence -= 15
            elif score_gap < 20:
                confidence -= 10
        
        # Cap confidence at 100
        confidence = min(100, confidence)
        
        # Determine success threshold
        success_threshold = self.confidence_threshold
        success = confidence >= success_threshold
        
        return {
            "confidence": round(confidence, 1),
            "success": success,
            "success_threshold": success_threshold,
            "term_count": term_count,
            "word_count": word_count,
            "exact_matches": exact_match_count,
            "score_gap": sorted_scores[0] - sorted_scores[1] if len(sorted_scores) >= 2 else 0
        }

    def _generate_suggestions(self, confidence: float, best_match: str, scores: Dict[str, float]) -> List[str]:
        """Generate intelligent suggestions based on confidence and scores"""
        
        if confidence < 30:
            # Low confidence - show all options
            return ["20DC", "40DC", "20RF", "40RF", "40HC", "20TK"]
        elif confidence < 60:
            # Medium confidence - show best match plus logical alternatives
            suggestions = [best_match]
            
            # Enhanced alternatives mapping
            alternatives = {
                "20DC": ["20RF", "40DC", "20TK"],
                "40DC": ["40HC", "40RF", "20DC"],
                "20RF": ["20DC", "40RF"],
                "40RF": ["40DC", "40HC", "20RF"],
                "40HC": ["40DC", "40RF"],
                "20TK": ["20DC"]
            }
            
            if best_match in alternatives:
                suggestions.extend(alternatives[best_match])
            
            return suggestions[:4]  # Limit to 4 suggestions
        else:
            # High confidence - just return best match
            return [best_match]

# =====================================================
#                 🔁 Enhanced Test Harness
# =====================================================

def test_container_standardization_agent():
    """Comprehensive test suite for container standardization"""
    print("=== Testing Enhanced Container Standardization Agent ===")
    
    agent = ContainerStandardizationAgent()
    
    # Enhanced test cases covering all scenarios
    test_cases = [
        # === EXACT MATCHES ===
        {"input": "20GP", "expected": "20DC", "category": "Exact Code"},
        {"input": "40GP", "expected": "40DC", "category": "Exact Code"},
        {"input": "40HC", "expected": "40HC", "category": "Exact Code"},
        {"input": "20RF", "expected": "20RF", "category": "Exact Code"},
        {"input": "40RF", "expected": "40RF", "category": "Exact Code"},
        {"input": "20TK", "expected": "20TK", "category": "Exact Code"},
        
        # === DESCRIPTIVE PHRASES ===
        {"input": "20 foot dry container", "expected": "20DC", "category": "Descriptive"},
        {"input": "40 foot dry container", "expected": "40DC", "category": "Descriptive"},
        {"input": "40 foot high cube", "expected": "40HC", "category": "Descriptive"},
        {"input": "20 foot reefer", "expected": "20RF", "category": "Descriptive"},
        {"input": "40 foot reefer", "expected": "40RF", "category": "Descriptive"},
        {"input": "20 foot tank", "expected": "20TK", "category": "Descriptive"},
        
        # === INDUSTRY VARIATIONS ===
        {"input": "TEU", "expected": "20DC", "category": "Industry Term"},
        {"input": "FEU", "expected": "40DC", "category": "Industry Term"},
        {"input": "20DV", "expected": "20DC", "category": "Industry Code"},
        {"input": "40DV", "expected": "40DC", "category": "Industry Code"},
        {"input": "40HQ", "expected": "40HC", "category": "Industry Code"},
        
        # === AMBIGUOUS CASES ===
        {"input": "container", "expected": "40DC", "category": "Ambiguous"},  # Should default to most common
        {"input": "20", "expected": "20DC", "category": "Size Only"},
        {"input": "40", "expected": "40DC", "category": "Size Only"},
        {"input": "reefer", "expected": "40RF", "category": "Type Only"},  # Should prefer 40RF
        {"input": "refrigerated", "expected": "40RF", "category": "Type Only"},
        {"input": "high cube", "expected": "40HC", "category": "Type Only"},
        {"input": "tank", "expected": "20TK", "category": "Type Only"},
        
        # === COMPLEX DESCRIPTIONS ===
        {"input": "forty foot refrigerated container", "expected": "40RF", "category": "Complex"},
        {"input": "20ft dry box", "expected": "20DC", "category": "Complex"},
        {"input": "large high cube container", "expected": "40HC", "category": "Complex"},
        {"input": "small reefer unit", "expected": "20RF", "category": "Complex"},
        {"input": "big tank container", "expected": "20TK", "category": "Complex"},  # Tank defaults to 20 unless specified
        
        # === EDGE CASES ===
        {"input": "", "expected": "40DC", "category": "Empty"},  # Should default
        {"input": "xyz", "expected": "40DC", "category": "Invalid"},  # Should default
        {"input": "CONTAINER BOX UNIT", "expected": "40DC", "category": "Generic Terms"},
        {"input": "20 FOOT COLD STORAGE", "expected": "20RF", "category": "Alternative Terms"},
        {"input": "FORTY FOOT TALL CONTAINER", "expected": "40HC", "category": "Alternative Terms"},
        
        # === REAL-WORLD VARIATIONS ===
        {"input": "20' dry", "expected": "20DC", "category": "Real World"},
        {"input": "40' HC", "expected": "40HC", "category": "Real World"},
        {"input": "20ft reefer container", "expected": "20RF", "category": "Real World"},
        {"input": "40 foot standard", "expected": "40DC", "category": "Real World"},
        {"input": "large container", "expected": "40DC", "category": "Real World"},
        {"input": "small container", "expected": "20DC", "category": "Real World"},
    ]
    
    # Load context
    context_loaded = agent.load_context()
    print(f"✓ Context loaded: {context_loaded}")
    print(f"✓ Confidence threshold: {agent.confidence_threshold}")
    print(f"✓ Default container: {agent.default_container}")
    print(f"✓ Supported types: {agent.supported_types}")
    
    # Run tests
    results = {"correct": 0, "total": len(test_cases), "by_category": {}}
    
    for i, test_case in enumerate(test_cases, 1):
        category = test_case["category"]
        if category not in results["by_category"]:
            results["by_category"][category] = {"correct": 0, "total": 0}
        
        print(f"\n--- Test Case {i}: {category} ---")
        print(f"Input: '{test_case['input']}'")
        print(f"Expected: {test_case['expected']}")
        
        result = agent.run({"container_description": test_case["input"]})
        
        if result.get("status") == "success":
            actual = result.get("standard_type")
            confidence = result.get("confidence")
            success = result.get("success")
            suggestions = result.get("suggestions", [])
            
            print(f"✓ Actual: {actual}")
            print(f"✓ Confidence: {confidence}%")
            print(f"✓ Success: {success}")
            print(f"✓ Suggestions: {suggestions}")
            
            # Show analysis for interesting cases
            if confidence < 70 or actual != test_case["expected"]:
                matched_terms = result.get("matched_terms", [])
                all_scores = result.get("all_scores", {})
                print(f"✓ Matched Terms: {matched_terms}")
                print(f"✓ Top Scores: {dict(sorted(all_scores.items(), key=lambda x: x[1], reverse=True)[:3])}")
            
            # Check correctness
            if actual == test_case["expected"]:
                print("✅ CORRECT")
                results["correct"] += 1
                results["by_category"][category]["correct"] += 1
            else:
                print("❌ WRONG")
            
            results["by_category"][category]["total"] += 1
            
        else:
            print(f"✗ Error: {result.get('error')}")
            results["by_category"][category]["total"] += 1
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"OVERALL RESULTS")
    print(f"{'='*50}")
    print(f"Total Accuracy: {results['correct']}/{results['total']} ({results['correct']/results['total']*100:.1f}%)")
    
    print(f"\nBY CATEGORY:")
    for category, stats in results["by_category"].items():
        accuracy = stats["correct"]/stats["total"]*100 if stats["total"] > 0 else 0
        print(f"  {category}: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")

def test_edge_cases():
    """Test specific edge cases and error handling"""
    print("\n=== Testing Edge Cases ===")
    
    agent = ContainerStandardizationAgent()
    agent.load_context()
    
    edge_cases = [
        {"input": None, "description": "None input"},
        {"input": "", "description": "Empty string"},
        {"input": "   ", "description": "Whitespace only"},
        {"input": "12345", "description": "Numbers only"},
        {"input": "!@#$%", "description": "Special characters"},
        {"input": "a" * 100, "description": "Very long input"},
        {"input": "MIXED case INPUT", "description": "Mixed case"},
        {"input": "20 40 RF HC", "description": "Multiple conflicting terms"},
    ]
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n--- Edge Case {i}: {test_case['description']} ---")
        print(f"Input: {repr(test_case['input'])}")
        
        try:
            result = agent.run({"container_description": test_case["input"]})
            
            if result.get("status") == "success":
                print(f"✓ Result: {result.get('standard_type')}")
                print(f"✓ Confidence: {result.get('confidence')}%")
                print(f"✓ Success: {result.get('success')}")
                print(f"✓ Fallback used: {result.get('fallback_used', False)}")
            else:
                print(f"✓ Error handled: {result.get('error')}")
                
        except Exception as e:
            print(f"✗ Unhandled exception: {e}")

def test_multiple_containers():
    """Test processing multiple container descriptions at once"""
    print("\n=== Testing Multiple Container Processing ===")
    
    agent = ContainerStandardizationAgent()
    agent.load_context()
    
    # Test multiple containers
    test_data = {
        "container_descriptions": [
            "20GP",
            "40 foot reefer",
            "high cube",
            "tank container",
            "invalid input"
        ]
    }
    
    print(f"Input: {test_data['container_descriptions']}")
    
    result = agent.run(test_data)
    
    if result.get("status") == "success":
        print(f"✓ Total processed: {result.get('total_processed')}")
        
        for i, container_result in enumerate(result.get("results", []), 1):
            original = test_data["container_descriptions"][i-1]
            standardized = container_result.get("standard_type")
            confidence = container_result.get("confidence")
            
            print(f"  {i}. '{original}' → {standardized} ({confidence}%)")
    else:
        print(f"✗ Error: {result.get('error')}")

def test_performance():
    """Test performance with various input sizes"""
    print("\n=== Testing Performance ===")
    
    agent = ContainerStandardizationAgent()
    agent.load_context()
    
    import time
    
    # Test different input complexities
    performance_tests = [
        {"input": "20GP", "description": "Simple code"},
        {"input": "twenty foot dry container", "description": "Medium description"},
        {"input": "large forty foot high cube refrigerated container with special requirements", "description": "Complex description"},
        {"input": " ".join(["container"] * 50), "description": "Very long repetitive input"},
    ]
    
    for test in performance_tests:
        print(f"\n--- Performance Test: {test['description']} ---")
        
        start_time = time.time()
        result = agent.run({"container_description": test["input"]})
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"✓ Input length: {len(test['input'])} characters")
        print(f"✓ Processing time: {processing_time:.2f}ms")
        print(f"✓ Result: {result.get('standard_type')}")
        print(f"✓ Confidence: {result.get('confidence')}%")

def test_rate_fallback():
    """Test rate fallback functionality"""
    print("\n=== Testing Rate Fallback ===")
    
    agent = ContainerStandardizationAgent()
    agent.load_context()
    
    # Test containers that need rate fallback
    fallback_tests = [
        {"input": "40RF", "expected_fallback": "40DC"},
        {"input": "20TK", "expected_fallback": "20DC"},
        {"input": "40HC", "expected_fallback": "40DC"},
        {"input": "20DC", "expected_fallback": "20DC"},  # No fallback needed
        {"input": "40DC", "expected_fallback": "40DC"},  # No fallback needed
    ]
    
    for test in fallback_tests:
        print(f"\n--- Fallback Test: {test['input']} ---")
        
        result = agent.run({"container_description": test["input"]})
        
        if result.get("status") == "success":
            standard_type = result.get("standard_type")
            fallback_type = result.get("rate_fallback_type")
            
            print(f"✓ Standard Type: {standard_type}")
            print(f"✓ Rate Fallback: {fallback_type}")
            print(f"✓ Expected Fallback: {test['expected_fallback']}")
            
            if fallback_type == test["expected_fallback"]:
                print("✅ CORRECT FALLBACK")
            else:
                print("❌ WRONG FALLBACK")
        else:
            print(f"✗ Error: {result.get('error')}")

if __name__ == "__main__":
    test_container_standardization_agent()
    test_edge_cases()
    test_multiple_containers()
    test_performance()
    test_rate_fallback()
