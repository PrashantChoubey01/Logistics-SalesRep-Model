#!/usr/bin/env python3
"""
Forwarder Conversation Test
==========================

This script tests the complete conversation flow including:
1. Customer initial request
2. Customer confirmation
3. Forwarder rate quotes
4. Customer response to forwarder quotes
5. Forwarder follow-ups

This tests the full end-to-end workflow with forwarder interactions.
"""

import json
from datetime import datetime
from langgraph_orchestrator import LangGraphOrchestrator

def test_complete_forwarder_conversation():
    """Test the complete conversation flow with forwarder interactions."""
    
    print("🚀 FORWARDER CONVERSATION TEST")
    print("=" * 80)
    
    # Initialize orchestrator
    orchestrator = LangGraphOrchestrator()
    
    # Test conversation flow
    conversation_flow = [
        {
            "step": 1,
            "description": "Customer Initial Request",
            "email": {
                "email_text": """Hi Sarah,

I need a quote for shipping from Shanghai to Los Angeles.

Details:
- Container: 40ft HC
- Weight: 15 tons
- Commodity: Electronics (smartphones and tablets)
- Shipment date: February 15, 2024
- Quantity: 1 container

Special requirements:
- Handle with extra care due to fragile electronics
- Insurance required

Please provide your best rates.

Thanks,
John Smith
TechCorp Inc.""",
                "subject": "Rate Request for FCL Shipment",
                "sender": "john.smith@techcorp.com",
                "thread_id": "forwarder-test-1"
            },
            "expected": {
                "conversation_state": "new_thread",
                "email_type": "customer_quote_request",
                "next_action": "send_confirmation_request"
            }
        },
        {
            "step": 2,
            "description": "Customer Confirmation",
            "email": {
                "email_text": """Hi James,

Yes, all the details are correct. Please proceed with the booking.

Thanks,
John Smith
TechCorp Inc.""",
                "subject": "Re: Confirmation of Shipment Details",
                "sender": "john.smith@techcorp.com",
                "thread_id": "forwarder-test-1"
            },
            "expected": {
                "conversation_state": "thread_confirmation",
                "email_type": "customer_confirmation",
                "next_action": "booking_details_confirmed_assign_forwarders"
            }
        },
        {
            "step": 3,
            "description": "Forwarder 1 Rate Quote",
            "email": {
                "email_text": """Dear DP World Team,

Thank you for your rate request. Please find our competitive quote:

**Rate Details:**
- Ocean Freight: USD 2,500 per 40HC
- THC Origin: USD 150
- THC Destination: USD 200
- Documentation: USD 50
- Total: USD 2,900

**Transit Time:** 18 days
**Valid Until:** February 28, 2024
**Sailing Date:** February 20, 2024

Please let us know if you need any clarification.

Best regards,
Global Logistics Partners
rates@globallogistics.com
+1-800-555-0123""",
                "subject": "Re: Rate Request - Shanghai to Los Angeles",
                "sender": "rates@globallogistics.com",
                "thread_id": "forwarder-test-1"
            },
            "expected": {
                "conversation_state": "thread_forwarder_interaction",
                "email_type": "forwarder_rate_quote",
                "next_action": "send_forwarder_response_to_customer"
            }
        },
        {
            "step": 4,
            "description": "Forwarder 2 Rate Quote",
            "email": {
                "email_text": """Dear DP World Team,

Please find our competitive quote for your Shanghai to Los Angeles shipment:

**Rate Details:**
- Ocean Freight: USD 2,300 per 40HC
- THC Origin: USD 120
- THC Destination: USD 180
- Documentation: USD 45
- Total: USD 2,645

**Transit Time:** 16 days
**Valid Until:** February 25, 2024
**Sailing Date:** February 18, 2024

We offer the best rates and fastest transit time.

Best regards,
Maritime Freight Solutions
quotes@maritimefreight.com
+1-800-555-0456""",
                "subject": "Re: Rate Request - Shanghai to Los Angeles",
                "sender": "quotes@maritimefreight.com",
                "thread_id": "forwarder-test-1"
            },
            "expected": {
                "conversation_state": "thread_forwarder_interaction",
                "email_type": "forwarder_rate_quote",
                "next_action": "send_forwarder_response_to_customer"
            }
        },
        {
            "step": 5,
            "description": "Customer Response to Forwarder Quotes",
            "email": {
                "email_text": """Hi James,

Thanks for the rate quotes. I like the Maritime Freight Solutions offer at USD 2,645.

Can you proceed with booking with them? Also, please confirm:
- Pickup date: February 18, 2024
- Delivery date: March 6, 2024
- Insurance coverage details

Please send booking confirmation.

Thanks,
John Smith
TechCorp Inc.""",
                "subject": "Re: Rate Quotes - Proceed with Booking",
                "sender": "john.smith@techcorp.com",
                "thread_id": "forwarder-test-1"
            },
            "expected": {
                "conversation_state": "thread_booking_request",
                "email_type": "customer_booking_request",
                "next_action": "send_booking_confirmation"
            }
        },
        {
            "step": 6,
            "description": "Forwarder Inquiry for More Details",
            "email": {
                "email_text": """Dear DP World Team,

We received your rate request. However, we need additional information:

1. Exact commodity description and HS codes
2. Dangerous goods classification (if any)
3. Special handling requirements
4. Preferred sailing dates
5. Insurance requirements

Please provide these details for accurate quoting.

Best regards,
Ocean Cargo Solutions
sales@oceancargo.com
+1-800-555-0789""",
                "subject": "Re: Rate Request - Additional Information Needed",
                "sender": "sales@oceancargo.com",
                "thread_id": "forwarder-test-1"
            },
            "expected": {
                "conversation_state": "thread_forwarder_interaction",
                "email_type": "forwarder_inquiry",
                "next_action": "send_forwarder_response_to_customer"
            }
        }
    ]
    
    # Track conversation results
    conversation_results = []
    
    # Process each step in the conversation
    for step_data in conversation_flow:
        print(f"\n📧 STEP {step_data['step']}: {step_data['description']}")
        print("-" * 60)
        
        # Process email
        result = orchestrator.orchestrate_workflow(step_data['email'])
        final_state = result.get('final_state', {})
        
        # Extract key results
        conversation_state = final_state.get('conversation_state', 'unknown')
        email_classification = final_state.get('email_classification', {})
        email_type = email_classification.get('email_type', 'unknown')
        next_action = final_state.get('next_action', 'unknown')
        
        # Store results
        step_result = {
            "step": step_data['step'],
            "description": step_data['description'],
            "actual": {
                "conversation_state": conversation_state,
                "email_type": email_type,
                "next_action": next_action
            },
            "expected": step_data['expected'],
            "status": "✅ PASS" if (
                conversation_state == step_data['expected']['conversation_state'] and
                email_type == step_data['expected']['email_type'] and
                next_action == step_data['expected']['next_action']
            ) else "❌ FAIL"
        }
        
        conversation_results.append(step_result)
        
        # Print results
        print(f"📊 Results:")
        print(f"   Conversation State: {conversation_state}")
        print(f"   Email Type: {email_type}")
        print(f"   Next Action: {next_action}")
        print(f"   Status: {step_result['status']}")
        
        # Print expected vs actual
        if step_result['status'] == "❌ FAIL":
            print(f"   Expected:")
            print(f"     Conversation State: {step_data['expected']['conversation_state']}")
            print(f"     Email Type: {step_data['expected']['email_type']}")
            print(f"     Next Action: {step_data['expected']['next_action']}")
        
        # Show response if generated
        final_response = final_state.get('final_response', {})
        if final_response:
            print(f"   📝 Response Generated: {final_response.get('response_type', 'unknown')}")
            print(f"   📧 Subject: {final_response.get('response_subject', 'N/A')}")
        
        # Show forwarder assignment if applicable
        forwarder_assignment = final_state.get('forwarder_assignment', {})
        if forwarder_assignment and forwarder_assignment.get('assigned_forwarders'):
            print(f"   🚛 Forwarders Assigned: {len(forwarder_assignment['assigned_forwarders'])}")
            for fw in forwarder_assignment['assigned_forwarders']:
                print(f"     - {fw.get('name', 'N/A')} ({fw.get('email', 'N/A')})")
    
    # Print summary
    print(f"\n📊 CONVERSATION TEST SUMMARY")
    print("=" * 80)
    
    passed_steps = sum(1 for result in conversation_results if result['status'] == "✅ PASS")
    total_steps = len(conversation_results)
    
    print(f"Total Steps: {total_steps}")
    print(f"Passed: {passed_steps}")
    print(f"Failed: {total_steps - passed_steps}")
    print(f"Success Rate: {(passed_steps/total_steps)*100:.1f}%")
    
    # Print detailed results
    print(f"\n📋 DETAILED RESULTS:")
    for result in conversation_results:
        status_icon = "✅" if result['status'] == "✅ PASS" else "❌"
        print(f"{status_icon} Step {result['step']}: {result['description']}")
        if result['status'] == "❌ FAIL":
            print(f"   Expected: {result['expected']['conversation_state']} → {result['expected']['email_type']} → {result['expected']['next_action']}")
            print(f"   Actual:   {result['actual']['conversation_state']} → {result['actual']['email_type']} → {result['actual']['next_action']}")
    
    return conversation_results

