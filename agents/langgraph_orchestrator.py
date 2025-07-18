import json
import logging
import os
from typing import Dict, Any, List
try:
    from .classification_agent import ClassificationAgent
    from .extraction_agent import ExtractionAgent
    from .validation_agent import ValidationAgent
    from .container_standardization_agent import ContainerStandardizationAgent
    from .port_lookup_agent import PortLookupAgent
    from .rate_recommendation_agent import RateRecommendationAgent
    from .response_generator_agent import ResponseGeneratorAgent
    from .memory_agent import MemoryAgent
    from .logging_agent import LoggingAgent
    from .country_extractor_agent import CountryExtractorAgent
    from .forwarder_assignment_agent import ForwarderAssignmentAgent
    from .smart_clarification_agent import SmartClarificationAgent
    from .confirmation_agent import ConfirmationAgent
    from .confirmation_response_agent import ConfirmationResponseAgent
    from .escalation_agent import EscalationAgent
    from .email_sender_agent import EmailSenderAgent
except ImportError:
    from classification_agent import ClassificationAgent
    from extraction_agent import ExtractionAgent
    from validation_agent import ValidationAgent
    from container_standardization_agent import ContainerStandardizationAgent
    from port_lookup_agent import PortLookupAgent
    from rate_recommendation_agent import RateRecommendationAgent
    from response_generator_agent import ResponseGeneratorAgent
    from memory_agent import MemoryAgent
    from logging_agent import LoggingAgent
    from country_extractor_agent import CountryExtractorAgent
    from forwarder_assignment_agent import ForwarderAssignmentAgent
    from smart_clarification_agent import SmartClarificationAgent
    from confirmation_agent import ConfirmationAgent
    from confirmation_response_agent import ConfirmationResponseAgent
    from escalation_agent import EscalationAgent
    from email_sender_agent import EmailSenderAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

def log_and_memory(state: dict, step: str):
    # Log the action
    LoggingAgent().process({
        "event_type": "info",
        "message": f"Step: {step}",
        "agent_name": "orchestrator",
        "details": state.copy()
    })
    # Store in memory
    MemoryAgent().process({
        "action": "store",
        "thread_id": state.get("thread_id", "unknown"),
        "message": {"step": step, "state": state.copy()}
    })

