"""Forwarder Email Draft Agent: Generates rate request emails to forwarders with sales manager signatures."""

import json
import sys
import os
from typing import Dict, Any, List

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.base_agent import BaseAgent
except ImportError:
    try:
        from base_agent import BaseAgent
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from agents.base_agent import BaseAgent

try:
    from utils.sales_team_manager import SalesTeamManager
except ImportError:
    SalesTeamManager = None

class ForwarderEmailDraftAgent(BaseAgent):
    """Agent for drafting professional rate request emails to forwarders with sales manager signatures."""

    def __init__(self):
        super().__init__("forwarder_email_draft_agent")
        self.sales_team_manager = SalesTeamManager() if SalesTeamManager else None

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate rate request email drafts for assigned forwarders.
        
        Expected input:
        - assigned_forwarders: List of assigned forwarders
        - shipment_details: Shipment information (without customer details)
        - origin_country: Origin country code
        - destination_country: Destination country code
        - thread_id: Thread identifier
        - sales_manager_id: Sales manager ID for signature
        - customer_email_content: Customer email content for additional details extraction
        """
        assigned_forwarders = input_data.get("assigned_forwarders", [])
        shipment_details = input_data.get("shipment_details", {})
        origin_country = input_data.get("origin_country", "")
        destination_country = input_data.get("destination_country", "")
        port_lookup_result = input_data.get("port_lookup_result", {})  # Get port codes
        thread_id = input_data.get("thread_id", "")
        sales_manager_id = input_data.get("sales_manager_id", "")
        customer_email_content = input_data.get("customer_email_content", "")

        if not assigned_forwarders:
            return {"error": "No forwarders assigned"}

        if not self.client:
            return {"error": "LLM client not initialized"}

        # Extract additional details from customer email
        additional_details = self._extract_additional_details(customer_email_content)
        
        return self._generate_email_drafts(
            assigned_forwarders, 
            shipment_details, 
            origin_country, 
            destination_country, 
            thread_id, 
            sales_manager_id,
            additional_details,
            port_lookup_result  # Pass port lookup result
        )

    def _extract_additional_details(self, customer_email_content: str) -> Dict[str, Any]:
        """Extract additional logistics-related details from customer email using LLM."""
        if not customer_email_content or not self.client:
            return {}
        
        try:
            function_schema = {
                "name": "extract_logistics_details",
                "description": "Extract logistics-related additional details from customer email",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "transit_time_requested": {
                            "type": "boolean",
                            "description": "Whether customer requested transit time information"
                        },
                        "urgency_level": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Urgency level mentioned by customer"
                        },
                        "special_requirements": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Special requirements or requests from customer"
                        },
                        "rate_preferences": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Rate preferences or requirements mentioned"
                        },
                        "additional_notes": {
                            "type": "string",
                            "description": "Any other logistics-related notes from customer"
                        },
                        "confirmation_status": {
                            "type": "string",
                            "enum": ["pending", "confirmed", "not_mentioned"],
                            "description": "Whether customer confirmed details"
                        }
                    }
                }
            }

            prompt = f"""
Extract logistics-related additional details from this customer email:

Email Content:
{customer_email_content}

Extract only logistics-related information such as:
- Transit time requests
- Urgency levels
- Special requirements
- Rate preferences
- Confirmations of details
- Additional logistics notes

