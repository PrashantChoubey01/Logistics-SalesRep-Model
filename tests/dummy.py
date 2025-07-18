"""Comprehensive test suite for all AI logistics system use cases."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'agents'))

from agents.langgraph_orchestrator import run_workflow
import json

def test_use_case_1_vague_non_logistics():
    """Use Case 1: Vague or non-logistics inquiry → Escalation"""
    print("=" * 80)
    print("USE CASE 1: VAGUE/NON-LOGISTICS INQUIRY")
    print("=" * 80)
    
    message_thread = [
        {
            "sender": "info@startupcompany.com",
            "timestamp": "2025-01-20 10:00:00",
            "body": """Hi,

I'm looking for information about your services. Can you tell me more about what you do?

Thanks,
Sarah Johnson
Startup Company"""
        }
    ]
    
    subject = "General Inquiry"
    thread_id = "use-case-1-vague"
    
    print(f"Subject: {subject}")
    print(f"From: {message_thread[0]['sender']}")
    print(f"Body: {message_thread[0]['body'][:100]}...")
    print("\nExpected Flow: Classification (non_logistics) → Escalation → SeaRates Info Response")
    print("-" * 80)
    
    try:
        result = run_workflow(message_thread, subject, thread_id)
        
        print("RESULTS:")
        print(f"Classification: {result.get('classification', {}).get('email_type', 'unknown')}")
        print(f"Confidence: {result.get('classification', {}).get('confidence', 0.0):.2f}")
        print(f"Escalation Triggered: {'escalation' in result}")
        print(f"Response Status: {result.get('response', {}).get('status', 'unknown')}")
        
        if 'response' in result:
            print(f"\nResponse Subject: {result['response'].get('response_subject', 'N/A')}")
            print(f"Response Preview: {result['response'].get('response_body', '')[:200]}...")
        
        print("✅ Use Case 1 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Use Case 1 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_use_case_2_complete_logistics_request():
    """Use Case 2: Complete logistics request → Full workflow"""
    print("\n" + "=" * 80)
    print("USE CASE 2: COMPLETE LOGISTICS REQUEST")
    print("=" * 80)
    
    message_thread = [
        {
            "sender": "john.smith@techcorp.com",
            "timestamp": "2025-01-20 11:00:00",
            "body": """Dear SeaRates Team,

I hope this email finds you well. We are looking to ship electronics from Shanghai to Long Beach, California.

Shipment Details:
- Container Type: 2x40ft containers
- Cargo: Electronics (TVs, smartphones, laptops)
- Total Weight: 45 metric tons
- Shipment Type: FCL
- Ready Date: February 15th, 2025
- Incoterms: FOB Shanghai

Please provide us with:
1. Rate quote for the above shipment
2. Transit time
3. Documentation requirements
4. Any additional charges

We would appreciate a quick response as we need to finalize our logistics arrangements.

