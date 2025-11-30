"""Runtime port lookup agent - returns port code, name, and confidence"""

import os
import sys
import json
import pickle
import re
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import base agent with error handling
try:
    from .base_agent import BaseAgent
except ImportError:
    try:
        from base_agent import BaseAgent
    except ImportError as e:
        import logging
        logging.error(f"Cannot import BaseAgent: {e}")
        # Create a minimal BaseAgent fallback
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

class PortLookupAgent(BaseAgent):
    """Runtime agent for port lookups - returns port code, name, and confidence"""

    def __init__(self, embeddings_dir: str = "data/embeddings"):
        super().__init__("port_lookup_agent")
        
        self.embeddings_dir = embeddings_dir
        self.port_data = {}  # code -> name mapping
        self.embeddings = {}  # text -> embedding data
        self.embedding_model = None
        self.confidence_threshold = 0.7
        
        # Load precomputed data
        self._load_precomputed_data()

    def _load_precomputed_data(self):
        """Load precomputed embeddings and port data"""
        try:
            # Load port data
            port_data_path = os.path.join(self.embeddings_dir, "port_data.json")
            if os.path.exists(port_data_path):
                with open(port_data_path, 'r', encoding='utf-8') as f:
                    self.port_data = json.load(f)
                self.logger.info(f"✅ Loaded {len(self.port_data)} ports")
            else:
                self.logger.warning("Port data not found, using fallback")
                self._create_fallback_data()
            
            # Load embeddings
            embeddings_path = os.path.join(self.embeddings_dir, "port_embeddings.pkl")
            if os.path.exists(embeddings_path):
                with open(embeddings_path, 'rb') as f:
                    self.embeddings = pickle.load(f)
                self.logger.info(f"✅ Loaded {len(self.embeddings)} embeddings")
            else:
                self.logger.warning("Embeddings not found, vector search disabled")
            
        except Exception as e:
            self.logger.error(f"Error loading precomputed data: {e}")
            self._create_fallback_data()

    def _create_fallback_data(self):
        """Create minimal fallback data"""
        self.port_data = {
            "CNSHA": "Shanghai",
            "USLAX": "Los Angeles",
            "SGSIN": "Singapore",
            "NLRTM": "Rotterdam",
            "DEHAM": "Hamburg",
            "HKHKG": "Hong Kong",
            "USNYC": "New York",
            "GBFXT": "Felixstowe",
            "BEANR": "Antwerp",
            "AEJEA": "Jebel Ali",  # Jebel Ali, UAE
            "INMUN": "Mundra",     # Mundra, India
            "PKKHI": "Karachi"     # Karachi, Pakistan
        }
        self.embeddings = {}
        self.logger.info("✅ Using fallback port data")

    def load_context(self) -> bool:
        """Load embedding model and LLM client for runtime use"""
        try:
            # Load embedding model if we have embeddings
            if self.embeddings:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("✅ Embedding model loaded for vector search")
            else:
                self.logger.info("✅ Agent loaded without vector search (using fallback methods)")
            
            # Load LLM client for fallback lookup (call parent method)
            super().load_context()
            
            return True
        except Exception as e:
            self.logger.error(f"Error loading context: {e}")
            return True  # Continue without vector search or LLM

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main process: Given a port name, return port code, name, and confidence
        
        Input: {"port_name": "shanghai"} or {"port_names": ["shanghai", "los angeles"]}
        Output: {
            "port_code": "CNSHA",
            "port_name": "Shanghai", 
            "confidence": 0.95,
            "method": "exact_match"
        }
        """
        
        # Handle single port lookup
        if "port_name" in input_data:
            port_name = input_data["port_name"]
            return self._lookup_single_port(port_name)
        
        # Handle multiple port lookups
        elif "port_names" in input_data:
            port_names = input_data["port_names"]
            results = []
            for port_name in port_names:
                result = self._lookup_single_port(port_name)
                results.append(result)
            return {"results": results}
        
        else:
            return {"error": "No port_name or port_names provided"}

    def _check_if_country_name(self, port_name: str) -> Optional[Dict[str, Any]]:
        """
        Check if input is a country name (not a port) using LLM with country_converter fallback.
        Returns country detection result if input is a country, None otherwise.
        """
        if not port_name or not isinstance(port_name, str):
            return None
        
        cleaned_name = port_name.strip()
        self.logger.debug(f"🔍 Checking if '{cleaned_name}' is a country name...")
        
        # Try LLM detection first if available
        if self.client:
            try:
                llm_result = self._llm_country_detection(cleaned_name)
                if llm_result and llm_result.get("is_country", False):
                    self.logger.info(f"✅ LLM detected '{cleaned_name}' as country: {llm_result.get('country')}")
                    return llm_result
            except Exception as e:
                self.logger.warning(f"LLM country detection failed: {e}, using fallback")
        
        # Fallback to country_converter
        try:
            import country_converter as coco
            
            # Also try common country aliases FIRST (before coco.convert)
            country_aliases = {
                "usa": "United States",
                "us": "United States",
                "u.s.": "United States",
                "u.s.a.": "United States",
                "uk": "United Kingdom",
                "u.k.": "United Kingdom",
                "uae": "United Arab Emirates",
                "china": "China"
            }
            
            cleaned_lower = cleaned_name.lower()
            alias_match = country_aliases.get(cleaned_lower)
            if alias_match:
                self.logger.info(f"✅ Alias match: '{cleaned_name}' → '{alias_match}'")
                return {
                    "port_code": None,
                    "port_name": None,
                    "country": alias_match,
                    "is_country": True,
                    "confidence": 0.95,
                    "method": "country_name_detection_alias",
                    "original_input": cleaned_name,
                    "suggestion": f"Please specify a port in {alias_match} (e.g., 'Los Angeles' or 'New York' for USA)"
                }
            
            # Try various country name formats with country_converter
            country_name = coco.convert(names=cleaned_name, to='name_short', not_found=None)
            
            # Also try with lowercase
            if not country_name or country_name == cleaned_name:
                country_name = coco.convert(names=cleaned_lower, to='name_short', not_found=None)
            
            if country_name and country_name != cleaned_name and country_name != cleaned_lower:
                # Found a country match
                self.logger.info(f"✅ Country converter detected '{cleaned_name}' as country: {country_name}")
                return {
                    "port_code": None,
                    "port_name": None,
                    "country": country_name,
                    "is_country": True,
                    "confidence": 0.9,
                    "method": "country_name_detection",
                    "original_input": cleaned_name,
                    "suggestion": f"Please specify a port in {country_name} (e.g., 'Los Angeles' or 'New York' for USA)"
                }
            else:
                self.logger.debug(f"❌ '{cleaned_name}' not recognized as a country")
        except ImportError:
            self.logger.warning("country_converter not available for country detection")
        except Exception as e:
            self.logger.warning(f"Country detection fallback failed: {e}")
        
        return None

    def _llm_country_detection(self, input_text: str) -> Optional[Dict[str, Any]]:
        """
        Use LLM to determine if input is a country name.
        Returns detection result if country, None otherwise.
        """
        try:
            prompt = f"""You are an expert in geography and international shipping. Determine if the following input is a COUNTRY NAME or a PORT/CITY NAME.

