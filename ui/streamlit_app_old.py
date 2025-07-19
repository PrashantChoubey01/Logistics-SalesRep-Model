import streamlit as st
import sys
import os
import json
from datetime import datetime

# Add the agents directory to the path to import agents
agents_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents")
sys.path.insert(0, agents_path)

# Import the orchestrator function robustly
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

# Page configuration
st.set_page_config(
    page_title="AI Logistics Response Model",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Simple spacing and layout improvements */
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Input area styling */
    .input-section {
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    
    /* Output area styling */
    .output-section {
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    
    /* Response box styling */
    .response-box {
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    
    /* Rate information box */
    .rate-box {
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    
    /* Summary box */
    .summary-box {
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    
    /* Thread message box */
    .thread-message {
        padding: 0.5rem;
        border-radius: 4px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }
    
    /* Footer styling */
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding: 1rem;
        border-radius: 6px;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

def reset_session():
    """Reset session state"""
    if 'result' in st.session_state:
        del st.session_state.result
    if 'processed' in st.session_state:
        del st.session_state.processed

def process_email_thread(message_thread, subject, thread_id):
    """Process email thread and return result"""
    try:
        result = run_workflow(
            message_thread=message_thread,
            subject=subject,
            thread_id=thread_id
        )
        return result, None
    except Exception as e:
        return None, str(e)

def process_single_email(email_text, subject, sender_email, thread_id):
    """Process single email (backward compatibility)"""
    try:
        # Convert single email to thread format
        message_thread = [
            {
                "sender": sender_email,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "body": email_text
            }
        ]
        result = run_workflow(
            message_thread=message_thread,
            subject=subject,
            thread_id=thread_id
        )
        return result, None
    except Exception as e:
        return None, str(e)

def create_sample_thread():
    """Create a sample email thread for testing"""
    return [
        {
            "sender": "customer@example.com",
            "timestamp": "2024-01-15 11:00:00",
            "body": "Yes, please proceed with the booking. The details look good."
        },
        {
            "sender": "logistics@company.com",
            "timestamp": "2024-01-15 10:45:00",
            "body": "Here are the final details for your shipment. Please confirm if everything looks correct."
        },
        {
            "sender": "customer@example.com",
            "timestamp": "2024-01-15 10:30:00",
            "body": "We want to ship from Shanghai to Long Beach using 2x40ft containers. The total quantity is 50, total weight is 15 Metric Ton, shipment type is FCL, and the shipment date is 20th January 2025. The cargo is electronics."
        }
    ]

def create_default_thread():
    """Create the default logistics request thread (same as single email)"""
    return [
        {
            "sender": "customer@example.com",
            "timestamp": "2024-01-15 10:30:00",
            "body": (
                "Hi,\n\n"
                "We need to ship 50 containers from Jebel Ali to Mundra. \n"
                "Details as follows:\n"
                "- Container type: 20DC\n"
                "- Total quantity: 50 containers\n"
                "- Weight: 15 metric tons per container\n"
                "- Shipment type: FCL\n"
                "- Cargo: Electronics\n"
                "- Shipment date: 15th December 2024\n\n"
                "Please provide rates and transit time.\n\n"
                "Best regards,\n"
                "John Smith\n"
                "ABC Electronics Ltd."
            )
        }
    ]

def main():
    # Header
    st.markdown('<h1 class="main-header">🚢 AI Logistics Response Model</h1>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Input mode selection
        st.markdown("#### 📧 Input Mode")
        input_mode = st.radio(
            "Choose input mode:",
            ["Single Email", "Email Thread"],
            index=0,
            help="Single Email: Process one message. Email Thread: Process multiple messages in conversation order."
        )
        
        # Email details
        st.markdown("#### 📧 Email Details")
        sender_email = st.text_input("Sender Email", value="customer@example.com")
        thread_id = st.text_input("Thread ID", value=f"thread-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        
        # Model settings
        st.markdown("#### 🔧 Model Settings")
        show_debug = st.checkbox("Show Debug Information", value=False)
        
        # Action buttons in sidebar
        st.markdown("---")
        st.markdown("#### 🎯 Actions")
        
        if st.button("🔄 Reset", use_container_width=True):
            reset_session()
            st.rerun()
        
        st.markdown("---")
        st.markdown("**About:** This AI system processes logistics requests and generates appropriate responses.")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.markdown("### 📧 Input")
        
        # Email subject
        subject = st.text_input("Email Subject", value="Rate request for container shipment", placeholder="Enter email subject...")
        
        if input_mode == "Single Email":
            # Single email input
            default_email = (
                "Hi,\n\n"
                "We need to ship 50 containers from Jebel Ali to Mundra. \n"
                "Details as follows:\n"
                "- Container type: 20DC\n"
                "- Total quantity: 50 containers\n"
                "- Weight: 15 metric tons per container\n"
                "- Shipment type: FCL\n"
                "- Cargo: Electronics\n"
                "- Shipment date: 15th December 2024\n\n"
                "Please provide rates and transit time.\n\n"
                "Best regards,\n"
                "John Smith\n"
                "ABC Electronics Ltd."
            )
            
            email_text = st.text_area(
                "Email Content", 
                value=default_email,
                placeholder="Enter the email content here...",
                height=300
            )
            
            # Action buttons for single email
            st.markdown("### 🎯 Actions")
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if st.button("🚀 Process Email", type="primary", use_container_width=True):
                    if not email_text.strip():
                        st.error("Please enter email content to process.")
                    elif not subject.strip():
                        st.error("Please enter email subject.")
                    else:
                        with st.spinner("Processing email..."):
                            result, error = process_single_email(email_text, subject, sender_email, thread_id)
                            
                            if error:
                                st.error(f"Error processing email: {error}")
                                st.session_state.processed = False
                            else:
                                st.session_state.result = result
                                st.session_state.processed = True
                                st.success("Email processed successfully!")
                                st.rerun()
            
            with col_b:
                if st.button("🔄 Rerun", use_container_width=True):
                    if hasattr(st.session_state, 'processed') and st.session_state.processed:
                        with st.spinner("Reprocessing email..."):
                            result, error = process_single_email(email_text, subject, sender_email, thread_id)
                            
                            if error:
                                st.error(f"Error processing email: {error}")
                            else:
                                st.session_state.result = result
                                st.success("Email reprocessed successfully!")
                                st.rerun()
                    else:
                        st.warning("No previous result to rerun. Please process an email first.")
            
            with col_c:
                if st.button("📝 New Email", use_container_width=True):
                    st.rerun()
        
        else:
            # Thread input mode
            st.markdown("#### 📨 Email Thread")
            st.markdown("Add messages to the thread in chronological order (oldest first):")
            
            # Initialize thread in session state
            if 'message_thread' not in st.session_state:
                st.session_state.message_thread = []
            
            # Auto-load default content if thread is empty
            if not st.session_state.message_thread:
                st.info("💡 Tip: Click 'Load Default' to use the same content as Single Email mode, or 'Load Sample' for a confirmation example.")
            
            # Add message form
            with st.expander("➕ Add Message", expanded=True):
                msg_sender = st.text_input("Sender Email", value="customer@example.com", key="msg_sender")
                msg_timestamp = st.text_input("Timestamp", value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), key="msg_timestamp")
                msg_body = st.text_area("Message Body", placeholder="Enter message content...", height=150, key="msg_body")
                
                col_add, col_sample, col_default = st.columns(3)
                with col_add:
                    if st.button("Add Message", use_container_width=True):
                        if msg_body.strip() and msg_sender.strip():
                            new_message = {
                                "sender": msg_sender,
                                "timestamp": msg_timestamp,
                                "body": msg_body
                            }
                            st.session_state.message_thread.append(new_message)
                            st.success("Message added to thread!")
                            st.rerun()
                        else:
                            st.error("Please enter both sender and message body.")
                
                with col_sample:
                    if st.button("Load Sample", use_container_width=True):
                        st.session_state.message_thread = create_sample_thread()
                        st.success("Sample thread loaded!")
                        st.rerun()
                
                with col_default:
                    if st.button("Load Default", use_container_width=True):
                        st.session_state.message_thread = create_default_thread()
                        st.success("Default thread loaded!")
                        st.rerun()
            
            # Display current thread
            if st.session_state.message_thread:
                st.markdown("#### 📋 Current Thread")
                for i, msg in enumerate(st.session_state.message_thread):
                    with st.container():
                        st.markdown(f'<div class="thread-message">', unsafe_allow_html=True)
                        st.markdown(f"**Message {i+1}** - {msg['sender']} at {msg['timestamp']}")
                        st.text_area(f"Message {i+1} Content", value=msg['body'], height=100, disabled=True, label_visibility="collapsed")
                        
                        # Delete button
                        if st.button(f"🗑️ Delete", key=f"del_{i}", use_container_width=True):
                            st.session_state.message_thread.pop(i)
                            st.success("Message removed!")
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Process thread button
                st.markdown("### 🎯 Actions")
                col_a, col_b, col_c = st.columns(3)
                
                with col_a:
                    if st.button("🚀 Process Thread", type="primary", use_container_width=True):
                        if not subject.strip():
                            st.error("Please enter email subject.")
                        else:
                            with st.spinner("Processing thread..."):
                                result, error = process_email_thread(st.session_state.message_thread, subject, thread_id)
                                
                                if error:
                                    st.error(f"Error processing thread: {error}")
                                    st.session_state.processed = False
                                else:
                                    st.session_state.result = result
                                    st.session_state.processed = True
                                    st.success("Thread processed successfully!")
                                    st.rerun()
                
                with col_b:
                    if st.button("🔄 Rerun", use_container_width=True):
                        if hasattr(st.session_state, 'processed') and st.session_state.processed:
                            with st.spinner("Reprocessing thread..."):
                                result, error = process_email_thread(st.session_state.message_thread, subject, thread_id)
                                
                                if error:
                                    st.error(f"Error processing thread: {error}")
                                else:
                                    st.session_state.result = result
                                    st.success("Thread reprocessed successfully!")
                                    st.rerun()
                        else:
                            st.warning("No previous result to rerun. Please process a thread first.")
                
                with col_c:
                    if st.button("📝 New Thread", use_container_width=True):
                        st.session_state.message_thread = []
                        st.rerun()
            else:
                st.info("👆 Add messages to the thread using the form above.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="output-section">', unsafe_allow_html=True)
        st.markdown("### 📤 Output")
        
        if hasattr(st.session_state, 'processed') and st.session_state.processed:
            result = st.session_state.result
            
            # Display response in separate box
            if 'response' in result:
                response = result['response']
                
                st.markdown('<div class="response-box">', unsafe_allow_html=True)
                st.markdown("#### ✅ Generated Response")
                
                if 'response_subject' in response:
                    st.write(f"**Subject:** {response['response_subject']}")
                
                if 'response_body' in response:
                    st.write(response['response_body'])
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Display thread analysis results
            if 'confirmation' in result:
                confirmation = result['confirmation']
                st.markdown('<div class="response-box">', unsafe_allow_html=True)
                st.markdown("#### 🔍 Thread Analysis")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Confirmation Detected:** {confirmation.get('is_confirmation', False)}")
                    st.write(f"**Confirmation Type:** {confirmation.get('confirmation_type', 'N/A')}")
                    st.write(f"**Confidence:** {confirmation.get('confidence', 0):.2f}")
                
                with col_b:
                    st.write(f"**Message Index:** {confirmation.get('confirmation_message_index', 'N/A')}")
                    st.write(f"**Sender:** {confirmation.get('confirmation_sender', 'N/A')}")
                    st.write(f"**Detection Method:** {confirmation.get('detection_method', 'N/A')}")
                
                if confirmation.get('confirmation_details'):
                    st.write(f"**Details:** {confirmation['confirmation_details']}")
                
                if confirmation.get('reasoning'):
                    st.write(f"**Reasoning:** {confirmation['reasoning']}")
                
                if confirmation.get('key_phrases'):
                    st.write(f"**Key Phrases:** {', '.join(confirmation['key_phrases'])}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Display email sending results
            if 'customer_email' in result:
                customer_email = result['customer_email']
                st.markdown('<div class="response-box">', unsafe_allow_html=True)
                st.markdown("#### 📧 Customer Email")
                st.write(f"**Email Sent:** {customer_email.get('email_sent', False)}")
                st.write(f"**Status:** {customer_email.get('message', 'N/A')}")
                if customer_email.get('email_content'):
                    st.write("**Email Content:**")
                    st.text_area("Customer Email", value=customer_email['email_content']['body'], height=150, disabled=True, label_visibility="collapsed")
                st.markdown('</div>', unsafe_allow_html=True)
            
            if 'forwarder_email' in result:
                forwarder_email = result['forwarder_email']
                st.markdown('<div class="response-box">', unsafe_allow_html=True)
                st.markdown("#### 📧 Forwarder Email")
                st.write(f"**Email Sent:** {forwarder_email.get('email_sent', False)}")
                st.write(f"**Status:** {forwarder_email.get('message', 'N/A')}")
                if forwarder_email.get('email_content'):
                    st.write("**Email Content:**")
                    st.text_area("Forwarder Email", value=forwarder_email['email_content']['body'], height=150, disabled=True, label_visibility="collapsed")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Display detailed agent information
            st.markdown("### 🔍 Agent Details")
            
            # Classification Agent
            if 'classification' in result:
                with st.expander("📧 Classification Agent", expanded=False):
                    classification = result['classification']
                    st.write("**Email Classification Results:**")
                    st.json(classification)
            
            # Extraction Agent
            if 'extraction' in result:
                with st.expander("🔍 Extraction Agent", expanded=False):
                    extraction = result['extraction']
                    st.write("**Extracted Information:**")
                    st.json(extraction)
            
            # Validation Agent
            if 'validation' in result:
                with st.expander("✅ Validation Agent", expanded=False):
                    validation = result['validation']
                    st.write("**Validation Results:**")
                    st.json(validation)
            
            # Smart Clarification Agent
            if 'smart_clarification' in result:
                with st.expander("❓ Smart Clarification Agent", expanded=False):
                    clarification = result['smart_clarification']
                    st.write("**Clarification Questions:**")
                    st.json(clarification)
            
            # Confirmation Agent
            if 'confirmation' in result:
                with st.expander("✅ Confirmation Agent", expanded=False):
                    confirmation = result['confirmation']
                    st.write("**Confirmation Detection:**")
                    st.json(confirmation)
            
            # Container Standardization Agent
            if 'container_standardization' in result:
                with st.expander("📦 Container Standardization Agent", expanded=False):
                    container = result['container_standardization']
                    st.write("**Container Standardization:**")
                    st.json(container)
            
            # Port Lookup Agent
            if 'port_lookup' in result:
                with st.expander("🌍 Port Lookup Agent", expanded=False):
                    port = result['port_lookup']
                    st.write("**Port Lookup Results:**")
                    st.json(port)
            
            # Rate Parser Agent
            if 'rate_parser' in result:
                with st.expander("💰 Rate Parser Agent", expanded=False):
                    rate_parser = result['rate_parser']
                    st.write("**Rate Parsing Results:**")
                    st.json(rate_parser)
            
            # Rate Recommendation Agent
            if 'rate_recommendation' in result:
                with st.expander("💡 Rate Recommendation Agent", expanded=False):
                    rate_rec = result['rate_recommendation']
                    st.write("**Rate Recommendations:**")
                    st.json(rate_rec)
            
            # Forwarder Assignment Agent
            if 'forwarder_assignment' in result:
                with st.expander("👤 Forwarder Assignment Agent", expanded=False):
                    forwarder = result['forwarder_assignment']
                    st.write("**Forwarder Assignment:**")
                    st.json(forwarder)
            
            # Country Extractor Agent
            if 'country_extractor' in result:
                with st.expander("🌍 Country Extractor Agent", expanded=False):
                    country = result['country_extractor']
                    st.write("**Country Extraction:**")
                    st.json(country)
            
            # Display rate information
            if 'rate' in result:
                rate = result['rate']
                
                st.markdown('<div class="rate-box">', unsafe_allow_html=True)
                st.markdown("#### 💰 Rate Information")
                
                if rate and isinstance(rate, dict):
                    if 'indicative_rate' in rate and rate['indicative_rate']:
                        st.write(f"**Indicative Rate:** {rate['indicative_rate']}")
                    elif 'rate_recommendation' in rate and rate['rate_recommendation'].get('rate_range'):
                        st.write(f"**Rate Range:** {rate['rate_recommendation']['rate_range']}")
                    
                    if 'rate_recommendation' in rate:
                        recommendation = rate['rate_recommendation']
                        if 'match_type' in recommendation:
                            st.write(f"**Match Type:** {recommendation['match_type']}")
                        if 'total_rates_found' in recommendation:
                            st.write(f"**Rates Found:** {recommendation['total_rates_found']}")
                    
                    if 'data_source' in rate:
                        st.write(f"**Data Source:** {rate['data_source']}")
                    
                    if 'query' in rate:
                        query = rate['query']
                        st.write(f"**Query:** {query.get('Origin_Code', 'N/A')} → {query.get('Destination_Code', 'N/A')} ({query.get('Container_Type', 'N/A')})")
                else:
                    st.write("**Status:** No rate information available")
                    st.write("**Reason:** Port codes or container type not found in rate database")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Display key information in compact format
            st.markdown('<div class="summary-box">', unsafe_allow_html=True)
            st.markdown("#### 📊 Processing Summary")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if 'classification' in result:
                    classification = result['classification']
                    st.write(f"**Email Type:** {classification.get('email_type', 'N/A')}")
                    st.write(f"**Confidence:** {classification.get('confidence', 'N/A')}")
                
                if 'extraction' in result:
                    extraction = result['extraction']
                    st.write(f"**Origin:** {extraction.get('origin', 'N/A')}")
                    st.write(f"**Destination:** {extraction.get('destination', 'N/A')}")
            
            with col_b:
                if 'validation' in result:
                    validation = result['validation']
                    st.write(f"**Validity:** {validation.get('overall_validity', 'N/A')}")
                    st.write(f"**Missing Fields:** {len(validation.get('missing_fields', []))}")
                
                if 'forwarder_assignment' in result:
                    forwarder = result['forwarder_assignment']
                    st.write(f"**Forwarder:** {forwarder.get('assigned_forwarder', 'N/A')}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Debug information (if enabled)
            if show_debug:
                with st.expander("🔧 Full Debug Information"):
                    st.json(result)
        
        else:
            st.info("👈 Enter email content and click 'Process Email' to see results.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown("AI Logistics Response Model - Powered by Streamlit")
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
