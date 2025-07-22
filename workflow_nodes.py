#!/usr/bin/env python3
"""
Workflow Nodes for LangGraph Orchestrator
========================================

Simple and focused nodes for the logistic AI workflow.
"""

import sys
import os
import logging
from typing import Dict, Any, TypedDict, List
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import agents
from agents.conversation_state_agent import ConversationStateAgent
from agents.classification_agent import ClassificationAgent
from agents.extraction_agent import ExtractionAgent
from agents.port_lookup_agent import PortLookupAgent
from agents.container_standardization_agent import ContainerStandardizationAgent
from agents.enhanced_validation_agent import EnhancedValidationAgent
from agents.rate_recommendation_agent import RateRecommendationAgent
from agents.next_action_agent import NextActionAgent
from agents.response_generator_agent import ResponseGeneratorAgent
from agents.forwarder_assignment_agent import ForwarderAssignmentAgent

# =====================================================
#                 🏗️ STATE DEFINITION
# =====================================================

class WorkflowState(TypedDict):
    """Workflow state object."""
    # Input
    email_text: str
    subject: str
    sender: str
    thread_id: str
    timestamp: str
    
    # Processing
    conversation_state: str
    confidence_score: float
    email_type: str
    intent: str
    email_classification: Dict[str, Any]
    extracted_data: Dict[str, Any]
    enriched_data: Dict[str, Any]
    validation_results: Dict[str, Any]
    rate_recommendation: Dict[str, Any]
    forwarder_assignment: Dict[str, Any]
    
    # Control
    current_node: str
    workflow_history: List[str]
    errors: List[str]
    next_action: str
    decision_result: Dict[str, Any]
    
    # Output
    final_response: Dict[str, Any]
    workflow_complete: bool

# =====================================================
#                 🎯 WORKFLOW NODES
# =====================================================

_agent_cache = {}

def get_cached_agent(agent_class, agent_name):
    """Get or create a cached agent instance."""
    if agent_name not in _agent_cache:
        agent = agent_class()
        agent.load_context()
        _agent_cache[agent_name] = agent
    return _agent_cache[agent_name]

def email_input_node(state: WorkflowState) -> WorkflowState:
    """Initialize workflow state with email input data."""
    print("\n" + "="*60)
    print("🚀 EMAIL_INPUT: Initializing workflow state...")
    print("="*60)
    print(f"📧 EMAIL_INPUT: Processing email from {state.get('sender', 'Unknown')}")
    print(f"📧 EMAIL_INPUT: Subject: {state.get('subject', 'No subject')}")
    
    # Initialize workflow state
    state["current_node"] = "EMAIL_INPUT"
    state["workflow_history"] = ["EMAIL_INPUT"]
    state["errors"] = []
    state["workflow_complete"] = False
    state["conversation_state"] = "new_request"
    state["confidence_score"] = 0.5
    state["extracted_data"] = {}
    state["enriched_data"] = {}
    state["validation_results"] = {}
    
    print("✅ EMAIL_INPUT: Workflow state initialized successfully")
    print("="*60)
    return state

def conversation_state_node(state: WorkflowState) -> WorkflowState:
    """Analyze conversation context and determine if this is a new request or continuation."""
    print("\n" + "="*60)
    print("🔄 CONVERSATION_STATE: Analyzing conversation context...")
    print("="*60)
    print(f"📧 CONVERSATION_STATE: Email text length: {len(state.get('email_text', ''))} characters")
    
    try:
        # Load conversation state agent
        agent = ConversationStateAgent()
        agent.load_context()
        
        result = agent.run({
            "email_text": state["email_text"],
            "thread_id": state["thread_id"],
            "sender": state["sender"],
            "timestamp": state["timestamp"]
        })
        
        if isinstance(result, dict):
            state["conversation_state"] = result.get("conversation_state", "new_request")
            state["confidence_score"] = result.get("confidence_score", 0.5)
            print(f"✅ CONVERSATION_STATE: Analysis complete - State = {state['conversation_state']}, Confidence = {state['confidence_score']:.2f}")
        else:
            print(f"⚠️ CONVERSATION_STATE: Unexpected result format - {type(result)}")
        
        state["workflow_history"].append("CONVERSATION_STATE")
        state["current_node"] = "CONVERSATION_STATE"
        
    except Exception as e:
        state["errors"].append(f"Conversation state error: {str(e)}")
        print(f"❌ CONVERSATION_STATE: Error occurred - {str(e)}")
    
    print("="*60)
    return state

