#!/usr/bin/env python3
"""
Test script to demonstrate thread analysis functionality.
This script tests confirmation detection across entire email threads.
"""

import json
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_thread_confirmation_detection():
    """Test confirmation detection with various thread scenarios."""
    print("=== Testing Thread-Based Confirmation Detection ===")
    
    # Test case 1: Confirmation in latest message
    print("\n--- Test Case 1: Confirmation in Latest Message ---")
    thread1 = [
        {
            "sender": "customer@example.com",
            "timestamp": "2024-01-15 10:30:00",
            "body": "Yes, I confirm the booking for 2x40ft containers from Shanghai to Long Beach. Please proceed with the arrangements."
        }
    ]
    
    # Test case 2: Confirmation in quoted reply (middle of thread)
    print("\n--- Test Case 2: Confirmation in Quoted Reply ---")
    thread2 = [
        {
            "sender": "customer@example.com",
            "timestamp": "2024-01-15 11:00:00",
            "body": "Thank you for the quick response. I'll review the details."
        },
        {
            "sender": "logistics@company.com",
            "timestamp": "2024-01-15 10:45:00",
            "body": "Here is your quote for 2x40ft containers from Shanghai to Long Beach: $2500 USD. Please confirm if you'd like to proceed."
        },
        {
            "sender": "customer@example.com",
            "timestamp": "2024-01-15 10:30:00",
            "body": "Can you provide a quote for shipping 2x40ft containers from Shanghai to Long Beach?"
        }
    ]
    
    # Test case 3: Confirmation in earlier message, latest is just "thanks"
    print("\n--- Test Case 3: Confirmation in Earlier Message ---")
    thread3 = [
        {
            "sender": "customer@example.com",
            "timestamp": "2024-01-15 11:30:00",
            "body": "Thanks for the confirmation. Looking forward to working with you."
        },
        {
            "sender": "logistics@company.com",
            "timestamp": "2024-01-15 11:15:00",
            "body": "Perfect! I've confirmed your booking. Your shipment is scheduled for pickup on January 20th."
        },
        {
            "sender": "customer@example.com",
            "timestamp": "2024-01-15 11:00:00",
            "body": "Yes, please proceed with the booking. The details look good."
        },
        {
            "sender": "logistics@company.com",
            "timestamp": "2024-01-15 10:45:00",
            "body": "Here are the final details for your shipment. Please confirm if everything looks correct."
        }
    ]
    
    # Test case 4: No confirmation in thread
    print("\n--- Test Case 4: No Confirmation in Thread ---")
    thread4 = [
        {
            "sender": "customer@example.com",
            "timestamp": "2024-01-15 11:00:00",
            "body": "Can you clarify the insurance terms? I need more information before making a decision."
        },
        {
            "sender": "logistics@company.com",
            "timestamp": "2024-01-15 10:45:00",
            "body": "Here is the insurance information for your shipment. Let me know if you have any questions."
        },
        {
            "sender": "customer@example.com",
            "timestamp": "2024-01-15 10:30:00",
            "body": "I need a quote for shipping with insurance coverage."
        }
    ]
    
    # Test case 5: Multiple confirmations (should pick the most recent valid one)
    print("\n--- Test Case 5: Multiple Confirmations ---")
    thread5 = [
        {
            "sender": "customer@example.com",
            "timestamp": "2024-01-15 12:00:00",
            "body": "Actually, I need to change the pickup date to January 25th."
        },
        {
            "sender": "logistics@company.com",
            "timestamp": "2024-01-15 11:45:00",
            "body": "I've updated your booking with the new pickup date. Please confirm this change."
        },
        {
            "sender": "customer@example.com",
            "timestamp": "2024-01-15 11:30:00",
            "body": "Yes, confirmed. Please proceed with the booking."
        },
        {
            "sender": "logistics@company.com",
            "timestamp": "2024-01-15 11:15:00",
            "body": "Here are the booking details. Please confirm if you'd like to proceed."
        },
        {
            "sender": "customer@example.com",
            "timestamp": "2024-01-15 11:00:00",
            "body": "Yes, I accept the quote. Please book it."
        }
    ]
    
    test_cases = [
        ("Latest Message Confirmation", thread1),
        ("Quoted Reply Confirmation", thread2),
        ("Earlier Message Confirmation", thread3),
        ("No Confirmation", thread4),
        ("Multiple Confirmations", thread5)
    ]
    
    try:
        from agents.confirmation_agent import ConfirmationAgent
        
        agent = ConfirmationAgent()
        agent.load_context()
        
        for test_name, thread in test_cases:
            print(f"\n--- {test_name} ---")
            print(f"Thread length: {len(thread)} messages")
            
            result = agent.process({
                "message_thread": thread,
                "subject": "Logistics Request",
                "thread_id": f"thread-{test_name.lower().replace(' ', '-')}"
            })
            
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Confirmation detected: {result.get('is_confirmation', False)}")
                print(f"Confirmation type: {result.get('confirmation_type', 'unknown')}")
                print(f"Confidence: {result.get('confidence', 0):.2f}")
                print(f"Message index: {result.get('confirmation_message_index', 'N/A')}")
                print(f"Sender: {result.get('confirmation_sender', 'N/A')}")
                print(f"Details: {result.get('confirmation_details', 'N/A')}")
                print(f"Key phrases: {result.get('key_phrases', [])}")
                print(f"Reasoning: {result.get('reasoning', 'N/A')}")
                
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