Best regards,
John Smith
Logistics Manager
TechCorp Industries
Phone: +1-555-0123
Email: john.smith@techcorp.com"""
        }
    ]
    
    subject = "Rate Request - Shanghai to Long Beach Electronics Shipment"
    thread_id = "use-case-2-logistics-request"
    
    print(f"Subject: {subject}")
    print(f"From: {message_thread[0]['sender']}")
    print(f"Body Preview: {message_thread[0]['body'][:100]}...")
    print("\nExpected Flow: Classification → Extraction → Validation → Rate Recommendation → Response")
    print("-" * 80)
    
    try:
        result = run_workflow(message_thread, subject, thread_id)
        
        print("RESULTS:")
        print(f"Classification: {result.get('classification', {}).get('email_type', 'unknown')}")
        print(f"Confidence: {result.get('classification', {}).get('confidence', 0.0):.2f}")
        print(f"Extraction Success: {'extraction' in result}")
        print(f"Validation Success: {'validation' in result}")
        print(f"Rate Available: {'rate' in result and result['rate']}")
        print(f"Forwarder Assigned: {result.get('forwarder_assignment', {}).get('assigned_forwarder', 'None')}")
        print(f"Response Status: {result.get('response', {}).get('status', 'unknown')}")
        
        if 'extraction' in result:
            extraction = result['extraction']
            print(f"\nExtracted Data:")
            print(f"  Origin: {extraction.get('origin', 'N/A')}")
            print(f"  Destination: {extraction.get('destination', 'N/A')}")
            print(f"  Container Type: {extraction.get('container_type', 'N/A')}")
            print(f"  Quantity: {extraction.get('quantity', 'N/A')}")
            print(f"  Weight: {extraction.get('weight', 'N/A')}")
            print(f"  Shipment Date: {extraction.get('shipment_date', 'N/A')}")
        
        if 'response' in result:
            print(f"\nResponse Subject: {result['response'].get('response_subject', 'N/A')}")
            print(f"Response Preview: {result['response'].get('response_body', '')[:200]}...")
        
        print("✅ Use Case 2 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Use Case 2 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_use_case_3_customer_confirmation():
    """Use Case 3: Customer confirmation → Confirmation detection + email sending"""
    print("\n" + "=" * 80)
    print("USE CASE 3: CUSTOMER CONFIRMATION")
    print("=" * 80)
    
    message_thread = [
        {
            "sender": "john.smith@techcorp.com",
            "timestamp": "2025-01-20 14:00:00",
            "body": """Hi SeaRates Team,

Thank you for the quote. We accept your rate of $2,800 for the 2x40ft containers from Shanghai to Long Beach.

Please proceed with the booking. Here are our details:

Company: TechCorp Industries
Contact: John Smith
Email: john.smith@techcorp.com
Phone: +1-555-0123

We confirm the following details:
- Origin: Shanghai
- Destination: Long Beach
- Container Type: 2x40ft
- Cargo: Electronics
- Ready Date: February 15th, 2025

Please send us the booking confirmation and next steps.

Best regards,
John Smith
TechCorp Industries"""
        }
    ]
    
    subject = "Re: Rate Quote - Shanghai to Long Beach - ACCEPTED"
    thread_id = "use-case-3-confirmation"
    
    print(f"Subject: {subject}")
    print(f"From: {message_thread[0]['sender']}")
    print(f"Body Preview: {message_thread[0]['body'][:100]}...")
    print("\nExpected Flow: Classification → Confirmation Detection → Response Generation → Email Sending")
    print("-" * 80)
    
    try:
        result = run_workflow(message_thread, subject, thread_id)
        
        print("RESULTS:")
        print(f"Classification: {result.get('classification', {}).get('email_type', 'unknown')}")
        print(f"Confidence: {result.get('classification', {}).get('confidence', 0.0):.2f}")
        print(f"Confirmation Detected: {result.get('confirmation', {}).get('is_confirmation', False)}")
        print(f"Confirmation Type: {result.get('confirmation', {}).get('confirmation_type', 'unknown')}")
        print(f"Response Status: {result.get('response', {}).get('status', 'unknown')}")
        print(f"Customer Email Sent: {'customer_email' in result}")
        print(f"Forwarder Email Sent: {'forwarder_email' in result}")
        
        if 'confirmation' in result:
            confirmation = result['confirmation']
            print(f"\nConfirmation Details:")
            print(f"  Type: {confirmation.get('confirmation_type', 'N/A')}")
            print(f"  Details: {confirmation.get('confirmation_details', 'N/A')}")
            print(f"  Key Phrases: {confirmation.get('key_phrases', [])}")
        
        if 'response' in result:
            print(f"\nResponse Subject: {result['response'].get('response_subject', 'N/A')}")
            print(f"Response Preview: {result['response'].get('response_body', '')[:200]}...")
        
        print("✅ Use Case 3 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Use Case 3 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_use_case_4_incomplete_logistics_request():
    """Use Case 4: Incomplete logistics request → Clarification needed"""
    print("\n" + "=" * 80)
    print("USE CASE 4: INCOMPLETE LOGISTICS REQUEST")
    print("=" * 80)
    
    message_thread = [
        {
            "sender": "maria.garcia@fashionco.com",
            "timestamp": "2025-01-20 15:00:00",
            "body": """Hello SeaRates,