def classification_node(state: WorkflowState) -> WorkflowState:
    """Classify email type and intent (customer request, confirmation, forwarder email, etc.)."""
    print("\n" + "="*60)
    print("🏷️ CLASSIFICATION: Analyzing email type and intent...")
    print("="*60)
    print(f"📧 CLASSIFICATION: Conversation state = {state.get('conversation_state', 'unknown')}")
    
    try:
        # Load classification agent
        agent = ClassificationAgent()
        agent.load_context()
        
        # Classify email
        print("🏷️ CLASSIFICATION: Running email classification...")
        result = agent.run({
            "email_text": state["email_text"],
            "conversation_state": state["conversation_state"]
        })
        
        if isinstance(result, dict):
            state["email_type"] = result.get("email_type", "unknown")
            state["intent"] = result.get("intent", "unknown")
            state["email_classification"] = result
            print(f"✅ CLASSIFICATION: Email type = {state['email_type']}, Intent = {state['intent']}")
        else:
            print(f"⚠️ CLASSIFICATION: Unexpected result format - {type(result)}")
        
        state["workflow_history"].append("CLASSIFICATION")
        state["current_node"] = "CLASSIFICATION"
        
    except Exception as e:
        state["errors"].append(f"Classification error: {str(e)}")
        print(f"❌ CLASSIFICATION: Error occurred - {str(e)}")
    
    print("="*60)
    return state

def data_extraction_node(state: WorkflowState) -> WorkflowState:
    """Extract shipment details from email content (ports, container, weight, commodity, etc.)."""
    print("\n" + "="*60)
    print("📋 DATA_EXTRACTION: Extracting shipment details from email...")
    print("="*60)
    print(f"📧 DATA_EXTRACTION: Email type = {state.get('email_type', 'unknown')}")
    
    try:
        # Load extraction agent
        agent = ExtractionAgent()
        agent.load_context()
        
        # Extract shipment data
        print("📋 DATA_EXTRACTION: Running data extraction...")
        result = agent.run({
            "email_text": state["email_text"],
            "email_type": state["email_type"],
            "intent": state["intent"]
        })
        
        if isinstance(result, dict):
            state["extracted_data"] = result
            
            # Pretty print extracted data
            import json
            from datetime import datetime
            print("\n📊 EXTRACTED DATA:")
            print("=" * 60)
            extracted_summary = {
                "NODE": "DATA_EXTRACTION",
                "STATUS": "SUCCESS",
                "EXTRACTED_FIELDS": {
                    "origin": {
                        "name": result.get('origin_name', 'N/A'),
                        "country": result.get('origin_country', 'N/A')
                    },
                    "destination": {
                        "name": result.get('destination_name', 'N/A'),
                        "country": result.get('destination_country', 'N/A')
                    },
                    "shipment_details": {
                        "type": result.get('shipment_type', 'N/A'),
                        "container": result.get('container_type', 'N/A'),
                        "weight": result.get('weight', 'N/A'),
                        "volume": result.get('volume', 'N/A'),
                        "commodity": result.get('commodity', 'N/A'),
                        "date": result.get('shipment_date', 'N/A'),
                        "quantity": result.get('quantity', 'N/A')
                    }
                },
                "CONFIDENCE": result.get('confidence_score', 0.0),
                "EXTRACTION_METHOD": "LLM_FUNCTION_CALL",
                "TIMESTAMP": datetime.now().isoformat()
            }
            print(json.dumps(extracted_summary, indent=2))
            print("=" * 60)
        else:
            print(f"⚠️ DATA_EXTRACTION: Unexpected result format - {type(result)}")
        
        state["workflow_history"].append("DATA_EXTRACTION")
        state["current_node"] = "DATA_EXTRACTION"
        
    except Exception as e:
        state["errors"].append(f"Data extraction error: {str(e)}")
        print(f"❌ DATA_EXTRACTION: Error occurred - {str(e)}")
    
    print("="*60)
    return state

