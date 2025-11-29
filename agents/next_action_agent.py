"""Next Action Agent: Determines next actions based on conversation state and extracted data using LLM."""

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

class NextActionAgent(BaseAgent):
    """Agent for determining next actions based on conversation state and data analysis."""

    def __init__(self):
        super().__init__("next_action_agent")
        
        # Available actions
        self.available_actions = [
            "send_clarification_request",
            "send_confirmation_request", 
            "send_confirmation_acknowledgment",
            "booking_details_confirmed_assign_forwarders",
            "send_forwarder_rate_request",
            "send_rate_recommendation",
            "send_rate_inquiry_response",
            "send_booking_confirmation",
            "send_forwarder_response_to_customer",
            "send_follow_up",
            "send_sales_notification",
            "escalate_to_sales",
            "escalate_confusing_email",
            "wait_for_forwarder_response",
            "wait_for_customer_response",
            "no_action_required"
        ]

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine next action based on conversation state, email classification, and extracted data.
        
        Expected input:
        - conversation_state: Current conversation state
        - email_classification: Email type classification (logistics_request, forwarder_response, etc.)
        - extracted_data: Extracted shipment data
        - confidence_score: Confidence in extraction/analysis
        - missing_fields: List of missing fields
        - thread_id: Thread identifier
        - latest_sender: Who sent the latest email
        - thread_context: Thread analysis context (optional)
        """
        conversation_state = input_data.get("conversation_state", "")
        email_classification = input_data.get("email_classification", {})
        extracted_data = input_data.get("extracted_data", {})
        confidence_score = input_data.get("confidence_score", 0.0)
        validation_results = input_data.get("validation_results", {})
        enriched_data = input_data.get("enriched_data", {})
        thread_id = input_data.get("thread_id", "")

        if not conversation_state:
            return {"error": "No conversation state provided"}

        if not self.client:
            return {"error": "LLM client not initialized"}

        return self._determine_next_action(
            conversation_state, 
            email_classification, 
            extracted_data, 
            confidence_score, 
            validation_results,
            enriched_data,
            thread_id
        )

    def _determine_next_action(self, conversation_state: str, email_classification: Dict[str, Any], extracted_data: Dict[str, Any], confidence_score: float, validation_results: Dict[str, Any], enriched_data: Dict[str, Any], thread_id: str) -> Dict[str, Any]:
        """Determine next action using LLM function calling."""
        try:
            function_schema = {
                "name": "determine_next_action",
                "description": "Determine the next action based on conversation state and data analysis",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "next_action": {
                            "type": "string",
                            "enum": self.available_actions,
                            "description": "Next action to take"
                        },
                        "action_priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Priority level for the action"
                        },
                        "escalation_needed": {
                            "type": "boolean",
                            "description": "Whether this case needs human escalation"
                        },
                        "sales_handoff_needed": {
                            "type": "boolean",
                            "description": "Whether sales team should be notified"
                        },
                        "response_type": {
                            "type": "string",
                            "enum": ["clarification", "confirmation", "status_update", "sales_notification", "escalation", "none"],
                            "description": "Type of response to generate"
                        },
                        "wait_time": {
                            "type": "integer",
                            "description": "Expected wait time in hours before next action",
                            "minimum": 0
                        },
                        "confidence_threshold": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence threshold for this action"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Detailed reasoning for the action decision"
                        },
                        "risk_factors": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Risk factors that influenced the decision"
                        }
                    },
                    "required": ["next_action", "action_priority", "escalation_needed", "sales_handoff_needed", "response_type", "wait_time", "confidence_threshold", "reasoning", "risk_factors"]
                }
            }

            # Format extracted data for analysis
            missing_fields = validation_results.get("overall_validation", {}).get("missing_fields", [])
            
            # CRITICAL: Check if ports are countries (not specific ports) - this is also a missing field
            # This check MUST happen before applying FCL/LCL rules
            # First check extracted_data for origin_country/destination_country fields
            shipment_details = extracted_data.get("shipment_details", {})
            origin = shipment_details.get("origin", "").strip()
            destination = shipment_details.get("destination", "").strip()
            origin_country = shipment_details.get("origin_country", "").strip()
            destination_country = shipment_details.get("destination_country", "").strip()
            
            # Only flag as missing if origin is EMPTY but origin_country is set (country-only input)
            # If origin is set (even if origin_country is also set), it's a valid port with country info
            if not origin and origin_country:
                if "Origin (specific port required)" not in missing_fields:
                    missing_fields.append("Origin (specific port required)")
                    self.logger.warning(f"⚠️ Origin is a country ({origin_country}), not a specific port. Adding to missing fields.")
            elif not origin:
                # Origin is empty and no country set - just missing origin
                if "Origin" not in missing_fields:
                    missing_fields.append("Origin")
            
            # Only flag as missing if destination is EMPTY but destination_country is set (country-only input)
            # If destination is set (even if destination_country is also set), it's a valid port with country info
            if not destination and destination_country:
                if "Destination (specific port required)" not in missing_fields:
                    missing_fields.append("Destination (specific port required)")
                    self.logger.warning(f"⚠️ Destination is a country ({destination_country}), not a specific port. Adding to missing fields.")
            elif not destination:
                # Destination is empty and no country set - just missing destination
                if "Destination" not in missing_fields:
                    missing_fields.append("Destination")
            
            # Fallback: Also check port_lookup_result if country fields are not extracted
            port_lookup_result = enriched_data.get("port_lookup", {})
            if port_lookup_result and not origin_country and not destination_country:
                # Check origin - if it's a country (not a specific port), add to missing fields
                origin_result = port_lookup_result.get("origin", {})
                if origin_result and origin_result.get("is_country", False):
                    if "Origin (specific port required)" not in missing_fields:
                        missing_fields.append("Origin (specific port required)")
                        self.logger.warning(f"⚠️ Origin is a country ({origin_result.get('country', 'unknown')}), not a specific port. Adding to missing fields.")
                
                # Check destination - if it's a country (not a specific port), add to missing fields
                destination_result = port_lookup_result.get("destination", {})
                if destination_result and destination_result.get("is_country", False):
                    if "Destination (specific port required)" not in missing_fields:
                        missing_fields.append("Destination (specific port required)")
                        self.logger.warning(f"⚠️ Destination is a country ({destination_result.get('country', 'unknown')}), not a specific port. Adding to missing fields.")
            
            # Apply FCL/LCL business rules to missing fields
            missing_fields = self._apply_fcl_lcl_rules_to_missing_fields(missing_fields, extracted_data)
            
            # Check if customer has confirmed the details
            customer_confirmed = self._check_customer_confirmation(conversation_state, email_classification)
            
            # CRITICAL: Even if customer confirmed, if mandatory fields are missing (including country-only ports), require clarification
            if customer_confirmed and missing_fields and len(missing_fields) > 0:
                self.logger.warning(f"⚠️ Customer confirmed but mandatory fields missing: {missing_fields}. Requiring clarification first - customer confirmation cannot override missing mandatory information.")
                # Force clarification - customer confirmation is ignored if mandatory fields are missing
            
            data_summary = self._format_data_summary(extracted_data, missing_fields)

            prompt = f"""
