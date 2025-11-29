"""Sales Notification Agent: Generates sales team notifications and deal summaries using LLM."""

import json
import sys
import os
from typing import Dict, Any, List

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.base_agent import BaseAgent
except ImportError:
    try:
        from base_agent import BaseAgent
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from agents.base_agent import BaseAgent

class SalesNotificationAgent(BaseAgent):
    """Agent for generating sales team notifications and deal summaries."""

    def __init__(self):
        super().__init__("sales_notification_agent")
        
        # Notification types
        self.notification_types = [
            "rates_received",
            "customer_rate_inquiry",
            "customer_booking_request",
            "escalation",
            "deal_update",
            "deal_closure"
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate sales team notification based on case details.
        
        Expected input:
        - notification_type: Type of notification
        - customer_details: Customer information
        - shipment_details: Shipment information
        - forwarder_rates: Forwarder rates (if available)
        - conversation_state: Current conversation state
        - thread_id: Thread identifier
        - urgency: Urgency level
        """
        notification_type = input_data.get("notification_type", "")
        customer_details = input_data.get("customer_details", {})
        shipment_details = input_data.get("shipment_details", {})
        forwarder_rates = input_data.get("forwarder_rates", [])
        forwarder_details = input_data.get("forwarder_details", {})
        forwarder_email_content = input_data.get("forwarder_email_content", "")
        timeline_information = input_data.get("timeline_information", {})
        conversation_state = input_data.get("conversation_state", "")
        thread_id = input_data.get("thread_id", "")
        urgency = input_data.get("urgency", "medium")

        if not notification_type:
            return {"error": "No notification type provided"}

        if not self.client:
            return {"error": "LLM client not initialized"}

        return self._generate_sales_notification(notification_type, customer_details, shipment_details, forwarder_rates, forwarder_details, forwarder_email_content, timeline_information, conversation_state, thread_id, urgency)

    def _generate_sales_notification(self, notification_type: str, customer_details: Dict[str, Any], shipment_details: Dict[str, Any], forwarder_rates: List[Dict[str, Any]], forwarder_details: Dict[str, Any], forwarder_email_content: str, timeline_information: Dict[str, Any], conversation_state: str, thread_id: str, urgency: str) -> Dict[str, Any]:
        """Generate sales notification using LLM function calling."""
        try:
            function_schema = {
                "name": "generate_sales_notification",
                "description": "Generate sales team notification with deal summary and recommendations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "subject": {
                            "type": "string",
                            "description": "Email subject line for sales notification"
                        },
                        "body": {
                            "type": "string",
                            "description": "Email body content for sales notification"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Priority level for the notification"
                        },
                        "deal_value_estimate": {
                            "type": "number",
                            "description": "Estimated deal value in USD"
                        },
                        "next_action_required": {
                            "type": "string",
                            "description": "Specific action required from sales team"
                        },
                        "customer_contact_info": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "email": {"type": "string"},
                                "company": {"type": "string"},
                                "phone": {"type": "string"}
                            },
                            "description": "Customer contact information"
                        },
                        "key_highlights": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key points to highlight for sales team"
                        },
                        "risk_factors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Risk factors or concerns to consider"
                        },
                        "recommendations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Recommendations for sales team"
                        }
                    },
                    "required": ["subject", "body", "priority", "deal_value_estimate", "next_action_required", "customer_contact_info", "key_highlights", "risk_factors", "recommendations"]
                }
            }

            # Format data for analysis
            customer_summary = self._format_customer_summary(customer_details)
            shipment_summary = self._format_shipment_summary(shipment_details)
            rates_summary = self._format_rates_summary(forwarder_rates)
            forwarder_summary = self._format_forwarder_summary(forwarder_details)
            timeline_summary = self._format_timeline_summary(timeline_information)

            prompt = f"""
You are an expert sales coordinator for logistics operations. Generate a comprehensive sales team notification.

NOTIFICATION TYPE: {notification_type}
CONVERSATION STATE: {conversation_state}
URGENCY: {urgency}
THREAD ID: {thread_id}

CUSTOMER DETAILS:
{customer_summary}

SHIPMENT DETAILS:
{shipment_summary}

FORWARDER DETAILS:
{forwarder_summary}

FORWARDER RATES:
{rates_summary}

TIMELINE INFORMATION:
{timeline_summary}

NOTIFICATION TYPES:
1. rates_received: Forwarder has sent rates, ready for customer presentation
2. customer_rate_inquiry: Customer is asking about rates or status
3. customer_booking_request: Customer wants to proceed with booking
4. escalation: Complex case or customer frustration
5. deal_update: General update on deal progress
6. deal_closure: Deal has been closed or finalized

PRIORITY LEVELS:
- urgent: Customer frustration, high-value deals, immediate action needed
- high: Rate inquiries, booking requests, forwarder responses
- medium: Deal updates, general inquiries
- low: Follow-ups, status updates

REQUIRED EMAIL STRUCTURE:
1. **THREAD ID** - Include at the top: Thread ID: [thread_id]

2. **CUSTOMER INFORMATION** - Include ONLY validated customer contact details:
   - Customer Name (if available)
   - Email Address (if available)
   - Phone Number (if available)
   - Company Name (if available)
   - Only include fields that have actual values, skip if unknown

3. **SHIPMENT DETAILS** - Include ONLY validated shipment specifications:
   - Origin (if validated)
   - Destination (if validated)
   - Container Type (if validated)
   - Container Count (if validated)
   - Commodity (if validated)
   - Weight (if validated)
   - Incoterm (if validated)
   - Only include fields that are confirmed/validated

4. **FORWARDER RATE QUOTE** - Include:
   - Forwarder Name and Contact Information (if available)
   - Rate per container (clearly stated)
   - Number of containers
   - Total shipment cost calculation (rate × containers)
   - Transit time
   - Valid until date
   - DO NOT include "Additional notes" or unvalidated information

5. **ACTION REQUIRED** - Provide SPECIFIC, ACTIONABLE steps:
   - Step 1: Contact customer at [email] by [deadline]
   - Step 2: Present rates with margin calculation (if applicable)
   - Step 3: Confirm booking if accepted
   - Step 4: Coordinate with forwarder at [forwarder_email]
   - Include specific deadlines and contact information

6. **URGENCY & TIMELINE** - Include:
   - Customer requested date (if available and validated)
   - Days until deadline (calculate if possible)
   - Urgency level justification

7. **KEY HIGHLIGHTS** - Important points for sales team

8. **RISK FACTORS** - Any concerns or considerations

9. **RECOMMENDATIONS** - Suggested approach for handling

IMPORTANT INSTRUCTIONS:
- Include Thread ID at the top of the email body
- DO NOT include the forwarder email content in the body - it will be appended separately only if needed
- Include ONLY validated customer information - skip fields marked as unknown or unvalidated
- Include ONLY validated shipment details - do not include unconfirmed information
- DO NOT include "Additional notes" section
- Include ALL forwarder contact information (name, email, company) if available
- Make action items SPECIFIC with actual contact details and deadlines
- Calculate total shipment cost clearly (rate × number of containers)
- Be professional, clear, and actionable

Make the notification comprehensive and provide all necessary information for the sales team to take immediate action.
"""

            # Use OpenAI client for function calling
            client = self.get_openai_client()
            if not client:
                return {"error": "OpenAI client not available for function calling"}
            
            response = client.chat.completions.create(
                model=self.config.get("model_name"),
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
            result["notification_method"] = "llm_function_call"
            result["thread_id"] = thread_id
            result["notification_type"] = notification_type
            result["conversation_state"] = conversation_state
            
            # Ensure thread ID is included in the body if not already present
            if thread_id and result.get("body"):
                # Check if thread ID is already in the body
                if f"Thread ID: {thread_id}" not in result.get("body", "") and f"thread_id: {thread_id}" not in result.get("body", "").lower():
                    # Add thread ID at the beginning if not present
                    result["body"] = f"Thread ID: {thread_id}\n\n{result['body']}"
            
            # Remove "Additional notes" section if present
            if result.get("body"):
                body = result["body"]
                # Remove lines containing "Additional notes" or similar
                lines = body.split('\n')
                filtered_lines = []
                skip_next = False
                for i, line in enumerate(lines):
                    line_lower = line.lower().strip()
                    # Skip lines with "additional notes" or "additional information"
                    if "additional notes" in line_lower or "additional information" in line_lower:
                        skip_next = True
                        continue
                    # Skip empty lines after "additional notes" section
                    if skip_next and (not line.strip() or line.strip().startswith('-')):
                        continue
                    if skip_next and line.strip() and not line.strip().startswith('-'):
                        skip_next = False
                    if not skip_next:
                        filtered_lines.append(line)
                result["body"] = '\n'.join(filtered_lines)
            
            # Only append forwarder email content if it's NOT already summarized in the body
            # Since we're summarizing the forwarder email in the body, we don't need to append it
            # The forwarder email details are already included in the FORWARDER RATE QUOTE section
            
            # Validate and correct result if needed
            if result.get("priority") not in ["low", "medium", "high", "urgent"]:
                result["priority"] = "medium"

            # Ensure deal value is reasonable
            deal_value = result.get("deal_value_estimate", 0)
            if deal_value < 0:
                result["deal_value_estimate"] = 0

            self.logger.info(f"Sales notification generated successfully: {notification_type} (priority: {result['priority']})")
            
            return result

        except Exception as e:
            self.logger.error(f"Sales notification generation failed: {e}")
            return {"error": f"Sales notification generation failed: {str(e)}"}

    def _format_customer_summary(self, customer_details: Dict[str, Any]) -> str:
        """Format customer details for analysis."""
        if not customer_details:
            return "No customer details available"
        
        summary_parts = []
        # Prioritize important fields
        priority_fields = ['name', 'email', 'phone', 'company', 'whatsapp']
        for field in priority_fields:
            if customer_details.get(field):
                summary_parts.append(f"- {field.title()}: {customer_details.get(field)}")
        
        # Add any other fields
        for key, value in customer_details.items():
            if key not in priority_fields and value and str(value).strip():
                summary_parts.append(f"- {key}: {value}")
        
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "No customer details available"

    def _format_shipment_summary(self, shipment_details: Dict[str, Any]) -> str:
        """Format shipment details for analysis."""
        if not shipment_details:
            return "No shipment details available"
        
        summary_parts = []
        for key, value in shipment_details.items():
            if value and str(value).strip():
                summary_parts.append(f"- {key}: {value}")
        
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "No shipment details available"

    def _format_rates_summary(self, forwarder_rates: List[Dict[str, Any]]) -> str:
        """Format forwarder rates for analysis."""
        if not forwarder_rates:
            return "No forwarder rates available"
        
        summary_parts = []
        for i, rate in enumerate(forwarder_rates, 1):
            rate_details = []
            
            # Format rate information in a readable way
            if rate.get('rate'):
                rate_details.append(f"Rate: ${rate.get('rate'):,.2f} USD" if isinstance(rate.get('rate'), (int, float)) else f"Rate: {rate.get('rate')} USD")
            elif rate.get('rates_with_dthc'):
                rate_value = rate.get('rates_with_dthc')
                rate_details.append(f"Total Rate: ${rate_value:,.2f} USD" if isinstance(rate_value, (int, float)) else f"Total Rate: {rate_value} USD")
            elif rate.get('rates_with_othc'):
                rate_value = rate.get('rates_with_othc')
                rate_details.append(f"Rate with OTHC: ${rate_value:,.2f} USD" if isinstance(rate_value, (int, float)) else f"Rate with OTHC: {rate_value} USD")
            elif rate.get('rates_without_thc'):
                rate_value = rate.get('rates_without_thc')
                rate_details.append(f"Freight Rate: ${rate_value:,.2f} USD" if isinstance(rate_value, (int, float)) else f"Freight Rate: {rate_value} USD")
            
            # Add other important fields
            if rate.get('transit_time'):
                rate_details.append(f"Transit Time: {rate.get('transit_time')} days")
            if rate.get('valid_until'):
                rate_details.append(f"Valid Until: {rate.get('valid_until')}")
            if rate.get('sailing_date'):
                rate_details.append(f"Sailing Date: {rate.get('sailing_date')}")
            if rate.get('origin_port'):
                rate_details.append(f"Origin: {rate.get('origin_port')}")
            if rate.get('destination_port'):
                rate_details.append(f"Destination: {rate.get('destination_port')}")
            if rate.get('container_type'):
                rate_details.append(f"Container: {rate.get('container_type')}")
            
            if rate_details:
                summary_parts.append(f"Forwarder Rate Quote {i}:\n" + "\n".join(f"  - {detail}" for detail in rate_details))
        
        if summary_parts:
            return "\n\n".join(summary_parts)
        else:
            return "No forwarder rates available"
    
    def _format_forwarder_summary(self, forwarder_details: Dict[str, Any]) -> str:
        """Format forwarder details for analysis."""
        if not forwarder_details:
            return "No forwarder details available"
        
        summary_parts = []
        if forwarder_details.get('name'):
            summary_parts.append(f"Name: {forwarder_details.get('name')}")
        if forwarder_details.get('email'):
            summary_parts.append(f"Email: {forwarder_details.get('email')}")
        if forwarder_details.get('company'):
            summary_parts.append(f"Company: {forwarder_details.get('company')}")
        if forwarder_details.get('phone'):
            summary_parts.append(f"Phone: {forwarder_details.get('phone')}")
        
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "No forwarder details available"
    
    def _format_timeline_summary(self, timeline_information: Dict[str, Any]) -> str:
        """Format timeline information for analysis."""
        if not timeline_information:
            return "No timeline information available"
        
        summary_parts = []
        if timeline_information.get('requested_dates'):
            summary_parts.append(f"Requested Date: {timeline_information.get('requested_dates')}")
        if timeline_information.get('deadline'):
            summary_parts.append(f"Deadline: {timeline_information.get('deadline')}")
        if timeline_information.get('urgency'):
            summary_parts.append(f"Urgency: {timeline_information.get('urgency')}")
        if timeline_information.get('transit_time'):
            summary_parts.append(f"Transit Time: {timeline_information.get('transit_time')}")
        
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "No timeline information available"

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_sales_notification_agent():
    print("=== Testing Sales Notification Agent ===")
    agent = SalesNotificationAgent()
    
    if not agent.load_context():
        print("✗ Failed to load context")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "Rates Received",
            "notification_type": "rates_received",
            "customer_details": {
                "name": "John Smith",
                "email": "john@abc.com",
                "company": "ABC Electronics"
            },
            "shipment_details": {
                "origin": "Shanghai",
                "destination": "Long Beach",
                "container_type": "40GP",
                "quantity": 2
            },
            "forwarder_rates": [
                {
                    "forwarder": "DHL Global Forwarding",
                    "rate": 2500,
                    "currency": "USD",
                    "valid_until": "2024-01-15"
                }
            ],
            "conversation_state": "forwarder_response",
            "urgency": "high"
        },
        {
            "name": "Customer Rate Inquiry",
            "notification_type": "customer_rate_inquiry",
            "customer_details": {
                "name": "Sarah Johnson",
                "email": "sarah@xyz.com",
                "company": "XYZ Trading"
            },
            "shipment_details": {
                "origin": "Hamburg",
                "destination": "New York",
                "container_type": "20GP",
                "quantity": 1
            },
            "forwarder_rates": [],
            "conversation_state": "rate_inquiry",
            "urgency": "medium"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        result = agent.run({
            "notification_type": test_case["notification_type"],
            "customer_details": test_case["customer_details"],
            "shipment_details": test_case["shipment_details"],
            "forwarder_rates": test_case["forwarder_rates"],
            "conversation_state": test_case["conversation_state"],
            "thread_id": "test-thread-1",
            "urgency": test_case["urgency"]
        })
        
        if result.get("status") == "success":
            subject = result.get("subject")
            priority = result.get("priority")
            deal_value = result.get("deal_value_estimate")
            next_action = result.get("next_action_required")
            
            print(f"✓ Subject: {subject}")
            print(f"✓ Priority: {priority}")
            print(f"✓ Deal Value: ${deal_value}")
            print(f"✓ Next Action: {next_action}")
            print(f"✓ Body Length: {len(result.get('body', ''))} characters")
        else:
            print(f"✗ Test failed: {result.get('error')}")

if __name__ == "__main__":
    test_sales_notification_agent() 