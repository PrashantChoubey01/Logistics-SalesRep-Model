#!/usr/bin/env python3
"""
Test Port Lookup Agent for 50 Popular Ports
===========================================
Tests if the port lookup agent returns correct port codes for 50 popular ports.
If ports fail, embeddings may need to be recreated.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from agents.port_lookup_agent import PortLookupAgent

# Test data: 50 popular ports with expected codes
TEST_PORTS = [
    # Asia
    {"port_name": "Shanghai", "expected_code": "CNSHA"},
    {"port_name": "Ningbo", "expected_code": "CNNGB"},
    {"port_name": "Shenzhen", "expected_code": "CNSZX"},
    {"port_name": "Qingdao", "expected_code": "CNQIN"},
    {"port_name": "Tianjin", "expected_code": "CNTNJ"},
    {"port_name": "Xiamen", "expected_code": "CNXMN"},
    {"port_name": "Dalian", "expected_code": "CNDLC"},
    {"port_name": "Guangzhou", "expected_code": "CNCAN"},
    {"port_name": "Singapore", "expected_code": "SGSIN"},
    {"port_name": "Port Klang", "expected_code": "MYPKG"},
    {"port_name": "Tanjung Pelepas", "expected_code": "MYTPP"},
    {"port_name": "Busan", "expected_code": "KRPUS"},
    {"port_name": "Kaohsiung", "expected_code": "TWKHH"},
    {"port_name": "Manila", "expected_code": "PHMNL"},
    {"port_name": "Jakarta", "expected_code": "IDJKT"},
    {"port_name": "Colombo", "expected_code": "LKCMB"},
    {"port_name": "Jebel Ali", "expected_code": "AEJEA"},
    {"port_name": "Dubai", "expected_code": "AEJEA"},  # Jebel Ali is Dubai's port
    {"port_name": "Sohar", "expected_code": "OMSOR"},
    {"port_name": "Jeddah", "expected_code": "SAJED"},
    {"port_name": "Hamad", "expected_code": "QADOH"},
    {"port_name": "Doha", "expected_code": "QADOH"},  # Hamad is Doha's port
    
    # India Subcontinent
    {"port_name": "Nhava Sheva", "expected_code": "INNSA"},
    {"port_name": "JNPT", "expected_code": "INNSA"},  # JNPT is Nhava Sheva
    {"port_name": "Mundra", "expected_code": "INMUN"},
    {"port_name": "Hazira", "expected_code": "INHZA"},
    {"port_name": "Chennai", "expected_code": "INMAA"},
    {"port_name": "Kolkata", "expected_code": "INKOL"},
    
    # Europe
    {"port_name": "Rotterdam", "expected_code": "NLRTM"},
    {"port_name": "Antwerp", "expected_code": "BEANR"},
    {"port_name": "Hamburg", "expected_code": "DEHAM"},
    {"port_name": "Bremerhaven", "expected_code": "DEBRV"},
    {"port_name": "Felixstowe", "expected_code": "GBFXT"},
    {"port_name": "Southampton", "expected_code": "GBSOU"},
    {"port_name": "Le Havre", "expected_code": "FRLEH"},
    {"port_name": "Valencia", "expected_code": "ESVLC"},
    {"port_name": "Barcelona", "expected_code": "ESBCN"},
    {"port_name": "Genoa", "expected_code": "ITGOA"},
    
    # North America
    {"port_name": "Los Angeles", "expected_code": "USLAX"},
    {"port_name": "Long Beach", "expected_code": "USLGB"},
    {"port_name": "New York", "expected_code": "USNYC"},
    {"port_name": "Newark", "expected_code": "USNYC"},  # Same port code as NYC
    {"port_name": "Savannah", "expected_code": "USSAV"},
    {"port_name": "Houston", "expected_code": "USHOU"},
    {"port_name": "Miami", "expected_code": "USMIA"},
    {"port_name": "Charleston", "expected_code": "USCHS"},
    
    # South America
    {"port_name": "Santos", "expected_code": "BRSSZ"},
    {"port_name": "Buenos Aires", "expected_code": "ARBUE"},
    {"port_name": "Callao", "expected_code": "PECLL"},
    {"port_name": "Cartagena", "expected_code": "COCTG"},
    
    # Africa
    {"port_name": "Tanger Med", "expected_code": "MAPTM"},
    {"port_name": "Durban", "expected_code": "ZADUR"},
    {"port_name": "Mombasa", "expected_code": "KEMBA"},
    {"port_name": "Lagos", "expected_code": "NGAPP"},
    {"port_name": "Apapa", "expected_code": "NGAPP"},  # Apapa is part of Lagos
    {"port_name": "Tin Can", "expected_code": "NGAPP"},  # Tin Can is part of Lagos
]

def test_port_lookup():
    """Test port lookup agent with 50 popular ports"""
    print("=" * 80)
    print("🌍 Testing Port Lookup Agent - 50 Popular Ports")
    print("=" * 80)
    
    # Initialize agent
    print("\n📦 Initializing Port Lookup Agent...")
    agent = PortLookupAgent()
    
    if not agent.load_context():
        print("❌ Failed to load agent context")
        return
    
    print(f"✅ Agent loaded successfully")
    print(f"   - Port data: {len(agent.port_data)} ports")
    print(f"   - Embeddings: {len(agent.embeddings)} embeddings")
    print(f"   - Vector search: {'✅ enabled' if agent.embedding_model else '❌ disabled'}")
    print()
    
    # Test results
    results = {
        "passed": [],
        "failed": [],
        "wrong_code": [],
        "low_confidence": []
    }
    
    # Test each port
    for i, test_case in enumerate(TEST_PORTS, 1):
        port_name = test_case["port_name"]
        expected_code = test_case["expected_code"]
        
        print(f"[{i:2d}/{len(TEST_PORTS)}] Testing: {port_name:20s} → Expected: {expected_code}", end=" ... ")
        
        # Lookup port
        result = agent._lookup_single_port(port_name)
        
        port_code = result.get("port_code")
        confidence = result.get("confidence", 0.0)
        method = result.get("method", "unknown")
        port_name_found = result.get("port_name", "")
        
        # Check result
        if port_code == expected_code:
            if confidence >= 0.7:
                results["passed"].append({
                    "port": port_name,
                    "code": port_code,
                    "confidence": confidence,
                    "method": method
                })
                print(f"✅ PASS (confidence: {confidence:.2f}, method: {method})")
            else:
                results["low_confidence"].append({
                    "port": port_name,
                    "code": port_code,
                    "confidence": confidence,
                    "method": method,
                    "expected": expected_code
                })
                print(f"⚠️  PASS (low confidence: {confidence:.2f}, method: {method})")
        elif port_code is None:
            results["failed"].append({
                "port": port_name,
                "expected": expected_code,
                "method": method,
                "error": result.get("error", "No match found")
            })
            print(f"❌ FAIL (no code returned)")
        else:
            results["wrong_code"].append({
                "port": port_name,
                "expected": expected_code,
                "got": port_code,
                "confidence": confidence,
                "method": method,
                "port_name_found": port_name_found
            })
            print(f"❌ FAIL (got: {port_code}, confidence: {confidence:.2f})")
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    total = len(TEST_PORTS)
    passed = len(results["passed"])
    low_conf = len(results["low_confidence"])
    wrong_code = len(results["wrong_code"])
    failed = len(results["failed"])
    
    print(f"\n✅ Passed (high confidence):     {passed:2d}/{total} ({passed/total*100:.1f}%)")
    print(f"⚠️  Passed (low confidence):     {low_conf:2d}/{total} ({low_conf/total*100:.1f}%)")
    print(f"❌ Wrong code:                    {wrong_code:2d}/{total} ({wrong_code/total*100:.1f}%)")
    print(f"❌ Failed (no code):              {failed:2d}/{total} ({failed/total*100:.1f}%)")
    print(f"\n📈 Overall Success Rate:         {(passed + low_conf)/total*100:.1f}%")
    
    # Print details for failures
    if results["wrong_code"]:
        print("\n" + "=" * 80)
        print("❌ WRONG CODE RESULTS")
        print("=" * 80)
        for item in results["wrong_code"]:
            print(f"  • {item['port']:20s} → Expected: {item['expected']}, Got: {item['got']:8s} "
                  f"(confidence: {item['confidence']:.2f}, method: {item['method']}, "
                  f"found: {item['port_name_found']})")
    
    if results["failed"]:
        print("\n" + "=" * 80)
        print("❌ FAILED (NO CODE RETURNED)")
        print("=" * 80)
        for item in results["failed"]:
            print(f"  • {item['port']:20s} → Expected: {item['expected']:8s} "
                  f"(method: {item['method']}, error: {item['error']})")
    
    if results["low_confidence"]:
        print("\n" + "=" * 80)
        print("⚠️  LOW CONFIDENCE RESULTS")
        print("=" * 80)
        for item in results["low_confidence"]:
            print(f"  • {item['port']:20s} → Code: {item['code']:8s} "
                  f"(confidence: {item['confidence']:.2f}, method: {item['method']})")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)
    
    if wrong_code + failed > 0:
        print("\n⚠️  Some ports failed or returned wrong codes.")
        print("   Consider recreating embeddings if failures are due to vector search issues.")
        print("\n   To recreate embeddings, check:")
        print("   - data/embeddings/port_embeddings.pkl")
        print("   - data/embeddings/port_data.json")
        print("   - Ensure all 50 ports are included in the port data")
    else:
        print("\n✅ All ports returned correct codes!")
        if low_conf > 0:
            print(f"   Note: {low_conf} ports have low confidence but correct codes.")
            print("   Consider improving embeddings for better confidence scores.")
    
    return results

if __name__ == "__main__":
    results = test_port_lookup()
    
    # Exit with error code if there are failures
    if results["wrong_code"] or results["failed"]:
        sys.exit(1)
    else:
        sys.exit(0)

