"""Confirmation Response Agent: Generates professional and friendly responses for confirmation scenarios."""

import os
import sys
import json
import random
from typing import Dict, Any
from base_agent import BaseAgent

class ConfirmationResponseAgent(BaseAgent):
    """
    Specialized agent for generating professional and friendly responses to customer confirmations.
    - Uses warm and appreciative tone
    - Acknowledges customer's decision
    - Provides clear next steps
    - Maintains customer relationship focus
    - HIDES FORWARDER INFORMATION - only acknowledges customer confirmation
    """
    
    def __init__(self):
        super().__init__("confirmation_response_agent")
        
        # Customer-focused sales team for confirmation responses
        self.sales_team = [
            {
                "name": "Sarah Johnson",
                "designation": "Customer Success Specialist",
                "company": "SeaRates by DP World",
                "email": "sarah.johnson@dpworld.com",
                "phone": "+1-555-0123",
                "whatsapp": "+1-555-0123"
            },
            {
                "name": "Michael Chen",
                "designation": "Customer Success Specialist",
                "company": "SeaRates by DP World",
                "email": "michael.chen@dpworld.com",
                "phone": "+1-555-0124",
                "whatsapp": "+1-555-0124"
            },
            {
                "name": "Emily Rodriguez",
                "designation": "Customer Success Specialist",
                "company": "SeaRates by DP World",
                "email": "emily.rodriguez@dpworld.com",
                "phone": "+1-555-0125",
                "whatsapp": "+1-555-0125"
            }
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate confirmation response."""
        if not self.client:
            return {"error": "LLM client not initialized"}

        # Extract input data
        customer_name = input_data.get("customer_name", "Valued Customer")
        customer_email = input_data.get("customer_email", "")
        confirmation_type = input_data.get("confirmation_type", "booking_confirmation")
        confirmation_details = input_data.get("confirmation_details", "")
        shipment_details = input_data.get("shipment_details", {})
        rate_info = input_data.get("rate_info", {})
        # REMOVED: forwarder_info - we don't mention forwarders to customers
        
        # Randomly assign a sales person
        assigned_sales_person = random.choice(self.sales_team)
        
        # Function schema for LLM output
        function_schema = {
            "name": "generate_confirmation_response",
            "description": "Generate a warm and professional confirmation response to customers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "response_subject": {"type": "string", "description": "Warm email subject line"},
                    "response_body": {"type": "string", "description": "Warm and appreciative email body"},
                    "tone": {"type": "string", "description": "Tone of the message (warm, appreciative, professional)"},
                    "acknowledgment": {"type": "string", "description": "Specific acknowledgment of customer's confirmation"},
                    "next_steps": {"type": "string", "description": "Clear next steps for the customer"},
                    "gratitude_expression": {"type": "string", "description": "Expression of gratitude for their business"},
                    "response_type": {"type": "string", "enum": ["booking_confirmation", "quote_acceptance", "shipment_approval", "schedule_confirmation", "document_approval"]},
                    "estimated_completion_time": {"type": "string", "description": "Estimated time for next steps"},
                    "sales_person_name": {"type": "string"},
                    "sales_person_designation": {"type": "string"},
                    "sales_person_company": {"type": "string"},
                    "sales_person_email": {"type": "string"},
                    "sales_person_phone": {"type": "string"},
                    "sales_person_whatsapp": {"type": "string"}
                },
                "required": [
                    "response_subject", "response_body", "tone", "acknowledgment", "next_steps",
                    "gratitude_expression", "response_type", "estimated_completion_time",
                    "sales_person_name", "sales_person_designation", "sales_person_company",
                    "sales_person_email", "sales_person_phone", "sales_person_whatsapp"
                ]
            }
        }

        prompt = f"""
You are a customer success specialist at SeaRates by DP World. Generate a warm and professional confirmation response to a customer.

CUSTOMER INFORMATION:
Name: {customer_name}
Email: {customer_email}

CONFIRMATION DETAILS:
Type: {confirmation_type}
Details: {confirmation_details}

SHIPMENT DETAILS:
{json.dumps(shipment_details, indent=2)}

RATE INFORMATION:
{json.dumps(rate_info, indent=2)}

ASSIGNED SALES PERSON:
Name: {assigned_sales_person['name']}
Designation: {assigned_sales_person['designation']}
Company: {assigned_sales_person['company']}
Email: {assigned_sales_person['email']}
Phone: {assigned_sales_person['phone']}
WhatsApp: {assigned_sales_person['whatsapp']}

CRITICAL CONFIDENTIALITY RULES:
1. NEVER mention forwarder names or companies
2. NEVER share forwarder contact information
3. NEVER reveal that we work with specific forwarders
4. Use phrases like "our logistics partners" or "our network" instead
5. Focus on customer acknowledgment and next steps only
6. Say we are "working to get the best rates" without mentioning specific forwarders

RESPONSE GUIDELINES:
1. Use warm, appreciative, and professional tone
2. Express genuine gratitude for their business
3. Acknowledge their specific confirmation clearly
4. Provide clear and reassuring next steps
5. Show enthusiasm for working with them
6. Use "you" and "your" to personalize the message
7. ALWAYS include complete contact information and signature
8. Be specific about what happens next
9. Maintain customer relationship focus
10. Focus on acknowledgment and clarification only
11. Sound human and personal, NOT robotic

CONFIRMATION TYPES:
- booking_confirmation: Customer confirmed a booking/reservation
- quote_acceptance: Customer accepted a price quote
- shipment_approval: Customer approved shipment details
- schedule_confirmation: Customer confirmed pickup/delivery schedule
- document_approval: Customer approved documents/terms

SIGNATURE REQUIREMENT:
ALWAYS end with a complete professional signature including:
- Sales person name
- Designation
- Company
- Phone number
- WhatsApp number
- Email address

Generate a response that shows appreciation and provides clear next steps, but NEVER mentions specific forwarders. Make it sound personal and human, not robotic.
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
            result["customer_name"] = customer_name
            result["customer_email"] = customer_email
            result["timestamp"] = self._now_iso()
            
            return result
            
        except Exception as e:
            self.logger.error(f"LLM confirmation response generation failed: {e}")
            return self._fallback_confirmation_response(
                customer_name, confirmation_type, confirmation_details,
                shipment_details, rate_info, assigned_sales_person
            )

    def _fallback_confirmation_response(self, customer_name: str, confirmation_type: str,
                                      confirmation_details: str, shipment_details: Dict,
                                      rate_info: Dict, assigned_sales_person: Dict) -> Dict[str, Any]:
        """Fallback response when LLM is unavailable."""
        
        # Generate subject based on confirmation type
        if confirmation_type == "booking_confirmation":
            subject = "Thank you for confirming your booking!"
        elif confirmation_type == "quote_acceptance":
            subject = "Thank you for accepting our quote!"
        elif confirmation_type == "shipment_approval":
            subject = "Thank you for approving the shipment details!"
        elif confirmation_type == "schedule_confirmation":
            subject = "Thank you for confirming the schedule!"
        elif confirmation_type == "document_approval":
            subject = "Thank you for approving the documents!"
        else:
            subject = "Thank you for your confirmation!"
        
        # Generate body based on confirmation type
        if confirmation_type == "booking_confirmation":
            body = f"""Dear {customer_name},

Thank you so much for confirming your booking! I'm delighted to confirm that we have received your confirmation and will proceed with arranging your shipment.

**Booking Confirmed:**
- Origin: {shipment_details.get('origin', 'TBD')}
- Destination: {shipment_details.get('destination', 'TBD')}
- Container Type: {shipment_details.get('container_type', 'TBD')}
- Quantity: {shipment_details.get('quantity', 'TBD')}
- Shipment Date: {shipment_details.get('shipment_date', 'TBD')}

**What happens next:**
1. Our team will work with our logistics partners to finalize the booking
2. You'll receive booking confirmation documents within 24 hours
3. We'll provide you with pickup instructions and tracking information
4. Our team will monitor your shipment throughout the journey

I'm excited to work with you on this shipment and ensure everything goes smoothly. If you have any questions or need any adjustments, please don't hesitate to reach out.

Thank you for choosing SeaRates by DP World for your logistics needs!

Best regards,
{assigned_sales_person['name']}
{assigned_sales_person['designation']}
{assigned_sales_person['company']}

Phone: {assigned_sales_person['phone']}
WhatsApp: {assigned_sales_person['whatsapp']}
Email: {assigned_sales_person['email']}"""
        
        elif confirmation_type == "quote_acceptance":
            body = f"""Dear {customer_name},

Excellent! Thank you for accepting our quote. I'm thrilled that we could provide you with a competitive rate that meets your requirements.

**Quote Accepted:**
- Rate: {rate_info.get('indicative_rate', 'TBD')}
- Origin: {shipment_details.get('origin', 'TBD')}
- Destination: {shipment_details.get('destination', 'TBD')}
- Container Type: {shipment_details.get('container_type', 'TBD')}

**Next Steps:**
1. I'll prepare the booking confirmation for your review
2. You'll receive booking documents within 2 hours
3. Once you approve the booking details, we'll proceed with our logistics partners
4. You'll receive pickup instructions and tracking information

I'm looking forward to making this shipment a success for you. If you need any clarification or have questions, I'm here to help!

Thank you for your trust in our services!

Best regards,
{assigned_sales_person['name']}
{assigned_sales_person['designation']}
{assigned_sales_person['company']}

Phone: {assigned_sales_person['phone']}
WhatsApp: {assigned_sales_person['whatsapp']}
Email: {assigned_sales_person['email']}"""
        
        else:  # other confirmation types
            body = f"""Dear {customer_name},

Thank you for your confirmation! I'm pleased to confirm that we have received your approval and will proceed accordingly.

**Confirmation Details:**
- Type: {confirmation_type.replace('_', ' ').title()}
- Details: {confirmation_details}

**What happens next:**
1. Our team will process your confirmation immediately
2. You'll receive updated status within 24 hours
3. We'll coordinate with our logistics partners
4. You'll be kept informed of all progress

I appreciate your prompt response and look forward to ensuring your shipment is handled with the utmost care and efficiency.

Thank you for choosing SeaRates by DP World!

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
            "tone": "warm_appreciative",
            "acknowledgment": f"Thank you for confirming your {confirmation_type.replace('_', ' ')}",
            "next_steps": "Processing your confirmation and coordinating with our logistics partners",
            "gratitude_expression": "Thank you for choosing SeaRates by DP World",
            "response_type": confirmation_type,
            "estimated_completion_time": "24 hours",
            "sales_person_name": assigned_sales_person['name'],
            "sales_person_designation": assigned_sales_person['designation'],
            "sales_person_company": assigned_sales_person['company'],
            "sales_person_email": assigned_sales_person['email'],
            "sales_person_phone": assigned_sales_person['phone'],
            "sales_person_whatsapp": assigned_sales_person['whatsapp'],
            "extraction_method": "fallback",
            "customer_name": customer_name,
            "customer_email": customer_email,
            "timestamp": self._now_iso()
        }

    def _now_iso(self):
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()

# Test function
def test_confirmation_response_agent():
    """Test the confirmation response agent."""
    print("=== Testing Confirmation Response Agent ===")
    
    agent = ConfirmationResponseAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}")
    
    test_input = {
        "customer_name": "John Smith",
        "customer_email": "john.smith@example.com",
        "confirmation_type": "booking_confirmation",
        "confirmation_details": "booking for 2x40ft containers from Shanghai to Long Beach",
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
        }
    }
    
    result = agent.process(test_input)
    print(f"Result: {json.dumps(result, indent=2)}")
    
    return result

if __name__ == "__main__":
    test_confirmation_response_agent() 