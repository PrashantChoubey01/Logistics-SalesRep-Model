#!/usr/bin/env python3
"""
Quick Forwarder Test
===================

Quick test script for individual forwarder conversation steps.
Use this for faster testing and debugging.
"""

from langgraph_orchestrator import LangGraphOrchestrator

def test_forwarder_rate_quote():
    """Test forwarder rate quote processing."""
    
    print("💰 TESTING FORWARDER RATE QUOTE")
    print("=" * 50)
    
    orchestrator = LangGraphOrchestrator()
    
    # Test forwarder rate quote
    forwarder_email = {
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
        "thread_id": "quick-test-1"
    }
    
    result = orchestrator.orchestrate_workflow(forwarder_email)
    final_state = result.get('final_state', {})
    
    print(f"📊 Results:")
    print(f"   Conversation State: {final_state.get('conversation_state', 'unknown')}")
    print(f"   Email Type: {final_state.get('email_classification', {}).get('email_type', 'unknown')}")
    print(f"   Next Action: {final_state.get('next_action', 'unknown')}")
    
    # Show response
    final_response = final_state.get('final_response', {})
    if final_response:
        print(f"   📝 Response Type: {final_response.get('response_type', 'unknown')}")
        print(f"   📧 Subject: {final_response.get('response_subject', 'N/A')}")
        print(f"   📄 Response Preview: {final_response.get('response_body', 'N/A')[:300]}...")

def test_forwarder_inquiry():
    """Test forwarder inquiry for more details."""
    
    print("\n❓ TESTING FORWARDER INQUIRY")
    print("=" * 50)
    
    orchestrator = LangGraphOrchestrator()
    
    # Test forwarder inquiry
    inquiry_email = {
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
        "thread_id": "quick-test-2"
    }
    
    result = orchestrator.orchestrate_workflow(inquiry_email)
    final_state = result.get('final_state', {})
    
    print(f"📊 Results:")
    print(f"   Conversation State: {final_state.get('conversation_state', 'unknown')}")
    print(f"   Email Type: {final_state.get('email_classification', {}).get('email_type', 'unknown')}")
    print(f"   Next Action: {final_state.get('next_action', 'unknown')}")
    
    # Show response
    final_response = final_state.get('final_response', {})
    if final_response:
        print(f"   📝 Response Type: {final_response.get('response_type', 'unknown')}")
        print(f"   📧 Subject: {final_response.get('response_subject', 'N/A')}")
        print(f"   📄 Response Preview: {final_response.get('response_body', 'N/A')[:300]}...")

def test_customer_booking_request():
    """Test customer booking request after receiving forwarder quotes."""
    
    print("\n📋 TESTING CUSTOMER BOOKING REQUEST")
    print("=" * 50)
    
    orchestrator = LangGraphOrchestrator()
    
    # Test customer booking request
    booking_email = {
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
        "thread_id": "quick-test-3"
    }
    
    result = orchestrator.orchestrate_workflow(booking_email)
    final_state = result.get('final_state', {})
    
    print(f"📊 Results:")
    print(f"   Conversation State: {final_state.get('conversation_state', 'unknown')}")
    print(f"   Email Type: {final_state.get('email_classification', {}).get('email_type', 'unknown')}")
    print(f"   Next Action: {final_state.get('next_action', 'unknown')}")
    
    # Show response
    final_response = final_state.get('final_response', {})
    if final_response:
        print(f"   📝 Response Type: {final_response.get('response_type', 'unknown')}")
        print(f"   📧 Subject: {final_response.get('response_subject', 'N/A')}")
        print(f"   📄 Response Preview: {final_response.get('response_body', 'N/A')[:300]}...")

def main():
    """Run quick forwarder tests."""
    
    print("🚢 QUICK FORWARDER TESTS")
    print("=" * 50)
    
    # Test 1: Forwarder rate quote
    test_forwarder_rate_quote()
    
    # Test 2: Forwarder inquiry
    test_forwarder_inquiry()
    
    # Test 3: Customer booking request
    test_customer_booking_request()
    
    print("\n✅ Quick tests completed!")

if __name__ == "__main__":
    main() 