def data_enrichment_node(state: WorkflowState) -> WorkflowState:
    """Enrich extracted data with port codes and container standardization."""
    print("\n" + "="*60)
    print("🔧 DATA_ENRICHMENT: Starting data enrichment process...")
    print("="*60)
    
    # Check if we can skip enrichment (optimization)
    if state.get("validation_results", {}).get("enriched_data"):
        print("⏭️ DATA_ENRICHMENT: Skipping - using enriched data from validation agent")
        enriched_data = state["validation_results"]["enriched_data"]
        state["enriched_data"] = enriched_data
        state["workflow_history"].append("DATA_ENRICHMENT")
        state["current_node"] = "DATA_ENRICHMENT"
        print("="*60)
        return state
    
    if state.get("enriched_data", {}).get("rate_data"):
        print("⏭️ DATA_ENRICHMENT: Skipping - rate_data already exists")
        state["workflow_history"].append("DATA_ENRICHMENT")
        state["current_node"] = "DATA_ENRICHMENT"
        print("="*60)
        return state
    
    enriched_data = {}
    
    try:
        # Port Lookup - Use new separate port fields if available
        port_names = []
        origin_name = state["extracted_data"].get("origin_name", "")
        destination_name = state["extracted_data"].get("destination_name", "")
        
        if origin_name:
            port_names.append(origin_name)
        elif state["extracted_data"].get("origin_port", ""):
            port_names.append(state["extracted_data"].get("origin_port", ""))
        elif state["extracted_data"].get("origin"):
            # Extract port name from full origin (e.g., "Jebel Ali, UAE" -> "Jebel Ali")
            origin = state["extracted_data"]["origin"]
            if "," in origin:
                port_names.append(origin.split(",")[0].strip())
            else:
                port_names.append(origin)
            
        if destination_name:
            port_names.append(destination_name)
        elif state["extracted_data"].get("destination_port", ""):
            port_names.append(state["extracted_data"].get("destination_port", ""))
        elif state["extracted_data"].get("destination"):
            # Extract port name from full destination (e.g., "Mundra, India" -> "Mundra")
            destination = state["extracted_data"]["destination"]
            if "," in destination:
                port_names.append(destination.split(",")[0].strip())
            else:
                port_names.append(destination)
        
        if port_names:
            print(f"🔧 DATA_ENRICHMENT: Found port names: {port_names}")
            
            # Use cached port lookup agent for better performance
            port_agent = get_cached_agent(PortLookupAgent, "port_lookup")
            print("🔧 DATA_ENRICHMENT: Running port lookup...")
            port_result = port_agent.run({"port_names": port_names})
            
            # Always add port lookup result
            enriched_data["port_lookup"] = port_result
            
            # Prepare rate data only if port lookup was successful
            if "results" in port_result and not "error" in port_result:
                port_results = port_result.get("results", [])
                print(f"✅ DATA_ENRICHMENT: Found {len(port_results)} port results")
                if len(port_results) >= 2:
                    enriched_data["rate_data"] = {
                        "origin_code": port_results[0].get("port_code", ""),
                        "destination_code": port_results[1].get("port_code", ""),
                        "origin_name": port_results[0].get("port_name", ""),
                        "destination_name": port_results[1].get("port_name", "")
                    }
                    print(f"✅ DATA_ENRICHMENT: Created rate_data with codes: {enriched_data['rate_data']['origin_code']} → {enriched_data['rate_data']['destination_code']}")
                else:
                    print(f"⚠️ DATA_ENRICHMENT: Not enough port results ({len(port_results)}) for rate data")
            else:
                print(f"❌ DATA_ENRICHMENT: Port lookup failed - {port_result.get('error', 'Unknown error')}")
        else:
            print(f"⚠️ DATA_ENRICHMENT: No port names found in extracted data")
            port_result = {"status": "error", "error": "No port names found"}
            enriched_data["port_lookup"] = port_result
        
        # Container Standardization
        if state["extracted_data"].get("container_type"):
            container_type = state["extracted_data"]["container_type"]
            print(f"🔍 DATA_ENRICHMENT: Container type = {container_type}")
            
            container_agent = get_cached_agent(ContainerStandardizationAgent, "container_standardization")
            container_result = container_agent.run({"container_type": container_type})
            
            # Always add container standardization result with status
            enriched_data["container_standardization"] = container_result
            
            # Add to rate data only if container standardization was successful
            if container_result.get("status") == "success":
                if enriched_data.get("rate_data"):
                    enriched_data["rate_data"]["container_type"] = container_result.get("standard_type", "")
        
        state["enriched_data"] = enriched_data
        
        # Pretty print enriched data
        import json
        from datetime import datetime
        print("\n📊 ENRICHED DATA:")
        print("=" * 60)
        
        # Helper function to safely get nested values
        def safe_get(data, key, default="N/A"):
            if isinstance(data, dict):
                return data.get(key, default)
            return default
        
        # Helper function to safely get list values
        def safe_get_list(data, key, default=None):
            if isinstance(data, dict):
                return data.get(key, default if default is not None else [])
            return default if default is not None else []
        
        rate_data = enriched_data.get("rate_data", {})
        container_std = enriched_data.get("container_standardization", {})
        
        enriched_summary = {
            "NODE": "DATA_ENRICHMENT",
            "STATUS": "SUCCESS",
            "ENRICHMENT_RESULTS": {
                "port_lookup": {
                    "status": safe_get(port_result, "status", "unknown"),
                    "results_count": len(safe_get_list(port_result, "results")),
                    "error": safe_get(port_result, "error", "none"),
                    "ports_found": [p.get("port_name", "") for p in safe_get_list(port_result, "results") if isinstance(p, dict)]
                },
                "rate_data": {
                    "origin_code": safe_get(rate_data, "origin_code"),
                    "destination_code": safe_get(rate_data, "destination_code"),
                    "origin_name": safe_get(rate_data, "origin_name"),
                    "destination_name": safe_get(rate_data, "destination_name"),
                    "container_type": safe_get(rate_data, "container_type")
                },
                "container_standardization": {
                    "input_type": state["extracted_data"].get("container_type", "N/A"),
                    "standardized_type": safe_get(container_std, "standard_type"),
                    "status": safe_get(container_std, "status")
                }
            },
            "ENRICHMENT_METHOD": "PORT_LOOKUP_AND_CONTAINER_STANDARDIZATION",
            "TIMESTAMP": datetime.now().isoformat()
        }
        print(json.dumps(enriched_summary, indent=2))
        print("=" * 60)
        
        state["workflow_history"].append("DATA_ENRICHMENT")
        state["current_node"] = "DATA_ENRICHMENT"
        
    except Exception as e:
        state["errors"].append(f"Data enrichment error: {str(e)}")
        print(f"❌ DATA_ENRICHMENT: Error occurred - {str(e)}")
    
    print("="*60)
    return state

