#!/usr/bin/env python3
"""
Forwarder Assignment Agent
==========================

Assigns forwarders based on POL/POD countries and generates rate requests.
"""

import json
import logging
import pandas as pd
import os
from typing import Dict, Any, List
from agents.base_agent import BaseAgent

class ForwarderAssignmentAgent(BaseAgent):
    """Agent for assigning forwarders and generating rate requests."""

    def __init__(self):
        super().__init__("forwarder_assignment_agent")
        self.logger = logging.getLogger(__name__)
        
        # Load forwarders from CSV file
        self.forwarders_by_country = self._load_forwarders_from_csv()
        
        # Default forwarders for unknown countries
        self.default_forwarders = [
            {
                "name": "Global Logistics Partners",
                "email": "rates@globallogistics.com",
                "phone": "+1-800-555-0123",
                "specialties": ["FCL", "LCL", "General Cargo"],
                "rating": 4.3,
                "operator": "Multiple Operators"
            }
        ]

    def _load_forwarders_from_csv(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load forwarders from CSV file."""
        try:
            # Get the path to the CSV file
            csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   "Forwarders_with_Operators_and_Emails.csv")
            
            if not os.path.exists(csv_path):
                self.logger.warning(f"Forwarder CSV file not found at {csv_path}")
                return {}
            
            # Read CSV file
            df = pd.read_csv(csv_path)
            self.logger.info(f"Loaded {len(df)} forwarder records from CSV")
            
            # Group by country
            forwarders_by_country = {}
            
            for _, row in df.iterrows():
                country = row['country']
                forwarder = {
                    "name": row['forwarder_name'],
                    "email": row['email'],
                    "phone": "+1-800-555-0000",  # Default phone since not in CSV
                    "specialties": ["FCL", "LCL", "General Cargo"],  # Default specialties
                    "operator": row['operator']
                    # Note: rating removed since not available in CSV
                }
                
                if country not in forwarders_by_country:
                    forwarders_by_country[country] = []
                
                forwarders_by_country[country].append(forwarder)
            
            self.logger.info(f"Organized forwarders by {len(forwarders_by_country)} countries")
            return forwarders_by_country
            
        except Exception as e:
            self.logger.error(f"Error loading forwarders from CSV: {str(e)}")
            return {}

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
        
        # Get special instructions and requirements
        special_instructions = extracted_data.get("special_instructions", "")
        special_requirements = extracted_data.get("special_requirements", "")
        dangerous_goods = extracted_data.get("dangerous_goods", False)
        insurance = extracted_data.get("insurance", False)
        packaging = extracted_data.get("packaging", "")
        customs_clearance = extracted_data.get("customs_clearance", False)
        delivery_address = extracted_data.get("delivery_address", "")
        pickup_address = extracted_data.get("pickup_address", "")
        
        # Get port codes from enriched data
        rate_data = enriched_data.get("rate_data", {})
        origin_code = rate_data.get("origin_code", "")
        destination_code = rate_data.get("destination_code", "")
        
        # Create email subject and body
        subject = f"Rate Request: {origin_name} to {destination_name} - {shipment_type}"
        
        # Get operator information
        operator = forwarder.get("operator", "Multiple Operators")
        
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
* Preferred Operator: {operator}"""

        # Add only essential special instructions to email body
        special_sections = []
        
        if special_instructions:
            special_sections.append(f"* Special Instructions: {special_instructions}")
        
        if special_requirements:
            special_sections.append(f"* Special Requirements: {special_requirements}")
        
        if dangerous_goods:
            special_sections.append("* Dangerous Goods: YES - Please include DG handling charges and required documentation")
        
        if insurance:
            special_sections.append("* Insurance: Required - Please include insurance coverage options")
        
        # Only add critical special requirements to email body
        if special_sections:
            body += "\n\n**Special Requirements:**\n" + "\n".join(special_sections)
        
        body += f"""

**Request:**
Please provide your best rates for this shipment, including:
- Ocean freight rates
- Additional charges (THC, documentation, etc.)
- Transit time
- Available sailing dates
- Operator-specific rates if applicable"""

        # Add specific requests based on critical special requirements
        if dangerous_goods:
            body += """
- DG handling charges and documentation requirements
- IMDG compliance confirmation
- Required safety measures"""
        
        if insurance:
            body += """
- Insurance coverage options and costs
- Coverage limits and terms"""
        
        body += f"""

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
                "quantity": quantity,
                "operator": operator,
                "special_instructions": special_instructions,
                "special_requirements": special_requirements,
                "dangerous_goods": dangerous_goods,
                "insurance": insurance,
                "packaging": packaging,
                "customs_clearance": customs_clearance,
                "delivery_address": delivery_address,
                "pickup_address": pickup_address
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