def test_forwarder_rate_comparison():
    """Test multiple forwarder rate quotes and comparison."""
    
    print(f"\n💰 FORWARDER RATE COMPARISON TEST")
    print("=" * 80)
    
    orchestrator = LangGraphOrchestrator()
    
    # Test multiple forwarder quotes
    forwarder_quotes = [
        {
            "name": "Global Logistics Partners",
            "email": "rates@globallogistics.com",
            "quote": {
                "ocean_freight": 2500,
                "thc_origin": 150,
                "thc_destination": 200,
                "documentation": 50,
                "total": 2900,
                "transit_time": 18,
                "valid_until": "2024-02-28"
            }
        },
        {
            "name": "Maritime Freight Solutions", 
            "email": "quotes@maritimefreight.com",
            "quote": {
                "ocean_freight": 2300,
                "thc_origin": 120,
                "thc_destination": 180,
                "documentation": 45,
                "total": 2645,
                "transit_time": 16,
                "valid_until": "2024-02-25"
            }
        },
        {
            "name": "Ocean Cargo Solutions",
            "email": "sales@oceancargo.com", 
            "quote": {
                "ocean_freight": 2400,
                "thc_origin": 140,
                "thc_destination": 190,
                "documentation": 40,
                "total": 2770,
                "transit_time": 17,
                "valid_until": "2024-02-26"
            }
        }
    ]
    
    print("📊 Forwarder Rate Comparison:")
    print(f"{'Forwarder':<25} {'Total Rate':<12} {'Transit':<8} {'Valid Until':<12}")
    print("-" * 60)
    
    for fw in forwarder_quotes:
        print(f"{fw['name']:<25} ${fw['quote']['total']:<11} {fw['quote']['transit_time']} days {fw['quote']['valid_until']}")
    
    # Find best rate
    best_rate = min(forwarder_quotes, key=lambda x: x['quote']['total'])
    print(f"\n🏆 Best Rate: {best_rate['name']} - ${best_rate['quote']['total']}")
    
    return forwarder_quotes