def validation_node(state: WorkflowState) -> WorkflowState:
    """Validate extracted data and apply business rules (FCL/LCL logic, dangerous goods detection, etc.)."""
    print("\n" + "="*60)
    print("✅ VALIDATION: Starting data validation and business rule application...")
    print("="*60)
    
    try:
        # Load validation agent
        agent = EnhancedValidationAgent()
        agent.load_context()
        
        # Get port codes from enriched data
        rate_data = state["enriched_data"].get("rate_data", {})
        origin_code = rate_data.get("origin_code", "")
        destination_code = rate_data.get("destination_code", "")
        container_type = rate_data.get("container_type", "")
        
        print(f"✅ VALIDATION: Port codes: {origin_code} → {destination_code}")
        print(f"✅ VALIDATION: Container type: {container_type}")
        
        # Create validation data with port codes instead of port names
        validation_data = {}
        
        # Add port codes if available
        if origin_code:
            validation_data["origin"] = origin_code
        if destination_code:
            validation_data["destination"] = destination_code
        if container_type:
            validation_data["container_type"] = container_type
            
        # Add other extracted data (including weight, volume, etc.)
        for key, value in state["extracted_data"].items():
            if key not in ["origin", "destination", "container_type"]:
                validation_data[key] = value  # Include all fields, even if empty
        
        validation_input = {
            "extracted_data": state["extracted_data"],  # Pass original extracted data
            "enriched_data": state["enriched_data"],
            "validation_data": validation_data,  # Pass processed validation data
            "port_codes": {
                "origin_port": origin_code,
                "destination_port": destination_code,
                "container_type": container_type
            }
        }
        
        # 🔍 DEBUG POINT 8
        #import pdb; pdb.set_trace()
        
        result = agent.run(validation_input)
        
        if isinstance(result, dict):
            state["validation_results"] = result
            
            # Pretty print validation results
            import json
            from datetime import datetime
            print("\n📊 VALIDATION RESULTS:")
            print("=" * 60)
            
            overall_validation = result.get("overall_validation", {})
            validation_summary = {
                "NODE": "VALIDATION",
                "STATUS": "SUCCESS",
                "VALIDATION_RESULTS": {
                    "completeness": {
                        "score": overall_validation.get("completeness_score", 0.0),
                        "percentage": f"{overall_validation.get('completeness_score', 0):.1%}",
                        "is_complete": overall_validation.get("is_complete", False)
                    },
                    "confidence": {
                        "score": overall_validation.get("confidence_score", 0.0),
                        "percentage": f"{overall_validation.get('confidence_score', 0):.1%}"
                    },
                    "issues": {
                        "missing_fields": overall_validation.get("missing_fields", []),
                        "critical_issues": overall_validation.get("critical_issues", []),
                        "warnings": overall_validation.get("warnings", [])
                    },
                    "business_logic": overall_validation.get("business_logic_validation", {})
                },
                "VALIDATION_METHOD": "ENHANCED_VALIDATION_AGENT",
                "TIMESTAMP": datetime.now().isoformat()
            }
            print(json.dumps(validation_summary, indent=2))
            print("=" * 60)
            
            # Extract enriched data from validation result if available
            if "enriched_data" in result and result["enriched_data"]:
                state["enriched_data"].update(result["enriched_data"])
                print(f"✅ VALIDATION: Added enriched data from validation agent")
        
        state["workflow_history"].append("VALIDATION")
        state["current_node"] = "VALIDATION"
        
    except Exception as e:
        state["errors"].append(f"Validation error: {str(e)}")
        print(f"❌ VALIDATION: Error occurred - {str(e)}")
    
    print("="*60)
    return state

