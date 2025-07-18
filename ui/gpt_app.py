# Updated Streamlit App for AI Logistics Response Model
# Enhanced UI with modular styling and modern layout
# --- Core logic preserved ---

import streamlit as st
import sys
import os
import json
from datetime import datetime

# --- Add agent directory to path ---
agents_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents")
sys.path.insert(0, agents_path)

try:
    from agents.langgraph_orchestrator import run_workflow 
except ImportError:
    import importlib.util
    orchestrator_path = os.path.join(agents_path, "langgraph_orchestrator.py")
    spec = importlib.util.spec_from_file_location("langgraph_orchestrator", orchestrator_path)
    if spec and spec.loader:
        langgraph_orchestrator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(langgraph_orchestrator)
        run_workflow = langgraph_orchestrator.run_workflow
    else:
        raise ImportError("Could not import langgraph_orchestrator")

# --- Page config ---
st.set_page_config(
    page_title="AI Logistics Assistant",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom style ---
st.markdown("""
<style>
    /* Dark theme with white text */
    .main-header {
        text-align: center;
        color: #ffffff;
        margin-bottom: 1rem;
        font-size: 2.2rem;
        font-weight: 700;
    }
    .section {
        background-color: #1e1e1e;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        border: 1px solid #333333;
    }
    .section h3 {
        margin-top: 0;
        color: #ffffff;
    }
    .output-section {
        max-height: 80vh;
        overflow-y: auto;
        background-color: #1e1e1e;
        border: 1px solid #333333;
    }
    .response-box {
        background-color: #2d2d2d;
        border: 2px solid #444444;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        max-height: 60vh;
        overflow-y: auto;
    }
    .response-content {
        background-color: #1e1e1e !important;
        border: 1px solid #444444;
        border-radius: 6px;
        padding: 1rem;
        margin-top: 0.5rem;
        white-space: pre-wrap;
        word-wrap: break-word;
        line-height: 1.6;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        max-height: 40vh;
        overflow-y: auto;
        color: #ffffff !important;
    }
    /* Ensure all text in response boxes is white */
    .response-box * {
        color: #ffffff !important;
    }
    .response-box p, .response-box div, .response-box span {
        color: #ffffff !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444444;
    }
    .stButton>button:hover {
        background-color: #3d3d3d;
        border-color: #555555;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
    .status-success { background-color: #1a4d2e; color: #ffffff; }
    .status-warning { background-color: #4d3a1a; color: #ffffff; }
    .status-error { background-color: #4d1a1a; color: #ffffff; }
    .footer {
        text-align: center;
        color: #cccccc;
        font-size: 0.85rem;
        margin-top: 2rem;
    }
    /* Ensure proper column spacing */
    .stColumns > div {
        padding: 0 0.5rem;
    }
    /* Better text area styling */
    .stTextArea textarea {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        line-height: 1.5;
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444444;
    }
    /* Improved button styling */
    .stButton > button {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444444;
    }
    .stButton > button:hover {
        background-color: #3d3d3d;
        border-color: #555555;
    }
    /* Ensure all text is visible */
    .stMarkdown, .stText, .stCode {
        color: #ffffff !important;
    }
    /* Force white text in all containers */
    div, p, span, h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    /* Input styling */
    .stTextInput > div > div > input {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444444;
    }
    .stSelectbox > div > div > select {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444444;
    }
    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444444;
        border-radius: 4px;
        font-weight: 500;
    }
    /* Info boxes */
    .stAlert {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444444;
        border-radius: 4px;
    }
    /* JSON display */
    .stJson {
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1px solid #444444;
        border-radius: 4px;
    }
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1a1a1a;
    }
    /* Main background */
    .main .block-container {
        background-color: #0f0f0f;
    }
    /* Radio buttons */
    .stRadio > div > div > label {
        color: #ffffff !important;
    }
    /* Checkbox */
    .stCheckbox > div > div > label {
        color: #ffffff !important;
    }
    /* Toggle */
    .stToggle > div > div > label {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper functions ---
def process_thread(thread, subject, thread_id):
    try:
        # Validate thread is not empty
        if not thread or len(thread) == 0:
            return None, "Message thread must contain at least one message"
        
        # Validate each message has required fields
        for i, msg in enumerate(thread):
            if not isinstance(msg, dict):
                return None, f"Message {i+1} must be a dictionary"
            if 'sender' not in msg or 'body' not in msg:
                return None, f"Message {i+1} must have 'sender' and 'body' fields"
            if not msg['body'].strip():
                return None, f"Message {i+1} body cannot be empty"
        
        result = run_workflow(message_thread=thread, subject=subject, thread_id=thread_id)
        return result, None
    except Exception as e:
        return None, str(e)

# --- Sidebar Configuration ---
with st.sidebar:
    st.title("🔧 Configuration")
    input_mode = st.radio("Input Mode", ["Single Email", "Email Thread"])
    sender = st.text_input("Sender Email", value="customer@example.com")
    subject = st.text_input("Email Subject", value="Rate request for container shipment")
    thread_id = st.text_input("Thread ID", value=f"thread-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    debug_mode = st.toggle("Show Debug Info", value=False)
    st.divider()
    if st.button("Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- Main Header ---
st.markdown('<h1 class="main-header">AI Logistics Response Model</h1>', unsafe_allow_html=True)

# --- Main Layout ---
col1, col2 = st.columns([1, 1])

# --- Input Column ---
with col1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.subheader("📥 Input Email")
    st.markdown("Enter your logistics inquiry below:")

    if input_mode == "Single Email":
        default_email = (
            "Hi,\n\nWe need to ship 50 containers from Jebel Ali to Mundra.\n"
            "Details:\n- Container type: 20DC\n- Weight: 15 MT\n- Shipment date: 15 Dec 2024\n"
            "Please provide rates.\n\nBest,\nJohn Smith\nABC Electronics Ltd."
        )
        email_text = st.text_area("Email Content", value=default_email, height=300)

        if st.button("🚀 Process Email"):
            if not email_text.strip():
                st.error("❌ Please enter email content")
            else:
                message_thread = [{
                    "sender": sender, 
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                    "body": email_text.strip()
                }]
                result, error = process_thread(message_thread, subject, thread_id)
                if error:
                    st.error(f"❌ Error: {error}")
                else:
                    st.session_state.result = result    
                    st.success("✅ Processed successfully!")
    else:
        if "message_thread" not in st.session_state:
            st.session_state.message_thread = []

        msg = st.text_area("Add Message to Thread", height=150)
        msg_sender = st.text_input("Sender", value="customer@example.com")
        if st.button("Add to Thread") and msg.strip():
            st.session_state.message_thread.append({
                "sender": msg_sender,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "body": msg.strip()
            })
            # st.experimental_rerun()

        st.markdown("### 📜 Current Thread")
        for i, m in enumerate(st.session_state.message_thread):
            st.markdown(f"**{m['sender']}** at *{m['timestamp']}*\n\n{m['body']}")
            if st.button("Delete", key=f"del_{i}"):
                st.session_state.message_thread.pop(i)
                # st.experimental_rerun()
                

        if st.button("🚀 Process Thread"):
            if not st.session_state.message_thread:
                st.error("❌ Please add at least one message to the thread")
            else:
                result, error = process_thread(st.session_state.message_thread, subject, thread_id)
                if error:
                    st.error(f"❌ Error: {error}")
                else:
                    st.session_state.result = result
                    st.success("✅ Thread processed!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Output Column ---
with col2:
    st.markdown('<div class="section output-section">', unsafe_allow_html=True)
    st.subheader("📤 Generated Response")
    
    if "result" in st.session_state and st.session_state.result is not None:
        res = st.session_state.result

        # Check if this is a non-logistics request
        if isinstance(res, dict) and res.get("classification", {}).get("email_type") != "logistics_request":
            st.markdown('<div class="response-box">', unsafe_allow_html=True)
            st.markdown("**📧 General Response:**")
            
            # Check if there's a specific response for non-logistics
            if res.get("response"):
                response_body = res["response"].get("response_body", "Thank you for your email. This appears to be outside our logistics services scope.")
            else:
                response_body = "Thank you for your email. This appears to be outside our logistics services scope. Please contact our general support team for assistance."
            
            st.markdown(f'<div class="response-content">{response_body}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Show escalation status if present
            if isinstance(res, dict) and res.get("escalation", {}).get("escalate"):
                reason = res["escalation"].get("reason", "Non-logistics request")
                st.markdown(f"<span class='status-badge status-warning'>⚠️ Escalated: {reason}</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='status-badge status-success'>✅ General response sent</span>", unsafe_allow_html=True)
        
        # Handle logistics requests
        elif isinstance(res, dict) and res.get("classification", {}).get("email_type") == "logistics_request":
            # Status indicator
            if res and res.get("escalation", {}).get("escalate"):
                reason = res["escalation"].get("reason", "N/A")
                escalation_type = res["escalation"].get("escalation_type", "general")
                st.markdown(f"<span class='status-badge status-warning'>⚠️ ESCALATED: {escalation_type}</span>", unsafe_allow_html=True)
                st.markdown(f"**Reason:** {reason}")
            else:
                response_status = res.get("response", {}).get("status", "completed") if res and res.get("response") else "completed"
                if response_status == "not_logistics_request":
                    st.markdown("<span class='status-badge status-warning'>📧 Non-Logistics Request</span>", unsafe_allow_html=True)
                elif response_status == "escalated_for_review":
                    st.markdown("<span class='status-badge status-warning'>⏳ Under Human Review</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='status-badge status-success'>✅ Processing Complete</span>", unsafe_allow_html=True)

            # Main response display
            if res.get("response"):
                response_body = res["response"].get("response_body", "No content generated")
                
                st.markdown('<div class="response-box">', unsafe_allow_html=True)
                st.markdown("**📧 AI Generated Email Response:**")
                st.markdown(f'<div class="response-content">{response_body}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Copy button functionality
                if st.button("📋 Copy Response", key="copy_response"):
                    st.write("Response copied to clipboard!")
                    st.session_state.copied = True
            else:
                st.info("No response generated yet. Process an email to see results.")
        
        # Fallback for other cases
        else:
            st.info("Processing completed. Check debug information for details.")

        # Debug information (collapsed by default)
        if debug_mode and isinstance(res, dict):
            with st.expander("🔧 Debug Information", expanded=False):
                st.json(res)
    else:
        st.info("👈 Enter email content and click 'Process Email' to generate a response.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown('<div class="footer">AI Logistics Assistant • Streamlit UI</div>', unsafe_allow_html=True)