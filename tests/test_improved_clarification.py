#!/usr/bin/env python3
"""
Test script to verify improved clarification logic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.validation_agent import ValidationAgent
from agents.clarification_agent import ClarificationAgent

def test_fcl_shipment_with_container_type():
    """Test FCL shipment with container type - should not ask for volume"""
    
    print("Testing FCL Shipment with Container Type")
    print("=" * 50)
    
    # Test data: FCL shipment with container type (should not ask for volume)
    test_data = {
        "origin": "Jebel Ali",
        "destination": "Mundra", 
        "shipment_type": "FCL",
        "container_type": "20DC",
        "quantity": 50,
        "weight": "15 metric tons",
        "volume": "",  # Should not be asked for FCL
        "shipment_date": "",  # Should be asked
        "commodity": "",  # Should be asked first
        "dangerous_goods": False,
        "special_requirements": "",
        "customer_name": "John Smith",
        "customer_company": "ABC Electronics Ltd.",
        "customer_email": "",
        "insurance": False,
        "packaging": "",
        "customs_clearance": False,
        "delivery_address": "",
        "pickup_address": "",
        "documents_required": []
    }
    
    # Test validation agent
    validation_agent = ValidationAgent()
    validation_result = validation_agent.process({
        "extraction_data": test_data,
        "email_type": "logistics_request"
    })
    
    print("Validation Result:")
    print(f"Missing fields: {validation_result.get('missing_fields', [])}")
    
    # Test clarification agent
    clarification_agent = ClarificationAgent()
    clarification_result = clarification_agent.process({
        "extraction_data": test_data,
        "validation": validation_result,
        "missing_fields": validation_result.get('missing_fields', []),
        "thread_id": "test-fcl-001"
    })
    
    print("\nClarification Result:")
    print(f"Clarification needed: {clarification_result.get('clarification_needed', False)}")
    print(f"Missing fields: {clarification_result.get('missing_fields', [])}")
    
    # Check that volume is NOT asked for FCL
    missing_fields = clarification_result.get('missing_fields', [])
    if 'volume' not in missing_fields:
        print("✅ SUCCESS: Volume not asked for FCL shipment")
    else:
        print("❌ FAILURE: Volume should not be asked for FCL shipment")
    
    # Check that shipment_date and commodity are asked
    expected_fields = ['shipment_date', 'commodity']
    for field in expected_fields:
        if field in missing_fields:
            print(f"✅ SUCCESS: {field} correctly asked")
        else:
            print(f"❌ FAILURE: {field} should be asked")
    
    return 'volume' not in missing_fields and all(field in missing_fields for field in expected_fields)

def test_lcl_shipment():
    """Test LCL shipment - should ask for volume"""
    
    print("\n\nTesting LCL Shipment")
    print("=" * 50)
    
    # Test data: LCL shipment (should ask for volume)
    test_data = {
        "origin": "Shanghai",
        "destination": "Los Angeles", 
        "shipment_type": "LCL",
        "container_type": "",
        "quantity": 5,
        "weight": "2 tons",
        "volume": "",  # Should be asked for LCL
        "shipment_date": "",  # Should be asked
        "commodity": "Electronics",  # Provided
        "dangerous_goods": False,  # Should be asked since commodity is provided
        "special_requirements": "",
        "customer_name": "Jane Doe",
        "customer_company": "Tech Solutions Inc.",
        "customer_email": "",
        "insurance": False,
        "packaging": "",
        "customs_clearance": False,
        "delivery_address": "",
        "pickup_address": "",
        "documents_required": []
    }
    
    # Test validation agent
    validation_agent = ValidationAgent()
    validation_result = validation_agent.process({
        "extraction_data": test_data,
        "email_type": "logistics_request"
    })
    
    print("Validation Result:")
    print(f"Missing fields: {validation_result.get('missing_fields', [])}")
    
    # Test clarification agent
    clarification_agent = ClarificationAgent()
    clarification_result = clarification_agent.process({
        "extraction_data": test_data,
        "validation": validation_result,
        "missing_fields": validation_result.get('missing_fields', []),
        "thread_id": "test-lcl-001"
    })
    
    print("\nClarification Result:")
    print(f"Clarification needed: {clarification_result.get('clarification_needed', False)}")
    print(f"Missing fields: {clarification_result.get('missing_fields', [])}")
    
    # Check that volume IS asked for LCL
    missing_fields = clarification_result.get('missing_fields', [])
    if 'volume' in missing_fields:
        print("✅ SUCCESS: Volume correctly asked for LCL shipment")
    else:
        print("❌ FAILURE: Volume should be asked for LCL shipment")
    
    # Check that dangerous_goods is asked since commodity is provided
    if 'dangerous_goods' in missing_fields:
        print("✅ SUCCESS: Dangerous goods asked since commodity is provided")
    else:
        print("❌ FAILURE: Dangerous goods should be asked since commodity is provided")
    
    return 'volume' in missing_fields and 'dangerous_goods' in missing_fields

def test_container_type_inference():
    """Test that container type infers FCL shipment type"""
    
    print("\n\nTesting Container Type Inference")
    print("=" * 50)
    
    # Test data: Container type specified but no shipment type
    test_data = {
        "origin": "Rotterdam",
        "destination": "New York", 
        "shipment_type": "",  # Not specified
        "container_type": "40HC",  # Should infer FCL
        "quantity": 10,
        "weight": "25 tons",
        "volume": "",  # Should not be asked since FCL inferred
        "shipment_date": "",  # Should be asked
        "commodity": "Machinery",
        "dangerous_goods": False,
        "special_requirements": "",
        "customer_name": "Bob Wilson",
        "customer_company": "Industrial Corp",
        "customer_email": "",
        "insurance": False,
        "packaging": "",
        "customs_clearance": False,
        "delivery_address": "",
        "pickup_address": "",
        "documents_required": []
    }
    
    # Test validation agent
    validation_agent = ValidationAgent()
    validation_result = validation_agent.process({
        "extraction_data": test_data,
        "email_type": "logistics_request"
    })
    
    print("Validation Result:")
    print(f"Missing fields: {validation_result.get('missing_fields', [])}")
    
    # Test clarification agent
    clarification_agent = ClarificationAgent()
    clarification_result = clarification_agent.process({
        "extraction_data": test_data,
        "validation": validation_result,
        "missing_fields": validation_result.get('missing_fields', []),
        "thread_id": "test-inference-001"
    })
    
    print("\nClarification Result:")
    print(f"Clarification needed: {clarification_result.get('clarification_needed', False)}")
    print(f"Missing fields: {clarification_result.get('missing_fields', [])}")
    
    # Check that volume is NOT asked (FCL inferred from container type)
    missing_fields = clarification_result.get('missing_fields', [])
    if 'volume' not in missing_fields:
        print("✅ SUCCESS: Volume not asked when FCL inferred from container type")
    else:
        print("❌ FAILURE: Volume should not be asked when FCL inferred from container type")
    
    # Check that shipment_date is asked
    if 'shipment_date' in missing_fields:
        print("✅ SUCCESS: Shipment date correctly asked")
    else:
        print("❌ FAILURE: Shipment date should be asked")
    
    return 'volume' not in missing_fields and 'shipment_date' in missing_fields

def test_port_validation_removal():
    """Test that port validation is not asked (handled by port lookup)"""
    
    print("\n\nTesting Port Validation Removal")
    print("=" * 50)
    
    # Test data: Invalid ports but should not be asked for clarification
    test_data = {
        "origin": "Invalid Port",  # Invalid but should not be asked
        "destination": "Another Invalid Port",  # Invalid but should not be asked
        "shipment_type": "FCL",
        "container_type": "20DC",
        "quantity": 5,
        "weight": "10 tons",
        "volume": "",
        "shipment_date": "",  # Should be asked
        "commodity": "",  # Should be asked
        "dangerous_goods": False,
        "special_requirements": "",
        "customer_name": "Alice Brown",
        "customer_company": "Test Company",
        "customer_email": "",
        "insurance": False,
        "packaging": "",
        "customs_clearance": False,
        "delivery_address": "",
        "pickup_address": "",
        "documents_required": []
    }
    
    # Test validation agent
    validation_agent = ValidationAgent()
    validation_result = validation_agent.process({
        "extraction_data": test_data,
        "email_type": "logistics_request"
    })
    
    print("Validation Result:")
    print(f"Missing fields: {validation_result.get('missing_fields', [])}")
    
    # Test clarification agent
    clarification_agent = ClarificationAgent()
    clarification_result = clarification_agent.process({
        "extraction_data": test_data,
        "validation": validation_result,
        "missing_fields": validation_result.get('missing_fields', []),
        "thread_id": "test-ports-001"
    })
    
    print("\nClarification Result:")
    print(f"Clarification needed: {clarification_result.get('clarification_needed', False)}")
    print(f"Missing fields: {clarification_result.get('missing_fields', [])}")
    
    # Check that origin and destination are NOT asked (handled by port lookup)
    missing_fields = clarification_result.get('missing_fields', [])
    if 'origin' not in missing_fields and 'destination' not in missing_fields:
        print("✅ SUCCESS: Port validation not asked (handled by port lookup)")
    else:
        print("❌ FAILURE: Port validation should not be asked")
    
    # Check that other fields are still asked
    expected_fields = ['shipment_date', 'commodity']
    for field in expected_fields:
        if field in missing_fields:
            print(f"✅ SUCCESS: {field} correctly asked")
        else:
            print(f"❌ FAILURE: {field} should be asked")
    
    return 'origin' not in missing_fields and 'destination' not in missing_fields

if __name__ == "__main__":
    print("Testing Improved Clarification Logic")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_fcl_shipment_with_container_type()
    test2_passed = test_lcl_shipment()
    test3_passed = test_container_type_inference()
    test4_passed = test_port_validation_removal()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print(f"FCL shipment with container type: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"LCL shipment: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"Container type inference: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    print(f"Port validation removal: {'✅ PASSED' if test4_passed else '❌ FAILED'}")
    
    if all([test1_passed, test2_passed, test3_passed, test4_passed]):
        print("\n🎉 All tests passed! Improved clarification logic is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the clarification logic.") 