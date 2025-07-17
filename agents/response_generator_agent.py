import os
import sys
import json
import random
from typing import Dict, Any
from base_agent import BaseAgent

class ResponseGeneratorAgent(BaseAgent):
    """
    Generates a human-like, confirmation-seeking response using all agent inputs and LLM function calling.
    - Summarizes all extracted shipment details in a customer-friendly way.
    - Includes rates when port codes/names are available.
    - Asks for WhatsApp contact if not found in email.
    - Uses friendly, empathetic, and professional tone.
    - Focuses on customer needs without technical validation details.
    """
    def __init__(self):
        super().__init__("response_generator_agent")
        
                # Standardized sales team data - all using SeaRates by DP World
        self.sales_team = [
            {
                "name": "Sarah Johnson",
                "designation": "Digital Sales Specialist",
                "company": "SeaRates by DP World",
                "email": "sarah.johnson@dpworld.com",
                "phone": "+1-555-0123",
                "whatsapp": "+1-555-0123"
            },
            {
                "name": "Michael Chen",
                "designation": "Digital Sales Specialist", 
                "company": "SeaRates by DP World",
                "email": "michael.chen@dpworld.com",
                "phone": "+1-555-0124",
                "whatsapp": "+1-555-0124"
            },
            {
                "name": "Emily Rodriguez",
                "designation": "Digital Sales Specialist",
                "company": "SeaRates by DP World",
                "email": "emily.rodriguez@dpworld.com", 
                "phone": "+1-555-0125",
                "whatsapp": "+1-555-0125"
            },
            {
                "name": "David Thompson",
                "designation": "Digital Sales Specialist",
                "company": "SeaRates by DP World",
                "email": "david.thompson@dpworld.com",
                "phone": "+1-555-0126",
                "whatsapp": "+1-555-0126"
            },
            {
                "name": "Lisa Wang",
                "designation": "Digital Sales Specialist",
                "company": "SeaRates by DP World",
                "email": "lisa.wang@dpworld.com",
                "phone": "+1-555-0127",
                "whatsapp": "+1-555-0127"
            },
            {
                "name": "James Wilson",
                "designation": "Digital Sales Specialist",
                "company": "SeaRates by DP World",
                "email": "james.wilson@dpworld.com", 
                "phone": "+1-555-0128",
                "whatsapp": "+1-555-0128"
            },
            {
                "name": "Maria Garcia",
                "designation": "Digital Sales Specialist",
                "company": "SeaRates by DP World",
                "email": "maria.garcia@dpworld.com",
                "phone": "+1-555-0129",
                "whatsapp": "+1-555-0129"
            },
            {
                "name": "Robert Kim",
                "designation": "Digital Sales Specialist",
                "company": "SeaRates by DP World",
                "email": "robert.kim@dpworld.com",
                "phone": "+1-555-0130",
                "whatsapp": "+1-555-0130"
            },
            {
                "name": "Jennifer Lee",
                "designation": "Digital Sales Specialist",
                "company": "SeaRates by DP World",
                "email": "jennifer.lee@dpworld.com", 
                "phone": "+1-555-0131",
                "whatsapp": "+1-555-0131"
            },
            {
                "name": "Alex Martinez",
                "designation": "Digital Sales Specialist",
                "company": "SeaRates by DP World",
                "email": "alex.martinez@dpworld.com",
                "phone": "+1-555-0132",
                "whatsapp": "+1-555-0132"
            }
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.client:
            return {"error": "LLM client not initialized"}

        classification_data = input_data.get("classification_data", {})
        confirmation_data = input_data.get("confirmation_data", {})
        extraction_data = input_data.get("extraction_data", {})
        validation_data = input_data.get("validation_data", {})
        clarification_data = input_data.get("clarification_data", {})
        container_standardization_data = input_data.get("container_standardization_data", {})
        port_lookup_data = input_data.get("port_lookup_data", {})
        rate_data = input_data.get("rate_data", {})
        subject = input_data.get("subject", "")
        email_text = input_data.get("email_text", "")
        sender = input_data.get("from", "customer@example.com")
        thread_id = input_data.get("thread_id", "")
        
        # Randomly assign a sales person
        assigned_sales_person = random.choice(self.sales_team)
        
        # Function schema for LLM output (OpenAI function-calling format)
        function_schema = {
            "name": "generate_response",
            "description": "Generate a human-like, customer-friendly logistics response email using all agent outputs.",
            "parameters": {
                "type": "object",
                "properties": {
                    "response_subject": {"type": "string", "description": "Email subject line"},
                    "response_body": {"type": "string", "description": "Email body, human-like, friendly, customer-focused"},
                    "tone": {"type": "string", "description": "Tone of the message (friendly, professional, empathetic)"},
                    "key_information_included": {"type": "array", "items": {"type": "string"}},
                    "attachments_needed": {"type": "array", "items": {"type": "string"}},
                    "next_steps": {"type": "string"},
                    "urgency_level": {"type": "string"},
                    "follow_up_required": {"type": "boolean"},
                    "estimated_response_time": {"type": "string"},
                    "extraction_method": {"type": "string"},
                    "clarification_included": {"type": "boolean", "description": "Whether clarification questions were included"},
                    "confirmation_handled": {"type": "boolean", "description": "Whether confirmation was handled appropriately"},
                    "response_type": {"type": "string", "enum": ["clarification_request", "confirmation_response", "standard_response", "quote_response"], "description": "Type of response generated"},
                    "sales_person_name": {"type": "string", "description": "Name of the assigned sales person"},
                    "sales_person_designation": {"type": "string", "description": "Designation of the sales person"},
                    "sales_person_company": {"type": "string", "description": "Company of the sales person"},
                    "sales_person_email": {"type": "string", "description": "Email of the sales person"},
                    "sales_person_phone": {"type": "string", "description": "Phone number of the sales person"},
                    "sales_person_whatsapp": {"type": "string", "description": "WhatsApp number of the sales person"}
                },
                "required": [
                    "response_subject", "response_body", "tone", "key_information_included", "attachments_needed", "next_steps", "urgency_level", "follow_up_required", "estimated_response_time", "extraction_method", "clarification_included", "confirmation_handled", "response_type",
                    "sales_person_name", "sales_person_designation", "sales_person_company", "sales_person_email", "sales_person_phone", "sales_person_whatsapp"
                ]
            }
        }

        # Check if clarification is needed
        clarification_needed = clarification_data.get("clarification_needed", False)
        clarification_message = clarification_data.get("clarification_message", "")
        clarification_details = clarification_data.get("clarification_details", [])
        missing_fields = clarification_data.get("missing_fields", [])
        
        # Get smart clarification questions if available
        smart_questions = clarification_data.get("questions", [])
        smart_priorities = clarification_data.get("priorities", [])
        smart_reasoning = clarification_data.get("reasoning", "")

        # Check confirmation status
        is_confirmation = confirmation_data.get("is_confirmation", False)
        confirmation_type = confirmation_data.get("confirmation_type", "no_confirmation")
        confirmation_details = confirmation_data.get("confirmation_details", "")
        confirmation_confidence = confirmation_data.get("confidence", 0.0)

        # Determine response type based on clarification and confirmation
        if clarification_needed:
            response_type = "clarification_request"
        elif is_confirmation:
            response_type = "confirmation_response"
        elif rate_data.get("indicative_rate") or rate_data.get("rate_recommendation"):
            response_type = "quote_response"
        else:
            response_type = "standard_response"

        # Get special instructions from extraction
        special_instructions = extraction_data.get("special_instructions", "")
        special_requirements = extraction_data.get("special_requirements", "")
        
        # Get customer information for personalized salutation
        customer_name = extraction_data.get("customer_name", "")
        customer_company = extraction_data.get("customer_company", "")

        prompt = f"""
You are an expert logistics customer service representative. Generate a comprehensive, customer-friendly response using the available information from our processing agents.

ASSIGNED SALES PERSON:
Name: {assigned_sales_person['name']}
Designation: {assigned_sales_person['designation']}
Company: {assigned_sales_person['company']}
Email: {assigned_sales_person['email']}
Phone: {assigned_sales_person['phone']}
WhatsApp: {assigned_sales_person['whatsapp']}

ORIGINAL EMAIL:
Subject: {subject}
From: {sender}
Body: {email_text}

INFORMATION FROM AGENTS:
Classification: {json.dumps(classification_data, indent=2)}
Confirmation: {json.dumps(confirmation_data, indent=2)}
Extraction: {json.dumps(extraction_data, indent=2)}
Validation: {json.dumps(validation_data, indent=2)}
Smart Clarification: {json.dumps(clarification_data, indent=2)}
Container Standardization: {json.dumps(container_standardization_data, indent=2)}
Port Lookup: {json.dumps(port_lookup_data, indent=2)}
Rate: {json.dumps(rate_data, indent=2)}

SMART CLARIFICATION STATUS:
- Clarification needed: {clarification_needed}
- Smart questions: {json.dumps(smart_questions, indent=2)}
- Priorities: {json.dumps(smart_priorities, indent=2)}
- Reasoning: {smart_reasoning}
- Missing fields: {missing_fields}

CONFIRMATION STATUS:
- Is confirmation: {is_confirmation}
- Confirmation type: {confirmation_type}
- Confirmation details: {confirmation_details}
- Confidence: {confirmation_confidence}

CUSTOMER INFORMATION:
- Customer name: {customer_name}
- Customer company: {customer_company}

SPECIAL INSTRUCTIONS/REQUIREMENTS:
- Special instructions: {special_instructions}
- Special requirements: {special_requirements}

RATE INFORMATION:
- Indicative Rate: {rate_data.get('indicative_rate', 'Not available')}
- Rate Range: {rate_data.get('rate_recommendation', {}).get('rate_range', 'Not available')}
- Match Type: {rate_data.get('rate_recommendation', {}).get('match_type', 'Not available')}

RESPONSE STRATEGY:
1. SALUTATION: Use customer name if available (e.g., "Dear John"), otherwise use "Dear valued customer" or "Dear sir/madam"

2. If clarification is needed (clarification_needed = True):
   - Generate a clarification_request response
   - FIRST list all extracted and standardized details clearly
   - THEN ask for missing information using the smart_questions from smart clarification agent
   - Use the smart_questions array - these are already conversational and human-like
   - Follow the priorities order from smart_priorities
   - Use the smart_reasoning to explain why information is needed
   - Be friendly and helpful, not demanding
   - Set clarification_included = True

3. If customer is confirming something (is_confirmation = True):
   - Generate a confirmation_response
   - Acknowledge their confirmation
   - Provide next steps based on confirmation type
   - Be enthusiastic and professional
   - Set confirmation_handled = True

4. If no clarification needed and no confirmation:
   - Generate a standard_response or quote_response
   - Confirm extracted details
   - Include rate information if available
   - Ask for WhatsApp if not found

5. Always consider special instructions/requirements in your response

IMPORTANT: The response_type should match the actual response you generate!

IMPORTANT INSTRUCTIONS:
1. DO NOT mention validation details, port codes, or technical validation processes or forwarder assignment to the customer
2. ALWAYS include indicative rate if available, regardless of response type (clarification, confirmation, or standard response) - include it prominently in the email body as "Indicative Rate: [rate] USD (freight cost only, based on current market analytics)" - DO NOT include rate in the email subject
3. DO NOT use phrases like "before we proceed with providing a rate and assigning a forwarder"
4. Use port names from port lookup results (not from extraction) to show user what ports were identified
5. Include port names in the confirmation request so user can validate if port codes were picked correctly
6. Use standardized container type from container standardization agent (not from extraction) to show user what container type was identified
7. Summarize shipment details in a clear, bullet-pointed format that's easy for customers to understand
8. Use a friendly, empathetic, and professional tone - do not sound like a bot
9. Focus on customer needs and next steps
10. Always include clear next steps and a polite closing
11. Sign the email with the assigned sales person's name, designation, and company
12. Include the sales person's contact information in the signature
13. Address special instructions/requirements if provided
14. For FCL shipments, don't ask for volume unless explicitly needed
15. For container types, if FCL is mentioned, ask if they prefer 20 or 40 DC
16. Ask for commodity first, then dangerous goods only if commodity is provided
17. Don't ask for port validation - let the system handle this automatically
18. ALWAYS include the indicative rate in ALL response types when available
19. Use the smart_questions from smart clarification agent - they are already conversational and human-like
20. ALWAYS include the email chain at the bottom showing the original email and your response

RESPONSE EXAMPLES:

CLARIFICATION REQUEST:
"Dear [customer_name if available, otherwise "valued customer"],

Thank you for your logistics request. Here's what I understand from your request:

• Origin: [origin_port_name]
• Destination: [destination_port_name]
• Shipment Type: [shipment_type]
• Container Type: [standardized_container_type]
• Quantity: [quantity]
• Weight: [weight]
• Commodity: [commodity]

[If rate available: Indicative Rate: [rate] USD (freight cost only, based on current market analytics)]

To provide you with the most accurate quote and service, I need a few additional details:

[Use the smart_questions from smart clarification agent - they are already conversational, for example:]
• Could you please let us know when you'd like to ship this cargo?
• Could you please specify the type of goods you wish to ship? (e.g., electronics, textiles, machinery, food products)

[If smart_reasoning is available, use it to explain why the information is needed]

Once you provide these details, I'll be able to give you a comprehensive quote and arrange everything for you.

Best regards,
{assigned_sales_person['name']}

---
Email Chain:
From: {sender}
Subject: {subject}
Date: [current_date]

{email_text}

---
Reply:
From: {assigned_sales_person['email']}
Subject: Re: {subject}
Date: [current_date]

[Your generated response body goes here]"

CONFIRMATION RESPONSE:
"Dear [customer_name if available, otherwise "valued customer"],

Excellent! I'm pleased to confirm that I've received your [confirmation_type] for [confirmation_details].

[If rate available: Indicative Rate: [rate] USD (freight cost only, based on current market analytics)]

[Next steps based on confirmation type]

I'll proceed with [specific action] and will keep you updated throughout the process.

Best regards,
{assigned_sales_person['name']}

---
Email Chain:
From: {sender}
Subject: {subject}
Date: [current_date]

{email_text}

---
Reply:
From: {assigned_sales_person['email']}
Subject: Re: {subject}
Date: [current_date]

[Your generated response body goes here]"

STANDARD RESPONSE:
"Dear [customer_name if available, otherwise "valued customer"],

Thank you for your logistics request. Here's a summary of your shipment details:
• Origin: [origin_port_name]
• Destination: [destination_port_name]
• Container Type: [standardized_container_type]
• Quantity: [quantity]
• Weight: [weight]
• Commodity: [commodity]

[If rate available: Indicative Rate: [rate] USD (freight cost only, based on current market analytics)]

Please confirm these details are correct so I can proceed with your booking.

Best regards,
{assigned_sales_person['name']}

---
Email Chain:
From: {sender}
Subject: {subject}
Date: [current_date]

{email_text}

---
Reply:
From: {assigned_sales_person['email']}
Subject: Re: {subject}
Date: [current_date]

[Your generated response body goes here]"
"""

        # Ensure model is always a string
        model = self.config.get("model_name") or "gpt-4.1"

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                tools=[{"type": "function", "function": function_schema}],  # type: ignore
                tool_choice={"type": "function", "function": {"name": function_schema["name"]}},
                temperature=0.1,
                max_tokens=800
            )  # type: ignore
            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if not tool_calls:
                raise Exception("No tool_calls in LLM response")
            tool_args = tool_calls[0].function.arguments
            if isinstance(tool_args, str):
                tool_args = json.loads(tool_args)
            result = dict(tool_args)
            result["agent_name"] = self.agent_name
            result["agent_id"] = self.agent_id
            result["processed_at"] = self._now_iso()
            result["status"] = "success"
            
            # Add assigned sales person information
            result["assigned_sales_person"] = assigned_sales_person
            
            return result
        except Exception as e:
            self.logger.error(f"LLM response generation failed: {e}")
            return {"error": f"LLM response generation failed: {str(e)}"}

    def _now_iso(self):
        import datetime
        return datetime.datetime.utcnow().isoformat()
