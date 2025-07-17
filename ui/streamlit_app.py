import streamlit as st
import sys
import os
import json
import time
from datetime import datetime

# Get the current directory and add paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
agents_dir = os.path.join(parent_dir, 'agents')

# Add both parent and agents directory to Python path
sys.path.insert(0, parent_dir)
sys.path.insert(0, agents_dir)

try:
    # Change working directory to agents folder temporarily
    original_cwd = os.getcwd()
    os.chdir(agents_dir)
    
    from agents.langgraph_orchestrator import run_workflow
    
    # Change back to original directory
    os.chdir(original_cwd)
    
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    st.error(f"Failed to import orchestrator: {e}")
    ORCHESTRATOR_AVAILABLE = False
    # Change back to original directory in case of error
    try:
        os.chdir(original_cwd)
    except:
        pass

st.set_page_config(page_title="AI Logistics LangGraph Demo", layout="wide")
st.title("📧 AI Logistics LangGraph Workflow Demo")

if not ORCHESTRATOR_AVAILABLE:
    st.error("❌ LangGraph orchestrator not available. Please check your imports.")
    st.info("Make sure all agent files are in the agents/ directory")
    st.stop()


# --- Session state for conversation and workflow history ---
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "workflow_states" not in st.session_state:
    st.session_state.workflow_states = []

# --- Sidebar for workflow visualization ---
with st.sidebar:
    st.header("🔄 Workflow Steps")
    workflow_steps = [
        "🧠 Classification",
        "🔍 Extraction", 
        "🚢 Port Lookup",
        "📦 Container Standardization",
        "🌍 Country Extraction",
        "❓ Clarification",
        "🚛 Forwarder Assignment",
        "💰 Rate Recommendation",
        "📧 Response Generation"
    ]
    
    for i, step in enumerate(workflow_steps):
        st.write(f"{i+1}. {step}")

# --- Main content area ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📥 Email Input")
    
    # --- Email input form ---
    with st.form("email_form", clear_on_submit=True):
        subject = st.text_input("Email Subject", value="Shipping Quote Request")
        email_text = st.text_area(
            "Email Body",
            value="We want to ship from jebel ali to mundra, using 20DC containers. The total quantity is 99, total weight is 26 Metric Ton, shipment type is FCL, and the shipment date is 20th June 2025. The cargo is electronics.",
            height=150
        )
        sender = st.text_input("Sender Email", value="customer@example.com")
        submitted = st.form_submit_button("🚀 Process Email", use_container_width=True)

with col2:
    st.subheader("📊 Workflow Status")
    
    # Placeholder for workflow status
    status_placeholder = st.empty()
    progress_bar = st.progress(0)

