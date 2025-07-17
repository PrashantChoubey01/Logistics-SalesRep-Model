"""Email Sender Agent: Sends acknowledgment emails to customers and notifications to forwarders."""

import json
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional
try:
    from .base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class EmailSenderAgent(BaseAgent):
    """Agent to send emails to customers and forwarders with safety controls."""

    def __init__(self):
        super().__init__("email_sender_agent")
        
        # Load email configuration from file
        self.email_config = self._load_email_config()
        
        self.logger = logging.getLogger(__name__)

    def _load_email_config(self) -> Dict[str, Any]:
        """Load email configuration from JSON file."""
        try:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "email_config.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                self.logger.info("Email configuration loaded from file")
                return config
            else:
                self.logger.warning("Email config file not found, using default configuration")
                return self._get_default_config()
        except Exception as e:
            self.logger.error(f"Failed to load email config: {e}, using default configuration")
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default email configuration."""
        return {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "sender_email": "logistics@dummycompany.com",  # Dummy email
            "sender_password": "dummy_password",  # Dummy password
            "enable_email_sending": False,  # Safety flag - set to True only in production
            "test_mode": True,  # Always in test mode for safety
            "allowed_domains": ["dummycompany.com", "test.com"],  # Whitelist for safety
            "max_emails_per_request": 2
        }
        
        self.logger = logging.getLogger(__name__)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send emails based on workflow state.
        
        Expected input:
        - email_type: "customer_acknowledgment" or "forwarder_notification"
        - customer_email: Customer's email address
        - forwarder_email: Forwarder's email address (for forwarder notifications)
        - subject: Email subject
        - body: Email body
        - thread_id: Thread identifier
        - confirmation_data: Confirmation details (for customer acknowledgment)
        - forwarder_assignment: Forwarder assignment details
        """
        email_type = input_data.get("email_type", "")
        thread_id = input_data.get("thread_id", "")
        
        if not email_type:
            return {"error": "No email type specified"}
        
        if email_type == "customer_acknowledgment":
            return self._send_customer_acknowledgment(input_data)
        elif email_type == "forwarder_notification":
            return self._send_forwarder_notification(input_data)
        else:
            return {"error": f"Unknown email type: {email_type}"}

    def _send_customer_acknowledgment(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send acknowledgment email to customer for confirmation."""
        try:
            customer_email = input_data.get("customer_email", "")
            confirmation_data = input_data.get("confirmation_data", {})
            thread_id = input_data.get("thread_id", "")
            
            if not customer_email:
                return {"error": "No customer email provided"}
            
            # Generate acknowledgment email content
            email_content = self._generate_customer_acknowledgment(confirmation_data, input_data)
            
            # Safety check - only send to allowed domains in test mode
            if self.email_config.get("test_mode", True):
                if not self._is_safe_email_domain(customer_email):
                    return {
                        "success": False,
                        "email_sent": False,
                        "reason": "test_mode_active",
                        "message": f"Email not sent - test mode active. Would send to: {customer_email}",
                        "email_content": email_content,
                        "thread_id": thread_id
                    }
            
            # Send email (if enabled and safe)
            if self.email_config.get("enable_email_sending", False) and not self.email_config.get("test_mode", True):
                result = self._send_email(
                    to_email=customer_email,
                    subject=email_content["subject"],
                    body=email_content["body"],
                    thread_id=thread_id
                )
                result["email_type"] = "customer_acknowledgment"
                return result
            else:
                return {
                    "success": True,
                    "email_sent": False,
                    "reason": "email_sending_disabled",
                    "message": f"Email sending disabled. Would send acknowledgment to: {customer_email}",
                    "email_content": email_content,
                    "thread_id": thread_id
                }
                
        except Exception as e:
            self.logger.error(f"Customer acknowledgment email failed: {e}")
            return {"error": f"Customer acknowledgment email failed: {str(e)}"}

    def _send_forwarder_notification(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send notification email to assigned forwarder."""
        try:
            forwarder_assignment = input_data.get("forwarder_assignment", {})
            thread_id = input_data.get("thread_id", "")
            
            if not forwarder_assignment:
                return {"error": "No forwarder assignment data provided"}
            
            # Extract forwarder email from assignment data
            forwarder_email = self._get_forwarder_email(forwarder_assignment)
            
            if not forwarder_email:
                return {"error": "No forwarder email found in assignment data"}
            
            # Generate forwarder notification content
            email_content = self._generate_forwarder_notification(forwarder_assignment, input_data)
            
            # Safety check
            if self.email_config.get("test_mode", True):
                if not self._is_safe_email_domain(forwarder_email):
                    return {
                        "success": False,
                        "email_sent": False,
                        "reason": "test_mode_active",
                        "message": f"Email not sent - test mode active. Would send to: {forwarder_email}",
                        "email_content": email_content,
                        "thread_id": thread_id
                    }
            
            # Send email (if enabled and safe)
            if self.email_config.get("enable_email_sending", False) and not self.email_config.get("test_mode", True):
                result = self._send_email(
                    to_email=forwarder_email,
                    subject=email_content["subject"],
                    body=email_content["body"],
                    thread_id=thread_id
                )
                result["email_type"] = "forwarder_notification"
                return result
            else:
                return {
                    "success": True,
                    "email_sent": False,
                    "reason": "email_sending_disabled",
                    "message": f"Email sending disabled. Would send notification to: {forwarder_email}",
                    "email_content": email_content,
                    "thread_id": thread_id
                }
                
        except Exception as e:
            self.logger.error(f"Forwarder notification email failed: {e}")
            return {"error": f"Forwarder notification email failed: {str(e)}"}

    def _generate_customer_acknowledgment(self, confirmation_data: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate customer acknowledgment email content."""
        confirmation_type = confirmation_data.get("confirmation_type", "booking_confirmation")
        confirmation_details = confirmation_data.get("confirmation_details", "your request")
        
        # Get confirmation message from config
        confirmation_messages = self.email_config.get("confirmation_messages", {})
        message_template = confirmation_messages.get(confirmation_type, confirmation_messages.get("no_confirmation", "your message regarding {details}"))
        confirmation_message = message_template.format(details=confirmation_details)
        
        # Get email template from config
        templates = self.email_config.get("email_templates", {}).get("customer_acknowledgment", {})
        subject_template = templates.get("subject_template", "Thank you for your confirmation")
        body_template = templates.get("body_template", "Dear Customer,\n\nThank you for your {confirmation_message}. I'm pleased to confirm that I've received your confirmation and will proceed accordingly.\n\nI will reach out to you shortly with the rates and further details for your shipment.\n\nIf you have any questions in the meantime, please don't hesitate to contact us.\n\nBest regards,\nLogistics AI Assistant")
        
        # Format templates - simplified without technical details
        subject = subject_template
        
        body = body_template.format(
            confirmation_message=confirmation_message
        )
        
        return {"subject": subject, "body": body}

    def _generate_forwarder_notification(self, forwarder_assignment: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate forwarder notification email content."""
        assigned_forwarder = forwarder_assignment.get("assigned_forwarder", "Unknown Forwarder")
        origin_country = forwarder_assignment.get("origin_country", "Unknown")
        destination_country = forwarder_assignment.get("destination_country", "Unknown")
        
        # Get email template from config
        templates = self.email_config.get("email_templates", {}).get("forwarder_notification", {})
        subject_template = templates.get("subject_template", "New Shipment Assignment - {origin_country} to {destination_country}")
        body_template = templates.get("body_template", "Dear {forwarder_name} Team,\n\nA new shipment has been assigned to your company for handling.\n\n**Shipment Details:**\n- Origin Country: {origin_country}\n- Destination Country: {destination_country}\n- Customer Email: {customer_email}\n- Shipment Type: {shipment_type}\n- Container Type: {container_type}\n\nPlease review the shipment details and contact the customer to proceed with the booking process. Rate requested within 24 hours.\n\nIf you have any questions or need additional information, please contact our support team.\n\nBest regards,\nLogistics AI System")
        
        # Format templates - simplified without technical details
        subject = subject_template.format(
            origin_country=origin_country,
            destination_country=destination_country
        )
        
        body = body_template.format(
            forwarder_name=assigned_forwarder,
            origin_country=origin_country,
            destination_country=destination_country,
            customer_email=input_data.get('customer_email', 'N/A'),
            shipment_type=input_data.get('extraction_data', {}).get('shipment_type', 'N/A'),
            container_type=input_data.get('extraction_data', {}).get('container_type', 'N/A')
        )
        
        return {"subject": subject, "body": body}

    def _get_forwarder_email(self, forwarder_assignment: Dict[str, Any]) -> Optional[str]:
        """Extract forwarder email from assignment data."""
        # This would typically come from the CSV file
        # For now, return a dummy email based on forwarder name
        assigned_forwarder = forwarder_assignment.get("assigned_forwarder", "")
        
        if not assigned_forwarder:
            return None
        
        # Create dummy email based on forwarder name
        forwarder_name_clean = assigned_forwarder.lower().replace(" ", "").replace("&", "and")
        return f"{forwarder_name_clean}@dummycompany.com"

    def _is_safe_email_domain(self, email: str) -> bool:
        """Check if email domain is in allowed list for safety."""
        if not email or "@" not in email:
            return False
        
        domain = email.split("@")[1].lower()
        allowed_domains = self.email_config.get("allowed_domains", [])
        
        return domain in allowed_domains

    def _send_email(self, to_email: str, subject: str, body: str, thread_id: str) -> Dict[str, Any]:
        """Actually send the email via SMTP."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get("sender_email", "")
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server (this will fail with dummy credentials)
            smtp_server = self.email_config.get("smtp_server", "")
            smtp_port = self.email_config.get("smtp_port", 587)
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            
            # Login (this will fail with dummy credentials)
            sender_email = self.email_config.get("sender_email", "")
            sender_password = self.email_config.get("sender_password", "")
            server.login(sender_email, sender_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(sender_email, to_email, text)
            server.quit()
            
            self.logger.info(f"Email sent successfully to {to_email} for thread {thread_id}")
            
            return {
                "success": True,
                "email_sent": True,
                "to_email": to_email,
                "subject": subject,
                "thread_id": thread_id,
                "message": "Email sent successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Email sending failed: {e}")
            return {
                "success": False,
                "email_sent": False,
                "error": str(e),
                "to_email": to_email,
                "subject": subject,
                "thread_id": thread_id,
                "message": f"Email sending failed: {str(e)}"
            }

    def enable_email_sending(self, enable: bool = True):
        """Enable or disable email sending (safety control)."""
        self.email_config["enable_email_sending"] = enable
        self.logger.info(f"Email sending {'enabled' if enable else 'disabled'}")

    def set_test_mode(self, test_mode: bool = True):
        """Set test mode (safety control)."""
        self.email_config["test_mode"] = test_mode
        self.logger.info(f"Test mode {'enabled' if test_mode else 'disabled'}")

# =====================================================
#                 🔁 Test Harness
# =====================================================
def test_email_sender_agent():
    """Test email sender agent with various scenarios"""
    print("=== Testing Email Sender Agent ===")
    
    agent = EmailSenderAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}")

    # Test customer acknowledgment
    print("\n--- Testing Customer Acknowledgment ---")
    customer_result = agent.process({
        "email_type": "customer_acknowledgment",
        "customer_email": "customer@dummycompany.com",
        "confirmation_data": {
            "is_confirmation": True,
            "confirmation_type": "booking_confirmation",
            "confirmation_details": "2x40ft containers from Shanghai to Long Beach"
        },
        "thread_id": "thread-1234",
        "timestamp": "2024-01-15 10:30:00"
    })
    print(json.dumps(customer_result, indent=2))

    # Test forwarder notification
    print("\n--- Testing Forwarder Notification ---")
    forwarder_result = agent.process({
        "email_type": "forwarder_notification",
        "forwarder_assignment": {
            "assigned_forwarder": "Global Logistics Partners",
            "origin_country": "China",
            "destination_country": "USA",
            "assignment_method": "both_countries"
        },
        "thread_id": "thread-1234",
        "customer_email": "customer@dummycompany.com",
        "extraction_data": {
            "shipment_type": "FCL",
            "container_type": "40ft"
        },
        "rate_data": {
            "rate": 2500,
            "source": "market_analytics"
        }
    })
    print(json.dumps(forwarder_result, indent=2))

    # Test unsafe email domain
    print("\n--- Testing Unsafe Email Domain ---")
    unsafe_result = agent.process({
        "email_type": "customer_acknowledgment",
        "customer_email": "customer@realcompany.com",  # Not in allowed domains
        "confirmation_data": {
            "is_confirmation": True,
            "confirmation_type": "quote_acceptance",
            "confirmation_details": "rate acceptance"
        },
        "thread_id": "thread-1234"
    })
    print(json.dumps(unsafe_result, indent=2))

if __name__ == "__main__":
    test_email_sender_agent() 