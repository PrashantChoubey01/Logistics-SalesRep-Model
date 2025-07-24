#!/usr/bin/env python3
"""
Test script for improved forwarder response system.
Tests LLM-generated acknowledgments and sales notifications for all forwarder emails.
"""

import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.forwarder_response_agent import ForwarderResponseAgent

def test_rate_quote_acknowledgment():
    """Test acknowledgment generation for rate quote emails."""
    print("🧪 Testing Rate Quote Acknowledgment")
    print("=" * 60)
    
    # Initialize agent
    forwarder_agent = ForwarderResponseAgent()
    forwarder_agent.load_context()
    
    # Test rate quote email
    rate_quote_email = {
        "email_data": {
            "email_text": """Dear SeaRates Team,

Thank you for your rate request for Jebel Ali to Mundra shipment.

Please find our competitive quote below:

Rate Details:
- Ocean Freight: USD 1,800 per 40HC
- THC Origin: USD 80
- THC Destination: USD 120
- Documentation: USD 35
- Total: USD 2,035

Validity: Valid until Friday, 15th December 2024
Transit Time: 7-10 days

Special Requirements:
- Temperature controlled container required
- Customs clearance assistance needed
- Special handling for fragile items

Terms & Conditions:
- FOB Jebel Ali
- Payment terms: 30 days after delivery
- Insurance coverage included

Additional Instructions:
- Please provide packing list 48 hours before departure
- All documentation must be submitted in advance
- Container inspection required before loading

Please let us know if you need any clarification or have questions.

Best regards,
Logistics Solutions Ltd.
Email: rates@logistics-solutions.com
Phone: +971-4-123-4567""",
            "subject": "Re: Rate Request - Jebel Ali to Mundra",
            "sender": "rates@logistics-solutions.com",
            "thread_id": "thread_12345"
        },
        "forwarder_detection": {
            "is_forwarder": True,
            "forwarder_details": {
                "name": "Logistics Solutions Ltd.",
                "email": "rates@logistics-solutions.com"
            }
        },
        "conversation_state": {
            "conversation_state": "forwarder_rate_received"
        }
    }
    
    print("📧 Testing Rate Quote Email:")
    print(f"Forwarder: {rate_quote_email['forwarder_detection']['forwarder_details']['name']}")
    print(f"Subject: {rate_quote_email['email_data']['subject']}")
    
    # Process the forwarder email
    result = forwarder_agent.process(rate_quote_email)
    
    print(f"\n✅ Rate Quote Response Result:")
    print(f"   Status: {result.get('status', 'unknown')}")
    print(f"   Response Type: {result.get('response_type', 'unknown')}")
    print(f"   Subject: {result.get('response_subject', 'N/A')}")
    
    # Show acknowledgment preview
    print(f"\n📄 Forwarder Acknowledgment Preview:")
    print(f"   {result['response_body'][:300]}...")
    
    # Show sales notification preview
    sales_notification = result.get('sales_notification', {})
    if sales_notification:
        print(f"\n📧 Sales Notification Preview:")
        print(f"   Subject: {sales_notification.get('subject', 'N/A')}")
        print(f"   Priority: {sales_notification.get('priority', 'N/A')}")
        print(f"   Body Preview: {sales_notification.get('body', 'N/A')[:200]}...")
    
    return result

def test_clarification_acknowledgment():
    """Test acknowledgment generation for clarification emails."""
    print("\n🧪 Testing Clarification Acknowledgment")
    print("=" * 60)
    
    forwarder_agent = ForwarderResponseAgent()
    
    # Test clarification email
    clarification_email = {
        "email_data": {
            "email_text": """Dear SeaRates Team,

Thank you for your rate request. We need some clarification before we can provide accurate rates:

1. What is the exact commodity being shipped?
2. Are there any special handling requirements?
3. Do you need door-to-door service or port-to-port only?
4. What is the preferred sailing schedule?
5. Are there any specific documentation requirements?

Please provide these details so we can give you the most competitive rates.

Best regards,
Global Shipping Solutions
clarifications@global-shipping.com""",
            "subject": "Clarification Required - Rate Request",
            "sender": "clarifications@global-shipping.com",
            "thread_id": "thread_67890"
        },
        "forwarder_detection": {
            "is_forwarder": True,
            "forwarder_details": {
                "name": "Global Shipping Solutions",
                "email": "clarifications@global-shipping.com"
            }
        },
        "conversation_state": {
            "conversation_state": "forwarder_clarification_request"
        }
    }
    
    print("📧 Testing Clarification Email:")
    print(f"Forwarder: {clarification_email['forwarder_detection']['forwarder_details']['name']}")
    
    # Process the forwarder email
    result = forwarder_agent.process(clarification_email)
    
    print(f"\n✅ Clarification Response Result:")
    print(f"   Status: {result.get('status', 'unknown')}")
    print(f"   Response Type: {result.get('response_type', 'unknown')}")
    
    # Show acknowledgment preview
    print(f"\n📄 Forwarder Acknowledgment Preview:")
    print(f"   {result['response_body'][:300]}...")
    
    # Show sales notification preview
    sales_notification = result.get('sales_notification', {})
    if sales_notification:
        print(f"\n📧 Sales Notification Preview:")
        print(f"   Subject: {sales_notification.get('subject', 'N/A')}")
        print(f"   Priority: {sales_notification.get('priority', 'N/A')}")
    
    return result

