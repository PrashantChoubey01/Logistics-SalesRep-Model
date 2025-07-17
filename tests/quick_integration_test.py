#!/usr/bin/env python3
"""
Quick integration test to verify Response Generator uses Clarification data
"""

import sys
import os

# Add the agents directory to the path
agents_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents")
sys.path.insert(0, agents_path)

# Import the orchestrator function robustly
try:
    from agents.langgraph_orchestrator import run_workflow
except ImportError:
    import importlib.util
    orchestrator_path = os.path.join(agents_path, "langgraph_orchestrator.py")
    spec = importlib.util.spec_from_file_location("langgraph_orchestrator", orchestrator_path)
    if spec and spec.loader:
        langgraph_orchestrator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(langgraph_orchestrator)
        run_workflow = langgraph_orchestrator.run_workflow
    else:
        raise ImportError("Could not import langgraph_orchestrator")

def quick_integration_test():
    """Quick test to verify clarification integration"""
    print("Quick Integration Test - Clarification + Response Generator")
    print("=" * 60)
    
    # Test email with missing shipment date
    email_text = """
    Hi,

    We need to ship 50 containers from Jebel Ali to Mundra.
    Container type: 20DC
    Quantity: 50
    Weight: 15 metric tons per container
    Shipment type: FCL
    Cargo: Electronics
    Shipment date: 

    Please provide rates and transit time.

    Best regards,
    John Smith
    ABC Electronics Ltd.
    """
    
    subject = "Rate request for container shipment"
    
    try:
        print("Running workflow with missing shipment date...")
        result = run_workflow(
            email_text=email_text,
            subject=subject,
            sender="john@abcelectronics.com",
            thread_id="quick-integration-001"
        )
        
        # Check clarification
        clarification = result.get('clarification', {})
        print(f"\n✓ Clarification needed: {clarification.get('clarification_needed', False)}")
        print(f"✓ Missing fields: {clarification.get('missing_fields', [])}")
        
        # Check response
        response = result.get('response', {})
        print(f"\n✓ Response type: {response.get('response_type', 'N/A')}")
        print(f"✓ Clarification included: {response.get('clarification_included', False)}")
        print(f"✓ Confirmation handled: {response.get('confirmation_handled', False)}")
        
        # Check response body
        response_body = response.get('response_body', '')
        print(f"\n✓ Response body length: {len(response_body)}")
        
        # Check if response asks for shipment date
        if 'shipment date' in response_body.lower() or 'depart' in response_body.lower():
            print("✓ Response asks for shipment date")
        else:
            print("✗ Response does not ask for shipment date")
        
        # Check if response uses customer name
        if 'Dear John' in response_body:
            print("✓ Response uses customer name")
        else:
            print("✗ Response does not use customer name")
        
        # Show response preview
        print(f"\n✓ Response preview:")
        print(response_body[:200] + "..." if len(response_body) > 200 else response_body)
        
        print("\n✓ Quick integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Quick integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_integration_test()
    if success:
        print("\nIntegration is working correctly!")
    else:
        print("\nIntegration has issues that need to be fixed.") 