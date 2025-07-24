#!/usr/bin/env python3
"""
Test Script for ConversationStateAgent
=====================================

This script tests the ConversationStateAgent with various email scenarios
to ensure it correctly identifies conversation states and determines next actions.
"""

import sys
import os
import json
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.conversation_state_agent import ConversationStateAgent

def print_test_header(test_name):
    """Print a formatted test header."""
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def print_test_result(result, expected_state=None):
    """Print formatted test results."""
    print(f"\n📊 TEST RESULTS:")
    print(f"   Status: {'✅ SUCCESS' if result.get('status') == 'success' else '❌ FAILED'}")
    
    if result.get('status') == 'success':
        conversation_state = result.get('conversation_state', 'unknown')
        confidence = result.get('confidence_score', 0.0)
        next_action = result.get('next_action', 'unknown')
        sales_handoff = result.get('sales_handoff_needed', False)
        latest_sender = result.get('latest_sender', 'unknown')
        reasoning = result.get('reasoning', 'No reasoning provided')
        
        print(f"   Conversation State: {conversation_state}")
        print(f"   Confidence Score: {confidence:.2f}")
        print(f"   Next Action: {next_action}")
        print(f"   Sales Handoff Needed: {sales_handoff}")
        print(f"   Latest Sender: {latest_sender}")
        
        if expected_state:
            if conversation_state == expected_state:
                print(f"   ✅ State Prediction: CORRECT")
            else:
                print(f"   ❌ State Prediction: INCORRECT (expected: {expected_state})")
        
        print(f"\n🔍 Reasoning: {reasoning}")
        
        # Show key indicators if available
        key_indicators = result.get('key_indicators', [])
        if key_indicators:
            print(f"\n🔑 Key Indicators: {', '.join(key_indicators)}")
            
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")

