#!/usr/bin/env python3
"""
Acknowledgment Response Agent
============================

Generates appropriate acknowledgment responses for:
- Sales person emails
- Forwarder emails
- Customer emails (general acknowledgments)

Uses the updated sales team configuration with Searates By DP World branding.
"""

import json
from typing import Dict, Any, List, Optional
from agents.base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class AcknowledgmentResponseAgent(BaseAgent):
    """Generates acknowledgment responses for different sender types"""

    def __init__(self):
        super().__init__("acknowledgment_response_agent")
        self.load_context()

    def load_context(self):
        """Load acknowledgment templates and sales team configuration"""
        try:
            # Load sales team configuration
            with open("config/sales_team.json", "r") as f:
                sales_config = json.load(f)
                self.response_templates = sales_config.get("response_templates", {})
                self.sales_team = sales_config.get("sales_team", [])
        except Exception as e:
            logger.error(f"Error loading sales team config: {e}")
            self.response_templates = {}
            self.sales_team = []

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate appropriate acknowledgment response based on sender type.
        
        Args:
            data: Dictionary containing:
                - sender_type: "sales_person", "forwarder", or "customer"
                - sender_email: Email address of sender
                - sender_details: Details about the sender
                - email_content: Original email content
                - thread_id: Thread identifier
                - assigned_sales_person: Currently assigned sales person
        
        Returns:
            Dictionary containing acknowledgment response
        """
        try:
            sender_type = data.get("sender_type", "customer")
            sender_email = data.get("sender_email", "")
            sender_details = data.get("sender_details", {})
            email_content = data.get("email_content", "")
            thread_id = data.get("thread_id", "")
            assigned_sales_person = data.get("assigned_sales_person", {})

            logger.info(f"Generating acknowledgment for {sender_type}: {sender_email}")

            if sender_type == "sales_person":
                return self._generate_sales_person_acknowledgment(
                    sender_email, sender_details, email_content, assigned_sales_person
                )
            elif sender_type == "forwarder":
                return self._generate_forwarder_acknowledgment(
                    sender_email, sender_details, email_content, assigned_sales_person
                )
            else:
                return self._generate_customer_acknowledgment(
                    sender_email, email_content, assigned_sales_person
                )

        except Exception as e:
            logger.error(f"Error generating acknowledgment: {e}")
            return {
                "error": f"Failed to generate acknowledgment: {str(e)}",
                "response_type": "acknowledgment"
            }

    def _generate_sales_person_acknowledgment(self, sender_email: str, sender_details: Dict[str, Any], 
                                            email_content: str, assigned_sales_person: Dict[str, Any]) -> Dict[str, Any]:
        """Generate acknowledgment for sales person emails"""
        try:
            # Get sender name from details
            sender_name = sender_details.get("name", "Team Member")
            
            # Extract key information from email content
            subject = self._extract_subject_from_content(email_content)
            
            response_body = f"""Dear {sender_name},

Thank you for your email regarding {subject or 'your inquiry'}.

I have received your message and will review the details. If any action is required, I will follow up accordingly.

Best regards,

{assigned_sales_person.get('name', 'Digital Sales Specialist')}
Digital Sales Specialist
Searates By DP World
📧 {assigned_sales_person.get('email', 'sales@searates.com')}
📞 {assigned_sales_person.get('phone', '+1-555-0123')}
🌐 www.searates.com"""

            return {
                "response_type": "sales_person_acknowledgment",
                "subject": f"Re: {subject or 'Your Inquiry'}",
                "body": response_body,
                "sender_type": "sales_person",
                "sender_email": sender_email,
                "sender_name": sender_name,
                "confidence_level": "high",
                "response_quality": 95,
                "reasoning": "Professional acknowledgment for internal sales team member"
            }

        except Exception as e:
            logger.error(f"Error generating sales person acknowledgment: {e}")
            return self._generate_fallback_acknowledgment(sender_email, "sales_person")

    def _generate_forwarder_acknowledgment(self, sender_email: str, sender_details: Dict[str, Any], 
                                         email_content: str, assigned_sales_person: Dict[str, Any]) -> Dict[str, Any]:
        """Generate acknowledgment for forwarder emails"""
        try:
            # Get forwarder name from details
            forwarder_name = sender_details.get("name", "Forwarder Team")
            company = sender_details.get("company", "Forwarder Company")
            
            # Extract key information from email content
            subject = self._extract_subject_from_content(email_content)
            
            # Use template from config if available
            template = self.response_templates.get("forwarder_acknowledgment", {})
            if template:
                response_body = template["body"].format(
                    forwarder_name=forwarder_name,
                    origin="your origin",
                    destination="your destination",
                    sales_person_name=assigned_sales_person.get('name', 'Digital Sales Specialist'),
                    sales_person_title=assigned_sales_person.get('title', 'Digital Sales Specialist'),
                    sales_person_email=assigned_sales_person.get('email', 'sales@searates.com'),
                    sales_person_phone=assigned_sales_person.get('phone', '+1-555-0123')
                )
            else:
                response_body = f"""Dear {forwarder_name},