We need to ship some textiles from Mumbai to Rotterdam.

Can you provide a quote?

Thanks,
Maria Garcia
Fashion Co."""
        }
    ]
    
    subject = "Shipping Quote Request"
    thread_id = "use-case-4-incomplete"
    
    print(f"Subject: {subject}")
    print(f"From: {message_thread[0]['sender']}")
    print(f"Body Preview: {message_thread[0]['body'][:100]}...")
    print("\nExpected Flow: Classification → Extraction → Validation → Clarification Needed")
    print("-" * 80)
    
    try:
        result = run_workflow(message_thread, subject, thread_id)
        
        print("RESULTS:")
        print(f"Classification: {result.get('classification', {}).get('email_type', 'unknown')}")
        print(f"Confidence: {result.get('classification', {}).get('confidence', 0.0):.2f}")
        print(f"Extraction Success: {'extraction' in result}")
        print(f"Clarification Needed: {result.get('clarification_needed', False)}")
        print(f"Missing Fields: {result.get('missing_fields', [])}")
        print(f"Response Status: {result.get('response', {}).get('status', 'unknown')}")
        
        if 'extraction' in result:
            extraction = result['extraction']
            print(f"\nExtracted Data:")
            print(f"  Origin: {extraction.get('origin', 'N/A')}")
            print(f"  Destination: {extraction.get('destination', 'N/A')}")
            print(f"  Container Type: {extraction.get('container_type', 'N/A')}")
            print(f"  Quantity: {extraction.get('quantity', 'N/A')}")
            print(f"  Weight: {extraction.get('weight', 'N/A')}")
        
        if 'response' in result:
            print(f"\nResponse Subject: {result['response'].get('response_subject', 'N/A')}")
            print(f"Response Preview: {result['response'].get('response_body', '')[:200]}...")
        
        print("✅ Use Case 4 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Use Case 4 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_use_case_5_forwarder_response():
    """Use Case 5: Forwarder response → Different handling"""
    print("\n" + "=" * 80)
    print("USE CASE 5: FORWARDER RESPONSE")
    print("=" * 80)
    
    message_thread = [
        {
            "sender": "rates@globalfreight.com",
            "timestamp": "2025-01-20 16:00:00",
            "body": """Dear Customer,

Thank you for your inquiry. Please find our rate quote below:

Route: Shanghai to Long Beach
Container: 2x40ft FCL
Rate: $2,800 USD per container
Validity: Until January 25, 2025
Transit Time: 12-14 days

Additional Services:
- Documentation: $150
- Insurance: $200
- Customs Clearance: $300

Total: $5,900 USD

Please let us know if you would like to proceed with this booking.

Best regards,
Global Freight Solutions
rates@globalfreight.com"""
        }
    ]
    
    subject = "Re: Rate Quote - Shanghai to Long Beach"
    thread_id = "use-case-5-forwarder"
    
    print(f"Subject: {subject}")
    print(f"From: {message_thread[0]['sender']}")
    print(f"Body Preview: {message_thread[0]['body'][:100]}...")
    print("\nExpected Flow: Classification (forwarder_response) → Specialized Handling")
    print("-" * 80)
    
    try:
        result = run_workflow(message_thread, subject, thread_id)
        
        print("RESULTS:")
        print(f"Classification: {result.get('classification', {}).get('email_type', 'unknown')}")
        print(f"Confidence: {result.get('classification', {}).get('confidence', 0.0):.2f}")
        print(f"Response Status: {result.get('response', {}).get('status', 'unknown')}")
        
        if 'response' in result:
            print(f"\nResponse Subject: {result['response'].get('response_subject', 'N/A')}")
            print(f"Response Preview: {result['response'].get('response_body', '')[:200]}...")
        
        print("✅ Use Case 5 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Use Case 5 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_use_case_6_clarification_reply():
    """Use Case 6: Customer clarification reply"""
    print("\n" + "=" * 80)
    print("USE CASE 6: CLARIFICATION REPLY")
    print("=" * 80)
    
    message_thread = [
        {
            "sender": "maria.garcia@fashionco.com",
            "timestamp": "2025-01-20 17:00:00",
            "body": """Hi SeaRates Team,

