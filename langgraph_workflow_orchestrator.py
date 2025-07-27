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

logger = get_logger(__name__)

class WorkflowState(TypedDict):
    """Enhanced workflow state with all necessary fields"""
    # Email data
    email_data: Annotated[Dict[str, Any], "shared"]
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
    
    # Forwarder handling
    forwarder_detection_result: Optional[Dict[str, Any]]
    forwarder_response_result: Optional[Dict[str, Any]]
    forwarder_email_draft_result: Optional[Dict[str, Any]]
    forwarder_assignment_result: Optional[Dict[str, Any]]
    
    # Escalation and notifications
    escalation_result: Optional[Dict[str, Any]]
    sales_notification_result: Optional[Dict[str, Any]]
    
    # Context and metadata
    customer_context: Annotated[Dict[str, Any], "shared"]
    forwarder_context: Annotated[Dict[str, Any], "shared"]
    market_data: Annotated[Dict[str, Any], "shared"]
    historical_data: Annotated[Dict[str, Any], "shared"]
    
    # Decision flags
    should_escalate: bool
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
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "classify_email",
            self._route_after_classification,
            {
                "check_escalation": "check_escalation",
                "conversation_state": "conversation_state",
                "generate_acknowledgment_response": "generate_acknowledgment_response",
                "notify_sales": "notify_sales"
            }
        )
        
        workflow.add_conditional_edges(
            "conversation_state",
            self._route_after_conversation_state,
            {
                "escalate": "check_escalation",
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
                "check_escalation": "check_escalation"
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
                "check_escalation": "check_escalation"
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
        
        # Acknowledgment response can trigger escalation if confidence is low
        workflow.add_conditional_edges(
            "generate_acknowledgment_response",
            self._route_after_acknowledgment,
            {
                "check_escalation": "check_escalation",
                "update_thread": "update_thread"
            }
        )
        
        # Forwarder handling edges
        workflow.add_edge("detect_forwarder", "process_forwarder_response")
        workflow.add_edge("process_forwarder_response", "draft_forwarder_email")
        workflow.add_edge("draft_forwarder_email", "update_thread")
        
        # Escalation edges
        workflow.add_edge("check_escalation", "notify_sales")
        workflow.add_edge("notify_sales", "update_thread")
        
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
        
        content = email_data.get('content', '')
        subject = email_data.get('subject', '')
        sender = email_data.get('sender', '')
        
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
            content = email_data.get('content', '')
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
            # Prepare email_data in the format expected by thread analyzer
            email_data = {
                "email_text": state["email_data"]["content"],
                "subject": state["email_data"]["subject"],
                "sender": state["email_data"]["sender"],
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
        print(f"📧 Email Content Length: {len(state['email_data']['content'])} characters")
        print(f"🧵 Thread History: {len(state['thread_history'])} previous emails")
        print(f"📊 Cumulative Extraction: {len(state['cumulative_extraction'])} existing items")
        
        try:
            result = self.extraction_agent.process({
                "email_text": state["email_data"]["content"],
                "sender": state["email_data"]["sender"],
                "subject": state["email_data"]["subject"],
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
            
            result = self.container_standardization_agent.process({
                "container_type": shipment_details.get("container_type"),
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
            # Determine missing fields first using the clarification agent's logic
            extracted_data = state["extraction_result"].get("extracted_data", {})
            missing_fields = self.clarification_agent._determine_missing_fields(extracted_data)
            
            print(f"📋 Missing Fields: {missing_fields}")
            
            result = self.next_action_agent.process({
                "conversation_state": state["conversation_state_result"].get("conversation_stage", "unknown"),
                "email_classification": state["classification_result"],
                "extracted_data": state["extraction_result"].get("extracted_data", {}),
                "confidence_score": state["extraction_result"].get("confidence", 0.0),
                "validation_results": state["validation_result"],
                "enriched_data": state["rate_recommendation_result"],
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
        """Generate clarification response"""
        logger.info("🔄 Generating clarification response...")
        
        try:
            extracted_data = state["extraction_result"].get("extracted_data", {})
            # Let the clarification agent determine missing fields instead of using validation result
            missing_fields = []  # Will be determined by clarification agent
            
            result = self.clarification_agent.process({
                "extracted_data": extracted_data,
                "missing_fields": missing_fields,  # Empty list - agent will determine missing fields
                "customer_name": state["email_data"].get("sender_name", "Valued Customer"),
                "agent_info": state["assigned_sales_person"],
                "port_lookup_result": state["port_lookup_result"]
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
    
    async def _generate_confirmation_response(self, state: WorkflowState) -> WorkflowState:
        """Generate confirmation response"""
        logger.info("🔄 Generating confirmation response...")
        
        try:
            extracted_data = state["extraction_result"].get("extracted_data", {})
            rate_info = state["rate_recommendation_result"]
            
            result = self.confirmation_agent.process({
                "extracted_data": extracted_data,
                "customer_name": state["email_data"].get("sender_name", "Valued Customer"),
                "agent_info": state["assigned_sales_person"],
                "rate_info": rate_info
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
            
            state["acknowledgment_response_result"] = result
            
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
            
        except Exception as e:
            logger.error(f"❌ Acknowledgment response generation failed: {e}")
            state["acknowledgment_response_result"] = {"error": str(e)}
        
        return state
    
    async def _generate_confirmation_acknowledgment(self, state: WorkflowState) -> WorkflowState:
        """Generate confirmation acknowledgment response"""
        logger.info("🔄 Generating confirmation acknowledgment response...")
        
        try:
            # Get extraction result safely
            extraction_result = state.get("extraction_result", {})
            extracted_data = extraction_result.get("extracted_data", {}) if extraction_result else {}
            
            # Get email data safely
            email_data = state.get("email_data", {})
            customer_name = email_data.get("sender_name", "Valued Customer") if email_data else "Valued Customer"
            
            result = self.confirmation_acknowledgment_agent.process({
                "extracted_data": extracted_data,
                "customer_name": customer_name,
                "agent_info": state["assigned_sales_person"],
                "tone": "professional",
                "quote_timeline": "24 hours",
                "include_forwarder_info": True
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
                state["forwarder_response_result"] = {"error": "Email data is missing"}
                return state
                
            result = self.forwarder_response_agent.process({
                "email_data": email_data,
                "forwarder_info": forwarder_info,
                "extracted_data": extracted_data
            })
            
            state["forwarder_response_result"] = result
            logger.info(f"✅ Forwarder response processed: {result.get('response_type', 'unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Forwarder response processing failed: {e}")
            state["forwarder_response_result"] = {"error": str(e)}
        
        return state
    
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
            # Get extracted data and enriched data
            extracted_data = state["extraction_result"].get("extracted_data", {})
            enriched_data = {
                "port_lookup": state.get("port_lookup_result", {}),
                "container_standardization": state.get("container_standardization_result", {}),
                "rate_recommendation": state.get("rate_recommendation_result", {})
            }
            
            # Extract origin and destination countries from port lookup
            origin_country = ""
            destination_country = ""
            
            if state.get("port_lookup_result"):
                port_lookup = state["port_lookup_result"]
                if port_lookup and isinstance(port_lookup, dict):
                    if port_lookup.get("origin") and isinstance(port_lookup["origin"], dict):
                        origin_country = port_lookup["origin"].get("country", "")
                    if port_lookup.get("destination") and isinstance(port_lookup["destination"], dict):
                        destination_country = port_lookup["destination"].get("country", "")
            
            # If no countries from port lookup, try to extract from shipment details
            if not origin_country:
                origin_country = extracted_data.get("shipment_details", {}).get("origin", "")
            if not destination_country:
                destination_country = extracted_data.get("shipment_details", {}).get("destination", "")
            
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
                customer_email_content = state["email_data"].get("content", "")
                
                # Generate rate request email using forwarder email draft agent
                rate_request_data = {
                    "assigned_forwarders": [assigned_forwarder],
                    "shipment_details": extracted_data.get("shipment_details", {}),
                    "origin_country": origin_country,
                    "destination_country": destination_country,
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
        
        try:
            result = self.escalation_agent.process({
                "email_data": state["email_data"],
                "classification_result": state["classification_result"],
                "conversation_state_result": state["conversation_state_result"],
                "extraction_result": state["extraction_result"],
                "validation_result": state["validation_result"]
            })
            
            state["escalation_result"] = result
            state["should_escalate"] = result.get("should_escalate", False)
            
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
            
            logger.info(f"✅ Escalation check completed: {'Escalate' if state['should_escalate'] else 'Continue'}")
            
        except Exception as e:
            logger.error(f"❌ Escalation check failed: {e}")
            state["escalation_result"] = {"error": str(e)}
            state["should_escalate"] = True
        
        return state
    
    async def _notify_sales(self, state: WorkflowState) -> WorkflowState:
        """Notify sales team"""
        logger.info("🔄 Notifying sales team...")
        
        try:
            result = self.sales_notification_agent.process({
                "email_data": state["email_data"],
                "escalation_result": state["escalation_result"],
                "classification_result": state["classification_result"],
                "extraction_result": state["extraction_result"]
            })
            
            state["sales_notification_result"] = result
            
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
            
        except Exception as e:
            logger.error(f"❌ Sales notification failed: {e}")
            state["sales_notification_result"] = {"error": str(e)}
        
        return state
    
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
            
            customer_email_entry = EmailEntry(
                timestamp=state["timestamp"],
                email_id=state["workflow_id"],
                sender=email_data.get("sender", "unknown"),
                direction="inbound",
                subject=email_data.get("subject", "No Subject"),
                content=email_data.get("content", ""),
                extracted_data=extraction_result.get("extracted_data", {}),
                response_type=next_action_result.get("action", "unknown"),
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
        """Route after email classification"""
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
            return "conversation_state"
        elif "forwarder" in email_type or sender_type == "forwarder":
            return "conversation_state"
        elif email_type == "escalation_needed" or classification_result.get("escalation_needed", False):
            return "check_escalation"
        else:
            return "check_escalation"
    
    def _route_after_conversation_state(self, state: WorkflowState) -> str:
        """Route after conversation state analysis"""
        if state["should_escalate"]:
            return "escalate"
        else:
            return "continue"
    
    def _route_after_next_action(self, state: WorkflowState) -> str:
        """Route after next action determination"""
        next_action_result = state.get("next_action_result", {})
        action = next_action_result.get("next_action", next_action_result.get("action", "escalate"))
        
        print(f"🔄 NEXT ACTION ROUTING: Action = {action}")
        
        # All response generation paths go through sales person assignment first
        if action in ["send_clarification_request", "clarification", "send_confirmation_request", "confirmation", "send_acknowledgment", "acknowledgment"]:
            return "assign_sales_person"
        elif action == "assign_forwarder" or action == "forwarder":
            return "detect_forwarder"
        elif action == "escalate" or next_action_result.get("should_escalate", False):
            return "check_escalation"
        else:
            return "check_escalation"
    
    def _route_after_sales_assignment(self, state: WorkflowState) -> str:
        """Intelligent routing based on missing fields, confidence, and data quality"""
        next_action_result = state.get("next_action_result", {})
        action = next_action_result.get("next_action", next_action_result.get("action", "escalate"))
        
        # Get confidence scores
        classification_confidence = state.get("classification_result", {}).get("confidence", 0.0)
        extraction_confidence = state.get("extraction_result", {}).get("confidence", 0.0)
        validation_confidence = state.get("validation_result", {}).get("confidence", 0.0)
        
        # Get missing fields from next action result
        missing_fields = next_action_result.get("missing_fields", [])
        
        # If missing_fields is not in next_action_result, try to get it from the state
        if not missing_fields:
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
        
        # Check for customer confirmation first
        if customer_confirmed:
            print(f"   ✅ CUSTOMER CONFIRMATION DETECTED")
            print(f"   📧 Sending confirmation acknowledgment")
            return "generate_confirmation_acknowledgment"
        
        # Intelligent routing logic
        if overall_confidence < LOW_CONFIDENCE_THRESHOLD:
            print(f"   🚨 LOW CONFIDENCE DETECTED: {overall_confidence:.2f} < {LOW_CONFIDENCE_THRESHOLD}")
            print(f"   📧 Sending acknowledgment to customer")
            print(f"   📞 Escalating to sales person")
            # Set escalation flag for later use
            state["should_escalate"] = True
            # Also update the next action result to reflect this decision
            if "next_action_result" in state:
                state["next_action_result"]["should_escalate"] = True
            return "generate_acknowledgment_response"
        
        # Check if next action agent explicitly chose clarification
        elif action == "send_clarification_request" or action == "clarification":
            print(f"   📋 NEXT ACTION AGENT CHOSE CLARIFICATION: {action}")
            print(f"   📧 Respecting next action agent decision")
            return "generate_clarification_response"
        
        elif not missing_fields:  # No missing fields
            print(f"   ✅ NO MISSING FIELDS: {missing_fields}")
            print(f"   📧 Sending confirmation request")
            return "generate_confirmation_response"
        
        else:  # Has missing fields
            print(f"   ❌ MISSING FIELDS DETECTED: {missing_fields}")
            print(f"   📧 Sending clarification request")
            return "generate_clarification_response"
    
    def _route_after_acknowledgment(self, state: WorkflowState) -> str:
        """Route after acknowledgment response - check if escalation is needed"""
        should_escalate = state.get("should_escalate", False) or state.get("next_action_result", {}).get("should_escalate", False)
        
        if should_escalate:
            print(f"🔄 ACKNOWLEDGMENT ROUTING: Escalation needed due to low confidence")
            return "check_escalation"
        else:
            # For forwarder/sales person emails, we can skip thread update to avoid NoneType errors
            # since the acknowledgment is already generated and the UI will handle it properly
            classification_result = state.get("classification_result", {})
            sender_classification = classification_result.get("sender_classification", {})
            sender_type = sender_classification.get("type", "customer")
            
            if sender_type in ["forwarder", "sales_person"]:
                print(f"🔄 Forwarder/Sales person email - skipping thread update to avoid errors")
                # Mark workflow as completed without thread update
                state["workflow_completed"] = True
                return END
            
            print(f"🔄 ACKNOWLEDGMENT ROUTING: Proceeding to thread update")
            return "update_thread"
    
    def _route_after_confirmation_acknowledgment(self, state: WorkflowState) -> str:
        """Route after confirmation acknowledgment - proceed with forwarder assignment"""
        print(f"🔄 CONFIRMATION ACKNOWLEDGMENT ROUTING: Proceeding with forwarder assignment")
        return "assign_forwarders"
    
    async def process_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email through the complete workflow"""
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Generate consistent thread ID based on sender email
        sender_email = email_data.get("sender", "unknown")
        thread_id = email_data.get("thread_id", f"thread_{sender_email.replace('@', '_').replace('.', '_')}")
        
        logger.info(f"🚀 Starting workflow {workflow_id} for thread {thread_id}")
        
        # Initialize state
        initial_state = WorkflowState(
            email_data=email_data,
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