INPUT: "{input_text}"

Analyze the input and determine:
1. Is this a country name? (e.g., "USA", "China", "United States", "United Kingdom")
2. Is this a port/city name? (e.g., "Shanghai", "Los Angeles", "Rotterdam")

Examples:
- "USA" → COUNTRY
- "United States" → COUNTRY  
- "China" → COUNTRY
- "Shanghai" → PORT/CITY
- "Los Angeles" → PORT/CITY
- "New York" → PORT/CITY

Respond with JSON:
{{
    "is_country": true/false,
    "country_name": "Full country name if is_country=true, else null",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation"
}}"""

            if not self.client:
                return None
            
            response = self.client.invoke(prompt)
            
            # Parse response
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            # Extract JSON from response
            import json
            import re
            
            # Try to find JSON in response
            json_match = re.search(r'\{[^{}]*"is_country"[^{}]*\}', content, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                if result.get("is_country", False):
                    country_name = result.get("country_name", input_text)
                    return {
                        "port_code": None,
                        "port_name": None,
                        "country": country_name,
                        "is_country": True,
                        "confidence": result.get("confidence", 0.85),
                        "method": "llm_country_detection",
                        "original_input": input_text,
                        "suggestion": f"Please specify a port in {country_name} (e.g., 'Los Angeles' or 'New York' for USA)"
                    }
        except Exception as e:
            self.logger.error(f"LLM country detection error: {e}")
        
        return None

    def _lookup_single_port(self, port_name: str) -> Dict[str, Any]:
        """Lookup a single port and return code, name, confidence"""
        
        if not port_name or not isinstance(port_name, str):
            return {
                "port_code": None,
                "port_name": None,
                "confidence": 0.0,
                "method": "invalid_input",
                "error": "Invalid port name"
            }
        
        # FIRST: Check if input is a country name (not a port)
        country_result = self._check_if_country_name(port_name)
        if country_result:
            return country_result
        
        # Clean input
        cleaned_name = self._clean_port_name(port_name)
        
        # Try different lookup methods in order of preference
        
        # Method 1: Exact code match
        result = self._exact_code_match(cleaned_name)
        if result["confidence"] > 0.9:
            return result
        
        # Method 2: Exact name match
        result = self._exact_name_match(cleaned_name)
        if result["confidence"] > 0.9:
            return result
        
        # Method 3: Vector similarity search
        if self.embedding_model and self.embeddings:
            result = self._vector_similarity_search(cleaned_name)
            if result["confidence"] >= self.confidence_threshold:
                return result
        
        # Method 4: Fuzzy string matching
        result = self._fuzzy_string_match(cleaned_name)
        if result["confidence"] >= 0.6:
            return result
        
        # Method 5: Partial matching
        result = self._partial_match(cleaned_name)
        if result["confidence"] >= 0.5:
            return result
        
        # Method 6: LLM fallback (if confidence is low and LLM is available)
        if self.client and result["confidence"] < 0.7:
            llm_result = self._llm_port_lookup(cleaned_name)
            if llm_result and llm_result.get("confidence", 0) > result["confidence"]:
                return llm_result
        
        return result

    def _clean_port_name(self, port_name: str) -> str:
        """Clean and normalize port name"""
        # Remove extra whitespace and convert to title case
        cleaned = re.sub(r'\s+', ' ', port_name.strip()).title()
        
        # Remove common prefixes/suffixes
        prefixes_suffixes = [
            "Port of ", "Port ", " Port", " Seaport", " Container Terminal", 
            " Terminal", " Harbor", " Harbour"
        ]
        
        for fix in prefixes_suffixes:
            if cleaned.startswith(fix):
                cleaned = cleaned[len(fix):]
            elif cleaned.endswith(fix):
                cleaned = cleaned[:-len(fix)]
        
        return cleaned.strip()

    def _exact_code_match(self, port_name: str) -> Dict[str, Any]:
        """Check if input is exactly a port code"""
        port_code = port_name.upper()
        
        if port_code in self.port_data:
            port_name = self.port_data[port_code]
            # Try to get country information from embeddings
            country = "Unknown"
            if self.embeddings and port_code in self.embeddings:
                country = self.embeddings[port_code].get("country", "Unknown")
            
            return {
                "port_code": port_code,
                "port_name": port_name,
                "country": country,
                "full_name": f"{port_name} ({port_code}) - {country}",
                "confidence": 1.0,
                "method": "exact_code_match"
            }
        
        return {
            "port_code": None,
            "port_name": None,
            "country": None,
            "full_name": None,
            "confidence": 0.0,
            "method": "exact_code_match"
        }

    def _exact_name_match(self, port_name: str) -> Dict[str, Any]:
        """Check for exact name match"""
        for port_code, name in self.port_data.items():
            if str(port_name).lower() == str(name).lower():
                # Get country from embeddings if available
                country = "Unknown"
                if self.embeddings and port_code in self.embeddings:
                    country = self.embeddings[port_code].get("country", "Unknown")
                
                return {
                    "port_code": port_code,
                    "port_name": name,
                    "country": country,
                    "confidence": 1.0,
                    "method": "exact_name_match"
                }
        
        return {
            "port_code": None,
            "port_name": None,
            "country": None,
            "confidence": 0.0,
            "method": "exact_name_match"
        }

    def _vector_similarity_search(self, port_name: str) -> Dict[str, Any]:
        """Use vector similarity to find best match"""
        try:
            # Create embedding for input
            query_embedding = self.embedding_model.encode([port_name])[0]
            
            best_match = None
            best_similarity = 0.0
            
            # Compare with all stored embeddings
            for text_key, embedding_data in self.embeddings.items():
                stored_embedding = np.array(embedding_data["embedding"])
                
                # Calculate cosine similarity
                similarity = np.dot(query_embedding, stored_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                )
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = embedding_data
            
            if best_match and best_similarity >= self.confidence_threshold:
                # Get country from match or embeddings
                country = best_match.get("country", "Unknown")
                if country == "Unknown" and self.embeddings and best_match.get("port_code") in self.embeddings:
                    country = self.embeddings[best_match["port_code"]].get("country", "Unknown")
                
                return {
                    "port_code": best_match["port_code"],
                    "port_name": best_match["port_name"],
                    "country": country,
                    "confidence": float(best_similarity),
                    "method": "vector_similarity",
                    "matched_text": best_match.get("port_name", port_name)
                }
        
        except Exception as e:
            self.logger.error(f"Vector similarity search failed: {e}")
        
        return {
            "port_code": None,
            "port_name": None,
            "country": None,
            "confidence": 0.0,
            "method": "vector_similarity"
        }

    def _fuzzy_string_match(self, port_name: str) -> Dict[str, Any]:
        """Fuzzy string matching as fallback"""
        try:
            from difflib import SequenceMatcher
            
            best_match = None
            best_ratio = 0.0
            
            for port_code, name in self.port_data.items():
                # Compare with port name
                ratio = SequenceMatcher(None, str(port_name).lower(), str(name).lower()).ratio()
                
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = (port_code, name)
            
            if best_match and best_ratio >= 0.6:
                # Get country from embeddings if available
                country = "Unknown"
                port_code = best_match[0]
                if self.embeddings and port_code in self.embeddings:
                    country = self.embeddings[port_code].get("country", "Unknown")
                
                return {
                    "port_code": port_code,
                    "port_name": best_match[1],
                    "country": country,
                    "confidence": best_ratio,
                    "method": "fuzzy_string_match"
                }
        
        except Exception as e:
            self.logger.error(f"Fuzzy string matching failed: {e}")
        
        return {
            "port_code": None,
            "port_name": None,
            "country": None,
            "confidence": 0.0,
            "method": "fuzzy_string_match"
        }

    def _partial_match(self, port_name: str) -> Dict[str, Any]:
        """Partial matching as last resort"""
        port_name_lower = str(port_name).lower()
        
        # Check if port name is contained in any port
        for port_code, name in self.port_data.items():
            if port_name_lower in str(name).lower() or str(name).lower() in port_name_lower:
                confidence = min(len(port_name_lower), len(str(name).lower())) / max(len(port_name_lower), len(str(name).lower()))
                
                # Get country from embeddings if available
                country = "Unknown"
                if self.embeddings and port_code in self.embeddings:
                    country = self.embeddings[port_code].get("country", "Unknown")
                
                return {
                    "port_code": port_code,
                    "port_name": name,
                    "country": country,
                    "confidence": confidence * 0.8,  # Reduce confidence for partial match
                    "method": "partial_match"
                }
        
        # No match found
        return {
            "port_code": None,
            "port_name": None,
            "country": None,
            "confidence": 0.0,
            "method": "no_match",
            "error": f"No match found for '{port_name}'"
        }

    def _get_vector_candidates(self, port_name: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Get top K candidate ports using vector similarity for LLM context"""
        candidates = []
        
        if not self.embedding_model or not self.embeddings:
            # Fallback: use fuzzy matching to get candidates
            try:
                from difflib import SequenceMatcher
                scored = []
                for port_code, name in self.port_data.items():
                    ratio = SequenceMatcher(None, port_name.lower(), name.lower()).ratio()
                    scored.append({
                        "port_code": port_code,
                        "port_name": name,
                        "score": ratio
                    })
                scored.sort(key=lambda x: x["score"], reverse=True)
                return scored[:top_k]
            except Exception:
                return []
        
        try:
            # Use vector similarity
            query_embedding = self.embedding_model.encode([port_name])[0]
            
            scored = []
            for text_key, embedding_data in self.embeddings.items():
                # Skip variation keys, only use main port codes
                if "_" in text_key:
                    continue
                    
                stored_embedding = np.array(embedding_data["embedding"])
                similarity = np.dot(query_embedding, stored_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                )
                
                scored.append({
                    "port_code": embedding_data["port_code"],
                    "port_name": embedding_data["port_name"],
                    "score": float(similarity)
                })
            
            scored.sort(key=lambda x: x["score"], reverse=True)
            return scored[:top_k]
        except Exception as e:
            self.logger.warning(f"Error getting vector candidates: {e}")
            return []

    def _format_port_context(self, candidates: List[Dict[str, Any]]) -> str:
        """Format candidate ports for LLM context"""
        if not candidates:
            # Fallback: provide a sample of ports
            sample_ports = list(self.port_data.items())[:20]
            context = "Sample ports:\n"
            for code, name in sample_ports:
                context += f"  - {code}: {name}\n"
            return context
        
        context = "Candidate ports (most similar first):\n"
        for i, candidate in enumerate(candidates[:10], 1):
            context += f"  {i}. {candidate['port_code']}: {candidate['port_name']} (similarity: {candidate['score']:.3f})\n"
        
        return context

    def _llm_port_lookup(self, port_name: str) -> Optional[Dict[str, Any]]:
        """
        Use LLM to find port code when other methods have low confidence.
        Returns port lookup result or None if LLM is unavailable.
        """
        if not self.client:
            return None
        
        try:
            # Get candidate ports for context
            candidates = self._get_vector_candidates(port_name, top_k=10)
            port_context = self._format_port_context(candidates)
            
            # Build prompt
            prompt = f"""You are an expert in international shipping and port codes (UN/LOCODE format).

Given the port name: "{port_name}"

Find the matching port code from the candidate list below. Port codes are 5-character UN/LOCODE format (e.g., CNSHA, USLAX, SGSIN).

{port_context}

Instructions:
1. Match the input port name to the most likely port code
2. Consider common variations, abbreviations, and alternative names
3. If the port name matches a candidate, return that port code
4. If no good match exists, return null for port_code
5. Provide confidence score (0.0 to 1.0) based on how certain you are

Return your response as valid JSON in this exact format:
{{
    "port_code": "CNSHA" or null,
    "port_name": "Full port name",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this port code was chosen"
}}

Examples:
- Input: "Shanghai" → {{"port_code": "CNSHA", "port_name": "Shanghai", "confidence": 0.95, "reasoning": "Exact match"}}
- Input: "LA" → {{"port_code": "USLAX", "port_name": "Los Angeles", "confidence": 0.85, "reasoning": "Common abbreviation for Los Angeles"}}
- Input: "UnknownPort" → {{"port_code": null, "port_name": null, "confidence": 0.0, "reasoning": "No matching port found"}}

Now analyze the input and return the JSON response:"""

            # Call LLM using ChatOpenAI format
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=prompt)]
            response = self.client.invoke(messages)
            content = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON response
            import re
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'\{[^{}]*"port_code"[^{}]*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Try to find JSON in the response
                json_str = content.strip()
                if json_str.startswith('```'):
                    # Remove markdown code blocks
                    json_str = re.sub(r'```json\s*', '', json_str)
                    json_str = re.sub(r'```\s*', '', json_str)
                    json_str = json_str.strip()
            
            result = json.loads(json_str)
            
            # Validate and format result
            port_code = result.get("port_code")
            if port_code:
                # Get port name from our data if available
                port_name_found = self.port_data.get(port_code, result.get("port_name", port_name))
                confidence = float(result.get("confidence", 0.7))
                
                # Get country from embeddings if available
                country = "Unknown"
                if self.embeddings and port_code in self.embeddings:
                    country = self.embeddings[port_code].get("country", "Unknown")
                
                return {
                    "port_code": port_code,
                    "port_name": port_name_found,
                    "country": country,
                    "confidence": confidence,
                    "method": "llm_lookup",
                    "reasoning": result.get("reasoning", ""),
                    "original_port_name": port_name
                }
            else:
                # LLM couldn't find a match
                return {
                    "port_code": None,
                    "port_name": None,
                    "country": None,
                    "confidence": 0.0,
                    "method": "llm_lookup",
                    "reasoning": result.get("reasoning", "No matching port found"),
                    "error": f"LLM could not find port code for '{port_name}'"
                }
        
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse LLM JSON response: {e}")
            return None
        except Exception as e:
            self.logger.warning(f"LLM port lookup failed: {e}")
            return None

    def bulk_lookup(self, port_names: List[str]) -> List[Dict[str, Any]]:
        """Lookup multiple ports efficiently"""
        results = []
        for port_name in port_names:
            result = self._lookup_single_port(port_name)
            results.append(result)
        return results

    def get_port_suggestions(self, partial_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get port suggestions for partial input"""
        suggestions = []
        partial_lower = str(partial_name).lower()
        
        for port_code, name in self.port_data.items():
            if partial_lower in str(name).lower():
                suggestions.append({
                    "port_code": port_code,
                    "port_name": name,
                    "match_type": "contains"
                })
        
        # Sort by name length (shorter names first for better matches)
        suggestions.sort(key=lambda x: len(x["port_name"]))
        
        return suggestions[:limit]

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_port_lookup_agent():
    print("=== Testing Port Lookup Agent ===")
    
    agent = PortLookupAgent()
    
    test_cases = [
        # Exact matches
        {"port_name": "Shanghai", "expected_code": "CNSHA"},
        {"port_name": "USLAX", "expected_code": "USLAX"},
        
        # Case variations
        {"port_name": "shanghai", "expected_code": "CNSHA"},
        {"port_name": "LOS ANGELES", "expected_code": "USLAX"},
        
        # With prefixes/suffixes
        {"port_name": "Port of Shanghai", "expected_code": "CNSHA"},
        {"port_name": "Los Angeles Port", "expected_code": "USLAX"},
        
        # Abbreviations
        {"port_name": "LA", "expected_code": "USLAX"},
        {"port_name": "NYC", "expected_code": "USNYC"},
        
        # Partial matches
        {"port_name": "Shang", "expected_code": "CNSHA"},
        {"port_name": "Angeles", "expected_code": "USLAX"},
        
        # No match
        {"port_name": "NonExistentPort", "expected_code": None}
    ]
    
    if agent.load_context():
        print(f"✅ Agent loaded successfully")
        print(f"✅ Port data: {len(agent.port_data)} ports")
        print(f"✅ Embeddings: {len(agent.embeddings)} embeddings")
        print(f"✅ Vector search: {'enabled' if agent.embedding_model else 'disabled'}")
        
        correct = 0
        total = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i} ---")
            print(f"Input: '{test_case['port_name']}'")
            print(f"Expected: {test_case['expected_code']}")
            
            result = agent.run(test_case)
            
            if result.get("status") == "success":
                port_code = result.get("port_code")
                port_name = result.get("port_name")
                confidence = result.get("confidence", 0)
                method = result.get("method", "unknown")
                
                print(f"✓ Found: {port_code} - {port_name}")
                print(f"✓ Confidence: {confidence:.2f}")
                print(f"✓ Method: {method}")
                
                if port_code == test_case["expected_code"]:
                    print("✅ CORRECT")
                    correct += 1
                else:
                    print("❌ WRONG")
            else:
                print(f"✗ Error: {result.get('error')}")
        
        print(f"\n=== SUMMARY ===")
        print(f"Accuracy: {correct}/{total} ({correct/total*100:.1f}%)")
        
        # Test bulk lookup
        print(f"\n--- Bulk Lookup Test ---")
        bulk_test = ["Shanghai", "Los Angeles", "Singapore"]
        bulk_results = agent.bulk_lookup(bulk_test)
        
        for name, result in zip(bulk_test, bulk_results):
            print(f"{name} -> {result['port_code']} ({result['confidence']:.2f})")
        
        # Test suggestions
        print(f"\n--- Suggestions Test ---")
        suggestions = agent.get_port_suggestions("Sha")
        for suggestion in suggestions:
            print(f"  {suggestion['port_code']} - {suggestion['port_name']}")
        
    else:
        print("✗ Failed to load context")

if __name__ == "__main__":
    test_port_lookup_agent()