def test_conversation_state_agent():
    """Main test function for ConversationStateAgent."""
    print("🚀 Starting ConversationStateAgent Tests")
    print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize the agent
    agent = ConversationStateAgent()
    
    # Load context
    print("\n📚 Loading agent context...")
    if not agent.load_context():
        print("❌ Failed to load agent context")
        return False
    
    print("✅ Agent context loaded successfully")
    
    # Test cases
    test_cases = [
        {
            "name": "New Logistics Request - FCL",
            "subject": "Need quote for FCL shipment from China to USA",
            "email_text": """
Hi there,

I need to ship 2x40ft containers from Shanghai to Long Beach. 
Ready date is February 15th, 2024.
Commodity: Electronics
Weight: 25 tons per container

Please provide rates and transit time.

Best regards,
John Smith
ABC Company
            """,
            "expected_state": "new_thread"
        },
        
        {
            "name": "New Logistics Request - LCL",
            "subject": "LCL shipment quote needed",
            "email_text": """
Hello,

We need to ship 5 pallets of textiles from Mumbai to London.
Volume: 15 CBM
Weight: 2.5 tons
Ready date: March 1st, 2024

Please provide LCL rates and schedule.

Thanks,
Sarah Johnson
Textile Exports Ltd
            """,
            "expected_state": "new_thread"
        },
        
        {
            "name": "Clarification Response",
            "subject": "Re: Clarification needed for your shipment",
            "email_text": """
Hi,

Thanks for asking. Here are the details:

Origin: Shanghai, China
Destination: Long Beach, USA
Container Type: 40ft HC
Quantity: 2 containers
Weight: 25 tons each
Commodity: Electronics
Ready Date: February 15th, 2024

Please let me know if you need anything else.

Best regards,
John Smith
            """,
            "expected_state": "thread_clarification"
        },
        
        {
            "name": "Confirmation Response",
            "subject": "Re: Please confirm your shipment details",
            "email_text": """
Hi,

Yes, all the details are correct:
- Origin: Shanghai
- Destination: Long Beach  
- 2x40ft containers
- Electronics
- February 15th ready date

Please proceed with the booking.

Thanks,
John Smith
            """,
            "expected_state": "thread_confirmation"
        },
        
        {
            "name": "Forwarder Rate Response",
            "subject": "Re: Rate Request - Shanghai to Long Beach",
            "email_text": """
Dear Logistics Team,

Thank you for your rate request. Here are our rates:

Route: Shanghai to Long Beach
Rate: USD 2,500 per 40ft container
Transit Time: 25 days
Valid Until: January 15th, 2024
Free Time: 7 days

Please let us know if you need any clarification.

Best regards,
Global Shipping Co.
            """,
            "expected_state": "thread_forwarder_interaction"
        },
        
        {
            "name": "Rate Inquiry Follow-up",
            "subject": "Re: When will I get the rates?",
            "email_text": """
Hi,

I confirmed all the shipment details yesterday. 
When can I expect to receive the rates?

I need this information urgently for our planning.

Thanks,
John Smith
            """,
            "expected_state": "thread_rate_inquiry"
        },
        
        {
            "name": "Booking Request",
            "subject": "Re: Ready to proceed with booking",
            "email_text": """
Hi,

The rates look good. I want to proceed with the booking.

Please send me the booking instructions and payment details.

Best regards,
John Smith
            """,
            "expected_state": "thread_booking_request"
        },
        
        {
            "name": "General Follow-up",
            "subject": "Re: Following up on my shipment",
            "email_text": """
Hi,

Just following up on my shipment request. 
Any updates on the rates?

Thanks,
John Smith
            """,
            "expected_state": "thread_followup"
        },
        
        {
            "name": "Urgent Escalation",
            "subject": "URGENT - Need immediate assistance",
            "email_text": """
URGENT!

I've been waiting for 3 days for rates. 
This is extremely urgent and I need immediate assistance.
Please escalate this to someone who can help right away.

I'm very frustrated with the lack of response.

John Smith
            """,
            "expected_state": "thread_escalation"
        },
        
        {
            "name": "Non-Logistics Email",
            "subject": "Marketing Newsletter - Q1 2024",
            "email_text": """
Dear Valued Customer,

Thank you for your continued business with us.
Here's our Q1 2024 newsletter with industry updates.

Best regards,
Marketing Team
            """,
            "expected_state": "thread_non_logistics"
        },
        
        {
            "name": "Complex Thread with History",
            "subject": "Re: Re: Re: Shipment from Shanghai",
            "email_text": """
From: John Smith <john@abc.com>
To: logistics@company.com
Subject: Re: Re: Re: Shipment from Shanghai
Date: Mon, 15 Jan 2024 10:30:00 +0000

Hi,

Thanks for the clarification request. Here are the updated details:

Origin: Shanghai, China
Destination: Long Beach, USA
Container: 2x40ft HC
Weight: 25 tons each
Commodity: Electronics
Ready Date: February 15th, 2024

Please proceed with the rate request.

Best regards,
John Smith

---
Previous Conversation:
From: logistics@company.com
To: john@abc.com
Subject: Re: Re: Shipment from Shanghai
Date: Sun, 14 Jan 2024 15:20:00 +0000

Hi John,

We need some clarification on your shipment:
- What is the exact weight per container?
- What type of electronics are you shipping?
- Do you have any special requirements?

Please provide these details so we can give you accurate rates.

Best regards,
Logistics Team

---
From: John Smith <john@abc.com>
To: logistics@company.com
Subject: Re: Shipment from Shanghai
Date: Sat, 13 Jan 2024 09:15:00 +0000

Hi,

I need to ship 2 containers from Shanghai to Long Beach.
Please provide rates.

Thanks,
John Smith

---
From: logistics@company.com
To: john@abc.com
Subject: Re: Shipment from Shanghai
Date: Fri, 12 Jan 2024 14:30:00 +0000

Hi John,

Thank you for your inquiry. We'll need more details to provide accurate rates.

Please provide:
- Container type and quantity
- Weight and dimensions
- Commodity description
- Ready date

Best regards,
Logistics Team

---
From: John Smith <john@abc.com>
To: logistics@company.com
Subject: Shipment from Shanghai
Date: Thu, 11 Jan 2024 11:00:00 +0000

Hi,

I need a quote for shipping from Shanghai to Long Beach.

Thanks,
John Smith
            """,
            "expected_state": "thread_clarification"
        }
    ]
    
    # Run tests
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print_test_header(f"{i}/{total_tests}: {test_case['name']}")
        
        try:
            # Run the agent
            result = agent.run({
                "email_text": test_case["email_text"],
                "subject": test_case["subject"],
                "thread_id": f"test-thread-{i}"
            })
            
            # Print results
            print_test_result(result, test_case.get("expected_state"))
            
            # Count successful tests
            if result.get('status') == 'success':
                successful_tests += 1
                
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📈 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Please review the results above.")
        return False

if __name__ == "__main__":
    success = test_conversation_state_agent()
    sys.exit(0 if success else 1) 