#!/usr/bin/env python3
"""
Test Agent with Claude API
Tests if agents can use Claude API for processing.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_classification_agent():
    """Test UnifiedEmailClassifierAgent with Claude"""
    print("=" * 60)
    print("TEST: UnifiedEmailClassifierAgent with Claude")
    print("=" * 60)
    
    try:
        from agents.unified_email_classifier_agent import UnifiedEmailClassifierAgent
        
        # Initialize agent
        print("\n1️⃣ Initializing agent...")
        agent = UnifiedEmailClassifierAgent()
        
        # Load context (connects to Claude)
        print("2️⃣ Loading context (connecting to Claude)...")
        if not agent.load_context():
            print("❌ Failed to load context")
            return False
        
        # Test with sample email
        print("3️⃣ Processing sample email...")
        test_email = {
            "subject": "Shipping Quote Request",
            "body_text": "Hello, I need a quote for shipping 2x40HC containers from Shanghai to Los Angeles. Ready date is March 15, 2026. Cargo is electronics.",
            "from_email": "customer@example.com",
            "thread_history": []
        }
        
        result = agent.process(test_email)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print(f"✅ Classification successful!")
        print(f"   Email Type: {result.get('email_type')}")
        print(f"   Sender Type: {result.get('sender_type')}")
        print(f"   Confidence: {result.get('confidence')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extraction_agent():
    """Test InformationExtractionAgent with Claude"""
    print("\n" + "=" * 60)
    print("TEST: InformationExtractionAgent with Claude")
    print("=" * 60)
    
    try:
        from agents.information_extraction_agent import InformationExtractionAgent
        
        # Initialize agent
        print("\n1️⃣ Initializing agent...")
        agent = InformationExtractionAgent()
        
        # Load context
        print("2️⃣ Loading context (connecting to Claude)...")
        if not agent.load_context():
            print("❌ Failed to load context")
            return False
        
        # Test with sample email
        print("3️⃣ Extracting information from email...")
        test_data = {
            "email_data": {
                "subject": "FCL Quote Request",
                "body_text": "I need to ship 2x40HC from Shanghai to Los Angeles. Ready date March 15. Cargo: Electronics, 20 tons.",
                "from_email": "john.doe@example.com"
            },
            "cumulative_extraction": {}
        }
        
        result = agent.process(test_data)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print(f"✅ Extraction successful!")
        extraction = result.get("extraction", {})
        shipment = extraction.get("shipment_details", {})
        print(f"   Origin: {shipment.get('origin_port')}")
        print(f"   Destination: {shipment.get('destination_port')}")
        print(f"   Container: {extraction.get('container_details', {}).get('container_type')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n🧪 Testing Agents with Claude API")
    print("=" * 60)
    
    results = []
    
    # Test 1: Classification
    results.append(("Classification Agent", test_classification_agent()))
    
    # Test 2: Extraction
    results.append(("Extraction Agent", test_extraction_agent()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Agents are working with Claude!")
        print("\n✅ Your logistics AI bot is now using Claude API!")
    else:
        print("⚠️  Some tests failed. Check errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