def rate_recommendation_node(state: WorkflowState) -> WorkflowState:
    """Get rate recommendations."""
    print("🔍 RATE_RECOMMENDATION: Starting")
    
    # 🔍 DEBUG POINT 10
    #import pdb; pdb.set_trace()
    
    try:
        agent = RateRecommendationAgent()
        agent.load_context()
        
        # Get validated data
        validation_results = state["validation_results"].get("validation_results", {})
        rate_data = state["enriched_data"].get("rate_data", {})
        
        print(f"🔍 RATE_RECOMMENDATION: Validation results = {validation_results}")
        print(f"🔍 RATE_RECOMMENDATION: Rate data = {rate_data}")
        
        # # Check if validation passed
        # origin_valid = validation_results.get("origin_port", {}).get("is_valid", False)
        # destination_valid = validation_results.get("destination_port", {}).get("is_valid", False)
        # container_valid = validation_results.get("container_type", {}).get("is_valid", False)

        origin_valid = validation_results.get("origin_port", {})
        destination_valid = validation_results.get("destination_port", {})
        container_valid = validation_results.get("container_type", {})
        
        if origin_valid and destination_valid and container_valid:
            rate_input = {
                "origin_code": rate_data.get("origin_code", ""),
                "destination_code": rate_data.get("destination_code", ""),
                "container_type": rate_data.get("container_type", "")
            }
            
            print(f"🔍 RATE_RECOMMENDATION: Rate input = {rate_input}")
            
            # 🔍 DEBUG POINT 11
            #import pdb; pdb.set_trace()
            
            result = agent.run(rate_input)
            
            print(f"🔍 RATE_RECOMMENDATION: Result = {result}")
            
            # 🔍 DEBUG POINT 12
            #import pdb; pdb.set_trace()
            
            if isinstance(result, dict):
                state["rate_recommendation"] = result
        else:
            print(f"🔍 RATE_RECOMMENDATION: Validation failed - skipping rate lookup")
            state["rate_recommendation"] = {"indicative_rate": None, "disclaimer": "Validation failed"}
        
        state["workflow_history"].append("RATE_RECOMMENDATION")
        state["current_node"] = "RATE_RECOMMENDATION"
        
    except Exception as e:
        state["errors"].append(f"Rate recommendation error: {str(e)}")
        print(f"❌ RATE_RECOMMENDATION: Error = {str(e)}")
    
    return state

