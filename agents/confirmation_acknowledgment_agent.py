#!/usr/bin/env python3
"""
Confirmation Acknowledgment Agent
================================

Generates human-like confirmation acknowledgment responses when customers
confirm their extracted information, acknowledging receipt and proceeding
with the next steps in the workflow.
"""

import json
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ConfirmationAcknowledgmentAgent(BaseAgent):
    """Generates confirmation acknowledgment responses for confirmed information"""
    
    def __init__(self):
        super().__init__("confirmation_acknowledgment_agent")
        self.load_context()
    
    def load_context(self):
        """Load agent context and configuration"""
        self.response_templates = {
            "professional": {
                "greeting": "Dear {customer_name},",
                "acknowledgment": "Thank you for confirming the details for your shipment from {origin} to {destination}.",
                "confirmation_received": "I have received your confirmation and will now proceed with the next steps in your shipping process.",
                "next_steps": "I will be working on your quote and will get back to you within the next 24 hours with comprehensive pricing and options.",
                "forwarder_assignment": "I am now assigning your shipment to our trusted forwarder partners to secure the best rates for your route.",
                "additional_info": "If you have any urgent requirements or need to make any changes, please don't hesitate to contact me immediately.",
                "closing": "Thank you for choosing our services. I look forward to providing you with the best possible shipping solution.",
                "signature": "Best regards,\n{agent_name}\n{agent_title}\n{agent_email}\n{agent_phone}"
            },
            "friendly": {
                "greeting": "Hi {customer_name},",
                "acknowledgment": "Perfect! Thanks for confirming the details for your shipment from {origin} to {destination}.",
                "confirmation_received": "I've got your confirmation and I'm already working on getting you the best possible quote.",
                "next_steps": "I'll have your detailed quote ready within 24 hours, and I'll make sure to include all the best options for your route.",
                "forwarder_assignment": "I'm now connecting you with our trusted forwarder partners to secure the most competitive rates for your shipment.",
                "additional_info": "If anything comes up or you need to make changes, just shoot me an email or give me a call right away.",
                "closing": "Thanks for choosing us! I'm excited to help you get the best shipping solution for your needs.",
                "signature": "Looking forward to helping you!\n\n{agent_name}\n{agent_title}\n{agent_email}\n{agent_phone}"
            }
        }
    
    def generate_confirmation_acknowledgment(self, 
                                          extracted_data: Dict[str, Any],
                                          customer_name: str = "Valued Customer",
                                          agent_info: Dict[str, str] = None,
                                          tone: str = "professional",
                                          quote_timeline: str = "24 hours",
                                          include_forwarder_info: bool = True) -> Dict[str, Any]:
        """
        Generate a human-like confirmation acknowledgment response
        
        Args:
            extracted_data: Confirmed information from customer
            customer_name: Customer's name
            agent_info: Sales agent information
            tone: Response tone (professional/friendly)
            quote_timeline: Timeline for quote delivery
            include_forwarder_info: Whether to mention forwarder assignment
        
        Returns:
            Dictionary containing response details
        """
        try:
            logger.info(f"Generating confirmation acknowledgment for customer: {customer_name}")
            
            # Get template based on tone
            template = self.response_templates.get(tone, self.response_templates["professional"])
            
            # Generate subject line
            subject = self._generate_subject_line(extracted_data)
            
            # Build response body
            response_body = self._build_response_body(
                template, customer_name, extracted_data, 
                agent_info, quote_timeline, include_forwarder_info
            )
            
            response = {
                "response_type": "confirmation_acknowledgment",
                "subject": subject,
                "body": response_body,
                "tone": tone,
                "confirmed_data": extracted_data,
                "quote_timeline": quote_timeline,
                "include_forwarder_info": include_forwarder_info,
                "confidence_level": "high",
                "response_quality": 95,
                "reasoning": "Customer confirmed all information, acknowledging receipt and proceeding with forwarder assignment"
            }
            
            logger.info(f"Generated confirmation acknowledgment with quote timeline: {quote_timeline}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating confirmation acknowledgment: {e}")
            return self._generate_fallback_response(extracted_data, customer_name)
    
    def _generate_subject_line(self, extracted_data: Dict[str, Any]) -> str:
        """Generate appropriate subject line for confirmation acknowledgment"""
        try:
            shipment = extracted_data.get("shipment_details", {})
            origin = shipment.get("origin", "your origin")
            destination = shipment.get("destination", "your destination")
            
            if origin and destination and origin != "your origin" and destination != "your destination":
                return f"Confirmation Received - Quote in Progress for {origin} to {destination}"
            else:
                return "Confirmation Received - Quote in Progress"
                
        except Exception as e:
            logger.error(f"Error generating subject line: {e}")
            return "Confirmation Received - Quote in Progress"
    
    def _build_response_body(self, template: Dict[str, str], customer_name: str, 
                           extracted_data: Dict[str, Any], agent_info: Dict[str, str], 
                           quote_timeline: str, include_forwarder_info: bool = True) -> str:
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
        
        # Build response parts
        response_parts = [
            template["greeting"].format(customer_name=customer_name),
            "",
            template["acknowledgment"].format(origin=origin, destination=destination),
            "",
            template["confirmation_received"],
            ""
        ]
        
        # Add forwarder assignment information if requested
        if include_forwarder_info:
            response_parts.extend([
                template["forwarder_assignment"],
                ""
            ])
        
        # Add next steps and timeline
        response_parts.extend([
            template["next_steps"].replace("24 hours", quote_timeline),
            "",
            template["additional_info"],
            "",
            template["closing"],
            "",
            template["signature"].format(
                agent_name=agent_info["name"],
                agent_title=agent_info["title"],
                agent_email=agent_info["email"],
                agent_phone=agent_info["phone"]
            )
        ])
        
        return "\n".join(response_parts)
    
    def _generate_fallback_response(self, extracted_data: Dict[str, Any], customer_name: str) -> Dict[str, Any]:
        """Generate a fallback response if the main generation fails"""
        return {
            "response_type": "confirmation_acknowledgment",
            "subject": "Confirmation Received - Quote in Progress",
            "body": f"""Dear {customer_name},

Thank you for confirming your shipment details.

I have received your confirmation and will now proceed with preparing your detailed shipping quote. I will get back to you within 24 hours with comprehensive pricing and options.

If you have any urgent requirements or need to make any changes, please don't hesitate to contact me immediately.

Thank you for choosing our services.

Best regards,
Digital Sales Specialist
sales@searates.com
+1-555-0123""",
            "tone": "professional",
            "confirmed_data": extracted_data,
            "quote_timeline": "24 hours",
            "confidence_level": "high",
            "response_quality": 85,
            "reasoning": "Fallback response generated due to processing error"
        }
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request and generate confirmation acknowledgment"""
        try:
            extracted_data = data.get("extracted_data", {})
            customer_name = data.get("customer_name", "Valued Customer")
            agent_info = data.get("agent_info")
            tone = data.get("tone", "professional")
            quote_timeline = data.get("quote_timeline", "24 hours")
            include_forwarder_info = data.get("include_forwarder_info", True)
            
            return self.generate_confirmation_acknowledgment(
                extracted_data=extracted_data,
                customer_name=customer_name,
                agent_info=agent_info,
                tone=tone,
                quote_timeline=quote_timeline,
                include_forwarder_info=include_forwarder_info
            )
            
        except Exception as e:
            logger.error(f"Error in confirmation acknowledgment processing: {e}")
            return {
                "error": f"Failed to generate confirmation acknowledgment: {str(e)}",
                "response_type": "confirmation_acknowledgment"
            } 