You are an expert logistics workflow coordinator. Determine the next action based on conversation state, email classification, and thread context.

CONVERSATION STATE: {conversation_state}
EMAIL CLASSIFICATION: {email_classification.get('email_type', 'unknown')} (confidence: {email_classification.get('confidence', 0.0):.2f})
CONFIDENCE SCORE: {confidence_score:.2f}
CUSTOMER CONFIRMED: {customer_confirmed}

VALIDATION RESULTS:
{json.dumps(validation_results, indent=2)}

ENRICHED DATA:
{json.dumps(enriched_data, indent=2)}

EXTRACTED DATA SUMMARY:
{data_summary}

MISSING FIELDS: {missing_fields}

**CRITICAL DECISION RULE - READ THIS FIRST (MANDATORY - NO EXCEPTIONS):**
- **IF missing_fields list contains ANY items (is NOT empty)**: You MUST choose send_clarification_request
- **ONLY if missing_fields list is completely empty ([])**: You may choose send_confirmation_request
- **NEVER choose send_confirmation_request if there are ANY missing mandatory fields**
- **ALL mandatory fields MUST be populated before confirmation can be triggered**
- **SPECIFIC PORTS REQUIRED**: Origin and Destination must be SPECIFIC PORTS (e.g., "Los Angeles", "Shanghai"), NOT countries (e.g., "USA", "China")
- **If country names are provided instead of ports**: This counts as a missing field ("Origin (specific port required)" or "Destination (specific port required)")
- **This rule takes absolute priority over ALL other considerations, including customer confirmation**
- **Customer confirmation is IGNORED if mandatory fields are missing - clarification is required first**

