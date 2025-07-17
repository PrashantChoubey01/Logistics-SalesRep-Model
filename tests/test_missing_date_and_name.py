#!/usr/bin/env python3
"""
Test script to verify missing shipment date detection and customer name extraction
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

def test_missing_shipment_date():
    """Test scenario with missing shipment date"""
    print("=== Testing Missing Shipment Date Scenario ===")
    
    email_text = """
    Hi,

    We need to ship 50 containers from Jebel Ali to Mundra. 
    Details as follows:
    - Container type: 20DC
    - Total quantity: 50 containers
    - Weight: 15 metric tons per container
    - Shipment type: FCL
    - Cargo: Electronics
    - Shipment date: 

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
        thread_id="test-missing-date-001"
    )
    
    print(f"Response Type: {result.get('response', {}).get('response_type', 'N/A')}")
    print(f"Clarification Needed: {result.get('clarification', {}).get('clarification_needed', 'N/A')}")
    
    # Check if shipment_date is in missing fields
    missing_fields = result.get('clarification', {}).get('missing_fields', [])
    print(f"Missing Fields: {missing_fields}")
    print(f"Shipment Date Missing: {'shipment_date' in missing_fields}")
    
    # Check customer name extraction
    extraction = result.get('extraction', {})
    customer_name = extraction.get('customer_name', 'N/A')
    customer_company = extraction.get('customer_company', 'N/A')
    print(f"Customer Name: {customer_name}")
    print(f"Customer Company: {customer_company}")
    
    # Check response body for personalized salutation
    response_body = result.get('response', {}).get('response_body', '')
    print(f"Response contains 'Dear John': {'Dear John' in response_body}")
    print(f"Response contains 'Dear valued customer': {'Dear valued customer' in response_body}")
    
    return result

def test_complete_information_with_name():
    """Test scenario with complete information and customer name"""
    print("\n=== Testing Complete Information with Customer Name ===")
    
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
    Sarah Johnson
    Global Trading Co.
    """
    
    subject = "Rate request for container shipment"
    
    result = run_workflow(
        email_text=email_text,
        subject=subject,
        sender="sarah@globaltrading.com",
        thread_id="test-complete-name-001"
    )
    
    print(f"Response Type: {result.get('response', {}).get('response_type', 'N/A')}")
    print(f"Clarification Needed: {result.get('clarification', {}).get('clarification_needed', 'N/A')}")
    
    # Check customer name extraction
    extraction = result.get('extraction', {})
    customer_name = extraction.get('customer_name', 'N/A')
    customer_company = extraction.get('customer_company', 'N/A')
    print(f"Customer Name: {customer_name}")
    print(f"Customer Company: {customer_company}")
    
    # Check response body for personalized salutation
    response_body = result.get('response', {}).get('response_body', '')
    print(f"Response contains 'Dear Sarah': {'Dear Sarah' in response_body}")
    
    return result

def test_no_name_provided():
    """Test scenario with no customer name in signature"""
    print("\n=== Testing No Customer Name Scenario ===")
    
    email_text = """
    Hi,

    We need to ship 20 containers from Shanghai to Long Beach.
    Container type: 40GP
    Quantity: 20
    Weight: 25 tons
    Shipment type: FCL
    Cargo: Textiles
    Shipment date: 20th January 2025

    Please provide rates.

    Thanks
    """
    
    subject = "Shipping request"
    
    result = run_workflow(
        email_text=email_text,
        subject=subject,
        sender="customer@example.com",
        thread_id="test-no-name-001"
    )
    
    print(f"Response Type: {result.get('response', {}).get('response_type', 'N/A')}")
    print(f"Clarification Needed: {result.get('clarification', {}).get('clarification_needed', 'N/A')}")
    
    # Check customer name extraction
    extraction = result.get('extraction', {})
    customer_name = extraction.get('customer_name', 'N/A')
    print(f"Customer Name: {customer_name}")
    
    # Check response body for generic salutation
    response_body = result.get('response', {}).get('response_body', '')
    print(f"Response contains 'Dear valued customer': {'Dear valued customer' in response_body}")
    print(f"Response contains 'Dear sir': {'Dear sir' in response_body}")
    
    return result

if __name__ == "__main__":
    print("Testing Missing Shipment Date Detection and Customer Name Extraction")
    print("=" * 70)
    
    try:
        # Test missing shipment date
        missing_date_result = test_missing_shipment_date()
        
        # Test complete information with name
        complete_name_result = test_complete_information_with_name()
        
        # Test no name provided
        no_name_result = test_no_name_provided()
        
        print("\n" + "=" * 70)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc() 