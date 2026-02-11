#!/usr/bin/env python3
"""
Test forwarder rate extraction with the exact email format from the user
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.forwarder_response_agent import ForwarderResponseAgent

def test_forwarder_extraction():
    print("="*80)
    print("Testing Forwarder Rate Extraction")
    print("="*80)
    
    # Initialize agent
    agent = ForwarderResponseAgent()
    
    # Exact email from user
    email_content = """Dear SeaRates Team,

Thank you for your rate request. Please find our competitive quote below:

Route: Jebel Ali (AEJEA) to Los Angeles (USLAX)
Container Type: 40HC
Rate: $3,200 USD per container
Transit Time: 21 days
Validity: March 31, 2026

Additional Services:
- Free detention: 7 days
- Documentation included

We look forward to your confirmation.

Best regards,
Michael Chen
Operations Manager
Pacific Bridge Logistics"""
    
    # Test extraction
    print("\n1. Testing rate extraction from email:")
    print("-" * 80)
    
    rate_info = agent._extract_rate_information(email_content)
    
    print(f"\n📊 Extracted Rate Information:")
    print(f"   Origin Port: {rate_info.get('origin_port')}")
    print(f"   Destination Port: {rate_info.get('destination_port')}")
    print(f"   Container Type: {rate_info.get('container_type')}")
    print(f"   Rate: ${rate_info.get('rate'):,.2f}" if rate_info.get('rate') else "   Rate: Not extracted")
    print(f"   Currency: {rate_info.get('currency')}")
    print(f"   Transit Time: {rate_info.get('transit_time')} days" if rate_info.get('transit_time') else "   Transit Time: Not extracted")
    print(f"   Valid Until: {rate_info.get('valid_until')}")
    
    # Check if all key fields were extracted
    print("\n✅ Extraction Results:")
    success_count = 0
    total_fields = 6
    
    if rate_info.get('origin_port'):
        print("   ✅ Origin Port: Extracted")
        success_count += 1
    else:
        print("   ❌ Origin Port: NOT extracted")
    
    if rate_info.get('destination_port'):
        print("   ✅ Destination Port: Extracted")
        success_count += 1
    else:
        print("   ❌ Destination Port: NOT extracted")
    
    if rate_info.get('container_type'):
        print("   ✅ Container Type: Extracted")
        success_count += 1
    else:
        print("   ❌ Container Type: NOT extracted")
    
    if rate_info.get('rate'):
        print(f"   ✅ Rate: Extracted (${rate_info['rate']:,.2f})")
        success_count += 1
    else:
        print("   ❌ Rate: NOT extracted")
    
    if rate_info.get('transit_time'):
        print(f"   ✅ Transit Time: Extracted ({rate_info['transit_time']} days)")
        success_count += 1
    else:
        print("   ❌ Transit Time: NOT extracted")
    
    if rate_info.get('valid_until'):
        print(f"   ✅ Valid Until: Extracted ({rate_info['valid_until']})")
        success_count += 1
    else:
        print("   ❌ Valid Until: NOT extracted")
    
    print(f"\n📈 Success Rate: {success_count}/{total_fields} fields extracted ({success_count/total_fields*100:.0f}%)")
    
    if success_count == total_fields:
        print("\n🎉 SUCCESS! All fields extracted correctly!")
    elif success_count >= 4:
        print("\n✅ GOOD! Most fields extracted successfully.")
    else:
        print("\n⚠️  WARNING! Some fields missing.")
    
    # Test full process
    print("\n\n2. Testing full forwarder response process:")
    print("-" * 80)
    
    input_data = {
        "email_data": {
            "content": email_content,
            "subject": "Rate Quote - Jebel Ali to Los Angeles",
            "sender": "ops@pacificbridgelogistics.com",
            "from_name": "Michael Chen"
        },
        "forwarder_detection": {
            "forwarder_details": {
                "name": "Pacific Bridge Logistics",
                "email": "ops@pacificbridgelogistics.com",
                "company": "Pacific Bridge Logistics"
            }
        },
        "conversation_state": {
            "conversation_state": "thread_forwarder_interaction"
        }
    }
    
    result = agent.process(input_data)
    
    print(f"\n📧 Response Generated:")
    print(f"   Response Type: {result.get('response_type')}")
    print(f"   Forwarder Name: {result.get('forwarder_name')}")
    print(f"   Forwarder Email: {result.get('forwarder_email')}")
    print(f"   Status: {result.get('status')}")
    
    extracted = result.get('extracted_rate_info', {})
    print(f"\n📊 Extracted Rate Info in Result:")
    print(f"   Origin: {extracted.get('origin_port')}")
    print(f"   Destination: {extracted.get('destination_port')}")
    print(f"   Container: {extracted.get('container_type')}")
    print(f"   Rate: ${extracted.get('rate'):,.2f}" if extracted.get('rate') else "   Rate: N/A")
    print(f"   Transit: {extracted.get('transit_time')} days" if extracted.get('transit_time') else "   Transit: N/A")
    print(f"   Valid Until: {extracted.get('valid_until')}")
    
    print("\n" + "="*80)
    print("Test Complete!")
    print("="*80)

if __name__ == "__main__":
    test_forwarder_extraction()
