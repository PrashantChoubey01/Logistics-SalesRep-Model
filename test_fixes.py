#!/usr/bin/env python3
"""
Test Fixes for Incomplete Data Handling
=======================================

This script tests the fixes for:
1. Validation agent not hallucinating data
2. NextActionAgent properly routing incomplete data to clarification
3. Response generator creating clarification requests
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph_orchestrator import LangGraphOrchestrator

def test_incomplete_data_fixes():
    """Test that incomplete data is properly handled."""
    print("\n" + "="*80)
    print("🚀 TESTING INCOMPLETE DATA FIXES")
    print("="*80)
    
    # Initialize orchestrator
    print("🔄 Initializing orchestrator...")
    try:
        orchestrator = LangGraphOrchestrator()
        print("✅ Orchestrator initialized successfully")
    except Exception as e:
        print(f"❌ Orchestrator initialization failed: {e}")
        return
    
    # Test incomplete email (should trigger clarification)
    print("\n📧 Test: Incomplete Customer Request")
    print("-" * 50)
    
    incomplete_email = {
        "email_text": """Hi,

I need shipping rates.

Thanks,
John Doe""",
        "subject": "Shipping Inquiry",
        "sender": "john.doe@company.com",
        "thread_id": "test_fixes_001",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        result = orchestrator.orchestrate_workflow(incomplete_email)
        
        if result.get('status') == 'success':
            print("✅ Incomplete request processed successfully")
            
            final_state = result.get('final_state', {})
            workflow_history = final_state.get('workflow_history', [])
            next_action = final_state.get('next_action', '')
            final_response = result.get('final_response', {})
            
            print(f"   🔄 Workflow Path: {' → '.join(workflow_history)}")
            print(f"   🎯 Next Action: {next_action}")
            print(f"   📧 Response Type: {final_response.get('response_type', 'unknown')}")
            
            # Check if clarification was triggered
            if 'CLARIFICATION_REQUEST' in workflow_history:
                print("   ✅ CLARIFICATION_REQUEST generated - SUCCESS!")
            else:
                print("   ❌ Expected CLARIFICATION_REQUEST not generated")
                print(f"   ⚠️ Instead went to: {workflow_history[-1] if workflow_history else 'Unknown'}")
            
            # Check extracted data for hallucination
            extracted_data = final_state.get('extracted_data', {})
            print(f"\n   📊 Extracted Data Analysis:")
            print(f"   Origin: {extracted_data.get('origin_name', 'N/A')}")
            print(f"   Destination: {extracted_data.get('destination_name', 'N/A')}")
            print(f"   Container: {extracted_data.get('container_type', 'N/A')}")
            
            # Check validation results for hallucination
            validation_results = final_state.get('validation_results', {})
            if validation_results:
                validation_data = validation_results.get('validation_results', {})
                print(f"\n   🔍 Validation Results Analysis:")
                
                origin_val = validation_data.get('origin_port', {})
                if origin_val:
                    input_value = origin_val.get('input_value', 'N/A')
                    print(f"   Origin Input: {input_value}")
                    if input_value and input_value not in ['', 'N/A', 'null', 'None']:
                        print("   ⚠️ WARNING: Validation agent may be hallucinating origin data!")
                
                dest_val = validation_data.get('destination_port', {})
                if dest_val:
                    input_value = dest_val.get('input_value', 'N/A')
                    print(f"   Destination Input: {input_value}")
                    if input_value and input_value not in ['', 'N/A', 'null', 'None']:
                        print("   ⚠️ WARNING: Validation agent may be hallucinating destination data!")
                
                container_val = validation_data.get('container_type', {})
                if container_val:
                    input_value = container_val.get('input_value', 'N/A')
                    print(f"   Container Input: {input_value}")
                    if input_value and input_value not in ['', 'N/A', 'null', 'None']:
                        print("   ⚠️ WARNING: Validation agent may be hallucinating container data!")
            
            # Check response content
            response_body = final_response.get('response_body', '')
            if 'clarification' in response_body.lower() or 'missing' in response_body.lower():
                print("   ✅ Response contains clarification language")
            else:
                print("   ⚠️ Response may not be asking for clarification")
                print(f"   📝 Response preview: {response_body[:200]}...")
                
        else:
            print(f"❌ Incomplete request failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("✅ INCOMPLETE DATA FIXES TESTING COMPLETED")
    print("="*80)
    print("\n🎯 EXPECTED BEHAVIOR:")
    print("• Incomplete request → CLARIFICATION_REQUEST")
    print("• No hallucinated data in validation results")
    print("• Response asks for missing information")

def main():
    """Run the fixes test."""
    print("🚀 INCOMPLETE DATA FIXES TEST SUITE")
    print("="*80)
    
    try:
        test_incomplete_data_fixes()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 