if submitted:
    # Reset workflow states for new input
    st.session_state.workflow_states = []
    
    # Add customer message to conversation
    st.session_state.conversation.append({
        "role": "customer",
        "subject": subject,
        "body": email_text,
        "sender": sender,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    
    # Show processing status
    with status_placeholder.container():
        st.info("🔄 Processing email through LangGraph workflow...")
    
    try:
        # Run the LangGraph workflow
        start_time = time.time()
        final_state = run_workflow(
            email_text=email_text,
            subject=subject,
            sender=sender
        )
        end_time = time.time()
        
        # Store the final state
        st.session_state.workflow_states.append({
            "input": {"email_text": email_text, "subject": subject, "sender": sender},
            "final_state": final_state,
            "processing_time": end_time - start_time,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        
        # Update progress
        progress_bar.progress(1.0)
        
        # Extract agent reply
        agent_reply = "No response generated"
        if final_state.get("response"):
            response_data = final_state["response"]
            if isinstance(response_data, dict):
                agent_reply = (
                    response_data.get("response_body") or 
                    response_data.get("response") or 
                    response_data.get("body") or
                    json.dumps(response_data, indent=2)
                )
            else:
                agent_reply = str(response_data)
        
        # Add agent response to conversation
        st.session_state.conversation.append({
            "role": "agent",
            "subject": f"Re: {subject}",
            "body": agent_reply,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time": f"{end_time - start_time:.2f}s"
        })
        
        # Update status
        with status_placeholder.container():
            if final_state.get("error"):
                st.error(f"❌ Workflow failed: {final_state['error']}")
            else:
                st.success(f"✅ Workflow completed in {end_time - start_time:.2f}s")
        
    except Exception as e:
        progress_bar.progress(0.0)
        with status_placeholder.container():
            st.error(f"❌ Workflow execution failed: {str(e)}")
        
        # Add error to conversation
        st.session_state.conversation.append({
            "role": "system",
            "subject": "Error",
            "body": f"Workflow execution failed: {str(e)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

# --- Display conversation history ---
st.subheader("💬 Conversation History")
for i, msg in enumerate(st.session_state.conversation):
    with st.container():
        if msg["role"] == "customer":
            st.markdown(f"**👤 Customer** - {msg.get('timestamp', '')}")
            st.markdown(f"**Subject:** {msg['subject']}")
            st.markdown(f"**From:** {msg.get('sender', 'N/A')}")
            with st.expander("📧 Email Content", expanded=True):
                st.text_area("", value=msg['body'], height=100, key=f"customer_{i}", disabled=True)
        
        elif msg["role"] == "agent":
            st.markdown(f"**🤖 AI Agent** - {msg.get('timestamp', '')} - ⏱️ {msg.get('processing_time', 'N/A')}")
            st.markdown(f"**Subject:** {msg['subject']}")
            with st.expander("📧 Agent Response", expanded=True):
                st.text_area("", value=msg['body'], height=150, key=f"agent_{i}", disabled=True)
        
        elif msg["role"] == "system":
            st.markdown(f"**⚠️ System** - {msg.get('timestamp', '')}")
            st.error(msg['body'])
        
        st.divider()

# --- Display detailed workflow states ---
if st.session_state.workflow_states:
    st.subheader("🔍 Detailed Workflow Analysis")
    
    # Select which workflow run to analyze
    if len(st.session_state.workflow_states) > 1:
        selected_run = st.selectbox(
            "Select workflow run:",
            range(len(st.session_state.workflow_states)),
            format_func=lambda x: f"Run {x+1} - {st.session_state.workflow_states[x]['timestamp']}"
        )
    else:
        selected_run = 0
    
    if selected_run < len(st.session_state.workflow_states):
        workflow_data = st.session_state.workflow_states[selected_run]
        final_state = workflow_data["final_state"]
        
        # Create tabs for different aspects of the workflow
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Step Results", "🔄 State Flow", "📈 Performance", "🐛 Debug Info"])
        
        with tab1:
            st.subheader("Step-by-Step Results")
            
            steps = [
                ("🧠 Classification", final_state.get("classification", {})),
                ("🔍 Extraction", final_state.get("extraction", {})),
                ("🚢 Port Lookup", final_state.get("ports", {})),
                ("📦 Container Standardization", final_state.get("container", {})),
                ("🌍 Country Extraction", final_state.get("countries", {})),
                ("❓ Clarification", final_state.get("clarification", {})),
                ("🚛 Forwarder Assignment", final_state.get("forwarder_assignment", {})),
                ("💰 Rate Recommendation", final_state.get("rate", {})),
                ("📧 Response Generation", final_state.get("response", {}))
            ]
            
            for step_name, step_data in steps:
                with st.expander(f"{step_name}", expanded=False):
                    if step_data:
                        # Show key metrics first
                        col1, col2 = st.columns(2)
                        with col1:
                            status = step_data.get("status", "unknown")
                            if status == "success":
                                st.success(f"Status: {status}")
                            elif status == "error":
                                st.error(f"Status: {status}")
                            else:
                                st.info(f"Status: {status}")
                        
                        with col2:
                            if "error" in step_data:
                                st.error(f"Error: {step_data['error']}")
                        
                        # Show full data
                        st.json(step_data)
                    else:
                        st.warning("No data available for this step")
        
        with tab2:
            st.subheader("State Flow Visualization")
            
            # Create a simple flow visualization
            flow_data = []
            for step_name, step_data in steps:
                status = step_data.get("status", "unknown") if step_data else "no_data"
                flow_data.append({
                    "step": step_name,
                    "status": status,
                    "has_error": "error" in step_data if step_data else False,
                    "data_size": len(str(step_data)) if step_data else 0
                })
            
            for i, flow_item in enumerate(flow_data):
                col1, col2, col3 = st.columns([1, 2, 1])
                
                with col1:
                    if flow_item["status"] == "success":
                        st.success("✅")
                    elif flow_item["status"] == "error":
                        st.error("❌")
                    else:
                        st.warning("⚠️")
                
                with col2:
                    st.write(f"**{flow_item['step']}**")
                    if flow_item["has_error"]:
                        st.error("Contains errors")
                
                with col3:
                    st.metric("Data Size", f"{flow_item['data_size']} chars")
                
                if i < len(flow_data) - 1:
                    st.write("⬇️")
        
        with tab3:
            st.subheader("Performance Metrics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Processing Time",
                    f"{workflow_data['processing_time']:.2f}s"
                )
            
            with col2:
                successful_steps = sum(1 for _, data in steps if data.get("status") == "success")
                st.metric("Successful Steps", f"{successful_steps}/{len(steps)}")
            
            with col3:
                error_count = sum(1 for _, data in steps if data.get("status") == "error" or "error" in data)
                st.metric("Errors", error_count)
            
            # Performance breakdown (if available)
            st.subheader("Step Performance")
            performance_data = []
            for step_name, step_data in steps:
                if step_data:
                    performance_data.append({
                        "Step": step_name,
                        "Status": step_data.get("status", "unknown"),
                        "Has Error": "Yes" if "error" in step_data else "No",
                        "Data Size": len(str(step_data))
                    })
            
            if performance_data:
                st.dataframe(performance_data, use_container_width=True)
        
        with tab4:
            st.subheader("Debug Information")
            
            # Show input data
            st.write("**Input Data:**")
            st.json(workflow_data["input"])
            
            # Show any errors
            if final_state.get("error"):
                st.write("**Workflow Error:**")
                st.error(final_state["error"])
            
            # Show full final state
            st.write("**Complete Final State:**")
            st.json(final_state)

# --- Control buttons ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Clear All Data", use_container_width=True):
        st.session_state.conversation = []
        st.session_state.workflow_states = []
        st.rerun()

with col2:
    if st.button("📊 Show Workflow Graph", use_container_width=True):
        st.info("Workflow Graph: Classification → Extraction → Port Lookup → Container → Countries → Clarification → Rate → Response")

with col3:
    if st.session_state.workflow_states:
        if st.button("💾 Export Results", use_container_width=True):
            export_data = {
                "conversation": st.session_state.conversation,
                "workflow_states": st.session_state.workflow_states,
                "export_timestamp": datetime.now().isoformat()
            }
            st.download_button(
                "📥 Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"workflow_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

# --- Footer ---
st.markdown("---")
st.markdown("**LangGraph Workflow:** Classification → Extraction → Port Lookup → Container → Countries → Clarification → Rate → Response")
