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
    extracted_data: Dict[str, Any]
    enriched_data: Dict[str, Any]
    validation_results: Dict[str, Any]
    rate_recommendation: Dict[str, Any]
    
    # Control
    current_node: str
    workflow_history: List[str]
    errors: List[str]
    next_action: str
    
    # Output
    final_response: Dict[str, Any]
    workflow_complete: bool

# =====================================================
#                 🎯 WORKFLOW NODES
# =====================================================

def email_input_node(state: WorkflowState) -> WorkflowState:
    """Initialize workflow state."""
    print("🔍 EMAIL_INPUT: Starting")
    
    state["current_node"] = "EMAIL_INPUT"
    state["workflow_history"] = ["EMAIL_INPUT"]
    state["errors"] = []
    state["workflow_complete"] = False
    state["conversation_state"] = "new_request"
    state["confidence_score"] = 0.5
    state["extracted_data"] = {}
    state["enriched_data"] = {}
    state["validation_results"] = {}
    
    print(f"🔍 EMAIL_INPUT: Email from {state.get('sender')}")
    return state

def conversation_state_node(state: WorkflowState) -> WorkflowState:
    """Analyze conversation context."""
    print("🔍 CONVERSATION_STATE: Starting")
    
    try:
        agent = ConversationStateAgent()
        agent.load_context()
        
        result = agent.run({
            "email_text": state["email_text"],
            "thread_id": state["thread_id"],
            "sender": state["sender"],
            "timestamp": state["timestamp"]
        })
        
        print(f"🔍 CONVERSATION_STATE: Result = {result}")
        
        if isinstance(result, dict):
            state["conversation_state"] = result.get("conversation_state", "new_request")
            state["confidence_score"] = result.get("confidence_score", 0.5)
        
        state["workflow_history"].append("CONVERSATION_STATE")
        state["current_node"] = "CONVERSATION_STATE"
        
    except Exception as e:
        state["errors"].append(f"Conversation state error: {str(e)}")
        print(f"❌ CONVERSATION_STATE: Error = {str(e)}")
    
    return state

def classification_node(state: WorkflowState) -> WorkflowState:
    """Classify email type and intent."""
    print("🔍 CLASSIFICATION: Starting")
    
    try:
        agent = ClassificationAgent()
        agent.load_context()
        
        result = agent.run({
            "email_text": state["email_text"],
            "conversation_state": state["conversation_state"]
        })
        
        print(f"🔍 CLASSIFICATION: Result = {result}")
        
        if isinstance(result, dict):
            state["email_type"] = result.get("email_type", "unknown")
            state["intent"] = result.get("intent", "unknown")
        
        state["workflow_history"].append("CLASSIFICATION")
        state["current_node"] = "CLASSIFICATION"
        
    except Exception as e:
        state["errors"].append(f"Classification error: {str(e)}")
        print(f"❌ CLASSIFICATION: Error = {str(e)}")
    
    return state

def data_extraction_node(state: WorkflowState) -> WorkflowState:
    """Extract shipment details."""
    print("🔍 DATA_EXTRACTION: Starting")
    
    try:
        agent = ExtractionAgent()
        agent.load_context()
        
        result = agent.run({
            "email_text": state["email_text"],
            "email_type": state["email_type"],
            "intent": state["intent"]
        })
        
        print(f"🔍 DATA_EXTRACTION: Result = {result}")
        
        if isinstance(result, dict):
            state["extracted_data"] = result
            print(f"🔍 DATA_EXTRACTION: Origin = {result.get('origin')}")
            print(f"🔍 DATA_EXTRACTION: Destination = {result.get('destination')}")
            print(f"🔍 DATA_EXTRACTION: Container = {result.get('container_type')}")
        
        state["workflow_history"].append("DATA_EXTRACTION")
        state["current_node"] = "DATA_EXTRACTION"
        
    except Exception as e:
        state["errors"].append(f"Data extraction error: {str(e)}")
        print(f"❌ DATA_EXTRACTION: Error = {str(e)}")
    
    return state

