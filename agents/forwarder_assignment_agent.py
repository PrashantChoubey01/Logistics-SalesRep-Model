#!/usr/bin/env python3
"""
Forwarder Assignment Agent
==========================

Assigns forwarders based on POL/POD countries and generates rate requests.
"""

import json
import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent

class ForwarderAssignmentAgent(BaseAgent):
    """Agent for assigning forwarders and generating rate requests."""
    
    def __init__(self):
        super().__init__("forwarder_assignment_agent")
        self.logger = logging.getLogger(__name__)
        
        # Forwarder database by country
        self.forwarders_by_country = {
            "China": [
                {
                    "name": "China Logistics Solutions",
                    "email": "rates@chinalogistics.com",
                    "phone": "+86-21-1234-5678",
                    "specialties": ["FCL", "LCL", "Electronics"],
                    "rating": 4.8
                },
                {
                    "name": "Shanghai Freight Forwarders",
                    "email": "quotes@shanghaifreight.com", 
                    "phone": "+86-21-8765-4321",
                    "specialties": ["FCL", "Heavy Cargo"],
                    "rating": 4.6
                }
            ],
            "USA": [
                {
                    "name": "American Cargo Solutions",
                    "email": "rates@americancargo.com",
                    "phone": "+1-310-555-0123",
                    "specialties": ["FCL", "LCL", "Electronics"],
                    "rating": 4.7
                },
                {
                    "name": "LA Port Logistics",
                    "email": "quotes@laportlogistics.com",
                    "phone": "+1-310-555-0456",
                    "specialties": ["FCL", "Import/Export"],
                    "rating": 4.5
                }
            ],
            "Germany": [
                {
                    "name": "German Freight Solutions",
                    "email": "rates@germanfreight.de",
                    "phone": "+49-40-1234-5678",
                    "specialties": ["FCL", "LCL", "Automotive"],
                    "rating": 4.9
                }
            ],
            "India": [
                {
                    "name": "India Cargo Express",
                    "email": "rates@indiacargo.in",
                    "phone": "+91-22-1234-5678",
                    "specialties": ["FCL", "LCL", "Textiles"],
                    "rating": 4.4
                }
            ]
        }
        
        # Default forwarders for unknown countries
        self.default_forwarders = [
            {
                "name": "Global Logistics Partners",
                "email": "rates@globallogistics.com",
                "phone": "+1-800-555-0123",
                "specialties": ["FCL", "LCL", "General Cargo"],
                "rating": 4.3
            }
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process forwarder assignment and rate request generation."""
        print("🔧 FORWARDER_ASSIGNMENT: Starting forwarder assignment...")
        
        try:
            # Extract shipment details
            extracted_data = input_data.get("extraction_data", {})
            enriched_data = input_data.get("enriched_data", {})
            
            # Get origin and destination countries
            origin_country = extracted_data.get("origin_country", "")
            destination_country = extracted_data.get("destination_country", "")
            
            # Assign forwarders based on countries
            assigned_forwarders = self._assign_forwarders(origin_country, destination_country)
            
            # Generate rate requests for each forwarder
            rate_requests = self._generate_rate_requests(assigned_forwarders, extracted_data, enriched_data)
            
            result = {
                "assigned_forwarders": assigned_forwarders,
                "rate_requests": rate_requests,
                "total_forwarders": len(assigned_forwarders),
                "origin_country": origin_country,
                "destination_country": destination_country,
                "assignment_method": "country_based",
                "agent_name": self.agent_name,
                "agent_id": self.agent_id,
                "processed_at": self._now_iso(),
                "status": "success"
            }
            
            print(f"✅ FORWARDER_ASSIGNMENT: Assigned {len(assigned_forwarders)} forwarders")
            return result
            
        except Exception as e:
            self.logger.error(f"Forwarder assignment failed: {e}")
            print(f"❌ FORWARDER_ASSIGNMENT: Error - {str(e)}")
            return {
                "error": f"Forwarder assignment failed: {str(e)}",
                "agent_name": self.agent_name,
                "agent_id": self.agent_id,
                "processed_at": self._now_iso(),
                "status": "error"
            }

    def _assign_forwarders(self, origin_country: str, destination_country: str) -> List[Dict[str, Any]]:
        """Assign forwarders based on POL/POD countries."""
        assigned_forwarders = []
        
        # Get forwarders for origin country
        if origin_country in self.forwarders_by_country:
            origin_forwarders = self.forwarders_by_country[origin_country]
            assigned_forwarders.extend(origin_forwarders)
            print(f"🔧 FORWARDER_ASSIGNMENT: Added {len(origin_forwarders)} forwarders from {origin_country}")
        
        # Get forwarders for destination country
        if destination_country in self.forwarders_by_country:
            dest_forwarders = self.forwarders_by_country[destination_country]
            # Avoid duplicates
            for forwarder in dest_forwarders:
                if forwarder not in assigned_forwarders:
                    assigned_forwarders.append(forwarder)
            print(f"🔧 FORWARDER_ASSIGNMENT: Added {len(dest_forwarders)} forwarders from {destination_country}")
        
        # If no specific forwarders found, use defaults
        if not assigned_forwarders:
            assigned_forwarders = self.default_forwarders
            print(f"🔧 FORWARDER_ASSIGNMENT: Using default forwarders")
        
        return assigned_forwarders

    def _generate_rate_requests(self, forwarders: List[Dict[str, Any]], extracted_data: Dict[str, Any], enriched_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate rate request emails for each forwarder."""
        rate_requests = []
        
        for forwarder in forwarders:
            rate_request = self._create_rate_request_email(forwarder, extracted_data, enriched_data)
            rate_requests.append(rate_request)
        
        return rate_requests

    def _create_rate_request_email(self, forwarder: Dict[str, Any], extracted_data: Dict[str, Any], enriched_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a rate request email for a specific forwarder."""
        
        # Get shipment details
        origin_name = extracted_data.get("origin_name", "")
        destination_name = extracted_data.get("destination_name", "")
        shipment_type = extracted_data.get("shipment_type", "")
        container_type = extracted_data.get("container_type", "")
        weight = extracted_data.get("weight", "")
        commodity = extracted_data.get("commodity", "")
        shipment_date = extracted_data.get("shipment_date", "")
        quantity = extracted_data.get("quantity", 1)
        
        # Get port codes from enriched data
        rate_data = enriched_data.get("rate_data", {})
        origin_code = rate_data.get("origin_code", "")
        destination_code = rate_data.get("destination_code", "")
        
        # Create email subject and body
        subject = f"Rate Request: {origin_name} to {destination_name} - {shipment_type}"
        
        body = f"""Dear {forwarder['name']} Team,

We are seeking competitive rates for the following shipment:

**Shipment Details:**
* Origin: {origin_name} ({origin_code})
* Destination: {destination_name} ({destination_code})
* Shipment Type: {shipment_type}
* Container Type: {container_type}
* Weight: {weight}
* Commodity: {commodity}
* Shipment Date: {shipment_date}
* Quantity: {quantity}

**Request:**
Please provide your best rates for this shipment, including:
- Ocean freight rates
- Additional charges (THC, documentation, etc.)
- Transit time
- Available sailing dates

**Response Required:**
Please respond within 24 hours with your competitive quote.

Thank you for your prompt attention to this matter.

Best regards,
DP World Logistics Team
rates@dpworld.com
+1-555-0123"""

        return {
            "forwarder_name": forwarder["name"],
            "forwarder_email": forwarder["email"],
            "forwarder_phone": forwarder["phone"],
            "subject": subject,
            "body": body,
            "shipment_details": {
                "origin": origin_name,
                "destination": destination_name,
                "origin_code": origin_code,
                "destination_code": destination_code,
                "shipment_type": shipment_type,
                "container_type": container_type,
                "weight": weight,
                "commodity": commodity,
                "shipment_date": shipment_date,
                "quantity": quantity
            }
        }

    def _now_iso(self):
        """Get current timestamp in ISO format."""
        import datetime
        return datetime.datetime.utcnow().isoformat()


# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_forwarder_assignment_agent():
    """Test the forwarder assignment agent."""
    print("🧪 Testing Forwarder Assignment Agent")
    print("="*50)
    
    agent = ForwarderAssignmentAgent()
    agent.load_context()
    
    # Test data
    test_input = {
        "extraction_data": {
            "origin_name": "Shanghai",
            "origin_country": "China",
            "destination_name": "Los Angeles",
            "destination_country": "USA",
            "shipment_type": "FCL",
            "container_type": "40HC",
            "weight": "15 tons",
            "commodity": "Electronics",
            "shipment_date": "February 15, 2024",
            "quantity": 1
        },
        "enriched_data": {
            "rate_data": {
                "origin_code": "CNSHG",
                "destination_code": "USLAX",
                "origin_name": "Shanghai",
                "destination_name": "Los Angeles"
            }
        }
    }
    
    result = agent.process(test_input)
    
    print(f"✅ Result: {result.get('status')}")
    print(f"📊 Assigned Forwarders: {result.get('total_forwarders', 0)}")
    
    if result.get("assigned_forwarders"):
        print("\n📧 Forwarders Assigned:")
        for i, forwarder in enumerate(result["assigned_forwarders"], 1):
            print(f"  {i}. {forwarder['name']} ({forwarder['email']})")
    
    if result.get("rate_requests"):
        print(f"\n📧 Rate Requests Generated: {len(result['rate_requests'])}")
        for i, request in enumerate(result["rate_requests"], 1):
            print(f"  {i}. To: {request['forwarder_name']}")
            print(f"     Subject: {request['subject']}")
    
    print("="*50)
    return result

if __name__ == "__main__":
    test_forwarder_assignment_agent() 