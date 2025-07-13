import streamlit as st
import json
import sys
import os

# Ensure agents are importable
sys.path.append(os.path.join(os.path.dirname(__file__), "agents"))
from agents.orchestrator_agent import OrchestratorAgent
from agents.classification_agent import ClassificationAgent
from agents.extraction_agent import ExtractionAgent
from agents.validation_agent import ValidationAgent
from agents.clarification_agent import ClarificationAgent
from agents.confirmation_agent import ConfirmationAgent
from agents.forwarder_assignment_agent import ForwarderAssignmentAgent
from agents.rate_parser_agent import RateParserAgent
from agents.response_generator_agent import ResponseGeneratorAgent
from agents.escalation_agent import EscalationAgent
from agents.memory_agent import MemoryAgent
from agents.logging_agent import LoggingAgent

st.set_page_config(page_title="AI Email Orchestrator Demo", layout="wide")

# --- Sidebar for Input and Agent Testing ---
with st.sidebar:
    st.title("📧 Email Input & Agent Testing")
    if "subject" not in st.session_state:
        st.session_state["subject"] = "Shipping Quote Request"
    if "email_text" not in st.session_state:
        st.session_state["email_text"] = "Need quote for 2x40ft FCL from Shanghai to Long Beach, electronics, ready July 15th"
    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = "demo-thread-001"
    if "workflow_state" not in st.session_state:
        st.session_state["workflow_state"] = "{}"
    if "agent_input" not in st.session_state:
        st.session_state["agent_input"] = {}

    subject = st.text_input("Email Subject", value=st.session_state["subject"], key="subject")
    email_text = st.text_area("Email Body", value=st.session_state["email_text"], key="email_text", height=120)
    thread_id = st.text_input("Thread ID", value=st.session_state["thread_id"], key="thread_id")
    workflow_state = st.text_area("Workflow State (JSON, optional)", value=st.session_state["workflow_state"], key="workflow_state", height=80, help="Paste workflow state JSON if continuing a thread.")

    col1, col2 = st.columns([1, 1])
    with col1:
        run_clicked = st.button("🚀 Run Orchestrator", use_container_width=True)
    with col2:
        reset_clicked = st.button("🔄 Reset Form", use_container_width=True)

    if reset_clicked:
        st.session_state["subject"] = "Shipping Quote Request"
        st.session_state["email_text"] = "Need quote for 2x40ft FCL from Shanghai to Long Beach, electronics, ready July 15th"
        st.session_state["thread_id"] = "demo-thread-001"
        st.session_state["workflow_state"] = "{}"
        st.session_state["agent_input"] = {}
        st.experimental_rerun()

    st.markdown("---")
    st.subheader("🔬 Test Individual Agent (Step-by-Step)")
    agent_list = [
        "None",
        "Classification",
        "Extraction",
        "Validation",
        "Clarification",
        "Confirmation",
        "Forwarder Assignment",
        "Rate Parser",
        "Response Generator",
        "Escalation",
        "Memory",
        "Logging"
    ]
    agent_to_test = st.selectbox("Choose agent to test", agent_list)
    test_agent_clicked = st.button("🧪 Run Agent Test")

    st.markdown("### Debug: Session State")
    st.json(dict(st.session_state))

# --- Main Page ---
st.title("AI Email Orchestrator Workflow Demo")
st.markdown(
    """
    <style>
    .step-badge {display:inline-block; padding:2px 10px; border-radius:8px; font-size:0.9em; margin-left:8px;}
    .badge-success {background:#d4edda; color:#155724;}
    .badge-fallback {background:#fff3cd; color:#856404;}
    .badge-llm {background:#e2e3f3; color:#383d7c;}
    .badge-error {background:#f8d7da; color:#721c24;}
    .badge-escalation {background:#fbeee6; color:#b86b00;}
    </style>
    """,
    unsafe_allow_html=True,
)

with st.expander("ℹ️ Instructions", expanded=True):
    st.markdown("""
    - Enter an email subject, body, and thread ID in the sidebar.
    - Click **Run Orchestrator** to process the email through the workflow.
    - Or, select and test an individual agent (step-by-step) in the sidebar.
    - Each step is shown with status, icon, and details.
    - Steps where LLM failed and fallback was used are **highlighted**.
    - Try different scenarios: customer request, forwarder quote, confirmation, etc.
    """)

def step_status_icon(step_data):
    """Returns icon, badge class, and status for step based on fallback/escalation/error."""
    if isinstance(step_data, dict):
        if step_data.get("classification_method", "").lower().startswith("regex") or \
           step_data.get("extraction_method", "").lower().startswith("regex") or \
           "fallback" in step_data.get("classification_method", "").lower() or \
           "fallback" in step_data.get("extraction_method", "").lower():
            return "🟡", "badge-fallback", "LLM failed, fallback used"
        if "llm" in step_data.get("classification_method", "").lower() or \
           "llm" in step_data.get("extraction_method", "").lower():
            return "🤖", "badge-llm", "LLM used"
        if "escalate" in step_data.get("action", "") or "escalation" in step_data.get("action", ""):
            return "🚨", "badge-escalation", "Escalation"
        if "error" in step_data:
            return "❌", "badge-error", "Error"
        if step_data.get("status") == "success":
            return "✅", "badge-success", "Success"
    return "🔵", "badge-success", "Step"

