#!/usr/bin/env python3
"""
Clarification Response Agent
===========================

Generates human-like clarification responses using LLM
while sharing extracted data for customer validation.
"""

import json
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class ClarificationResponseAgent(BaseAgent):
    """Generates clarification responses for missing information using LLM"""
    
    def __init__(self):
        super().__init__("clarification_response_agent")
        self.load_context()
    
    def load_context(self):
        """Load agent context and configuration"""
        # No predefined templates - using LLM for dynamic responses
        pass
    
    def generate_clarification_response(self, 
                                      extracted_data: Dict[str, Any],
                                      missing_fields: List[str],
                                      customer_name: str = "Valued Customer",
                                      agent_info: Dict[str, str] = None,
                                      tone: str = "professional",
                                      port_lookup_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a human-like clarification response using LLM
        
        Args:
            extracted_data: Information extracted from customer email
            missing_fields: List of missing required fields
            customer_name: Customer's name
            agent_info: Sales agent information
            tone: Response tone (professional/friendly)
        
        Returns:
            Dictionary containing response details
        """
        try:
            # Debug logging
            logger.info(f"🔍 DEBUG: Generating clarification response")
            logger.info(f"🔍 DEBUG: Extracted data: {json.dumps(extracted_data, indent=2)}")
            logger.info(f"🔍 DEBUG: Port lookup result: {json.dumps(port_lookup_result, indent=2) if port_lookup_result else 'None'}")
            
            # Determine missing fields based on business rules if not provided
            if not missing_fields:
                missing_fields = self._determine_missing_fields(extracted_data)
            
            logger.info(f"Generating clarification response for {len(missing_fields)} missing fields")
            
            # Generate response using LLM
            response_body = self._generate_llm_response(
                extracted_data, missing_fields, customer_name, agent_info, tone, port_lookup_result
            )
            
            # Generate subject line
            subject = self._generate_subject_line(extracted_data, port_lookup_result)
            
            response = {
                "response_type": "clarification",
                "subject": subject,
                "body": response_body,
                "tone": tone,
                "missing_fields": missing_fields,
                "extracted_data_shared": extracted_data,
                "confidence_level": "high",
                "response_quality": 95,
                "reasoning": "Customer provided partial information, clarification needed for complete quote"
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating clarification response: {e}")
            return self._generate_fallback_response(missing_fields, customer_name, extracted_data, port_lookup_result)
    
    def _format_extracted_info(self, extracted_data: Dict[str, Any], port_lookup_result: Dict[str, Any] = None) -> str:
        """
        Format extracted information for display with standardized port names.
        Per spec: Clarification responses show enriched ports with port codes (e.g., "Shanghai (CNSHG)").
        """
        formatted_sections = []
        
        # Shipment details
        if "shipment_details" in extracted_data:
            shipment = extracted_data["shipment_details"]
            # Always create shipment section if shipment_details exists, even if some fields are empty
            shipment_text = "**Shipment Details:**\n"
            has_any_data = False
                
            # Origin with standardized port name, port code, and country (per spec: clarification shows codes)
            origin = shipment.get("origin", "").strip() if shipment.get("origin") else ""
            if origin:
                has_any_data = True
                origin_display = origin
                # Use port_lookup_result to get enriched port with code and country
                if port_lookup_result and port_lookup_result.get("origin"):
                    origin_result = port_lookup_result["origin"]
                    port_name = origin_result.get('port_name', origin)
                    port_code = origin_result.get('port_code', '')
                    country = origin_result.get('country', '')
                    
                    # Format: If country is available and different from port_name, show both
                    # Format: "Port Name (Port Code), Country" or "Country - Port Name (Port Code)" if country was input
                    if port_code:
                        if country and country != "Unknown" and country.lower() != port_name.lower():
                            # Check if original input was a country name (e.g., "USA", "China")
                            origin_lower = origin.lower()
                            country_lower = country.lower()
                            # If input matches country better than port name, show country first
                            if country_lower in origin_lower or origin_lower in country_lower:
                                origin_display = f"{country} - {port_name} ({port_code})"
                            else:
                                origin_display = f"{port_name} ({port_code}), {country}"
                        else:
                            origin_display = f"{port_name} ({port_code})"
                    elif country and country != "Unknown" and country.lower() != port_name.lower():
                        origin_display = f"{port_name}, {country}"
                    else:
                        origin_display = port_name if port_name else origin
                shipment_text += f"• Origin: {origin_display}\n"
                
            # Destination with standardized port name, port code, and country (per spec: clarification shows codes)
            destination = shipment.get("destination", "").strip() if shipment.get("destination") else ""
            if destination:
                has_any_data = True
                destination_display = destination
                # Use port_lookup_result to get enriched port with code and country
                if port_lookup_result and port_lookup_result.get("destination"):
                    destination_result = port_lookup_result["destination"]
                    port_name = destination_result.get('port_name', destination)
                    port_code = destination_result.get('port_code', '')
                    country = destination_result.get('country', '')
                    
                    # Format: If country is available and different from port_name, show both
                    # Format: "Port Name (Port Code), Country" or "Country - Port Name (Port Code)" if country was input
                    if port_code:
                        if country and country != "Unknown" and country.lower() != port_name.lower():
                            # Check if original input was a country name (e.g., "USA", "China")
                            destination_lower = destination.lower()
                            country_lower = country.lower()
                            # If input matches country better than port name, show country first
                            if country_lower in destination_lower or destination_lower in country_lower:
                                destination_display = f"{country} - {port_name} ({port_code})"
                            else:
                                destination_display = f"{port_name} ({port_code}), {country}"
                        else:
                            destination_display = f"{port_name} ({port_code})"
                    elif country and country != "Unknown" and country.lower() != port_name.lower():
                        destination_display = f"{port_name}, {country}"
                    else:
                        destination_display = port_name if port_name else destination
                shipment_text += f"• Destination: {destination_display}\n"
                
            # Container information
            container_type = shipment.get("container_type", "").strip() if shipment.get("container_type") else ""
            if container_type:
                has_any_data = True
                shipment_text += f"• Container Type: {container_type}\n"
            
            container_count = shipment.get("container_count", "").strip() if shipment.get("container_count") else ""
            if container_count:
                has_any_data = True
                shipment_text += f"• Quantity: {container_count}\n"
                
            # Commodity
            commodity = shipment.get("commodity", "").strip() if shipment.get("commodity") else ""
            if commodity:
                has_any_data = True
                shipment_text += f"• Commodity: {commodity}\n"
                
            # Weight and volume
            weight = shipment.get("weight", "").strip() if shipment.get("weight") else ""
            if weight:
                has_any_data = True
                shipment_text += f"• Weight: {weight}\n"
            
            volume = shipment.get("volume", "").strip() if shipment.get("volume") else ""
            if volume:
                has_any_data = True
                shipment_text += f"• Volume: {volume}\n"
            
            # Incoterm
            incoterm = shipment.get("incoterm", "").strip() if shipment.get("incoterm") else ""
            if incoterm:
                has_any_data = True
                shipment_text += f"• Incoterm: {incoterm}\n"
                
            # Timeline information
            timeline_info = extracted_data.get("timeline_information", {})
            requested_dates = timeline_info.get("requested_dates", "").strip() if timeline_info.get("requested_dates") else ""
            if requested_dates:
                has_any_data = True
                shipment_text += f"• Shipment Date: {requested_dates}\n"
            
            # Only add section if we have at least one field
            if has_any_data:
                formatted_sections.append(shipment_text)
        
        # Contact information
        if "contact_information" in extracted_data:
            contact = extracted_data["contact_information"]
            if any(contact.values()):
                contact_text = "**Contact Information:**\n"
                if contact.get("name"):
                    contact_text += f"• Name: {contact['name']}\n"
                if contact.get("email"):
                    contact_text += f"• Email: {contact['email']}\n"
                if contact.get("phone"):
                    contact_text += f"• Phone: {contact['phone']}\n"
                if contact.get("company"):
                    contact_text += f"• Company: {contact['company']}\n"
                formatted_sections.append(contact_text)
        
        # Special requirements
        if "special_requirements" in extracted_data and extracted_data["special_requirements"]:
            requirements_text = "**Special Requirements:**\n"
            for req in extracted_data["special_requirements"]:
                requirements_text += f"• {req}\n"
            formatted_sections.append(requirements_text)
        
        # Additional notes
        if extracted_data.get("additional_notes"):
            notes_text = "**Additional Notes:**\n"
            notes_text += f"• {extracted_data['additional_notes']}\n"
            formatted_sections.append(notes_text)
        
        return "\n".join(formatted_sections) if formatted_sections else "No specific details provided yet."
    
    def _generate_llm_response(self, extracted_data: Dict[str, Any], missing_fields: List[str], 
                             customer_name: str, agent_info: Dict[str, str], tone: str, 
                             port_lookup_result: Dict[str, Any]) -> str:
        """Generate response using LLM - ALWAYS includes extracted information section per spec"""
        
        if not self.client:
            self.load_context()
        
        if not self.client:
            return self._generate_fallback_response(missing_fields, customer_name, extracted_data, port_lookup_result)["body"]
        
        # Format extracted information - MUST be included in response per spec
        extracted_info = self._format_extracted_info(extracted_data, port_lookup_result)
        missing_info = self._format_missing_fields(missing_fields)
        
        # Get agent signature
        signature = agent_info.get("signature", "") if agent_info else ""
        
        prompt = f"""
You are a professional logistics sales representative. Generate a {tone} email response to a customer who has provided some shipping information but is missing required details.

CUSTOMER NAME: {customer_name}

EXTRACTED INFORMATION FROM CUSTOMER (this will be displayed separately - DO NOT mention specific port names or details):
{extracted_info}

MISSING REQUIRED INFORMATION:
{missing_info}

AGENT SIGNATURE:
{signature}

INSTRUCTIONS:
1. Write a completely unique and dynamic email response - DO NOT use any templates or standard phrases
2. Make the response sound natural and conversational, as if written by a real person
3. Acknowledge that you've reviewed their information and found some details that need clarification
4. Clearly explain what additional information is needed and why it's important
5. Use a {tone} tone - professional but approachable
6. Keep the response concise but comprehensive
7. Make it easy for the customer to provide the missing information
8. Vary your language and sentence structure - avoid repetitive patterns
9. Be creative with your opening and closing statements
10. DO NOT mention specific port names, container types, or shipment details in your response - these will be shown separately

RESPONSE REQUIREMENTS:
- Start with a unique greeting using the customer's name
- Thank them for their inquiry and acknowledge that you've reviewed their information
- Explain what's missing and why it's needed in a helpful way
- Provide clear instructions on how to provide the information
- End with a professional but friendly closing
- Make each response sound different from typical template responses
- DO NOT include the agent signature in your response - it will be added separately

IMPORTANT: 
- Focus on explaining what's missing and why it's needed
- This response should sound like it was written by a real person, not a template
- The extracted information section will be added separately, so do NOT include it in your response
- DO NOT mention specific ports, cities, container types, or other extracted details - just reference "the information you provided" or "your shipment details"

Generate ONLY the email body text (greeting, explanation of missing info, closing - NO signature):
"""
        
        try:
            # Use OpenAI client
            client = self.get_openai_client()
            if not client:
                raise Exception("OpenAI client not available")
            
            response = client.chat.completions.create(
                model=self.config.get("model_name"),
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,  # Higher temperature for more creative responses
                max_tokens=800
            )
            
            llm_response_text = response.choices[0].message.content.strip()
            
            # Clean the response to ensure JSON safety
            llm_response_text = self._clean_response_for_json(llm_response_text)
            
            # CRITICAL: Per spec, clarification responses MUST explicitly show extracted information
            # Combine LLM response with extracted information section
            # Format: Introduction + Extracted Info Section + Missing Info + Closing
            
            # Build the full response
            full_response_parts = [llm_response_text]
            
            # Add extracted information section if we have any data
            if extracted_info and extracted_info.strip() and extracted_info != "No specific details provided yet.":
                full_response_parts.append("")
                full_response_parts.append("I've carefully reviewed your email and extracted the following information. Please take a moment to confirm these details are accurate:")
                full_response_parts.append("")
                full_response_parts.append(extracted_info)
            
            # Add next steps section
            if missing_info and missing_info.strip() and missing_info != "All required information has been provided.":
                full_response_parts.append("")
                full_response_parts.append("**Next Steps:**")
                full_response_parts.append("")
                full_response_parts.append(missing_info)
                full_response_parts.append("")
                full_response_parts.append("Please provide the missing information, and I'll proceed with preparing your comprehensive shipping quote.")
            
            # Add signature
            if signature:
                full_response_parts.append("")
                full_response_parts.append(signature)
            
            full_response = "\n".join(full_response_parts)
            
            return full_response
            
        except Exception as e:
            logger.error(f"LLM response generation failed: {e}")
            return self._generate_fallback_response(missing_fields, customer_name, extracted_data, port_lookup_result)["body"]
    
    def _determine_missing_fields(self, extracted_data: Dict[str, Any]) -> List[str]:
        """Determine missing required fields based on shipment type and business rules"""
        shipment_details = extracted_data.get("shipment_details", {})
        timeline_info = extracted_data.get("timeline_information", {})
        
        # Determine shipment type
        container_type = shipment_details.get("container_type", "").strip()
        container_count = shipment_details.get("container_count", "").strip()
        
        # FCL indicators: container type OR quantity OR mentions of "containers"
        is_fcl = bool(container_type or container_count or "container" in str(shipment_details).lower())
        
        missing_fields = []
        
        # Common required fields for both FCL and LCL
        if not shipment_details.get("origin", "").strip():
            missing_fields.append("Origin port name/code")
        if not shipment_details.get("destination", "").strip():
            missing_fields.append("Destination port name/code")
        if not shipment_details.get("commodity", "").strip():
            missing_fields.append("Commodity name")
        
        # Check for shipment date in timeline information
        requested_dates = timeline_info.get("requested_dates", "").strip()
        if not requested_dates:
            missing_fields.append("Shipment date")
        
        # FCL specific requirements
        if is_fcl:
            if not container_type:
                missing_fields.append("Container type (20GP, 40GP, 40HC, etc.)")
            if not container_count:
                missing_fields.append("Number of containers (e.g., 1, 2, 3)")
            # For FCL, weight and volume are NOT required if container type and quantity are provided
        else:
            # LCL specific requirements
            if not shipment_details.get("weight", "").strip():
                missing_fields.append("Weight")
            if not shipment_details.get("volume", "").strip():
                missing_fields.append("Volume")
        
        return missing_fields
    
    def _format_missing_fields(self, missing_fields: List[str]) -> str:
        """Format missing fields as a list"""
        if not missing_fields:
            return "All required information has been provided."
        
        formatted_fields = []
        for field in missing_fields:
            # Convert field names to user-friendly format
            friendly_name = field.replace("_", " ").title()
            formatted_fields.append(f"• {friendly_name}")
        
        return "\n".join(formatted_fields)
    
    def _generate_subject_line(self, extracted_data: Dict[str, Any], port_lookup_result: Dict[str, Any] = None) -> str:
        """
        Generate appropriate subject line with standardized port names and codes.
        Per spec: Clarification responses show enriched ports with port codes (e.g., "Shanghai (CNSHG)").
        """
        shipment = extracted_data.get("shipment_details", {})
        origin = shipment.get("origin", "origin")
        destination = shipment.get("destination", "destination")
        
        # Use port_lookup_result to get enriched port with code (per spec: clarification shows codes)
        if port_lookup_result:
            if port_lookup_result.get("origin"):
                origin_result = port_lookup_result["origin"]
                port_name = origin_result.get("port_name", origin)
                port_code = origin_result.get("port_code", "")
                if port_code:
                    origin = f"{port_name} ({port_code})"  # Show with code per spec
                else:
                    origin = port_name
            
            if port_lookup_result.get("destination"):
                destination_result = port_lookup_result["destination"]
                port_name = destination_result.get("port_name", destination)
                port_code = destination_result.get("port_code", "")
                if port_code:
                    destination = f"{port_name} ({port_code})"  # Show with code per spec
                else:
                    destination = port_name
        
        return f"Additional Information Needed - Shipping from {origin} to {destination}"
    
    def _generate_fallback_response(self, missing_fields: List[str], customer_name: str, 
                                  extracted_data: Dict[str, Any] = None, 
                                  port_lookup_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a fallback response if main generation fails"""
        
        # Format extracted information for validation display
        extracted_info = ""
        if extracted_data:
            extracted_info = self._format_extracted_info(extracted_data, port_lookup_result)
        
        # Format missing fields
        missing_info = self._format_missing_fields(missing_fields)
        
        body = f"""Dear {customer_name},

Thank you for your inquiry. I've reviewed the information you provided and need some additional details to prepare your quote.

{extracted_info}

**Missing Required Information:**
{missing_info}

Please provide these details, and I'll be happy to assist you further.

Best regards,
Digital Sales Specialist
sales@searates.com"""
        
        # Generate subject line with port standardization
        subject = self._generate_subject_line(extracted_data, port_lookup_result) if extracted_data else "Additional Information Needed"
        
        return {
            "response_type": "clarification",
            "subject": subject,
            "body": body,
            "tone": "professional",
            "missing_fields": missing_fields,
            "extracted_data_shared": extracted_data or {},
            "confidence_level": "medium",
            "response_quality": 70,
            "reasoning": "Fallback response generated due to processing error"
        }
    
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process request and generate clarification response"""
        try:
            extracted_data = data.get("extracted_data", {})
            missing_fields = data.get("missing_fields", [])
            customer_name = data.get("customer_name", "Valued Customer")
            agent_info = data.get("agent_info")
            tone = data.get("tone", "professional")
            
            port_lookup_result = data.get("port_lookup_result")
            
            return self.generate_clarification_response(
                extracted_data=extracted_data,
                missing_fields=missing_fields,
                customer_name=customer_name,
                agent_info=agent_info,
                tone=tone,
                port_lookup_result=port_lookup_result
            )
            
        except Exception as e:
            logger.error(f"Error in clarification response processing: {e}")
            return {
                "error": f"Failed to generate clarification response: {str(e)}",
                "response_type": "clarification"
            }
    
    def _clean_response_for_json(self, response_text: str) -> str:
        """Clean response text to ensure JSON safety"""
        if not response_text:
            return response_text
        
        # Remove any problematic characters that could cause JSON parsing issues
        problematic_chars = ['📋', '🚢', '👤', '📝', '📄', '🔍', '✅', '❓', '📧', '📊', '🎯', '🔄', '💾', '📚']
        
        for char in problematic_chars:
            response_text = response_text.replace(char, '')
        
        # Remove any markdown formatting that might cause issues
        response_text = response_text.replace('**', '').replace('*', '')
        
        # Ensure no trailing whitespace or newlines that could cause issues
        response_text = response_text.strip()
        
        return response_text 