Thank you for your questions. Here are the additional details:

- Container Type: 1x40ft container
- Cargo: Textiles (cotton fabric)
- Weight: 25 tons
- Volume: 67 CBM
- Ready Date: March 1st, 2025
- Incoterms: FOB Mumbai

Please provide the updated quote with these details.

Best regards,
Maria Garcia
Fashion Co."""
        }
    ]
    
    subject = "Re: Additional Information Required"
    thread_id = "use-case-6-clarification"
    
    print(f"Subject: {subject}")
    print(f"From: {message_thread[0]['sender']}")
    print(f"Body Preview: {message_thread[0]['body'][:100]}...")
    print("\nExpected Flow: Classification (clarification_reply) → Complete Processing")
    print("-" * 80)
    
    try:
        result = run_workflow(message_thread, subject, thread_id)
        
        print("RESULTS:")
        print(f"Classification: {result.get('classification', {}).get('email_type', 'unknown')}")
        print(f"Confidence: {result.get('classification', {}).get('confidence', 0.0):.2f}")
        print(f"Extraction Success: {'extraction' in result}")
        print(f"Validation Success: {'validation' in result}")
        print(f"Response Status: {result.get('response', {}).get('status', 'unknown')}")
        
        if 'extraction' in result:
            extraction = result['extraction']
            print(f"\nExtracted Data:")
            print(f"  Origin: {extraction.get('origin', 'N/A')}")
            print(f"  Destination: {extraction.get('destination', 'N/A')}")
            print(f"  Container Type: {extraction.get('container_type', 'N/A')}")
            print(f"  Quantity: {extraction.get('quantity', 'N/A')}")
            print(f"  Weight: {extraction.get('weight', 'N/A')}")
            print(f"  Volume: {extraction.get('volume', 'N/A')}")
        
        if 'response' in result:
            print(f"\nResponse Subject: {result['response'].get('response_subject', 'N/A')}")
            print(f"Response Preview: {result['response'].get('response_body', '')[:200]}...")
        
        print("✅ Use Case 6 completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Use Case 6 failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_use_cases():
    """Run all use case tests"""
    print("🚀 COMPREHENSIVE AI LOGISTICS SYSTEM USE CASE TESTING")
    print("=" * 80)
    
    use_cases = [
        ("Vague/Non-Logistics Inquiry", test_use_case_1_vague_non_logistics),
        ("Complete Logistics Request", test_use_case_2_complete_logistics_request),
        ("Customer Confirmation", test_use_case_3_customer_confirmation),
        ("Incomplete Logistics Request", test_use_case_4_incomplete_logistics_request),
        ("Forwarder Response", test_use_case_5_forwarder_response),
        ("Clarification Reply", test_use_case_6_clarification_reply)
    ]
    
    results = []
    
    for i, (name, test_func) in enumerate(use_cases, 1):
        print(f"\n{'='*20} TESTING USE CASE {i}: {name} {'='*20}")
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Use case {i} failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {name}")
        if success:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} use cases passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All use cases passed! System is working correctly.")
    else:
        print("⚠️ Some use cases failed. Check the logs above for details.")

if __name__ == "__main__":
    run_all_use_cases()