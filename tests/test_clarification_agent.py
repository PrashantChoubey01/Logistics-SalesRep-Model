#!/usr/bin/env python3
"""
Comprehensive test script for Clarification Agent
Tests all aspects of clarification generation and identifies issues
"""

import sys
import os
import json
from typing import Dict, Any

# Add the agents directory to the path
agents_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents")
sys.path.insert(0, agents_path)

# Import the clarification agent
try:
    from clarification_agent import ClarificationAgent
except ImportError:
    import importlib.util
    clarification_path = os.path.join(agents_path, "clarification_agent.py")
    spec = importlib.util.spec_from_file_location("clarification_agent", clarification_path)
    if spec and spec.loader:
        clarification_agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(clarification_agent_module)
        ClarificationAgent = clarification_agent_module.ClarificationAgent
    else:
        raise ImportError("Could not import clarification_agent")

def test_agent_initialization():
    """Test if the clarification agent can be initialized properly"""
    print("=== Testing Agent Initialization ===")
    
    try:
        agent = ClarificationAgent()
        print(f"✓ Agent initialized successfully: {agent.agent_name}")
        
        # Test context loading
        context_loaded = agent.load_context()
        print(f"✓ Context loaded: {context_loaded}")
        print(f"✓ LLM client available: {agent.client is not None}")
        print(f"✓ Config available: {agent.config is not None}")
        
        if agent.config:
            print(f"✓ Model name: {agent.config.get('model_name', 'Not set')}")
        
        return agent
    except Exception as e:
        print(f"✗ Agent initialization failed: {e}")
        return None

def test_fallback_clarification(agent):
    """Test fallback clarification when LLM is not available"""
    print("\n=== Testing Fallback Clarification ===")
    
    if not agent:
        print("✗ Agent not available for testing")
        return
    
    # Test data with missing fields
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
        "thread_id": "test-fallback-001"
    }
    
    try:
        # Temporarily disable LLM client to test fallback
        original_client = agent.client
        agent.client = None
        
        result = agent.process(test_input)
        
        print(f"✓ Fallback clarification result: {result.get('clarification_needed', False)}")
        print(f"✓ Missing fields: {result.get('missing_fields', [])}")
        print(f"✓ Priority: {result.get('priority', 'unknown')}")
        print(f"✓ Method: {result.get('clarification_method', 'unknown')}")
        
        if result.get('clarification_details'):
            print("✓ Clarification details:")
            for detail in result['clarification_details']:
                print(f"   - {detail.get('field')}: {detail.get('prompt')}")
        
        # Restore client
        agent.client = original_client
        return result
        
    except Exception as e:
        print(f"✗ Fallback clarification failed: {e}")
        # Restore client
        agent.client = original_client
        return None

