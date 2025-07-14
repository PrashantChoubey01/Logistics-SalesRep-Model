import streamlit as st
import sys
import os
import json

# Ensure agents are importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.llm_orchestrator_agent import LLMOrchestratorAgent

st.set_page_config(page_title="AI Logistics Email Demo", layout="wide")
st.title("📧 AI Logistics Email Chat Demo")

# --- Session state for conversation and workflow history ---
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "workflow_history" not in st.session_state:
    st.session_state.workflow_history = []

# --- Email input form ---
with st.form("email_form", clear_on_submit=True):
    st.subheader("Send a new customer email")
    subject = st.text_input("Email Subject", value="Shipping Quote Request")
    email_text = st.text_area("Email Body", value="Need quote for 2x40ft FCL from Shanghai to Long Beach, electronics, ready July 15th")
    submitted = st.form_submit_button("Send Email")

if submitted:
    # Add customer message to conversation
    st.session_state.conversation.append({
        "role": "customer",
        "subject": subject,
        "body": email_text
    })

    # Prepare orchestrator input
    agent = LLMOrchestratorAgent()
    input_data = {
        "subject": subject,
        "email_text": email_text,
        "thread_id": f"thread-{len(st.session_state.conversation)}"
    }
    result = agent.run(input_data)

    # Save workflow steps for this turn
    st.session_state.workflow_history.append(result.get("steps", []))

    # Try to extract agent reply
    agent_reply = None
    # Try several possible locations for the agent's reply
    if "final_email" in result and isinstance(result["final_email"], dict):
        for key in ["response_body", "response", "body"]:
            if key in result["final_email"]:
                agent_reply = result["final_email"][key]
                break
        if not agent_reply:
            agent_reply = json.dumps(result["final_email"], indent=2)
    elif "final_summary" in result:
        agent_reply = result["final_summary"]
    elif "status" in result and result["status"] == "escalated":
        agent_reply = "This case has been escalated to a human operator."
    else:
        agent_reply = "No agent reply found."

    st.session_state.conversation.append({
        "role": "agent",
        "subject": f"Re: {subject}",
        "body": agent_reply
    })

# --- Display conversation history ---
st.subheader("Conversation History")
for i, msg in enumerate(st.session_state.conversation):
    if msg["role"] == "customer":
        st.markdown(f"**Customer:** <span style='color:#1a73e8'>{msg['subject']}</span>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-left:20px; color:#333'>{msg['body']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"**Agent:** <span style='color:#34a853'>{msg['subject']}</span>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-left:20px; color:#222'>{msg['body']}</div>", unsafe_allow_html=True)
    st.markdown("---")

# --- Display agent workflow for each turn ---
st.subheader("Agent Workflow Details")
for idx, steps in enumerate(st.session_state.workflow_history):
    with st.expander(f"Show Agent Steps for Message {idx+1}"):
        for step in steps:
            st.markdown(
                f"<b>Step {step['step']}:</b> <span style='color:#6c63ff'>{step['agent']}</span> &mdash; <i>{step['reason']}</i>",
                unsafe_allow_html=True
            )
            st.markdown("**Input:**")
            st.code(json.dumps(step.get("input", {}), indent=2), language="json")
            st.markdown("**Output:**")
            st.code(json.dumps(step.get("output", {}), indent=2), language="json")

# --- Option to clear conversation and workflow ---
if st.button("🔄 Clear Conversation"):
    st.session_state.conversation = []
    st.session_state.workflow_history = []
    st.experimental_rerun()
