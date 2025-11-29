#!/usr/bin/env python3
"""
Confirmation Response Agent
==========================

Generates human-like confirmation responses asking customers to confirm
extracted information before proceeding with the quote.
"""

import json
import re
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
                                    rate_info: Dict[str, Any] = None,
                                    container_standardization_result: Dict[str, Any] = None,
                                    port_lookup_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a human-like confirmation response
        
        Args:
            extracted_data: Information extracted from customer email (should contain standardized container type)
            customer_name: Customer's name
            agent_info: Sales agent information
            tone: Response tone (professional/friendly)
            rate_info: Rate information if available
            container_standardization_result: Container standardization result (for reference, standardized type should already be in extracted_data)
            port_lookup_result: Port lookup result for human-friendly port formatting (per spec: show "Shanghai, China" not "Shanghai (CNSHG)")
        
        Returns:
            Dictionary containing response details
        """
        try:
            logger.info(f"Generating confirmation response for customer: {customer_name}")
            
            # Get template based on tone
            template = self.response_templates.get(tone, self.response_templates["professional"])
            
            # Format extracted information for confirmation (with human-friendly ports)
            confirmation_info = self._format_confirmation_info(extracted_data, port_lookup_result)
            
            # Generate subject line (with human-friendly ports)
            subject = self._generate_subject_line(extracted_data, port_lookup_result)
            
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
    
    def _format_confirmation_info(self, extracted_data: Dict[str, Any], port_lookup_result: Dict[str, Any] = None) -> str:
        """
        Format extracted information for confirmation display.
        Per spec: Shows human-friendly ports (e.g., "Shanghai, China") NOT with port codes.
        """
        formatted_sections = []
        
        # Shipment details
        if "shipment_details" in extracted_data:
            shipment = extracted_data["shipment_details"]
            if any(shipment.values()):
                shipment_text = "**Shipment Details:**\n"
                
                # Origin - format with port code for customer validation
                # If port lookup was performed, show port code so customer can validate
                if shipment.get("origin"):
                    origin_display = shipment['origin']
                    # Use port_lookup_result to get enriched port with code for validation
                    if port_lookup_result and port_lookup_result.get("origin"):
                        origin_result = port_lookup_result["origin"]
                        port_name = origin_result.get("port_name", shipment['origin'])
                        port_code = origin_result.get("port_code", "")
                        country = origin_result.get("country", "")
                        logger.debug(f"🔍 Origin formatting: port_name={port_name}, port_code={port_code}, country={country}")
                        # Show port code for customer validation (e.g., "Shanghai (CNSHG), China")
                        if port_code:
                            if country and country != "Unknown" and country:
                                origin_display = f"{port_name} ({port_code}), {country}"
                            else:
                                origin_display = f"{port_name} ({port_code})"
                        elif country and country != "Unknown" and country:
                            origin_display = f"{port_name}, {country}"
                        else:
                            origin_display = port_name
                            logger.debug(f"⚠️ No port code or country available for origin, using port_name only: {origin_display}")
                    else:
                        logger.debug(f"⚠️ No port_lookup_result for origin, using raw value: {origin_display}")
                    shipment_text += f"• Origin: {origin_display}\n"
                
                # Destination - format with port code for customer validation
                # If port lookup was performed, show port code so customer can validate
                if shipment.get("destination"):
                    destination_display = shipment['destination']
                    # Use port_lookup_result to get enriched port with code for validation
                    if port_lookup_result and port_lookup_result.get("destination"):
                        destination_result = port_lookup_result["destination"]
                        port_name = destination_result.get("port_name", shipment['destination'])
                        port_code = destination_result.get("port_code", "")
                        country = destination_result.get("country", "")
                        logger.debug(f"🔍 Destination formatting: port_name={port_name}, port_code={port_code}, country={country}")
                        # Show port code for customer validation (e.g., "Los Angeles (USLAX), USA")
                        if port_code:
                            if country and country != "Unknown" and country:
                                destination_display = f"{port_name} ({port_code}), {country}"
                            else:
                                destination_display = f"{port_name} ({port_code})"
                        elif country and country != "Unknown" and country:
                            destination_display = f"{port_name}, {country}"
                        else:
                            destination_display = port_name
                            logger.debug(f"⚠️ No port code or country available for destination, using port_name only: {destination_display}")
                    else:
                        logger.debug(f"⚠️ No port_lookup_result for destination, using raw value: {destination_display}")
                    shipment_text += f"• Destination: {destination_display}\n"
                
                # CRITICAL: Check shipment_type to determine which fields to display
                shipment_type = shipment.get("shipment_type", "").strip().upper() if shipment.get("shipment_type") else ""
                
                # If shipment_type is LCL, don't display container_type or container_count
                # If shipment_type is FCL, display container_type and container_count
                # If shipment_type is not set, check if container_type exists (defaults to FCL)
                is_lcl = shipment_type == "LCL"
                is_fcl = shipment_type == "FCL" or (not shipment_type and shipment.get("container_type"))
                
                # FCL-specific fields (only show for FCL shipments)
                if is_fcl and not is_lcl:
                    if shipment.get("container_type"):
                        shipment_text += f"• Container Type: {shipment['container_type']}\n"
                    if shipment.get("container_count"):
                        shipment_text += f"• Number of Containers: {shipment['container_count']}\n"
                
                # LCL-specific fields (only show for LCL shipments)
                if is_lcl:
                    if shipment.get("weight"):
                        shipment_text += f"• Weight: {shipment['weight']}\n"
                    if shipment.get("volume"):
                        shipment_text += f"• Volume: {shipment['volume']}\n"
                elif not is_fcl:
                    # If shipment type is unknown, show both (but this shouldn't happen)
                    if shipment.get("weight"):
                        shipment_text += f"• Weight: {shipment['weight']}\n"
                    if shipment.get("volume"):
                        shipment_text += f"• Volume: {shipment['volume']}\n"
                
                # Common fields (always show)
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
        
        # Additional notes - REMOVED per user request (too confusing)
        # if "additional_notes" in extracted_data:
        #     notes = extracted_data["additional_notes"]
        #     if notes and notes.strip():
        #         # Clean up additional notes - remove redundant information
        #         cleaned_notes = self._clean_additional_notes(notes)
        #         if cleaned_notes:  # Only add if there's meaningful content after cleaning
        #             notes_text = "**Additional Notes:**\n"
        #             notes_text += f"• {cleaned_notes}\n"
        #             formatted_sections.append(notes_text)
        
        return "\n".join(formatted_sections) if formatted_sections else "No specific details to confirm."
    
    def _clean_additional_notes(self, notes: str) -> str:
        """
        Clean additional notes by removing:
        - Signature text (job titles, names repeated)
        - Redundant phrases
        - Information already shown in other sections
        - Common email closings and greetings
        """
        if not notes or not notes.strip():
            return ""
        
        cleaned = notes.strip()
        
        # Split by newlines and process each line
        lines = cleaned.split('\n')
        meaningful_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip common signature/closing patterns
            skip_patterns = [
                r'^Logistics Manager[;,]?\s*$',
                r'^Best regards[;,]?\s*$',
                r'^Regards[;,]?\s*$',
                r'^Sincerely[;,]?\s*$',
                r'^Thank you[;,]?\s*$',
                r'^Please provide rates and transit time[;,]?\s*$',
                r'^Please provide[;,]?\s*$',
                r'^rates and transit time[;,]?\s*$',
                r'^Manager[;,]?\s*$',
                r'^Director[;,]?\s*$',
                r'^Coordinator[;,]?\s*$',
            ]
            
            should_skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
            
            if should_skip:
                continue
            
            # Remove these phrases from the line (but keep the line if other content remains)
            line = re.sub(r'Logistics Manager[;,]?\s*', '', line, flags=re.IGNORECASE)
            line = re.sub(r'Please provide rates and transit time[;,]?\s*', '', line, flags=re.IGNORECASE)
            line = re.sub(r'Please provide[;,]?\s*', '', line, flags=re.IGNORECASE)
            line = re.sub(r'rates and transit time[;,]?\s*', '', line, flags=re.IGNORECASE)
            line = line.strip(' .,;:')
            
            # Only add if line has meaningful content (at least 5 chars after cleaning)
            if line and len(line) >= 5:
                meaningful_lines.append(line)
        
        # Join meaningful lines
        cleaned = ' '.join(meaningful_lines)
        
        # Remove if it's just job titles or common email closings
        job_titles = ['logistics manager', 'manager', 'director', 'coordinator', 'executive']
        cleaned_lower = cleaned.lower().strip()
        if cleaned_lower in job_titles or cleaned_lower in ['best regards', 'regards', 'sincerely', 'thank you']:
            return ""
        
        # Remove if note is too short or just punctuation
        if len(cleaned.strip()) < 5:
            return ""
        
        # Remove trailing/leading punctuation and whitespace
        cleaned = cleaned.strip(' .,;:')
        
        # If after cleaning there's nothing meaningful, return empty
        if not cleaned or len(cleaned.strip()) < 3:
            return ""
        
        return cleaned.strip()
    
    def _generate_subject_line(self, extracted_data: Dict[str, Any], port_lookup_result: Dict[str, Any] = None) -> str:
        """
        Generate appropriate subject line with port names and codes for validation.
        Shows port codes if available from port lookup.
        """
        shipment = extracted_data.get("shipment_details", {})
        origin = shipment.get("origin", "origin")
        destination = shipment.get("destination", "destination")
        
        # Format with port codes if available (for customer validation)
        if port_lookup_result:
            if port_lookup_result.get("origin"):
                origin_result = port_lookup_result["origin"]
                port_name = origin_result.get("port_name", origin)
                port_code = origin_result.get("port_code", "")
                country = origin_result.get("country", "")
                if port_code:
                    if country and country != "Unknown":
                        origin = f"{port_name} ({port_code}), {country}"
                    else:
                        origin = f"{port_name} ({port_code})"
                elif country and country != "Unknown":
                    origin = f"{port_name}, {country}"
                else:
                    origin = port_name
            
            if port_lookup_result.get("destination"):
                destination_result = port_lookup_result["destination"]
                port_name = destination_result.get("port_name", destination)
                port_code = destination_result.get("port_code", "")
                country = destination_result.get("country", "")
                if port_code:
                    if country and country != "Unknown":
                        destination = f"{port_name} ({port_code}), {country}"
                    else:
                        destination = f"{port_name} ({port_code})"
                elif country and country != "Unknown":
                    destination = f"{port_name}, {country}"
                else:
                    destination = port_name
        
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
            container_standardization_result = data.get("container_standardization_result")
            
            # Ensure standardized container type is used (per spec: confirmation shows standardized container types)
            if container_standardization_result and isinstance(container_standardization_result, dict):
                standardized_type = container_standardization_result.get("standardized_type")
                if standardized_type and "shipment_details" in extracted_data:
                    extracted_data["shipment_details"]["container_type"] = standardized_type
            
            port_lookup_result = data.get("port_lookup_result")
            
            return self.generate_confirmation_response(
                extracted_data=extracted_data,
                customer_name=customer_name,
                agent_info=agent_info,
                tone=tone,
                rate_info=rate_info,
                container_standardization_result=container_standardization_result,
                port_lookup_result=port_lookup_result
            )
            
        except Exception as e:
            logger.error(f"Error in confirmation response processing: {e}")
            return {
                "error": f"Failed to generate confirmation response: {str(e)}",
                "response_type": "confirmation"
            } 