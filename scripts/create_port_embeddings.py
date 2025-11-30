#!/usr/bin/env python3
"""
Create Port Data and Embeddings from port_names.json
====================================================
Converts port_names.json to port_data.json format and generates embeddings
for vector similarity search.
"""

import json
import pickle
import os
import sys
from pathlib import Path
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_port_names() -> Dict[str, str]:
    """Load port_names.json file"""
    port_names_path = project_root / "port_names.json"
    
    if not port_names_path.exists():
        raise FileNotFoundError(f"port_names.json not found at {port_names_path}")
    
    with open(port_names_path, 'r', encoding='utf-8') as f:
        port_data = json.load(f)
    
    print(f"✅ Loaded {len(port_data)} ports from port_names.json")
    return port_data

def create_port_data_json(port_data: Dict[str, str], output_dir: Path):
    """Create port_data.json in the format expected by PortLookupAgent"""
    # port_data is already in the correct format: {code: name}
    output_path = output_dir / "port_data.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(port_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Created port_data.json with {len(port_data)} ports")
    return output_path

def create_embeddings(port_data: Dict[str, str], output_dir: Path):
    """Create embeddings for all port names using SentenceTransformer"""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print("❌ sentence-transformers not installed. Install with: pip install sentence-transformers")
        return None
    
    print("📦 Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("🔄 Generating embeddings for port names...")
    embeddings = {}
    
    for port_code, port_name in port_data.items():
        # Create embeddings for multiple variations
        variations = [
            port_name,  # Full name
            port_name.lower(),  # Lowercase
            port_code,  # Port code itself
        ]
        
        # Add variations without common prefixes/suffixes
        name_clean = port_name
        for prefix in ["Port of ", "Port ", " Port"]:
            if name_clean.startswith(prefix):
                name_clean = name_clean[len(prefix):]
            if name_clean.endswith(prefix):
                name_clean = name_clean[:-len(prefix)]
        if name_clean != port_name:
            variations.append(name_clean)
            variations.append(name_clean.lower())
        
        # Generate embedding for the primary name (use first variation)
        embedding = model.encode([variations[0]])[0]
        
        # Store embedding data
        embeddings[port_code] = {
            "port_code": port_code,
            "port_name": port_name,
            "embedding": embedding.tolist(),  # Convert numpy array to list
            "variations": variations[:3],  # Store first 3 variations
        }
        
        # Also create entries for variations (for better matching)
        for variation in variations[1:3]:  # Use first 2 additional variations
            variation_key = f"{port_code}_{variation.lower()}"
            embeddings[variation_key] = {
                "port_code": port_code,
                "port_name": port_name,
                "embedding": embedding.tolist(),
                "variations": [variation],
            }
    
    # Save embeddings
    output_path = output_dir / "port_embeddings.pkl"
    with open(output_path, 'wb') as f:
        pickle.dump(embeddings, f)
    
    print(f"✅ Created port_embeddings.pkl with {len(embeddings)} embeddings")
    return output_path

def main():
    """Main function to create port data and embeddings"""
    print("=" * 80)
    print("🌍 Creating Port Data and Embeddings")
    print("=" * 80)
    
    # Create output directory
    output_dir = project_root / "data" / "embeddings"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {output_dir}")
    
    # Load port names
    try:
        port_data = load_port_names()
    except Exception as e:
        print(f"❌ Error loading port_names.json: {e}")
        return 1
    
    # Create port_data.json
    try:
        create_port_data_json(port_data, output_dir)
    except Exception as e:
        print(f"❌ Error creating port_data.json: {e}")
        return 1
    
    # Create embeddings
    try:
        embeddings_path = create_embeddings(port_data, output_dir)
        if not embeddings_path:
            print("⚠️  Embeddings not created, but port_data.json is ready")
    except Exception as e:
        print(f"❌ Error creating embeddings: {e}")
        print("⚠️  Continuing without embeddings (vector search will be disabled)")
    
    print("\n" + "=" * 80)
    print("✅ Port data and embeddings created successfully!")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"   - Port data: {len(port_data)} ports")
    print(f"   - Output directory: {output_dir}")
    print(f"\n💡 Next steps:")
    print(f"   1. Test with: python3 test_port_lookup_50_ports.py")
    print(f"   2. The PortLookupAgent will automatically use these files")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

