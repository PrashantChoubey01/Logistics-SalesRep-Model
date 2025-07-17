#!/usr/bin/env python3
"""
Test script to demonstrate email sending functionality with confirmation detection.
This script tests the complete workflow including email sending for confirmations.
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.langgraph_orchestrator import run_workflow

def test_confirmation_with_email():
    """Test the complete workflow with confirmation detection and email sending."""
    print("=== Testing Confirmation Detection with Email Sending ===")
    
    # Test case 1: Clear booking confirmation
    print("\n--- Test Case 1: Booking Confirmation ---")
    result1 = run_workflow(
        email_text="Yes, I confirm the booking for 2x40ft containers from Shanghai to Long Beach. Please proceed with the arrangements.",
        subject="Booking Confirmation",
        sender="customer@dummycompany.com",
        thread_id="thread-confirmation-1"
    )
    
    print("Confirmation detected:", result1.get("confirmation", {}).get("is_confirmation", False))
    print("Confirmation type:", result1.get("confirmation", {}).get("confirmation_type", "unknown"))
    
    if "customer_email" in result1:
        print("Customer email result:", result1["customer_email"].get("message", "No message"))
    
    if "forwarder_email" in result1:
        print("Forwarder email result:", result1["forwarder_email"].get("message", "No message"))
    
    # Test case 2: Quote acceptance
    print("\n--- Test Case 2: Quote Acceptance ---")
    result2 = run_workflow(
        email_text="We accept your quote of $2500 for the FCL shipment. Please proceed with the booking.",
        subject="Quote Acceptance",
        sender="customer@dummycompany.com",
        thread_id="thread-confirmation-2"
    )
    
    print("Confirmation detected:", result2.get("confirmation", {}).get("is_confirmation", False))
    print("Confirmation type:", result2.get("confirmation", {}).get("confirmation_type", "unknown"))
    
    if "customer_email" in result2:
        print("Customer email result:", result2["customer_email"].get("message", "No message"))
    
    if "forwarder_email" in result2:
        print("Forwarder email result:", result2["forwarder_email"].get("message", "No message"))
    
    # Test case 3: Not a confirmation (should not send emails)
    print("\n--- Test Case 3: Not a Confirmation ---")
    result3 = run_workflow(
        email_text="Can you please provide a quote for shipping from Mumbai to Rotterdam?",
        subject="Quote Request",
        sender="customer@dummycompany.com",
        thread_id="thread-no-confirmation"
    )
    
    print("Confirmation detected:", result3.get("confirmation", {}).get("is_confirmation", False))
    print("Confirmation type:", result3.get("confirmation", {}).get("confirmation_type", "unknown"))
    
    if "customer_email" in result3:
        print("Customer email result:", result3["customer_email"].get("message", "No message"))
    else:
        print("No customer email sent (as expected for non-confirmation)")
    
    if "forwarder_email" in result3:
        print("Forwarder email result:", result3["forwarder_email"].get("message", "No message"))
    else:
        print("No forwarder email sent (as expected for non-confirmation)")

def test_email_sender_agent_directly():
    """Test the email sender agent directly."""
    print("\n=== Testing Email Sender Agent Directly ===")
    
    from agents.email_sender_agent import EmailSenderAgent
    
    agent = EmailSenderAgent()
    agent.load_context()
    
    # Test customer acknowledgment
    print("\n--- Testing Customer Acknowledgment ---")
    customer_result = agent.process({
        "email_type": "customer_acknowledgment",
        "customer_email": "customer@dummycompany.com",
        "confirmation_data": {
            "is_confirmation": True,
            "confirmation_type": "booking_confirmation",
            "confirmation_details": "2x40ft containers from Shanghai to Long Beach"
        },
        "thread_id": "thread-direct-test",
        "timestamp": "2024-01-15 10:30:00"
    })
    
    print("Customer email result:")
    print(json.dumps(customer_result, indent=2))
    
    # Test forwarder notification
    print("\n--- Testing Forwarder Notification ---")
    forwarder_result = agent.process({
        "email_type": "forwarder_notification",
        "forwarder_assignment": {
            "assigned_forwarder": "Global Logistics Partners",
            "origin_country": "China",
            "destination_country": "USA",
            "assignment_method": "both_countries"
        },
        "thread_id": "thread-direct-test",
        "customer_email": "customer@dummycompany.com",
        "extraction_data": {
            "shipment_type": "FCL",
            "container_type": "40ft"
        },
        "rate_data": {
            "rate": 2500,
            "source": "market_analytics"
        }
    })
    
    print("Forwarder email result:")
    print(json.dumps(forwarder_result, indent=2))
    
    # Test unsafe email domain
    print("\n--- Testing Unsafe Email Domain ---")
    unsafe_result = agent.process({
        "email_type": "customer_acknowledgment",
        "customer_email": "customer@realcompany.com",  # Not in allowed domains
        "confirmation_data": {
            "is_confirmation": True,
            "confirmation_type": "quote_acceptance",
            "confirmation_details": "rate acceptance"
        },
        "thread_id": "thread-unsafe-test"
    })
    
    print("Unsafe email result:")
    print(json.dumps(unsafe_result, indent=2))

def test_email_safety_controls():
    """Test email safety controls."""
    print("\n=== Testing Email Safety Controls ===")
    
    from agents.email_sender_agent import EmailSenderAgent
    
    agent = EmailSenderAgent()
    agent.load_context()
    
    # Test current settings
    print("Current email sending enabled:", agent.email_config.get("enable_email_sending"))
    print("Current test mode:", agent.email_config.get("test_mode"))
    print("Allowed domains:", agent.email_config.get("allowed_domains"))
    
    # Test enabling email sending (this should be done carefully in production)
    print("\n--- Testing Email Sending Control ---")
    agent.enable_email_sending(True)
    print("Email sending enabled:", agent.email_config.get("enable_email_sending"))
    
    # Test disabling test mode (this should be done carefully in production)
    print("\n--- Testing Test Mode Control ---")
    agent.set_test_mode(False)
    print("Test mode disabled:", not agent.email_config.get("test_mode"))
    
    # Reset to safe defaults
    agent.enable_email_sending(False)
    agent.set_test_mode(True)
    print("\nReset to safe defaults:")
    print("Email sending enabled:", agent.email_config.get("enable_email_sending"))
    print("Test mode:", agent.email_config.get("test_mode"))

if __name__ == "__main__":
    print("Email Functionality Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Complete workflow with email sending
        test_confirmation_with_email()
        
        # Test 2: Direct email sender agent testing
        test_email_sender_agent_directly()
        
        # Test 3: Safety controls
        test_email_safety_controls()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("\nIMPORTANT SAFETY NOTES:")
        print("- Email sending is DISABLED by default")
        print("- Test mode is ENABLED by default")
        print("- Only emails to allowed domains will be processed")
        print("- To enable actual email sending, you must:")
        print("  1. Set real SMTP credentials")
        print("  2. Call agent.enable_email_sending(True)")
        print("  3. Call agent.set_test_mode(False)")
        print("  4. Add target domains to allowed_domains list")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc() 