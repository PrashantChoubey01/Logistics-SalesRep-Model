"""One-time script to build and save port embeddings for vector search"""

import os
import sys
import json
import pickle
import numpy as np
from typing import Dict, List, Any
from datetime import datetime

class PortEmbeddingBuilder:
    """One-time builder for port embeddings"""
    
    def __init__(self):
        self.embedding_model = None
        self.port_data = {}
        self.embeddings = {}
        
    def initialize_embedding_model(self):
        """Initialize sentence transformer model"""
        try:
            from sentence_transformers import SentenceTransformer
            print("🔄 Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Embedding model loaded successfully")
            return True
        except ImportError:
            print("❌ sentence-transformers not installed. Run: pip install sentence-transformers")
            return False
        except Exception as e:
            print(f"❌ Error loading embedding model: {e}")
            return False
    
    def load_port_json(self, port_file: str = "port_names.json"):
        """Load port data from JSON file"""
        try:
            with open(port_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Convert to standard format: code -> name
            self.port_data = {}
            for key, value in raw_data.items():
                if len(key) == 5 and key.isupper():  # Standard port code format
                    self.port_data[key] = value
                elif isinstance(value, str) and len(value) == 5 and value.isupper():
                    self.port_data[value] = key  # Reverse mapping
            
            print(f"✅ Loaded {len(self.port_data)} ports from {port_file}")
            return True
            
        except FileNotFoundError:
            print(f"❌ {port_file} not found. Creating sample data...")
            self._create_sample_port_data()
            return True
        except Exception as e:
            print(f"❌ Error loading port data: {e}")
            return False
    
    def _create_sample_port_data(self):
        """Create sample port data for testing"""
        self.port_data = {
            "CNSHA": "Shanghai",
            "USLAX": "Los Angeles", 
            "USLGB": "Long Beach",
            "SGSIN": "Singapore",
            "NLRTM": "Rotterdam",
            "DEHAM": "Hamburg",
            "HKHKG": "Hong Kong",
            "USNYC": "New York",
            "GBFXT": "Felixstowe",
            "BEANR": "Antwerp",
            "INMUN": "Mumbai",
            "USOAK": "Oakland",
            "USSAV": "Savannah",
            "USORF": "Norfolk",
            "CAVAN": "Vancouver",
            "JPYOK": "Yokohama",
            "KRPUS": "Busan",
            "TWKHH": "Kaohsiung",
            "THBKK": "Bangkok",
            "MYTPP": "Port Klang",
            "CNQIN": "Qingdao",
            "CNNGB": "Ningbo",
            "CNSZX": "Shenzhen",
            "JPTYO": "Tokyo",
            "JPKOB": "Kobe"
        }
        print("✅ Using sample port data")
    
    def build_embeddings(self):
        """Build embeddings for all ports and their variations"""
        if not self.embedding_model:
            print("❌ Embedding model not initialized")
            return False
        
        print("🔄 Building port embeddings...")
        
        # Prepare all text variations for embedding
        embedding_data = {}
        texts_to_embed = []
        text_metadata = []
        
        for port_code, port_name in self.port_data.items():
            # Add original port name
            texts_to_embed.append(port_name)
            text_metadata.append({
                "text": port_name,
                "port_code": port_code,
                "port_name": port_name,
                "type": "original_name"
            })
            
            # Add port code
            texts_to_embed.append(port_code)
            text_metadata.append({
                "text": port_code,
                "port_code": port_code,
                "port_name": port_name,
                "type": "port_code"
            })
            
            # Add variations
            variations = self._generate_variations(port_name)
            for variation in variations:
                texts_to_embed.append(variation)
                text_metadata.append({
                    "text": variation,
                    "port_code": port_code,
                    "port_name": port_name,
                    "type": "variation"
                })
        
        # Create embeddings in batches
        print(f"🔄 Creating embeddings for {len(texts_to_embed)} text variations...")
        batch_size = 32
        all_embeddings = []
        
        for i in range(0, len(texts_to_embed), batch_size):
            batch = texts_to_embed[i:i + batch_size]
            batch_embeddings = self.embedding_model.encode(batch, convert_to_numpy=True)
            all_embeddings.extend(batch_embeddings)
            
            print(f"🔄 Processed {min(i + batch_size, len(texts_to_embed))}/{len(texts_to_embed)} embeddings")
        
        # Store embeddings with metadata
        for i, (metadata, embedding) in enumerate(zip(text_metadata, all_embeddings)):
            key = metadata["text"].lower().strip()
            embedding_data[key] = {
                "embedding": embedding.tolist(),  # Convert numpy to list for JSON serialization
                "port_code": metadata["port_code"],
                "port_name": metadata["port_name"],
                "original_text": metadata["text"],
                "type": metadata["type"]
            }
        
        self.embeddings = embedding_data
        print(f"✅ Built {len(embedding_data)} embeddings")
        return True
    
    def _generate_variations(self, port_name: str) -> List[str]:
        """Generate common variations of port names"""
        variations = set()
        
        # Common prefixes and suffixes
        variations.add(f"Port of {port_name}")
        variations.add(f"{port_name} Port")
        variations.add(f"{port_name} Seaport")
        variations.add(f"{port_name} Container Terminal")
        variations.add(f"{port_name} Terminal")
        variations.add(f"{port_name} Harbor")
        variations.add(f"{port_name} Harbour")
        
        # Handle multi-word names
        words = port_name.split()
        if len(words) > 1:
            # Create abbreviation from first letters
            abbreviation = ''.join(word[0].upper() for word in words)
            variations.add(abbreviation)
            
            # Specific common abbreviations
            if port_name == "Los Angeles":
                variations.update(["LA", "L.A.", "Los Angeles Port"])
            elif port_name == "New York":
                variations.update(["NYC", "NY", "New York Port"])
            elif port_name == "Long Beach":
                variations.update(["LB", "Long Beach Port"])
            elif port_name == "Hong Kong":
                variations.update(["HK", "HKG"])
            elif port_name == "San Francisco":
                variations.update(["SF", "San Fran"])
        
        # Remove original name and empty strings
        variations.discard(port_name)
        variations.discard("")
        
        return list(variations)
    
    def save_embeddings(self, output_dir: str = "data/embeddings"):
        """Save embeddings and metadata to files"""
        if not self.embeddings:
            print("❌ No embeddings to save")
            return False
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save embeddings as pickle (fast loading)
        embeddings_path = os.path.join(output_dir, "port_embeddings.pkl")
        with open(embeddings_path, 'wb') as f:
            pickle.dump(self.embeddings, f)
        
        # Save port data as JSON
        port_data_path = os.path.join(output_dir, "port_data.json")
        with open(port_data_path, 'w', encoding='utf-8') as f:
            json.dump(self.port_data, f, indent=2, ensure_ascii=False)
        
        # Save metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "total_embeddings": len(self.embeddings),
            "total_ports": len(self.port_data),
            "embedding_model": "all-MiniLM-L6-v2",
            "embedding_dimension": len(list(self.embeddings.values())[0]["embedding"]) if self.embeddings else 0,
            "files": {
                "embeddings": "port_embeddings.pkl",
                "port_data": "port_data.json"
            }
        }
        
        metadata_path = os.path.join(output_dir, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✅ Saved embeddings to:")
        print(f"   📁 {embeddings_path}")
        print(f"   📁 {port_data_path}")
        print(f"   📁 {metadata_path}")
        
        return True
    
    def build_complete_embeddings(self, port_file: str = "port_names.json", output_dir: str = "data/embeddings"):
        """Complete one-time build process"""
        print("🚀 Starting one-time port embedding build...")
        
        # Step 1: Initialize embedding model
        if not self.initialize_embedding_model():
            return False
        
        # Step 2: Load port JSON
        if not self.load_port_json(port_file):
            return False
        
        # Step 3: Build embeddings
        if not self.build_embeddings():
            return False
        
        # Step 4: Save everything
        if not self.save_embeddings(output_dir):
            return False
        
        print("🎉 One-time embedding build completed successfully!")
        print("The PortLookupAgent can now be used for fast port lookups.")
        return True

def main():
    """Main function for one-time embedding build"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build port embeddings for vector search")
    parser.add_argument("--port-file", default="port_names.json", help="Input port JSON file")
    parser.add_argument("--output-dir", default="data/embeddings", help="Output directory for embeddings")
    
    args = parser.parse_args()
    
    builder = PortEmbeddingBuilder()
    success = builder.build_complete_embeddings(args.port_file, args.output_dir)
    
    if success:
        print("\n✅ Embedding build completed successfully!")
        print("You can now use the PortLookupAgent for fast port lookups.")
        return 0
    else:
        print("\n❌ Embedding build failed!")
        return 1

if __name__ == "__main__":
    exit(main())