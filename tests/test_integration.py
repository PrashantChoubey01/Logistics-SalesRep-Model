#!/usr/bin/env python3
"""
Test script to verify clarification and confirmation agent integration
"""

import sys
import os
import json

# Add the agents directory to the path
agents_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents")
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

def test_clarification_scenario():
    """Test scenario where clarification is needed"""
    print("=== Testing Clarification Scenario ===")
    
    email_text = """
    Hi,
    
    I need to ship some containers from Shanghai to Los Angeles.
    Please provide rates.
    
    Thanks,
    John
    """
    
    subject = "Shipping request"
    
    result = run_workflow(
        email_text=email_text,
        subject=subject,
        sender="john@example.com",
        thread_id="test-clarification-001"
    )
    
    print(f"Response Type: {result.get('response', {}).get('response_type', 'N/A')}")
    print(f"Clarification Needed: {result.get('clarification', {}).get('clarification_needed', 'N/A')}")
    print(f"Confirmation Detected: {result.get('confirmation', {}).get('is_confirmation', 'N/A')}")
    
    return result

def test_confirmation_scenario():
    """Test scenario where customer is confirming something"""
    print("\n=== Testing Confirmation Scenario ===")
    
    email_text = """
    Hi,
    
    Yes, I confirm the booking for 2x40ft containers from Shanghai to Long Beach.
    Please proceed with the arrangements.
    
    Thanks,
    Sarah
    """
    
    subject = "Booking Confirmation"
    
    result = run_workflow(
        email_text=email_text,
        subject=subject,
        sender="sarah@example.com",
        thread_id="test-confirmation-001"
    )
    
    print(f"Response Type: {result.get('response', {}).get('response_type', 'N/A')}")
    print(f"Clarification Needed: {result.get('clarification', {}).get('clarification_needed', 'N/A')}")
    print(f"Confirmation Detected: {result.get('confirmation', {}).get('is_confirmation', 'N/A')}")
    print(f"Confirmation Type: {result.get('confirmation', {}).get('confirmation_type', 'N/A')}")
    
    return result

def test_complete_scenario():
    """Test scenario with complete information"""
    print("\n=== Testing Complete Information Scenario ===")
    
    email_text = """
    Hi,
    
    We need to ship 50 containers from Jebel Ali to Mundra.
    Details as follows:
    - Container type: 20DC
    - Total quantity: 50 containers
    - Weight: 15 metric tons per container
    - Shipment type: FCL
    - Cargo: Electronics
    - Shipment date: 15th December 2024
    
    Please provide rates and transit time.
    
    Best regards,
    John Smith
    ABC Electronics Ltd.
    """
    
    subject = "Rate request for container shipment"
    
    result = run_workflow(
        email_text=email_text,
        subject=subject,
        sender="john@abcelectronics.com",
        thread_id="test-complete-001"
    )
    
    print(f"Response Type: {result.get('response', {}).get('response_type', 'N/A')}")
    print(f"Clarification Needed: {result.get('clarification', {}).get('clarification_needed', 'N/A')}")
    print(f"Confirmation Detected: {result.get('confirmation', {}).get('is_confirmation', 'N/A')}")
    
    return result

if __name__ == "__main__":
    print("Testing Clarification and Confirmation Agent Integration")
    print("=" * 60)
    
    try:
        # Test clarification scenario
        clarification_result = test_clarification_scenario()
        
        # Test confirmation scenario
        confirmation_result = test_confirmation_scenario()
        
        # Test complete scenario
        complete_result = test_complete_scenario()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc() 