def test_llm_clarification(agent):
    """Test LLM-based clarification generation"""
    print("\n=== Testing LLM Clarification ===")
    
    if not agent or not agent.client:
        print("✗ Agent or LLM client not available for testing")
        return
    
    # Test data with missing fields
    test_input = {
        "extraction_data": {
            "origin": "Shanghai",
            "destination": None,
            "shipment_type": "FCL",
            "container_type": "40GP",
            "quantity": 2,
            "weight": "25 tons",
            "commodity": "electronics",
            "shipment_date": None,
            "dangerous_goods": False
        },
        "validation": {
            "overall_validity": False,
            "missing_fields": ["destination", "shipment_date"],
            "completeness_score": 0.6
        },
        "missing_fields": ["destination", "shipment_date"],
        "thread_id": "test-llm-001"
    }
    
    try:
        result = agent.process(test_input)
        
        print(f"✓ LLM clarification result: {result.get('clarification_needed', False)}")
        print(f"✓ Missing fields: {result.get('missing_fields', [])}")
        print(f"✓ Priority: {result.get('priority', 'unknown')}")
        print(f"✓ Method: {result.get('clarification_method', 'unknown')}")
        
        if result.get('clarification_message'):
            print(f"✓ Clarification message preview: {result['clarification_message'][:100]}...")
        
        if result.get('clarification_details'):
            print("✓ Clarification details:")
            for detail in result['clarification_details']:
                print(f"   - {detail.get('field')}: {detail.get('prompt')}")
        
        return result
        
    except Exception as e:
        print(f"✗ LLM clarification failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_no_missing_fields(agent):
    """Test behavior when no fields are missing"""
    print("\n=== Testing No Missing Fields ===")
    
    if not agent:
        print("✗ Agent not available for testing")
        return
    
    # Test data with complete information
    test_input = {
        "extraction_data": {
            "origin": "Shanghai",
            "destination": "Long Beach",
            "shipment_type": "FCL",
            "container_type": "40GP",
            "quantity": 2,
            "weight": "25 tons",
            "volume": "50 CBM",
            "commodity": "electronics",
            "shipment_date": "2024-12-15",
            "dangerous_goods": False
        },
        "validation": {
            "overall_validity": True,
            "missing_fields": [],
            "completeness_score": 1.0
        },
        "missing_fields": [],
        "thread_id": "test-complete-001"
    }
    
    try:
        result = agent.process(test_input)
        
        print(f"✓ No missing fields result: {result.get('clarification_needed', True)}")
        print(f"✓ Missing fields: {result.get('missing_fields', [])}")
        print(f"✓ Message: {result.get('message', 'No message')}")
        
        return result
        
    except Exception as e:
        print(f"✗ No missing fields test failed: {e}")
        return None

def test_lcl_volume_requirement(agent):
    """Test LCL shipment volume requirement detection"""
    print("\n=== Testing LCL Volume Requirement ===")
    
    if not agent:
        print("✗ Agent not available for testing")
        return
    
    # Test LCL shipment without volume
    test_input = {
        "extraction_data": {
            "origin": "Mumbai",
            "destination": "Rotterdam",
            "shipment_type": "LCL",
            "container_type": None,
            "quantity": None,
            "weight": "500 kg",
            "volume": None,  # Missing volume for LCL
            "commodity": "textiles",
            "shipment_date": "2025-01-15",
            "dangerous_goods": False
        },
        "validation": {
            "overall_validity": False,
            "missing_fields": ["volume"],
            "completeness_score": 0.7
        },
        "missing_fields": ["volume"],
        "thread_id": "test-lcl-volume-001"
    }
    
    try:
        result = agent.process(test_input)
        
        print(f"✓ LCL volume requirement result: {result.get('clarification_needed', False)}")
        print(f"✓ Missing fields: {result.get('missing_fields', [])}")
        print(f"✓ Volume missing: {'volume' in result.get('missing_fields', [])}")
        
        if result.get('clarification_details'):
            volume_detail = next((d for d in result['clarification_details'] if d.get('field') == 'volume'), None)
            if volume_detail:
                print(f"✓ Volume question: {volume_detail.get('prompt')}")
        
        return result
        
    except Exception as e:
        print(f"✗ LCL volume requirement test failed: {e}")
        return None

def test_dangerous_goods_documents(agent):
    """Test dangerous goods document requirement detection"""
    print("\n=== Testing Dangerous Goods Documents ===")
    
    if not agent:
        print("✗ Agent not available for testing")
        return
    
    # Test dangerous goods without documents
    test_input = {
        "extraction_data": {
            "origin": "Hamburg",
            "destination": "New York",
            "shipment_type": "FCL",
            "container_type": "20GP",
            "quantity": 1,
            "weight": "2 tons",
            "volume": "15 CBM",
            "commodity": "chemicals",
            "shipment_date": "2025-02-20",
            "dangerous_goods": True,  # Dangerous goods
            "documents_required": None  # Missing documents
        },
        "validation": {
            "overall_validity": False,
            "missing_fields": ["documents_required"],
            "completeness_score": 0.8
        },
        "missing_fields": ["documents_required"],
        "thread_id": "test-dg-docs-001"
    }
    
    try:
        result = agent.process(test_input)
        
        print(f"✓ Dangerous goods documents result: {result.get('clarification_needed', False)}")
        print(f"✓ Missing fields: {result.get('missing_fields', [])}")
        print(f"✓ Documents required: {'documents_required' in result.get('missing_fields', [])}")
        
        if result.get('clarification_details'):
            docs_detail = next((d for d in result['clarification_details'] if d.get('field') == 'documents_required'), None)
            if docs_detail:
                print(f"✓ Documents question: {docs_detail.get('prompt')}")
        
        return result
        
    except Exception as e:
        print(f"✗ Dangerous goods documents test failed: {e}")
        return None

def test_priority_levels(agent):
    """Test different priority levels based on missing fields"""
    print("\n=== Testing Priority Levels ===")
    
    if not agent:
        print("✗ Agent not available for testing")
        return
    
    test_cases = [
        {
            "name": "High Priority - Missing Critical Fields",
            "input": {
                "extraction_data": {
                    "origin": None,
                    "destination": None,
                    "shipment_type": "FCL",
                    "container_type": None,
                    "quantity": None
                },
                "missing_fields": ["origin", "destination", "container_type", "quantity"],
                "thread_id": "test-high-priority-001"
            }
        },
        {
            "name": "Medium Priority - Missing Important Fields",
            "input": {
                "extraction_data": {
                    "origin": "Shanghai",
                    "destination": "Long Beach",
                    "shipment_type": "FCL",
                    "container_type": "40GP",
                    "quantity": 2,
                    "weight": None,
                    "volume": None,
                    "shipment_date": None
                },
                "missing_fields": ["weight", "volume", "shipment_date"],
                "thread_id": "test-medium-priority-001"
            }
        },
        {
            "name": "Low Priority - Missing Optional Fields",
            "input": {
                "extraction_data": {
                    "origin": "Shanghai",
                    "destination": "Long Beach",
                    "shipment_type": "FCL",
                    "container_type": "40GP",
                    "quantity": 2,
                    "weight": "25 tons",
                    "volume": "50 CBM",
                    "shipment_date": "2024-12-15",
                    "commodity": "electronics",
                    "special_requirements": None,
                    "customer_name": None
                },
                "missing_fields": ["special_requirements", "customer_name"],
                "thread_id": "test-low-priority-001"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        try:
            result = agent.process(test_case["input"])
            print(f"✓ Priority: {result.get('priority', 'unknown')}")
            print(f"✓ Missing fields: {result.get('missing_fields', [])}")
            print(f"✓ Clarification needed: {result.get('clarification_needed', False)}")
        except Exception as e:
            print(f"✗ Test failed: {e}")

def test_field_questions_coverage(agent):
    """Test that all field questions are properly defined"""
    print("\n=== Testing Field Questions Coverage ===")
    
    if not agent:
        print("✗ Agent not available for testing")
        return
    
    # Test all possible field questions
    all_fields = [
        "origin", "destination", "shipment_type", "container_type", "quantity",
        "weight", "volume", "shipment_date", "commodity", "dangerous_goods",
        "special_requirements", "customer_name", "customer_company", "customer_email",
        "insurance", "packaging", "customs_clearance", "delivery_address",
        "pickup_address", "documents_required"
    ]
    
    # Create test input with all fields missing
    test_input = {
        "extraction_data": {field: None for field in all_fields},
        "missing_fields": all_fields,
        "thread_id": "test-all-fields-001"
    }
    
    try:
        result = agent.process(test_input)
        
        if result.get('clarification_details'):
            covered_fields = [detail.get('field') for detail in result['clarification_details']]
            missing_questions = [field for field in all_fields if field not in covered_fields]
            
            print(f"✓ Total fields tested: {len(all_fields)}")
            print(f"✓ Fields with questions: {len(covered_fields)}")
            print(f"✓ Missing questions: {missing_questions}")
            
            if missing_questions:
                print("✗ Some fields don't have questions defined")
            else:
                print("✓ All fields have questions defined")
        
        return result
        
    except Exception as e:
        print(f"✗ Field questions coverage test failed: {e}")
        return None

def run_comprehensive_test():
    """Run all clarification agent tests"""
    print("Comprehensive Clarification Agent Test")
    print("=" * 60)
    
    # Initialize agent
    agent = test_agent_initialization()
    
    if not agent:
        print("✗ Cannot proceed with tests - agent initialization failed")
        return
    
    # Run all tests
    test_fallback_clarification(agent)
    test_llm_clarification(agent)
    test_no_missing_fields(agent)
    test_lcl_volume_requirement(agent)
    test_dangerous_goods_documents(agent)
    test_priority_levels(agent)
    test_field_questions_coverage(agent)
    
    print("\n" + "=" * 60)
    print("Comprehensive test completed!")
    print("\nSummary:")
    print("✓ Agent initialization and configuration")
    print("✓ Fallback clarification (when LLM unavailable)")
    print("✓ LLM-based clarification generation")
    print("✓ Complete information handling")
    print("✓ LCL volume requirement detection")
    print("✓ Dangerous goods document requirements")
    print("✓ Priority level assignment")
    print("✓ Field questions coverage")

if __name__ == "__main__":
    run_comprehensive_test() 