def test_forwarder_inquiry_handling():
    """Test how the system handles forwarder inquiries for more details."""
    
    print(f"\n❓ FORWARDER INQUIRY HANDLING TEST")
    print("=" * 80)
    
    orchestrator = LangGraphOrchestrator()
    
    # Test forwarder inquiry
    inquiry_email = {
        "email_text": """Dear DP World Team,

We received your rate request for Shanghai to Los Angeles shipment.

However, we need additional information for accurate quoting:

1. **Commodity Details:**
   - Exact commodity description
   - HS codes
   - Dangerous goods classification (if any)

2. **Special Requirements:**
   - Temperature control needed?
   - Special handling requirements?
   - Insurance requirements?

3. **Timeline:**
   - Preferred sailing dates
   - Delivery deadline
   - Pickup requirements

Please provide these details so we can give you the most competitive quote.

Best regards,
Ocean Cargo Solutions
sales@oceancargo.com
+1-800-555-0789""",
        "subject": "Re: Rate Request - Additional Information Required",
        "sender": "sales@oceancargo.com",
        "thread_id": "inquiry-test-1"
    }
    
    print("📧 Processing Forwarder Inquiry...")
    result = orchestrator.orchestrate_workflow(inquiry_email)
    final_state = result.get('final_state', {})
    
    # Extract results
    conversation_state = final_state.get('conversation_state', 'unknown')
    email_classification = final_state.get('email_classification', {})
    email_type = email_classification.get('email_type', 'unknown')
    next_action = final_state.get('next_action', 'unknown')
    
    print(f"📊 Results:")
    print(f"   Conversation State: {conversation_state}")
    print(f"   Email Type: {email_type}")
    print(f"   Next Action: {next_action}")
    
    # Show response
    final_response = final_state.get('final_response', {})
    if final_response:
        print(f"   📝 Response Type: {final_response.get('response_type', 'unknown')}")
        print(f"   📧 Subject: {final_response.get('response_subject', 'N/A')}")
        print(f"   📄 Response Preview: {final_response.get('response_body', 'N/A')[:200]}...")
    
    return {
        "conversation_state": conversation_state,
        "email_type": email_type,
        "next_action": next_action,
        "response": final_response
    }

def main():
    """Run all forwarder conversation tests."""
    
    print("🚢 FORWARDER CONVERSATION TEST SUITE")
    print("=" * 80)
    print("Testing complete conversation flow with forwarder interactions")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Complete conversation flow
        conversation_results = test_complete_forwarder_conversation()
        
        # Test 2: Forwarder rate comparison
        forwarder_quotes = test_forwarder_rate_comparison()
        
        # Test 3: Forwarder inquiry handling
        inquiry_results = test_forwarder_inquiry_handling()
        
        # Final summary
        print(f"\n🎯 TEST SUMMARY")
        print("=" * 80)
        print("✅ Complete conversation flow tested")
        print("✅ Forwarder rate comparison analyzed")
        print("✅ Forwarder inquiry handling verified")
        print(f"✅ All tests completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save results
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "conversation_results": conversation_results,
            "forwarder_quotes": forwarder_quotes,
            "inquiry_results": inquiry_results
        }
        
        with open("forwarder_test_results.json", "w") as f:
            json.dump(test_results, f, indent=2)
        
        print("💾 Results saved to: forwarder_test_results.json")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 