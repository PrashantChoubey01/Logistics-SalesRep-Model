"""Freight Forwarder Response Agent: Generates professional and friendly responses for forwarder communications."""

import os
import sys
import json
import random
from typing import Dict, Any
from base_agent import BaseAgent

class FreightForwarderResponseAgent(BaseAgent):
    """
    Specialized agent for generating professional and friendly responses to freight forwarders.
    - Uses professional yet warm tone
    - Includes call-to-action when needed
    - Provides clear next steps
    - Maintains business relationship focus
    - HIDES CUSTOMER DETAILS - only includes shipment requirements
    """
    
    def __init__(self):
        super().__init__("freight_forwarder_response_agent")
        
        # Professional sales team for forwarder communications
        self.sales_team = [
            {
                "name": "Sarah Johnson",
                "designation": "Senior Logistics Coordinator",
                "company": "SeaRates by DP World",
                "email": "sarah.johnson@dpworld.com",
                "phone": "+1-555-0123",
                "whatsapp": "+1-555-0123"
            },
            {
                "name": "Michael Chen",
                "designation": "Senior Logistics Coordinator",
                "company": "SeaRates by DP World",
                "email": "michael.chen@dpworld.com",
                "phone": "+1-555-0124",
                "whatsapp": "+1-555-0124"
            },
            {
                "name": "Emily Rodriguez",
                "designation": "Senior Logistics Coordinator",
                "company": "SeaRates by DP World",
                "email": "emily.rodriguez@dpworld.com",
                "phone": "+1-555-0125",
                "whatsapp": "+1-555-0125"
            }
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate professional forwarder response."""
        if not self.client:
            return {"error": "LLM client not initialized"}

        # Extract input data
        forwarder_name = input_data.get("forwarder_name", "Valued Partner")
        forwarder_email = input_data.get("forwarder_email", "")
        shipment_details = input_data.get("shipment_details", {})
        # REMOVED: customer_info - we don't share customer details with forwarders
        rate_info = input_data.get("rate_info", {})
        response_type = input_data.get("response_type", "rate_request")
        urgency_level = input_data.get("urgency_level", "normal")
        
        # Randomly assign a sales person
        assigned_sales_person = random.choice(self.sales_team)
        
        # Function schema for LLM output
        function_schema = {
            "name": "generate_forwarder_response",
            "description": "Generate a professional and friendly response for freight forwarders.",
            "parameters": {
                "type": "object",
                "properties": {
                    "response_subject": {"type": "string", "description": "Professional email subject line"},
                    "response_body": {"type": "string", "description": "Professional and friendly email body"},
                    "tone": {"type": "string", "description": "Tone of the message (professional, friendly, urgent)"},
                    "call_to_action": {"type": "string", "description": "Clear call to action for the forwarder"},
                    "next_steps": {"type": "string", "description": "Next steps for the forwarder"},
                    "urgency_indicators": {"type": "array", "items": {"type": "string"}},
                    "response_type": {"type": "string", "enum": ["rate_request", "follow_up", "confirmation", "escalation"]},
                    "estimated_response_time": {"type": "string", "description": "Expected response time"},
                    "sales_person_name": {"type": "string"},
                    "sales_person_designation": {"type": "string"},
                    "sales_person_company": {"type": "string"},
                    "sales_person_email": {"type": "string"},
                    "sales_person_phone": {"type": "string"},
                    "sales_person_whatsapp": {"type": "string"}
                },
                "required": [
                    "response_subject", "response_body", "tone", "call_to_action", "next_steps",
                    "urgency_indicators", "response_type", "estimated_response_time",
                    "sales_person_name", "sales_person_designation", "sales_person_company",
                    "sales_person_email", "sales_person_phone", "sales_person_whatsapp"
                ]
            }
        }

        prompt = f"""
You are a senior logistics coordinator at SeaRates by DP World. Generate a professional and friendly response to a freight forwarder.

FORWARDER INFORMATION:
Name: {forwarder_name}
Email: {forwarder_email}

SHIPMENT REQUIREMENTS (CUSTOMER DETAILS HIDDEN):
{json.dumps(shipment_details, indent=2)}

RATE INFORMATION:
{json.dumps(rate_info, indent=2)}

RESPONSE TYPE: {response_type}
URGENCY LEVEL: {urgency_level}

ASSIGNED SALES PERSON:
Name: {assigned_sales_person['name']}
Designation: {assigned_sales_person['designation']}
Company: {assigned_sales_person['company']}
Email: {assigned_sales_person['email']}
Phone: {assigned_sales_person['phone']}
WhatsApp: {assigned_sales_person['whatsapp']}

CRITICAL CONFIDENTIALITY RULES:
1. NEVER mention customer name, email, or company details
2. NEVER share customer contact information
3. ONLY share shipment requirements and port-level details
4. Refer to customer as "our client" or "the customer" without specifics
5. Focus on shipment details, dates, and requirements only

RESPONSE GUIDELINES:
1. Use professional yet warm and friendly tone
2. Show appreciation for the partnership
3. Be clear and concise about requirements
4. Include specific call-to-action when needed
5. Provide clear next steps and timeline
6. Use "we" and "our partnership" to build relationship
7. Include contact information for easy communication
8. Be responsive to urgency level
9. Maintain professional business relationship focus
10. Focus on shipment requirements and port details only

RESPONSE TYPES:
- rate_request: Request for rate quote with shipment details (NO customer info)
- follow_up: Follow up on previous request or quote
- confirmation: Confirm receipt of forwarder's response
- escalation: Escalate urgent or complex matters

Generate a response that maintains our professional relationship while being friendly and actionable, but NEVER reveals customer details.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.config.get("model_name", "databricks-meta-llama-3-3-70b-instruct"),
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "function",
                    "function": function_schema
                }],
                tool_choice={"type": "function", "function": {"name": function_schema["name"]}},
                temperature=0.3,
                max_tokens=800
            )
            
            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if not tool_calls:
                raise Exception("No tool_calls in LLM response")
            
            tool_args = tool_calls[0].function.arguments
            if isinstance(tool_args, str):
                tool_args = json.loads(tool_args)
            
            result = dict(tool_args)
            result["extraction_method"] = "llm_function_call"
            result["forwarder_name"] = forwarder_name
            result["forwarder_email"] = forwarder_email
            result["timestamp"] = self._now_iso()
            
            return result
            
        except Exception as e:
            self.logger.error(f"LLM forwarder response generation failed: {e}")
            return self._fallback_forwarder_response(
                forwarder_name, shipment_details, 
                rate_info, response_type, urgency_level, assigned_sales_person
            )

    def _fallback_forwarder_response(self, forwarder_name: str, shipment_details: Dict, 
                                   rate_info: Dict, response_type: str, urgency_level: str, 
                                   assigned_sales_person: Dict) -> Dict[str, Any]:
        """Fallback response when LLM is unavailable."""
        
        # Generate subject based on response type
        if response_type == "rate_request":
            subject = f"Rate Request: {shipment_details.get('origin', '')} to {shipment_details.get('destination', '')}"
        elif response_type == "follow_up":
            subject = f"Follow-up: {shipment_details.get('origin', '')} to {shipment_details.get('destination', '')}"
        elif response_type == "confirmation":
            subject = f"Confirmation: {shipment_details.get('origin', '')} to {shipment_details.get('destination', '')}"
        else:
            subject = f"Shipment Update: {shipment_details.get('origin', '')} to {shipment_details.get('destination', '')}"
        
        # Generate body based on response type
        if response_type == "rate_request":
            body = f"""Dear {forwarder_name} Team,

I hope this email finds you well. We have a new shipment request that we'd like to discuss with you.

**Shipment Requirements:**
- Origin: {shipment_details.get('origin', 'TBD')}
- Destination: {shipment_details.get('destination', 'TBD')}
- Container Type: {shipment_details.get('container_type', 'TBD')}
- Quantity: {shipment_details.get('quantity', 'TBD')}
- Shipment Type: {shipment_details.get('shipment_type', 'TBD')}
- Cargo: {shipment_details.get('commodity', 'TBD')}
- Shipment Date: {shipment_details.get('shipment_date', 'TBD')}

Our client has confirmed these requirements and is looking for competitive rates. Please provide us with your best quote including:
- Freight rates
- Transit time
- Any additional charges
- Validity period

{self._get_urgency_message(urgency_level)}

Please feel free to call me directly if you need any additional information or have questions.

Best regards,
{assigned_sales_person['name']}
{assigned_sales_person['designation']}
{assigned_sales_person['company']}

Phone: {assigned_sales_person['phone']}
WhatsApp: {assigned_sales_person['whatsapp']}
Email: {assigned_sales_person['email']}"""
        
        elif response_type == "follow_up":
            body = f"""Dear {forwarder_name} Team,

I hope you're doing well. I wanted to follow up on our previous communication regarding the shipment from {shipment_details.get('origin', '')} to {shipment_details.get('destination', '')}.

{self._get_urgency_message(urgency_level)}

Could you please provide an update on the status of our rate request? Our client is waiting for this information to proceed with their booking.

If you need any additional details or have any questions, please don't hesitate to reach out.

Best regards,
{assigned_sales_person['name']}
{assigned_sales_person['designation']}
{assigned_sales_person['company']}

Phone: {assigned_sales_person['phone']}
WhatsApp: {assigned_sales_person['whatsapp']}
Email: {assigned_sales_person['email']}"""
        
        else:  # confirmation or default
            body = f"""Dear {forwarder_name} Team,

Thank you for your prompt response regarding the shipment from {shipment_details.get('origin', '')} to {shipment_details.get('destination', '')}.

We have received your quote and will review it with our client. We'll get back to you shortly with their feedback and next steps.

Thank you for your continued partnership and excellent service.

Best regards,
{assigned_sales_person['name']}
{assigned_sales_person['designation']}
{assigned_sales_person['company']}

Phone: {assigned_sales_person['phone']}
WhatsApp: {assigned_sales_person['whatsapp']}
Email: {assigned_sales_person['email']}"""

        return {
            "response_subject": subject,
            "response_body": body,
            "tone": "professional_friendly",
            "call_to_action": "Please provide rates and contact for any questions",
            "next_steps": "Await forwarder response and coordinate with client",
            "urgency_indicators": [urgency_level] if urgency_level != "normal" else [],
            "response_type": response_type,
            "estimated_response_time": "24 hours",
            "sales_person_name": assigned_sales_person['name'],
            "sales_person_designation": assigned_sales_person['designation'],
            "sales_person_company": assigned_sales_person['company'],
            "sales_person_email": assigned_sales_person['email'],
            "sales_person_phone": assigned_sales_person['phone'],
            "sales_person_whatsapp": assigned_sales_person['whatsapp'],
            "extraction_method": "fallback",
            "forwarder_name": forwarder_name,
            "forwarder_email": "",
            "timestamp": self._now_iso()
        }

    def _get_urgency_message(self, urgency_level: str) -> str:
        """Get urgency message based on level."""
        if urgency_level == "urgent":
            return "**URGENT:** This is a time-sensitive request. We would appreciate your immediate attention and response within 4 hours."
        elif urgency_level == "high":
            return "**HIGH PRIORITY:** Please provide your response within 12 hours."
        elif urgency_level == "medium":
            return "Please provide your response within 24 hours."
        else:
            return "Please provide your response at your earliest convenience."

    def _now_iso(self):
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Test function
def test_freight_forwarder_response_agent():
    """Test the freight forwarder response agent."""
    print("=== Testing Freight Forwarder Response Agent ===")
    
    agent = FreightForwarderResponseAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}")
    
    test_input = {
        "forwarder_name": "Global Logistics Partners",
        "forwarder_email": "rates@globallogistics.com",
        "shipment_details": {
            "origin": "Shanghai",
            "destination": "Long Beach",
            "container_type": "40GP",
            "quantity": "2",
            "shipment_type": "FCL",
            "commodity": "Electronics",
            "shipment_date": "2024-12-15"
        },
        "rate_info": {
            "indicative_rate": "2500 USD"
        },
        "response_type": "rate_request",
        "urgency_level": "normal"
    }
    
    result = agent.process(test_input)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    return result

if __name__ == "__main__":
    test_freight_forwarder_response_agent() 