def decision_node(state: WorkflowState) -> WorkflowState:
    """Decide next action."""
    print("🔍 DECISION: Starting")
    
    try:
        agent = NextActionAgent()
        agent.load_context()
        
        result = agent.run({
            "conversation_state": state["conversation_state"],
            "email_classification": state.get("email_classification", {}),
            "extracted_data": state["extracted_data"],
            "confidence_score": state["confidence_score"],
            "validation_results": state.get("validation_results", {}),
            "enriched_data": state.get("enriched_data", {}),
            "thread_id": state["thread_id"]
        })
        
        print(f"🔍 DECISION: Result = {result}")
        
        if isinstance(result, dict):
            state["next_action"] = result.get("next_action", "escalate_to_human")
            state["decision_result"] = result  # Store the full decision result
            
            # Pretty print decision results
            import json
            from datetime import datetime
            print("\n📊 DECISION RESULTS:")
            print("=" * 60)
            decision_summary = {
                "NODE": "DECISION",
                "STATUS": "SUCCESS",
                "DECISION_RESULTS": {
                    "next_action": result.get("next_action", "unknown"),
                    "action_priority": result.get("action_priority", "unknown"),
                    "response_type": result.get("response_type", "unknown"),
                    "escalation_needed": result.get("escalation_needed", False),
                    "sales_handoff_needed": result.get("sales_handoff_needed", False),
                    "confidence_score": result.get("confidence_score", 0.0),
                    "reasoning": result.get("reasoning", "No reasoning provided"),
                    "risk_factors": result.get("risk_factors", [])
                },
                "INPUT_CONTEXT": {
                    "conversation_state": state["conversation_state"],
                    "email_type": state.get("email_classification", {}).get("email_type", "unknown"),
                    "validation_completeness": state.get("validation_results", {}).get("overall_validation", {}).get("completeness_score", 0.0)
                },
                "DECISION_METHOD": "NEXT_ACTION_AGENT",
                "TIMESTAMP": datetime.now().isoformat()
            }
            print(json.dumps(decision_summary, indent=2))
            print("=" * 60)
        
        state["workflow_history"].append("DECISION")
        state["current_node"] = "DECISION"
        
    except Exception as e:
        state["errors"].append(f"Decision error: {str(e)}")
        print(f"❌ DECISION: Error = {str(e)}")
        state["next_action"] = "escalate_to_human"
    
    return state

