#!/usr/bin/env python3
"""
Test script to verify Smart Clarification Agent integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.smart_clarification_agent import SmartClarificationAgent

def test_smart_clarification_agent():
    """Test the smart clarification agent with real scenarios"""
    
    print("Testing Smart Clarification Agent Integration")
    print("=" * 60)
    
    agent = SmartClarificationAgent()
    
    # Test Case 1: FCL with container type - should NOT ask for volume/weight
    print("\n1. Testing FCL with Container Type")
    print("-" * 40)
    
    test_data_1 = {
        "extraction_data": {
            "origin": "Jebel Ali",
            "destination": "Mundra",
            "shipment_type": "FCL",
            "container_type": "20DC",
            "quantity": 50,
            "weight": "15 metric tons",
            "volume": "",  # Should NOT be asked
            "shipment_date": "",  # Should be asked
            "commodity": "",  # Should be asked
            "customer_name": "John Smith",
            "customer_company": "ABC Electronics Ltd."
        },
        "container_standardization_data": {"standard_type": "20DC"},
        "port_lookup_data": {
            "results": [
                {"port_code": "AEJEA", "port_name": "Jebel Ali (Dubai)", "confidence": 0.87, "method": "vector_similarity"},
                {"port_code": "INMUN", "port_name": "Mundra", "confidence": 1.0, "method": "exact_name_match"}
            ]
        },
        "missing_fields": ["volume", "shipment_date", "commodity"],
        "thread_id": "test-fcl-001"
    }
    
    result_1 = agent.process(test_data_1)
    print(f"✓ Clarification needed: {result_1.get('clarification_needed')}")
    print(f"✓ Missing fields: {result_1.get('missing_fields', [])}")
    print(f"✓ Context: {result_1.get('context', {})}")
    
    if result_1.get("clarification_needed"):
        print(f"✓ Extracted summary:")
        print(result_1.get("extracted_summary", ""))
        print(f"✓ Message preview:")
        print(result_1.get("clarification_message", "")[:300] + "...")
    
    # Test Case 2: LCL shipment - should ask for volume/weight
    print("\n\n2. Testing LCL Shipment")
    print("-" * 40)
    
    test_data_2 = {
        "extraction_data": {
            "origin": "Shanghai",
            "destination": "Los Angeles",
            "shipment_type": "LCL",
            "container_type": "",
            "quantity": 5,
            "weight": "",  # Should be asked
            "volume": "",  # Should be asked
            "shipment_date": "",  # Should be asked
            "commodity": "Electronics",  # Provided
            "customer_name": "Jane Doe",
            "customer_company": "Tech Solutions Inc."
        },
        "container_standardization_data": {},
        "port_lookup_data": {
            "results": [
                {"port_code": "CNSHA", "port_name": "Shanghai", "confidence": 1.0, "method": "exact_name_match"},
                {"port_code": "USLAX", "port_name": "Los Angeles", "confidence": 1.0, "method": "exact_name_match"}
            ]
        },
        "missing_fields": ["weight", "volume", "shipment_date"],
        "thread_id": "test-lcl-001"
    }
    
    result_2 = agent.process(test_data_2)
    print(f"✓ Clarification needed: {result_2.get('clarification_needed')}")
    print(f"✓ Missing fields: {result_2.get('missing_fields', [])}")
    print(f"✓ Context: {result_2.get('context', {})}")
    
    if result_2.get("clarification_needed"):
        print(f"✓ Extracted summary:")
        print(result_2.get("extracted_summary", ""))
        print(f"✓ Message preview:")
        print(result_2.get("clarification_message", "")[:300] + "...")
    
    # Test Case 3: FCL without container - should ask for container preference
    print("\n\n3. Testing FCL without Container Type")
    print("-" * 40)
    
    test_data_3 = {
        "extraction_data": {
            "origin": "Rotterdam",
            "destination": "New York",
            "shipment_type": "FCL",
            "container_type": "",  # Not specified
            "quantity": 10,
            "weight": "25 tons",
            "shipment_date": "",  # Should be asked
            "commodity": "Machinery",
            "customer_name": "Bob Wilson",
            "customer_company": "Industrial Corp"
        },
        "container_standardization_data": {},
        "port_lookup_data": {
            "results": [
                {"port_code": "NLRTM", "port_name": "Rotterdam", "confidence": 1.0, "method": "exact_name_match"},
                {"port_code": "USNYC", "port_name": "New York", "confidence": 1.0, "method": "exact_name_match"}
            ]
        },
        "missing_fields": ["container_type", "shipment_date"],
        "thread_id": "test-fcl-no-container-001"
    }
    
    result_3 = agent.process(test_data_3)
    print(f"✓ Clarification needed: {result_3.get('clarification_needed')}")
    print(f"✓ Missing fields: {result_3.get('missing_fields', [])}")
    print(f"✓ Context: {result_3.get('context', {})}")
    
    if result_3.get("clarification_needed"):
        print(f"✓ Extracted summary:")
        print(result_3.get("extracted_summary", ""))
        print(f"✓ Message preview:")
        print(result_3.get("clarification_message", "")[:300] + "...")
    
    # Test Case 4: Dangerous goods assessment
    print("\n\n4. Testing Dangerous Goods Assessment")
    print("-" * 40)
    
    test_data_4 = {
        "extraction_data": {
            "origin": "Dubai",
            "destination": "Singapore",
            "shipment_type": "FCL",
            "container_type": "20DC",
            "quantity": 2,
            "weight": "5 tons",
            "shipment_date": "",  # Should be asked
            "commodity": "chemicals",  # Potentially dangerous
            "customer_name": "Alice Brown",
            "customer_company": "Chemical Corp"
        },
        "container_standardization_data": {"standard_type": "20DC"},
        "port_lookup_data": {
            "results": [
                {"port_code": "AEDXB", "port_name": "Dubai", "confidence": 1.0, "method": "exact_name_match"},
                {"port_code": "SGSIN", "port_name": "Singapore", "confidence": 1.0, "method": "exact_name_match"}
            ]
        },
        "missing_fields": ["shipment_date", "dangerous_goods"],
        "thread_id": "test-dangerous-001"
    }
    
    result_4 = agent.process(test_data_4)
    print(f"✓ Clarification needed: {result_4.get('clarification_needed')}")
    print(f"✓ Missing fields: {result_4.get('missing_fields', [])}")
    print(f"✓ Context: {result_4.get('context', {})}")
    
    if result_4.get("clarification_needed"):
        print(f"✓ Extracted summary:")
        print(result_4.get("extracted_summary", ""))
        print(f"✓ Message preview:")
        print(result_4.get("clarification_message", "")[:300] + "...")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print(f"1. FCL with container type: {'✅ PASSED' if 'volume' not in result_1.get('missing_fields', []) else '❌ FAILED'}")
    print(f"2. LCL shipment: {'✅ PASSED' if 'volume' in result_2.get('missing_fields', []) else '❌ FAILED'}")
    print(f"3. FCL without container: {'✅ PASSED' if 'container_preference' in result_3.get('missing_fields', []) else '❌ FAILED'}")
    print(f"4. Dangerous goods: {'✅ PASSED' if 'dangerous_goods' in result_4.get('missing_fields', []) else '❌ FAILED'}")
    
    all_passed = (
        'volume' not in result_1.get('missing_fields', []) and
        'volume' in result_2.get('missing_fields', []) and
        'container_preference' in result_3.get('missing_fields', []) and
        'dangerous_goods' in result_4.get('missing_fields', [])
    )
    
    if all_passed:
        print("\n🎉 All tests passed! Smart Clarification Agent is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the Smart Clarification Agent logic.")

if __name__ == "__main__":
    test_smart_clarification_agent() 