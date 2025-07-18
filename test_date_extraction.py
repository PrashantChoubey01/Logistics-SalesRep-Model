#!/usr/bin/env python3
"""Test extraction agent date capture"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.extraction_agent import ExtractionAgent

def test_date_extraction():
    """Test if extraction agent now captures ready date"""
    print("=== Testing Date Extraction ===")
    
    agent = ExtractionAgent()
    agent.load_context()
    
    test_email = """SeaRates Team,

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
    
    result = agent.run({
        "email_text": test_email,
        "subject": "enquret"
    })
    
    print(f"Status: {result.get('status')}")
    if result.get('status') == 'success':
        print(f"✅ Extracted shipment_date: {result.get('shipment_date')}")
        if result.get('shipment_date'):
            print("✅ SUCCESS: Ready date is now being captured!")
        else:
            print("❌ FAILED: Ready date still not captured")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    test_date_extraction() 