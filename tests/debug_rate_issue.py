#!/usr/bin/env python3
"""
Debug script to check why rate recommendation isn't being triggered
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.langgraph_orchestrator import run_workflow

def debug_rate_issue():
    """Debug why rate recommendation isn't working"""
    
    print("Debugging Rate Recommendation Issue")
    print("=" * 50)
    
    # Test email that should trigger rate recommendation
    email_text = """Hi team,

We want to ship 50 containers from Jebel Ali to Mundra using 20DC containers. The total weight is 15 metric tons. Please provide your best rate.

Regards,
John Smith
ABC Electronics Ltd."""
    
    print("Running workflow with test email...")
    result = run_workflow(
        email_text=email_text,
        subject="Shipping Request - FCL",
        sender="john.smith@abcelectronics.com",
        thread_id="debug-001"
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
    
    print("\n=== RESPONSE ===")
    response = result.get("response", {})
    print(f"Response Body: {response.get('response_body', '')[:500]}...")
    
    # Check why rate wasn't triggered
    origin_code = validated_data.get("origin_code")
    destination_code = validated_data.get("destination_code")
    standardized_container = container_std.get("standard_type") or validated_data.get("container_type")
    
    print("\n=== RATE TRIGGER CONDITIONS ===")
    print(f"Origin Code: {origin_code} {'✅' if origin_code else '❌'}")
    print(f"Destination Code: {destination_code} {'✅' if destination_code else '❌'}")
    print(f"Standardized Container: {standardized_container} {'✅' if standardized_container else '❌'}")
    
    if not origin_code:
        print("❌ Missing origin code - Port lookup may have failed for 'Jebel Ali'")
    if not destination_code:
        print("❌ Missing destination code - Port lookup may have failed for 'Mundra'")
    if not standardized_container:
        print("❌ Missing container type - Container standardization may have failed")
    
    if origin_code and destination_code and standardized_container:
        print("✅ All conditions met - Rate should have been triggered")

if __name__ == "__main__":
    debug_rate_issue() 