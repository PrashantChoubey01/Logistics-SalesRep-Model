#!/usr/bin/env python3
"""
Forwarder Response Agent
========================

Handles forwarder communications and generates appropriate responses.
Enhanced to extract rate information and send structured acknowledgments.
"""

import logging
import re
from datetime import datetime
from typing import Dict, Any
from agents.base_agent import BaseAgent

class ForwarderResponseAgent(BaseAgent):
    """Agent for handling forwarder communications and generating responses."""

    def __init__(self):
        super().__init__("forwarder_response_agent")
        self.logger = logging.getLogger(__name__)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process forwarder communication and generate response."""
        print("📧 FORWARDER_RESPONSE: Starting forwarder response generation...")
        
        try:
            # Extract input data
            email_data = input_data.get("email_data", {})
            forwarder_detection = input_data.get("forwarder_detection", {})
            conversation_state = input_data.get("conversation_state", {})
            
            # Get forwarder details
            forwarder_details = forwarder_detection.get("forwarder_details", {})
            forwarder_name = forwarder_details.get("name", "Forwarder")
            forwarder_email = forwarder_details.get("email", "")
            
            # Extract rate information from email (try multiple possible field names)
            email_text = (
                email_data.get("email_text", "") or 
                email_data.get("content", "") or 
                email_data.get("body_text", "") or
                email_data.get("body", "")
            )
            rate_info = self._extract_rate_information(email_text)
            
            # Generate response based on email content
            response = self._generate_forwarder_response(
                email_data, 
                forwarder_details, 
                conversation_state,
                rate_info
            )
            
            # Always generate acknowledgment for forwarder emails
            acknowledgment = self._generate_forwarder_acknowledgment(
                forwarder_name, 
                email_data, 
                rate_info
            )
            
            # Generate collate email for sales team if rate information is present
            collate_email = None
            if rate_info.get("rates_with_othc") or rate_info.get("rates_with_dthc") or rate_info.get("rates_without_thc"):
                collate_email = self._generate_collate_email_for_sales(
                    email_data, forwarder_details, rate_info, conversation_state
                )
            
            result = {
                "response_subject": acknowledgment["subject"],
                "response_body": acknowledgment["body"],
                "response_type": "forwarder_acknowledgment",
                "sales_person_email": "sales@searates.com",  # Common sales email
                "sales_person_name": "Sales Team",
                "forwarder_name": forwarder_name,
                "forwarder_email": forwarder_email,
                "extracted_rate_info": rate_info,
                "collate_email": collate_email,  # New field for sales team
                "response_method": "forwarder_specific_with_rate_extraction",
                "agent_name": self.agent_name,
                "agent_id": self.agent_id,
                "processed_at": self._now_iso(),
                "status": "success"
            }
            
            print(f"✅ FORWARDER_RESPONSE: Response generated for {forwarder_name}")
            print(f"   Response Type: {response['type']}")
            print(f"   Rate Info Extracted: {len(rate_info)} fields")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in forwarder response generation: {str(e)}")
            return {
                "response_subject": "Re: Your Inquiry",
                "response_body": "Thank you for your message. We will get back to you shortly.",
                "response_type": "generic_response",
                "sales_person_email": "sales@searates.com",
                "sales_person_name": "Sales Team",
                "error": str(e),
                "agent_name": self.agent_name,
                "agent_id": self.agent_id,
                "processed_at": self._now_iso(),
                "status": "error"
            }

    def _extract_rate_information(self, email_text: str) -> Dict[str, Any]:
        """Extract rate information from forwarder email."""
        rate_info = {
            "origin_port": None,
            "destination_port": None,
            "container_type": None,
            "rates_with_othc": None,  # Origin THC included
            "rates_with_dthc": None,  # Destination THC included
            "rates_without_thc": None,  # Freight only
            "transit_time": None,
            "valid_until": None,
            "sailing_date": None,
            "commodity": None,
            "additional_instructions": []
        }
        
        # Extract origin and destination ports
        port_patterns = [
            r"from\s+([A-Za-z\s]+)\s+to\s+([A-Za-z\s]+)",
            r"([A-Za-z\s]+)\s+to\s+([A-Za-z\s]+)",
            r"origin[:\s]*([A-Za-z\s]+)",
            r"destination[:\s]*([A-Za-z\s]+)"
        ]
        
        for pattern in port_patterns:
            matches = re.findall(pattern, email_text, re.IGNORECASE)
            if matches:
                if len(matches[0]) == 2:
                    rate_info["origin_port"] = matches[0][0].strip()
                    rate_info["destination_port"] = matches[0][1].strip()
                elif "origin" in pattern.lower():
                    rate_info["origin_port"] = matches[0].strip()
                elif "destination" in pattern.lower():
                    rate_info["destination_port"] = matches[0].strip()
                break
        
        # Extract container type
        container_patterns = [
            r"(\d+[A-Z]{2})",  # 20GP, 40GP, 40HC, etc.
            r"container[:\s]*([A-Za-z0-9\s]+)",
            r"(\d+ft\s*[A-Z]+)"  # 40ft HC, etc.
        ]
        
        for pattern in container_patterns:
            matches = re.findall(pattern, email_text, re.IGNORECASE)
            if matches:
                rate_info["container_type"] = matches[0].strip()
                break
        
        # Extract rates
        # Simple "Rate:" pattern (most common in forwarder emails)
        rate_patterns = [
            r"rate[:\s]*\$?\s*([\d,]+\.?\d*)\s*USD?",
            r"rate[:\s]*USD?\s*([\d,]+\.?\d*)",
            r"rate[:\s]*\$?\s*([\d,]+\.?\d*)",
            r"\$?\s*([\d,]+\.?\d*)\s*USD?\s*\(?rate\)?"
        ]
        
        for pattern in rate_patterns:
            matches = re.findall(pattern, email_text, re.IGNORECASE)
            if matches:
                rate_value = float(matches[0].replace(',', ''))
                # Store in rates_with_dthc as it's likely the total rate
                rate_info["rates_with_dthc"] = rate_value
                # Also store as a general rate field for compatibility
                rate_info["rate"] = rate_value
                break
        
        # Total rate (usually includes all charges)
        total_patterns = [
            r"total[:\s]*USD?\s*([\d,]+\.?\d*)",
            r"total[:\s]*\$?\s*([\d,]+\.?\d*)",
            r"USD?\s*([\d,]+\.?\d*)\s*\(?total\)?",
            r"\$?\s*([\d,]+\.?\d*)\s*\(?total\)?"
        ]
        
        for pattern in total_patterns:
            matches = re.findall(pattern, email_text, re.IGNORECASE)
            if matches:
                rate_info["rates_with_dthc"] = float(matches[0].replace(',', ''))
                break
        
        # Ocean freight (freight only)
        freight_patterns = [
            r"ocean\s*freight[:\s]*USD?\s*([\d,]+\.?\d*)",
            r"freight[:\s]*USD?\s*([\d,]+\.?\d*)",
            r"USD?\s*([\d,]+\.?\d*)\s*\(?freight\)?"
        ]
        
        for pattern in freight_patterns:
            matches = re.findall(pattern, email_text, re.IGNORECASE)
            if matches:
                rate_info["rates_without_thc"] = float(matches[0].replace(',', ''))
                break
        
        # THC charges
        thc_patterns = [
            r"thc\s*origin[:\s]*USD?\s*([\d,]+\.?\d*)",
            r"origin\s*thc[:\s]*USD?\s*([\d,]+\.?\d*)",
            r"thc\s*destination[:\s]*USD?\s*([\d,]+\.?\d*)",
            r"destination\s*thc[:\s]*USD?\s*([\d,]+\.?\d*)"
        ]
        
        othc_found = False
        dthc_found = False
        
        for pattern in thc_patterns:
            matches = re.findall(pattern, email_text, re.IGNORECASE)
            if matches:
                if "origin" in pattern.lower():
                    rate_info["rates_with_othc"] = rate_info["rates_without_thc"] + float(matches[0].replace(',', '')) if rate_info["rates_without_thc"] else None
                    othc_found = True
                elif "destination" in pattern.lower():
                    if not othc_found:
                        rate_info["rates_with_othc"] = rate_info["rates_without_thc"] + float(matches[0].replace(',', '')) if rate_info["rates_without_thc"] else None
                    dthc_found = True
        
        # Extract transit time
        transit_patterns = [
            r"transit\s*time[:\s]*(\d+)\s*days?",
            r"(\d+)\s*days?\s*transit",
            r"(\d+)\s*days?\s*delivery"
        ]
        
        for pattern in transit_patterns:
            matches = re.findall(pattern, email_text, re.IGNORECASE)
            if matches:
                rate_info["transit_time"] = int(matches[0])
                break
        
        # Extract dates
        date_patterns = [
            r"valid\s*until[:\s]*([A-Za-z]+\s+\d+,\s+\d{4})",
            r"sailing\s*date[:\s]*([A-Za-z]+\s+\d+,\s+\d{4})",
            r"([A-Za-z]+\s+\d+,\s+\d{4})\s*\(?valid\s*until\)?"
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, email_text, re.IGNORECASE)
            if matches:
                if "valid" in pattern.lower():
                    rate_info["valid_until"] = matches[0].strip()
                elif "sailing" in pattern.lower():
                    rate_info["sailing_date"] = matches[0].strip()
                break
        
        # Extract commodity
        commodity_patterns = [
            r"commodity[:\s]*([A-Za-z\s]+)",
            r"cargo[:\s]*([A-Za-z\s]+)",
            r"goods[:\s]*([A-Za-z\s]+)"
        ]
        
        for pattern in commodity_patterns:
            matches = re.findall(pattern, email_text, re.IGNORECASE)
            if matches:
                rate_info["commodity"] = matches[0].strip()
                break
        
        # Collect additional instructions (anything that doesn't fit the above patterns)
        lines = email_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and not any(keyword in line.lower() for keyword in [
                'dear', 'best regards', 'thank you', 'please', 'rate', 'freight', 'thc', 
                'total', 'transit', 'valid', 'sailing', 'container', 'commodity', 'origin', 'destination'
            ]):
                if len(line) > 10:  # Only add substantial lines
                    rate_info["additional_instructions"].append(line)
        
        return rate_info

    def _generate_forwarder_response(self, email_data: Dict[str, Any], 
                                   forwarder_details: Dict[str, Any], 
                                   conversation_state: Dict[str, Any],
                                   rate_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate appropriate response for forwarder communication."""
        
        email_text = email_data.get("email_text", "").lower()
        subject = email_data.get("subject", "").lower()
        forwarder_name = forwarder_details.get("name", "Forwarder")
        
        # Determine response type based on email content
        if any(keyword in email_text for keyword in ["rate", "quote", "pricing", "cost"]):
            return self._generate_rate_quote_acknowledgment(forwarder_name, email_data, rate_info)
        elif any(keyword in email_text for keyword in ["information", "details", "specification"]):
            return self._generate_information_request_response(forwarder_name, email_data)
        elif any(keyword in email_text for keyword in ["booking", "confirm", "proceed"]):
            return self._generate_booking_response(forwarder_name, email_data)
        elif any(keyword in email_text for keyword in ["issue", "problem", "concern"]):
            return self._generate_issue_response(forwarder_name, email_data)
        else:
            return self._generate_generic_response(forwarder_name, email_data)

    def _generate_rate_quote_acknowledgment(self, forwarder_name: str, email_data: Dict[str, Any], rate_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate acknowledgment with extracted rate information using LLM."""
        
        # Prepare rate information for LLM
        rate_details = []
        if rate_info["origin_port"] and rate_info["destination_port"]:
            rate_details.append(f"Route: {rate_info['origin_port']} to {rate_info['destination_port']}")
        
        if rate_info["container_type"]:
            rate_details.append(f"Container: {rate_info['container_type']}")
        
        if rate_info["rates_without_thc"]:
            rate_details.append(f"Ocean Freight: USD {rate_info['rates_without_thc']:,.2f}")
        
        if rate_info["rates_with_othc"]:
            rate_details.append(f"With Origin THC: USD {rate_info['rates_with_othc']:,.2f}")
        
        if rate_info["rates_with_dthc"]:
            rate_details.append(f"Total Rate: USD {rate_info['rates_with_dthc']:,.2f}")
        
        if rate_info["transit_time"]:
            rate_details.append(f"Transit Time: {rate_info['transit_time']} days")
        
        if rate_info["valid_until"]:
            rate_details.append(f"Valid Until: {rate_info['valid_until']}")
        
        if rate_info["sailing_date"]:
            rate_details.append(f"Sailing Date: {rate_info['sailing_date']}")
        
        if rate_info["commodity"]:
            rate_details.append(f"Commodity: {rate_info['commodity']}")
        
        # Use LLM to generate human-friendly response with email formatting
        prompt = f"""You are a professional sales representative at SeaRates by DP World. 
Generate a friendly, professional acknowledgment email to a forwarder who has sent a rate quote.

Forwarder Name: {forwarder_name}
Rate Details: {', '.join(rate_details) if rate_details else 'Rate information provided'}

REQUIREMENTS:
1. Professional, friendly, and warm tone
2. Acknowledge receipt of their rate quote in 1-2 sentences
3. Mention that the sales team will review it
4. Present rate details in structured bullet points
5. NO "next steps" sections
6. NO unnecessary information
7. Format as a professional email with proper structure

RESPONSE FORMAT:
From: Sales Team <sales@searates.com>
To: {forwarder_name} <{email_data.get('sender', 'forwarder@example.com')}>
Subject: Re: {email_data.get('subject', 'Rate Quote')}
Date: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')}

Dear {forwarder_name},

[Professional acknowledgment - 1-2 sentences]

Here are the rate details you provided:
* Route: [origin] to [destination]
* Container: [type]
* Commodity: [type]
* Rate Breakdown:
  + Ocean Freight: USD [amount]
  + With Origin THC: USD [amount] (if available)
  + Total Rate: USD [amount]
* Transit Time: [days] days
* Valid Until: [date]

[Brief closing - 1 sentence]

Best regards,
Sales Team
SeaRates by DP World
sales@searates.com

Generate the complete email with headers and body:
"""

        try:
            # Use the LLM to generate the response
            response_body = self._generate_llm_response(prompt)
            
            # Fallback if LLM fails
            if not response_body or len(response_body.strip()) < 50:
                # Build structured rate details for fallback
                rate_details_list = []
                if rate_info.get('origin_port') and rate_info.get('destination_port'):
                    rate_details_list.append(f"* Route: {rate_info['origin_port']} to {rate_info['destination_port']}")
                if rate_info.get('container_type'):
                    rate_details_list.append(f"* Container: {rate_info['container_type']}")
                if rate_info.get('commodity'):
                    rate_details_list.append(f"* Commodity: {rate_info['commodity']}")
                
                rate_breakdown = []
                if rate_info.get('rates_without_thc'):
                    rate_breakdown.append(f"  + Ocean Freight: USD {rate_info['rates_without_thc']:,.2f}")
                if rate_info.get('rates_with_othc'):
                    rate_breakdown.append(f"  + With Origin THC: USD {rate_info['rates_with_othc']:,.2f}")
                if rate_info.get('rates_with_dthc'):
                    rate_breakdown.append(f"  + Total Rate: USD {rate_info['rates_with_dthc']:,.2f}")
                
                if rate_breakdown:
                    rate_details_list.append("* Rate Breakdown:")
                    rate_details_list.extend(rate_breakdown)
                
                if rate_info.get('transit_time'):
                    rate_details_list.append(f"* Transit Time: {rate_info['transit_time']} days")
                if rate_info.get('valid_until'):
                    rate_details_list.append(f"* Valid Until: {rate_info['valid_until']}")
                
                rate_details_text = '\n'.join(rate_details_list) if rate_details_list else "Rate details are being reviewed."
                
                response_body = f"""Dear {forwarder_name},

Thank you for your rate quote. We have received your information and our sales team will review it shortly.

Here are the rate details you provided:
{rate_details_text}

Best regards,
Sales Team
SeaRates by DP World
sales@searates.com"""
            
        except Exception as e:
            self.logger.error(f"LLM generation failed: {str(e)}")
            # Fallback response
            response_body = f"""Dear {forwarder_name},

Thank you for your rate quote. We have received your information and our sales team will review it shortly.

Best regards,
Sales Team
SeaRates by DP World
sales@searates.com"""
        
        return {
            "type": "rate_quote_acknowledgment",
            "subject": f"Rate Quote Received - {forwarder_name}",
            "body": response_body
        }

    def _generate_information_request_response(self, forwarder_name: str, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for information requests."""
        return {
            "type": "information_response",
            "subject": f"Information Request - {forwarder_name}",
            "body": f"""Dear {forwarder_name},

Thank you for your inquiry. Our sales team will gather the information you need and get back to you within 24 hours.

Best regards,
Sales Team
SeaRates by DP World
sales@searates.com"""
        }

    def _generate_booking_response(self, forwarder_name: str, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for booking requests."""
        return {
            "type": "booking_response",
            "subject": f"Booking Request - {forwarder_name}",
            "body": f"""Dear {forwarder_name},

Thank you for your booking request. Our team will process this and send you confirmation within 2 hours.

Best regards,
Sales Team
SeaRates by DP World
sales@searates.com"""
        }

    def _generate_issue_response(self, forwarder_name: str, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response for issue reports."""
        return {
            "type": "issue_response",
            "subject": f"Issue Report - {forwarder_name}",
            "body": f"""Dear {forwarder_name},

Thank you for bringing this to our attention. We take all concerns seriously and our team will investigate immediately.

Best regards,
Sales Team
SeaRates by DP World
sales@searates.com"""
        }

    def _generate_generic_response(self, forwarder_name: str, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate generic response for other communications."""
        return {
            "type": "generic_response",
            "subject": f"Your Message - {forwarder_name}",
            "body": f"""Dear {forwarder_name},

Thank you for your message. Our sales team will review it and contact you shortly.

Best regards,
Sales Team
SeaRates by DP World
sales@searates.com"""
        }

    def _generate_llm_response(self, prompt: str) -> str:
        """Generate response using LLM."""
        try:
            # Ensure LLM client is loaded
            if not self.client:
                self.load_context()
            
            if not self.client:
                raise Exception("LLM client not available")
            
            model_name = self.config.get("model_name")
            if not model_name:
                raise Exception("Model name not configured")
            
            # Generate response using LLM (use OpenAI client for function calling)
            client = self.get_openai_client()
            if not client:
                raise Exception("OpenAI client not available")
            
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a professional sales representative at SeaRates by DP World. Generate friendly, professional, and human-like responses."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            if not content:
                raise Exception("Empty response from LLM")
            
            return content.strip()
            
        except Exception as e:
            self.logger.error(f"LLM generation failed: {str(e)}")
            raise e

    def _now_iso(self):
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()

    def _generate_collate_email_for_sales(self, email_data: Dict[str, Any], forwarder_details: Dict[str, Any], 
                                         rate_info: Dict[str, Any], conversation_state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive collate email for sales team with deal details."""
        
        # Extract customer information from conversation state
        customer_info = conversation_state.get("customer_info", {})
        customer_name = customer_info.get("name", "Customer")
        customer_email = customer_info.get("email", "customer@example.com")
        thread_id = email_data.get("thread_id", "N/A")
        
        # Extract forwarder information
        forwarder_name = forwarder_details.get("name", "Forwarder")
        forwarder_email = forwarder_details.get("email", "forwarder@example.com")
        
        # Format rate information
        rate_summary = self._format_rate_summary(rate_info)
        
        # Generate subject line
        origin = rate_info.get("origin_port", "Unknown")
        destination = rate_info.get("destination_port", "Unknown")
        subject = f"DEAL OPPORTUNITY - Customer: {customer_name} | Forwarder: {forwarder_name} | Route: {origin}-{destination}"
        
        # Generate comprehensive body
        body = f"""Dear Sales Team,

🚨 NEW DEAL OPPORTUNITY - ACTION REQUIRED 🚨

Customer Details:
- Name: {customer_name}
- Email: {customer_email}
- Thread ID: {thread_id}
- Original Request: {email_data.get('subject', 'Rate Quote Request')}

Forwarder Details:
- Name: {forwarder_name}
- Email: {forwarder_email}
- Rate Quote: {rate_info.get('rates_with_othc', 'N/A')} USD
- Valid Until: {rate_info.get('valid_until', 'N/A')}
- Sailing Date: {rate_info.get('sailing_date', 'N/A')}

Shipment Details:
- Origin: {rate_info.get('origin_port', 'N/A')}
- Destination: {rate_info.get('destination_port', 'N/A')}
- Container: {rate_info.get('container_type', 'N/A')}
- Commodity: {rate_info.get('commodity', 'N/A')}
- Transit Time: {rate_info.get('transit_time', 'N/A')}

Rate Information:
{rate_summary}

Additional Instructions:
{chr(10).join(rate_info.get('additional_instructions', ['None']))}

🎯 ACTION REQUIRED:
1. Contact customer ({customer_email}) to confirm acceptance of rates
2. Connect with forwarder ({forwarder_email}) to finalize booking
3. Coordinate between customer and forwarder for deal closure
4. Update system with final booking details
5. Ensure all documentation is completed

⚠️ URGENCY: This is a live deal opportunity - immediate action required!

Best regards,
AI Logistics System
SeaRates by DP World
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

        return {
            "subject": subject,
            "body": body,
            "type": "collate_email_for_sales",
            "priority": "high",
            "customer_email": customer_email,
            "forwarder_email": forwarder_email,
            "thread_id": thread_id
        }

    def _generate_forwarder_acknowledgment(self, forwarder_name: str, email_data: Dict[str, Any], rate_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate acknowledgment email to forwarder."""
        subject = f"Re: {email_data.get('subject', 'Rate Quote')}"
        
        # Check if rate information was extracted
        has_rates = rate_info.get("rates_with_othc") or rate_info.get("rates_with_dthc") or rate_info.get("rates_without_thc")
        
        if has_rates:
            body = f"""Dear {forwarder_name},

Thank you for providing the rate quote for this shipment.

We have received and processed your rate information:
- Origin: {rate_info.get('origin_port', 'N/A')}
- Destination: {rate_info.get('destination_port', 'N/A')}
- Container: {rate_info.get('container_type', 'N/A')}
- Transit Time: {rate_info.get('transit_time', 'N/A')}
- Valid Until: {rate_info.get('valid_until', 'N/A')}

Our sales team will review your quote and contact you shortly regarding next steps.

Best regards,
SeaRates Team
SeaRates by DP World
sales@searates.com"""
        else:
            body = f"""Dear {forwarder_name},

Thank you for your response regarding this shipment inquiry.

We have received your communication and our team will review it shortly.

Best regards,
SeaRates Team
SeaRates by DP World
sales@searates.com"""

        return {
            "subject": subject,
            "body": body,
            "type": "forwarder_acknowledgment"
        }

    def generate_forwarder_assignment_acknowledgment(self, forwarder_assignment: Dict[str, Any], customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate acknowledgment email for forwarder assignment."""
        
        # Get forwarder details
        forwarders = forwarder_assignment.get('assigned_forwarders', [])
        if not forwarders:
            return {"error": "No forwarders assigned"}
        
        # Get customer details
        customer_name = customer_data.get('customer_name', 'Customer')
        customer_email = customer_data.get('customer_email', 'customer@example.com')
        
        # Get shipment details
        extracted_data = customer_data.get('extracted_data', {})
        origin = extracted_data.get('origin_name', 'N/A')
        destination = extracted_data.get('destination_name', 'N/A')
        container_type = extracted_data.get('container_type', 'N/A')
        commodity = extracted_data.get('commodity', 'N/A')
        
        # Generate acknowledgment for each forwarder
        acknowledgments = []
        
        for forwarder in forwarders:
            forwarder_name = forwarder.get('name', 'Forwarder')
            forwarder_email = forwarder.get('email', 'forwarder@example.com')
            
            subject = f"Rate Request - {origin} to {destination} - {container_type}"
            
            body = f"""Dear {forwarder_name},

We hope this email finds you well. We are reaching out regarding a rate request for one of our valued customers.

**Customer Details:**
- Customer: {customer_name}
- Email: {customer_email}

**Shipment Details:**
- Origin: {origin}
- Destination: {destination}
- Container Type: {container_type}
- Commodity: {commodity}
- Shipment Type: FCL

**Request:**
We would appreciate if you could provide competitive rates for this shipment. Please include:
- Ocean freight rates
- Terminal handling charges (origin and destination)
- Documentation fees
- Transit time
- Valid until date
- Any additional charges

**Response Required:**
Please provide your rates within 24 hours to ensure timely processing.

**Contact Information:**
If you have any questions or need additional information, please don't hesitate to contact us.

We look forward to your prompt response.

Best regards,
SeaRates Team
SeaRates by DP World
sales@searates.com
Phone: +1-555-0123
Email: sales@searates.com"""

            acknowledgments.append({
                "forwarder_name": forwarder_name,
                "forwarder_email": forwarder_email,
                "subject": subject,
                "body": body,
                "type": "forwarder_assignment_acknowledgment",
                "timestamp": self._now_iso()
            })
        
        return {
            "acknowledgments": acknowledgments,
            "total_forwarders": len(forwarders),
            "status": "success",
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "processed_at": self._now_iso()
        }

    def _format_rate_summary(self, rate_info: Dict[str, Any]) -> str:
        """Format rate information for sales team."""
        summary = []
        
        if rate_info.get("rates_with_othc"):
            summary.append(f"• Rate with OTHC: USD {rate_info['rates_with_othc']}")
        if rate_info.get("rates_with_dthc"):
            summary.append(f"• Rate with DTHC: USD {rate_info['rates_with_dthc']}")
        if rate_info.get("rates_without_thc"):
            summary.append(f"• Freight Only: USD {rate_info['rates_without_thc']}")
        
        if not summary:
            summary.append("• Rate information not clearly specified")
        
        return "\n".join(summary)


def test_forwarder_response_agent():
    """Test the enhanced forwarder response agent."""
    
    print("🧪 Testing Enhanced Forwarder Response Agent")
    print("=" * 50)
    
    agent = ForwarderResponseAgent()
    
    # Test rate quote extraction
    rate_quote_email = {
        "email_text": """Dear DP World Team,

Thank you for your rate request for Shanghai to Los Angeles shipment.

Please find our competitive quote below:

**Rate Details:**
- Ocean Freight: USD 2,800 per 40HC
- THC Origin: USD 120
- THC Destination: USD 180
- Documentation: USD 45
- **Total: USD 3,145**

**Service Details:**
- Transit Time: 16 days
- Valid Until: March 15, 2024
- Sailing Date: March 20, 2024
- Container: 40HC
- Commodity: Electronics

**Special Services:**
- Temperature controlled if needed
- Insurance available
- Door-to-door service option

Please let us know if you need any clarification.

Best regards,
DHL Global Forwarding
dhl.global.forwarding@logistics.com""",
        "subject": "Rate Quote - Shanghai to Los Angeles (40HC)",
        "sender": "dhl.global.forwarding@logistics.com"
    }
    
    input_data = {
        "email_data": rate_quote_email,
        "forwarder_detection": {
            "forwarder_details": {
                "name": "DHL Global Forwarding",
                "email": "dhl.global.forwarding@logistics.com"
            }
        },
        "conversation_state": {
            "conversation_state": "thread_forwarder_interaction"
        }
    }
    
    result = agent.process(input_data)
    
    print(f"📊 Results:")
    print(f"   Response Type: {result['response_type']}")
    print(f"   Sales Email: {result['sales_person_email']}")
    print(f"   Subject: {result['response_subject']}")
    
    # Show extracted rate info
    rate_info = result.get('extracted_rate_info', {})
    print(f"\n📋 Extracted Rate Information:")
    for key, value in rate_info.items():
        if value:
            print(f"   {key}: {value}")
    
    print(f"\n📄 Response Preview:")
    print(f"   {result['response_body'][:300]}...")
    
    print(f"\n✅ Enhanced Forwarder Response Test Completed")


if __name__ == "__main__":
    test_forwarder_response_agent() 