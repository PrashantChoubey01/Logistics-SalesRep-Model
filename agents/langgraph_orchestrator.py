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
    if classification_result.get("email_type") != "logistics_request":
        state["response"] = {
            "response_subject": "Thank you for your email",
            "response_body": "Your message does not appear to be a logistics request. If you need logistics support, please clarify your request.",
            "status": "not_logistics_request"
        }
        log_and_memory(state, "exit_non_logistics")
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
        "email_type": classification_result.get("email_type", "logistics_request")
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
        "thread_id": state["thread_id"]
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
        "thread_id": state["thread_id"]
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
