#!/usr/bin/env python3
"""
Test LangGraph Forwarder Assignment Fix
======================================

This script tests that the LangGraph workflow properly routes customer confirmation to forwarder assignment.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph_orchestrator import LangGraphOrchestrator

def test_langgraph_forwarder_fix():
    """Test that LangGraph properly routes customer confirmation to forwarder assignment."""
    print("\n" + "="*80)
    print("🚀 TESTING LANGGRAPH FORWARDER ASSIGNMENT FIX")
    print("="*80)
    
    # Initialize orchestrator
    print("🔄 Initializing orchestrator...")
    try:
        orchestrator = LangGraphOrchestrator()
        print("✅ Orchestrator initialized successfully")
    except Exception as e:
        print(f"❌ Orchestrator initialization failed: {e}")
        return
    
    # Test customer confirmation email
    print("\n📧 Test: Customer Confirmation Email")
    print("-" * 50)
    
    confirmation_email = {
        "email_text": """Yes, I confirm all the shipment details are correct.

Please proceed with forwarder assignment and rate quotes.

Best regards,
Sarah Johnson""",
        "subject": "Re: Rate Request - Jebel Ali to Mundra",
        "sender": "sarah.johnson@techcorp.com",
        "thread_id": "test_langgraph_fix_001",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        result = orchestrator.orchestrate_workflow(confirmation_email)
        
        if result.get('status') == 'success':
            print("✅ Customer confirmation processed successfully")
            
            final_state = result.get('final_state', {})
            workflow_history = final_state.get('workflow_history', [])
            next_action = final_state.get('next_action', '')
            decision_result = final_state.get('decision_result', {})
            
            print(f"   🔄 Workflow Path: {' → '.join(workflow_history)}")
            print(f"   🎯 Next Action: {next_action}")
            print(f"   🧠 Decision Action: {decision_result.get('next_action', 'N/A')}")
            
            # Check if forwarder assignment was triggered
            if 'FORWARDER_ASSIGNMENT' in workflow_history:
                print("   🎯 FORWARDER_ASSIGNMENT DETECTED - SUCCESS!")
                
                # Check forwarder assignment details
                forwarder_assignment = final_state.get('forwarder_assignment', {})
                if forwarder_assignment:
                    print(f"   🚢 Assigned Forwarder: {forwarder_assignment.get('name', 'N/A')}")
                    print(f"   📧 Forwarder Email: {forwarder_assignment.get('email', 'N/A')}")
                    print(f"   🏢 Company: {forwarder_assignment.get('company', 'N/A')}")
                
            elif 'FORWARDER_RESPONSE' in workflow_history:
                print("   📧 FORWARDER_RESPONSE generated - SUCCESS!")
                
                # Check for collate email
                final_response = result.get('final_response', {})
                collate_email = final_response.get('collate_email')
                if collate_email:
                    print("   🎯 COLLATE EMAIL TO SALES TEAM - SUCCESS!")
                    print(f"   📋 Subject: {collate_email.get('subject', 'N/A')}")
                    print(f"   🚨 Priority: {collate_email.get('priority', 'N/A')}")
                    print(f"   👤 Customer: {collate_email.get('customer_email', 'N/A')}")
                    print(f"   🚢 Forwarder: {collate_email.get('forwarder_email', 'N/A')}")
                else:
                    print("   ⚠️ No collate email generated")
                    
            elif next_action == 'booking_details_confirmed_assign_forwarders':
                print("   🎯 CORRECT DECISION - booking_details_confirmed_assign_forwarders")
                print("   ⚠️ But workflow didn't reach FORWARDER_ASSIGNMENT node")
                
            elif next_action == 'send_confirmation_acknowledgment':
                print("   ❌ INCORRECT DECISION - send_confirmation_acknowledgment")
                print("   ❌ LangGraph fix should have overridden this")
                
            else:
                print(f"   ⚠️ UNEXPECTED ACTION: {next_action}")
                
            # Check conversation state and email classification
            conversation_state = final_state.get('conversation_state', '')
            email_classification = final_state.get('email_classification', {})
            email_type = email_classification.get('email_type', '')
            
            print(f"\n   📊 Analysis:")
            print(f"   Conversation State: {conversation_state}")
            print(f"   Email Type: {email_type}")
            print(f"   Email Classification: {email_classification.get('confidence', 0):.1%}")
            
        else:
            print(f"❌ Customer confirmation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("✅ LANGGRAPH FORWARDER ASSIGNMENT FIX TESTING COMPLETED")
    print("="*80)
    print("\n🎯 EXPECTED BEHAVIOR:")
    print("• Customer confirmation → FORWARDER_ASSIGNMENT → FORWARDER_RESPONSE")
    print("• LangGraph should override NextActionAgent decision")
    print("• Forwarder response should include collate email to sales team")

def main():
    """Run the LangGraph forwarder assignment fix test."""
    print("🚀 LANGGRAPH FORWARDER ASSIGNMENT FIX TEST SUITE")
    print("="*80)
    
    try:
        test_langgraph_forwarder_fix()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 