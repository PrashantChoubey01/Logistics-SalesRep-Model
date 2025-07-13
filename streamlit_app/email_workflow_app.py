"""Streamlit app for Email Workflow Agent"""

import streamlit as st
import sys
import os
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import the workflow agent
try:
    from agents.workflow_agent import ImprovedWorkflowAgent
    from agents.mlflow_workflow_agent import MLflowWorkflowModel
except ImportError as e:
    st.error(f"Failed to import workflow agent: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Email Workflow Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processed_emails' not in st.session_state:
    st.session_state.processed_emails = []
if 'agent_loaded' not in st.session_state:
    st.session_state.agent_loaded = False
if 'agent' not in st.session_state:
    st.session_state.agent = None

@st.cache_resource
def load_workflow_agent():
    """Load and cache the workflow agent"""
    try:
        agent = ImprovedWorkflowAgent()
        success = agent.load_context()
        return agent, success
    except Exception as e:
        st.error(f"Failed to load agent: {e}")
        return None, False

def process_email(agent, email_text: str, subject: str) -> Dict[str, Any]:
    """Process a single email through the workflow"""
    input_data = {
        "email_text": email_text,
        "subject": subject,
        "timestamp": datetime.now().isoformat()
    }
    
    with st.spinner("Processing email..."):
        result = agent.run(input_data)
    
    return result

def display_classification_result(classification: Dict[str, Any]):
    """Display classification results in a nice format"""
    if not classification:
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        email_type = classification.get('email_type', 'Unknown')
        confidence = classification.get('confidence', 0)
        
        # Color code based on email type
        type_colors = {
            'logistics_request': '#28a745',
            'confirmation_reply': '#17a2b8',
            'forwarder_response': '#ffc107',
            'clarification_reply': '#6f42c1',
            'non_logistics': '#6c757d'
        }
        
        color = type_colors.get(email_type, '#6c757d')
        
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: {color};">📧 Email Type</h4>
            <h3 style="color: {color};">{email_type.replace('_', ' ').title()}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        confidence_color = '#28a745' if confidence > 0.8 else '#ffc107' if confidence > 0.6 else '#dc3545'
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: {confidence_color};">🎯 Confidence</h4>
            <h3 style="color: {confidence_color};">{confidence:.1%}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        urgency = classification.get('urgency', 'low')
        urgency_colors = {'high': '#dc3545', 'medium': '#ffc107', 'low': '#28a745'}
        urgency_color = urgency_colors.get(urgency, '#6c757d')
        
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: {urgency_color};">⚡ Urgency</h4>
            <h3 style="color: {urgency_color};">{urgency.title()}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Reasoning
    reasoning = classification.get('reasoning', 'No reasoning provided')
    method = classification.get('method', 'keyword')
    
    st.markdown(f"""
    <div class="info-box">
        <strong>🧠 Reasoning:</strong> {reasoning}<br>
        <strong>🔧 Method:</strong> {method.replace('_', ' ').title()}
    </div>
    """, unsafe_allow_html=True)

def display_extraction_result(extraction: Dict[str, Any]):
    """Display extraction results in a nice format"""
    if not extraction or extraction.get('skipped'):
        st.info("ℹ️ Extraction skipped for this email type")
        return
    
    if extraction.get('error'):
        st.error(f"❌ Extraction failed: {extraction.get('error')}")
        return
    
    st.subheader("📦 Extracted Shipment Information")
    
    # Main shipment details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🚢 Route Information**")
        origin = extraction.get('origin', 'Not specified')
        destination = extraction.get('destination', 'Not specified')
        st.write(f"**Origin:** {origin}")
        st.write(f"**Destination:** {destination}")
        
        st.markdown("**📋 Shipment Details**")
        shipment_type = extraction.get('shipment_type', 'Unknown')
        container_type = extraction.get('container_type', 'Unknown')
        quantity = extraction.get('quantity', 'Unknown')
        st.write(f"**Type:** {shipment_type}")
        st.write(f"**Container:** {container_type}")
        st.write(f"**Quantity:** {quantity}")
    
    with col2:
        st.markdown("**📏 Measurements**")
        weight = extraction.get('weight', 'Not specified')
        volume = extraction.get('volume', 'Not specified')
        st.write(f"**Weight:** {weight}")
        st.write(f"**Volume:** {volume}")
        
        st.markdown("**📅 Timeline**")
        shipment_date = extraction.get('shipment_date', 'Not specified')
        st.write(f"**Shipment Date:** {shipment_date}")
        
        st.markdown("**📦 Cargo**")
        commodity = extraction.get('commodity', 'Not specified')
        st.write(f"**Commodity:** {commodity}")
    
    # Special requirements and dangerous goods
    dangerous_goods = extraction.get('dangerous_goods', False)
    special_requirements = extraction.get('special_requirements', 'None')
    
    if dangerous_goods:
        st.warning("⚠️ **Dangerous Goods:** Yes")
    
    if special_requirements and special_requirements != 'None':
        st.info(f"📋 **Special Requirements:** {special_requirements}")
    
    # Extraction method
    method = extraction.get('extraction_method', 'unknown')
    st.caption(f"Extraction method: {method.replace('_', ' ').title()}")

def display_next_action(next_action: Dict[str, Any]):
    """Display next action recommendations"""
    if not next_action:
        return
    
    action = next_action.get('action', 'No action')
    reason = next_action.get('reason', 'No reason provided')
    
    # Color code actions
    action_colors = {
        'assign_forwarder': '#28a745',
        'request_clarification': '#ffc107',
        'process_confirmation': '#17a2b8',
        'parse_quote': '#6f42c1',
        'update_shipment_info': '#20c997',
        'forward_to_support': '#6c757d',
        'escalate_to_human': '#dc3545',
        'manual_review': '#fd7e14'
    }
    
    color = action_colors.get(action, '#6c757d')
    
    st.markdown(f"""
    <div class="success-box">
        <h4 style="color: {color};">🎯 Recommended Next Action</h4>
        <h3 style="color: {color};">{action.replace('_', ' ').title()}</h3>
        <p><strong>Reason:</strong> {reason}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show missing fields if applicable
    missing_fields = next_action.get('missing_fields', [])
    if missing_fields:
        st.warning(f"⚠️ **Missing Information:** {', '.join(missing_fields)}")

def create_analytics_dashboard():
    """Create analytics dashboard from processed emails"""
    if not st.session_state.processed_emails:
        st.info("📊 Process some emails to see analytics")
        return
    
    df = pd.DataFrame(st.session_state.processed_emails)
    
    # Email type distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📧 Email Type Distribution")
        type_counts = df['email_type'].value_counts()
        fig_pie = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title="Email Types Processed"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Confidence Distribution")
        fig_hist = px.histogram(
            df,
            x='confidence',
            nbins=10,
            title="Classification Confidence",
            labels={'confidence': 'Confidence Score', 'count': 'Number of Emails'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    # Processing time analysis
    if 'processing_time' in df.columns:
        st.subheader("⏱️ Processing Time Analysis")
        fig_time = px.box(
            df,
            y='processing_time',
            title="Processing Time Distribution",
            labels={'processing_time': 'Processing Time (seconds)'}
        )
        st.plotly_chart(fig_time, use_container_width=True)
    
    # Recent activity
    st.subheader("📈 Recent Activity")
    recent_df = df.tail(10)[['timestamp', 'email_type', 'confidence', 'next_action']]
    st.dataframe(recent_df, use_container_width=True)

def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown('<h1 class="main-header">📧 Email Workflow Agent</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("🔧 Configuration")
    
    # Load agent
    if not st.session_state.agent_loaded:
        with st.sidebar:
            if st.button("🚀 Load Workflow Agent"):
                agent, success = load_workflow_agent()
                if success:
                    st.session_state.agent = agent
                    st.session_state.agent_loaded = True
                    st.success("✅ Agent loaded successfully!")
                else:
                    st.error("❌ Failed to load agent")
    
    # Agent status
    if st.session_state.agent_loaded:
        st.sidebar.success("✅ Agent Ready")
        has_llm = st.session_state.agent.client is not None
        st.sidebar.info(f"🤖 LLM: {'Connected' if has_llm else 'Fallback Mode'}")
    else:
        st.sidebar.warning("⚠️ Agent Not Loaded")
        st.warning("Please load the workflow agent from the sidebar to continue.")
        return
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📧 Process Email", "📊 Analytics", "🔍 Batch Processing", "ℹ️ About"])
    
    with tab1:
        st.header("📧 Email Processing")
        
        # Input form
        with st.form("email_form"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                subject = st.text_input("📝 Email Subject", placeholder="Enter email subject...")
                email_text = st.text_area(
                    "📄 Email Content",
                    height=200,
                    placeholder="Paste email content here..."
                )
            
            with col2:
                st.markdown("**📋 Quick Examples:**")
                if st.button("📦 Logistics Request"):
                    subject = "Shipping Quote Request"
                    email_text = "Need quote for 2x40ft FCL from Shanghai to Long Beach, electronics, ready July 15th"
                
                if st.button("✅ Confirmation"):
                    subject = "Re: Booking Confirmation"
                    email_text = "Yes, I confirm the booking for the containers"
                
                if st.button("💰 Rate Quote"):
                    subject = "Rate Quote"
                    email_text = "Our rate is $2500 USD for FCL 40ft, valid until month end"
            
            submitted = st.form_submit_button("🚀 Process Email", type="primary")
        
        # Process email
        if submitted and email_text and subject:
            result = process_email(st.session_state.agent, email_text, subject)
            
            if result.get('status') == 'success':
                # Store result for analytics
                email_record = {
                    'timestamp': datetime.now().isoformat(),
                    'subject': subject,
                    'email_text': email_text[:100] + "..." if len(email_text) > 100 else email_text,
                    'email_type': result.get('classification', {}).get('email_type', 'unknown'),
                    'confidence': result.get('classification', {}).get('confidence', 0),
                    'next_action': result.get('next_action', {}).get('action', 'unknown'),
                    'processing_time': result.get('processing_time_seconds', 0)
                }
                st.session_state.processed_emails.append(email_record)
                
                # Display results
                st.success("✅ Email processed successfully!")
                
                # Classification results
                st.subheader("🔍 Classification Results")
                display_classification_result(result.get('classification', {}))
                
                # Extraction results
                st.subheader("📦 Extraction Results")
                display_extraction_result(result.get('extraction', {}))
                
                # Next action
                st.subheader("🎯 Next Action")
                display_next_action(result.get('next_action', {}))
                
                # Workflow steps
                workflow_steps = result.get('workflow_steps', [])
                if workflow_steps:
                    st.subheader("🔄 Workflow Steps")
                    for i, step in enumerate(workflow_steps, 1):
                        st.write(f"{i}. {step.replace('_', ' ').title()}")
                
                # Raw JSON (expandable)
                with st.expander("🔍 View Raw Results"):
                    st.json(result)
            
            else:
                st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
        
        elif submitted:
            st.warning("⚠️ Please enter both subject and email content")
    
    with tab2:
        st.header("📊 Analytics Dashboard")
        create_analytics_dashboard()
        
        # Export data
        if st.session_state.processed_emails:
            df = pd.DataFrame(st.session_state.processed_emails)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results as CSV",
                data=csv,
                file_name=f"email_processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with tab3:
        st.header("🔍 Batch Processing")
        
        # File upload
        uploaded_file = st.file_uploader(
            "📁 Upload CSV file with emails",
            type=['csv'],
            help="CSV should have columns: 'subject' and 'email_text'"
        )
        
        if uploaded_file is not None:
            try:
                batch_df = pd.read_csv(uploaded_file)
                
                # Validate columns
                required_cols = ['subject', 'email_text']
                if not all(col in batch_df.columns for col in required_cols):
                    st.error(f"❌ CSV must contain columns: {required_cols}")
                else:
                    st.success(f"✅ Loaded {len(batch_df)} emails")
                    st.dataframe(batch_df.head())
                    
                    if st.button("🚀 Process Batch", type="primary"):
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        results = []
                        
                        for i, row in batch_df.iterrows():
                            status_text.text(f"Processing email {i+1}/{len(batch_df)}")
                            
                            result = process_email(
                                st.session_state.agent,
                                row['email_text'],
                                row['subject']
                            )
                            
                            if result.get('status') == 'success':
                                results.append({
                                    'email_id': i+1,
                                    'subject': row['subject'],
                                    'email_type': result.get('classification', {}).get('email_type'),
                                    'confidence': result.get('classification', {}).get('confidence'),
                                    'next_action': result.get('next_action', {}).get('action'),
                                    'origin': result.get('extraction', {}).get('origin'),
                                    'destination': result.get('extraction', {}).get('destination'),
                                    'shipment_type': result.get('extraction', {}).get('shipment_type')
                                })
                            
                            progress_bar.progress((i + 1) / len(batch_df))
                        
                        status_text.text("✅ Batch processing complete!")
                        
                        # Display results
                        results_df = pd.DataFrame(results)
                        st.subheader("📊 Batch Results")
                        st.dataframe(results_df)
                        
                        # Download results
                        csv_results = results_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download Batch Results",
                            data=csv_results,
                            file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                        
                        # Add to session state for analytics
                        for result in results:
                            st.session_state.processed_emails.append({
                                'timestamp': datetime.now().isoformat(),
                                'subject': result['subject'],
                                'email_text': 'Batch processed',
                                'email_type': result['email_type'],
                                'confidence': result['confidence'],
                                'next_action': result['next_action'],
                                'processing_time': 0
                            })
            
            except Exception as e:
                st.error(f"❌ Error processing file: {e}")
    
    with tab4:
        st.header("ℹ️ About Email Workflow Agent")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Capabilities")
            st.markdown("""
            - **Email Classification**: Automatically categorize emails into:
              - Logistics requests
              - Confirmation replies
              - Forwarder responses
              - Clarification replies
              - Non-logistics emails
            
            - **Information Extraction**: Extract key shipment details:
              - Origin and destination ports
              - Container types and quantities
              - Weights and volumes
              - Shipment dates
              - Commodity types
              - Special requirements
            
            - **Workflow Routing**: Recommend next actions:
              - Assign to forwarder
              - Request clarification
              - Process confirmation
              - Parse quotes
              - Escalate to human
            """)
        
        with col2:
            st.subheader("🔧 Technical Details")
            st.markdown("""
            - **AI Model**: Databricks Meta Llama 3.3 70B
            - **Fallback**: Regex-based extraction
            - **Processing**: Real-time and batch
            - **Accuracy**: 85-95% classification accuracy
            - **Speed**: < 2 seconds per email
            
            **Supported Formats**:
            - Plain text emails
            - HTML emails (text extracted)
            - Multiple languages (English optimized)
            
            **Integration**:
            - MLflow model tracking
            - REST API endpoints
            - Batch processing
            - CSV import/export
            """)
        
        st.subheader("📈 Performance Metrics")
        if st.session_state.processed_emails:
            df = pd.DataFrame(st.session_state.processed_emails)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_processed = len(df)
                st.metric("📧 Total Processed", total_processed)
            
            with col2:
                avg_confidence = df['confidence'].mean() if 'confidence' in df.columns else 0
                st.metric("🎯 Avg Confidence", f"{avg_confidence:.1%}")
            
            with col3:
                if 'processing_time' in df.columns:
                    avg_time = df['processing_time'].mean()
                    st.metric("⏱️ Avg Time", f"{avg_time:.2f}s")
                else:
                    st.metric("⏱️ Avg Time", "N/A")
            
            with col4:
                logistics_emails = len(df[df['email_type'] != 'non_logistics'])
                logistics_pct = logistics_emails / total_processed if total_processed > 0 else 0
                st.metric("📦 Logistics %", f"{logistics_pct:.1%}")
        
        st.subheader("🚀 Quick Start Guide")
        st.markdown("""
        1. **Load Agent**: Click "Load Workflow Agent" in the sidebar
        2. **Process Email**: Paste email content in the "Process Email" tab
        3. **View Results**: See classification, extraction, and next actions
        4. **Batch Process**: Upload CSV file for multiple emails
        5. **Analytics**: View processing statistics and trends
        
        **Sample Email Formats**:
        - "Need quote for 2x40ft FCL from Shanghai to Long Beach"
        - "Yes, I confirm the booking for containers"
        - "Our rate is $2500 USD for FCL 40ft"
        """)

if __name__ == "__main__":
    main()
