#!/usr/bin/env python3
"""
Quick test to verify rate recommendation display in confirmation response
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.rate_recommendation_agent import RateRecommendationAgent
from agents.confirmation_response_agent import ConfirmationResponseAgent

def test_rate_display():
    print("="*80)
    print("Testing Rate Recommendation Display")
    print("="*80)
    
    # Initialize agents
    rate_agent = RateRecommendationAgent()
    confirmation_agent = ConfirmationResponseAgent()
    
    # Test route: AEJEA → USLAX (Jebel Ali → Los Angeles)
    print("\n1. Testing AEJEA → USLAX (Jebel Ali → Los Angeles)")
    print("-" * 80)
    
    rate_result = rate_agent.process({
        "origin": "AEJEA",
        "destination": "USLAX",
        "container_type": "40HC"
    })
    
    print(f"Status: {rate_result.get('status')}")
    print(f"Price Range: {rate_result.get('price_range_recommendation')}")
    print(f"Market Average: {rate_result.get('market_average')}")
    print(f"Rate Quality: {rate_result.get('rate_quality')}")
    
    # Test confirmation response with rate data
    extracted_data = {
        "shipment_details": {
            "origin": "Jebel Ali",
            "destination": "Los Angeles",
            "container_type": "40HC",
            "container_count": "2",
            "commodity": "Electronics"
        },
        "contact_information": {
            "name": "John Smith",
            "email": "john.smith@techcorp.com"
        }
    }
    
    confirmation_result = confirmation_agent.generate_confirmation_response(
        extracted_data=extracted_data,
        customer_name="John",
        rate_info=rate_result
    )
    
    print("\n" + "="*80)
    print("CONFIRMATION EMAIL WITH RATES:")
    print("="*80)
    print(f"Subject: {confirmation_result['subject']}")
    print("\nBody:")
    print(confirmation_result['body'])
    print("="*80)
    
    # Check if rates are in the body
    if "Indicative Market Rates" in confirmation_result['body']:
        print("\n✅ SUCCESS: Rate information is included in confirmation response!")
    else:
        print("\n❌ FAIL: Rate information is NOT included in confirmation response!")
        print("\nRate info passed:")
        print(rate_result)
    
    # Test other routes
    print("\n\n2. Testing other routes:")
    print("-" * 80)
    
    test_routes = [
        ("CNSGH", "DEHAM", "40HC", "Shanghai → Hamburg"),
        ("SGSIN", "NLRTM", "40HC", "Singapore → Rotterdam"),
        ("VNSGN", "USLAX", "40HC", "Ho Chi Minh → Los Angeles"),
    ]
    
    for origin, dest, container, route_name in test_routes:
        rate_result = rate_agent.process({
            "origin": origin,
            "destination": dest,
            "container_type": container
        })
        
        print(f"\n{route_name}:")
        print(f"  Status: {rate_result.get('status')}")
        if rate_result.get('status') == 'success':
            print(f"  Price Range: {rate_result.get('price_range_recommendation')}")
            print(f"  Market Average: ${rate_result.get('market_average')}")
            print(f"  ✅ Rates available")
        else:
            print(f"  ❌ No rates available")

if __name__ == "__main__":
    test_rate_display()