def highlight_json(json_obj):
    """Highlight fallback keys in JSON."""
    text = json.dumps(json_obj, indent=2)
    text = text.replace("regex_fallback", "🟡 regex_fallback")
    text = text.replace("llm_enhanced", "🤖 llm_enhanced")
    text = text.replace("databricks_llm", "🤖 databricks_llm")
    text = text.replace("escalate", "🚨 escalate")
    return text

# --- Agent Test Output ---
if agent_to_test != "None" and test_agent_clicked:
    st.subheader(f"🔬 {agent_to_test} Agent Test Output")
    # Allow chaining: use previous agent output if available
    agent_input = st.session_state.get("agent_input", {})
    base_input = {
        "subject": subject,
        "email_text": email_text,
        "thread_id": thread_id
    }
    # Merge previous output if available
    if agent_input:
        base_input.update(agent_input)

    if agent_to_test == "Classification":
        agent = ClassificationAgent()
        agent.load_context()
        result = agent.run(base_input)
        st.session_state["agent_input"] = result
        st.json(result)
    elif agent_to_test == "Extraction":
        agent = ExtractionAgent()
        agent.load_context()
        result = agent.run(base_input)
        st.session_state["agent_input"] = result
        st.json(result)
    elif agent_to_test == "Validation":
        agent = ValidationAgent()
        agent.load_context()
        result = agent.run(base_input)
        st.session_state["agent_input"] = result
        st.json(result)
    elif agent_to_test == "Clarification":
        agent = ClarificationAgent()
        agent.load_context()
        result = agent.run(base_input)
        st.session_state["agent_input"] = result
        st.json(result)
    elif agent_to_test == "Confirmation":
        agent = ConfirmationAgent()
        agent.load_context()
        result = agent.run(base_input)
        st.session_state["agent_input"] = result
        st.json(result)
    elif agent_to_test == "Forwarder Assignment":
        agent = ForwarderAssignmentAgent()
        agent.load_context()
        result = agent.run(base_input)
        st.session_state["agent_input"] = result
        st.json(result)
    elif agent_to_test == "Rate Parser":
        agent = RateParserAgent()
        agent.load_context()
        result = agent.run(base_input)
        st.session_state["agent_input"] = result
        st.json(result)
    elif agent_to_test == "Response Generator":
        agent = ResponseGeneratorAgent()
        agent.load_context()
        result = agent.run(base_input)
        st.session_state["agent_input"] = result
        st.json(result)
    elif agent_to_test == "Escalation":
        agent = EscalationAgent()
        agent.load_context()
        result = agent.run(base_input)
        st.session_state["agent_input"] = result
        st.json(result)
    elif agent_to_test == "Memory":
        agent = MemoryAgent()
        agent.load_context()
        result = agent.run(base_input)
        st.session_state["agent_input"] = result
        st.json(result)
    elif agent_to_test == "Logging":
        agent = LoggingAgent()
        agent.load_context()
        result = agent.run(base_input)
        st.session_state["agent_input"] = result
        st.json(result)

    st.info("You can now test the next agent using the output above as input.")

# --- Orchestrator Workflow Output ---
if run_clicked:
    st.session_state["agent_input"] = {}  # Reset agent chaining for orchestrator run
    st.info("Running orchestrator...")

    # Parse workflow_state if provided
    try:
        workflow_state_dict = json.loads(workflow_state) if workflow_state.strip() else {}
    except Exception as e:
        st.error(f"Invalid workflow_state JSON: {e}")
        workflow_state_dict = {}

    # Run orchestrator (no caching)
    agent = OrchestratorAgent()
    agent.load_context()
    input_data = {
        "subject": subject,
        "email_text": email_text,
        "thread_id": thread_id,
        "workflow_state": workflow_state_dict
    }
    result = agent.run(input_data)

    # --- Display Results ---
    st.header("Workflow Result")
    st.json(result)

    # --- Timeline/Steps Visualization ---
    if "steps" in result:
        st.subheader("Workflow Timeline")
        for i, step in enumerate(result["steps"], 1):
            step_name = list(step.keys())[0]
            step_data = step[step_name]
            icon, badge_class, status = step_status_icon(step_data)
            with st.container():
                cols = st.columns([0.08, 0.82, 0.1])
                with cols[0]:
                    st.markdown(f"<div style='font-size:2em'>{icon}</div>", unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(
                        f"<b>Step {i}: {step_name.replace('_', ' ').title()}</b> "
                        f"<span class='step-badge {badge_class}'>{status}</span>",
                        unsafe_allow_html=True
                    )
                    st.code(highlight_json(step_data), language="json")
                with cols[2]:
                    pass

    # --- Final Action ---
    if "final_action" in result:
        action = result['final_action'].get('action', 'N/A')
        details = result['final_action'].get("details", {})
        if "escalate" in action:
            st.error(f"🚨 **Final Action:** {action}")
        elif "wait" in action:
            st.warning(f"⏳ **Final Action:** {action}")
        elif "confirmation" in action or "assign" in action:
            st.success(f"✅ **Final Action:** {action}")
        else:
            st.info(f"**Final Action:** {action}")
        if details:
            st.write(details)

    # --- Status ---
    st.markdown(f"**Status:** `{result.get('status', 'unknown')}`")

    # --- Show workflow_state for next round ---
    st.markdown("#### Copy this Workflow State for next round (if needed):")
    st.code(json.dumps(result.get("workflow_state", input_data.get("workflow_state", {})), indent=2), language="json")
