#!/usr/bin/env python3
"""
Enhanced LangGraph Workflow Orchestrator
=======================================

Complete workflow orchestrator for the multi-LLM logistics CRM system.
Integrates all agents with enhanced thread management and forwarder handling.
"""

import asyncio
import json
import logging
import operator
import copy
from datetime import datetime
from typing import Dict, Any, List, Optional, Annotated, TypedDict
from dataclasses import asdict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Import all agents
from agents.unified_email_classifier_agent import UnifiedEmailClassifierAgent
from agents.conversation_state_agent import ConversationStateAgent
from agents.thread_context_analyzer_agent import ThreadContextAnalyzerAgent
from agents.information_extraction_agent import InformationExtractionAgent
from agents.data_validation_agent import DataValidationAgent
from agents.port_lookup_agent import PortLookupAgent
from agents.container_standardization_agent import ContainerStandardizationAgent
from agents.rate_recommendation_agent import RateRecommendationAgent
# from agents.rate_analysis_agent import RateAnalysisAgent
from agents.next_action_agent import NextActionAgent
from agents.clarification_response_agent import ClarificationResponseAgent
from agents.confirmation_response_agent import ConfirmationResponseAgent
from agents.acknowledgment_response_agent import AcknowledgmentResponseAgent
from agents.confirmation_acknowledgment_agent import ConfirmationAcknowledgmentAgent
from agents.escalation_decision_agent import EscalationDecisionAgent
from agents.sales_notification_agent import SalesNotificationAgent
from agents.forwarder_detection_agent import ForwarderDetectionAgent
from agents.forwarder_response_agent import ForwarderResponseAgent
from agents.forwarder_email_draft_agent import ForwarderEmailDraftAgent

# Import utilities
from utils.thread_manager import ThreadManager, EmailEntry
from utils.forwarder_manager import ForwarderManager
from utils.logger import get_logger
from utils.sales_team_manager import SalesTeamManager
from utils.name_extractor import extract_name_from_email_data

logger = get_logger(__name__)

