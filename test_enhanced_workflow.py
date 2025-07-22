#!/usr/bin/env python3
"""
Test Enhanced LangGraph Workflow
===============================

This script tests the enhanced LangGraph workflow with:
1. Clarification requests for incomplete data
2. Enhanced forwarder responses with acknowledgments
3. Complete customer confirmation flow
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph_orchestrator import LangGraphOrchestrator

def test_enhanced_workflow():
    """Test the enhanced LangGraph workflow."""
    print("\n" + "="*80)
    print("🚀 TESTING ENHANCED LANGGRAPH WORKFLOW")
    print("="*80)
    
    # Initialize orchestrator
    print("🔄 Initializing orchestrator...")
    try:
        orchestrator = LangGraphOrchestrator()
        print("✅ Orchestrator initialized successfully")
    except Exception as e:
        print(f"❌ Orchestrator initialization failed: {e}")
        return
    
    # Test 1: Incomplete customer request (should trigger clarification)
    print("\n📧 Test 1: Incomplete Customer Request")
    print("-" * 50)
    
    incomplete_email = {
        "email_text": """Hi,

I need shipping rates.

Thanks,
John Doe""",
        "subject": "Shipping Inquiry",
        "sender": "john.doe@company.com",
        "thread_id": "test_enhanced_001",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        result = orchestrator.orchestrate_workflow(incomplete_email)
        
        if result.get('status') == 'success':
            print("✅ Incomplete request processed successfully")
            
            final_state = result.get('final_state', {})
            workflow_history = final_state.get('workflow_history', [])
            next_action = final_state.get('next_action', '')
            
            print(f"   🔄 Workflow Path: {' → '.join(workflow_history)}")
            print(f"   🎯 Next Action: {next_action}")
            
            # Should go to clarification request
            if 'CLARIFICATION_REQUEST' in workflow_history:
                print("   ✅ CLARIFICATION_REQUEST generated - SUCCESS!")
                
                final_response = result.get('final_response', {})
                response_type = final_response.get('response_type', 'unknown')
                print(f"   📧 Response Type: {response_type}")
                
            else:
                print("   ⚠️ Expected CLARIFICATION_REQUEST not generated")
                
        else:
            print(f"❌ Incomplete request failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Complete customer request (should trigger confirmation)
    print("\n📧 Test 2: Complete Customer Request")
    print("-" * 50)
    
    complete_email = {
        "email_text": """Dear SeaRates Team,

I need rates for 2x40HC from Jebel Ali to Mundra.
Cargo: Electronics, weight: 25,000 kg
Ready date: 20th April 2024

Thanks,
Sarah Johnson
TechCorp Solutions""",
        "subject": "Rate Request - Jebel Ali to Mundra",
        "sender": "sarah.johnson@techcorp.com",
        "thread_id": "test_enhanced_002",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        result = orchestrator.orchestrate_workflow(complete_email)
        
        if result.get('status') == 'success':
            print("✅ Complete request processed successfully")
            
            final_state = result.get('final_state', {})
            workflow_history = final_state.get('workflow_history', [])
            next_action = final_state.get('next_action', '')
            
            print(f"   🔄 Workflow Path: {' → '.join(workflow_history)}")
            print(f"   🎯 Next Action: {next_action}")
            
            # Should go to confirmation request
            if 'CONFIRMATION_REQUEST' in workflow_history:
                print("   ✅ CONFIRMATION_REQUEST generated - SUCCESS!")
                
                final_response = result.get('final_response', {})
                response_type = final_response.get('response_type', 'unknown')
                print(f"   📧 Response Type: {response_type}")
                
            else:
                print("   ⚠️ Expected CONFIRMATION_REQUEST not generated")
                
        else:
            print(f"❌ Complete request failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Customer confirmation (should trigger forwarder assignment)
    print("\n📧 Test 3: Customer Confirmation")
    print("-" * 50)
    
    confirmation_email = {
        "email_text": """Yes, I confirm all the shipment details are correct.

Please proceed with forwarder assignment and rate quotes.