AVAILABLE ACTIONS:
1. send_clarification_request: Ask customer for missing information
2. send_confirmation_request: Present extracted data for customer confirmation
3. assign_forwarder_and_send_rate_request: Assign forwarder and request rates
4. collate_rates_and_send_to_sales: Collate forwarder rates and send to sales
5. notify_sales_team: Send case to sales team for handling
6. send_status_update: Provide status update to customer
7. escalate_to_human: Escalate complex case to human agent
8. route_to_appropriate_department: Route non-logistics emails
9. wait_for_forwarder_response: Wait for forwarder to respond
10. wait_for_customer_response: Wait for customer to respond
11. send_forwarder_acknowledgment: Send acknowledgment to forwarder
12. escalate_confusing_email: Escalate confusing/ambiguous email to human

INTELLIGENT ANALYSIS INSTRUCTIONS:

**PRIORITY DECISION RULE (STRICT ENFORCEMENT):**
- **FIRST AND MANDATORY**: Check the missing_fields list
  - **IF missing_fields has ANY items**: You MUST choose send_clarification_request (NO EXCEPTIONS)
  - **IF missing_fields is empty ([])**: Then proceed to check if confirmation is appropriate
- **SECOND**: Only if missing_fields is empty, analyze validation results and data completeness
- **THIRD**: Only if ALL mandatory fields are present AND missing_fields is empty, consider send_confirmation_request

**DATA QUALITY ANALYSIS:**
- Analyze the validation results to understand data completeness and quality
- Check if port codes are valid or if country names were provided instead
- Evaluate if the enriched data contains specific port information or just country names
- Assess the confidence levels across all validation fields
- **CRITICAL**: Determine shipment type (FCL vs LCL) and apply appropriate field requirements

**SMART DECISION MAKING:**

**CLARIFICATION FLOW LOGIC:**
- **Incomplete Data** → send_clarification_request (ask for missing info)
- **Missing Critical Fields** → send_clarification_request (specific questions)
- **Unclear Requirements** → send_clarification_request (clarify details)
- **Null/Empty Values** → send_clarification_request (ask for missing info)
- **No Origin/Destination** → send_clarification_request (critical for routing)

**CONFIRMATION FLOW LOGIC (STRICT REQUIREMENTS):**
- **MANDATORY PREREQUISITE**: missing_fields list MUST be empty ([]) before considering confirmation
- **MANDATORY PREREQUISITE**: Origin and Destination MUST be specific ports (not countries)
- **Complete Data + No Customer Confirmation + missing_fields is empty + specific ports provided** → send_confirmation_request (ask customer to confirm)
- **Complete Data + Customer Confirmed + missing_fields is empty + specific ports provided** → booking_details_confirmed_assign_forwarders (proceed to forwarder assignment)
- **Customer Confirmation Received BUT missing_fields has items OR country-only ports** → send_clarification_request (MUST ask for missing information first, including specific ports)
- **If ANY mandatory field is missing OR if ports are countries instead of specific ports** → send_clarification_request (MUST ask for missing information first)
- **NEVER send confirmation if missing_fields contains ANY items, even if customer confirmed**
- **NEVER send confirmation if origin/destination are countries instead of specific ports**
- **Customer confirmation is IGNORED when mandatory fields are missing**