# Reducer function for escalation_result - handles concurrent updates
def _escalation_reducer(x: Optional[Dict[str, Any]], y: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Reducer for escalation_result - takes first non-None value to prevent conflicts"""
    return x if x is not None else y

# Reducer function for should_escalate - takes True if either value is True (OR logic)
def _should_escalate_reducer(x: bool, y: bool) -> bool:
    """Reducer for should_escalate - True if either value is True"""
    return x or y

# Reducer function for sales_notification_result - takes first non-None value
def _sales_notification_reducer(x: Optional[Dict[str, Any]], y: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Reducer for sales_notification_result - takes first non-None value to prevent conflicts"""
    return x if x is not None else y

# Reducer function for forwarder_response_result - takes first non-None value
# Using operator.add pattern for LangGraph compatibility
def _forwarder_response_reducer(x: Optional[Dict[str, Any]], y: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Reducer for forwarder_response_result - takes first non-None value to prevent conflicts.
    This ensures only one node can set forwarder_response_result per step."""
    # If both are None, return None
    if x is None and y is None:
        return None
    # If x is not None, return x (first value takes precedence)
    if x is not None:
        return x
    # Otherwise return y
    return y

class WorkflowState(TypedDict):
    """Enhanced workflow state with all necessary fields"""
    # Email data (immutable - set once at workflow start)
    email_data: Dict[str, Any]
    thread_history: Annotated[List[Dict[str, Any]], "shared"]
    
    # Agent results
    classification_result: Optional[Dict[str, Any]]
    conversation_state_result: Optional[Dict[str, Any]]
    thread_analysis_result: Optional[Dict[str, Any]]
    extraction_result: Optional[Dict[str, Any]]
    validation_result: Optional[Dict[str, Any]]
    port_lookup_result: Optional[Dict[str, Any]]
    container_standardization_result: Optional[Dict[str, Any]]
    rate_recommendation_result: Optional[Dict[str, Any]]
    next_action_result: Optional[Dict[str, Any]]
    
    # Response generation
    clarification_response_result: Optional[Dict[str, Any]]
    confirmation_response_result: Optional[Dict[str, Any]]
    acknowledgment_response_result: Optional[Dict[str, Any]]
    confirmation_acknowledgment_result: Optional[Dict[str, Any]]
    customer_quote_result: Optional[Dict[str, Any]]
    
    # Forwarder handling
    forwarder_detection_result: Optional[Dict[str, Any]]
    forwarder_response_result: Annotated[Optional[Dict[str, Any]], _forwarder_response_reducer]
    forwarder_email_draft_result: Optional[Dict[str, Any]]
    forwarder_assignment_result: Optional[Dict[str, Any]]
    
    # Escalation and notifications
    # Use reducer to handle concurrent updates - take the first non-None value
    escalation_result: Annotated[Optional[Dict[str, Any]], _escalation_reducer]
    sales_notification_result: Annotated[Optional[Dict[str, Any]], _sales_notification_reducer]
    
    # Context and metadata
    customer_context: Annotated[Dict[str, Any], "shared"]
    forwarder_context: Annotated[Dict[str, Any], "shared"]
    market_data: Annotated[Dict[str, Any], "shared"]
    historical_data: Annotated[Dict[str, Any], "shared"]
    
    # Decision flags
    # Use reducer to handle concurrent updates - True if either value is True
    should_escalate: Annotated[bool, _should_escalate_reducer]
    is_forwarder_email: bool
    workflow_completed: bool
    
    # Thread management
    thread_id: str
    cumulative_extraction: Dict[str, Any]
    
    # Metadata
    workflow_id: str
    timestamp: str
    assigned_sales_person: Optional[Dict[str, Any]]
    workflow_history: List[str]

class LangGraphWorkflowOrchestrator:
    """Enhanced workflow orchestrator with complete agent integration"""
    
    def __init__(self):
        self.thread_manager = ThreadManager()
        self.forwarder_manager = ForwarderManager()
        self._initialize_agents()
        self._build_workflow_graph()
        logger.info("LangGraph Workflow Orchestrator initialized successfully")
    
    def _initialize_agents(self):
        """Initialize all agents"""
        try:
            # Core agents
            self.classification_agent = UnifiedEmailClassifierAgent()
            self.conversation_state_agent = ConversationStateAgent()
            self.thread_analysis_agent = ThreadContextAnalyzerAgent()
            self.extraction_agent = InformationExtractionAgent()
            self.validation_agent = DataValidationAgent()
            self.port_lookup_agent = PortLookupAgent()
            self.container_standardization_agent = ContainerStandardizationAgent()
            self.rate_recommendation_agent = RateRecommendationAgent()
            self.next_action_agent = NextActionAgent()
            
            # Response generation agents
            self.clarification_agent = ClarificationResponseAgent()
            self.confirmation_agent = ConfirmationResponseAgent()
            self.acknowledgment_agent = AcknowledgmentResponseAgent()
            self.confirmation_acknowledgment_agent = ConfirmationAcknowledgmentAgent()
            
            # Forwarder handling agents
            self.forwarder_detection_agent = ForwarderDetectionAgent()
            self.forwarder_response_agent = ForwarderResponseAgent()
            self.forwarder_email_draft_agent = ForwarderEmailDraftAgent()
            
            # Escalation and notification agents
            self.escalation_agent = EscalationDecisionAgent()
            self.sales_notification_agent = SalesNotificationAgent()
            
            # Sales team manager for random assignments
            self.sales_team_manager = SalesTeamManager()
            
            # Load contexts for all agents
            agents = [
                self.classification_agent, self.conversation_state_agent, self.thread_analysis_agent,
                self.extraction_agent, self.validation_agent, self.port_lookup_agent,
                self.container_standardization_agent, self.rate_recommendation_agent, self.next_action_agent,
                self.clarification_agent, self.confirmation_agent, self.acknowledgment_agent, self.confirmation_acknowledgment_agent,
                self.forwarder_detection_agent, self.forwarder_response_agent, self.forwarder_email_draft_agent,
                self.escalation_agent, self.sales_notification_agent
            ]
            
            for agent in agents:
                if hasattr(agent, 'load_context'):
                    agent.load_context()
            
            logger.info("✅ All agents initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agents: {e}")
            raise
    
    def _build_workflow_graph(self):
        """Build the complete workflow graph"""
        logger.info("Building workflow graph...")
        
        workflow = StateGraph(WorkflowState)
        
        # Add all nodes
        workflow.add_node("classify_email", self._classify_email)
        workflow.add_node("conversation_state", self._conversation_state)
        workflow.add_node("analyze_thread", self._analyze_thread)
        workflow.add_node("extract_information", self._extract_information)
        workflow.add_node("update_cumulative_extraction", self._update_cumulative_extraction)
        workflow.add_node("validate_data", self._validate_data)
        workflow.add_node("lookup_ports", self._lookup_ports)
        workflow.add_node("standardize_container", self._standardize_container)
        workflow.add_node("recommend_rates", self._recommend_rates)
        workflow.add_node("next_action", self._next_action)
        workflow.add_node("assign_sales_person", self._assign_sales_person)
        
        # Response generation nodes
        workflow.add_node("generate_clarification_response", self._generate_clarification_response)
        workflow.add_node("generate_confirmation_response", self._generate_confirmation_response)
        workflow.add_node("generate_acknowledgment_response", self._generate_acknowledgment_response)
        workflow.add_node("generate_confirmation_acknowledgment", self._generate_confirmation_acknowledgment)
        
        # Forwarder handling nodes
        workflow.add_node("detect_forwarder", self._detect_forwarder)
        workflow.add_node("process_forwarder_response", self._process_forwarder_response)
        workflow.add_node("draft_forwarder_email", self._draft_forwarder_email)
        workflow.add_node("assign_forwarders", self._assign_forwarders)
        
        # Escalation and notification nodes
        workflow.add_node("check_escalation", self._check_escalation)
        workflow.add_node("notify_sales", self._notify_sales)
        
        # Thread management
        workflow.add_node("update_thread", self._update_thread)
        
        # Set entry point
        workflow.set_entry_point("classify_email")
        
        # Add conditional edges - Happy flow only, escalation removed
        workflow.add_conditional_edges(
            "classify_email",
            self._route_after_classification,
            {
                # REMOVED: "check_escalation": "check_escalation" - no escalation in happy flow
                "conversation_state": "conversation_state",
                "generate_acknowledgment_response": "generate_acknowledgment_response",
                "notify_sales": "notify_sales"
            }
        )
        
        workflow.add_conditional_edges(
            "conversation_state",
            self._route_after_conversation_state,
            {
                # REMOVED: "escalate": "check_escalation" - no escalation in happy flow
                "continue": "analyze_thread"
            }
        )
        
        workflow.add_edge("analyze_thread", "extract_information")
        workflow.add_edge("extract_information", "update_cumulative_extraction")
        workflow.add_edge("update_cumulative_extraction", "validate_data")
        workflow.add_edge("validate_data", "lookup_ports")
        workflow.add_edge("lookup_ports", "standardize_container")
        workflow.add_edge("standardize_container", "recommend_rates")
        workflow.add_edge("recommend_rates", "next_action")
        workflow.add_edge("next_action", "assign_sales_person")
        
        workflow.add_conditional_edges(
            "next_action",
            self._route_after_next_action,
            {
                "assign_sales_person": "assign_sales_person",
                "detect_forwarder": "detect_forwarder",
                # REMOVED: "check_escalation": "check_escalation" - no escalation in happy flow
            }
        )
        
        workflow.add_conditional_edges(
            "assign_sales_person",
            self._route_after_sales_assignment,
            {
                "generate_clarification_response": "generate_clarification_response",
                "generate_confirmation_response": "generate_confirmation_response",
                "generate_acknowledgment_response": "generate_acknowledgment_response",
                "generate_confirmation_acknowledgment": "generate_confirmation_acknowledgment",
                # REMOVED: "check_escalation": "check_escalation" - no escalation in happy flow
            }
        )
        
        # Response generation edges
        workflow.add_edge("generate_clarification_response", "update_thread")
        workflow.add_edge("generate_confirmation_response", "update_thread")
        workflow.add_edge("generate_acknowledgment_response", "update_thread")
        
        # Confirmation acknowledgment leads to forwarder assignment
        workflow.add_conditional_edges(
            "generate_confirmation_acknowledgment",
            self._route_after_confirmation_acknowledgment,
            {
                "assign_forwarders": "assign_forwarders",
                "update_thread": "update_thread"
            }
        )
        
        # Forwarder assignment leads to thread update
        workflow.add_edge("assign_forwarders", "update_thread")
        
        # Acknowledgment response routing - Happy flow only, escalation removed
        # For forwarder emails: acknowledgment -> process_forwarder_response -> notify_sales
        # For other emails: acknowledgment -> update_thread
        workflow.add_conditional_edges(
            "generate_acknowledgment_response",
            self._route_after_acknowledgment,
            {
                # REMOVED: "check_escalation": "check_escalation" - no escalation in happy flow
                "process_forwarder_response": "process_forwarder_response",  # For forwarder emails
                "update_thread": "update_thread"  # For other emails
            }
        )
        
        # Forwarder handling edges
        workflow.add_edge("detect_forwarder", "process_forwarder_response")
        workflow.add_edge("process_forwarder_response", "notify_sales")  # After processing forwarder response, notify sales
        
        # Add customer quote generation node
        workflow.add_node("generate_customer_quote", self._generate_customer_quote)
        workflow.add_edge("draft_forwarder_email", "update_thread")
        
        # Escalation edges
        workflow.add_edge("check_escalation", "notify_sales")
        # After sales notification, generate customer quote if forwarder rates are available
        workflow.add_conditional_edges(
            "notify_sales",
            self._route_after_sales_notification,
            {
                "generate_customer_quote": "generate_customer_quote",  # If forwarder rates available
                "update_thread": "update_thread"  # Otherwise just update thread
            }
        )
        
        # Customer quote leads to thread update
        workflow.add_edge("generate_customer_quote", "update_thread")
        
        # Final edge to END
        workflow.add_edge("update_thread", END)
        
        # Compile the workflow
        self.workflow = workflow.compile()
        logger.info("Workflow graph built and compiled successfully")
    
    # Node implementations
    async def _classify_email(self, state: WorkflowState) -> WorkflowState:
        """Step 1: Classify incoming email"""
        logger.info("🔄 Step 1: Classifying email...")
        print(f"\n{'='*60}")
        print(f"🔄 STEP 1: EMAIL CLASSIFICATION")
        print(f"{'='*60}")
        
        # Add safety checks for email_data structure
        email_data = state.get('email_data', {})
        if not email_data:
            error_msg = "❌ Email data is missing or empty"
            logger.error(error_msg)
            print(f"\n❌ CLASSIFICATION ERROR: {error_msg}")
            state["classification_result"] = {"error": error_msg, "email_type": "escalation_needed"}
            return state
        
        # Handle both content/body_text and sender/from_email formats
        content = email_data.get('content', email_data.get('body_text', email_data.get('body', '')))
        subject = email_data.get('subject', '')
        sender = email_data.get('sender', email_data.get('from_email', email_data.get('from', '')))
        
        if not content:
            error_msg = "❌ Email content is missing"
            logger.error(error_msg)
            print(f"\n❌ CLASSIFICATION ERROR: {error_msg}")
            state["classification_result"] = {"error": error_msg, "email_type": "escalation_needed"}
            return state
        
        print(f"📧 Email Content: {content[:200]}...")
        print(f"📧 Email Subject: {subject}")
        print(f"👤 Sender: {sender}")
        
        try:
            result = self.classification_agent.process({
                "email_text": content,
                "email_subject": subject,
                "sender": sender,
                "thread_id": state["thread_id"],
                "thread_history": state["thread_history"]
            })
            
            state["classification_result"] = result
            
            print(f"\n✅ CLASSIFICATION RESULT:")
            print(f"   Email Type: {result.get('email_type', 'unknown')}")
            print(f"   Sender Type: {result.get('sender_type', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 0.0)}")
            print(f"   Escalation Needed: {result.get('escalation_needed', False)}")
            print(f"   Intent: {result.get('intent', 'unknown')}")
            print(f"   Reasoning: {result.get('reasoning', 'No reasoning provided')}")
            
            logger.info(f"✅ Email classified as: {result.get('email_type', 'unknown')} (confidence: {result.get('confidence', 0.0)})")
            
        except Exception as e:
            error_msg = f"❌ Email classification failed: {e}"
            logger.error(error_msg)
            print(f"\n❌ CLASSIFICATION ERROR: {e}")
            state["classification_result"] = {"error": str(e), "email_type": "escalation_needed"}
        
        return state
    
    async def _conversation_state(self, state: WorkflowState) -> WorkflowState:
        """Step 2: Analyze conversation state"""
        logger.info("🔄 Step 2: Analyzing conversation state...")
        print(f"\n{'='*60}")
        print(f"🔄 STEP 2: CONVERSATION STATE ANALYSIS")
        print(f"{'='*60}")
        print(f"🧵 Thread ID: {state['thread_id']}")
        print(f"📧 Thread History Length: {len(state['thread_history'])}")
        print(f"👤 Customer Context: {len(state['customer_context'])} items")
        print(f"🚢 Forwarder Context: {len(state['forwarder_context'])} items")
        
        try:
            # Get email data safely
            email_data = state.get('email_data', {})
            if not email_data:
                raise ValueError("Email data is missing")
            
            # Handle both content/body_text formats
            content = email_data.get('content', email_data.get('body_text', email_data.get('body', '')))
            subject = email_data.get('subject', '')
            
            if not content:
                raise ValueError("Email content is missing")
            
            result = self.conversation_state_agent.process({
                "email_text": content,
                "subject": subject,
                "thread_id": state["thread_id"],
                "message_thread": state["thread_history"],
                "cumulative_extraction": state["cumulative_extraction"],
                "customer_context": state["customer_context"],
                "forwarder_context": state["forwarder_context"]
            })
            
            state["conversation_state_result"] = result
            state["should_escalate"] = result.get("should_escalate", False)
            
            print(f"\n✅ CONVERSATION STATE RESULT:")
            print(f"   Conversation Stage: {result.get('conversation_stage', 'unknown')}")
            print(f"   Latest Sender: {result.get('latest_sender', 'unknown')}")
            print(f"   Next Action: {result.get('next_action', 'unknown')}")
            print(f"   Should Escalate: {result.get('should_escalate', False)}")
            print(f"   Thread Context: {result.get('thread_context', {})}")
            
            logger.info(f"✅ Conversation state analyzed: {result.get('conversation_stage', 'unknown')}")
            
        except Exception as e:
            error_msg = f"❌ Conversation state analysis failed: {e}"
            logger.error(error_msg)
            print(f"\n❌ CONVERSATION STATE ERROR: {e}")
            state["conversation_state_result"] = {"error": str(e)}
            state["should_escalate"] = True
        
        return state
    
    async def _analyze_thread(self, state: WorkflowState) -> WorkflowState:
        """Step 3: Analyze thread context"""
        logger.info("🔄 Step 3: Analyzing thread context...")
        
        try:
            # Get email_data safely
            email_data_raw = state.get("email_data", {})
            if not email_data_raw:
                logger.error("❌ Email data is missing in thread analysis")
                state["thread_analysis_result"] = {"error": "Email data is missing"}
                return state
            
            # Handle both content/body_text and sender/from_email formats
            email_content = email_data_raw.get("content", email_data_raw.get("body_text", email_data_raw.get("body", "")))
            email_subject = email_data_raw.get("subject", "")
            email_sender = email_data_raw.get("sender", email_data_raw.get("from_email", email_data_raw.get("from", "")))
            
            # Prepare email_data in the format expected by thread analyzer
            email_data = {
                "email_text": email_content,
                "subject": email_subject,
                "sender": email_sender,
                "thread_id": state["thread_id"]
            }
            
            # Extract previous classifications from thread history
            previous_classifications = []
            for email_entry in state["thread_history"]:
                if "step_results" in email_entry and "classification" in email_entry["step_results"]:
                    classification = email_entry["step_results"]["classification"]
                    if classification and "error" not in classification:
                        previous_classifications.append(classification)
            
            result = self.thread_analysis_agent.process({
                "email_data": email_data,
                "thread_history": state["thread_history"],
                "previous_classifications": previous_classifications,
                "customer_context": state["customer_context"],
                "forwarder_context": state["forwarder_context"]
            })
            
            state["thread_analysis_result"] = result
            logger.info(f"✅ Thread analysis completed: {len(result.get('key_insights', []))} insights found")
            
        except Exception as e:
            logger.error(f"❌ Thread analysis failed: {e}")
            state["thread_analysis_result"] = {"error": str(e)}
        
        return state
    
    async def _extract_information(self, state: WorkflowState) -> WorkflowState:
        """Step 4: Extract information from email"""
        logger.info("🔄 Step 4: Extracting information...")
        print(f"\n{'='*60}")
        print(f"🔄 STEP 4: INFORMATION EXTRACTION")
        print(f"{'='*60}")
        email_data_raw = state.get("email_data", {})
        email_content = email_data_raw.get("content", email_data_raw.get("body_text", email_data_raw.get("body", "")))
        print(f"📧 Email Content Length: {len(email_content)} characters")
        print(f"🧵 Thread History: {len(state['thread_history'])} previous emails")
        print(f"📊 Cumulative Extraction: {len(state['cumulative_extraction'])} existing items")
        
        try:
            # Get email_data safely
            email_data_raw = state.get("email_data", {})
            if not email_data_raw:
                logger.error("❌ Email data is missing in information extraction")
                state["extraction_result"] = {"error": "Email data is missing"}
                return state
            
            # Handle both content/body_text and sender/from_email formats
            email_content = email_data_raw.get("content", email_data_raw.get("body_text", email_data_raw.get("body", "")))
            email_sender = email_data_raw.get("sender", email_data_raw.get("from_email", email_data_raw.get("from", "")))
            email_subject = email_data_raw.get("subject", "")
            
            result = self.extraction_agent.process({
                "email_text": email_content,
                "sender": email_sender,
                "subject": email_subject,
                "thread_id": state["thread_id"],
                "timestamp": state["timestamp"],
                "customer_context": state["customer_context"],
                "forwarder_context": state["forwarder_context"],
                "prioritize_recent": True,
                "cumulative_extraction": state["cumulative_extraction"]
            })
            
            state["extraction_result"] = result
            
            print(f"\n✅ EXTRACTION RESULT:")
            extracted_data = result.get('extracted_data', {})
            print(f"   Categories Extracted: {len(extracted_data)}")
            print(f"   Quality Score: {result.get('quality_score', 0.0)}")
            print(f"   Confidence: {result.get('confidence', 0.0)}")
            
            # Show key extracted information
            if 'shipment_details' in extracted_data:
                shipment = extracted_data['shipment_details']
                print(f"   📦 Shipment Details:")
                print(f"      Origin: {shipment.get('origin', 'Not found')}")
                print(f"      Destination: {shipment.get('destination', 'Not found')}")
                print(f"      Container: {shipment.get('container_type', 'Not found')}")
                print(f"      Weight: {shipment.get('weight', 'Not found')}")
            
            if 'contact_information' in extracted_data:
                contact = extracted_data['contact_information']
                print(f"   👤 Contact Information:")
                print(f"      Name: {contact.get('name', 'Not found')}")
                print(f"      Email: {contact.get('email', 'Not found')}")
            
            logger.info(f"✅ Information extraction completed: {len(extracted_data)} categories extracted")
            
        except Exception as e:
            error_msg = f"❌ Information extraction failed: {e}"
            logger.error(error_msg)
            print(f"\n❌ EXTRACTION ERROR: {e}")
            state["extraction_result"] = {"error": str(e)}
        
        return state
    
    async def _update_cumulative_extraction(self, state: WorkflowState) -> WorkflowState:
        """Step 4.5: Update cumulative extraction with new data"""
        logger.info("🔄 Step 4.5: Updating cumulative extraction...")
        
        try:
            # Get the new extraction result
            new_extraction = state["extraction_result"].get("extracted_data", {})
            
            if new_extraction:
                # Update cumulative extraction using thread manager's merge function
                updated_cumulative = self.thread_manager.merge_with_recency_priority(
                    new_extraction, 
                    state["cumulative_extraction"]
                )
                
                # Update the state
                state["cumulative_extraction"] = updated_cumulative
                
                # Also update the thread storage to persist the changes
                self.thread_manager.update_cumulative_extraction(
                    state["thread_id"], 
                    updated_cumulative
                )
                
                logger.info(f"✅ Cumulative extraction updated with {len(new_extraction)} new categories")
                logger.info(f"📊 Updated cumulative data: {updated_cumulative}")
                
                # Log detailed field updates
                for category, data in new_extraction.items():
                    if isinstance(data, dict):
                        for field, value in data.items():
                            if value and str(value).strip():
                                logger.info(f"   📝 Updated {category}.{field}: {value}")
                    elif value and str(value).strip():
                        logger.info(f"   📝 Updated {category}: {value}")
            else:
                logger.warning("⚠️ No new extraction data to merge")
            
        except Exception as e:
            logger.error(f"❌ Cumulative extraction update failed: {e}")
        
        return state
    
    async def _validate_data(self, state: WorkflowState) -> WorkflowState:
        """Step 5: Validate extracted data"""
        logger.info("🔄 Step 5: Validating extracted data...")
        
        try:
            result = self.validation_agent.process({
                "extracted_data": state["extraction_result"].get("extracted_data", {}),
                "validation_rules": state.get("validation_rules", {})
            })
            
            state["validation_result"] = result
            logger.info(f"✅ Data validation completed: {result.get('validation_score', 0)}% valid")
            
        except Exception as e:
            logger.error(f"❌ Data validation failed: {e}")
            state["validation_result"] = {"error": str(e)}
        
        return state
    
    async def _lookup_ports(self, state: WorkflowState) -> WorkflowState:
        """Step 6: Lookup port information"""
        logger.info("🔄 Step 6: Looking up port information...")
        
        try:
            # Use cumulative extraction data if available, otherwise use current extraction
            if state["cumulative_extraction"] and state["cumulative_extraction"].get("shipment_details"):
                shipment_details = state["cumulative_extraction"]["shipment_details"]
                logger.info("📊 Using cumulative extraction data for port lookup")
            else:
                shipment_details = state["extraction_result"].get("extracted_data", {}).get("shipment_details", {})
                logger.info("📊 Using current extraction data for port lookup")
            
            # Lookup origin port
            origin_result = None
            if shipment_details.get("origin"):
                origin_result = self.port_lookup_agent.process({
                    "port_name": shipment_details.get("origin")
                })
            
            # Lookup destination port
            destination_result = None
            if shipment_details.get("destination"):
                destination_result = self.port_lookup_agent.process({
                    "port_name": shipment_details.get("destination")
                })
            
            # Combine results
            result = {
                "origin": origin_result,
                "destination": destination_result,
                "port_codes": {}
            }
            
            # Extract port codes for rate recommendation
            if origin_result and origin_result.get("port_code"):
                result["port_codes"]["origin"] = origin_result["port_code"]
            if destination_result and destination_result.get("port_code"):
                result["port_codes"]["destination"] = destination_result["port_code"]
            
            state["port_lookup_result"] = result
            logger.info(f"✅ Port lookup completed: {len(result.get('port_codes', {}))} port codes found")
            
        except Exception as e:
            logger.error(f"❌ Port lookup failed: {e}")
            state["port_lookup_result"] = {"error": str(e)}
        
        return state
    
    async def _standardize_container(self, state: WorkflowState) -> WorkflowState:
        """Step 7: Standardize container information"""
        logger.info("🔄 Step 7: Standardizing container information...")
        
        try:
            # Use cumulative extraction data if available, otherwise use current extraction
            if state["cumulative_extraction"] and state["cumulative_extraction"].get("shipment_details"):
                shipment_details = state["cumulative_extraction"]["shipment_details"]
                logger.info("📊 Using cumulative extraction data for container standardization")
            else:
                shipment_details = state["extraction_result"].get("extracted_data", {}).get("shipment_details", {})
                logger.info("📊 Using current extraction data for container standardization")
            
            # CRITICAL: Check shipment_type - skip container standardization for LCL shipments
            shipment_type = shipment_details.get("shipment_type", "").strip().upper() if shipment_details.get("shipment_type") else ""
            
            if shipment_type == "LCL":
                # LCL shipments don't need container standardization
                logger.info("⏭️ Skipping container standardization for LCL shipment")
                state["container_standardization_result"] = {
                    "standardized_type": None,
                    "reason": "LCL shipment - container standardization not applicable"
                }
                return state
            
            # Only standardize if container_type exists (FCL shipment)
            container_type = shipment_details.get("container_type", "").strip() if shipment_details.get("container_type") else ""
            if not container_type:
                logger.info("⏭️ No container type to standardize")
                state["container_standardization_result"] = {
                    "standardized_type": None,
                    "reason": "No container type provided"
                }
                return state
            
            result = self.container_standardization_agent.process({
                "container_type": container_type,
                "container_count": shipment_details.get("container_count")
            })
            
            state["container_standardization_result"] = result
            logger.info(f"✅ Container standardization completed: {result.get('standardized_type', 'unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Container standardization failed: {e}")
            state["container_standardization_result"] = {"error": str(e)}
        
        return state
    
    async def _recommend_rates(self, state: WorkflowState) -> WorkflowState:
        """Step 8: Recommend rates"""
        logger.info("🔄 Step 8: Recommending rates...")
        
        try:
            # Use cumulative extraction data if available, otherwise use current extraction
            if state["cumulative_extraction"] and state["cumulative_extraction"].get("shipment_details"):
                shipment_details = state["cumulative_extraction"]["shipment_details"]
                logger.info("📊 Using cumulative extraction data for rate recommendation")
            else:
                shipment_details = state["extraction_result"].get("extracted_data", {}).get("shipment_details", {})
                logger.info("📊 Using current extraction data for rate recommendation")
            
            port_codes = state["port_lookup_result"].get("port_codes", {})
            container_type = state["container_standardization_result"]
            
            # Check if this is FCL shipment (has container type)
            container_type_from_extraction = shipment_details.get("container_type", "").strip()
            is_fcl = bool(container_type_from_extraction)
            
            if not is_fcl:
                logger.info("⏭️ Skipping rate recommendation for LCL shipment")
                state["rate_recommendation_result"] = {
                    "status": "skipped",
                    "reason": "LCL shipment - rate recommendation not applicable",
                    "rate_ranges": {},
                    "recommendations": []
                }
                return state
            
            # For FCL, use port codes and standardized container type
            enhanced_shipment_details = shipment_details.copy()
            enhanced_shipment_details["container_type"] = container_type  # Use standardized container type
            
            # Log the data being sent to rate recommendation
            logger.info(f"🔍 Rate Recommendation Input Data:")
            logger.info(f"   Shipment Details: {enhanced_shipment_details}")
            logger.info(f"   Port Codes: {port_codes}")
            
            result = self.rate_recommendation_agent.process({
                "shipment_details": enhanced_shipment_details,
                "port_codes": port_codes,
                "market_data": state["market_data"]
            })
            
            state["rate_recommendation_result"] = result
            logger.info(f"✅ Rate recommendation completed: {len(result.get('rate_ranges', {}))} routes analyzed")
            
        except Exception as e:
            logger.error(f"❌ Rate recommendation failed: {e}")
            state["rate_recommendation_result"] = {"error": str(e)}
        
        return state
    

    
    async def _next_action(self, state: WorkflowState) -> WorkflowState:
        """Step 10: Determine next action"""
        logger.info("🔄 Step 10: Determining next action...")
        print(f"\n{'='*60}")
        print(f"🔄 STEP 10: NEXT ACTION DETERMINATION")
        print(f"{'='*60}")
        print(f"📊 Classification: {state['classification_result'].get('email_type', 'unknown')}")
        print(f"🧵 Conversation State: {state['conversation_state_result'].get('conversation_stage', 'unknown')}")
        print(f"📦 Extraction Quality: {state['extraction_result'].get('quality_score', 0.0)}")
        print(f"✅ Validation Status: {state['validation_result'].get('validation_status', 'unknown')}")
        
        try:
            # CRITICAL: Use cumulative_extraction which has merged data including special_requirements
            # This ensures FCL/LCL detection works correctly
            extracted_data = state.get("cumulative_extraction", {})
            if not extracted_data:
                # Fallback to extraction_result if cumulative_extraction is not available
                extracted_data = state["extraction_result"].get("extracted_data", {})
            
            # Determine missing fields first using the clarification agent's logic
            missing_fields = self.clarification_agent._determine_missing_fields(extracted_data)
            
            print(f"📋 Missing Fields: {missing_fields}")
            
            result = self.next_action_agent.process({
                "conversation_state": state["conversation_state_result"].get("conversation_stage", "unknown"),
                "email_classification": state["classification_result"],
                "extracted_data": extracted_data,  # Use cumulative_extraction (with special_requirements)
                "confidence_score": state["extraction_result"].get("confidence", 0.0),
                "validation_results": state["validation_result"],
                "enriched_data": {
                    "port_lookup": state.get("port_lookup_result", {}),
                    "container_standardization": state.get("container_standardization_result", {}),
                    "rate_recommendation": state.get("rate_recommendation_result", {})
                },
                "thread_id": state["thread_id"],
                "missing_fields": missing_fields  # Pass missing fields to next action agent
            })
            
            state["next_action_result"] = result
            
            print(f"\n✅ NEXT ACTION RESULT:")
            print(f"   Next Action: {result.get('next_action', result.get('action', 'unknown'))}")
            print(f"   Action Priority: {result.get('action_priority', 'unknown')}")
            print(f"   Confidence: {result.get('confidence', 0.0)}")
            print(f"   Reasoning: {result.get('reasoning', 'No reasoning provided')}")
            print(f"   Should Escalate: {result.get('should_escalate', False)}")
            
            logger.info(f"✅ Next action determined: {result.get('next_action', result.get('action', 'unknown'))}")
            
        except Exception as e:
            error_msg = f"❌ Next action determination failed: {e}"
            logger.error(error_msg)
            print(f"\n❌ NEXT ACTION ERROR: {e}")
            state["next_action_result"] = {"error": str(e), "action": "escalate"}
        
        return state
    
    async def _assign_sales_person(self, state: WorkflowState) -> WorkflowState:
        """Assign a random sales person for dynamic signatures"""
        logger.info("🔄 Assigning sales person...")
        
        try:
            # Extract route information for assignment
            extraction_result = state.get("extraction_result", {})
            if not extraction_result:
                # For forwarder/sales person emails, we might not have extraction data
                logger.info("ℹ️ No extraction result available, using default route info")
                route_info = {
                    "origin": "",
                    "destination": "",
                    "container_type": "",
                    "commodity": ""
                }
            else:
                extracted_data = extraction_result.get("extracted_data", {})
                shipment_details = extracted_data.get("shipment_details", {})
                
                route_info = {
                    "origin": shipment_details.get("origin", ""),
                    "destination": shipment_details.get("destination", ""),
                    "container_type": shipment_details.get("container_type", ""),
                    "commodity": shipment_details.get("commodity", "")
                }
            
            # Generate random sales person
            assigned_person = self.sales_team_manager.assign_sales_person(route_info, {})
            state["assigned_sales_person"] = assigned_person
            
            print(f"\n✅ SALES PERSON ASSIGNED:")
            print(f"   Name: {assigned_person.get('name', 'Unknown')}")
            print(f"   Title: {assigned_person.get('title', 'Unknown')}")
            print(f"   Email: {assigned_person.get('email', 'Unknown')}")
            print(f"   Phone: {assigned_person.get('phone', 'Unknown')}")
            
            logger.info(f"✅ Sales person assigned: {assigned_person.get('name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Sales person assignment failed: {e}")
            # Fallback to default
            state["assigned_sales_person"] = {
                "name": "Digital Sales Specialist",
                "title": "Digital Sales Specialist",
                "email": "sales@logistics-company.com",
                "phone": "+1-555-0123",
                "signature": "Best regards,\n\nDigital Sales Specialist\nLogistics Solutions Inc.\n📧 sales@logistics-company.com\n📞 +1-555-0123"
            }
        
        return state
    
    # Response generation nodes
    async def _generate_clarification_response(self, state: WorkflowState) -> WorkflowState:
        """Generate clarification response - uses enriched ports and standardized container per spec"""
        logger.info("🔄 Generating clarification response...")
        
        try:
            # CRITICAL: Reload cumulative_extraction from thread_manager to ensure we have the latest merged data
            # This ensures we get the most up-to-date data even if state hasn't been updated yet
            thread_id = state.get("thread_id", "")
            if thread_id:
                latest_cumulative = self.thread_manager.get_cumulative_extraction(thread_id)
                if latest_cumulative and isinstance(latest_cumulative, dict):
                    # Use deepcopy to avoid modifying the original
                    extracted_data = copy.deepcopy(latest_cumulative)
                    logger.info("📊 Using latest cumulative extraction from thread manager for clarification response")
                elif state.get("cumulative_extraction") and isinstance(state["cumulative_extraction"], dict):
                    extracted_data = copy.deepcopy(state["cumulative_extraction"])
                    logger.info("📊 Using cumulative extraction from state for clarification response")
                else:
                    extracted_data = state["extraction_result"].get("extracted_data", {})
                    logger.info("📊 Using current extraction data for clarification response (no cumulative data available)")
            elif state.get("cumulative_extraction") and isinstance(state["cumulative_extraction"], dict):
                extracted_data = copy.deepcopy(state["cumulative_extraction"])
                logger.info("📊 Using cumulative extraction from state for clarification response")
            else:
                extracted_data = state["extraction_result"].get("extracted_data", {})
                logger.info("📊 Using current extraction data for clarification response (no cumulative data available)")
            
            # Debug logging
            logger.info(f"🔍 DEBUG: Raw extracted_data: {extracted_data}")
            logger.info(f"🔍 DEBUG: Container standardization result: {state.get('container_standardization_result')}")
            logger.info(f"🔍 DEBUG: Port lookup result: {state.get('port_lookup_result')}")
            
            # Let the clarification agent determine missing fields instead of using validation result
            missing_fields = []  # Will be determined by clarification agent
            
            # Use standardized container type in extracted_data for display (per spec)
            # The spec says clarification responses show standardized container types
            # IMPORTANT: Use standardized_type, NOT rate_fallback_type
            # CRITICAL: Only add container_type if shipment_type is NOT LCL
            shipment_type = extracted_data.get("shipment_details", {}).get("shipment_type", "").strip().upper() if extracted_data.get("shipment_details", {}).get("shipment_type") else ""
            
            if shipment_type == "LCL":
                # For LCL shipments, ensure container_type is cleared
                logger.info(f"🔍 DEBUG: LCL shipment detected - clearing container_type and container_count")
                if "shipment_details" in extracted_data:
                    if "container_type" in extracted_data["shipment_details"]:
                        del extracted_data["shipment_details"]["container_type"]
                    if "container_count" in extracted_data["shipment_details"]:
                        del extracted_data["shipment_details"]["container_count"]
            elif state.get("container_standardization_result") and isinstance(state["container_standardization_result"], dict):
                # Get standardized_type (the actual standardized type, e.g., "40HC")
                standardized_type = state["container_standardization_result"].get("standardized_type")
                # Do NOT use rate_fallback_type - that's only for pricing, not display
                logger.info(f"🔍 DEBUG: Standardized container type: {standardized_type}")
                logger.info(f"🔍 DEBUG: Rate fallback type (NOT used for display): {state['container_standardization_result'].get('rate_fallback_type')}")
                
                if standardized_type:
                    # Update extracted_data with standardized container type for display (only for FCL)
                    if "shipment_details" in extracted_data:
                        original_type = extracted_data["shipment_details"].get("container_type", "")
                        extracted_data["shipment_details"]["container_type"] = standardized_type
                        logger.info(f"🔍 DEBUG: Updated container type from '{original_type}' to '{standardized_type}'")
                    else:
                        # Create shipment_details if it doesn't exist
                        if "shipment_details" not in extracted_data:
                            extracted_data["shipment_details"] = {}
                        extracted_data["shipment_details"]["container_type"] = standardized_type
                        logger.info(f"🔍 DEBUG: Created shipment_details and set container type to '{standardized_type}'")
                else:
                    logger.warning(f"🔍 DEBUG: Standardized type is empty/None")
            else:
                logger.warning(f"🔍 DEBUG: No container standardization result available")
            
            result = self.clarification_agent.process({
                "extracted_data": extracted_data,
                "missing_fields": missing_fields,  # Empty list - agent will determine missing fields
                "customer_name": state["email_data"].get("sender_name", "Valued Customer"),  # First name extracted from email
                "agent_info": state["assigned_sales_person"],
                "port_lookup_result": state["port_lookup_result"],  # For enriched port display with codes
                "container_standardization_result": state.get("container_standardization_result")  # For reference
            })
            
            state["clarification_response_result"] = result
            
            # Print final response on terminal
            print(f"\n{'='*80}")
            print(f"📧 FINAL RESPONSE GENERATED: CLARIFICATION")
            print(f"{'='*80}")
            print(f"📧 Subject: {result.get('subject', 'No subject')}")
            print(f"👤 To: {state['email_data'].get('sender', 'Unknown')}")
            print(f"📝 Response Type: Clarification Request")
            print(f"📊 Missing Fields: {len(result.get('missing_fields', []))}")
            print(f"\n📄 RESPONSE BODY:")
            print(f"{result.get('body', 'No body')}")
            print(f"{'='*80}")
            
            logger.info(f"✅ Clarification response generated: {result.get('subject', 'No subject')}")
            
        except Exception as e:
            logger.error(f"❌ Clarification response generation failed: {e}")
            state["clarification_response_result"] = {"error": str(e)}
        
        return state
    
    def _validate_mandatory_fields_for_confirmation(self, extracted_data: Dict[str, Any], port_lookup_result: Dict[str, Any] = None) -> tuple:
        """
        Validate Priority 1-3 mandatory fields before generating confirmation.
        Returns (is_valid, missing_fields_list)
        """
        missing_fields = []
        shipment_details = extracted_data.get("shipment_details", {})
        
        # Priority 1: Origin & Destination (must be specific ports, not countries)
        origin = shipment_details.get("origin", "").strip()
        destination = shipment_details.get("destination", "").strip()
        origin_country = shipment_details.get("origin_country", "").strip()
        destination_country = shipment_details.get("destination_country", "").strip()
        
        # Only flag as missing if origin is EMPTY but origin_country is set (country-only input)
        # If origin is set (even if origin_country is also set), it's a valid port with country info
        if not origin and origin_country:
            # Origin is a country, not a specific port
            missing_fields.append("Origin (specific port required)")
        elif not origin:
            missing_fields.append("Origin")
        else:
            # Origin is set - check port_lookup_result as fallback to ensure it's not a country
            if port_lookup_result and port_lookup_result.get("origin"):
                origin_result = port_lookup_result.get("origin", {})
                if origin_result.get("is_country", False):
                    if "Origin (specific port required)" not in missing_fields:
                        missing_fields.append("Origin (specific port required)")
        
        # Only flag as missing if destination is EMPTY but destination_country is set (country-only input)
        # If destination is set (even if destination_country is also set), it's a valid port with country info
        if not destination and destination_country:
            # Destination is a country, not a specific port
            missing_fields.append("Destination (specific port required)")
        elif not destination:
            missing_fields.append("Destination")
        else:
            # Destination is set - check port_lookup_result as fallback to ensure it's not a country
            if port_lookup_result and port_lookup_result.get("destination"):
                destination_result = port_lookup_result.get("destination", {})
                if destination_result.get("is_country", False):
                    if "Destination (specific port required)" not in missing_fields:
                        missing_fields.append("Destination (specific port required)")
        
        # CRITICAL: Check extracted shipment_type FIRST (directly extracted from email)
        shipment_type = shipment_details.get("shipment_type", "").strip().upper()
        
        # Handle container_type which might be a string or a dict (from container standardization)
        container_type_raw = shipment_details.get("container_type", "")
        if isinstance(container_type_raw, dict):
            container_type = container_type_raw.get("standardized_type", "") or container_type_raw.get("standard_type", "") or container_type_raw.get("original_input", "")
            container_type = str(container_type).strip() if container_type else ""
        else:
            container_type = str(container_type_raw).strip() if container_type_raw else ""
        
        # CRITICAL: Do NOT assume shipment type - ask for it if missing
        # Only determine shipment type if explicitly mentioned
        is_fcl = None
        
        if shipment_type == "LCL":
            # Shipment type was directly extracted as LCL - use it directly
            is_fcl = False
        elif shipment_type == "FCL":
            # Shipment type was directly extracted as FCL - use it directly
            is_fcl = True
        else:
            # Check special_requirements for explicit LCL/FCL mentions
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
            elif is_explicitly_fcl:
                is_fcl = True
            # CRITICAL: If shipment_type is not explicitly mentioned, do NOT assume - ask for it
            # Do NOT default to FCL based on container_type alone
        
        # Get shipment date from either shipment_details or timeline_information
        timeline_info = extracted_data.get("timeline_information", {})
        shipment_date = (
            shipment_details.get("shipment_date", "").strip() or 
            timeline_info.get("requested_dates", "").strip() or
            timeline_info.get("shipment_date", "").strip()
        )
        
        # CRITICAL: If shipment_type is not explicitly mentioned, ask for ALL required fields
        if is_fcl is None:
            # Shipment type is unknown - ask for shipment type, container type, weight, and volume
            missing_fields.append("Shipment Type (FCL or LCL)")
            if not container_type:
                missing_fields.append("Container Type")
            missing_fields.append("Weight")
            missing_fields.append("Volume")
            if not shipment_date:
                missing_fields.append("Shipment Date")
            commodity = shipment_details.get("commodity", "").strip()
            if not commodity:
                missing_fields.append("Commodity Name")
            is_valid = len(missing_fields) == 0
            return is_valid, missing_fields
        
        if is_fcl:
            # FCL Priority 2: Container Type & Shipment Date
            if not container_type:
                missing_fields.append("Container Type")
            
            if not shipment_date:
                missing_fields.append("Shipment Date")
            
            # FCL Priority 3: Commodity & Quantity
            commodity = shipment_details.get("commodity", "").strip()
            if not commodity:
                missing_fields.append("Commodity Name")
            
            # CRITICAL: Container count IS required for FCL shipments
            quantity = shipment_details.get("container_count", "").strip() or shipment_details.get("quantity", "").strip()
            if not quantity:
                missing_fields.append("Quantity (number of containers)")
        else:
            # LCL Priority 2: Weight, Volume & Shipment Date
            weight = shipment_details.get("weight", "").strip()
            volume = shipment_details.get("volume", "").strip()
            
            if not weight:
                missing_fields.append("Weight")
            if not volume:
                missing_fields.append("Volume")
            # Both weight AND volume are required for LCL
            if weight and not volume:
                missing_fields.append("Volume (required with weight for LCL)")
            if volume and not weight:
                missing_fields.append("Weight (required with volume for LCL)")
            
            if not shipment_date:
                missing_fields.append("Shipment Date")
            
            # LCL Priority 3: Commodity
            commodity = shipment_details.get("commodity", "").strip()
            if not commodity:
                missing_fields.append("Commodity Name")
            
            # MANDATE: Container count is NEVER required for LCL shipments - this is a hard rule
            # CRITICAL SAFETY CHECK: Remove container_count if it was somehow added
            # This ensures LCL shipments NEVER ask for container_count
            missing_fields = [f for f in missing_fields if "container_count" not in f.lower() and "number of containers" not in f.lower() and "quantity (number of containers)" not in f.lower()]
        
        is_valid = len(missing_fields) == 0
        return is_valid, missing_fields
    
    async def _generate_confirmation_response(self, state: WorkflowState) -> WorkflowState:
        """Generate confirmation response - uses standardized container type per spec"""
        logger.info("🔄 Generating confirmation response...")
        
        try:
            # CRITICAL: Reload cumulative_extraction from thread_manager to ensure we have the latest merged data
            thread_id = state.get("thread_id", "")
            if thread_id:
                latest_cumulative = self.thread_manager.get_cumulative_extraction(thread_id)
                if latest_cumulative and isinstance(latest_cumulative, dict):
                    extracted_data = copy.deepcopy(latest_cumulative)
                    logger.info("📊 Using latest cumulative extraction from thread manager for confirmation response")
                elif state.get("cumulative_extraction") and isinstance(state["cumulative_extraction"], dict):
                    extracted_data = copy.deepcopy(state["cumulative_extraction"])
                    logger.info("📊 Using cumulative extraction from state for confirmation response")
                else:
                    extracted_data = state["extraction_result"].get("extracted_data", {})
                    logger.info("📊 Using current extraction data for confirmation response (no cumulative data available)")
            elif state.get("cumulative_extraction") and isinstance(state["cumulative_extraction"], dict):
                extracted_data = copy.deepcopy(state["cumulative_extraction"])
                logger.info("📊 Using cumulative extraction from state for confirmation response")
            else:
                extracted_data = state["extraction_result"].get("extracted_data", {})
                logger.info("📊 Using current extraction data for confirmation response (no cumulative data available)")
            
            rate_info = state["rate_recommendation_result"]
            port_lookup_result = state.get("port_lookup_result", {})
            
            # CRITICAL: Validate Priority 1-3 mandatory fields before generating confirmation
            is_valid, missing_fields = self._validate_mandatory_fields_for_confirmation(
                extracted_data, port_lookup_result
            )
            
            if not is_valid:
                logger.error(f"❌ Cannot generate confirmation - mandatory fields missing: {missing_fields}")
                logger.warning(f"⚠️ Overriding to clarification due to missing mandatory fields")
                # Override to clarification instead of confirmation
                state["confirmation_response_result"] = {
                    "error": f"Cannot generate confirmation - mandatory fields missing: {', '.join(missing_fields)}",
                    "missing_fields": missing_fields,
                    "override_reason": "Mandatory fields (Priority 1-3) are missing"
                }
                # Generate clarification instead
                return await self._generate_clarification_response(state)
            
            # Use standardized container type in extracted_data for display (per spec)
            # The spec says confirmation responses show standardized container types
            # CRITICAL: Only add container_type if shipment_type is NOT LCL
            shipment_type = extracted_data.get("shipment_details", {}).get("shipment_type", "").strip().upper() if extracted_data.get("shipment_details", {}).get("shipment_type") else ""
            
            if shipment_type != "LCL" and state.get("container_standardization_result") and isinstance(state["container_standardization_result"], dict):
                standardized_type = state["container_standardization_result"].get("standardized_type")
                if standardized_type:
                    # Update extracted_data with standardized container type for display (only for FCL)
                    if "shipment_details" in extracted_data:
                        extracted_data["shipment_details"]["container_type"] = standardized_type
            elif shipment_type == "LCL":
                # For LCL shipments, ensure container_type is cleared
                if "shipment_details" in extracted_data:
                    if "container_type" in extracted_data["shipment_details"]:
                        del extracted_data["shipment_details"]["container_type"]
                    if "container_count" in extracted_data["shipment_details"]:
                        del extracted_data["shipment_details"]["container_count"]
            
            result = self.confirmation_agent.process({
                "extracted_data": extracted_data,
                "customer_name": state["email_data"].get("sender_name", "Valued Customer"),  # First name extracted from email
                "agent_info": state["assigned_sales_person"],
                "rate_info": rate_info,
                "container_standardization_result": state.get("container_standardization_result"),  # Pass for reference
                "port_lookup_result": state.get("port_lookup_result")  # For human-friendly port formatting (per spec)
            })
            
            state["confirmation_response_result"] = result
            
            # Print final response on terminal
            print(f"\n{'='*80}")
            print(f"📧 FINAL RESPONSE GENERATED: CONFIRMATION")
            print(f"{'='*80}")
            print(f"📧 Subject: {result.get('subject', 'No subject')}")
            print(f"👤 To: {state['email_data'].get('sender', 'Unknown')}")
            print(f"📝 Response Type: Confirmation Request")
            print(f"\n📄 RESPONSE BODY:")
            print(f"{result.get('body', 'No body')}")
            print(f"{'='*80}")
            
            logger.info(f"✅ Confirmation response generated: {result.get('subject', 'No subject')}")
            
        except Exception as e:
            logger.error(f"❌ Confirmation response generation failed: {e}")
            state["confirmation_response_result"] = {"error": str(e)}
        
        return state
    
    async def _generate_acknowledgment_response(self, state: WorkflowState) -> WorkflowState:
        """Generate acknowledgment response for different sender types"""
        logger.info("🔄 Generating acknowledgment response...")
        
        try:
            # Get sender classification from classification result
            classification_result = state.get("classification_result", {})
            sender_classification = classification_result.get("sender_classification", {})
            sender_type = sender_classification.get("type", "customer")
            sender_details = sender_classification.get("details", {})
            
            # Get email data safely
            email_data = state.get("email_data", {})
            if not email_data:
                logger.error("❌ Email data is missing in acknowledgment generation")
                state["acknowledgment_response_result"] = {"error": "Email data is missing"}
                return state
                
            email_content = email_data.get("content", "")
            sender_email = email_data.get("sender", "")
            
            # Ensure a sales person is assigned for forwarder/sales person emails
            assigned_sales_person = state.get("assigned_sales_person")
            if not assigned_sales_person:
                logger.info("ℹ️ No sales person assigned, assigning one for acknowledgment")
                # Assign a sales person for forwarder/sales person emails
                try:
                    # Check if sales team manager is available
                    if not hasattr(self, 'sales_team_manager') or not self.sales_team_manager:
                        raise Exception("Sales team manager not available")
                        
                    # Use default route info for assignment
                    route_info = {
                        "origin": "",
                        "destination": "",
                        "container_type": "",
                        "commodity": ""
                    }
                    assigned_sales_person = self.sales_team_manager.assign_sales_person(route_info, {})
                    state["assigned_sales_person"] = assigned_sales_person
                    logger.info(f"✅ Sales person assigned for acknowledgment: {assigned_sales_person.get('name', 'Unknown')}")
                    print(f"\n👤 SALES PERSON ASSIGNED FOR ACKNOWLEDGMENT:")
                    print(f"   Name: {assigned_sales_person.get('name', 'Unknown')}")
                    print(f"   Title: {assigned_sales_person.get('title', 'Unknown')}")
                    print(f"   Email: {assigned_sales_person.get('email', 'Unknown')}")
                    print(f"   Phone: {assigned_sales_person.get('phone', 'Unknown')}")
                except Exception as e:
                    logger.error(f"❌ Failed to assign sales person for acknowledgment: {e}")
                    # Use default sales person
                    assigned_sales_person = {
                        "name": "Digital Sales Specialist",
                        "title": "Digital Sales Specialist",
                        "email": "sales@searates.com",
                        "phone": "+1-555-0123",
                        "signature": "Best regards,\n\nDigital Sales Specialist\nSearates By DP World\n📧 sales@searates.com\n📞 +1-555-0123"
                    }
                    state["assigned_sales_person"] = assigned_sales_person
            
            result = self.acknowledgment_agent.process({
                "sender_type": sender_type,
                "sender_email": sender_email,
                "sender_details": sender_details,
                "email_content": email_content,
                "thread_id": state["thread_id"],
                "assigned_sales_person": assigned_sales_person
            })
            
            # Print final response on terminal
            print(f"\n{'='*80}")
            print(f"📧 FINAL RESPONSE GENERATED: {sender_type.upper()} ACKNOWLEDGMENT")
            print(f"{'='*80}")
            print(f"📧 Subject: {result.get('subject', 'No subject')}")
            print(f"👤 To: {sender_email}")
            print(f"📝 Response Type: {sender_type.title()} Acknowledgment")
            print(f"📊 Sender Type: {sender_type}")
            print(f"👤 From: {assigned_sales_person.get('name', 'Unknown')} ({assigned_sales_person.get('email', 'Unknown')})")
            print(f"\n📄 RESPONSE BODY:")
            print(f"{result.get('body', 'No body')}")
            print(f"{'='*80}")
            
            logger.info(f"✅ {sender_type.title()} acknowledgment response generated: {result.get('subject', 'No subject')}")
            
            # Return only the fields we modify (don't include email_data)
            return {
                "acknowledgment_response_result": result
            }
            
        except Exception as e:
            logger.error(f"❌ Acknowledgment response generation failed: {e}")
            # Return only the fields we modify
            return {
                "acknowledgment_response_result": {"error": str(e)}
            }
    
    async def _generate_confirmation_acknowledgment(self, state: WorkflowState) -> WorkflowState:
        """Generate confirmation acknowledgment response - uses standardized container type per spec"""
        logger.info("🔄 Generating confirmation acknowledgment response...")
        
        try:
            # CRITICAL: Reload cumulative_extraction from thread_manager to ensure we have the latest merged data
            thread_id = state.get("thread_id", "")
            if thread_id:
                latest_cumulative = self.thread_manager.get_cumulative_extraction(thread_id)
                if latest_cumulative and isinstance(latest_cumulative, dict):
                    extracted_data = copy.deepcopy(latest_cumulative)
                    logger.info("📊 Using latest cumulative extraction from thread manager for confirmation acknowledgment")
                elif state.get("cumulative_extraction") and isinstance(state["cumulative_extraction"], dict):
                    extracted_data = copy.deepcopy(state["cumulative_extraction"])
                    logger.info("📊 Using cumulative extraction from state for confirmation acknowledgment")
                else:
                    extraction_result = state.get("extraction_result", {})
                    extracted_data = extraction_result.get("extracted_data", {}) if extraction_result else {}
                    logger.info("📊 Using current extraction data for confirmation acknowledgment (no cumulative data available)")
            elif state.get("cumulative_extraction") and isinstance(state["cumulative_extraction"], dict):
                extracted_data = copy.deepcopy(state["cumulative_extraction"])
                logger.info("📊 Using cumulative extraction from state for confirmation acknowledgment")
            else:
                extraction_result = state.get("extraction_result", {})
                extracted_data = extraction_result.get("extracted_data", {}) if extraction_result else {}
                logger.info("📊 Using current extraction data for confirmation acknowledgment (no cumulative data available)")
            
            port_lookup_result = state.get("port_lookup_result", {})
            
            # CRITICAL: Validate Priority 1-3 mandatory fields before generating confirmation acknowledgment
            # Even if customer confirmed, we must validate all mandatory fields are present
            is_valid, missing_fields = self._validate_mandatory_fields_for_confirmation(
                extracted_data, port_lookup_result
            )
            
            if not is_valid:
                logger.error(f"❌ Cannot generate confirmation acknowledgment - mandatory fields missing: {missing_fields}")
                logger.warning(f"⚠️ Customer confirmed but mandatory fields are missing. Overriding to clarification.")
                # Override to clarification instead of confirmation acknowledgment
                state["confirmation_acknowledgment_result"] = {
                    "error": f"Cannot proceed with confirmation acknowledgment - mandatory fields missing: {', '.join(missing_fields)}",
                    "missing_fields": missing_fields,
                    "override_reason": "Customer confirmed but mandatory fields (Priority 1-3) are missing"
                }
                # Generate clarification instead
                return await self._generate_clarification_response(state)
            
            # Use standardized container type in extracted_data for display (per spec)
            # The spec says confirmation acknowledgment shows standardized container types
            # CRITICAL: Only add container_type if shipment_type is NOT LCL
            shipment_type = extracted_data.get("shipment_details", {}).get("shipment_type", "").strip().upper() if extracted_data.get("shipment_details", {}).get("shipment_type") else ""
            
            if shipment_type != "LCL" and state.get("container_standardization_result") and isinstance(state["container_standardization_result"], dict):
                standardized_type = state["container_standardization_result"].get("standardized_type")
                if standardized_type:
                    # Update extracted_data with standardized container type for display (only for FCL)
                    if "shipment_details" in extracted_data:
                        extracted_data["shipment_details"]["container_type"] = standardized_type
            elif shipment_type == "LCL":
                # For LCL shipments, ensure container_type is cleared
                if "shipment_details" in extracted_data:
                    if "container_type" in extracted_data["shipment_details"]:
                        del extracted_data["shipment_details"]["container_type"]
                    if "container_count" in extracted_data["shipment_details"]:
                        del extracted_data["shipment_details"]["container_count"]
            
            # Get email data safely
            email_data = state.get("email_data", {})
            customer_name = email_data.get("sender_name", "Valued Customer") if email_data else "Valued Customer"
            
            result = self.confirmation_acknowledgment_agent.process({
                "extracted_data": extracted_data,
                "customer_name": customer_name,
                "agent_info": state["assigned_sales_person"],
                "tone": "professional",
                "quote_timeline": "24 hours",
                "include_forwarder_info": True,
                "container_standardization_result": state.get("container_standardization_result"),  # Pass for reference
                "port_lookup_result": state.get("port_lookup_result")  # Pass port codes for display
            })
            
            state["confirmation_acknowledgment_result"] = result
            
            # Print final response on terminal
            print(f"\n{'='*80}")
            print(f"📧 FINAL RESPONSE GENERATED: CONFIRMATION ACKNOWLEDGMENT")
            print(f"{'='*80}")
            print(f"📧 Subject: {result.get('subject', 'No subject')}")
            print(f"👤 To: {email_data.get('sender', 'Unknown')}")
            print(f"📝 Response Type: Confirmation Acknowledgment")
            print(f"\n📄 RESPONSE BODY:")
            print(f"{result.get('body', 'No body')}")
            print(f"{'='*80}")
            
            logger.info(f"✅ Confirmation acknowledgment response generated: {result.get('subject', 'No subject')}")
            
        except Exception as e:
            logger.error(f"❌ Confirmation acknowledgment response generation failed: {e}")
            state["confirmation_acknowledgment_result"] = {"error": str(e)}
        
        return state
    
    # Forwarder handling nodes
    async def _detect_forwarder(self, state: WorkflowState) -> WorkflowState:
        """Detect forwarder email"""
        logger.info("🔄 Detecting forwarder...")
        
        try:
            # Get email data safely
            email_data = state.get("email_data", {})
            if not email_data:
                logger.error("❌ Email data is missing in forwarder detection")
                state["forwarder_detection_result"] = {"error": "Email data is missing"}
                state["is_forwarder_email"] = False
                return state
                
            result = self.forwarder_detection_agent.process({
                "email_data": email_data,
                "forwarder_manager": self.forwarder_manager
            })
            
            state["forwarder_detection_result"] = result
            state["is_forwarder_email"] = result.get("is_forwarder", False)
            logger.info(f"✅ Forwarder detection completed: {result.get('forwarder_name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Forwarder detection failed: {e}")
            state["forwarder_detection_result"] = {"error": str(e)}
            state["is_forwarder_email"] = False
        
        return state
    
    async def _process_forwarder_response(self, state: WorkflowState) -> WorkflowState:
        """Process forwarder response"""
        logger.info("🔄 Processing forwarder response...")
        
        try:
            # Get data safely
            email_data = state.get("email_data", {})
            forwarder_info = state.get("forwarder_detection_result", {})
            extraction_result = state.get("extraction_result", {})
            extracted_data = extraction_result.get("extracted_data", {}) if extraction_result else {}
            
            if not email_data:
                logger.error("❌ Email data is missing in forwarder response processing")
                # Return only the field we modify (consistent with success path)
                return {
                    "forwarder_response_result": {"error": "Email data is missing"}
                }
                
            result = self.forwarder_response_agent.process({
                "email_data": email_data,
                "forwarder_info": forwarder_info,
                "extracted_data": extracted_data
            })
            
            # Return only the field we modify (don't include email_data)
            return {
                "forwarder_response_result": result
            }
            
        except Exception as e:
            logger.error(f"❌ Forwarder response processing failed: {e}")
            # Return only the field we modify
            return {
                "forwarder_response_result": {"error": str(e)}
            }
    
    async def _draft_forwarder_email(self, state: WorkflowState) -> WorkflowState:
        """Draft forwarder email"""
        logger.info("🔄 Drafting forwarder email...")
        
        try:
            result = self.forwarder_email_draft_agent.process({
                "forwarder_info": state["forwarder_detection_result"],
                "forwarder_response": state["forwarder_response_result"],
                "customer_context": state["customer_context"]
            })
            
            state["forwarder_email_draft_result"] = result
            logger.info(f"✅ Forwarder email drafted: {result.get('subject', 'No subject')}")
            
        except Exception as e:
            logger.error(f"❌ Forwarder email drafting failed: {e}")
            state["forwarder_email_draft_result"] = {"error": str(e)}
        
        return state
    
    async def _assign_forwarders(self, state: WorkflowState) -> WorkflowState:
        """Assign forwarders and generate rate requests"""
        logger.info("🔄 Assigning forwarders...")
        
        # Add to workflow history
        if "workflow_history" not in state:
            state["workflow_history"] = []
        state["workflow_history"].append("assign_forwarders")
        
        try:
            # Use cumulative extraction data if available (has all merged/validated data), otherwise use current extraction
            cumulative_extraction = state.get("cumulative_extraction", {})
            if cumulative_extraction and cumulative_extraction.get("shipment_details"):
                shipment_details = cumulative_extraction.get("shipment_details", {})
                logger.info("📊 Using cumulative extraction data for forwarder assignment")
            else:
                extracted_data = state["extraction_result"].get("extracted_data", {})
                shipment_details = extracted_data.get("shipment_details", {})
                logger.info("📊 Using current extraction data for forwarder assignment")
            
            enriched_data = {
                "port_lookup": state.get("port_lookup_result", {}),
                "container_standardization": state.get("container_standardization_result", {}),
                "rate_recommendation": state.get("rate_recommendation_result", {})
            }
            
            # Extract origin and destination countries - prioritize extracted country fields
            origin_country = ""
            destination_country = ""
            origin_country = shipment_details.get("origin_country", "").strip()
            destination_country = shipment_details.get("destination_country", "").strip()
            
            # Fallback: Extract from port lookup if country fields are not set
            if not origin_country or not destination_country:
                if state.get("port_lookup_result"):
                    port_lookup = state["port_lookup_result"]
                    if port_lookup and isinstance(port_lookup, dict):
                        if not origin_country and port_lookup.get("origin") and isinstance(port_lookup["origin"], dict):
                            origin_country = port_lookup["origin"].get("country", "")
                        if not destination_country and port_lookup.get("destination") and isinstance(port_lookup["destination"], dict):
                            destination_country = port_lookup["destination"].get("country", "")
            
            # If still no countries, try to extract from origin/destination fields (as last resort)
            if not origin_country:
                origin_country = shipment_details.get("origin", "").strip()
            if not destination_country:
                destination_country = shipment_details.get("destination", "").strip()
            
            # If still no countries, use default values for testing
            if not origin_country:
                origin_country = "China"  # Default origin
            if not destination_country:
                destination_country = "USA"  # Default destination
            
            # Use forwarder manager to assign forwarders
            assigned_forwarder = self.forwarder_manager.assign_forwarder_for_route(origin_country, destination_country)
            
            if assigned_forwarder:
                # Get sales manager ID from assigned sales person
                sales_manager_id = state.get("assigned_sales_person", {}).get("id", "")
                
                # Get customer email content for additional details extraction
                email_data = state.get("email_data", {})
                customer_email_content = email_data.get("content", email_data.get("body_text", email_data.get("body", "")))
                
                # Generate rate request email using forwarder email draft agent
                # Include all confirmed shipment details including port codes
                # Use cumulative extraction to get complete shipment details
                complete_shipment_details = shipment_details.copy() if shipment_details else {}
                
                # Use standardized container type if available
                if state.get("container_standardization_result") and isinstance(state["container_standardization_result"], dict):
                    standardized_type = state["container_standardization_result"].get("standardized_type")
                    if standardized_type:
                        complete_shipment_details["container_type"] = standardized_type
                        logger.info(f"📦 Using standardized container type: {standardized_type}")
                
                # Also include timeline information from cumulative extraction for shipment_date
                if cumulative_extraction and cumulative_extraction.get("timeline_information"):
                    timeline_info = cumulative_extraction.get("timeline_information", {})
                    # Add requested_dates to shipment_details if shipment_date is missing
                    if not complete_shipment_details.get("shipment_date") and timeline_info.get("requested_dates"):
                        complete_shipment_details["shipment_date"] = timeline_info.get("requested_dates")
                        logger.info(f"📅 Added shipment_date from timeline_information: {timeline_info.get('requested_dates')}")
                
                rate_request_data = {
                    "assigned_forwarders": [assigned_forwarder],
                    "shipment_details": complete_shipment_details,  # Use complete shipment details from cumulative extraction
                    "origin_country": origin_country,
                    "destination_country": destination_country,
                    "port_lookup_result": state.get("port_lookup_result", {}),  # Include port codes
                    "thread_id": state["thread_id"],
                    "sales_manager_id": sales_manager_id,
                    "customer_email_content": customer_email_content
                }
                
                rate_request_result = self.forwarder_email_draft_agent.process(rate_request_data)
                
                # Extract the first email draft for display
                rate_request_email = None
                if rate_request_result and not rate_request_result.get('error'):
                    email_drafts = rate_request_result.get('email_drafts', [])
                    if email_drafts:
                        rate_request_email = email_drafts[0]  # Get the first email draft
                
                state["forwarder_assignment_result"] = {
                    "assigned_forwarder": assigned_forwarder,
                    "origin_country": origin_country,
                    "destination_country": destination_country,
                    "rate_request": rate_request_email,  # Use the extracted email
                    "rate_request_full": rate_request_result,  # Keep the full result
                    "assignment_method": "country_based",
                    "status": "success"
                }
                
                # Enhanced terminal logging
                print("\n" + "="*80)
                print("🚚 FORWARDER ASSIGNMENT COMPLETED")
                print("="*80)
                print(f"✅ Forwarder Assigned: {assigned_forwarder.get('name', 'Unknown')}")
                print(f"📧 Forwarder Email: {assigned_forwarder.get('email', 'Unknown')}")
                print(f"🏢 Company: {assigned_forwarder.get('company', 'Unknown')}")
                print(f"🌍 Countries: {assigned_forwarder.get('countries', 'Unknown')}")
                print(f"📊 Route: {origin_country} → {destination_country}")
                print(f"🎯 Assignment Method: Country-based matching")
                
                # Show sales manager information
                if state.get("assigned_sales_person"):
                    sales_person = state["assigned_sales_person"]
                    print(f"👤 Sales Manager: {sales_person.get('name', 'Unknown')}")
                    print(f"📧 Sales Email: {sales_person.get('email', 'Unknown')}")
                    print(f"📞 Sales Phone: {sales_person.get('phone', 'Unknown')}")
                
                if rate_request_email:
                    print("\n📧 RATE REQUEST EMAIL TO FORWARDER:")
                    print("-" * 50)
                    print(f"Subject: {rate_request_email.get('subject', 'Rate Request')}")
                    print(f"To: {assigned_forwarder.get('email', 'Unknown')}")
                    print(f"From: {state.get('assigned_sales_person', {}).get('email', 'sales@logistics-company.com')}")
                    print("\nBody:")
                    print(rate_request_email.get('body', 'No email body generated'))
                    print("-" * 50)
                
                logger.info(f"✅ Forwarder assigned: {assigned_forwarder.get('name', 'Unknown')}")
                logger.info(f"✅ Rate request generated for {origin_country} to {destination_country}")
            else:
                state["forwarder_assignment_result"] = {
                    "assigned_forwarder": None,
                    "origin_country": origin_country,
                    "destination_country": destination_country,
                    "rate_request": None,
                    "assignment_method": "country_based",
                    "status": "no_forwarder_available",
                    "error": "No forwarder available for the specified route"
                }
                
                print("\n" + "="*80)
                print("❌ FORWARDER ASSIGNMENT FAILED")
                print("="*80)
                print(f"🚫 No forwarder available for route: {origin_country} → {destination_country}")
                print("💡 Consider adding forwarders for this route or using random assignment")
                print("="*80)
                
                logger.warning(f"❌ No forwarder available for route: {origin_country} to {destination_country}")
            
        except Exception as e:
            logger.error(f"❌ Forwarder assignment failed: {e}")
            state["forwarder_assignment_result"] = {
                "error": str(e),
                "status": "error"
            }
        
        return state
    
    # Escalation and notification nodes
    async def _check_escalation(self, state: WorkflowState) -> WorkflowState:
        """Check if escalation is needed"""
        logger.info("🔄 Checking escalation...")
        
        # Guard: If escalation_result already exists, don't process again
        if state.get("escalation_result") is not None:
            logger.info("⚠️ Escalation already processed, skipping duplicate call")
            return {}  # Return empty dict to avoid updating state
        
        print("🚨 ESCALATION_DECISION: Starting specialized LLM escalation analysis...")
        
        try:
            # Safely get email_data and ensure it's not None
            email_data_raw = state.get("email_data", {})
            if not email_data_raw:
                logger.error("❌ Email data is missing in escalation check")
                # Return only the fields we modify (don't include email_data)
                return {
                    "escalation_result": {"error": "Email data is missing", "should_escalate": True},
                    "should_escalate": True
                }
            
            # Create a normalized copy (don't modify shared state)
            email_data = email_data_raw.copy()
            if "content" not in email_data and "body_text" in email_data:
                email_data["content"] = email_data["body_text"]
            if "sender" not in email_data and "from_email" in email_data:
                email_data["sender"] = email_data["from_email"]
            
            # Get email content and sender safely
            email_content = email_data.get("content", email_data.get("body_text", email_data.get("body", "")))
            email_sender = email_data.get("sender", email_data.get("from_email", email_data.get("from", "")))
            
            print(f"📧 Email: {email_content[:100] if email_content else 'No content'}...")
            print(f"👤 Sender: {email_sender}")
            print(f"🧵 Thread ID: {state.get('thread_id', 'unknown')}")
            
            result = self.escalation_agent.process({
                "email_data": email_data,
                "classification_result": state.get("classification_result"),
                "conversation_state_result": state.get("conversation_state_result"),
                "extraction_result": state.get("extraction_result"),
                "validation_result": state.get("validation_result")
            })
            
            # Print final response on terminal
            print(f"\n{'='*80}")
            print(f"📧 FINAL RESPONSE GENERATED: ESCALATION")
            print(f"{'='*80}")
            print(f"📧 Subject: {result.get('subject', 'Escalation Required')}")
            print(f"👤 To: Sales Team")
            print(f"📝 Response Type: Escalation")
            print(f"🚨 Escalation Reason: {result.get('escalation_reason', 'Unknown')}")
            print(f"\n📄 RESPONSE BODY:")
            print(f"{result.get('body', 'No body')}")
            print(f"{'='*80}")
            
            logger.info(f"✅ Escalation check completed: {'Escalate' if result.get('should_escalate', False) else 'Continue'}")
            
            # Return only the fields we modify (don't include email_data)
            return {
                "escalation_result": result,
                "should_escalate": result.get("should_escalate", False)
            }
            
        except Exception as e:
            error_msg = f"❌ Escalation check failed: {e}"
            logger.error(error_msg)
            print(f"\n❌ ESCALATION ERROR: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Return only the fields we modify
            return {
                "escalation_result": {"error": str(e), "should_escalate": True},
                "should_escalate": True
            }
    
    async def _notify_sales(self, state: WorkflowState) -> WorkflowState:
        """Notify sales team"""
        logger.info("🔄 Notifying sales team...")
        
        try:
            # Safely get email_data and ensure it's not None
            email_data_raw = state.get("email_data", {})
            if not email_data_raw:
                logger.error("❌ Email data is missing in sales notification")
                # Return only the fields we modify (don't include email_data)
                return {
                    "sales_notification_result": {
                        "error": "Email data is missing",
                        "notification_type": "unknown",
                        "to": "Sales Team",
                        "subject": "Sales Notification",
                        "body": "No body"
                    }
                }
            
            # Create a normalized copy (don't modify shared state)
            email_data = email_data_raw.copy()
            if "content" not in email_data and "body_text" in email_data:
                email_data["content"] = email_data["body_text"]
            if "sender" not in email_data and "from_email" in email_data:
                email_data["sender"] = email_data["from_email"]
            
            # Include forwarder response data if available (for collated email)
            forwarder_response_result = state.get("forwarder_response_result", {})
            cumulative_extraction = state.get("cumulative_extraction", {})
            extraction_result = state.get("extraction_result", {})
            
            # Determine notification type
            notification_type = "rates_received" if forwarder_response_result and not forwarder_response_result.get('error') else "deal_update"
            
            # Extract customer details from cumulative extraction (with proper None checks)
            customer_details = {}
            if cumulative_extraction and isinstance(cumulative_extraction, dict):
                customer_details = cumulative_extraction.get("contact_information", {})
            
            shipment_details = {}
            if cumulative_extraction and isinstance(cumulative_extraction, dict):
                shipment_details = cumulative_extraction.get("shipment_details", {})
            elif extraction_result and isinstance(extraction_result, dict):
                extracted_data = extraction_result.get("extracted_data", {})
                if extracted_data and isinstance(extracted_data, dict):
                    shipment_details = extracted_data.get("shipment_details", {})
            
            # Extract forwarder rates from forwarder_response_result
            forwarder_rates = []
            if forwarder_response_result and not forwarder_response_result.get('error'):
                # Forwarder response agent returns 'extracted_rate_info', not 'rate_info'
                rate_info = forwarder_response_result.get('extracted_rate_info', {}) or forwarder_response_result.get('rate_info', {})
                
                # Only add to forwarder_rates if rate_info has actual rate data
                if rate_info and isinstance(rate_info, dict):
                    # Check if rate_info has any actual rate values (not just None/empty)
                    has_rate_data = any(
                        rate_info.get(key) is not None and str(rate_info.get(key)).strip()
                        for key in ['rates_with_othc', 'rates_with_dthc', 'rates_without_thc', 'rate', 'total_rate']
                    )
                    if has_rate_data:
                        forwarder_rates = [rate_info]
            
            # Get conversation state (with proper None check)
            conversation_state = "unknown"
            conversation_state_result = state.get("conversation_state_result")
            if conversation_state_result and isinstance(conversation_state_result, dict):
                conversation_state = conversation_state_result.get("conversation_stage", "unknown")
            
            # Get forwarder email content if available (the email RECEIVED FROM forwarder)
            forwarder_email_content = ""
            forwarder_email_subject = ""
            forwarder_email_from = ""
            forwarder_email_to = ""
            forwarder_details = {}
            if forwarder_response_result and not forwarder_response_result.get('error'):
                # Get the original forwarder email content from email_data
                forwarder_email_content = (
                    email_data.get("content", "") or 
                    email_data.get("body_text", "") or 
                    email_data.get("body", "") or
                    email_data.get("email_text", "")
                )
                # Get email metadata for complete forwarder email
                forwarder_email_subject = email_data.get("subject", "")
                forwarder_email_from = email_data.get("sender", "") or email_data.get("from_email", "")
                forwarder_email_to = email_data.get("to_email", "") or email_data.get("to", "")
                
                # Format the complete forwarder received email
                if forwarder_email_content:
                    formatted_forwarder_email = f"""
FORWARDER EMAIL RECEIVED:
--------------------------------------------------
Subject: {forwarder_email_subject}
From: {forwarder_email_from}
To: {forwarder_email_to}

Body:
{forwarder_email_content}
--------------------------------------------------
"""
                    forwarder_email_content = formatted_forwarder_email
                # Extract forwarder details from forwarder_response_result
                forwarder_details = {
                    "name": forwarder_response_result.get("forwarder_name", ""),
                    "email": forwarder_response_result.get("forwarder_email", ""),
                    "company": forwarder_response_result.get("forwarder_name", "")  # Use name as company fallback
                }
            
            # Also check forwarder_detection_result for forwarder details
            forwarder_detection_result = state.get("forwarder_detection_result", {})
            if forwarder_detection_result and not forwarder_detection_result.get('error'):
                forwarder_detection_details = forwarder_detection_result.get("forwarder_details", {})
                if forwarder_detection_details:
                    if not forwarder_details.get("name") or forwarder_details.get("name") == "Forwarder":
                        forwarder_details["name"] = forwarder_detection_details.get("name", "")
                    if not forwarder_details.get("email"):
                        forwarder_details["email"] = forwarder_detection_details.get("email", "")
                    if not forwarder_details.get("company"):
                        forwarder_details["company"] = forwarder_detection_details.get("company", forwarder_detection_details.get("name", ""))
            
            # Final fallback: Extract from email sender if still missing
            if not forwarder_details.get("name") or forwarder_details.get("name") == "Forwarder":
                sender_email = email_data.get("sender", "")
                if sender_email:
                    # Extract name from email prefix or domain
                    forwarder_details["name"] = self._extract_name_from_email(sender_email, forwarder_email_content)
                    if not forwarder_details.get("email"):
                        forwarder_details["email"] = sender_email
                    if not forwarder_details.get("company"):
                        forwarder_details["company"] = forwarder_details.get("name", "")
            
            # Get timeline information for urgency calculation
            timeline_info = {}
            if cumulative_extraction and isinstance(cumulative_extraction, dict):
                timeline_info = cumulative_extraction.get("timeline_information", {})
            
            # Get forwarder rate request email if available (from forwarder assignment)
            forwarder_rate_request_email = ""
            forwarder_assignment_result = state.get("forwarder_assignment_result", {})
            if forwarder_assignment_result and not forwarder_assignment_result.get('error'):
                rate_request = forwarder_assignment_result.get("rate_request", {})
                if rate_request and isinstance(rate_request, dict):
                    # Extract the email body, subject, and to/from from the rate request
                    rate_request_body = rate_request.get("body", "")
                    rate_request_subject = rate_request.get("subject", "")
                    rate_request_to = rate_request.get("to", "")
                    rate_request_from = rate_request.get("from", "")
                    
                    # Format the complete rate request email
                    if rate_request_body:
                        forwarder_rate_request_email = f"""
RATE REQUEST EMAIL SENT TO FORWARDER:
--------------------------------------------------
Subject: {rate_request_subject}
To: {rate_request_to}
From: {rate_request_from}

Body:
{rate_request_body}
--------------------------------------------------
"""
            
            result = self.sales_notification_agent.process({
                "notification_type": notification_type,
                "customer_details": customer_details,
                "shipment_details": shipment_details,
                "forwarder_rates": forwarder_rates,
                "forwarder_details": forwarder_details,
                "forwarder_email_content": forwarder_email_content,
                "forwarder_rate_request_email": forwarder_rate_request_email,  # Add rate request email
                "timeline_information": timeline_info,
                "conversation_state": conversation_state,
                "thread_id": state.get("thread_id", ""),
                "urgency": "high" if forwarder_response_result else "medium"
            })
            
            # Print final response on terminal
            print(f"\n{'='*80}")
            print(f"📧 FINAL RESPONSE GENERATED: SALES NOTIFICATION")
            print(f"{'='*80}")
            print(f"📧 Subject: {result.get('subject', 'Sales Notification')}")
            print(f"👤 To: Sales Team")
            print(f"📝 Response Type: Sales Notification")
            print(f"📊 Notification Type: {result.get('notification_type', 'unknown')}")
            print(f"\n📄 RESPONSE BODY:")
            print(f"{result.get('body', 'No body')}")
            print(f"{'='*80}")
            
            logger.info(f"✅ Sales notification sent: {result.get('notification_type', 'unknown')}")
            
            # Return only the fields we modify (don't include email_data)
            return {
                "sales_notification_result": result
            }
            
        except Exception as e:
            logger.error(f"❌ Sales notification failed: {e}")
            # Return only the fields we modify
            return {
                "sales_notification_result": {"error": str(e)}
            }
    
    def _route_after_sales_notification(self, state: WorkflowState) -> str:
        """Route after sales notification - generate customer quote if forwarder rates available"""
        forwarder_response_result = state.get("forwarder_response_result", {})
        if forwarder_response_result and not forwarder_response_result.get('error'):
            rate_info = forwarder_response_result.get('rate_info', {})
            if rate_info:
                return "generate_customer_quote"
        return "update_thread"
    
    async def _generate_customer_quote(self, state: WorkflowState) -> WorkflowState:
        """Generate final customer quote email after forwarder rates are received"""
        logger.info("🔄 Generating customer quote email...")
        
        try:
            # Get customer details
            email_data = state.get("email_data", {})
            customer_name = email_data.get("sender_name", "Valued Customer")
            customer_email = email_data.get("sender", email_data.get("from_email", ""))
            
            # Get shipment details
            cumulative_extraction = state.get("cumulative_extraction", {})
            shipment_details = cumulative_extraction.get("shipment_details", {}) if cumulative_extraction else {}
            
            # Get forwarder rates
            forwarder_response_result = state.get("forwarder_response_result", {})
            rate_info = forwarder_response_result.get('rate_info', {}) if forwarder_response_result else {}
            
            # Get port lookup result for formatting
            port_lookup_result = state.get("port_lookup_result", {})
            
            # Get assigned sales person
            assigned_sales_person = state.get("assigned_sales_person", {})
            
            # Build quote body with rates
            origin = shipment_details.get('origin', 'N/A')
            destination = shipment_details.get('destination', 'N/A')
            
            # Format ports with codes if available
            if port_lookup_result:
                origin_result = port_lookup_result.get("origin", {})
                dest_result = port_lookup_result.get("destination", {})
                if origin_result:
                    origin = f"{origin_result.get('port_name', origin)} ({origin_result.get('port_code', '')})"
                if dest_result:
                    destination = f"{dest_result.get('port_name', destination)} ({dest_result.get('port_code', '')})"
            
            quote_subject = f"Shipping Quote - {origin} to {destination}"
            
            quote_body = f"""Dear {customer_name},

Thank you for your patience. I'm pleased to provide you with the shipping quote for your shipment.

**Shipment Details:**
• Origin: {origin}
• Destination: {destination}
• Container Type: {shipment_details.get('container_type', 'N/A')}
• Number of Containers: {shipment_details.get('container_count', 'N/A')}
"""
            
            if shipment_details.get('commodity'):
                quote_body += f"• Commodity: {shipment_details.get('commodity')}\n"
            if shipment_details.get('weight'):
                quote_body += f"• Weight: {shipment_details.get('weight')}\n"
            if shipment_details.get('volume'):
                quote_body += f"• Volume: {shipment_details.get('volume')}\n"
            if shipment_details.get('shipment_date'):
                quote_body += f"• Ready Date: {shipment_details.get('shipment_date')}\n"
            if shipment_details.get('incoterm'):
                quote_body += f"• Incoterm: {shipment_details.get('incoterm')}\n"
            
            quote_body += "\n**Rate Information:**\n"
            if rate_info:
                quote_body += f"• Rate: {rate_info.get('rate', 'N/A')} {rate_info.get('currency', 'USD')}\n"
                if rate_info.get('rate_with_othc'):
                    quote_body += f"• Rate with Origin THC: {rate_info.get('rate_with_othc')} {rate_info.get('currency', 'USD')}\n"
                if rate_info.get('transit_time'):
                    quote_body += f"• Transit Time: {rate_info.get('transit_time')} days\n"
                if rate_info.get('valid_until'):
                    quote_body += f"• Valid Until: {rate_info.get('valid_until')}\n"
                if rate_info.get('sailing_date'):
                    quote_body += f"• Sailing Date: {rate_info.get('sailing_date')}\n"
            else:
                quote_body += "• Rate information will be provided shortly.\n"
            
            quote_body += f"""
Please review the quote above and let me know if you'd like to proceed with the booking.

Best regards,
{assigned_sales_person.get('name', 'Sales Team')}
{assigned_sales_person.get('title', 'Account Executive')}
{assigned_sales_person.get('email', 'sales@searates.com')}
{assigned_sales_person.get('phone', '+1-555-0101')}
"""
            
            customer_quote_result = {
                "response_type": "customer_quote",
                "subject": quote_subject,
                "body": quote_body,
                "to": customer_email,
                "from": assigned_sales_person.get('email', 'sales@searates.com'),
                "rate_info": rate_info,
                "shipment_details": shipment_details
            }
            
            logger.info(f"✅ Customer quote generated for {customer_email}")
            
            # Return only the field we modify
            return {
                "customer_quote_result": customer_quote_result
            }
            
        except Exception as e:
            logger.error(f"❌ Customer quote generation failed: {e}")
            return {
                "customer_quote_result": {"error": str(e)}
            }
    
    # Thread management
    async def _update_thread(self, state: WorkflowState) -> WorkflowState:
        """Update thread with current email and results"""
        logger.info("🔄 Updating thread...")
        
        try:
            # Create email entry for customer email
            next_action_result = state.get("next_action_result", {})
            extraction_result = state.get("extraction_result", {})
            
            # Get email data safely
            email_data = state.get("email_data", {})
            if not email_data:
                logger.error("❌ Email data is missing in _update_thread")
                state["workflow_completed"] = True
                return state
            
            # Normalize email data structure
            email_content = email_data.get("content", email_data.get("body_text", email_data.get("body", "")))
            email_sender = email_data.get("sender", email_data.get("from_email", email_data.get("from", "unknown")))
            email_subject = email_data.get("subject", "No Subject")
            
            customer_email_entry = EmailEntry(
                timestamp=state["timestamp"],
                email_id=state["workflow_id"],
                sender=email_sender,
                direction="inbound",
                subject=email_subject,
                content=email_content,
                extracted_data=extraction_result.get("extracted_data", {}) if extraction_result else {},
                response_type=next_action_result.get("action", "unknown") if next_action_result else "unknown",
                workflow_id=state["workflow_id"]
            )
            
            # Add customer email to thread
            thread_id = state.get("thread_id", "")
            if not thread_id:
                logger.error("❌ Thread ID is missing in _update_thread")
                state["workflow_completed"] = True
                return state
                
            try:
                thread_data = self.thread_manager.add_email_to_thread(
                    thread_id, customer_email_entry
                )
                if not thread_data:
                    logger.warning("⚠️ Thread manager returned None, creating fallback thread data")
                    # Create a fallback thread data structure
                    thread_data = type('ThreadData', (), {
                        'cumulative_extraction': {},
                        'total_emails': 1
                    })()
            except Exception as thread_error:
                logger.error(f"❌ Thread manager error: {thread_error}")
                # Create a fallback thread data structure
                thread_data = type('ThreadData', (), {
                    'cumulative_extraction': {},
                    'total_emails': 1
                })()
            
            # Create bot response entry if response was generated
            response_result = None
            if state.get("clarification_response_result"):
                response_result = state["clarification_response_result"]
            elif state.get("confirmation_response_result"):
                response_result = state["confirmation_response_result"]
            elif state.get("acknowledgment_response_result"):
                response_result = state["acknowledgment_response_result"]
            elif state.get("confirmation_acknowledgment_result"):
                response_result = state["confirmation_acknowledgment_result"]
            elif state.get("customer_quote_result"):
                response_result = state["customer_quote_result"]
            elif state.get("forwarder_assignment_result"):
                # For forwarder assignment, we don't create a bot response entry
                # as it's an internal process
                response_result = None
            
            if response_result:
                bot_email_entry = EmailEntry(
                    timestamp=state["timestamp"],
                    email_id=f"bot_{state['workflow_id']}",
                    sender="bot@logistics-company.com",
                    direction="outbound",
                    subject=response_result.get("subject", "Response"),
                    content=response_result.get("body", ""),
                    extracted_data={},
                    response_type=response_result.get("response_type", "unknown"),
                    bot_response=response_result,
                    workflow_id=state["workflow_id"]
                )
                
                # Add bot response to thread
                try:
                    thread_data = self.thread_manager.add_email_to_thread(
                        thread_id, bot_email_entry
                    )
                    if not thread_data:
                        logger.warning("⚠️ Thread manager returned None for bot response, using existing thread data")
                except Exception as bot_thread_error:
                    logger.error(f"❌ Thread manager error for bot response: {bot_thread_error}")
                    # Continue with existing thread_data if available
            
            # Update cumulative extraction
            if thread_data and hasattr(thread_data, 'cumulative_extraction'):
                state["cumulative_extraction"] = thread_data.cumulative_extraction
                logger.info(f"✅ Thread updated: {thread_data.total_emails} emails in thread")
            else:
                logger.warning("⚠️ Thread data not available, using empty cumulative extraction")
                state["cumulative_extraction"] = {}
                
            # Ensure thread_data is always defined for safety
            if not thread_data:
                logger.warning("⚠️ Creating fallback thread data")
                thread_data = type('ThreadData', (), {
                    'cumulative_extraction': {},
                    'total_emails': 1
                })()
            
            # Ensure workflow_completed is set
            state["workflow_completed"] = True
            logger.info("✅ Workflow completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Thread update failed: {e}")
        
        state["workflow_completed"] = True
        return state
    
    # Routing methods
    def _route_after_classification(self, state: WorkflowState) -> str:
        """Route after email classification - Happy flow only, no escalation"""
        classification_result = state.get("classification_result", {})
        email_type = classification_result.get("email_type", "unknown")
        sender_type = classification_result.get("sender_type", "unknown")
        sender_classification = classification_result.get("sender_classification", {})
        sender_classification_type = sender_classification.get("type", "customer")
        
        print(f"🔄 ROUTING: Email type = {email_type}, Sender type = {sender_type}, Sender Classification = {sender_classification_type}")
        
        # Route based on sender classification first (most reliable)
        if sender_classification_type == "sales_person":
            print(f"📧 Sales person email detected - routing to acknowledgment")
            return "generate_acknowledgment_response"
        elif sender_classification_type == "forwarder":
            print(f"📧 Forwarder email detected - routing to acknowledgment")
            return "generate_acknowledgment_response"
        elif "customer" in email_type or sender_type == "customer" or sender_classification_type == "customer":
            # Happy flow: Customer emails go to conversation_state for processing
            return "conversation_state"
        elif "forwarder" in email_type or sender_type == "forwarder":
            # Forwarder emails also go through conversation_state
            return "conversation_state"
        else:
            # REMOVED: Escalation routing - default to conversation_state for happy flow
            # Previously: return "check_escalation"
            # Now: Always continue with normal flow
            print(f"📧 Default routing to conversation_state (happy flow)")
            return "conversation_state"
    
    def _route_after_conversation_state(self, state: WorkflowState) -> str:
        """Route after conversation state analysis - Happy flow only, no escalation"""
        # REMOVED: Escalation check - always continue to analyze_thread for happy flow
        # Previously: if state["should_escalate"]: return "escalate"
        # Now: Always continue with normal processing flow
        return "continue"  # Maps to "analyze_thread" in conditional edges
    
    def _route_after_next_action(self, state: WorkflowState) -> str:
        """Route after next action determination - Happy flow only, no escalation"""
        next_action_result = state.get("next_action_result", {})
        # REMOVED: Default to "escalate" - now default to "send_confirmation_request" for happy flow
        # Previously: action = next_action_result.get("next_action", next_action_result.get("action", "escalate"))
        action = next_action_result.get("next_action", next_action_result.get("action", "send_confirmation_request"))
        
        print(f"🔄 NEXT ACTION ROUTING: Action = {action}")
        
        # All response generation paths go through sales person assignment first
        if action in ["send_clarification_request", "clarification", "send_confirmation_request", "confirmation", "send_acknowledgment", "acknowledgment"]:
            return "assign_sales_person"
        elif action == "assign_forwarder" or action == "forwarder":
            return "detect_forwarder"
        else:
            # REMOVED: Escalation routing - default to assign_sales_person for happy flow
            # Previously: return "check_escalation"
            # Now: Default to sales person assignment to continue normal flow
            print(f"📧 Default routing to assign_sales_person (happy flow)")
            return "assign_sales_person"
    
    def _route_after_sales_assignment(self, state: WorkflowState) -> str:
        """Intelligent routing based on missing fields, confidence, and data quality"""
        next_action_result = state.get("next_action_result", {})
        action = next_action_result.get("next_action", next_action_result.get("action", "escalate"))
        
        # Get confidence scores
        classification_confidence = state.get("classification_result", {}).get("confidence", 0.0)
        extraction_confidence = state.get("extraction_result", {}).get("confidence", 0.0)
        validation_confidence = state.get("validation_result", {}).get("confidence", 0.0)
        
        # CRITICAL: Validate mandatory fields directly in routing to ensure accuracy
        # This is the source of truth - don't rely only on next_action_result
        # Use cumulative_extraction which has merged data including special_requirements
        extracted_data = state.get("cumulative_extraction", {})
        if not extracted_data:
            # Fallback to extraction_result if cumulative_extraction is not available
            extracted_data = state.get("extraction_result", {}).get("extracted_data", {})
        port_lookup_result = state.get("port_lookup_result", {})
        
        # Validate mandatory fields using the same validation function
        is_valid, validated_missing_fields = self._validate_mandatory_fields_for_confirmation(
            extracted_data, port_lookup_result
        )
        
        # PRIORITY: Use validated missing fields as the source of truth
        # Only fall back to next_action_result if validation didn't find any missing fields
        if validated_missing_fields and len(validated_missing_fields) > 0:
            missing_fields = validated_missing_fields
            logger.info(f"🔍 Routing: Using validated missing fields: {missing_fields}")
        else:
            # Fallback: Get missing fields from next action result
            missing_fields = next_action_result.get("missing_fields", [])
        if not missing_fields:
                # If missing_fields is not in next_action_result, try to get it from the state
            missing_fields = state.get("missing_fields", [])
        
        # Also check if missing fields were determined in the next action step
        if not missing_fields and "next_action_result" in state:
            # Try to extract missing fields from the reasoning or other fields
            reasoning = next_action_result.get("reasoning", "")
            if "missing fields" in reasoning.lower():
                # Extract missing fields from reasoning if available
                import re
                missing_matches = re.findall(r"missing fields? such as ([^.]+)", reasoning.lower())
                if missing_matches:
                    missing_fields = [field.strip() for field in missing_matches[0].split(",")]
        
        # Calculate overall confidence (average of all confidence scores)
        overall_confidence = (classification_confidence + extraction_confidence + validation_confidence) / 3
        
        # Check for customer confirmation
        conversation_state = state.get("conversation_state_result", {}).get("conversation_state", "")
        email_classification = state.get("classification_result", {})
        email_type = email_classification.get("email_type", "").lower()
        
        # Check if customer has confirmed details
        customer_confirmed = (
            "confirmation" in conversation_state.lower() or 
            "confirmed" in conversation_state.lower() or
            email_type == "customer_confirmation" or
            "confirmation" in email_type or
            "confirmed" in email_type
        )
        
        print(f"🔄 INTELLIGENT ROUTING ANALYSIS:")
        print(f"   Action from next_action_agent: {action}")
        print(f"   Missing fields: {missing_fields}")
        print(f"   Classification confidence: {classification_confidence:.2f}")
        print(f"   Extraction confidence: {extraction_confidence:.2f}")
        print(f"   Validation confidence: {validation_confidence:.2f}")
        print(f"   Overall confidence: {overall_confidence:.2f}")
        print(f"   Customer confirmed: {customer_confirmed}")
        print(f"   Conversation state: {conversation_state}")
        print(f"   Email type: {email_type}")
        
        # Define confidence thresholds
        HIGH_CONFIDENCE_THRESHOLD = 0.7
        LOW_CONFIDENCE_THRESHOLD = 0.5
        
        # PRIORITY ORDER (as per user requirement):
        # 1. Clarification response (if missing fields)
        # 2. Confirmation request (if all fields complete but not confirmed)
        # 3. Confirmation acknowledgment (if customer confirmed and all fields complete)
        
        # PRIORITY 1: Check for missing fields FIRST - send clarification if any missing
        if missing_fields and len(missing_fields) > 0:
            print(f"   ❌ MISSING FIELDS DETECTED: {missing_fields}")
            print(f"   📧 PRIORITY 1: Sending clarification request")
            return "generate_clarification_response"
        
        # PRIORITY 2: If all fields complete but customer hasn't confirmed - send confirmation request
        if not customer_confirmed:
            print(f"   ✅ NO MISSING FIELDS: All information is complete")
            print(f"   📧 PRIORITY 2: Sending confirmation request (customer not yet confirmed)")
            return "generate_confirmation_response"
        
        # PRIORITY 3: Customer confirmed AND all fields complete - send confirmation acknowledgment
        # This will trigger forwarder assignment if successful
        if customer_confirmed:
            print(f"   ✅ CUSTOMER CONFIRMATION DETECTED + ALL FIELDS COMPLETE")
            print(f"   📧 PRIORITY 3: Sending confirmation acknowledgment")
            return "generate_confirmation_acknowledgment"
        
        # Fallback: Low confidence or unclear state - send clarification
        if overall_confidence < LOW_CONFIDENCE_THRESHOLD:
            print(f"   ⚠️ LOW CONFIDENCE DETECTED: {overall_confidence:.2f} < {LOW_CONFIDENCE_THRESHOLD}")
            print(f"   📧 FALLBACK: Sending clarification request")
            return "generate_clarification_response"
        
        # Final fallback: clarification
        print(f"   📧 FINAL FALLBACK: Sending clarification request")
        return "generate_clarification_response"
    
    def _route_after_acknowledgment(self, state: WorkflowState) -> str:
        """Route after acknowledgment response - Happy flow only, no escalation"""
        # REMOVED: Escalation check - always proceed to thread update for happy flow
        # Previously: if should_escalate: return "check_escalation"
        # Now: Always continue to thread update
        
        # For forwarder emails, process the response and notify sales
        classification_result = state.get("classification_result", {})
        sender_classification = classification_result.get("sender_classification", {})
        sender_type = sender_classification.get("type", "customer")
        email_type = classification_result.get("email_type", "")
        
        if sender_type == "forwarder" or email_type == "forwarder_response":
            print(f"🔄 Forwarder email detected - processing response and notifying sales")
            # Process forwarder response first, then notify sales
            return "process_forwarder_response"
        
        if sender_type == "sales_person":
            print(f"🔄 Sales person email - proceeding to thread update")
            return "update_thread"
        
        print(f"🔄 ACKNOWLEDGMENT ROUTING: Proceeding to thread update (happy flow)")
        return "update_thread"
    
    def _extract_name_from_email(self, sender_email: str, email_content: str = "") -> str:
        """Extract forwarder/company name from email sender or content."""
        import re
        
        # Try to extract from email content signature
        if email_content:
            signature_patterns = [
                r"best\s+regards,?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                r"sincerely,?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                r"regards,?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            ]
            
            for pattern in signature_patterns:
                matches = re.findall(pattern, email_content, re.IGNORECASE | re.MULTILINE)
                if matches:
                    name = matches[-1].strip()
                    if len(name.split()) <= 3 and len(name) > 2:
                        return name
        
        # Extract from sender email (before @)
        if sender_email and "@" in sender_email:
            email_prefix = sender_email.split("@")[0]
            # Remove common prefixes
            email_prefix = re.sub(r'^(info|contact|sales|quotes|rates|support|hello|hi)', '', email_prefix, flags=re.IGNORECASE)
            email_prefix = email_prefix.replace('.', ' ').replace('_', ' ').replace('-', ' ')
            # Capitalize words
            name_parts = [word.capitalize() for word in email_prefix.split() if word]
            if name_parts and len(name_parts) <= 3:
                return ' '.join(name_parts)
            
            # Fallback: extract domain name
            domain = sender_email.split("@")[1]
            domain_parts = domain.split(".")[0].replace('-', ' ').replace('_', ' ')
            name_parts = [word.capitalize() for word in domain_parts.split() if word]
            if name_parts:
                return ' '.join(name_parts)
        
        return "Forwarder"  # Final fallback
    
    def _route_after_confirmation_acknowledgment(self, state: WorkflowState) -> str:
        """Route after confirmation acknowledgment - proceed with forwarder assignment only if successful"""
        confirmation_ack_result = state.get("confirmation_acknowledgment_result", {})
        clarification_result = state.get("clarification_response_result", {})
        
        # CRITICAL: If clarification was generated (because confirmation acknowledgment failed),
        # do NOT assign forwarders - just update thread
        if clarification_result and not clarification_result.get('error'):
            print(f"🔄 CONFIRMATION ACKNOWLEDGMENT ROUTING: Clarification was generated instead, skipping forwarder assignment")
            return "update_thread"
        
        # Check if confirmation acknowledgment was successful (no error)
        if confirmation_ack_result and not confirmation_ack_result.get('error'):
            print(f"🔄 CONFIRMATION ACKNOWLEDGMENT ROUTING: Proceeding with forwarder assignment")
            return "assign_forwarders"
        else:
            # If there was an error (e.g., missing mandatory fields), clarification was generated instead
            # Don't assign forwarders - just update thread
            print(f"🔄 CONFIRMATION ACKNOWLEDGMENT ROUTING: Error detected, skipping forwarder assignment (clarification was generated)")
            return "update_thread"
    
    async def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email through the complete workflow"""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Normalize email data structure - handle both Streamlit format and standard format
        # Create a copy to avoid modifying the original input
        normalized_email_data = email_data.copy() if email_data else {}
        
        if normalized_email_data:
            # Map body_text -> content if content doesn't exist
            if "content" not in normalized_email_data and "body_text" in normalized_email_data:
                normalized_email_data["content"] = normalized_email_data["body_text"]
            # Map from_email -> sender if sender doesn't exist
            if "sender" not in normalized_email_data and "from_email" in normalized_email_data:
                normalized_email_data["sender"] = normalized_email_data["from_email"]
            # Ensure content exists (use body_text as fallback)
            if "content" not in normalized_email_data:
                normalized_email_data["content"] = normalized_email_data.get("body_text", normalized_email_data.get("body", ""))
            # Ensure sender exists (use from_email as fallback)
            if "sender" not in normalized_email_data:
                normalized_email_data["sender"] = normalized_email_data.get("from_email", normalized_email_data.get("from", "unknown"))
        
        # Generate consistent thread ID - use provided thread_id or create one with current timestamp
        thread_id = normalized_email_data.get("thread_id")
        if not thread_id:
            # Default to timestamp-based thread ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            thread_id = f"thread_{timestamp}"
        
        # Extract sender email for logging
        sender_email = normalized_email_data.get("sender", normalized_email_data.get("from_email", "unknown"))
        
        # Extract first name from email data (per Rule IV: "Dear <FirstName>," not "Dear Valued Customer,")
        sender_name = extract_name_from_email_data(normalized_email_data)
        normalized_email_data["sender_name"] = sender_name
        logger.info(f"👤 Extracted sender name: {sender_name} from email: {sender_email}")
        
        logger.info(f"🚀 Starting workflow {workflow_id} for thread {thread_id}")
        
        # Initialize state with normalized email_data
        initial_state = WorkflowState(
            email_data=normalized_email_data,
            thread_history=[],
            classification_result=None,
            conversation_state_result=None,
            thread_analysis_result=None,
            extraction_result=None,
            validation_result=None,
            port_lookup_result=None,
            container_standardization_result=None,
            rate_recommendation_result=None,
            next_action_result=None,
            clarification_response_result=None,
            confirmation_response_result=None,
            acknowledgment_response_result=None,
            confirmation_acknowledgment_result=None,
            forwarder_detection_result=None,
            forwarder_response_result=None,
            forwarder_email_draft_result=None,
            forwarder_assignment_result=None,
            escalation_result=None,
            sales_notification_result=None,
            customer_context={},
            forwarder_context={},
            market_data={},
            historical_data={},
            should_escalate=False,
            is_forwarder_email=False,
            workflow_completed=False,
            thread_id=thread_id,
            cumulative_extraction={},
            workflow_id=workflow_id,
            timestamp=datetime.now().isoformat(),
            assigned_sales_person=None,
            workflow_history=[]
        )
        
        try:
            # Load existing thread data
            existing_thread = self.thread_manager.load_thread(thread_id)
            if existing_thread:
                try:
                    # Safely convert email chain to dictionaries
                    email_history = []
                    if hasattr(existing_thread, 'email_chain') and existing_thread.email_chain:
                        for email in existing_thread.email_chain:
                            if email is not None:
                                try:
                                    email_dict = asdict(email)
                                    email_history.append(email_dict)
                                except Exception as email_error:
                                    logger.warning(f"⚠️ Failed to convert email to dict: {email_error}")
                                    # Create a fallback email dict
                                    email_history.append({
                                        "timestamp": datetime.now().isoformat(),
                                        "email_id": "unknown",
                                        "sender": "unknown",
                                        "direction": "inbound",
                                        "subject": "Unknown",
                                        "content": "Unknown",
                                        "extracted_data": {},
                                        "response_type": "unknown",
                                        "workflow_id": "unknown"
                                    })
                    
                    initial_state["thread_history"] = email_history
                    initial_state["cumulative_extraction"] = getattr(existing_thread, 'cumulative_extraction', {})
                    initial_state["customer_context"] = getattr(existing_thread, 'customer_context', {})
                    initial_state["forwarder_context"] = getattr(existing_thread, 'forwarder_context', {})
                    logger.info(f"📧 Loaded existing thread with {len(initial_state['thread_history'])} emails")
                except Exception as thread_load_error:
                    logger.error(f"❌ Failed to load thread data: {thread_load_error}")
                    # Use empty defaults
                    initial_state["thread_history"] = []
                    initial_state["cumulative_extraction"] = {}
                    initial_state["customer_context"] = {}
                    initial_state["forwarder_context"] = {}
            
            # Run workflow
            result = await self.workflow.ainvoke(initial_state)
            
            logger.info(f"✅ Workflow {workflow_id} completed successfully")
            return {
                "workflow_id": workflow_id,
                "thread_id": thread_id,
                "status": "completed",
                "result": result
            }
            
        except Exception as e:
            logger.error(f"❌ Workflow {workflow_id} failed: {e}")
            
            # Try to return partial results if available
            try:
                # Check if we have any partial results in the initial_state
                partial_result = {}
                
                # Add any available data from initial_state
                if initial_state.get("classification_result"):
                    partial_result["classification_result"] = initial_state["classification_result"]
                if initial_state.get("acknowledgment_response_result"):
                    partial_result["acknowledgment_response_result"] = initial_state["acknowledgment_response_result"]
                if initial_state.get("assigned_sales_person"):
                    partial_result["assigned_sales_person"] = initial_state["assigned_sales_person"]
                if initial_state.get("workflow_history"):
                    partial_result["workflow_history"] = initial_state["workflow_history"]
                if initial_state.get("email_data"):
                    partial_result["email_data"] = initial_state["email_data"]
                
                return {
                    "workflow_id": workflow_id,
                    "thread_id": thread_id,
                    "status": "failed",
                    "error": str(e),
                    "result": partial_result if partial_result else None
                }
            except Exception as partial_error:
                logger.error(f"❌ Failed to extract partial results: {partial_error}")
                return {
                    "workflow_id": workflow_id,
                    "thread_id": thread_id,
                    "status": "failed",
                    "error": str(e)
                }


# =====================================================
#                 🧪 Test Functions
# =====================================================

async def test_langgraph_workflow():
    """Test the LangGraph workflow orchestrator"""
    print("🧪 Testing LangGraph Workflow Orchestrator")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = LangGraphWorkflowOrchestrator()
    
    # Test customer email
    test_email = {
        "email_text": """Hi, I need shipping rates for the following shipment:
        
Origin: Shanghai, China
Destination: Los Angeles, USA
Container Type: 40HC
Weight: 15,000 kg
Volume: 68 CBM

Please provide rates and transit time.

Best regards,
John Smith""",
        "subject": "Shipping Quote Request - Shanghai to Los Angeles",
        "sender": "john.smith@techsolutions.com",
        "thread_id": "thread_123"
    }
    
    print(f"\n📧 Processing Test Email:")
    print(f"   Subject: {test_email['subject']}")
    print(f"   Sender: {test_email['sender']}")
    
    # Process email through LangGraph workflow
    print("\n🔄 Processing email through LangGraph workflow...")
    try:
        result = await orchestrator.process_email(
            email_data=test_email,
            customer_context={
                "priority": "high",
                "customer_info": {
                    "name": "John Smith",
                    "company": "Tech Solutions Inc."
                }
            },
            forwarder_context={},
            market_data={},
            historical_data=[]
        )
        
        print("✅ LangGraph workflow processing completed!")
        
        # Display results
        print(f"\n📊 Workflow Results Summary:")
        print(f"   Status: {result.get('status', 'Unknown')}")
        print(f"   Outcome: {result.get('workflow_outcome', 'Unknown')}")
        print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ LangGraph workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_langgraph_workflow())
    print(f"\n🎉 LangGraph workflow test {'passed' if success else 'failed'}!") 