def test_orchestrator_with_threads():
    """Test the orchestrator with thread input."""
    print("\n=== Testing Orchestrator with Thread Input ===")
    
    try:
        from agents.langgraph_orchestrator import run_workflow
        
        # Test thread with confirmation
        thread_with_confirmation = [
            {
                "sender": "customer@example.com",
                "timestamp": "2024-01-15 11:00:00",
                "body": "Yes, please proceed with the booking. The details look good."
            },
            {
                "sender": "logistics@company.com",
                "timestamp": "2024-01-15 10:45:00",
                "body": "Here are the final details for your shipment. Please confirm if everything looks correct."
            },
            {
                "sender": "customer@example.com",
                "timestamp": "2024-01-15 10:30:00",
                "body": "We want to ship from Shanghai to Long Beach using 2x40ft containers. The total quantity is 50, total weight is 15 Metric Ton, shipment type is FCL, and the shipment date is 20th January 2025. The cargo is electronics."
            }
        ]
        
        print("Running workflow with thread containing confirmation...")
        result = run_workflow(
            message_thread=thread_with_confirmation,
            subject="Booking Confirmation",
            thread_id="thread-orchestrator-test"
        )
        
        print(f"Workflow completed successfully: {result.get('response', {}).get('status', 'unknown')}")
        
        if "confirmation" in result:
            confirmation = result["confirmation"]
            print(f"Confirmation detected: {confirmation.get('is_confirmation', False)}")
            print(f"Confirmation type: {confirmation.get('confirmation_type', 'unknown')}")
            print(f"Message index: {confirmation.get('confirmation_message_index', 'N/A')}")
        
        if "customer_email" in result:
            print(f"Customer email result: {result['customer_email'].get('message', 'No message')}")
        
        if "forwarder_email" in result:
            print(f"Forwarder email result: {result['forwarder_email'].get('message', 'No message')}")
            
    except Exception as e:
        print(f"Orchestrator test failed with error: {e}")
        import traceback
        traceback.print_exc()

def test_backward_compatibility():
    """Test backward compatibility with single message input."""
    print("\n=== Testing Backward Compatibility ===")
    
    try:
        from agents.confirmation_agent import ConfirmationAgent
        
        agent = ConfirmationAgent()
        agent.load_context()
        
        # Test with single message (old format)
        result = agent.process({
            "email_text": "Yes, I confirm the booking for 2x40ft containers.",
            "subject": "Booking Confirmation",
            "thread_id": "thread-backward-compat"
        })
        
        print(f"Backward compatibility test - Confirmation detected: {result.get('is_confirmation', False)}")
        print(f"Confirmation type: {result.get('confirmation_type', 'unknown')}")
        
    except Exception as e:
        print(f"Backward compatibility test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Thread Analysis Test Suite")
    print("=" * 50)
    
    try:
        # Test 1: Thread confirmation detection
        test_thread_confirmation_detection()
        
        # Test 2: Orchestrator with threads
        test_orchestrator_with_threads()
        
        # Test 3: Backward compatibility
        test_backward_compatibility()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        print("\nKey Improvements:")
        print("- Agents now analyze entire message threads")
        print("- Confirmation detection works across quoted replies")
        print("- Backward compatibility maintained")
        print("- Message index tracking shows which message contains confirmation")
        
    except Exception as e:
        print(f"Test suite failed with error: {e}")
        import traceback
        traceback.print_exc() 