**FCL SHIPMENT LOGIC:**
- **Mandatory Fields**: Port names, shipment type, container type, shipment date
- **Optional Fields**: Weight (not required for FCL)
- **Never Required**: Volume (not needed for FCL - container type provides volume)
- **Container Type Detection**: If container type is provided (20GP, 40GP, 40HC, etc.) → automatically FCL
- **Container Type Required**: If shipment type is FCL but no container type → ask for container type
- **Volume Logic**: For FCL with container type → NEVER ask for volume (container type determines volume)
- **If customer confirms** → proceed with booking even without weight
- **Only ask for weight** if explicitly missing AND customer hasn't confirmed

**LCL SHIPMENT LOGIC:**
- **Mandatory Fields**: Port names, shipment type, weight, volume, shipment date
- **Both weight AND volume** are required for LCL
- **No Container Type**: LCL shipments do NOT have container types
- **No Container Count**: LCL shipments do NOT require number of containers (only weight and volume)
- **Don't proceed** without both weight and volume
- **Ask for missing weight/volume** even if customer confirms
- **NEVER ask for container count** for LCL shipments

**FORWARDER EMAIL HANDLING:**
- **forwarder_response**: When forwarder provides rates/quote → collate_rates_and_send_to_sales
- **forwarder_acknowledgment**: When forwarder acknowledges request → send_forwarder_acknowledgment
- **forwarder_inquiry**: When forwarder asks for more details → send_clarification_request

**CUSTOMER EMAIL HANDLING:**
- **logistics_request**: New customer request → send_confirmation_request or send_clarification_request
- **customer_confirmation**: Customer confirms details → booking_details_confirmed_assign_forwarders
- **customer_clarification**: Customer provides missing info → send_confirmation_request

**GENERAL DECISION RULES:**
- **Container Type Logic**: If container type is provided (20GP, 40GP, 40HC, etc.) → automatically set shipment_type to FCL
- **Container Count Logic**: 
  - **FCL**: Container count (number of containers) IS REQUIRED
  - **LCL**: Container count is NOT REQUIRED (only weight and volume are needed)
  - **NEVER ask for container count for LCL shipments**
- **Port Information**: If specific port names are provided (Shanghai, Los Angeles, etc.) → do NOT ask for port clarification
- **Data Completeness**: Only ask for missing critical fields, not for information already provided
- **CRITICAL**: If missing_fields list contains ANY items → send_clarification_request (MANDATORY - no confirmation allowed)
- **CRITICAL**: If missing_fields list is empty → then consider send_confirmation_request (only if all mandatory fields present)
- **CRITICAL**: Missing fields list takes ABSOLUTE priority - if missing_fields has ANY items, clarification is REQUIRED
- **CRITICAL**: Do NOT ask customers for rate information or transit time - these are what customers request, not provide
- **CRITICAL**: Date format issues in validation should NOT trigger clarification if the date is present (but missing date should be in missing_fields)
- If validation shows invalid port codes but country names are provided → send_clarification_request for specific ports
- If validation shows missing critical fields (ports, date, etc.) → send_clarification_request
- If extracted data has null/empty values for critical fields → send_clarification_request
- If data is complete and valid → send_confirmation_request
- If customer confirms details → booking_details_confirmed_assign_forwarders
- If forwarder provides rates → collate_rates_and_send_to_sales
- If email is confusing/ambiguous → escalate_confusing_email

**CLARIFICATION PRIORITY:**
- **Missing Origin/Destination** → send_clarification_request (critical for routing)
- **Missing Container Type** → send_clarification_request (needed for pricing)
- **Missing Shipment Date** → send_clarification_request (needed for availability)
- **Missing Commodity** → send_clarification_request (needed for documentation)
- **Unclear Requirements** → send_clarification_request (clarify specifics)

