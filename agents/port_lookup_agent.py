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
            "BEANR": "Antwerp"
        }
        self.embeddings = {}
        self.logger.info("✅ Using fallback port data")

    def load_context(self) -> bool:
        """Load embedding model for runtime use"""
        try:
            # Only load embedding model if we have embeddings
            if self.embeddings:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.logger.info("✅ Embedding model loaded for vector search")
            else:
                self.logger.info("✅ Agent loaded without vector search (using fallback methods)")
            return True
        except Exception as e:
            self.logger.error(f"Error loading embedding model: {e}")
            return True  # Continue without vector search

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
            return {
                "port_code": port_code,
                "port_name": self.port_data[port_code],
                "confidence": 1.0,
                "method": "exact_code_match"
            }
        
        return {
            "port_code": None,
            "port_name": None,
            "confidence": 0.0,
            "method": "exact_code_match"
        }

    def _exact_name_match(self, port_name: str) -> Dict[str, Any]:
        """Check for exact name match"""
        for port_code, name in self.port_data.items():
            if str(port_name).lower() == str(name).lower():
                return {
                    "port_code": port_code,
                    "port_name": name,
                    "confidence": 1.0,
                    "method": "exact_name_match"
                }
        
        return {
            "port_code": None,
            "port_name": None,
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
                return {
                    "port_code": best_match["port_code"],
                    "port_name": best_match["port_name"],
                    "confidence": float(best_similarity),
                    "method": "vector_similarity",
                    "matched_text": best_match["original_text"]
                }
        
        except Exception as e:
            self.logger.error(f"Vector similarity search failed: {e}")
        
        return {
            "port_code": None,
            "port_name": None,
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
                return {
                    "port_code": best_match[0],
                    "port_name": best_match[1],
                    "confidence": best_ratio,
                    "method": "fuzzy_string_match"
                }
        
        except Exception as e:
            self.logger.error(f"Fuzzy string matching failed: {e}")
        
        return {
            "port_code": None,
            "port_name": None,
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
                
                return {
                    "port_code": port_code,
                    "port_name": name,
                    "confidence": confidence * 0.8,  # Reduce confidence for partial match
                    "method": "partial_match"
                }
        
        # No match found
        return {
            "port_code": None,
            "port_name": None,
            "confidence": 0.0,
            "method": "no_match",
            "error": f"No match found for '{port_name}'"
        }

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