def test_confirmation_acknowledgment():
    """Test acknowledgment generation for confirmation emails."""
    print("\n🧪 Testing Confirmation Acknowledgment")
    print("=" * 60)
    
    forwarder_agent = ForwarderResponseAgent()
    
    # Test confirmation email
    confirmation_email = {
        "email_data": {
            "email_text": """Dear SeaRates Team,

Thank you for the rate quote. We confirm our acceptance of the following:

Route: Shanghai to Los Angeles
Container: 40HC
Rate: USD 2,800 (all inclusive)
Transit Time: 16 days
Sailing Date: March 20, 2024

We would like to proceed with the booking. Please provide the booking confirmation and next steps.

Best regards,
Pacific Logistics
bookings@pacific-logistics.com""",
            "subject": "Rate Confirmation - Shanghai to Los Angeles",
            "sender": "bookings@pacific-logistics.com",
            "thread_id": "thread_11111"
        },
        "forwarder_detection": {
            "is_forwarder": True,
            "forwarder_details": {
                "name": "Pacific Logistics",
                "email": "bookings@pacific-logistics.com"
            }
        },
        "conversation_state": {
            "conversation_state": "forwarder_confirmation"
        }
    }
    
    print("📧 Testing Confirmation Email:")
    print(f"Forwarder: {confirmation_email['forwarder_detection']['forwarder_details']['name']}")
    
    # Process the forwarder email
    result = forwarder_agent.process(confirmation_email)
    
    print(f"\n✅ Confirmation Response Result:")
    print(f"   Status: {result.get('status', 'unknown')}")
    print(f"   Response Type: {result.get('response_type', 'unknown')}")
    
    # Show acknowledgment preview
    print(f"\n📄 Forwarder Acknowledgment Preview:")
    print(f"   {result['response_body'][:300]}...")
    
    # Show sales notification preview
    sales_notification = result.get('sales_notification', {})
    if sales_notification:
        print(f"\n📧 Sales Notification Preview:")
        print(f"   Subject: {sales_notification.get('subject', 'N/A')}")
        print(f"   Priority: {sales_notification.get('priority', 'N/A')}")
    
    return result

def test_forwarder_assignment():
    """Test forwarder assignment acknowledgment generation."""
    print("\n🧪 Testing Forwarder Assignment")
    print("=" * 60)
    
    forwarder_agent = ForwarderResponseAgent()
    
    # Test forwarder assignment
    forwarder_assignment = {
        "assigned_forwarders": [
            {
                "name": "DHL Global Forwarding",
                "email": "rates@dhl.com"
            },
            {
                "name": "Kuehne + Nagel",
                "email": "quotes@kn.com"
            }
        ]
    }
    
    customer_data = {
        "customer_name": "Tech Solutions Inc.",
        "customer_email": "logistics@techsolutions.com",
        "extracted_data": {
            "origin_name": "Shanghai",
            "destination_name": "Los Angeles",
            "container_type": "40HC",
            "commodity": "Electronics"
        }
    }
    
    print("📧 Testing Forwarder Assignment:")
    print(f"Customer: {customer_data['customer_name']}")
    print(f"Forwarders: {len(forwarder_assignment['assigned_forwarders'])}")
    
    # Generate forwarder assignment acknowledgments
    result = forwarder_agent.generate_forwarder_assignment_acknowledgment(
        forwarder_assignment, customer_data
    )
    
    print(f"\n✅ Forwarder Assignment Result:")
    print(f"   Status: {result.get('status', 'unknown')}")
    print(f"   Total Forwarders: {result.get('total_forwarders', 'unknown')}")
    
    # Show acknowledgments
    acknowledgments = result.get('acknowledgments', [])
    for i, ack in enumerate(acknowledgments, 1):
        print(f"\n📄 Forwarder {i} Acknowledgment:")
        print(f"   Forwarder: {ack.get('forwarder_name', 'N/A')}")
        print(f"   Subject: {ack.get('subject', 'N/A')}")
        print(f"   Body Preview: {ack.get('body', 'N/A')[:200]}...")
    
    return result

def main():
    """Run all tests."""
    print("🚀 Improved Forwarder Response System Test")
    print("=" * 60)
    
    try:
        # Test 1: Rate quote acknowledgment
        result1 = test_rate_quote_acknowledgment()
        
        # Test 2: Clarification acknowledgment
        result2 = test_clarification_acknowledgment()
        
        # Test 3: Confirmation acknowledgment
        result3 = test_confirmation_acknowledgment()
        
        # Test 4: Forwarder assignment
        result4 = test_forwarder_assignment()
        
        print("\n🎉 All Tests Completed!")
        print("=" * 60)
        
        # Summary
        print("\n📊 Test Summary:")
        print(f"   ✅ Rate Quote Acknowledgment: {result1.get('status', 'failed')}")
        print(f"   ✅ Clarification Acknowledgment: {result2.get('status', 'failed')}")
        print(f"   ✅ Confirmation Acknowledgment: {result3.get('status', 'failed')}")
        print(f"   ✅ Forwarder Assignment: {result4.get('status', 'failed')}")
        
        # Verify all tests generated acknowledgments
        if (result1.get('status') == 'success' and 
            result2.get('status') == 'success' and 
            result3.get('status') == 'success' and 
            result4.get('status') == 'success'):
            print("   ✅ All tests generated successful acknowledgments")
        else:
            print("   ❌ Some tests failed to generate acknowledgments")
        
        # Verify sales notifications were generated
        sales_notifications = [
            result1.get('sales_notification'),
            result2.get('sales_notification'),
            result3.get('sales_notification')
        ]
        
        if all(sales_notifications):
            print("   ✅ All forwarder emails generated sales notifications")
        else:
            print("   ❌ Some forwarder emails failed to generate sales notifications")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 