**CONTEXT-AWARE REASONING:**
- **PRIORITY 1**: Email classification determines the primary action
- **PRIORITY 2**: Conversation state provides additional context
- **PRIORITY 3**: Data validation results guide specific requirements
- Consider the email classification and confidence level
- Analyze the conversation state and progression
- Evaluate the quality of extracted and enriched data
- Make decisions based on the overall context, not just individual rules

**EMAIL CLASSIFICATION PRIORITY:**
- **forwarder_response** (95% confidence) → MUST route to collate_rates_and_send_to_sales
- **customer_confirmation** → MUST route to booking_details_confirmed_assign_forwarders
- **logistics_request** → Route to send_confirmation_request or send_clarification_request
- **confusing_email** → MUST route to escalate_confusing_email

**PRIORITY ASSESSMENT:**
- High priority: Incomplete data, invalid port codes, missing critical information
- Medium priority: Confirmation requests, standard responses
- Low priority: Follow-ups, status updates

PRIORITY LEVELS:
- urgent: Customer frustration, high-value deals, confusing emails
- high: Rate inquiries, booking requests, forwarder responses
- medium: Clarification responses, confirmation replies
- low: Follow-ups, status updates

SALES HANDOFF RULES:
- Handoff when forwarder rates are received
- Handoff for confusing emails (escalate_confusing_email)
- Handoff when confidence < 0.6
- Handoff for complex cases or escalations
- Do NOT handoff for normal clarification/confirmation flows