def confirmation_request_node(state: WorkflowState) -> WorkflowState:
    """Generate confirmation response."""
    print("🔍 CONFIRMATION_REQUEST: Starting")
    
    try:
        agent = ResponseGeneratorAgent()
        agent.load_context()
        
        # Get enriched data with port names
        enriched_data = state.get("enriched_data", {})
        rate_data = enriched_data.get("rate_data", {})
        
        # Create response data with enriched port names and validation results
        response_data = {
            "extraction_data": state["extracted_data"],
            "rate_data": state.get("rate_recommendation", {}),
            "enriched_data": enriched_data,  # Include enriched data with port names
            "port_lookup_data": enriched_data.get("port_lookup", {}),
            "container_standardization_data": enriched_data.get("container_standardization", {}),
            "next_action_data": state.get("decision_result", {}),  # Pass decision result
            "validation_data": state.get("validation_results", {}),  # Pass validation results
            "is_confirmation": False
        }
        
        result = agent.run(response_data)
        
        print(f"🔍 CONFIRMATION_REQUEST: Result = {result}")
        
        if isinstance(result, dict):
            state["final_response"] = result
        
        state["workflow_complete"] = True
        state["workflow_history"].append("CONFIRMATION_REQUEST")
        state["current_node"] = "CONFIRMATION_REQUEST"
        
    except Exception as e:
        state["errors"].append(f"Confirmation error: {str(e)}")
        print(f"❌ CONFIRMATION_REQUEST: Error = {str(e)}")
    
    return state

def confirmation_acknowledgment_node(state: WorkflowState) -> WorkflowState:
    """Generate confirmation acknowledgment response."""
    print("🔍 CONFIRMATION_ACKNOWLEDGMENT: Starting")
    
    try:
        agent = ResponseGeneratorAgent()
        agent.load_context()
        
        # Get enriched data with port names
        enriched_data = state.get("enriched_data", {})
        rate_data = enriched_data.get("rate_data", {})
        
        # Create response data for acknowledgment
        response_data = {
            "extraction_data": state["extracted_data"],
            "rate_data": state.get("rate_recommendation", {}),
            "enriched_data": enriched_data,  # Include enriched data with port names
            "port_lookup_data": enriched_data.get("port_lookup", {}),
            "container_standardization_data": enriched_data.get("container_standardization", {}),
            "next_action_data": state.get("decision_result", {}),  # Pass decision result
            "validation_data": state.get("validation_results", {}),  # Pass validation results
            "is_confirmation": True,
            "response_type": "confirmation_acknowledgment"  # Explicitly set response type
        }
        
        result = agent.run(response_data)
        
        print(f"🔍 CONFIRMATION_ACKNOWLEDGMENT: Result = {result}")
        
        if isinstance(result, dict):
            state["final_response"] = result
        
        state["workflow_complete"] = True
        state["workflow_history"].append("CONFIRMATION_ACKNOWLEDGMENT")
        state["current_node"] = "CONFIRMATION_ACKNOWLEDGMENT"
        
    except Exception as e:
        state["errors"].append(f"Confirmation acknowledgment error: {str(e)}")
        print(f"❌ CONFIRMATION_ACKNOWLEDGMENT: Error = {str(e)}")
    
    return state

