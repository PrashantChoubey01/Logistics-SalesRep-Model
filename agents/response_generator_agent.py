import os
import sys
import json
import random
from typing import Dict, Any
from .base_agent import BaseAgent

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
        """Generate customer-friendly response email using all agent outputs."""
        print("📧 RESPONSE_GENERATOR: Starting response generation...")
        
        if not self.client:
            return {"error": "LLM client not initialized"}

        # Extract all input data
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
        
        # Assign a sales person for the response
        assigned_sales_person = random.choice(self.sales_team)
        print(f"📧 RESPONSE_GENERATOR: Assigned sales person: {assigned_sales_person['name']}")
        
        # Simplified function schema for faster processing
        function_schema = {
            "name": "generate_response",
            "description": "Generate a customer-friendly logistics response email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "response_subject": {"type": "string", "description": "Email subject line"},
                    "response_body": {"type": "string", "description": "Email body, friendly and professional"},
                    "response_type": {"type": "string", "enum": ["clarification_request", "confirmation_response", "standard_response", "quote_response", "escalation_response"], "description": "Type of response generated"},
                    "sales_person_name": {"type": "string", "description": "Name of the assigned sales person"},
                    "sales_person_email": {"type": "string", "description": "Email of the sales person"},
                    "sales_person_phone": {"type": "string", "description": "Phone number of the sales person"}
                },
                "required": ["response_subject", "response_body", "response_type", "sales_person_name", "sales_person_email", "sales_person_phone"]
            }
        }

        # Check if clarification is needed
        clarification_needed = clarification_data.get("clarification_needed", False)
        clarification_message = clarification_data.get("clarification_message", "")
        clarification_details = clarification_data.get("clarification_details", [])
        missing_fields = clarification_data.get("missing_fields", [])
        
        # Get validation results for intelligent response generation
        validation_data = input_data.get("validation_data", {})
        validation_results = validation_data.get("validation_results", {})
        overall_validation = validation_data.get("overall_validation", {})
        
        # Get missing fields from validation
        missing_fields = overall_validation.get("missing_fields", [])
        critical_issues = overall_validation.get("critical_issues", [])
        warnings = overall_validation.get("warnings", [])
        
        # Apply FCL/LCL business rules to missing fields
        missing_fields = self._apply_fcl_lcl_rules_to_missing_fields(missing_fields, extraction_data)
        
        # Analyze missing fields for better response generation
        missing_fields = self._analyze_missing_fields_for_response(extraction_data, missing_fields)
        
        # Get smart clarification questions if available
        smart_questions = clarification_data.get("questions", [])
        smart_priorities = clarification_data.get("priorities", [])
        smart_reasoning = clarification_data.get("reasoning", "")

        # Check confirmation status
        is_confirmation = confirmation_data.get("is_confirmation", False)
        confirmation_type = confirmation_data.get("confirmation_type", "no_confirmation")
        confirmation_details = confirmation_data.get("confirmation_details", "")
        confirmation_confidence = confirmation_data.get("confidence", 0.0)

        # Get next action decision for intelligent response generation
        # The next action data comes from the previous agent in the workflow
        next_action_data = input_data.get("next_action_data", {})
        if not next_action_data:
            # Try to get from decision result if available
            decision_result = input_data.get("decision_result", {})
            if decision_result:
                next_action_data = decision_result
        
        # Ensure next_action_data is a dictionary
        if not isinstance(next_action_data, dict):
            next_action_data = {}
        
        next_action = next_action_data.get("next_action", "")
        response_type_decision = next_action_data.get("response_type", "")
        
        # Determine response type based on next action decision (priority) and fallback to existing logic
        if next_action == "send_clarification_request":
            response_type = "clarification_request"
        elif next_action == "send_confirmation_request":
            response_type = "confirmation_response"
        elif next_action == "booking_details_confirmed_assign_forwarders":
            response_type = "confirmation_acknowledgment"  # Send acknowledgment to customer
        elif next_action == "escalate_confusing_email":
            response_type = "escalation_response"
        elif next_action == "send_forwarder_acknowledgment":
            response_type = "forwarder_acknowledgment"
        elif next_action == "collate_rates_and_send_to_sales":
            response_type = "sales_notification"  # This will trigger sales notification response
        elif next_action == "notify_sales_team":
            response_type = "sales_notification"
        elif next_action == "send_status_update":
            response_type = "status_update"
        elif response_type_decision:  # Use decision from next action agent
            response_type = response_type_decision
        elif clarification_needed:  # Fallback to existing logic
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
        
        # Get enriched data with port names
        enriched_data = input_data.get("enriched_data", {})
        rate_data_enriched = enriched_data.get("rate_data", {})
        
        # Format extracted data for better prompt generation
        formatted_data = self._format_extracted_data_for_prompt(extraction_data)
        
        # Get appropriate response template
        response_template = self._get_response_template(extraction_data, missing_fields, response_type)
        
        # Use enriched port names if available, otherwise fall back to formatted data
        origin_port_name = rate_data_enriched.get("origin_name", formatted_data.get("origin", ""))
        destination_port_name = rate_data_enriched.get("destination_name", formatted_data.get("destination", ""))
        
        # Use standardized container type if available
        container_standardization = enriched_data.get("container_standardization", {})
        standardized_container_type = container_standardization.get("standard_type", formatted_data.get("container_type", ""))

        # Enhanced prompt with better business logic
        prompt = f"""
Generate a customer-friendly logistics response email.

SALES PERSON: {assigned_sales_person['name']} ({assigned_sales_person['email']}, {assigned_sales_person['phone']})

CUSTOMER: {customer_name or 'Valued Customer'} from {customer_company or 'your company'}

RESPONSE TYPE: {response_type}
RESPONSE TEMPLATE: {response_template}

EXTRACTED DATA:
- Origin: {origin_port_name}
- Destination: {destination_port_name}
- Shipment Type: {formatted_data.get('shipment_type')}
- Container: {standardized_container_type or formatted_data.get('container_type')}
- Weight: {formatted_data.get('weight')}
- Volume: {formatted_data.get('volume')}
- Commodity: {formatted_data.get('commodity')}
- Shipment Date: {formatted_data.get('shipment_date')}
- Quantity: {formatted_data.get('quantity')}

MISSING FIELDS: {missing_fields if missing_fields else 'None'}

RATE: {rate_data.get('indicative_rate', 'Not available')}

RESPONSE STRATEGY:
1. **FCL Shipments**: Ask for container type if missing, NEVER ask for volume
2. **LCL Shipments**: Ask for both weight AND volume if missing
3. **Port Information**: If only country provided, ask for specific ports
4. **Be Specific**: Mention exactly what information is needed
5. **Professional Sales Tone**: Warm, friendly, and professional like a real sales person
6. **Natural Flow**: Sound human, not robotic
7. **Rate Information**: Include if available, mention if not available

RESPONSE FORMATTING:
- Use structured format with bullet points for shipment details
- Keep paragraphs natural and conversational
- Avoid robotic phrases like "Next steps:" or "Please respond to this email"
- Make it sound like a real sales person writing to a client

CONFIRMATION LOGIC:
- **CONFIRMATION_REQUEST**: Present details naturally and ask for confirmation
- **CONFIRMATION_ACKNOWLEDGMENT**: Thank customer warmly and proceed
- Ask for confirmation in a friendly, professional way

SPECIFIC INSTRUCTIONS:
- Write like a professional sales person, not a bot
- Use warm, friendly tone while maintaining professionalism
- Avoid robotic phrases like "We hope this email finds you well" or "Please respond to this email"
- Be conversational and natural
- If asking for container type (FCL), suggest common types: 20GP, 40GP, 40HC
- If asking for ports, request SPECIFIC port names (e.g., "Shanghai", "Los Angeles", "New York") not just countries
- If asking for weight/volume (LCL), specify units (tons, CBM)
- Keep response concise and to the point
- Be very specific about what information is needed
- For ports, ask for the exact port/city name, not just "port name"
- Use bullet points for shipment details but keep the rest conversational

**RESPONSE EXAMPLES:**

**CONFIRMATION_REQUEST (Natural Sales Style):**
"Hi [Customer Name],

Thanks for reaching out about your shipment from [Origin] to [Destination]. I've reviewed your details and wanted to confirm everything before we proceed:

* Origin: [Origin]
* Destination: [Destination]
* Shipment Type: [Type]
* Container: [Container Type]
* Weight: [Weight]
* Commodity: [Commodity]
* Shipment Date: [Date]
* Quantity: [Quantity]

Could you please confirm these details are correct? Once you give me the green light, I'll get started on securing the best rates for you.

Feel free to reach out if you need any adjustments or have questions.

Best regards,
[Sales Person Name]"

**CLARIFICATION_REQUEST (Natural Sales Style):**
"Hi [Customer Name],

Thanks for your inquiry about shipping from [Origin] to [Destination]. I just need a couple of details to get you the best rates:

* [Missing field 1]: [Specific request]
* [Missing field 2]: [Specific request]

Once you provide these details, I'll be able to give you a comprehensive quote right away.

Looking forward to hearing from you!

Best regards,
[Sales Person Name]"

**CONFIRMATION_ACKNOWLEDGMENT (Natural Sales Style):**
"Hi [Customer Name],

Perfect! Thanks for confirming the details. I've got everything I need to proceed with your shipment from [Origin] to [Destination].

* Origin: [Origin]
* Destination: [Destination]
* Shipment Type: [Type]
* Container: [Container Type]
* Weight: [Weight]
* Commodity: [Commodity]
* Shipment Date: [Date]
* Quantity: [Quantity]

I'm now working on securing the best rates and arrangements for your shipment. I'll be in touch with a comprehensive quote and next steps shortly.

Regarding your question about insurance coverage for the electronics - yes, we can definitely arrange that. I'll include insurance options in the quote I send you.

Thanks for choosing us for your logistics needs!

Best regards,
[Sales Person Name]"

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
            
            print(f"✅ RESPONSE_GENERATOR: Response generated successfully")
            print(f"📧 RESPONSE_GENERATOR: Response type: {result.get('response_type', 'unknown')}")
            
            return result
        except Exception as e:
            self.logger.error(f"LLM response generation failed: {e}")
            print(f"❌ RESPONSE_GENERATOR: Error occurred - {str(e)}")
            return {"error": f"LLM response generation failed: {str(e)}"}

    def _now_iso(self):
        import datetime
        return datetime.datetime.utcnow().isoformat()

    def _apply_fcl_lcl_rules_to_missing_fields(self, missing_fields: list, extracted_data: dict) -> list:
        """Apply FCL/LCL business rules to filter missing fields."""
        # Check if this is an FCL shipment (has container type)
        container_type = extracted_data.get("container_type", "")
        has_container_type = container_type and str(container_type).strip().upper() in [
            "20GP", "40GP", "40HC", "20RF", "40RF", "20DC", "40DC", "20FT", "40FT"
        ]
        
        if has_container_type:
            # This is an FCL shipment - volume should NOT be required
            if "volume" in missing_fields:
                missing_fields.remove("volume")
                print(f"✅ RESPONSE_GENERATOR: Removed volume from missing fields (FCL shipment with container type: {container_type})")
        
        return missing_fields

    def _analyze_missing_fields_for_response(self, extracted_data: dict, missing_fields: list) -> list:
        """Analyze what's actually missing vs what should be asked for based on shipment type."""
        shipment_type = extracted_data.get("shipment_type", "")
        
        # FCL Logic
        if shipment_type == "FCL":
            # For FCL: container_type is mandatory, weight/volume optional
            if not extracted_data.get("container_type"):
                if "container_type" not in missing_fields:
                    missing_fields.append("container_type")
            # Remove volume/weight from missing fields for FCL
            if "volume" in missing_fields:
                missing_fields.remove("volume")
                print(f"✅ RESPONSE_GENERATOR: Removed volume from missing fields (FCL shipment)")
            if "weight" in missing_fields:
                missing_fields.remove("weight")
                print(f"✅ RESPONSE_GENERATOR: Removed weight from missing fields (FCL shipment)")
        
        # LCL Logic  
        elif shipment_type == "LCL":
            # For LCL: weight and volume are mandatory, no container type
            if not extracted_data.get("weight"):
                if "weight" not in missing_fields:
                    missing_fields.append("weight")
            if not extracted_data.get("volume"):
                if "volume" not in missing_fields:
                    missing_fields.append("volume")
            # Remove container_type from missing fields for LCL
            if "container_type" in missing_fields:
                missing_fields.remove("container_type")
                print(f"✅ RESPONSE_GENERATOR: Removed container_type from missing fields (LCL shipment)")
        
        # Port specificity logic
        if not extracted_data.get("origin_name") and extracted_data.get("origin_country"):
            if "origin_name" not in missing_fields:
                missing_fields.append("origin_name")
        if not extracted_data.get("destination_name") and extracted_data.get("destination_country"):
            if "destination_name" not in missing_fields:
                missing_fields.append("destination_name")
        
        return missing_fields

    def _format_extracted_data_for_prompt(self, extracted_data: dict) -> dict:
        """Format extracted data with proper NULL handling for better prompt generation."""
        formatted = {}
        
        # Handle port information intelligently
        if extracted_data.get("origin_name"):
            formatted["origin"] = extracted_data["origin_name"]
        elif extracted_data.get("origin_country"):
            formatted["origin"] = f"country: {extracted_data['origin_country']}"
        else:
            formatted["origin"] = "Not specified"
        
        if extracted_data.get("destination_name"):
            formatted["destination"] = extracted_data["destination_name"]
        elif extracted_data.get("destination_country"):
            formatted["destination"] = f"country: {extracted_data['destination_country']}"
        else:
            formatted["destination"] = "Not specified"
        
        # Handle other fields
        formatted["shipment_type"] = extracted_data.get("shipment_type", "Not specified")
        formatted["container_type"] = extracted_data.get("container_type", "Not specified")
        formatted["weight"] = extracted_data.get("weight", "Not specified")
        formatted["volume"] = extracted_data.get("volume", "Not specified")
        formatted["commodity"] = extracted_data.get("commodity", "Not specified")
        formatted["shipment_date"] = extracted_data.get("shipment_date", "Not specified")
        formatted["quantity"] = extracted_data.get("quantity", "Not specified")
        formatted["dangerous_goods"] = extracted_data.get("dangerous_goods", False)
        formatted["special_requirements"] = extracted_data.get("special_requirements", "")
        formatted["insurance"] = extracted_data.get("insurance", False)
        formatted["packaging"] = extracted_data.get("packaging", "")
        formatted["customs_clearance"] = extracted_data.get("customs_clearance", False)
        
        return formatted

    def _get_response_template(self, extracted_data: dict, missing_fields: list, response_type: str) -> str:
        """Get appropriate response template based on data completeness and type."""
        shipment_type = extracted_data.get("shipment_type", "")
        
        if missing_fields:
            if "container_type" in missing_fields and shipment_type == "FCL":
                return "FCL_CLARIFICATION_CONTAINER"
            elif ("weight" in missing_fields or "volume" in missing_fields) and shipment_type == "LCL":
                return "LCL_CLARIFICATION_WEIGHT_VOLUME"
            elif "origin_name" in missing_fields or "destination_name" in missing_fields:
                return "CLARIFICATION_PORTS"
            elif "shipment_date" in missing_fields:
                return "CLARIFICATION_DATE"
            else:
                return "GENERAL_CLARIFICATION"
        else:
            if response_type == "confirmation_response":
                return "CONFIRMATION_REQUEST"  # Ask customer to confirm details
            elif response_type == "confirmation_acknowledgment":
                return "CONFIRMATION_ACKNOWLEDGMENT"  # Thank for confirmation
            elif response_type == "quote_response":
                return "QUOTE_WITH_RATE"
            else:
                return "STANDARD_RESPONSE"
