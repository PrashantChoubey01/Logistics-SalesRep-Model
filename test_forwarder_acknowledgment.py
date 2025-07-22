#!/usr/bin/env python3
"""
Test Forwarder Acknowledgment Functionality
==========================================

This script tests the forwarder acknowledgment generation and mail trail functionality.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.forwarder_acknowledgment_api import generate_forwarder_acknowledgment, get_forwarder_mail_trail

def test_forwarder_acknowledgment():
    """Test forwarder acknowledgment generation."""
    print("\n" + "="*80)
    print("🚀 TESTING FORWARDER ACKNOWLEDGMENT FUNCTIONALITY")
    print("="*80)
    
    # Mock forwarder assignment data
    forwarder_assignment = {
        "assigned_forwarders": [
            {
                "name": "DHL Global Forwarding",
                "email": "dhl.global.forwarding@logistics.com",
                "phone": "+1-555-0101",
                "operator": "DHL",
                "specialties": ["FCL", "LCL", "Air Freight"],
                "rating": 4.8,
                "country": "Germany"
            },
            {
                "name": "Maersk Logistics",
                "email": "maersk.logistics@shipping.com",
                "phone": "+1-555-0102",
                "operator": "Maersk",
                "specialties": ["FCL", "LCL"],
                "rating": 4.7,
                "country": "Denmark"
            }
        ],
        "total_forwarders": 2,
        "origin_country": "UAE",
        "destination_country": "India",
        "assignment_method": "geographic_matching"
    }
    
    # Mock customer data
    customer_data = {
        "customer_name": "Sarah Johnson",
        "customer_email": "sarah.johnson@techcorp.com",
        "extracted_data": {
            "origin_name": "Jebel Ali",
            "destination_name": "Mundra",
            "container_type": "40HC",
            "commodity": "Electronics",
            "weight": "25,000 kg",
            "shipment_date": "March 15-30, 2024"
        }
    }
    
    print("📧 Test: Generate Forwarder Acknowledgment")
    print("-" * 50)
    
    try:
        # Test acknowledgment generation
        result = generate_forwarder_acknowledgment(forwarder_assignment, customer_data)
        
        if result.get('status') == 'success':
            print("✅ Forwarder acknowledgment generated successfully")
            print(f"   📧 Total forwarders: {result.get('total_forwarders', 0)}")
            print(f"   📝 Message: {result.get('message', 'N/A')}")
            
            acknowledgments = result.get('acknowledgments', [])
            for i, ack in enumerate(acknowledgments, 1):
                print(f"\n   📧 Forwarder Email #{i}:")
                print(f"   To: {ack['forwarder_name']} <{ack['forwarder_email']}>")
                print(f"   Subject: {ack['subject']}")
                print(f"   Type: {ack['type']}")
                print(f"   Timestamp: {ack['timestamp']}")
                
                # Show email preview
                body_preview = ack['body'][:200] + "..." if len(ack['body']) > 200 else ack['body']
                print(f"   Body Preview: {body_preview}")
                
        else:
            print(f"❌ Failed to generate acknowledgment: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n📧 Test: Mail Trail Generation")
    print("-" * 50)
    
    try:
        # Mock customer thread history
        customer_thread_history = [
            {
                "type": "customer",
                "sender": "sarah.johnson@techcorp.com",
                "subject": "Rate Request - Jebel Ali to Mundra",
                "content": "Dear SeaRates Team,\n\nI need rates for 2x40HC from Jebel Ali to Mundra...",
                "timestamp": "2025-07-22T20:00:00"
            },
            {
                "type": "bot",
                "sender": "lisa.wang@dpworld.com",
                "subject": "Re: Rate Request - Jebel Ali to Mundra",
                "content": "Dear Sarah Johnson,\n\nThank you for your inquiry...",
                "timestamp": "2025-07-22T20:05:00",
                "response_type": "confirmation_response"
            }
        ]
        
        # Test mail trail generation
        trail_result = get_forwarder_mail_trail(customer_thread_history, acknowledgments)
        
        if trail_result.get('status') == 'success':
            print("✅ Mail trail generated successfully")
            print(f"   📧 Customer emails: {trail_result.get('total_customer_emails', 0)}")
            print(f"   🚢 Forwarder emails: {trail_result.get('total_forwarder_emails', 0)}")
            
            customer_trail = trail_result.get('customer_trail', [])
            forwarder_trail = trail_result.get('forwarder_trail', [])
            
            print(f"\n   📧 Customer Trail ({len(customer_trail)} emails):")
            for i, email in enumerate(customer_trail, 1):
                print(f"   {i}. {email['type'].title()} - {email['subject']}")
            
            print(f"\n   🚢 Forwarder Trail ({len(forwarder_trail)} emails):")
            for i, email in enumerate(forwarder_trail, 1):
                print(f"   {i}. {email['type'].title()} - {email['subject']}")
                
        else:
            print(f"❌ Failed to generate mail trail: {trail_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("✅ FORWARDER ACKNOWLEDGMENT TESTING COMPLETED")
    print("="*80)
    print("\n🎯 EXPECTED BEHAVIOR:")
    print("• Forwarder acknowledgment emails generated for each assigned forwarder")
    print("• Mail trail shows both customer and forwarder email conversations")
    print("• Professional rate request emails with customer and shipment details")

def main():
    """Run the forwarder acknowledgment test."""
    print("🚀 FORWARDER ACKNOWLEDGMENT TEST SUITE")
    print("="*80)
    
    try:
        test_forwarder_acknowledgment()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 