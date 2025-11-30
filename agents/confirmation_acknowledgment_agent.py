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
                                          include_forwarder_info: bool = True,
                                          port_lookup_result: Dict[str, Any] = None) -> Dict[str, Any]:
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
            subject = self._generate_subject_line(extracted_data, port_lookup_result)
            
            # Build response body
            response_body = self._build_response_body(
                template, customer_name, extracted_data, 
                agent_info, quote_timeline, include_forwarder_info, port_lookup_result
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
    
    def _generate_subject_line(self, extracted_data: Dict[str, Any], port_lookup_result: Dict[str, Any] = None) -> str:
        """Generate appropriate subject line for confirmation acknowledgment with port codes"""
        try:
            shipment = extracted_data.get("shipment_details", {})
            origin = shipment.get("origin", "your origin")
            destination = shipment.get("destination", "your destination")
            
            # Add port codes if available (unless confidence < 0.5 or use_port_name is True)
            if port_lookup_result:
                if port_lookup_result.get("origin"):
                    origin_result = port_lookup_result["origin"]
                    origin_code = origin_result.get("port_code", "")
                    # CRITICAL: Use original_port_name if port_name is None, otherwise use port_name, fallback to origin
                    original_origin_name = origin_result.get("original_port_name", origin)
                    origin_name = origin_result.get("port_name") or original_origin_name or origin
                    confidence = origin_result.get("confidence", 0.0)
                    use_port_name = origin_result.get("use_port_name", False)
                    # Show port code if available and conditions met
                    if origin_code and origin_code.strip() and confidence >= 0.5 and not use_port_name:
                        origin = f"{origin_name} ({origin_code})"
                    else:
                        origin = origin_name
                
                if port_lookup_result.get("destination"):
                    dest_result = port_lookup_result["destination"]
                    dest_code = dest_result.get("port_code", "")
                    # CRITICAL: Use original_port_name if port_name is None, otherwise use port_name, fallback to destination
                    original_dest_name = dest_result.get("original_port_name", destination)
                    dest_name = dest_result.get("port_name") or original_dest_name or destination
                    confidence = dest_result.get("confidence", 0.0)
                    use_port_name = dest_result.get("use_port_name", False)
                    # Show port code if available and conditions met
                    if dest_code and dest_code.strip() and confidence >= 0.5 and not use_port_name:
                        destination = f"{dest_name} ({dest_code})"
                    else:
                        destination = dest_name
            
            if origin and destination and origin != "your origin" and destination != "your destination":
                return f"Confirmation Received - Quote in Progress for {origin} to {destination}"
            else:
                return "Confirmation Received - Quote in Progress"
                
        except Exception as e:
            logger.error(f"Error generating subject line: {e}")
            return "Confirmation Received - Quote in Progress"
    
    def _build_response_body(self, template: Dict[str, str], customer_name: str, 
                           extracted_data: Dict[str, Any], agent_info: Dict[str, str], 
                           quote_timeline: str, include_forwarder_info: bool = True,
                           port_lookup_result: Dict[str, Any] = None) -> str:
        """Build the complete response body - per spec: shows confirmed shipment details"""
        
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
        
        # Format confirmed shipment details (per spec: confirmation acknowledgment shows confirmed details with port codes)
        confirmed_details = self._format_confirmed_details(extracted_data, port_lookup_result)
        
        # Build response parts
        response_parts = [
            template["greeting"].format(customer_name=customer_name),
            "",
            template["acknowledgment"].format(origin=origin, destination=destination),
            "",
            "I've received your confirmation for:",
            "",
            confirmed_details,
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
    
    def _format_confirmed_details(self, extracted_data: Dict[str, Any], port_lookup_result: Dict[str, Any] = None) -> str:
        """Format confirmed shipment details for display with port codes (per spec)"""
        formatted_sections = []
        
        # Shipment details
        if "shipment_details" in extracted_data:
            shipment = extracted_data["shipment_details"]
            if any(shipment.values()):
                shipment_text = "**Confirmed Shipment Details:**\n"
                
                # Origin with port code
                # Show port codes when available (unless confidence < 0.5 or use_port_name is True)
                if shipment.get("origin"):
                    origin_display = shipment['origin']
                    if port_lookup_result and port_lookup_result.get("origin"):
                        origin_result = port_lookup_result["origin"]
                        # CRITICAL: Use original_port_name if port_name is None, otherwise use port_name, fallback to shipment origin
                        original_port_name = origin_result.get("original_port_name", shipment['origin'])
                        port_name = origin_result.get("port_name") or original_port_name or shipment['origin']
                        port_code = origin_result.get("port_code", "")
                        confidence = origin_result.get("confidence", 0.0)
                        use_port_name = origin_result.get("use_port_name", False)
                        # Show port code if available and conditions met
                        if port_code and port_code.strip() and confidence >= 0.5 and not use_port_name:
                            origin_display = f"{port_name} ({port_code})"
                        else:
                            origin_display = port_name
                    shipment_text += f"- Origin: {origin_display}\n"
                
                # Destination with port code
                # Show port codes when available (unless confidence < 0.5 or use_port_name is True)
                if shipment.get("destination"):
                    destination_display = shipment['destination']
                    if port_lookup_result and port_lookup_result.get("destination"):
                        destination_result = port_lookup_result["destination"]
                        # CRITICAL: Use original_port_name if port_name is None, otherwise use port_name, fallback to shipment destination
                        original_port_name = destination_result.get("original_port_name", shipment['destination'])
                        port_name = destination_result.get("port_name") or original_port_name or shipment['destination']
                        port_code = destination_result.get("port_code", "")
                        confidence = destination_result.get("confidence", 0.0)
                        use_port_name = destination_result.get("use_port_name", False)
                        # Show port code if available and conditions met
                        if port_code and port_code.strip() and confidence >= 0.5 and not use_port_name:
                            destination_display = f"{port_name} ({port_code})"
                        else:
                            destination_display = port_name
                    shipment_text += f"- Destination: {destination_display}\n"
                
                # CRITICAL: Check shipment_type to determine which fields to display
                shipment_type = shipment.get("shipment_type", "").strip().upper() if shipment.get("shipment_type") else ""
                is_lcl = shipment_type == "LCL"
                is_fcl = shipment_type == "FCL" or (not shipment_type and shipment.get("container_type"))
                
                # FCL-specific fields (only show for FCL shipments)
                if is_fcl and not is_lcl:
                    if shipment.get("container_type"):
                        shipment_text += f"- Container Type: {shipment['container_type']}\n"
                    if shipment.get("container_count"):
                        shipment_text += f"- Number of Containers: {shipment['container_count']}\n"
                
                # LCL-specific fields (only show for LCL shipments)
                if is_lcl:
                    if shipment.get("weight"):
                        shipment_text += f"- Weight: {shipment['weight']}\n"
                    if shipment.get("volume"):
                        shipment_text += f"- Volume: {shipment['volume']}\n"
                if shipment.get("commodity"):
                    shipment_text += f"- Commodity: {shipment['commodity']}\n"
                if shipment.get("weight"):
                    shipment_text += f"- Weight: {shipment['weight']}\n"
                if shipment.get("volume"):
                    shipment_text += f"- Volume: {shipment['volume']}\n"
                
                # Timeline information
                timeline_info = extracted_data.get("timeline_information", {})
                if timeline_info.get("requested_dates"):
                    shipment_text += f"- Ready Date: {timeline_info['requested_dates']}\n"
                
                # Incoterms (if in shipment_details or additional_notes)
                if shipment.get("incoterm"):
                    shipment_text += f"- Incoterm: {shipment['incoterm']}\n"
                
                formatted_sections.append(shipment_text)
        
        return "\n".join(formatted_sections) if formatted_sections else "Confirmed shipment details."
    
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
            container_standardization_result = data.get("container_standardization_result")
            port_lookup_result = data.get("port_lookup_result")
            
            # Ensure standardized container type is used (per spec: confirmation acknowledgment shows standardized container types)
            if container_standardization_result and isinstance(container_standardization_result, dict):
                standardized_type = container_standardization_result.get("standardized_type")
                if standardized_type and "shipment_details" in extracted_data:
                    extracted_data["shipment_details"]["container_type"] = standardized_type
            
            return self.generate_confirmation_acknowledgment(
                extracted_data=extracted_data,
                customer_name=customer_name,
                agent_info=agent_info,
                tone=tone,
                quote_timeline=quote_timeline,
                include_forwarder_info=include_forwarder_info,
                port_lookup_result=port_lookup_result
            )
            
        except Exception as e:
            logger.error(f"Error in confirmation acknowledgment processing: {e}")
            return {
                "error": f"Failed to generate confirmation acknowledgment: {str(e)}",
                "response_type": "confirmation_acknowledgment"
            } 