Determine the next action, priority, and whether escalation or sales handoff is needed based on ALL available context.
"""

            # Use OpenAI client for function calling
            client = self.get_openai_client()
            if not client:
                raise Exception("OpenAI client not available for function calling")
            
            response = client.chat.completions.create(
                model=self.config.get("model_name"),
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "function",
                    "function": function_schema
                }],
                tool_choice={"type": "function", "function": {"name": function_schema["name"]}},
                temperature=0.1,
                max_tokens=500
            )

            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if not tool_calls:
                raise Exception("No tool_calls in LLM response")

            tool_args = tool_calls[0].function.arguments
            if isinstance(tool_args, str):
                tool_args = json.loads(tool_args)

            result = dict(tool_args)
            result["decision_method"] = "llm_function_call"
            result["thread_id"] = thread_id
            result["conversation_state"] = conversation_state
            result["confidence_score"] = confidence_score
            
            # CRITICAL: Enforce rule - NO confirmation if ANY mandatory fields are missing
            # This applies EVEN IF customer has confirmed - all mandatory fields must be present first
            next_action = result.get("next_action", "")
            if missing_fields and len(missing_fields) > 0:
                # If there are missing fields, override confirmation actions - EVEN if customer confirmed
                if next_action in ["send_confirmation_request", "booking_details_confirmed_assign_forwarders"]:
                    self.logger.warning(f"⚠️ LLM attempted to send confirmation with missing fields: {missing_fields}. Overriding to clarification (customer_confirmed={customer_confirmed}). Customer confirmation cannot override missing mandatory information.")
                    result["next_action"] = "send_clarification_request"
                    result["response_type"] = "clarification"
                    result["reasoning"] = f"OVERRIDE: Mandatory fields missing ({', '.join(missing_fields)}). Confirmation requires ALL mandatory fields, including specific ports (not countries). Customer confirmation cannot override missing mandatory information. " + result.get("reasoning", "")
                    result["decision_method"] = "llm_function_call_with_override"
            
            # Validate and correct result if needed
            if result.get("next_action") not in self.available_actions:
                self.logger.warning(f"Invalid next_action: {result.get('next_action')}, defaulting to escalate_to_human")
                result["next_action"] = "escalate_to_human"
                result["escalation_needed"] = True

            # Ensure confidence threshold is within bounds
            confidence_threshold = result.get("confidence_threshold", 0.7)
            if not (0.0 <= confidence_threshold <= 1.0):
                result["confidence_threshold"] = max(0.0, min(1.0, confidence_threshold))

            # Ensure wait time is reasonable
            wait_time = result.get("wait_time", 24)
            if wait_time < 0:
                result["wait_time"] = 24

            self.logger.info(f"Next action determination successful: {result['next_action']} (priority: {result['action_priority']})")
            
            return result

        except Exception as e:
            self.logger.error(f"Next action determination failed: {e}")
            return {"error": f"Next action determination failed: {str(e)}"}

    def _format_data_summary(self, extracted_data: Dict[str, Any], missing_fields: List[str]) -> str:
        """Format extracted data for analysis."""
        if not extracted_data:
            return "No data extracted"
        
        summary_parts = []
        for key, value in extracted_data.items():
            if value and str(value).strip():
                summary_parts.append(f"- {key}: {value}")
        
        if missing_fields:
            summary_parts.append(f"\nMissing fields: {', '.join(missing_fields)}")
        
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "No valid data extracted"

    def _apply_fcl_lcl_rules_to_missing_fields(self, missing_fields: List[str], extracted_data: Dict[str, Any]) -> List[str]:
        """Apply FCL/LCL business rules to filter missing fields."""
        shipment_details = extracted_data.get("shipment_details", {})
        
        # CRITICAL: Check extracted shipment_type FIRST (directly extracted from email)
        shipment_type = shipment_details.get("shipment_type", "").strip().upper()
        
        # Get container type from nested structure
        container_type = shipment_details.get("container_type", "")
        if isinstance(container_type, dict):
            container_type = container_type.get("standardized_type", "") or container_type.get("standard_type", "")
        container_type = str(container_type).strip() if container_type else ""
        
        # Determine shipment type with priority: extracted shipment_type > special_requirements > container_type
        is_fcl = None
        
        if shipment_type == "LCL":
            # Shipment type was directly extracted as LCL - use it directly
            is_fcl = False
            # CRITICAL: Remove container_count from missing_fields for LCL shipments
            if "container_count" in missing_fields or "Number of containers" in " ".join(missing_fields) or "Quantity (number of containers)" in " ".join(missing_fields):
                missing_fields = [f for f in missing_fields if "container_count" not in f.lower() and "number of containers" not in f.lower() and "quantity (number of containers)" not in f.lower()]
                print(f"✅ NEXT_ACTION: Removed container_count from missing fields (LCL shipment - extracted shipment_type: {shipment_type})")
        elif shipment_type == "FCL":
            # Shipment type was directly extracted as FCL - use it directly
            is_fcl = True
        else:
            # Fallback: Check special_requirements for explicit LCL/FCL mentions
            special_requirements = extracted_data.get("special_requirements", [])
            is_explicitly_lcl = False
            is_explicitly_fcl = False
            
            if special_requirements:
                requirements_text = " ".join([str(req).lower() for req in special_requirements])
                if "lcl" in requirements_text or "less than container" in requirements_text:
                    is_explicitly_lcl = True
                if "fcl" in requirements_text or "full container" in requirements_text:
                    is_explicitly_fcl = True
            
            if is_explicitly_lcl:
                is_fcl = False
                # CRITICAL: Remove container_count from missing_fields for LCL shipments
                if "container_count" in missing_fields or "Number of containers" in " ".join(missing_fields) or "Quantity (number of containers)" in " ".join(missing_fields):
                    missing_fields = [f for f in missing_fields if "container_count" not in f.lower() and "number of containers" not in f.lower() and "quantity (number of containers)" not in f.lower()]
                    print(f"✅ NEXT_ACTION: Removed container_count from missing fields (LCL shipment with special_requirements: {special_requirements})")
            elif is_explicitly_fcl:
                is_fcl = True
            elif container_type and container_type.upper() in ["20GP", "40GP", "40HC", "20RF", "40RF", "20DC", "40DC", "20FT", "40FT", "20HC", "40FT HC"]:
                # Has container type but no shipment_type - assume FCL
                is_fcl = True
            else:
                # Default: not FCL (could be LCL or unknown)
                is_fcl = False
        
        if is_fcl:
            # This is an FCL shipment - volume should NOT be required
            if "volume" in missing_fields:
                missing_fields.remove("volume")
                print(f"✅ NEXT_ACTION: Removed volume from missing fields (FCL shipment with container type: {container_type})")
        else:
            # This is an LCL shipment - container_count should NOT be required
            if "container_count" in missing_fields or "Number of containers" in " ".join(missing_fields) or "Quantity (number of containers)" in " ".join(missing_fields):
                missing_fields = [f for f in missing_fields if "container_count" not in f.lower() and "number of containers" not in f.lower() and "quantity (number of containers)" not in f.lower()]
                print(f"✅ NEXT_ACTION: Removed container_count from missing fields (LCL shipment)")
        
        return missing_fields

    def _check_customer_confirmation(self, conversation_state: str, email_classification: Dict[str, Any]) -> bool:
        """Check if customer has confirmed the shipment details."""
        # Check conversation state for confirmation indicators
        if "confirmation" in conversation_state.lower() or "confirmed" in conversation_state.lower():
            return True
        
        # Check email classification for confirmation intent
        email_type = email_classification.get("email_type", "").lower()
        intent = email_classification.get("intent", "").lower()
        
        if "confirmation" in email_type or "confirmed" in intent:
            return True
        
        # Check for confirmation keywords in email type
        confirmation_keywords = ["confirmation", "confirmed", "yes", "correct", "proceed", "okay", "ok"]
        for keyword in confirmation_keywords:
            if keyword in email_type or keyword in intent:
                return True
        
        return False

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_next_action_agent():
    print("=== Testing Next Action Agent ===")
    agent = NextActionAgent()
    
    if not agent.load_context():
        print("✗ Failed to load context")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "New Request - Complete Data",
            "conversation_state": "new_request",
            "extracted_data": {
                "origin": "Shanghai",
                "destination": "Long Beach",
                "container_type": "40GP",
                "quantity": 2,
                "ready_date": "2024-02-15"
            },
            "confidence_score": 0.85,
            "missing_fields": [],
            "latest_sender": "customer",
            "expected_action": "send_confirmation_request"
        },
        {
            "name": "New Request - Incomplete Data",
            "conversation_state": "new_request",
            "extracted_data": {
                "origin": "Shanghai",
                "destination": "Long Beach"
            },
            "confidence_score": 0.75,
            "missing_fields": ["container_type", "quantity", "ready_date"],
            "latest_sender": "customer",
            "expected_action": "send_clarification_request"
        },
        {
            "name": "Forwarder Response",
            "conversation_state": "forwarder_response",
            "extracted_data": {
                "rate_amount": 2500,
                "currency": "USD",
                "valid_until": "2024-01-15"
            },
            "confidence_score": 0.90,
            "missing_fields": [],
            "latest_sender": "forwarder",
            "expected_action": "analyze_rates_and_notify_sales"
        },
        {
            "name": "Low Confidence",
            "conversation_state": "new_request",
            "extracted_data": {},
            "confidence_score": 0.45,
            "missing_fields": ["origin", "destination", "container_type"],
            "latest_sender": "customer",
            "expected_action": "escalate_to_human"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        result = agent.run({
            "conversation_state": test_case["conversation_state"],
            "extracted_data": test_case["extracted_data"],
            "confidence_score": test_case["confidence_score"],
            "missing_fields": test_case["missing_fields"],
            "latest_sender": test_case["latest_sender"],
            "thread_id": "test-thread-1"
        })
        
        if result.get("status") == "success":
            actual_action = result.get("next_action")
            expected_action = test_case["expected_action"]
            priority = result.get("action_priority")
            escalation = result.get("escalation_needed")
            sales_handoff = result.get("sales_handoff_needed")
            
            print(f"✓ Action: {actual_action} (expected: {expected_action})")
            print(f"✓ Priority: {priority}")
            print(f"✓ Escalation: {escalation}")
            print(f"✓ Sales Handoff: {sales_handoff}")
            
            if actual_action == expected_action:
                print("✓ Action prediction correct!")
            else:
                print("✗ Action prediction incorrect")
        else:
            print(f"✗ Test failed: {result.get('error')}")

if __name__ == "__main__":
    test_next_action_agent() 