Ignore personal information, greetings, or non-logistics content.
"""

            # Use OpenAI client for function calling
            client = self.get_openai_client()
            if not client:
                return {"error": "OpenAI client not available for function calling"}
            
            response = client.chat.completions.create(
                model=self.config.get("model_name"),
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "function",
                    "function": function_schema
                }],
                tool_choice={"type": "function", "function": {"name": function_schema["name"]}},
                temperature=0.1,
                max_tokens=400
            )

            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if tool_calls:
                tool_args = tool_calls[0].function.arguments
                if isinstance(tool_args, str):
                    tool_args = json.loads(tool_args)
                return dict(tool_args)
            
            return {}
            
        except Exception as e:
            self.logger.error(f"Error extracting additional details: {e}")
            return {}

    def _generate_email_drafts(self, assigned_forwarders: List[Dict[str, Any]], shipment_details: Dict[str, Any], origin_country: str, destination_country: str, thread_id: str, sales_manager_id: str, additional_details: Dict[str, Any], port_lookup_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate email drafts using LLM function calling with sales manager signatures."""
        try:
            # Get sales manager signature
            sales_manager_signature = self._get_sales_manager_signature(sales_manager_id)
            
            function_schema = {
                "name": "generate_forwarder_emails",
                "description": "Generate professional rate request emails for forwarders with sales manager signatures",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_drafts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "forwarder_name": {"type": "string"},
                                    "to_email": {"type": "string"},
                                    "subject": {"type": "string"},
                                    "body": {"type": "string"},
                                    "priority": {"type": "string"},
                                    "urgency_level": {"type": "string"},
                                    "expected_response_time": {"type": "string"}
                                }
                            }
                        },
                        "total_emails_generated": {
                            "type": "integer"
                        },
                        "email_strategy": {
                            "type": "string"
                        },
                        "confidentiality_level": {
                            "type": "string"
                        }
                    }
                }
            }

            # Prepare shipment details for email - include ALL confirmed details
            # Get origin and destination with port codes
            origin_display = shipment_details.get("origin", origin_country)
            destination_display = shipment_details.get("destination", destination_country)
            
            # Add port codes if available
            if port_lookup_result:
                if port_lookup_result.get("origin") and port_lookup_result["origin"].get("port_code"):
                    origin_code = port_lookup_result["origin"]["port_code"]
                    origin_name = port_lookup_result["origin"].get("port_name", origin_display)
                    origin_display = f"{origin_name} ({origin_code})"
                
                if port_lookup_result.get("destination") and port_lookup_result["destination"].get("port_code"):
                    dest_code = port_lookup_result["destination"]["port_code"]
                    dest_name = port_lookup_result["destination"].get("port_name", destination_display)
                    destination_display = f"{dest_name} ({dest_code})"
            
            shipment_info = {
                "origin": origin_display,
                "destination": destination_display,
                "origin_country": origin_country,
                "destination_country": destination_country,
                "commodity": shipment_details.get("commodity", ""),
                "container_type": shipment_details.get("container_type", ""),
                "container_count": shipment_details.get("container_count", shipment_details.get("quantity", "")),
                "weight": shipment_details.get("weight", ""),
                "volume": shipment_details.get("volume", ""),
                "shipment_date": shipment_details.get("shipment_date", shipment_details.get("requested_dates", "")),
                "incoterm": shipment_details.get("incoterm", ""),
                "shipment_type": shipment_details.get("shipment_type", "FCL")
            }

            # Format additional details for email
            additional_info = self._format_additional_details(additional_details)

            prompt = f"""
Generate professional rate request emails for forwarders.

Forwarders: {json.dumps(assigned_forwarders, indent=2)}

Shipment Details:
{self._format_shipment_details(shipment_info)}

Additional Requirements:
{additional_info}

Sales Manager Signature:
{sales_manager_signature}

Rules:
- Professional and courteous tone
- Clear, organized shipment details
- Request competitive rates and transit times
- Include all additional requirements from customer
- NO customer information or personal details
- Request all-inclusive rates
- Use the provided sales manager signature
- Format details in a clear, structured manner

Generate one email per forwarder with subject, body, priority, urgency, and response time.
"""

            # Use OpenAI client for function calling
            client = self.get_openai_client()
            if not client:
                return {"error": "OpenAI client not available for function calling"}
            
            response = client.chat.completions.create(
                model=self.config.get("model_name"),
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "function",
                    "function": function_schema
                }],
                tool_choice={"type": "function", "function": {"name": function_schema["name"]}},
                temperature=0.1,
                max_tokens=1000
            )

            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if not tool_calls:
                raise Exception("No tool_calls in LLM response")

            tool_args = tool_calls[0].function.arguments
            if isinstance(tool_args, str):
                tool_args = json.loads(tool_args)

            result = dict(tool_args)
            result["generation_method"] = "llm_function_call"
            result["thread_id"] = thread_id
            result["origin_country"] = origin_country
            result["destination_country"] = destination_country
            result["sales_manager_id"] = sales_manager_id
            result["additional_details"] = additional_details
            
            # Validate and correct result if needed
            if not result.get("email_drafts"):
                result["email_drafts"] = []
                result["total_emails_generated"] = 0
                result["confidentiality_level"] = "high"

            # Ensure confidentiality level is set
            if not result.get("confidentiality_level"):
                result["confidentiality_level"] = "high"

            self.logger.info(f"Email draft generation successful: {result['total_emails_generated']} emails generated (confidentiality: {result['confidentiality_level']})")
            
            return result

        except Exception as e:
            self.logger.error(f"Email draft generation failed: {e}")
            return {"error": f"Email draft generation failed: {str(e)}"}

    def _get_sales_manager_signature(self, sales_manager_id: str) -> str:
        """Get sales manager signature by ID."""
        if not self.sales_team_manager or not sales_manager_id:
            return self._get_default_signature()
        
        try:
            sales_person = self.sales_team_manager.get_sales_person_by_id(sales_manager_id)
            if sales_person:
                return sales_person.get("signature", self._get_default_signature())
        except Exception as e:
            self.logger.error(f"Error getting sales manager signature: {e}")
        
        return self._get_default_signature()

    def _get_default_signature(self) -> str:
        """Get default signature if sales manager not found."""
        return """Best regards,

Digital Sales Specialist
Searates By DP World
📧 sales@searates.com
📞 +1-555-0123
🌐 www.searates.com"""

    def _format_shipment_details(self, shipment_info: Dict[str, Any]) -> str:
        """Format shipment details in a clear, structured manner with ALL confirmed information."""
        details = []
        
        # Origin and Destination (with port codes if available)
        if shipment_info.get("origin"):
            details.append(f"Origin: {shipment_info['origin']}")
        elif shipment_info.get("origin_country"):
            details.append(f"Origin Country: {shipment_info['origin_country']}")
        
        if shipment_info.get("destination"):
            details.append(f"Destination: {shipment_info['destination']}")
        elif shipment_info.get("destination_country"):
            details.append(f"Destination Country: {shipment_info['destination_country']}")
        
        # Container information
        if shipment_info.get("container_type"):
            details.append(f"Container Type: {shipment_info['container_type']}")
        
        if shipment_info.get("container_count"):
            details.append(f"Number of Containers: {shipment_info['container_count']}")
        
        # Commodity
        if shipment_info.get("commodity"):
            details.append(f"Commodity: {shipment_info['commodity']}")
        
        # Weight and Volume
        if shipment_info.get("weight"):
            details.append(f"Weight: {shipment_info['weight']}")
        
        if shipment_info.get("volume"):
            details.append(f"Volume: {shipment_info['volume']}")
        
        # Dates
        if shipment_info.get("shipment_date"):
            details.append(f"Ready Date / Shipment Date: {shipment_info['shipment_date']}")
        
        # Incoterm
        if shipment_info.get("incoterm"):
            details.append(f"Incoterm: {shipment_info['incoterm']}")
        
        # Shipment Type
        if shipment_info.get("shipment_type"):
            details.append(f"Shipment Type: {shipment_info['shipment_type']}")
        
        return "\n".join([f"- {detail}" for detail in details])

    def _format_additional_details(self, additional_details: Dict[str, Any]) -> str:
        """Format additional details for email inclusion."""
        if not additional_details:
            return "No additional requirements specified."
        
        details = []
        
        if additional_details.get("transit_time_requested"):
            details.append("- Transit time information requested")
        
        if additional_details.get("urgency_level"):
            details.append(f"- Urgency Level: {additional_details['urgency_level'].title()}")
        
        if additional_details.get("special_requirements"):
            for req in additional_details["special_requirements"]:
                details.append(f"- Special Requirement: {req}")
        
        if additional_details.get("rate_preferences"):
            for pref in additional_details["rate_preferences"]:
                details.append(f"- Rate Preference: {pref}")
        
        if additional_details.get("additional_notes"):
            details.append(f"- Additional Notes: {additional_details['additional_notes']}")
        
        if additional_details.get("confirmation_status") == "confirmed":
            details.append("- Customer has confirmed all details")
        
        return "\n".join(details) if details else "No additional requirements specified."

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_forwarder_email_draft_agent():
    print("=== Testing Forwarder Email Draft Agent ===")
    agent = ForwarderEmailDraftAgent()
    
    if not agent.load_context():
        print("✗ Failed to load context")
        return
    
    # Test case
    test_input = {
        "assigned_forwarders": [
            {
                "forwarder_name": "DHL Global Forwarding",
                "email": "rates@dhl.com",
                "contact": "DHL Rate Team",
                "priority": "primary",
                "assignment_reason": "Strong presence in both countries with electronics specialty",
                "specialty_match": True,
                "country_coverage": "Full coverage"
            },
            {
                "forwarder_name": "Kuehne + Nagel",
                "email": "quotes@kuehne-nagel.com",
                "contact": "KN Rate Team",
                "priority": "secondary",
                "assignment_reason": "Good coverage with competitive rates",
                "specialty_match": True,
                "country_coverage": "Full coverage"
            }
        ],
        "shipment_details": {
            "commodity": "electronics",
            "container_type": "40HC",
            "quantity": 2,
            "weight": "25,000 kg",
            "volume": "35 CBM",
            "shipment_date": "2024-04-20",
            "shipment_type": "FCL"
        },
        "origin_country": "AE",
        "destination_country": "IN",
        "thread_id": "test-thread-1",
        "sales_manager_id": "SM001", # Added sales_manager_id
        "customer_email_content": "Dear Logistics Solutions Inc., I am interested in a rate for a shipment from Dubai to Mumbai. The shipment consists of 2 units of electronics weighing 25,000 kg and occupying 35 CBM. Could you please provide a competitive rate for this route? I would appreciate a response within 24 hours. Thank you!" # Added customer_email_content
    }
    
    print(f"\n--- Testing Email Draft Generation ---")
    result = agent.run(test_input)
    
    if result.get("status") == "success":
        email_drafts = result.get("email_drafts", [])
        total_emails = result.get("total_emails_generated", 0)
        strategy = result.get("email_strategy", "")
        confidentiality = result.get("confidentiality_level", "")
        
        print(f"✓ Emails Generated: {total_emails}")
        print(f"✓ Strategy: {strategy}")
        print(f"✓ Confidentiality: {confidentiality}")
        
        for i, email in enumerate(email_drafts, 1):
            print(f"\n  {i}. {email.get('forwarder_name')} ({email.get('priority')})")
            print(f"     To: {email.get('to_email')}")
            print(f"     Subject: {email.get('subject')}")
            print(f"     Urgency: {email.get('urgency_level')}")
            print(f"     Response Time: {email.get('expected_response_time')}")
            print(f"     Body Preview: {email.get('body', '')[:100]}...")
        
        if total_emails > 0:
            print("✓ Email draft generation successful!")
        else:
            print("✗ No email drafts generated")
    else:
        print(f"✗ Test failed: {result.get('error')}")

if __name__ == "__main__":
    test_forwarder_email_draft_agent() 