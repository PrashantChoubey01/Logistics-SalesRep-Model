"""Enhanced Response Generator Agent: Generates comprehensive responses using all agent inputs"""

import os
import sys
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class ResponseGeneratorAgent(BaseAgent):
    """Enhanced agent to generate context-aware responses using comprehensive agent inputs"""

    def __init__(self):
        super().__init__("response_generator_agent")
        
        # Response templates for different scenarios
        self.response_templates = {
            "quote_request": {
                "subject_template": "Re: {original_subject} - Shipping Quote {route}",
                "greeting": "Dear valued customer,",
                "closing": "Best regards,\nLogistics Team"
            },
            "confirmation": {
                "subject_template": "Booking Confirmation - {route}",
                "greeting": "Dear customer,",
                "closing": "Thank you for choosing our services.\n\nBest regards,\nBooking Team"
            },
            "clarification": {
                "subject_template": "Re: {original_subject} - Additional Information Required",
                "greeting": "Dear customer,",
                "closing": "Thank you for your patience.\n\nBest regards,\nCustomer Service Team"
            },
            "rate_available": {
                "subject_template": "Shipping Quote - {route} - Rate: {rate_range}",
                "greeting": "Dear valued customer,",
                "closing": "We look forward to serving you.\n\nBest regards,\nSales Team"
            }
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced processing using comprehensive agent inputs:
        - classification_data: Email type and confidence
        - extraction_data: Shipment details
        - validation_data: Validation results and missing fields
        - clarification_data: Clarification requirements
        - confirmation_data: Confirmation detection results
        - rate_data: Rate recommendations
        - port_data: Port lookup results
        - container_data: Container standardization
        - country_data: Country information
        """
        
        # Extract all agent inputs
        classification_data = input_data.get("classification_data", {})
        extraction_data = input_data.get("extraction_data", {})
        validation_data = input_data.get("validation_data", {})
        clarification_data = input_data.get("clarification_data", {})
        confirmation_data = input_data.get("confirmation_data", {})
        rate_data = input_data.get("rate_data", {})
        port_data = input_data.get("port_data", {})
        container_data = input_data.get("container_data", {})
        country_data = input_data.get("country_data", {})
        
        # Original email context
        original_subject = input_data.get("subject", "")
        original_email = input_data.get("email_text", "")
        thread_id = input_data.get("thread_id", "")
        
        # Determine response type and generate appropriate response
        response_type = self._determine_response_type(
            classification_data, confirmation_data, clarification_data, validation_data
        )
        
        if self.client:
            print("[INFO] Using enhanced LLM function calling for response generation")
            try:
                return self._enhanced_llm_function_call(
                    response_type=response_type,
                    classification_data=classification_data,
                    extraction_data=extraction_data,
                    validation_data=validation_data,
                    clarification_data=clarification_data,
                    confirmation_data=confirmation_data,
                    rate_data=rate_data,
                    port_data=port_data,
                    container_data=container_data,
                    country_data=country_data,
                    original_subject=original_subject,
                    original_email=original_email,
                    thread_id=thread_id
                )
            except Exception as e:
                print(f"[WARN] Enhanced LLM function call failed: {e}")
                return self._fallback_response_generation(
                    response_type, extraction_data, clarification_data, rate_data, original_subject
                )
        else:
            print("[INFO] LLM client not available, using fallback response generation")
            return self._fallback_response_generation(
                response_type, extraction_data, clarification_data, rate_data, original_subject
            )

    def _determine_response_type(self, classification_data, confirmation_data, clarification_data, validation_data):
        """Determine the appropriate response type based on agent outputs"""
        
        # Check if confirmation is detected
        if confirmation_data.get("is_confirmation", False):
            return "confirmation"
        
        # Check if clarification is needed
        if clarification_data.get("clarification_needed", False):
            return "clarification"
        
        # Check email classification
        email_type = classification_data.get("email_type", "")
        if email_type in ["logistics_request", "quote_request"]:
            return "quote_request"
        elif email_type == "confirmation_reply":
            return "confirmation"
        
        # Default to quote request
        return "quote_request"

    def _enhanced_llm_function_call(self, **kwargs):
        """Enhanced LLM function call with comprehensive context"""
        
        function_schema = {
            "name": "generate_comprehensive_response",
            "description": "Generate a comprehensive response using all available agent data",
            "parameters": {
                "type": "object",
                "properties": {
                    "response_type": {
                        "type": "string",
                        "description": "Type of response (quote_request, confirmation, clarification, rate_available)"
                    },
                    "response_subject": {
                        "type": "string",
                        "description": "Professional subject line for the response"
                    },
                    "response_body": {
                        "type": "string",
                        "description": "Complete response message body"
                    },
                    "tone": {
                        "type": "string",
                        "description": "Tone of the message (professional, friendly, urgent, apologetic)"
                    },
                    "key_information_included": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of key information included in response (route, rate, container_type, etc.)"
                    },
                    "attachments_needed": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of suggested attachments"
                    },
                    "next_steps": {
                        "type": "string",
                        "description": "Clear next steps for the customer"
                    },
                    "urgency_level": {
                        "type": "string",
                        "description": "Response urgency (low, medium, high)"
                    },
                    "follow_up_required": {
                        "type": "boolean",
                        "description": "Whether follow-up is required"
                    },
                    "estimated_response_time": {
                        "type": "string",
                        "description": "Estimated time for next response if follow-up needed"
                    }
                },
                "required": [
                    "response_type", "response_subject", "response_body", "tone", 
                    "key_information_included", "attachments_needed", "next_steps",
                    "urgency_level", "follow_up_required"
                ]
            }
        }

        # Build comprehensive context for LLM
        context = self._build_comprehensive_context(**kwargs)
        
        prompt = f"""
You are an expert logistics customer service representative. Generate a comprehensive, professional response using ALL available information from our processing agents.

IMPORTANT INSTRUCTIONS:
1. Use ALL relevant information from the agent outputs
2. If rate information is available, include it prominently
3. If clarification is needed, ask specific questions
4. If confirmation is detected, acknowledge appropriately
5. Include route information (origin → destination) when available
6. Mention container type and quantity when known
7. Address any validation issues or missing information
8. Be professional, helpful, and specific
9. Include clear next steps for the customer

CONTEXT FROM ALL AGENTS:
{json.dumps(context, indent=2)}

Generate a response that:
- Acknowledges the customer's request specifically
- Uses the extracted shipment details
- Includes rate information if available
- Addresses any clarification needs
- Provides clear next steps
- Maintains a professional, helpful tone
"""

        response = self.client.chat.completions.create(
            model=self.config.get("model_name", "databricks-meta-llama-3-3-70b-instruct"),
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "type": "function",
                "function": function_schema
            }],
            tool_choice={"type": "function", "function": {"name": function_schema["name"]}},
            temperature=0.1,
            max_tokens=800
        )
        
        tool_calls = getattr(response.choices[0].message, "tool_calls", None)
        if not tool_calls:
            raise Exception("No tool_calls in LLM response")
        
        tool_args = tool_calls[0].function.arguments
        if isinstance(tool_args, str):
            tool_args = json.loads(tool_args)
        
        result = dict(tool_args)
        result["extraction_method"] = "enhanced_databricks_llm_function_call"
        result["context_used"] = context
        
        return result

    def _build_comprehensive_context(self, **kwargs):
        """Build comprehensive context from all agent outputs"""
        
        context = {
            "original_request": {
                "subject": kwargs.get("original_subject", ""),
                "email_text": kwargs.get("original_email", "")[:200] + "..." if len(kwargs.get("original_email", "")) > 200 else kwargs.get("original_email", ""),
                "thread_id": kwargs.get("thread_id", "")
            },
            "response_type": kwargs.get("response_type", "quote_request")
        }
        
        # Classification information
        classification_data = kwargs.get("classification_data", {})
        if classification_data and classification_data.get("status") == "success":
            context["classification"] = {
                "email_type": classification_data.get("email_type", "unknown"),
                "confidence": classification_data.get("confidence", 0),
                "intent": classification_data.get("intent", "unknown")
            }
        
        # Extraction information
        extraction_data = kwargs.get("extraction_data", {})
        if extraction_data and extraction_data.get("status") == "success":
            context["shipment_details"] = {
                "origin": extraction_data.get("origin", "Not specified"),
                "destination": extraction_data.get("destination", "Not specified"),
                "origin_port_code": extraction_data.get("origin_port_code", ""),
                "destination_port_code": extraction_data.get("destination_port_code", ""),
                "shipment_type": extraction_data.get("shipment_type", "Not specified"),
                "container_type": extraction_data.get("container_type", "Not specified"),
                "standardized_container_type": extraction_data.get("standardized_container_type", ""),
                "quantity": extraction_data.get("quantity", "Not specified"),
                "weight": extraction_data.get("weight", "Not specified"),
                "volume": extraction_data.get("volume", "Not specified"),
                "shipment_date": extraction_data.get("shipment_date", "Not specified"),
                "commodity": extraction_data.get("commodity", "Not specified"),
                "dangerous_goods": extraction_data.get("dangerous_goods", False),
                "special_requirements": extraction_data.get("special_requirements", "None")
            }
            
            # Build route string
            origin = extraction_data.get("origin", "")
            destination = extraction_data.get("destination", "")
            if origin and destination:
                context["route"] = f"{origin} → {destination}"
            elif extraction_data.get("origin_port_code") and extraction_data.get("destination_port_code"):
                context["route"] = f"{extraction_data.get('origin_port_code')} → {extraction_data.get('destination_port_code')}"
        
        # Validation information
        validation_data = kwargs.get("validation_data", {})
        if validation_data and validation_data.get("status") == "success":
            context["validation"] = {
                "overall_validity": validation_data.get("overall_validity", False),
                "missing_fields": validation_data.get("missing_fields", []),
                "validation_errors": validation_data.get("validation_errors", []),
                "warnings": validation_data.get("warnings", []),
                "completeness_score": validation_data.get("completeness_score", 0)
            }
        
        # Clarification information
        clarification_data = kwargs.get("clarification_data", {})
        if clarification_data and clarification_data.get("status") == "success":
            context["clarification"] = {
                "clarification_needed": clarification_data.get("clarification_needed", False),
                "clarification_message": clarification_data.get("clarification_message", ""),
                "clarification_details": clarification_data.get("clarification_details", []),
                "missing_fields": clarification_data.get("missing_fields", [])
            }
        
        # Confirmation information
        confirmation_data = kwargs.get("confirmation_data", {})
        if confirmation_data and confirmation_data.get("status") == "success":
            context["confirmation"] = {
                "is_confirmation": confirmation_data.get("is_confirmation", False),
                "confirmation_type": confirmation_data.get("confirmation_type", ""),
                "confirmation_details": confirmation_data.get("confirmation_details", ""),
                "reasoning": confirmation_data.get("reasoning", "")
            }
        
        # Rate information
        rate_data = kwargs.get("rate_data", {})
        if rate_data and rate_data.get("status") == "success":
            rate_recommendation = rate_data.get("rate_recommendation", {})
            if rate_recommendation.get("match_type") == "exact_match":
                context["rate_information"] = {
                    "rate_available": True,
                    "recommended_rate": rate_recommendation.get("recommended_rate", 0),
                    "rate_range": rate_recommendation.get("rate_range", ""),
                    "confidence": rate_recommendation.get("confidence", ""),
                    "total_rates_found": rate_recommendation.get("total_rates_found", 0),
                    "match_type": rate_recommendation.get("match_type", "")
                }
            else:
                context["rate_information"] = {
                    "rate_available": False,
                    "match_type": rate_recommendation.get("match_type", "no_match"),
                    "message": rate_recommendation.get("message", "No rates available"),
                    "suggestions": rate_recommendation.get("suggestions", {})
                }
        
        # Port information
        port_data = kwargs.get("port_data", {})
        if port_data:
            context["port_information"] = {
                "origin_port": port_data.get("origin", {}),
                "destination_port": port_data.get("destination", {})
            }
        
        # Container information
        container_data = kwargs.get("container_data", {})
        if container_data and container_data.get("status") == "success":
            context["container_information"] = {
                "standardized_container_type": container_data.get("standardized_container_type", ""),
                "container_specifications": container_data.get("container_specifications", {}),
                "validation_status": container_data.get("validation_status", "")
            }
        
        # Country information
        country_data = kwargs.get("country_data", {})
        if country_data:
            context["country_information"] = {
                "origin_country": country_data.get("origin", {}),
                "destination_country": country_data.get("destination", {})
            }
        
        return context

    def _fallback_response_generation(self, response_type, extraction_data, clarification_data, rate_data, original_subject):
        """Enhanced fallback response generation with better context awareness"""
        
        # Extract key information
        origin = extraction_data.get("origin", "your specified origin")
        destination = extraction_data.get("destination", "your specified destination")
        container_type = extraction_data.get("container_type", "container")
        quantity = extraction_data.get("quantity", "")
        
        # Build route string
        route = f"{origin} to {destination}" if origin != "your specified origin" and destination != "your specified destination" else "your specified route"
        
        # Generate response based on type
        if response_type == "clarification":
            return self._generate_clarification_response(clarification_data, original_subject, route)
        elif response_type == "confirmation":
            return self._generate_confirmation_response(extraction_data, original_subject, route)
        elif response_type == "quote_request":
            return self._generate_quote_response(extraction_data, rate_data, original_subject, route)
        else:
            return self._generate_default_response(extraction_data, original_subject, route)

    def _generate_clarification_response(self, clarification_data, original_subject, route):
        """Generate clarification request response"""
        
        clarification_message = clarification_data.get("clarification_message", "")
        missing_fields = clarification_data.get("missing_fields", [])
        clarification_details = clarification_data.get("clarification_details", [])
        
        if clarification_message:
            response_body = f"""Dear valued customer,

Thank you for your shipping inquiry regarding {route}.

{clarification_message}

"""
            # Add specific questions if available
            if clarification_details:
                response_body += "Specifically, we need:\n\n"
                for detail in clarification_details:
                    field = detail.get("field", "")
                    prompt = detail.get("prompt", "")
                    response_body += f"• {prompt}\n"
                response_body += "\n"
        else:
            response_body = f"""Dear valued customer,

Thank you for your shipping inquiry regarding {route}.

To provide you with an accurate quote, we need some additional information:

"""
            for field in missing_fields:
                response_body += f"• {field.replace('_', ' ').title()}\n"
            response_body += "\n"
        
        response_body += """Please provide this information so we can process your request promptly.

Thank you for your patience.

Best regards,
Customer Service Team"""

        return {
            "response_type": "clarification",
            "response_subject": f"Re: {original_subject} - Additional Information Required",
            "response_body": response_body,
            "tone": "professional",
            "key_information_included": ["clarification_request", "missing_fields"],
            "attachments_needed": [],
            "next_steps": "Customer to provide missing information",
            "urgency_level": "medium",
            "follow_up_required": True,
            "estimated_response_time": "Within 24 hours of receiving information",
            "extraction_method": "fallback_clarification"
        }

    def _generate_confirmation_response(self, extraction_data, original_subject, route):
        """Generate booking confirmation response"""
        
        container_info = ""
        if extraction_data.get("quantity") and extraction_data.get("container_type"):
            container_info = f" for {extraction_data.get('quantity')}x{extraction_data.get('container_type')}"
        
        response_body = f"""Dear customer,

Thank you for your confirmation regarding the shipment{container_info} from {route}.

We have received your confirmation and are processing your booking. Our team will contact you shortly with the next steps and documentation requirements.

Shipment Details Confirmed:
• Route: {route}
• Container Type: {extraction_data.get('container_type', 'As specified')}
• Quantity: {extraction_data.get('quantity', 'As specified')}
• Commodity: {extraction_data.get('commodity', 'As specified')}

Our operations team will be in touch within 24 hours to coordinate the pickup and provide you with the necessary documentation.

Thank you for choosing our services.

Best regards,
Booking Team"""

        return {
            "response_type": "confirmation",
            "response_subject": f"Booking Confirmation - {route}",
            "response_body": response_body,
            "tone": "professional",
            "key_information_included": ["confirmation_acknowledgment", "shipment_details", "next_steps"],
            "attachments_needed": ["booking_confirmation", "documentation_checklist"],
            "next_steps": "Operations team will contact within 24 hours",
            "urgency_level": "high",
            "follow_up_required": True,
            "estimated_response_time": "Within 24 hours",
            "extraction_method": "fallback_confirmation"
        }

    def _generate_quote_response(self, extraction_data, rate_data, original_subject, route):
        """Generate quote response with rate information if available"""
        
        # Check if rate information is available
        rate_available = False
        rate_info = ""
        
        if rate_data and rate_data.get("status") == "success":
            rate_recommendation = rate_data.get("rate_recommendation", {})
            if rate_recommendation.get("match_type") == "exact_match":
                rate_available = True
                recommended_rate = rate_recommendation.get("recommended_rate", 0)
                rate_range = rate_recommendation.get("rate_range", "")
                confidence = rate_recommendation.get("confidence", "")
                
                rate_info = f"""
INDICATIVE RATE INFORMATION:
• Recommended Rate: ${recommended_rate:,.2f} USD per container
• Rate Range: {rate_range}
• Confidence Level: {confidence.title()}
• Based on current market conditions

Please note: This is an indicative rate. Final pricing will be confirmed upon booking.
"""
        
        # Build shipment summary
        shipment_summary = self._build_shipment_summary(extraction_data)
        
        if rate_available:
            response_body = f"""Dear valued customer,

Thank you for your shipping inquiry. We are pleased to provide you with an indicative quote for your shipment from {route}.

SHIPMENT SUMMARY:
{shipment_summary}
{rate_info}

NEXT STEPS:
1. Review the quote and shipment details
2. Confirm your booking by replying to this email
3. Our operations team will contact you for documentation
4. Schedule pickup at your convenience

This quote is valid for 7 days. Please let us know if you have any questions or would like to proceed with the booking.

We look forward to serving you.

Best regards,
Sales Team"""
        else:
            response_body = f"""Dear valued customer,

Thank you for your shipping inquiry regarding your shipment from {route}.

SHIPMENT SUMMARY:
{shipment_summary}

We are currently preparing your customized quote. Our team will review your requirements and provide you with competitive pricing within 24 hours.

WHAT HAPPENS NEXT:
1. Our pricing team will analyze your shipment requirements
2. We will provide you with a detailed quote within 24 hours
3. Upon your approval, we will proceed with booking arrangements
4. Our operations team will coordinate pickup and documentation

If you have any urgent questions or additional requirements, please don't hesitate to contact us.

Thank you for considering our services.

Best regards,
Sales Team"""

        return {
            "response_type": "quote_request",
            "response_subject": f"Shipping Quote - {route}" + (f" - Rate: {rate_data.get('rate_recommendation', {}).get('rate_range', '')}" if rate_available else " - Quote in Progress"),
            "response_body": response_body,
            "tone": "professional",
            "key_information_included": ["shipment_summary", "rate_information" if rate_available else "quote_in_progress", "next_steps"],
            "attachments_needed": ["terms_conditions", "documentation_checklist"] if rate_available else [],
            "next_steps": "Customer to confirm booking" if rate_available else "Quote to be provided within 24 hours",
            "urgency_level": "medium",
            "follow_up_required": not rate_available,
            "estimated_response_time": "Within 24 hours" if not rate_available else "Upon customer confirmation",
            "indicative_rate": f"${rate_data.get('rate_recommendation', {}).get('recommended_rate', 0):,.2f}" if rate_available else "Quote in progress",
            "extraction_method": "fallback_quote_response"
        }

    def _generate_default_response(self, extraction_data, original_subject, route):
        """Generate default response for unclassified emails"""
        
        shipment_summary = self._build_shipment_summary(extraction_data)
        
        response_body = f"""Dear valued customer,

Thank you for contacting us regarding your logistics requirements.

We have received your inquiry about shipment from {route} and our team is reviewing your requirements.

SHIPMENT DETAILS RECEIVED:
{shipment_summary}

Our customer service team will review your request and respond with appropriate next steps within 24 hours.

If this is an urgent matter, please contact us directly at [phone number] or reply to this email with "URGENT" in the subject line.

Thank you for your patience.

Best regards,
Customer Service Team"""

        return {
            "response_type": "default",
            "response_subject": f"Re: {original_subject} - Request Received",
            "response_body": response_body,
            "tone": "professional",
            "key_information_included": ["acknowledgment", "shipment_details", "next_steps"],
            "attachments_needed": [],
            "next_steps": "Customer service team will respond within 24 hours",
            "urgency_level": "low",
            "follow_up_required": True,
            "estimated_response_time": "Within 24 hours",
            "extraction_method": "fallback_default"
        }

    def _build_shipment_summary(self, extraction_data):
        """Build formatted shipment summary from extraction data"""
        
        summary_lines = []
        
        # Route information
        origin = extraction_data.get("origin", "Not specified")
        destination = extraction_data.get("destination", "Not specified")
        summary_lines.append(f"• Route: {origin} → {destination}")
        
        # Container information
        container_type = extraction_data.get("container_type", "Not specified")
        quantity = extraction_data.get("quantity", "Not specified")
        if quantity != "Not specified" and container_type != "Not specified":
            summary_lines.append(f"• Container: {quantity}x {container_type}")
        else:
            summary_lines.append(f"• Container Type: {container_type}")
            summary_lines.append(f"• Quantity: {quantity}")
        
        # Shipment details
        shipment_type = extraction_data.get("shipment_type", "Not specified")
        summary_lines.append(f"• Shipment Type: {shipment_type}")
        
        weight = extraction_data.get("weight", "Not specified")
        if weight != "Not specified":
            summary_lines.append(f"• Weight: {weight}")
        
        volume = extraction_data.get("volume", "Not specified")
        if volume != "Not specified":
            summary_lines.append(f"• Volume: {volume}")
        
        commodity = extraction_data.get("commodity", "Not specified")
        summary_lines.append(f"• Commodity: {commodity}")
        
        shipment_date = extraction_data.get("shipment_date", "Not specified")
        if shipment_date != "Not specified":
            summary_lines.append(f"• Expected Shipment Date: {shipment_date}")
        
        # Special requirements
        dangerous_goods = extraction_data.get("dangerous_goods", False)
        if dangerous_goods:
            summary_lines.append("• Special Note: Dangerous goods declared")
        
        special_requirements = extraction_data.get("special_requirements")
        if special_requirements and special_requirements.lower() not in ["none", "null", ""]:
            summary_lines.append(f"• Special Requirements: {special_requirements}")
        
        return "\n".join(summary_lines)

# =====================================================
#                 🔁 Enhanced Test Harness
# =====================================================

def test_enhanced_response_generator():
    print("=== Testing Enhanced Response Generator Agent ===")
    agent = ResponseGeneratorAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}, Has LLM client: {bool(agent.client)}")

    # Comprehensive test case with all agent inputs
    comprehensive_test = {
        "subject": "Shipping Quote Request - Shanghai to Rotterdam",
        "email_text": "Please provide quote for 2x40HC containers from Shanghai to Rotterdam, electronics cargo, ready July 22nd",
        "thread_id": "thread-001",
        
        # Classification agent output
        "classification_data": {
            "email_type": "logistics_request",
            "confidence": 0.95,
            "intent": "quote_request",
            "status": "success"
        },
        
        # Extraction agent output
        "extraction_data": {
            "origin": "Shanghai",
            "destination": "Rotterdam", 
            "origin_port_code": "CNSHA",
            "destination_port_code": "NLRTM",
            "shipment_type": "FCL",
            "container_type": "40HC",
            "standardized_container_type": "40HC",
            "quantity": 2,
            "weight": "25 tons",
            "volume": "67 CBM",
            "shipment_date": "2024-07-22",
            "commodity": "electronics",
            "dangerous_goods": False,
            "special_requirements": None,
            "status": "success"
        },
        
        # Validation agent output
        "validation_data": {
            "overall_validity": True,
            "missing_fields": [],
            "validation_errors": [],
            "warnings": [],
            "completeness_score": 0.9,
            "status": "success"
        },
        
        # Clarification agent output
        "clarification_data": {
            "clarification_needed": False,
            "clarification_message": "",
            "missing_fields": [],
            "status": "success"
        },
        
        # Confirmation agent output
        "confirmation_data": {
            "is_confirmation": False,
            "confirmation_type": "",
            "status": "success"
        },
        
        # Rate recommendation agent output
        "rate_data": {
            "rate_recommendation": {
                "match_type": "exact_match",
                "recommended_rate": 2450.00,
                "rate_range": "$2,200 - $2,700",
                "confidence": "high",
                "total_rates_found": 15,
                "rate_statistics": {
                    "market_average": {
                        "min": 2200,
                        "max": 2700,
                        "average": 2450.00,
                        "median": 2400.00
                    }
                }
            },
            "status": "success"
        },
        
        # Port lookup agent output
        "port_data": {
            "origin": {
                "port_code": "CNSHA",
                "port_name": "Shanghai",
                "country": "China",
                "region": "Asia"
            },
            "destination": {
                "port_code": "NLRTM", 
                "port_name": "Rotterdam",
                "country": "Netherlands",
                "region": "Europe"
            }
        },
        
        # Container standardization agent output
        "container_data": {
            "standardized_container_type": "40HC",
            "container_specifications": {
                "name": "40ft High Cube Container",
                "category": "dry",
                "max_weight": 29.0,
                "max_volume": 76.0
            },
            "validation_status": "valid",
            "status": "success"
        },
        
        # Country extraction agent output
        "country_data": {
            "origin": {
                "country_name": "China",
                "country_code": "CN",
                "region": "Asia"
            },
            "destination": {
                "country_name": "Netherlands", 
                "country_code": "NL",
                "region": "Europe"
            }
        }
    }

    # Test cases for different scenarios
    test_cases = [
        {
            "name": "Complete Quote Request with Rate Available",
            "data": comprehensive_test
        },
        {
            "name": "Quote Request - No Rate Available",
            "data": {
                **comprehensive_test,
                "rate_data": {
                    "rate_recommendation": {
                        "match_type": "no_match",
                        "message": "No rates found for this route"
                    },
                    "status": "success"
                }
            }
        },
        {
            "name": "Clarification Required",
            "data": {
                **comprehensive_test,
                "validation_data": {
                    "overall_validity": False,
                    "missing_fields": ["origin", "shipment_date"],
                    "completeness_score": 0.6,
                    "status": "success"
                },
                "clarification_data": {
                    "clarification_needed": True,
                    "clarification_message": "We need additional information to process your request.",
                    "clarification_details": [
                        {"field": "origin", "prompt": "What is the origin port or city?"},
                        {"field": "shipment_date", "prompt": "What is the expected shipment date?"}
                    ],
                    "missing_fields": ["origin", "shipment_date"],
                    "status": "success"
                }
            }
        },
        {
            "name": "Booking Confirmation",
            "data": {
                **comprehensive_test,
                "classification_data": {
                    "email_type": "confirmation_reply",
                    "confidence": 0.98,
                    "intent": "booking_confirmation",
                    "status": "success"
                },
                "confirmation_data": {
                    "is_confirmation": True,
                    "confirmation_type": "booking",
                    "confirmation_details": "2x40HC containers from Shanghai to Rotterdam",
                    "reasoning": "Customer explicitly confirmed the booking",
                    "status": "success"
                }
            }
        },
        {
            "name": "Partial Information - Fallback Response",
            "data": {
                "subject": "Shipping inquiry",
                "email_text": "Need shipping quote",
                "extraction_data": {
                    "origin": None,
                    "destination": None,
                    "shipment_type": None,
                    "status": "success"
                },
                "classification_data": {
                    "email_type": "logistics_request",
                    "confidence": 0.7,
                    "status": "success"
                },
                "clarification_data": {
                    "clarification_needed": True,
                    "missing_fields": ["origin", "destination", "shipment_type", "container_type"],
                    "status": "success"
                }
            }
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test Case {i}: {test_case['name']}")
        print(f"{'='*60}")
        
        result = agent.run(test_case["data"])
        
        if result.get("status") == "success":
            print(f"✓ Response Type: {result.get('response_type', 'unknown')}")
            print(f"✓ Subject: {result.get('response_subject', 'N/A')}")
            print(f"✓ Tone: {result.get('tone', 'N/A')}")
            print(f"✓ Key Information: {result.get('key_information_included', [])}")
            print(f"✓ Next Steps: {result.get('next_steps', 'N/A')}")
            print(f"✓ Urgency: {result.get('urgency_level', 'N/A')}")
            print(f"✓ Follow-up Required: {result.get('follow_up_required', 'N/A')}")
            
            if result.get('indicative_rate'):
                print(f"✓ Indicative Rate: {result.get('indicative_rate')}")
            
            print(f"\n--- Response Body ---")
            print(result.get('response_body', 'No response body'))
            
            if result.get('attachments_needed'):
                print(f"\n--- Suggested Attachments ---")
                for attachment in result.get('attachments_needed', []):
                    print(f"• {attachment}")
                    
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")

def test_fallback_responses():
    """Test fallback response generation when LLM is not available"""
    print("\n" + "="*60)
    print("Testing Fallback Response Generation")
    print("="*60)
    
    # Create agent without LLM client
    agent = ResponseGeneratorAgent()
    agent.client = None  # Force fallback mode
    
    fallback_test_cases = [
        {
            "name": "Fallback Quote Response with Rate",
            "response_type": "quote_request",
            "extraction_data": {
                "origin": "Shanghai",
                "destination": "Rotterdam",
                "container_type": "40HC",
                "quantity": 2,
                "commodity": "electronics"
            },
            "rate_data": {
                "status": "success",
                "rate_recommendation": {
                    "match_type": "exact_match",
                    "recommended_rate": 2450.00,
                    "rate_range": "$2,200 - $2,700"
                }
            },
            "clarification_data": {"clarification_needed": False},
            "original_subject": "Shipping Quote Request"
        },
        {
            "name": "Fallback Clarification Response",
            "response_type": "clarification",
            "extraction_data": {
                "origin": "Shanghai",
                "destination": None,
                "container_type": None
            },
            "clarification_data": {
                "clarification_needed": True,
                "clarification_message": "We need additional information to process your request.",
                "clarification_details": [
                    {"field": "destination", "prompt": "What is the destination port?"},
                    {"field": "container_type", "prompt": "What container type do you need?"}
                ],
                "missing_fields": ["destination", "container_type"]
            },
            "rate_data": {},
            "original_subject": "Shipping Quote"
        },
        {
            "name": "Fallback Confirmation Response", 
            "response_type": "confirmation",
            "extraction_data": {
                "origin": "Mumbai",
                "destination": "Hamburg",
                "container_type": "20DC",
                "quantity": 1,
                "commodity": "textiles"
            },
            "clarification_data": {"clarification_needed": False},
            "rate_data": {},
            "original_subject": "Booking Confirmation"
        }
    ]
    
    for i, test_case in enumerate(fallback_test_cases, 1):
        print(f"\n--- Fallback Test {i}: {test_case['name']} ---")
        
        result = agent._fallback_response_generation(
            test_case["response_type"],
            test_case["extraction_data"],
            test_case["clarification_data"],
            test_case["rate_data"],
            test_case["original_subject"]
        )
        
        print(f"✓ Response Type: {result.get('response_type')}")
        print(f"✓ Subject: {result.get('response_subject')}")
        print(f"✓ Tone: {result.get('tone')}")
        print(f"✓ Next Steps: {result.get('next_steps')}")
        print(f"\n--- Fallback Response Body ---")
        print(result.get('response_body', 'No response body'))

def test_context_building():
    """Test comprehensive context building from agent outputs"""
    print("\n" + "="*60)
    print("Testing Context Building")
    print("="*60)
    
    agent = ResponseGeneratorAgent()
    
    # Sample agent outputs
    sample_context_data = {
        "response_type": "quote_request",
        "original_subject": "Shipping Quote - Electronics",
        "original_email": "Need quote for electronics shipment from Shanghai to Rotterdam",
        "thread_id": "thread-123",
        "classification_data": {
            "email_type": "logistics_request",
            "confidence": 0.95,
            "intent": "quote_request",
            "status": "success"
        },
        "extraction_data": {
            "origin": "Shanghai",
            "destination": "Rotterdam",
            "origin_port_code": "CNSHA",
            "destination_port_code": "NLRTM",
            "shipment_type": "FCL",
            "container_type": "40HC",
            "quantity": 2,
            "commodity": "electronics",
            "status": "success"
        },
        "validation_data": {
            "overall_validity": True,
            "missing_fields": [],
            "completeness_score": 0.9,
            "status": "success"
        },
        "rate_data": {
            "status": "success",
            "rate_recommendation": {
                "match_type": "exact_match",
                "recommended_rate": 2450.00,
                "rate_range": "$2,200 - $2,700",
                "confidence": "high"
            }
        }
    }
    
    context = agent._build_comprehensive_context(**sample_context_data)
    
    print("✓ Context built successfully")
    print(f"✓ Context keys: {list(context.keys())}")
    
    if 'shipment_details' in context:
        print(f"✓ Route: {context.get('route', 'N/A')}")
        shipment = context['shipment_details']
        print(f"✓ Container: {shipment.get('quantity')}x {shipment.get('container_type')}")
        print(f"✓ Commodity: {shipment.get('commodity')}")
    
    if 'rate_information' in context:
        rate_info = context['rate_information']
        print(f"✓ Rate Available: {rate_info.get('rate_available')}")
        if rate_info.get('rate_available'):
            print(f"✓ Recommended Rate: ${rate_info.get('recommended_rate'):,.2f}")
            print(f"✓ Rate Range: {rate_info.get('rate_range')}")
    
    print(f"\n--- Full Context Structure ---")
    print(json.dumps(context, indent=2))

def run_comprehensive_tests():
    """Run all test suites"""
    print("🚀 Starting Comprehensive Response Generator Tests")
    print("=" * 80)
    
    try:
        # Main functionality tests
        test_enhanced_response_generator()
        
        # Fallback tests
        test_fallback_responses()
        
        # Context building tests
        test_context_building()
        
        print("\n" + "=" * 80)
        print("🎉 All Response Generator tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_comprehensive_tests()
