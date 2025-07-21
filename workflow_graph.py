#!/usr/bin/env python3
"""
Workflow Graph Creator
=====================

Creates the LangGraph workflow with all nodes and connections.
"""

from langgraph.graph import StateGraph, END
from workflow_nodes import (
    WorkflowState,
    email_input_node,
    conversation_state_node,
    classification_node,
    data_extraction_node,
    data_enrichment_node,
    validation_node,
    rate_recommendation_node,
    decision_node,
    confirmation_request_node,
    confirmation_acknowledgment_node,
    forwarder_assignment_node,
    escalation_node,
    route_decision
)

def create_workflow_graph():
    """Create the LangGraph workflow."""
    print("🏗️ Creating LangGraph workflow...")
    
    # Create the state graph
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("EMAIL_INPUT", email_input_node)
    workflow.add_node("CONVERSATION_STATE", conversation_state_node)
    workflow.add_node("CLASSIFICATION", classification_node)
    workflow.add_node("DATA_EXTRACTION", data_extraction_node)
    workflow.add_node("DATA_ENRICHMENT", data_enrichment_node)
    workflow.add_node("VALIDATION", validation_node)
    workflow.add_node("RATE_RECOMMENDATION", rate_recommendation_node)
    workflow.add_node("DECISION", decision_node)
    workflow.add_node("CONFIRMATION_REQUEST", confirmation_request_node)
    workflow.add_node("CONFIRMATION_ACKNOWLEDGMENT", confirmation_acknowledgment_node)
    workflow.add_node("FORWARDER_ASSIGNMENT", forwarder_assignment_node)
    workflow.add_node("ESCALATION", escalation_node)
    
    # Set entry point
    workflow.set_entry_point("EMAIL_INPUT")
    
    # Add edges (linear flow)
    workflow.add_edge("EMAIL_INPUT", "CONVERSATION_STATE")
    workflow.add_edge("CONVERSATION_STATE", "CLASSIFICATION")
    workflow.add_edge("CLASSIFICATION", "DATA_EXTRACTION")
    workflow.add_edge("DATA_EXTRACTION", "DATA_ENRICHMENT")
    workflow.add_edge("DATA_ENRICHMENT", "VALIDATION")
    workflow.add_edge("VALIDATION", "RATE_RECOMMENDATION")
    workflow.add_edge("RATE_RECOMMENDATION", "DECISION")
    
    # Add conditional edges from decision node
    workflow.add_conditional_edges(
        "DECISION",
        route_decision,
        {
            "CONFIRMATION_REQUEST": "CONFIRMATION_REQUEST",
            "CONFIRMATION_ACKNOWLEDGMENT": "CONFIRMATION_ACKNOWLEDGMENT",
            "FORWARDER_ASSIGNMENT": "FORWARDER_ASSIGNMENT",
            "ESCALATION": "ESCALATION"
        }
    )
    
    # Add edges to END
    workflow.add_edge("CONFIRMATION_REQUEST", END)
    workflow.add_edge("CONFIRMATION_ACKNOWLEDGMENT", END)
    workflow.add_edge("FORWARDER_ASSIGNMENT", END)
    workflow.add_edge("ESCALATION", END)
    
    print("✅ LangGraph workflow created successfully")
    return workflow 