Best regards,
Sarah Johnson""",
        "subject": "Re: Rate Request - Jebel Ali to Mundra",
        "sender": "sarah.johnson@techcorp.com",
        "thread_id": "test_enhanced_002",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        result = orchestrator.orchestrate_workflow(confirmation_email)
        
        if result.get('status') == 'success':
            print("✅ Customer confirmation processed successfully")
            
            final_state = result.get('final_state', {})
            workflow_history = final_state.get('workflow_history', [])
            next_action = final_state.get('next_action', '')
            
            print(f"   🔄 Workflow Path: {' → '.join(workflow_history)}")
            print(f"   🎯 Next Action: {next_action}")
            
            # Should go to forwarder assignment
            if 'FORWARDER_ASSIGNMENT' in workflow_history:
                print("   🎯 FORWARDER_ASSIGNMENT DETECTED - SUCCESS!")
                
                # Check forwarder assignment details
                forwarder_assignment = final_state.get('forwarder_assignment', {})
                if forwarder_assignment:
                    print(f"   🚢 Assigned Forwarder: {forwarder_assignment.get('name', 'N/A')}")
                    print(f"   📧 Forwarder Email: {forwarder_assignment.get('email', 'N/A')}")
                
            elif 'FORWARDER_RESPONSE' in workflow_history:
                print("   📧 FORWARDER_RESPONSE generated - SUCCESS!")
                
                # Check for collate email
                final_response = result.get('final_response', {})
                collate_email = final_response.get('collate_email')
                if collate_email:
                    print("   🎯 COLLATE EMAIL TO SALES TEAM - SUCCESS!")
                    print(f"   📋 Subject: {collate_email.get('subject', 'N/A')}")
                    print(f"   🚨 Priority: {collate_email.get('priority', 'N/A')}")
                else:
                    print("   ⚠️ No collate email generated")
                    
            else:
                print("   ⚠️ Expected forwarder assignment not generated")
                
        else:
            print(f"❌ Customer confirmation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Forwarder rate response (should trigger acknowledgment)
    print("\n📧 Test 4: Forwarder Rate Response")
    print("-" * 50)
    
    forwarder_email = {
        "email_text": """Dear SeaRates Team,

Thank you for your rate request for Jebel Ali to Mundra shipment.

Please find our competitive quote below:

**Rate Details:**
- Ocean Freight: USD 1,800 per 40HC
- THC Origin: USD 80
- THC Destination: USD 120
- Documentation: USD 35
- **Total: USD 2,035**

**Service Details:**
- Transit Time: 12 days
- Valid Until: March 15, 2024
- Sailing Date: March 20, 2024
- Container: 40HC
- Commodity: Electronics

Please let us know if you need any clarification.

Best regards,
DHL Global Forwarding
dhl.global.forwarding@logistics.com""",
        "subject": "Rate Quote - Jebel Ali to Mundra (40HC) - Electronics",
        "sender": "dhl.global.forwarding@logistics.com",
        "thread_id": "test_enhanced_003",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        result = orchestrator.orchestrate_workflow(forwarder_email)
        
        if result.get('status') == 'success':
            print("✅ Forwarder response processed successfully")
            
            final_state = result.get('final_state', {})
            workflow_history = final_state.get('workflow_history', [])
            final_response = result.get('final_response', {})
            
            print(f"   🔄 Workflow Path: {' → '.join(workflow_history)}")
            
            # Should go to forwarder response
            if 'FORWARDER_RESPONSE' in workflow_history:
                print("   📧 FORWARDER_RESPONSE generated - SUCCESS!")
                
                response_type = final_response.get('response_type', 'unknown')
                print(f"   📧 Response Type: {response_type}")
                
                # Check for acknowledgment
                if response_type == 'forwarder_acknowledgment':
                    print("   ✅ FORWARDER ACKNOWLEDGMENT generated - SUCCESS!")
                
                # Check for collate email
                collate_email = final_response.get('collate_email')
                if collate_email:
                    print("   🎯 COLLATE EMAIL TO SALES TEAM - SUCCESS!")
                    print(f"   📋 Subject: {collate_email.get('subject', 'N/A')}")
                    print(f"   🚨 Priority: {collate_email.get('priority', 'N/A')}")
                    print(f"   👤 Customer: {collate_email.get('customer_email', 'N/A')}")
                    print(f"   🚢 Forwarder: {collate_email.get('forwarder_email', 'N/A')}")
                else:
                    print("   ⚠️ No collate email generated")
                    
            else:
                print("   ⚠️ Expected forwarder response not generated")
                
        else:
            print(f"❌ Forwarder response failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("✅ ENHANCED WORKFLOW TESTING COMPLETED")
    print("="*80)
    print("\n🎯 EXPECTED BEHAVIOR:")
    print("• Incomplete request → CLARIFICATION_REQUEST")
    print("• Complete request → CONFIRMATION_REQUEST")
    print("• Customer confirmation → FORWARDER_ASSIGNMENT → FORWARDER_RESPONSE")
    print("• Forwarder response → ACKNOWLEDGMENT + COLLATE EMAIL TO SALES")

def main():
    """Run the enhanced workflow test."""
    print("🚀 ENHANCED WORKFLOW TEST SUITE")
    print("="*80)
    
    try:
        test_enhanced_workflow()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 