def forwarder_assignment_node(state: WorkflowState) -> WorkflowState:
    """Assign forwarders and generate rate requests."""
    print("🔧 FORWARDER_ASSIGNMENT: Starting")
    
    try:
        agent = ForwarderAssignmentAgent()
        agent.load_context()
        
        # Create input data for forwarder assignment
        assignment_data = {
            "extraction_data": state["extracted_data"],
            "enriched_data": state.get("enriched_data", {}),
            "validation_results": state.get("validation_results", {}),
            "thread_id": state["thread_id"]
        }
        
        result = agent.process(assignment_data)
        
        print(f"🔧 FORWARDER_ASSIGNMENT: Result = {result}")
        
        if isinstance(result, dict) and result.get("status") == "success":
            # Pretty print forwarder assignment results
            import json
            from datetime import datetime
            print("\n📊 FORWARDER ASSIGNMENT RESULTS:")
            print("=" * 60)
            forwarder_summary = {
                "NODE": "FORWARDER_ASSIGNMENT",
                "STATUS": "SUCCESS",
                "ASSIGNMENT_RESULTS": {
                    "total_forwarders": result.get("total_forwarders", 0),
                    "origin_country": result.get("origin_country", "N/A"),
                    "destination_country": result.get("destination_country", "N/A"),
                    "assignment_method": result.get("assignment_method", "unknown"),
                    "forwarders_assigned": [
                        {
                            "name": f.get("name", "N/A"),
                            "email": f.get("email", "N/A"),
                            "phone": f.get("phone", "N/A"),
                            "specialties": f.get("specialties", []),
                            "rating": f.get("rating", 0.0)
                        }
                        for f in result.get("assigned_forwarders", [])
                    ],
                    "rate_requests_generated": len(result.get("rate_requests", []))
                },
                "RATE_REQUESTS": [
                    {
                        "forwarder_name": req.get("forwarder_name", "N/A"),
                        "forwarder_email": req.get("forwarder_email", "N/A"),
                        "subject": req.get("subject", "N/A"),
                        "shipment_details": req.get("shipment_details", {})
                    }
                    for req in result.get("rate_requests", [])
                ],
                "ASSIGNMENT_METHOD": "COUNTRY_BASED_FORWARDER_ASSIGNMENT",
                "TIMESTAMP": datetime.now().isoformat()
            }
            print(json.dumps(forwarder_summary, indent=2))
            print("=" * 60)
            # Store forwarder assignment results
            state["forwarder_assignment"] = result
            
            # Generate customer acknowledgment response
            response_agent = ResponseGeneratorAgent()
            response_agent.load_context()
            
            # Create response data for customer acknowledgment
            response_data = {
                "extraction_data": state["extracted_data"],
                "rate_data": state.get("rate_recommendation", {}),
                "enriched_data": state.get("enriched_data", {}),
                "next_action_data": state.get("decision_result", {}),
                "validation_data": state.get("validation_results", {}),
                "forwarder_data": result,  # Include forwarder assignment data
                "is_confirmation": True,
                "response_type": "confirmation_acknowledgment"
            }
            
            customer_response = response_agent.run(response_data)
            
            if isinstance(customer_response, dict):
                state["final_response"] = customer_response
            
            state["workflow_complete"] = True
            state["workflow_history"].append("FORWARDER_ASSIGNMENT")
            state["current_node"] = "FORWARDER_ASSIGNMENT"
            
        else:
            state["errors"].append(f"Forwarder assignment failed: {result.get('error', 'Unknown error')}")
            print(f"❌ FORWARDER_ASSIGNMENT: Assignment failed")
        
    except Exception as e:
        state["errors"].append(f"Forwarder assignment error: {str(e)}")
        print(f"❌ FORWARDER_ASSIGNMENT: Error = {str(e)}")
    
    return state

def escalation_node(state: WorkflowState) -> WorkflowState:
    """Escalate to human."""
    print("🔍 ESCALATION: Starting")
    
    state["final_response"] = {
        "status": "escalation",
        "reason": "Low confidence or system error",
        "confidence_score": state["confidence_score"]
    }
    
    state["workflow_complete"] = True
    state["workflow_history"].append("ESCALATION")
    state["current_node"] = "ESCALATION"
    
    return state

# =====================================================
#                 🛣️ ROUTING FUNCTION
# =====================================================

def route_decision(state: WorkflowState) -> str:
    """Route to next node based on decision."""
    next_action = state.get("next_action", "escalate_to_human")
    print(f"🔍 ROUTING: Next action = {next_action}")
    
    # Route to CONFIRMATION_REQUEST for customer-facing responses
    if next_action in ["send_confirmation_request", "send_clarification_request"]:
        return "CONFIRMATION_REQUEST"
    
    # Route to FORWARDER_ASSIGNMENT for booking confirmations
    elif next_action in ["booking_details_confirmed_assign_forwarders"]:
        return "FORWARDER_ASSIGNMENT"
    
    # Route to CONFIRMATION_ACKNOWLEDGMENT for other confirmations
    elif next_action in ["send_confirmation_acknowledgment"]:
        return "CONFIRMATION_ACKNOWLEDGMENT"
    
    # Route to CONFIRMATION_REQUEST for forwarder-related actions (since FORWARDER_ASSIGNMENT node doesn't exist yet)
    elif next_action in ["collate_rates_and_send_to_sales", "send_forwarder_acknowledgment", "assign_forwarder_and_send_rate_request"]:
        return "CONFIRMATION_REQUEST"
    
    # Route to ESCALATION for everything else
    else:
        return "ESCALATION" 