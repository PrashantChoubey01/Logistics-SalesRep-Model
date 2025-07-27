#!/usr/bin/env python3
"""
Confirmation Response Agent
==========================

Generates human-like confirmation responses asking customers to confirm
extracted information before proceeding with the quote.
"""

import json
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ConfirmationResponseAgent(BaseAgent):
    """Generates confirmation responses for extracted information"""
    
    def __init__(self):
        super().__init__("confirmation_response_agent")
        self.load_context()
    
    def load_context(self):
        """Load agent context and configuration"""
        self.response_templates = {
            "professional": {
                "greeting": "Dear {customer_name},",
                "acknowledgment": "Thank you for providing the details for your shipment from {origin} to {destination}.",
                "confirmation_request": "Before I prepare your detailed quote, please confirm the following information is correct:",
                "confirmation_instructions": "Please review the details below and confirm if they are accurate. If any information needs to be corrected, please let me know.",
                "closing": "Once you confirm these details, I'll proceed with preparing your comprehensive shipping quote.",
                "signature": "Best regards,\n{agent_name}\n{agent_title}\n{agent_email}\n{agent_phone}"
            },
            "friendly": {
                "greeting": "Hi {customer_name},",
                "acknowledgment": "Thanks for sharing the details about your shipment from {origin} to {destination}!",
                "confirmation_request": "I've gathered all the information needed. Could you please confirm these details are correct:",
                "confirmation_instructions": "Take a moment to review the information below. If anything looks off, just let me know and I'll update it right away.",
                "closing": "Once you give me the thumbs up on these details, I'll get your quote ready right away!",
                "signature": "Looking forward to helping you!\n\n{agent_name}\n{agent_title}\n{agent_email}\n{agent_phone}"
            }
        }
    
    def generate_confirmation_response(self, 
                                    extracted_data: Dict[str, Any],
                                    customer_name: str = "Valued Customer",
                                    agent_info: Dict[str, str] = None,
                                    tone: str = "professional",
                                    rate_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a human-like confirmation response
        
        Args:
            extracted_data: Information extracted from customer email
            customer_name: Customer's name
            agent_info: Sales agent information
            tone: Response tone (professional/friendly)
            rate_info: Rate information if available
        
        Returns:
            Dictionary containing response details
        """
        try:
            logger.info(f"Generating confirmation response for customer: {customer_name}")
            
            # Get template based on tone
            template = self.response_templates.get(tone, self.response_templates["professional"])
            
            # Format extracted information for confirmation
            confirmation_info = self._format_confirmation_info(extracted_data)
            
            # Generate subject line
            subject = self._generate_subject_line(extracted_data)
            
            # Build response body
            response_body = self._build_response_body(
                template, customer_name, extracted_data, 
                confirmation_info, agent_info, rate_info
            )
            
            response = {
                "response_type": "confirmation",
                "subject": subject,
                "body": response_body,
                "tone": tone,
                "extracted_data_shared": extracted_data,
                "rate_info_included": bool(rate_info),
                "confidence_level": "high",
                "response_quality": 95,
                "reasoning": "All required information provided, confirmation needed before quote generation"
            }
            
            logger.info(f"Generated confirmation response with {len(extracted_data)} data categories")
            return response
            
        except Exception as e:
            logger.error(f"Error generating confirmation response: {e}")
            return self._generate_fallback_response(extracted_data, customer_name)
    
    def _format_confirmation_info(self, extracted_data: Dict[str, Any]) -> str:
        """Format extracted information for confirmation display"""
        formatted_sections = []
        
        # Shipment details
        if "shipment_details" in extracted_data:
            shipment = extracted_data["shipment_details"]
            if any(shipment.values()):
                shipment_text = "**Shipment Details:**\n"
                if shipment.get("origin"):
                    shipment_text += f"• Origin: {shipment['origin']}\n"
                if shipment.get("destination"):
                    shipment_text += f"• Destination: {shipment['destination']}\n"
                if shipment.get("container_type"):
                    shipment_text += f"• Container Type: {shipment['container_type']}\n"
                if shipment.get("container_count"):
                    shipment_text += f"• Number of Containers: {shipment['container_count']}\n"
                if shipment.get("weight"):
                    shipment_text += f"• Weight: {shipment['weight']}\n"
                if shipment.get("volume"):
                    shipment_text += f"• Volume: {shipment['volume']}\n"
                if shipment.get("commodity"):
                    shipment_text += f"• Commodity: {shipment['commodity']}\n"
                formatted_sections.append(shipment_text)
        
        # Contact information
        if "contact_information" in extracted_data:
            contact = extracted_data["contact_information"]
            if any(contact.values()):
                contact_text = "**Contact Information:**\n"
                if contact.get("name"):
                    contact_text += f"• Name: {contact['name']}\n"
                if contact.get("company"):
                    contact_text += f"• Company: {contact['company']}\n"
                if contact.get("email"):
                    contact_text += f"• Email: {contact['email']}\n"
                if contact.get("phone"):
                    contact_text += f"• Phone: {contact['phone']}\n"
                formatted_sections.append(contact_text)
        
        # Timeline information
        if "timeline_information" in extracted_data:
            timeline = extracted_data["timeline_information"]
            timeline_text = "**Timeline:**\n"
            has_timeline_data = False
            
            if timeline.get("requested_dates"):
                timeline_text += f"• Requested Dates: {timeline['requested_dates']}\n"
                has_timeline_data = True
            if timeline.get("transit_time"):
                timeline_text += f"• Transit Time: {timeline['transit_time']}\n"
                has_timeline_data = True
            if timeline.get("urgency"):
                timeline_text += f"• Urgency: {timeline['urgency']}\n"
                has_timeline_data = True
            if timeline.get("deadline"):
                timeline_text += f"• Deadline: {timeline['deadline']}\n"
                has_timeline_data = True
            
            if has_timeline_data:
                formatted_sections.append(timeline_text)
        
        # Special requirements
        if "special_requirements" in extracted_data:
            requirements = extracted_data["special_requirements"]
            if requirements and isinstance(requirements, list) and len(requirements) > 0:
                requirements_text = "**Special Requirements:**\n"
                for req in requirements:
                    if req and req.strip():
                        requirements_text += f"• {req}\n"
                formatted_sections.append(requirements_text)
        
        # Additional notes
        if "additional_notes" in extracted_data:
            notes = extracted_data["additional_notes"]
            if notes and notes.strip():
                notes_text = "**Additional Notes:**\n"
                notes_text += f"• {notes}\n"
                formatted_sections.append(notes_text)
        
        return "\n".join(formatted_sections) if formatted_sections else "No specific details to confirm."
    
    def _generate_subject_line(self, extracted_data: Dict[str, Any]) -> str:
        """Generate appropriate subject line"""
        shipment = extracted_data.get("shipment_details", {})
        origin = shipment.get("origin", "origin")
        destination = shipment.get("destination", "destination")
        
        return f"Please Confirm Your Shipment Details - {origin} to {destination}"
    
    def _build_response_body(self, template: Dict[str, str], customer_name: str, 
                           extracted_data: Dict[str, Any], confirmation_info: str, 
                           agent_info: Dict[str, str], rate_info: Dict[str, Any] = None) -> str:
        """Build the complete response body"""
        
        # Default agent info
        default_agent = {
            "name": "Digital Sales Specialist",
            "title": "Digital Sales Specialist",
            "email": "sales@searates.com",
            "phone": "+1-555-0123"
        }
        
        agent_info = agent_info or default_agent
        
        # Get origin and destination for template
        shipment = extracted_data.get("shipment_details", {})
        origin = shipment.get("origin", "your origin")
        destination = shipment.get("destination", "your destination")
        
        # Build response with enhanced validation focus
        response_parts = [
            template["greeting"].format(customer_name=customer_name),
            "",
            template["acknowledgment"].format(origin=origin, destination=destination),
            "",
            "I've carefully reviewed your email and extracted the following information. Please take a moment to confirm these details are accurate:",
            "",
            confirmation_info,
            "",
            "**Next Steps:**",
            "• If all information above is correct, please reply with 'Confirmed' or 'Yes, that's correct'",
            "• If any information needs correction, please provide the correct details",
            "• If any information is missing, please provide it",
            "",
            template["closing"],
            ""
        ]
        
        # Add rate information if available
        if rate_info:
            rate_text = self._format_rate_info(rate_info)
            response_parts.extend([
                "**Rate Information:**",
                "",
                rate_text,
                ""
            ])
        
        response_parts.extend([
            template["signature"].format(
                agent_name=agent_info["name"],
                agent_title=agent_info["title"],
                agent_email=agent_info["email"],
                agent_phone=agent_info["phone"]
            )
        ])
        
        return "\n".join(response_parts)
    
    def _format_rate_info(self, rate_info: Dict[str, Any]) -> str:
        """Format rate information for display"""
        rate_text = ""
        
        if rate_info.get("rate_ranges"):
            rate_text += "**Rate Ranges:**\n"
            for route, rates in rate_info["rate_ranges"].items():
                rate_text += f"• {route}: ${rates.get('min', 'N/A')} - ${rates.get('max', 'N/A')}\n"
        
        if rate_info.get("rate_disclaimer"):
            rate_text += f"\n**Note:** {rate_info['rate_disclaimer']}\n"
        
        return rate_text if rate_text else "Rate information will be provided in the final quote."
    
    def _generate_fallback_response(self, extracted_data: Dict[str, Any], customer_name: str) -> Dict[str, Any]:
        """Generate a fallback response if main generation fails"""
        return {
            "response_type": "confirmation",
            "subject": "Please Confirm Your Shipment Details",
            "body": f"""Dear {customer_name},

Thank you for providing your shipment details. Before I prepare your quote, please confirm the following information is correct:

{self._format_confirmation_info(extracted_data)}

Please review these details and let me know if any corrections are needed.

Best regards,
Digital Sales Specialist
sales@searates.com""",
            "tone": "professional",
            "extracted_data_shared": extracted_data,
            "confidence_level": "medium",
            "response_quality": 70,
            "reasoning": "Fallback response generated due to processing error"
        }
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request and generate confirmation response"""
        try:
            extracted_data = data.get("extracted_data", {})
            customer_name = data.get("customer_name", "Valued Customer")
            agent_info = data.get("agent_info")
            tone = data.get("tone", "professional")
            rate_info = data.get("rate_info")
            
            return self.generate_confirmation_response(
                extracted_data=extracted_data,
                customer_name=customer_name,
                agent_info=agent_info,
                tone=tone,
                rate_info=rate_info
            )
            
        except Exception as e:
            logger.error(f"Error in confirmation response processing: {e}")
            return {
                "error": f"Failed to generate confirmation response: {str(e)}",
                "response_type": "confirmation"
            } 