Thank you for your email regarding {subject or 'your inquiry'}.

We have received your message and our team is reviewing the details. You can expect a response within 24 hours.

If you have any urgent requirements, please don't hesitate to contact us immediately.

Best regards,

{assigned_sales_person.get('name', 'Digital Sales Specialist')}
Digital Sales Specialist
Searates By DP World
📧 {assigned_sales_person.get('email', 'sales@searates.com')}
📞 {assigned_sales_person.get('phone', '+1-555-0123')}
🌐 www.searates.com"""

            return {
                "response_type": "forwarder_acknowledgment",
                "subject": f"Re: {subject or 'Your Inquiry'}",
                "body": response_body,
                "to": sender_email,  # Add 'to' field for UI display
                "sender_type": "forwarder",
                "sender_email": sender_email,
                "sender_name": forwarder_name,
                "company": company,
                "confidence_level": "high",
                "response_quality": 95,
                "reasoning": "Professional acknowledgment for forwarder partner"
            }

        except Exception as e:
            logger.error(f"Error generating forwarder acknowledgment: {e}")
            return self._generate_fallback_acknowledgment(sender_email, "forwarder")

    def _generate_customer_acknowledgment(self, sender_email: str, email_content: str, 
                                        assigned_sales_person: Dict[str, Any]) -> Dict[str, Any]:
        """Generate acknowledgment for customer emails"""
        try:
            # Extract key information from email content
            subject = self._extract_subject_from_content(email_content)
            
            # Use template from config if available
            template = self.response_templates.get("acknowledgment", {})
            if template:
                response_body = template["body"].format(
                    sender_name="Valued Customer",
                    origin="your origin",
                    destination="your destination",
                    agent_name=assigned_sales_person.get('name', 'Digital Sales Specialist')
                )
            else:
                response_body = f"""Dear Valued Customer,

Thank you for reaching out to Searates By DP World regarding {subject or 'your shipping inquiry'}.

We have received your request and our team is currently reviewing the details. You can expect a comprehensive response within 24 hours.

If you have any urgent requirements, please don't hesitate to contact us immediately.

Best regards,

{assigned_sales_person.get('name', 'Digital Sales Specialist')}
Digital Sales Specialist
Searates By DP World
📧 {assigned_sales_person.get('email', 'sales@searates.com')}
📞 {assigned_sales_person.get('phone', '+1-555-0123')}
🌐 www.searates.com"""

            return {
                "response_type": "customer_acknowledgment",
                "subject": f"Thank you for your inquiry - {subject or 'Shipping Request'}",
                "body": response_body,
                "sender_type": "customer",
                "sender_email": sender_email,
                "confidence_level": "high",
                "response_quality": 95,
                "reasoning": "Professional acknowledgment for customer inquiry"
            }

        except Exception as e:
            logger.error(f"Error generating customer acknowledgment: {e}")
            return self._generate_fallback_acknowledgment(sender_email, "customer")

    def _extract_subject_from_content(self, email_content: str) -> str:
        """Extract subject or key topic from email content"""
        if not email_content:
            return ""
        
        # Simple extraction - look for common patterns
        lines = email_content.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line.startswith('Subject:') or line.startswith('Re:') or line.startswith('Fwd:'):
                return line.replace('Subject:', '').replace('Re:', '').replace('Fwd:', '').strip()
            if 'rate' in line.lower() or 'quote' in line.lower() or 'shipment' in line.lower():
                return line[:50] + "..." if len(line) > 50 else line
        
        return ""

    def _generate_fallback_acknowledgment(self, sender_email: str, sender_type: str) -> Dict[str, Any]:
        """Generate fallback acknowledgment if main generation fails"""
        return {
            "response_type": f"{sender_type}_acknowledgment",
            "subject": "Thank you for your email",
            "body": f"""Dear {sender_type.title()},

Thank you for your email. We have received your message and will respond shortly.

Best regards,

Digital Sales Specialist
Searates By DP World
📧 sales@searates.com
📞 +1-555-0123
🌐 www.searates.com""",
            "sender_type": sender_type,
            "sender_email": sender_email,
            "confidence_level": "medium",
            "response_quality": 80,
            "reasoning": "Fallback acknowledgment generated due to processing error"
        } 