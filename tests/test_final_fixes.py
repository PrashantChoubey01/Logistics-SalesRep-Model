#!/usr/bin/env python3
"""
Test script to verify all fixes: rate display, friendly questions, correct ports, email chain
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.langgraph_orchestrator import run_workflow

def test_final_fixes():
    """Test that all fixes work correctly"""
    
    print("Testing All Fixes")
    print("=" * 50)
    
    # Test email that should trigger all the fixes
    email_text = """Hi,

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
ABC Electronics Ltd."""
    
    print("Running workflow with test email...")
    result = run_workflow(
        email_text=email_text,
        subject="Rate request for container shipment",
        sender="john.smith@abcelectronics.com",
        thread_id="test-final-fixes"
    )
    
    print("\n=== EXTRACTION RESULTS ===")
    extraction = result.get("extraction", {})
    print(f"Origin: {extraction.get('origin')}")
    print(f"Destination: {extraction.get('destination')}")
    print(f"Container Type: {extraction.get('container_type')}")
    print(f"Shipment Type: {extraction.get('shipment_type')}")
    
    print("\n=== PORT LOOKUP RESULTS ===")
    port_lookup = result.get("port_lookup", {})
    print(f"Port Lookup Results: {port_lookup.get('results', [])}")
    
    print("\n=== VALIDATION RESULTS ===")
    validation = result.get("validation", {})
    validated_data = validation.get("validated_data", {})
    print(f"Origin Code: {validated_data.get('origin_code')}")
    print(f"Destination Code: {validated_data.get('destination_code')}")
    print(f"Container Type: {validated_data.get('container_type')}")
    
    print("\n=== CONTAINER STANDARDIZATION ===")
    container_std = result.get("container_standardization", {})
    print(f"Standardized Container: {container_std.get('standard_type')}")
    
    print("\n=== RATE RECOMMENDATION ===")
    rate = result.get("rate", {})
    print(f"Rate Result: {rate}")
    
    print("\n=== CLARIFICATION ===")
    clarification = result.get("clarification", {})
    print(f"Clarification Needed: {clarification.get('clarification_needed')}")
    print(f"Missing Fields: {clarification.get('missing_fields', [])}")
    print(f"Extracted Summary: {clarification.get('extracted_summary', '')}")
    
    print("\n=== RESPONSE ===")
    response = result.get("response", {})
    response_body = response.get('response_body', '')
    print(f"Response Type: {response.get('response_type')}")
    print(f"Response Body Preview:")
    print(response_body[:800] + "..." if len(response_body) > 800 else response_body)
    
    # Check if rate is included
    if 'indicative rate' in response_body.lower() or '$4' in response_body or '$220' in response_body:
        print("\n✅ Indicative rate is included in the response")
    else:
        print("\n❌ Indicative rate is NOT included in the response")
    
    # Check if email chain is included
    if 'email chain' in response_body.lower() or '---' in response_body:
        print("✅ Email chain format is included")
    else:
        print("❌ Email chain format is NOT included")
    
    # Check if questions are friendly
    if 'could you please' in response_body.lower():
        print("✅ Questions are friendly and conversational")
    else:
        print("❌ Questions are not friendly enough")
    
    # Check if ports are correct
    if 'jebel ali (dubai)' in response_body.lower() and 'mundra' in response_body.lower():
        print("✅ Port names are correctly displayed")
    else:
        print("❌ Port names are not correctly displayed")
    
    print("\n" + "=" * 50)
    print("FULL RESPONSE:")
    print(response_body)

if __name__ == "__main__":
    test_final_fixes() 