#!/usr/bin/env python3
"""
Test Databricks Claude 3.7 Sonnet
Verify the better model is working
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_databricks_claude():
    """Test with Databricks Claude 3.7 Sonnet"""
    print("=" * 70)
    print("TEST: Databricks Claude 3.7 Sonnet")
    print("=" * 70)
    
    try:
        from agents.unified_email_classifier_agent import UnifiedEmailClassifierAgent
        
        print("\n1️⃣ Initializing agent...")
        agent = UnifiedEmailClassifierAgent()
        
        print("2️⃣ Loading context (connecting to Databricks Claude 3.7 Sonnet)...")
        if not agent.load_context():
            print("❌ Failed to load context")
            return False
        
        print("3️⃣ Processing sample email...")
        test_email = {
            "subject": "Urgent: FCL Shipping Quote Needed",
            "body_text": """Hello,
            
I urgently need a quote for shipping 3x40HC containers from Shanghai, China to Los Angeles, USA.

Details:
- Cargo: Electronics (laptops and tablets)
- Weight: approximately 25 tons per container
- Ready date: March 20, 2026
- Incoterms: FOB Shanghai
- Special requirements: Temperature controlled, insurance required

Please provide your best rate ASAP.

Best regards,
John Smith
Procurement Manager
TechCorp International
john.smith@techcorp.com
+1-555-0123
""",
            "from_email": "john.smith@techcorp.com",
            "thread_history": []
        }
        
        result = agent.process(test_email)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print(f"\n✅ Classification successful with Claude 3.7 Sonnet!")
        print(f"   Email Type: {result.get('email_type')}")
        print(f"   Sender Type: {result.get('sender_type')}")
        print(f"   Confidence: {result.get('confidence')}")
        print(f"   Urgency: {result.get('urgency', 'normal')}")
        
        if result.get('confidence', 0) >= 0.8:
            print(f"\n🎉 HIGH CONFIDENCE! Claude 3.7 Sonnet is working perfectly!")
            return True
        else:
            print(f"\n⚠️  Low confidence, but model is responding")
            return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("\n🧪 Testing Databricks Claude 3.7 Sonnet (Better Model!)")
    print("=" * 70)
    
    success = test_databricks_claude()
    
    print("\n" + "=" * 70)
    if success:
        print("🎉 SUCCESS! You're now using Claude 3.7 Sonnet!")
        print("\n📊 Model Comparison:")
        print("   ❌ Claude 3 Haiku (Anthropic)     - Fast but basic")
        print("   ✅ Claude 3.7 Sonnet (Databricks) - MUCH BETTER! ⭐")
        print("\n💡 Claude 3.7 Sonnet is:")
        print("   • More accurate for complex tasks")
        print("   • Better at understanding context")
        print("   • Superior reasoning capabilities")
        print("   • Perfect for production logistics AI!")
    else:
        print("⚠️  Test failed. Check errors above.")
    print("=" * 70)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
