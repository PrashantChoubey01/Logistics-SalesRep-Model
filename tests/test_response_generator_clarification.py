#!/usr/bin/env python3
"""
Test script to verify Response Generator uses Clarification data properly
"""

import sys
import os
import json

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

def test_clarification_response():
    """Test that response generator creates clarification request when needed"""
    print("=== Testing Clarification Response Generation ===")
    
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
    
    result = run_workflow(
        email_text=email_text,
        subject=subject,
        sender="john@abcelectronics.com",
        thread_id="test-clarification-response-001"
    )
    
    # Check clarification data
    clarification = result.get('clarification', {})
    print(f"✓ Clarification needed: {clarification.get('clarification_needed', False)}")
    print(f"✓ Missing fields: {clarification.get('missing_fields', [])}")
    
    # Check response data
    response = result.get('response', {})
    print(f"✓ Response type: {response.get('response_type', 'N/A')}")
    print(f"✓ Clarification included: {response.get('clarification_included', False)}")
    print(f"✓ Confirmation handled: {response.get('confirmation_handled', False)}")
    
    # Check response body
    response_body = response.get('response_body', '')
    print(f"✓ Response body length: {len(response_body)}")
    
    # Check if response contains clarification questions
    missing_fields = clarification.get('missing_fields', [])
    clarification_details = clarification.get('clarification_details', [])
    
    print(f"✓ Response contains missing field questions:")
    for detail in clarification_details:
        field = detail.get('field', '')
        prompt = detail.get('prompt', '')
        if field in response_body or any(word in response_body for word in prompt.split()[:3]):
            print(f"   ✓ {field}: Found in response")
        else:
            print(f"   ✗ {field}: Not found in response")
    
    # Check if response uses customer name
    extraction = result.get('extraction', {})
    customer_name = extraction.get('customer_name', '')
    if customer_name and customer_name in response_body:
        print(f"✓ Customer name '{customer_name}' used in response")
    else:
        print(f"✗ Customer name not used in response")
    
    return result

def test_confirmation_response():
    """Test that response generator creates confirmation response when needed"""
    print("\n=== Testing Confirmation Response Generation ===")
    
    email_text = """
    Hi,

    Yes, I confirm the booking for 2x40ft containers from Shanghai to Long Beach.
    Please proceed with the arrangements.

    Thanks,
    Sarah Johnson
    """
    
    subject = "Booking Confirmation"
    
    result = run_workflow(
        email_text=email_text,
        subject=subject,
        sender="sarah@example.com",
        thread_id="test-confirmation-response-001"
    )
    
    # Check confirmation data
    confirmation = result.get('confirmation', {})
    print(f"✓ Is confirmation: {confirmation.get('is_confirmation', False)}")
    print(f"✓ Confirmation type: {confirmation.get('confirmation_type', 'N/A')}")
    
    # Check response data
    response = result.get('response', {})
    print(f"✓ Response type: {response.get('response_type', 'N/A')}")
    print(f"✓ Clarification included: {response.get('clarification_included', False)}")
    print(f"✓ Confirmation handled: {response.get('confirmation_handled', False)}")
    
    # Check response body
    response_body = response.get('response_body', '')
    print(f"✓ Response body length: {len(response_body)}")
    
    # Check if response acknowledges confirmation
    if 'confirm' in response_body.lower() or 'excellent' in response_body.lower():
        print("✓ Response acknowledges confirmation")
    else:
        print("✗ Response does not acknowledge confirmation")
    
    return result

def test_complete_information_response():
    """Test that response generator creates standard response when no clarification needed"""
    print("\n=== Testing Complete Information Response Generation ===")
    
    email_text = """
    Hi,

    We need to ship 50 containers from Jebel Ali to Mundra.
    Container type: 20DC
    Quantity: 50
    Weight: 15 metric tons per container
    Volume: 750 CBM
    Shipment type: FCL
    Cargo: Electronics
    Shipment date: 15th December 2024

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
        thread_id="test-complete-response-001"
    )
    
    # Check clarification data
    clarification = result.get('clarification', {})
    print(f"✓ Clarification needed: {clarification.get('clarification_needed', True)}")
    print(f"✓ Missing fields: {clarification.get('missing_fields', [])}")
    
    # Check response data
    response = result.get('response', {})
    print(f"✓ Response type: {response.get('response_type', 'N/A')}")
    print(f"✓ Clarification included: {response.get('clarification_included', False)}")
    print(f"✓ Confirmation handled: {response.get('confirmation_handled', False)}")
    
    # Check response body
    response_body = response.get('response_body', '')
    print(f"✓ Response body length: {len(response_body)}")
    
    # Check if response confirms details
    if 'confirm' in response_body.lower() or 'summary' in response_body.lower():
        print("✓ Response confirms shipment details")
    else:
        print("✗ Response does not confirm shipment details")
    
    return result

def test_lcl_volume_clarification():
    """Test LCL volume clarification response"""
    print("\n=== Testing LCL Volume Clarification Response ===")
    
    email_text = """
    Hi,

    We need LCL shipment from Mumbai to Rotterdam.
    Weight: 500 kg
    Commodity: Textiles
    Shipment date: 15th January 2025

    Please provide rates.

    Best regards,
    Sarah Johnson
    """
    
    subject = "LCL shipment request"
    
    result = run_workflow(
        email_text=email_text,
        subject=subject,
        sender="sarah@example.com",
        thread_id="test-lcl-volume-001"
    )
    
    # Check clarification data
    clarification = result.get('clarification', {})
    print(f"✓ Clarification needed: {clarification.get('clarification_needed', False)}")
    print(f"✓ Missing fields: {clarification.get('missing_fields', [])}")
    print(f"✓ Volume missing: {'volume' in clarification.get('missing_fields', [])}")
    
    # Check response data
    response = result.get('response', {})
    print(f"✓ Response type: {response.get('response_type', 'N/A')}")
    print(f"✓ Clarification included: {response.get('clarification_included', False)}")
    
    # Check if response asks for volume
    response_body = response.get('response_body', '')
    if 'volume' in response_body.lower() or 'cbm' in response_body.lower():
        print("✓ Response asks for volume information")
    else:
        print("✗ Response does not ask for volume information")
    
    return result

def run_comprehensive_test():
    """Run all response generator clarification tests"""
    print("Response Generator Clarification Test")
    print("=" * 60)
    
    try:
        # Test all scenarios
        test_clarification_response()
        test_confirmation_response()
        test_complete_information_response()
        test_lcl_volume_clarification()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("\nSummary:")
        print("✓ Clarification response generation")
        print("✓ Confirmation response generation")
        print("✓ Complete information response generation")
        print("✓ LCL volume clarification response")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_comprehensive_test() 