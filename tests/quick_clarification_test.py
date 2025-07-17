#!/usr/bin/env python3
"""
Quick test script for Clarification Agent
Simple test to identify basic issues
"""

import sys
import os

# Add the agents directory to the path
agents_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents")
sys.path.insert(0, agents_path)

def quick_test():
    """Quick test of clarification agent"""
    print("Quick Clarification Agent Test")
    print("=" * 40)
    
    try:
        # Import the clarification agent
        from clarification_agent import ClarificationAgent
        print("✓ Clarification agent imported successfully")
        
        # Initialize agent
        agent = ClarificationAgent()
        print(f"✓ Agent initialized: {agent.agent_name}")
        
        # Test context loading
        context_loaded = agent.load_context()
        print(f"✓ Context loaded: {context_loaded}")
        print(f"✓ LLM client: {agent.client is not None}")
        
        # Simple test with missing fields
        test_input = {
            "extraction_data": {
                "origin": "Shanghai",
                "destination": None,
                "shipment_type": "FCL",
                "container_type": "40GP",
                "quantity": 2,
                "weight": "25 tons",
                "commodity": "electronics",
                "shipment_date": None
            },
            "missing_fields": ["destination", "shipment_date"],
            "thread_id": "quick-test-001"
        }
        
        print("\nTesting with missing fields...")
        result = agent.process(test_input)
        
        print(f"✓ Clarification needed: {result.get('clarification_needed', False)}")
        print(f"✓ Missing fields: {result.get('missing_fields', [])}")
        print(f"✓ Priority: {result.get('priority', 'unknown')}")
        print(f"✓ Method: {result.get('clarification_method', 'unknown')}")
        
        if result.get('clarification_details'):
            print("✓ Clarification details:")
            for detail in result['clarification_details']:
                print(f"   - {detail.get('field')}: {detail.get('prompt')}")
        
        if result.get('clarification_message'):
            print(f"✓ Message preview: {result['clarification_message'][:100]}...")
        
        print("\n✓ Quick test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Quick test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_test()
    if success:
        print("\nClarification agent is working correctly!")
    else:
        print("\nClarification agent has issues that need to be fixed.") 