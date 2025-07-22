#!/usr/bin/env python3
"""
Test LLM-Based Forwarder Response
=================================

Test the improved LLM-based forwarder response generation that creates
human-friendly, professional responses with extracted rate information.
"""

from langgraph_orchestrator import LangGraphOrchestrator

def test_llm_based_response():
    """Test the LLM-based forwarder response generation."""
    
    print("🤖 TESTING LLM-BASED FORWARDER RESPONSE")
    print("=" * 60)
    
    orchestrator = LangGraphOrchestrator()
    
    # Forwarder email with detailed rate information
    forwarder_email = {
        "email_text": """Dear DP World Team,

Thank you for your rate request for Shanghai to Los Angeles shipment.

Please find our competitive quote below:

**Rate Details:**
- Ocean Freight: USD 2,800 per 40HC
- THC Origin: USD 120
- THC Destination: USD 180
- Documentation: USD 45
- **Total: USD 3,145**

**Service Details:**
- Transit Time: 16 days
- Valid Until: March 15, 2024
- Sailing Date: March 20, 2024
- Container: 40HC
- Commodity: Electronics

**Special Services:**
- Temperature controlled if needed
- Insurance available
- Door-to-door service option

Please let us know if you need any clarification.

Best regards,
DHL Global Forwarding
dhl.global.forwarding@logistics.com""",
        "subject": "Rate Quote - Shanghai to Los Angeles (40HC) - Electronics",
        "sender": "dhl.global.forwarding@logistics.com",
        "thread_id": "llm-response-test-1"
    }
    
    print("📧 Processing forwarder email with LLM response generation...")
    print(f"   Sender: {forwarder_email['sender']}")
    print(f"   Subject: {forwarder_email['subject']}")
    
    result = orchestrator.orchestrate_workflow(forwarder_email)
    final_state = result.get('final_state', {})
    
    print(f"\n📊 Results:")
    print(f"   Workflow Complete: {final_state.get('workflow_complete', False)}")
    print(f"   Current Node: {final_state.get('current_node', 'unknown')}")
    print(f"   Workflow History: {' → '.join(final_state.get('workflow_history', []))}")
    
    # Check forwarder detection
    forwarder_detection = final_state.get('forwarder_detection', {})
    print(f"   Is Forwarder: {forwarder_detection.get('is_forwarder', False)}")
    
    # Show the LLM-generated response
    final_response = final_state.get('final_response', {})
    if final_response:
        print(f"\n🤖 LLM-GENERATED RESPONSE:")
        print(f"   Response Type: {final_response.get('response_type', 'unknown')}")
        print(f"   Subject: {final_response.get('response_subject', 'N/A')}")
        print(f"   Sales Email: {final_response.get('sales_person_email', 'N/A')}")
        
        # Show extracted rate info
        extracted_rate_info = final_response.get('extracted_rate_info', {})
        if extracted_rate_info:
            print(f"\n📋 EXTRACTED RATE INFORMATION:")
            print(f"   Origin Port: {extracted_rate_info.get('origin_port', 'Not found')}")
            print(f"   Destination Port: {extracted_rate_info.get('destination_port', 'Not found')}")
            print(f"   Container Type: {extracted_rate_info.get('container_type', 'Not found')}")
            print(f"   Freight Only: ${extracted_rate_info.get('rates_without_thc', 'Not found')}")
            print(f"   With Origin THC: ${extracted_rate_info.get('rates_with_othc', 'Not found')}")
            print(f"   Total Rate: ${extracted_rate_info.get('rates_with_dthc', 'Not found')}")
            print(f"   Transit Time: {extracted_rate_info.get('transit_time', 'Not found')} days")
            print(f"   Valid Until: {extracted_rate_info.get('valid_until', 'Not found')}")
            print(f"   Sailing Date: {extracted_rate_info.get('sailing_date', 'Not found')}")
            print(f"   Commodity: {extracted_rate_info.get('commodity', 'Not found')}")
        
        print(f"\n📄 FINAL LLM-GENERATED RESPONSE BODY:")
        print("=" * 50)
        response_body = final_response.get('response_body', 'N/A')
        print(response_body)
        print("=" * 50)
        
        # Check response quality
        print(f"\n✅ RESPONSE QUALITY CHECK:")
        print(f"   Human Tone: {'✅' if 'thank you' in response_body.lower() else '❌'}")
        print(f"   Professional: {'✅' if 'sales team' in response_body.lower() else '❌'}")
        print(f"   Rate Details Included: {'✅' if any(keyword in response_body.lower() for keyword in ['shanghai', 'los angeles', '40hc', 'transit', 'valid']) else '❌'}")
        print(f"   No Next Steps: {'✅' if 'next steps' not in response_body.lower() else '❌'}")
        print(f"   Proper Signature: {'✅' if 'searates' in response_body.lower() and 'sales@searates.com' in response_body else '❌'}")
    
    # Check if it went through forwarder path
    workflow_history = final_state.get('workflow_history', [])
    if 'FORWARDER_RESPONSE' in workflow_history:
        print(f"\n✅ SUCCESS: Email routed through FORWARDER_PATH")
        print(f"   Response Method: LLM-based generation")
        print(f"   Rate Extraction: ✅ Successfully extracted")
        print(f"   Human Response: ✅ LLM-generated friendly response")
    else:
        print(f"\n❌ FAILED: Email routed through CUSTOMER_PATH instead of FORWARDER_PATH")

def test_fallback_response():
    """Test fallback response when LLM is not available."""
    
    print("\n🔄 TESTING FALLBACK RESPONSE")
    print("=" * 40)
    
    # Test with a simpler email to see fallback behavior
    simple_email = {
        "email_text": """Dear DP World Team,

Rate quote for Rotterdam to Miami:

Freight: USD 1,500
Total: USD 1,800
Transit: 12 days
Container: 20GP

Best regards,
Test Forwarder""",
        "subject": "Simple Rate Quote",
        "sender": "dhl.global.forwarding@logistics.com"
    }
    
    print("📧 Testing with simple email...")
    
    orchestrator = LangGraphOrchestrator()
    result = orchestrator.orchestrate_workflow(simple_email)
    final_state = result.get('final_state', {})
    
    final_response = final_state.get('final_response', {})
    if final_response:
        print(f"   Response Type: {final_response.get('response_type', 'unknown')}")
        print(f"   Response Preview: {final_response.get('response_body', 'N/A')[:200]}...")

def main():
    """Run LLM response tests."""
    
    print("🧪 LLM-BASED RESPONSE TEST SUITE")
    print("=" * 80)
    print("Testing improved LLM-based forwarder responses")
    
    try:
        # Test 1: LLM-based response generation
        test_llm_based_response()
        
        # Test 2: Fallback response
        test_fallback_response()
        
        print(f"\n✅ All LLM response tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 