def run_workflow(message_thread: List[Dict[str, Any]], subject: str, thread_id: str = "thread-1"):
    """
    Run workflow with full message thread analysis.
    
    Args:
        message_thread: List of message dictionaries with keys:
            - sender: email address
            - timestamp: message timestamp
            - body: message content
            - subject: message subject (optional)
        subject: Current thread subject
        thread_id: Thread identifier
    """
    # Validate input
    if not message_thread or not isinstance(message_thread, list):
        raise ValueError("message_thread must be a non-empty list")
    
    # Get latest message for backward compatibility
    latest_message = message_thread[0] if message_thread else {}
    
    state: Dict[str, Any] = {
        "message_thread": message_thread,
        "latest_message": latest_message,
        "email_text": latest_message.get("body", ""),  # Backward compatibility
        "subject": subject,
        "from": latest_message.get("sender", "customer@example.com"),
        "thread_id": thread_id
    }

    # Step 2: Classification
    classification_agent = ClassificationAgent()
    classification_agent.load_context()
    classification_result = classification_agent.process({
        "message_thread": state["message_thread"],
        "email_text": state["email_text"],  # Backward compatibility
        "subject": state["subject"],
        "thread_id": state["thread_id"]
    })
    state["classification"] = classification_result
    log_and_memory(state, "classification")
    
    # Check if classification is poor (low confidence or unclear email type)
    classification_confidence = classification_result.get("confidence", 0.0)
    email_type = classification_result.get("email_type", "unknown")
    
    # Define what constitutes "poor classification"
    poor_classification = (
        classification_confidence < 0.6 or  # Very low confidence
        email_type == "unknown" or  # Unknown email type
        email_type == "non_logistics" or  # Non-logistics emails
        email_type not in ["logistics_request", "confirmation_reply", "forwarder_response", "clarification_reply"]  # Invalid types
    )
    
    if poor_classification:
        # Route to escalation agent for poor classification
        escalation_agent = EscalationAgent()
        escalation_agent.load_context()
        escalation_result = escalation_agent.process({
            "email_text": state["email_text"],
            "subject": state["subject"],
            "message_thread": state["message_thread"],
            "prior_results": {
                "classification": classification_result
            }
        })
        
        state["escalation"] = escalation_result
        
        # Use the acknowledgment response from escalation agent
        customer_intent = escalation_result.get("customer_intent", "general inquiry")
        acknowledgment_response = escalation_result.get("acknowledgment_response", "")
        is_non_logistics = escalation_result.get("is_non_logistics_inquiry", False)
        escalation_type = escalation_result.get("escalation_type", "poor_classification")
        
        # If escalation agent didn't provide acknowledgment, use default
        if not acknowledgment_response:
            if is_non_logistics:
                # Comprehensive response for non-logistics inquiries
                acknowledgment_response = f"""Dear {state.get('from', 'Valued Customer')},

Thank you for contacting SeaRates by DP World, a leading global logistics and supply chain solutions provider.

**About SeaRates by DP World:**
We are part of DP World, one of the world's largest port operators, with a presence in over 40 countries and 78 marine and inland terminals. Our digital platform serves customers in 190+ countries.

**Our Comprehensive Service Portfolio:**
• **Ocean Freight:** FCL/LCL shipping, project cargo, dangerous goods, temperature-controlled shipping
• **Air Freight:** Express and standard air freight services worldwide
• **Land Transport:** Road and rail transportation solutions
• **Warehousing & Distribution:** Global warehousing and fulfillment services
• **Customs Clearance:** Expert customs documentation and clearance
• **Insurance:** Comprehensive cargo insurance solutions
• **Supply Chain Solutions:** End-to-end supply chain optimization

**Digital Solutions:**
• Online booking and rate comparison at www.searates.com
• Real-time shipment tracking and visibility
• Digital documentation management
• API integration for seamless connectivity

**Industry Expertise:**
We specialize in serving automotive, electronics, pharmaceuticals, fashion, food & beverage, and chemical industries with tailored solutions.

**Sustainability:**
Committed to reducing carbon footprint through sustainable logistics practices and green initiatives.

**Your Inquiry:** {customer_intent}

**Next Steps:**
Visit www.searates.com for detailed information, online booking, and instant rate quotes. Our team is also available to provide personalized assistance.

**Contact Information:**
• Website: www.searates.com
• Phone: +1-555-0123
• WhatsApp: +1-555-0123
• Email: info@dpworld.com

We look forward to serving your logistics needs!

Best regards,
SeaRates by DP World Team"""
            else:
                # Standard escalation response for logistics-related issues
                acknowledgment_response = f"""Dear {state.get('from', 'Valued Customer')},

Thank you for reaching out to SeaRates by DP World. We have received your message and a human agent will contact you shortly to assist with your inquiry.

**About SeaRates by DP World:**
We are a leading global logistics and supply chain solutions provider, offering:
- International shipping and freight forwarding
- Container shipping (FCL/LCL) worldwide
- Supply chain optimization and consulting
- Customs clearance and documentation
- Real-time tracking and visibility
- Competitive rates and reliable service

**Your Inquiry:** {customer_intent}

**What happens next:**
1. A human agent will review your message within 1 hour
2. They will contact you directly to understand your specific needs
3. You'll receive personalized assistance and competitive quotes

**Contact Information:**
- Phone: +1-555-0123
- WhatsApp: +1-555-0123
- Email: support@dpworld.com
- Website: www.searates.com

We appreciate your interest in our services and look forward to serving you.

Best regards,
SeaRates by DP World Team"""
        
        # Determine response status based on escalation type
        if is_non_logistics:
            response_status = "non_logistics_inquiry_handled"
        else:
            response_status = "escalated_poor_classification"
        
        state["response"] = {
            "response_subject": "Thank you for contacting SeaRates by DP World",
            "response_body": acknowledgment_response,
            "status": response_status,
            "escalation_type": escalation_type,
            "customer_intent": customer_intent,
            "escalation_details": escalation_result,
            "is_non_logistics_inquiry": is_non_logistics
        }
        log_and_memory(state, "exit_poor_classification")
        return state

    # Step 2.5: Confirmation Detection (moved to after clarification)
    # This will be processed after clarification to understand if customer is responding to clarification

    # Step 3: Extraction
    extraction_agent = ExtractionAgent()
    extraction_agent.load_context()
    
    extraction_result = extraction_agent.process({
        "message_thread": state["message_thread"],
        "email_text": state["email_text"],  # Backward compatibility
        "subject": state["subject"]
    })
    state["extraction"] = extraction_result
    
    # Store extraction result in memory for future reference
    if extraction_result.get("status") == "success":
        MemoryAgent().process({
            "action": "store",
            "thread_id": state["thread_id"],
            "message": {"step": "extraction", "previous_extraction": extraction_result}
        })
    
    log_and_memory(state, "extraction")

    # Step 4: Check completeness
    clarification_needed = extraction_result.get("clarification_needed", False)
    state["clarification_needed"] = clarification_needed
    state["missing_fields"] = extraction_result.get("missing_fields", [])
    log_and_memory(state, "check_completeness")

    # Step 5: Validation/Standardization
    validation_agent = ValidationAgent()
    validation_agent.load_context()
    validation_result = validation_agent.process({
        "extraction_data": extraction_result,
        "email_type": classification_result.get("email_type", "logistics_request"),
        "message_thread": state["message_thread"]
    })
    state["validation"] = validation_result
    log_and_memory(state, "validation")

    # Step 5.5: Smart Clarification Agent (after container standardization and port lookup)
    # This will be moved to after container standardization and port lookup
    # for now, we'll keep it here but update the logic later

    # Step 5.6: Confirmation Detection (after clarification)
    confirmation_agent = ConfirmationAgent()
    confirmation_agent.load_context()
    confirmation_result = confirmation_agent.process({
        "message_thread": state["message_thread"],
        "email_text": state["email_text"],  # Backward compatibility
        "subject": state["subject"],
        "thread_id": state["thread_id"]
    })
    state["confirmation"] = confirmation_result
    log_and_memory(state, "confirmation")

    # Step 5.5: Container Standardization
    container_standardization_result = {}
    container_type = extraction_result.get("container_type", "")
    if container_type:
        container_standardization_agent = ContainerStandardizationAgent()
        container_standardization_agent.load_context()
        container_standardization_result = container_standardization_agent.process({
            "container_type": container_type
        })
    
    state["container_standardization"] = container_standardization_result
    log_and_memory(state, "container_standardization")

    # Step 6: Port Lookup (get port names for user validation)
    port_lookup_result = {}
    origin_port = extraction_result.get("origin", "")
    destination_port = extraction_result.get("destination", "")
    
    if origin_port or destination_port:
        port_lookup_agent = PortLookupAgent()
        port_lookup_agent.load_context()
        
        port_names = []
        if origin_port:
            port_names.append(origin_port)
        if destination_port:
            port_names.append(destination_port)
        
        port_lookup_result = port_lookup_agent.process({
            "port_names": port_names
        })
    
    state["port_lookup"] = port_lookup_result
    log_and_memory(state, "port_lookup")
    
    # Step 6.5: Update validated_data with port codes from port lookup
    if port_lookup_result.get("results"):
        validated_data = validation_result.get("validated_data", {})
        
        for port_result in port_lookup_result["results"]:
            port_name = port_result.get("port_name", "")
            port_code = port_result.get("port_code", "")
            
            # Update origin if it matches
            if origin_port and origin_port.lower() in port_name.lower():
                validated_data["origin_code"] = port_code
                validated_data["origin_name"] = port_name
            # Update destination if it matches
            elif destination_port and destination_port.lower() in port_name.lower():
                validated_data["destination_code"] = port_code
                validated_data["destination_name"] = port_name
        
        # Update the validation result with the corrected data
        validation_result["validated_data"] = validated_data

    # Step 6.6: Smart Clarification Agent (after container standardization and port lookup)
    smart_clarification_agent = SmartClarificationAgent()
    smart_clarification_result = smart_clarification_agent.process({
        "extraction_data": extraction_result,
        "validation_data": validation_result,
        "container_standardization_data": container_standardization_result,
        "port_lookup_data": port_lookup_result,
        "missing_fields": validation_result.get("missing_fields", []),
        "thread_id": state["thread_id"],
        "message_thread": state["message_thread"]
    })
    state["clarification"] = smart_clarification_result
    log_and_memory(state, "smart_clarification")

    # Step 7: Indicative Rate (if codes and container_type present)
    rate_result = {}
    origin_code = validation_result.get("validated_data", {}).get("origin_code")
    destination_code = validation_result.get("validated_data", {}).get("destination_code")
    
    # Get standardized container type from container standardization agent
    standardized_container_type = None
    if container_standardization_result.get("success"):
        standardized_container_type = container_standardization_result.get("standard_type")
    elif validation_result.get("validated_data", {}).get("container_type"):
        # Fallback to validation agent's container type
        standardized_container_type = validation_result.get("validated_data", {}).get("container_type")
    
    if origin_code and destination_code and standardized_container_type:
        rate_agent = RateRecommendationAgent()
        rate_agent.load_context()
        rate_result = rate_agent.process({
            "Origin_Code": origin_code,
            "Destination_Code": destination_code,
            "Container_Type": standardized_container_type
        })
    state["rate"] = rate_result
    log_and_memory(state, "rate_recommendation")

    # Step 7.5: Check if confirmation is detected and handle accordingly
    is_confirmation = confirmation_result.get("is_confirmation", False)
    confirmation_type = confirmation_result.get("confirmation_type", "no_confirmation")
    confirmation_confidence = confirmation_result.get("confidence", 0.0)
    
    if is_confirmation and confirmation_confidence > 0.6:
        # Use confirmation response agent for confirmed requests
        confirmation_response_agent = ConfirmationResponseAgent()
        confirmation_response_agent.load_context()
        
        # Get customer information from extraction
        customer_name = extraction_result.get("customer_name", "Valued Customer")
        customer_email = extraction_result.get("customer_email", state.get("from", "customer@example.com"))
        
        # Get shipment details from extraction
        shipment_details = {
            "origin": extraction_result.get("origin"),
            "destination": extraction_result.get("destination"),
            "container_type": extraction_result.get("container_type"),
            "quantity": extraction_result.get("quantity"),
            "weight": extraction_result.get("weight"),
            "volume": extraction_result.get("volume"),
            "commodity": extraction_result.get("commodity"),
            "shipment_date": extraction_result.get("shipment_date"),
            "shipment_type": extraction_result.get("shipment_type")
        }
        
        # Get rate information
        rate_info = {
            "indicative_rate": rate_result.get("indicative_rate"),
            "rate_range": rate_result.get("rate_recommendation", {}).get("rate_range")
        }
        
        # Get assigned sales person from forwarder assignment
        assigned_sales_person = {
            "name": "Sarah Johnson",
            "designation": "Digital Sales Specialist", 
            "company": "SeaRates by DP World",
            "email": "sarah.johnson@dpworld.com",
            "phone": "+1-555-0123",
            "whatsapp": "+1-555-0123"
        }
        
        confirmation_response_result = confirmation_response_agent.process({
            "customer_name": customer_name,
            "customer_email": customer_email,
            "confirmation_type": confirmation_type,
            "confirmation_details": confirmation_result.get("confirmation_details", ""),
            "shipment_details": shipment_details,
            "rate_info": rate_info,
            "assigned_sales_person": assigned_sales_person
        })
        
        state["confirmation_response"] = confirmation_response_result
        log_and_memory(state, "confirmation_response")
        
        # Set response to confirmation response
        state["response"] = confirmation_response_result
        log_and_memory(state, "confirmation_response_final")
        return state

    # Step 7.5: Extract countries using CountryExtractorAgent and assign forwarder using CSV
    forwarder_assignment = {}
    origin_country = ""
    destination_country = ""
    
    # Extract countries from port codes using CountryExtractorAgent
    origin_code = validation_result.get("validated_data", {}).get("origin_code", "")
    destination_code = validation_result.get("validated_data", {}).get("destination_code", "")
    
    if origin_code:
        country_extractor = CountryExtractorAgent()
        country_extractor.load_context()
        origin_country_result = country_extractor.process({
            "port_code": origin_code,
            "include_recommendations": False
        })
        if origin_country_result.get("success"):
            origin_country = origin_country_result.get("country_name", "")
    
    if destination_code:
        country_extractor = CountryExtractorAgent()
        country_extractor.load_context()
        destination_country_result = country_extractor.process({
            "port_code": destination_code,
            "include_recommendations": False
        })
        if destination_country_result.get("success"):
            destination_country = destination_country_result.get("country_name", "")
    
    # Use ForwarderAssignmentAgent with CSV file
    forwarder_csv_path = "Forwarders_with_Operators_and_Emails.csv"
    if os.path.exists(forwarder_csv_path) and origin_country and destination_country:
        try:
            forwarder_agent = ForwarderAssignmentAgent(forwarder_csv_path)
            forwarder_result = forwarder_agent.assign_forwarders(origin_country, destination_country)
            
            # Select forwarder based on priority: both_countries > origin_forwarders > destination_forwarders > random
            selected_forwarder = "Global Logistics Partners"  # default
            assignment_method = "default"
            
            if forwarder_result.get("both_countries"):
                # Forwarders that operate in both origin and destination countries
                selected_forwarder = forwarder_result["both_countries"][0]
                assignment_method = "both_countries"
            elif forwarder_result.get("origin_forwarders"):
                # Forwarders that operate in origin country
                selected_forwarder = forwarder_result["origin_forwarders"][0]
                assignment_method = "origin_country"
            elif forwarder_result.get("destination_forwarders"):
                # Forwarders that operate in destination country
                selected_forwarder = forwarder_result["destination_forwarders"][0]
                assignment_method = "destination_country"
            
            forwarder_assignment = {
                "assigned_forwarder": selected_forwarder,
                "origin_country": origin_country,
                "destination_country": destination_country,
                "assignment_method": assignment_method,
                "available_forwarders": {
                    "both_countries": forwarder_result.get("both_countries", []),
                    "origin_forwarders": forwarder_result.get("origin_forwarders", []),
                    "destination_forwarders": forwarder_result.get("destination_forwarders", [])
                }
            }
        except Exception as e:
            logger.error(f"Forwarder assignment failed: {e}")
            forwarder_assignment = {
                "assigned_forwarder": "Global Logistics Partners",
                "origin_country": origin_country,
                "destination_country": destination_country,
                "assignment_method": "error_fallback"
            }
    else:
        forwarder_assignment = {
            "assigned_forwarder": "Global Logistics Partners",
            "origin_country": origin_country or "Unknown",
            "destination_country": destination_country or "Unknown", 
            "assignment_method": "default"
        }
    
    state["forwarder_assignment"] = forwarder_assignment
    log_and_memory(state, "forwarder_assignment")

    # Step 8: Response Generation
    response_agent = ResponseGeneratorAgent()
    response_agent.load_context()
    response_input = {
        "classification_data": classification_result,
        "confirmation_data": confirmation_result,
        "extraction_data": extraction_result,
        "validation_data": validation_result,
        "clarification_data": smart_clarification_result,
        "container_standardization_data": container_standardization_result,
        "port_lookup_data": port_lookup_result,
        "rate_data": rate_result,
        "forwarder_assignment": forwarder_assignment,
        "subject": state["subject"],
        "email_text": state["email_text"],
        "from": state["from"],
        "thread_id": state["thread_id"],
        "message_thread": state["message_thread"]
    }
    response_result = response_agent.process(response_input)
    state["response"] = response_result
    log_and_memory(state, "response_generation")

    # Step 9: Email Sending (if confirmation detected)
    email_sender_agent = EmailSenderAgent()
    email_sender_agent.load_context()
    
    # Check if this is a confirmation and send acknowledgment email
    if confirmation_result.get("is_confirmation", False):
        customer_email_result = email_sender_agent.process({
            "email_type": "customer_acknowledgment",
            "customer_email": state["from"],
            "confirmation_data": confirmation_result,
            "thread_id": state["thread_id"],
            "timestamp": "2024-01-15 10:30:00"  # You might want to get this from actual timestamp
        })
        state["customer_email"] = customer_email_result
        log_and_memory(state, "customer_acknowledgment_email")
        
        # Send notification to assigned forwarder
        if forwarder_assignment.get("assigned_forwarder"):
            forwarder_email_result = email_sender_agent.process({
                "email_type": "forwarder_notification",
                "forwarder_assignment": forwarder_assignment,
                "thread_id": state["thread_id"],
                "customer_email": state["from"],
                "extraction_data": extraction_result,
                "rate_data": rate_result
            })
            state["forwarder_email"] = forwarder_email_result
            log_and_memory(state, "forwarder_notification_email")

    return state

if __name__ == "__main__":
    # Example test run
    result = run_workflow(
        message_thread=[
            {
                "sender": "customer@example.com",
                "timestamp": "2024-01-15 10:30:00",
                "body": "We want to ship from jebel ali to mundra,using 20DC containers. The total quantity is 99, total weight is 26 Metric Ton, shipment type is FCL, and the shipment date is 20th June 2025. The cargo is electronics."
            }
        ],
        subject="rate request",
        thread_id="thread-1234"
    )
    print(json.dumps(result["response"], indent=2))
