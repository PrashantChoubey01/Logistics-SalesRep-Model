import json
import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

from classification_agent import ClassificationAgent
from extraction_agent import ExtractionAgent
from port_lookup_agent import PortLookupAgent
from container_standardization_agent import ContainerStandardizationAgent
from country_extractor_agent import CountryExtractorAgent
from clarification_agent import ClarificationAgent
from rate_recommendation_agent import RateRecommendationAgent
from response_generator_agent import ResponseGeneratorAgent
from forwarder_assignment_agent import ForwarderAssignmentAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")

# Define the state structure
class WorkflowState(TypedDict):
    email_text: str
    subject: str
    sender: str
    classification: Dict[str, Any]
    extraction: Dict[str, Any]
    ports: Dict[str, Any]
    container: Dict[str, Any]
    countries: Dict[str, Any]
    clarification: Dict[str, Any]
    rate: Dict[str, Any]
    response: Dict[str, Any]
    error: str

# Node functionsdef classify_email(state: WorkflowState) -> WorkflowState:
logger.info("🧠 Step O: Logging started")
    
def classify_email(state: WorkflowState) -> WorkflowState:
    logger.info("🧠 Step 1: Classification")
    try:
        # Initialize the classification agent
        agent = ClassificationAgent()
        # Load context (this returns True/False, not the agent itself)
        context_loaded = agent.load_context()
        # Prepare input data
        input_data = {
            "email_text": state["email_text"], 
            "subject": state["subject"], 
            "from": state["sender"]
        }
        # Run the agent (use the agent itself, not the context_loaded result)
        result = agent.run(input_data)
        # Store result in state
        state["classification"] = result
        logger.info(f"Classification completed: {result.get('email_type', 'unknown')}")
        print(f"Classification Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        state["classification"] = {"error": str(e), "status": "error"}
        state["error"] = str(e)
    return state


def extract_information(state: WorkflowState) -> WorkflowState:
    logger.info("🔍 Step 2: Extraction")
    agent = ExtractionAgent()
    context_loaded = agent.load_context()
    input_data = {"email_text": state["email_text"], "subject": state["subject"], "from": state["sender"]}
    result = agent.run(input_data)
    state["extraction"] = result
    logger.info(f"Extraction completed: {result}")
    return state

def lookup_ports(state: WorkflowState) -> WorkflowState:
    logger.info("🚢 Step 3: Port Lookup")
    agent = PortLookupAgent()
    context_loaded = agent.load_context()
    ports = {}
    extraction = state["extraction"]
    
    for loc in ["origin", "destination"]:
        if extraction.get(loc):
            ports[f"{loc}_port"] = agent.run({"port_name": extraction[loc]})
    
    state["ports"] = ports
    print(f"Port Lookup Result: {json.dumps(ports, indent=2)}")
    return state

def standardize_container(state: WorkflowState) -> WorkflowState:
    logger.info("📦 Step 4: Container Standardization")
    agent = ContainerStandardizationAgent()
    context_loaded = agent.load_context()
    result = agent.run({"container_type": state["extraction"].get("container_type", "")})
    state["container"] = result
    print(f"Container Standardization Result: {json.dumps(result, indent=2)}")
    return state

def extract_countries(state: WorkflowState) -> WorkflowState:
    logger.info("🌍 Step 5: Country Extraction")
    agent = CountryExtractorAgent()
    countries = {}
    
    for loc in ["origin", "destination"]:
        port_data = state["ports"].get(f"{loc}_port", {})
        if port_data.get("port_code"):
            countries[f"{loc}_country"] = agent.run({"port_code": port_data["port_code"]})
    
    state["countries"] = countries
    print(f"Country Extraction Result: {json.dumps(countries, indent=2)}")
    return state

def get_clarification(state: WorkflowState) -> WorkflowState:
    logger.info("❓ Step 6: Clarification")
    agent = ClarificationAgent()
    context_loaded = agent.load_context()
    # Enrich extraction data
    enriched = state["extraction"].copy()
    enriched.update({
        "origin_port_code": state["ports"].get("origin_port", {}).get("port_code"),
        "destination_port_code": state["ports"].get("destination_port", {}).get("port_code"),
        "standardized_container_type": state["container"].get("standardized_container_type"),
        "origin_country": state["countries"].get("origin_country", {}).get("country"),
        "destination_country": state["countries"].get("destination_country", {}).get("country")
    })
    
    clarification_input = {
        "extraction_data": enriched,
        "validation": {"status": "skipped", "missing_fields": []},
        "missing_fields": [],
        "thread_id": f"thread-{hash(state['email_text']) % 10000}"
    }
    
    result = agent.run(clarification_input)
    state["clarification"] = result
    state["extraction"] = enriched  # Update with enriched data
    print(f"Clarification Result: {json.dumps(result, indent=2)}")
    return state

def get_rate_recommendation(state: WorkflowState) -> WorkflowState:
    logger.info("💰 Step 7: Rate Recommendation")
    agent = RateRecommendationAgent()
    context_loaded = agent.load_context()
    rate_input = {
        "Origin_Code": state["extraction"].get("origin_port_code"),
        "Destination_Code": state["extraction"].get("destination_port_code"),
        "Container_Type": state["extraction"].get("standardized_container_type") or state["extraction"].get("container_type", "40DC")
    }
    
    result = agent.run(rate_input)
    state["rate"] = result
    print(f"Rate Recommendation Result: {json.dumps(result, indent=2)}")
    return state

def generate_response(state: WorkflowState) -> WorkflowState:
    logger.info("📧 Step 8: Response Generation")
    agent = ResponseGeneratorAgent()
    agent.load_context()
    
    response_input = {
        "recipient_type": "customer",
        "context": {
            "classification": state["classification"],
            "extraction": state["extraction"],
            "clarification": state["clarification"],
            "rate": state["rate"]
        },
        "previous_messages": [state["email_text"]],
        "custom_instructions": "Be polite, mention rate, and thank the customer.",
        "indicative_rate": state["rate"].get("indicative_rate")
    }
    logger.info(f"Response Input: {json.dumps(response_input, indent=2)}")
    try:
        result = agent.run(response_input)
        state["response"] = result
    except Exception as e:
        logger.error(f"❌ Response generation failed: {e}")
        state["error"] = str(e)
        state["response"] = {"error": str(e), "status": "error"}
    
    print(f"Response Generation Result: {json.dumps(result, indent=2)}")
    return state

def assign_forwarders(state: WorkflowState) -> WorkflowState:
    logger.info("🚛 Step 7: Forwarder Assignment")
    
    try:
        # Initialize the forwarder assignment agent
        agent = ForwarderAssignmentAgent('/Users/prashant.choubey/Documents/VSWorkspace/AI-Sales-Bot-V2/logistic-ai-response-model/Forwarders_with_Operators_and_Emails.csv')
        # Load context
        context_loaded = agent.load_context()
        # Prepare input data with validated shipment information
        validated_data = {
            "origin_country": state["countries"].get("origin_country", {}).get("country"),
            "destination_country": state["countries"].get("destination_country", {}).get("country"),
            # "origin_port_code": state["ports"].get("origin_port", {}).get("port_code"),
            # "destination_port_code": state["ports"].get("destination_port", {}).get("port_code"),
            # "container_type": state["container"].get("standardized_container_type"),
            # "shipment_type": state["extraction"].get("shipment_type", "FCL"),
            # "quantity": state["extraction"].get("quantity"),
            # "weight": state["extraction"].get("weight"),
            # "cargo_type": state["extraction"].get("cargo_type")
        }
        
        # Check if countries are available
        if validated_data["origin_country"] or validated_data["destination_country"]:
            logger.warning("Missing country information for forwarder assignment")
            state["forwarder_assignment"] = {
                "error": "Missing origin or destination country information",
                "status": "skipped",
                "reason": "Cannot assign forwarders without country information"
            }
            return state
        
        # Prepare input for forwarder assignment agent
        forwarder_input = {
            "validated_data": validated_data
        }
        
        # Run the forwarder assignment
        result = agent.run(forwarder_input)
        
        # Store result in state
        state["forwarder_assignment"] = result
        
        logger.info(f"Forwarder assignment completed: {result.get('assignment_status', 'unknown')}")
        print(f"Forwarder Assignment Result: {json.dumps(result, indent=2)}")
        
        # Log summary if successful
        if result.get("status") == "success" and result.get("assignment_status") == "success":
            assigned_forwarders = result.get("assigned_forwarders", [])
            logger.info(f"Successfully assigned {len(assigned_forwarders)} forwarders")
            if assigned_forwarders:
                top_forwarder = assigned_forwarders[0]
                logger.info(f"Top recommendation: {top_forwarder.get('forwarder_name')}")
        
    except Exception as e:
        logger.error(f"Forwarder assignment failed: {e}")
        state["forwarder_assignment"] = {"error": str(e), "status": "error"}
        state["error"] = str(e)
    
    return state

# Build the workflow graph
def create_workflow():
    workflow = StateGraph(WorkflowState)
    
    # Add nodes
    workflow.add_node("classify", classify_email)
    workflow.add_node("extract", extract_information)
    workflow.add_node("ports", lookup_ports)
    workflow.add_node("container", standardize_container)
    workflow.add_node("countries", extract_countries)
    workflow.add_node("clarify", get_clarification)
    workflow.add_node("rate", get_rate_recommendation)
    workflow.add_node("respond", generate_response)
    workflow.add_node("assign_forwarders", assign_forwarders)  
    
    # Define the flow
    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "extract")
    workflow.add_edge("extract", "ports")
    workflow.add_edge("ports", "container")
    workflow.add_edge("container", "countries")
    workflow.add_edge("countries", "clarify")
    workflow.add_edge("clarify", "assign_forwarders")      
    workflow.add_edge("assign_forwarders", "rate")
    workflow.add_edge("rate", "respond")
    workflow.add_edge("respond", END)
    
    return workflow.compile()

# Main execution function
def run_workflow(email_text: str, subject: str, sender: str = "customer@example.com"):
    logger.info("📥 Running LangGraph workflow...")
    
    # Create initial state
    initial_state = WorkflowState(
        email_text=email_text,
        subject=subject,
        sender=sender,
        classification={},
        extraction={},
        ports={},
        container={},
        countries={},
        clarification={},
        forwarder_assignment={},
        rate={},
        response={},
        error=""
    )
    
    # Create and run workflow
    app = create_workflow()
    final_state = app.invoke(initial_state)
    
    logger.info("✅ Workflow completed!")
    logger.info(f"📧 Final Response: {json.dumps(final_state['response'], indent=2)}")
    
    return final_state

# Test the workflow
if __name__ == "__main__":
    run_workflow(
        email_text="We want to ship from jebel ali to mundra,using 20DC containers. The total quantity is 99, total weight is 26 Metric Ton, shipment type is FCL, and the shipment date is 20th June 2025. The cargo is electronics.",
        subject="rate request",
        sender="customer@example.com"
    )