def data_enrichment_node(state: WorkflowState) -> WorkflowState:
    """Enrich data with port codes and container standardization."""
    print("🔍 DATA_ENRICHMENT: Starting")
    

    
    enriched_data = {}
    
    try:
        # Port Lookup
        if state["extracted_data"].get("origin") or state["extracted_data"].get("destination"):
            port_names = []
            if state["extracted_data"].get("origin"):
                port_names.append(state["extracted_data"]["origin"])
            if state["extracted_data"].get("destination"):
                port_names.append(state["extracted_data"]["destination"])
            
            print(f"🔍 DATA_ENRICHMENT: Port names = {port_names}")
            

            
            port_agent = PortLookupAgent()
            port_agent.load_context()
            port_result = port_agent.run({"port_names": port_names})
            
            print(f"🔍 DATA_ENRICHMENT: Port result = {port_result}")
            
            # 🔍 DEBUG POINT 3
            #import pdb; pdb.set_trace()
            
            # Always add port lookup result with status
            enriched_data["port_lookup"] = port_result
            
            # Prepare rate data only if port lookup was successful
            if port_result.get("status") == "success":
                port_results = port_result.get("results", [])
                if len(port_results) >= 2:
                    enriched_data["rate_data"] = {
                        "origin_code": port_results[0].get("port_code", ""),
                        "destination_code": port_results[1].get("port_code", ""),
                        "origin_name": port_results[0].get("port_name", ""),
                        "destination_name": port_results[1].get("port_name", "")
                    }
        
        # Container Standardization
        if state["extracted_data"].get("container_type"):
            container_type = state["extracted_data"]["container_type"]
            print(f"🔍 DATA_ENRICHMENT: Container type = {container_type}")
            
            # 🔍 DEBUG POINT 4
            #import pdb; pdb.set_trace()
            
            container_agent = ContainerStandardizationAgent()
            container_agent.load_context()
            container_result = container_agent.run({"container_type": container_type})
            
            print(f"🔍 DATA_ENRICHMENT: Container result = {container_result}")
            
            # 🔍 DEBUG POINT 5
            #import pdb; pdb.set_trace()
            
            # Always add container standardization result with status
            enriched_data["container_standardization"] = container_result
            
            # Add to rate data only if container standardization was successful
            if container_result.get("status") == "success":
                if enriched_data.get("rate_data"):
                    enriched_data["rate_data"]["container_type"] = container_result.get("standard_type", "")
        
        state["enriched_data"] = enriched_data
        print(f"🔍 DATA_ENRICHMENT: Final enriched data = {enriched_data}")
        
        # 🔍 DEBUG POINT 6
        #import pdb; pdb.set_trace()
        
        state["workflow_history"].append("DATA_ENRICHMENT")
        state["current_node"] = "DATA_ENRICHMENT"
        
    except Exception as e:
        state["errors"].append(f"Data enrichment error: {str(e)}")
        print(f"❌ DATA_ENRICHMENT: Error = {str(e)}")
    
    return state

def validation_node(state: WorkflowState) -> WorkflowState:
    """Validate enriched data."""
    print("🔍 VALIDATION: Starting")
    
    # 🔍 DEBUG POINT 7
    #import pdb; pdb.set_trace()
    
    try:
        agent = EnhancedValidationAgent()
        agent.load_context()
        
        # Get port codes from enriched data
        rate_data = state["enriched_data"].get("rate_data", {})
        origin_code = rate_data.get("origin_code", "")
        destination_code = rate_data.get("destination_code", "")
        container_type = rate_data.get("container_type", "")
        
        print(f"🔍 VALIDATION: Port codes = {origin_code}, {destination_code}")
        print(f"🔍 VALIDATION: Container type = {container_type}")
        
        # Create validation data with port codes instead of port names
        validation_data = {}
        
        # Add port codes if available
        if origin_code:
            validation_data["origin"] = origin_code
        if destination_code:
            validation_data["destination"] = destination_code
        if container_type:
            validation_data["container_type"] = container_type
            
        # Add other extracted data
        for key, value in state["extracted_data"].items():
            if key not in ["origin", "destination", "container_type"] and value:
                validation_data[key] = value
        
        validation_input = {
            "extracted_data": validation_data,  # Use validation_data with port codes
            "enriched_data": state["enriched_data"],
            "port_codes": {
                "origin_port": origin_code,
                "destination_port": destination_code,
                "container_type": container_type
            }
        }
        
        # 🔍 DEBUG POINT 8
        #import pdb; pdb.set_trace()
        
        result = agent.run(validation_input)
        
        print(f"🔍 VALIDATION: Result = {result}")
        
        # 🔍 DEBUG POINT 9
        #import pdb; pdb.set_trace()
        
        if isinstance(result, dict):
            state["validation_results"] = result
        
        state["workflow_history"].append("VALIDATION")
        state["current_node"] = "VALIDATION"
        
    except Exception as e:
        state["errors"].append(f"Validation error: {str(e)}")
        print(f"❌ VALIDATION: Error = {str(e)}")
    
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
            "extracted_data": state["extracted_data"],
            "confidence_score": state["confidence_score"],
            "thread_id": state["thread_id"]
        })
        
        print(f"🔍 DECISION: Result = {result}")
        
        if isinstance(result, dict):
            state["next_action"] = result.get("next_action", "escalate_to_human")
        
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
        
        # Create response data with enriched port names
        response_data = {
            "extraction_data": state["extracted_data"],
            "rate_data": state.get("rate_recommendation", {}),
            "enriched_data": enriched_data,  # Include enriched data with port names
            "port_lookup_data": enriched_data.get("port_lookup", {}),
            "container_standardization_data": enriched_data.get("container_standardization", {}),
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
    
    if next_action == "send_confirmation_request":
        return "CONFIRMATION_REQUEST"
    else:
        return "ESCALATION" 