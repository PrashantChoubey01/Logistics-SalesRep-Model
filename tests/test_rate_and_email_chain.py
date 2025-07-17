#!/usr/bin/env python3
"""
Test script to verify indicative rate inclusion and email chain formatting
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.response_generator_agent import ResponseGeneratorAgent

def test_rate_inclusion_and_email_chain():
    """Test that indicative rate is always included and email chain is formatted"""
    
    print("Testing Rate Inclusion and Email Chain")
    print("=" * 50)
    
    agent = ResponseGeneratorAgent()
    
    # Mock data that includes rate information
    test_input = {
        "classification_data": {
            "email_type": "logistics_request",
            "confidence": 0.95
        },
        "confirmation_data": {
            "is_confirmation": False,
            "confirmation_type": "no_confirmation"
        },
        "extraction_data": {
            "origin": "Jebel Ali",
            "destination": "Mundra",
            "shipment_type": "FCL",
            "container_type": "20DC",
            "quantity": 50,
            "weight": "15 metric tons",
            "commodity": "Electronics",
            "customer_name": "John Smith",
            "customer_company": "ABC Electronics Ltd."
        },
        "validation_data": {
            "validated_data": {
                "origin_code": "AEJEA",
                "destination_code": "INMUN",
                "container_type": "20DC"
            }
        },
        "clarification_data": {
            "clarification_needed": True,
            "missing_fields": ["shipment_date"],
            "clarification_message": "Please provide shipment date"
        },
        "container_standardization_data": {
            "standard_type": "20DC"
        },
        "port_lookup_data": {
            "results": [
                {"port_code": "AEJEA", "port_name": "Jebel Ali (Dubai)", "confidence": 0.87},
                {"port_code": "INMUN", "port_name": "Mundra", "confidence": 1.0}
            ]
        },
        "rate_data": {
            "indicative_rate": "$1,200 - $1,800",
            "rate_recommendation": {
                "rate_range": "$1,200 - $1,800",
                "match_type": "exact_match"
            }
        },
        "forwarder_assignment": {
            "assigned_forwarder": "Global Logistics Partners"
        },
        "subject": "Shipping Request - FCL",
        "email_text": """Hi team,

We want to ship 50 containers from Jebel Ali to Mundra using 20DC containers. The total weight is 15 metric tons. Please provide your best rate.

Regards,
John Smith
ABC Electronics Ltd.""",
        "from": "john.smith@abcelectronics.com",
        "thread_id": "test-001"
    }
    
    print("Testing with rate data and clarification needed...")
    result = agent.process(test_input)
    
    if result.get("error"):
        print(f"❌ Error: {result.get('error')}")
        return
    
    print(f"✅ Response generated successfully")
    print(f"✅ Response type: {result.get('response_type')}")
    print(f"✅ Response body preview:")
    print(result.get('response_body', '')[:500] + "...")
    
    # Check if rate is included
    response_body = result.get('response_body', '').lower()
    if 'indicative rate' in response_body or '$1,200' in response_body or '$1,800' in response_body:
        print("✅ Indicative rate is included in the response")
    else:
        print("❌ Indicative rate is NOT included in the response")
    
    # Check if email chain is included
    if 'email chain' in response_body.lower() or '---' in response_body:
        print("✅ Email chain format is included")
    else:
        print("❌ Email chain format is NOT included")
    
    print("\n" + "=" * 50)
    print("FULL RESPONSE:")
    print(result.get('response_body', ''))

if __name__ == "__main__":
    test_rate_inclusion_and_email_chain() 