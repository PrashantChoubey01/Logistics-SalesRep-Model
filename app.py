#!/usr/bin/env python3
"""
LangGraph Orchestrator Streamlit App
====================================

A comprehensive Streamlit application that showcases the LangGraph orchestrator
for the logistic AI response system with beautiful UI and detailed workflow monitoring.
"""

import streamlit as st
import json
import time
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the LangGraph orchestrator
try:
    from langgraph_orchestrator import LangGraphOrchestrator
except ImportError as e:
    st.error(f"❌ Failed to import LangGraph orchestrator: {e}")
    st.stop()

# =====================================================
#                 🎨 PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="LangGraph Logistic AI Orchestrator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
#                 🎨 CUSTOM CSS
# =====================================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .workflow-node {
        background: #f8f9fa;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .workflow-node.completed {
        background: #d4edda;
        border-color: #28a745;
    }
    
    .workflow-node.error {
        background: #f8d7da;
        border-color: #dc3545;
    }
    
    .workflow-node.current {
        background: #fff3cd;
        border-color: #ffc107;
        box-shadow: 0 0 10px rgba(255, 193, 7, 0.3);
    }
    
    .metric-card {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    
    .workflow-graph {
        background: white;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .email-preview {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    
    .sidebar-section {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
#                 🏗️ HELPER FUNCTIONS
# =====================================================

def create_workflow_visualization(workflow_history, current_node=None, errors=None):
    """Create a visual representation of the workflow"""
    
    # Define node positions for the graph
    node_positions = {
        'EMAIL_INPUT': (0, 0),
        'CONVERSATION_STATE_ANALYSIS': (1, 0),
        'CLASSIFICATION': (2, 0),
        'DATA_EXTRACTION': (3, 0),
        'DATA_ENRICHMENT': (4, 0),
        'VALIDATION': (5, 0),
        'RATE_RECOMMENDATION': (6, 0),
        'DECISION_NODE': (7, 0),
        'CLARIFICATION_REQUEST': (8, -1),
        'CONFIRMATION_REQUEST': (8, 0),
        'FORWARDER_ASSIGNMENT': (8, 1),
        'FORWARDER_EMAIL_GENERATION': (9, 1),
        'RATE_COLLATION': (9, 0),
        'ESCALATION': (9, -1)
    }
    
    # Create the graph
    fig = go.Figure()
    
    # Add nodes
    for node, (x, y) in node_positions.items():
        # Determine node color based on status
        if node in workflow_history:
            if errors and any(error for error in errors if node in str(error)):
                color = '#dc3545'  # Red for errors
            elif node == current_node:
                color = '#ffc107'  # Yellow for current
            else:
                color = '#28a745'  # Green for completed
        else:
            color = '#6c757d'  # Gray for not started
        
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(size=30, color=color, line=dict(width=2, color='white')),
            text=[node.replace('_', '\n')],
            textposition="middle center",
            textfont=dict(size=8, color='white'),
            name=node,
            showlegend=False
        ))
    
    # Add edges (workflow connections)
    edges = [
        ('EMAIL_INPUT', 'CONVERSATION_STATE_ANALYSIS'),
        ('CONVERSATION_STATE_ANALYSIS', 'CLASSIFICATION'),
        ('CLASSIFICATION', 'DATA_EXTRACTION'),
        ('DATA_EXTRACTION', 'DATA_ENRICHMENT'),
        ('DATA_ENRICHMENT', 'VALIDATION'),
        ('VALIDATION', 'RATE_RECOMMENDATION'),
        ('RATE_RECOMMENDATION', 'DECISION_NODE'),
        ('DECISION_NODE', 'CLARIFICATION_REQUEST'),
        ('DECISION_NODE', 'CONFIRMATION_REQUEST'),
        ('DECISION_NODE', 'FORWARDER_ASSIGNMENT'),
        ('DECISION_NODE', 'RATE_COLLATION'),
        ('DECISION_NODE', 'ESCALATION'),
        ('FORWARDER_ASSIGNMENT', 'FORWARDER_EMAIL_GENERATION')
    ]
    
    for start_node, end_node in edges:
        if start_node in node_positions and end_node in node_positions:
            x1, y1 = node_positions[start_node]
            x2, y2 = node_positions[end_node]
            
            # Determine edge color
            if start_node in workflow_history and end_node in workflow_history:
                edge_color = '#28a745'
            else:
                edge_color = '#dee2e6'
            
            fig.add_trace(go.Scatter(
                x=[x1, x2], y=[y1, y2],
                mode='lines',
                line=dict(color=edge_color, width=2),
                showlegend=False
            ))
    
    # Update layout
    fig.update_layout(
        title="LangGraph Workflow Visualization",
        xaxis=dict(showgrid=False, showticklabels=False, range=[-0.5, 9.5]),
        yaxis=dict(showgrid=False, showticklabels=False, range=[-1.5, 1.5]),
        height=400,
        margin=dict(l=0, r=0, t=50, b=0),
        plot_bgcolor='white'
    )
    
    return fig

def format_email_preview(email_data):
    """Format email data for preview"""
    preview = f"""
From: {email_data.get('sender', 'Unknown')}
Subject: {email_data.get('subject', 'No Subject')}
Thread ID: {email_data.get('thread_id', 'No Thread ID')}
Timestamp: {email_data.get('timestamp', 'Unknown')}

Content:
{email_data.get('email_text', 'No content')}
"""
    return preview

def create_metrics_dashboard(result):
    """Create a metrics dashboard"""
    summary = result.get('final_state', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Total Nodes</div>
        </div>
        """.format(len(summary.get('workflow_history', []))), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Errors</div>
        </div>
        """.format(len(summary.get('errors', []))), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Confidence</div>
        </div>
        """.format(f"{summary.get('confidence_score', 0):.1%}"), unsafe_allow_html=True)
    
    with col4:
        status = "✅ Complete" if result.get('workflow_complete', False) else "⏳ In Progress"
        status_class = "status-success" if result.get('workflow_complete', False) else "status-warning"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{status}</div>
            <div class="metric-label">Status</div>
        </div>
        """, unsafe_allow_html=True)

# =====================================================
#                 🎯 MAIN APPLICATION
# =====================================================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚀 LangGraph Logistic AI Orchestrator</h1>
        <p>Intelligent workflow orchestration for logistic AI response system</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Email input section
        st.markdown("### 📧 Email Input")
        email_text = st.text_area(
            "Email Content",
            height=200,
            placeholder="Enter the email content here...",
            help="Paste the email content that needs to be processed"
        )
        
        # Email Thread History
        st.markdown("### 📧 Email Thread History")
        
        # Initialize thread history if not exists
        if 'email_thread_history' not in st.session_state:
            st.session_state.email_thread_history = []
        
        # Display current thread as structured JSON
        if st.session_state.email_thread_history:
            with st.expander("📚 Current Email Thread (JSON)", expanded=False):
                st.json(st.session_state.email_thread_history)
        
        # Show formatted thread for reference
        email_thread = st.text_area(
            "Formatted Email Thread (Most Recent First)",
            value=st.session_state.get('email_thread', ''),
            height=200,
            placeholder="Email thread will be built here automatically...",
            help="Complete email conversation history (most recent emails at top)"
        )
        
        # Email metadata
        st.markdown("### 📋 Email Metadata")
        col1, col2 = st.columns(2)
        
        with col1:
            subject = st.text_input("Subject", value="Rate Request")
            sender = st.text_input("Sender", value="customer@example.com")
        
        with col2:
            thread_id = st.text_input("Thread ID", value=f"thread-{int(time.time())}")
            timestamp = st.text_input("Timestamp", value=datetime.now().isoformat())
        
        # Processing options
        st.markdown("### 🔧 Processing Options")
        enable_debug = st.checkbox("Enable Debug Mode", value=True)
        show_workflow_viz = st.checkbox("Show Workflow Visualization", value=True)
        
        # Process button
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            process_button = st.button("🚀 Process Email", type="primary", use_container_width=True)
        
        with col2:
            clear_thread_button = st.button("🗑️ Clear Thread", use_container_width=True)
            
        # Clear thread if button clicked
        if clear_thread_button:
            st.session_state.email_thread = ""
            st.session_state.email_thread_history = []
            st.rerun()
    
    # Main content area
    if process_button and email_text:
        # Initialize orchestrator
        with st.spinner("🔄 Initializing LangGraph orchestrator..."):
            try:
                orchestrator = LangGraphOrchestrator()
                st.success("✅ LangGraph orchestrator initialized successfully!")
            except Exception as e:
                st.error(f"❌ Failed to initialize orchestrator: {e}")
                return
        
        # Combine new email with existing thread
        if st.session_state.email_thread_history:
            # Build full email content from structured history
            full_email_content = f"""
{email_text}

---
Previous Conversation:
"""
            # Add previous emails in reverse chronological order (most recent first, excluding current email)
            # Skip the first entry (current email) and show the rest in reverse order
            previous_emails = st.session_state.email_thread_history[1:]  # Exclude current email
            for email in previous_emails:
                full_email_content += f"""
From: {email['sender']}
Subject: {email['subject']}
Date: {email['timestamp']}

{email['content']}

"""
        else:
            full_email_content = email_text
        
        # Create structured email entry for customer email
        customer_email_entry = {
            "timestamp": timestamp,
            "sender": sender,
            "subject": subject,
            "content": email_text,
            "type": "customer",
            "thread_id": thread_id
        }
        
        # Add customer email to structured thread history (most recent first)
        st.session_state.email_thread_history.insert(0, customer_email_entry)
        
        # Update formatted thread for backward compatibility (most recent first)
        new_email_formatted = f"""
From: {sender}
Subject: {subject}
Date: {timestamp}

{email_text}

"""
        
        if email_thread:
            # Add new email at the top (most recent first)
            st.session_state.email_thread = new_email_formatted + "---\n" + email_thread
        else:
            # First email
            st.session_state.email_thread = new_email_formatted.strip()
        
        # Prepare email data with full thread
        email_data = {
            'email_text': full_email_content,
            'subject': subject,
            'sender': sender,
            'thread_id': thread_id,
            'timestamp': timestamp
        }
        
        # Process email
        with st.spinner("🔄 Processing email through LangGraph workflow..."):
            try:
                result = orchestrator.orchestrate_workflow(email_data)
                
                if result.get('status') == 'success':
                    st.success("✅ Email processed successfully!")
                else:
                    st.error(f"❌ Processing failed: {result.get('error')}")
                    return
                    
            except Exception as e:
                st.error(f"❌ Processing error: {e}")
                return
        
        # Display results
        st.markdown("## 📊 Processing Results")
        
        # Show current thread status
        if st.session_state.email_thread_history:
            with st.expander("📧 Current Email Thread", expanded=False):
                st.markdown("**Structured conversation history being processed:**")
                
                # Display thread summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    customer_emails = len([e for e in st.session_state.email_thread_history if e['type'] == 'customer'])
                    st.metric("Customer Emails", customer_emails)
                
                with col2:
                    bot_responses = len([e for e in st.session_state.email_thread_history if e['type'] == 'bot'])
                    st.metric("Bot Responses", bot_responses)
                
                with col3:
                    total_emails = len(st.session_state.email_thread_history)
                    st.metric("Total Messages", total_emails)
                
                # Show thread timeline (most recent first)
                st.markdown("### 📅 Thread Timeline (Most Recent First)")
                for i, email in enumerate(st.session_state.email_thread_history):
                    if email['type'] == 'customer':
                        st.markdown(f"**{i+1}. 📧 Customer** - {email['timestamp']} - {email['subject']}")
                    else:
                        st.markdown(f"**{i+1}. 🤖 Bot** - {email['timestamp']} - {email.get('response_type', 'response')}")
                
                # Show complete thread content
                st.markdown("### 📝 Complete Thread Content")
                complete_thread_content = ""
                for email in st.session_state.email_thread_history:
                    if email['type'] == 'customer':
                        complete_thread_content += f"""
From: {email['sender']}
Subject: {email['subject']}
Date: {email['timestamp']}

{email['content']}

"""
                    else:
                        complete_thread_content += f"""
From: {email['sender']}
Subject: {email['subject']}
Date: {email['timestamp']}

{email['content']}

"""
                
                st.text_area("Thread Content", value=complete_thread_content.strip(), height=300, disabled=True)
        
        # Metrics dashboard
        create_metrics_dashboard(result)
        
        # Workflow visualization
        if show_workflow_viz:
            st.markdown("## 🔄 Workflow Visualization")
            
            final_state = result.get('final_state', {})
            workflow_history = final_state.get('workflow_history', [])
            current_node = final_state.get('current_node', '')
            errors = final_state.get('errors', [])
            
            fig = create_workflow_visualization(workflow_history, current_node, errors)
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed workflow information
        st.markdown("## 📋 Workflow Details")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Workflow history
            st.markdown("### 🔄 Workflow History")
            workflow_history = result.get('final_state', {}).get('workflow_history', [])
            
            for i, node in enumerate(workflow_history):
                status_icon = "✅" if i < len(workflow_history) - 1 else "🔄"
                st.markdown(f"{status_icon} **{node}**")
            
            # Current status
            st.markdown("### 📈 Current Status")
            final_state = result.get('final_state', {})
            
            status_data = {
                "Conversation State": final_state.get('conversation_state', 'N/A'),
                "Email Type": final_state.get('email_type', 'N/A'),
                "Intent": final_state.get('intent', 'N/A'),
                "Confidence Score": f"{final_state.get('confidence_score', 0):.1%}",
                "Next Action": final_state.get('next_action', 'N/A'),
                "Workflow Complete": "Yes" if result.get('workflow_complete', False) else "No"
            }
            
            for key, value in status_data.items():
                st.markdown(f"**{key}:** {value}")
        
        with col2:
            # Errors and warnings
            st.markdown("### ⚠️ Issues")
            
            errors = result.get('final_state', {}).get('errors', [])
            warnings = result.get('final_state', {}).get('warnings', [])
            
            if errors:
                st.markdown("#### ❌ Errors")
                for error in errors:
                    st.error(error)
            
            if warnings:
                st.markdown("#### ⚠️ Warnings")
                for warning in warnings:
                    st.warning(warning)
            
            if not errors and not warnings:
                st.success("✅ No issues detected!")
        
        # Extracted data
        st.markdown("## 📊 Extracted Data")
        
        extracted_data = result.get('final_state', {}).get('extracted_data', {})
        if extracted_data:
            # Display in organized sections
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏠 Port Information")
                port_data = {
                    "Origin Port": extracted_data.get('origin_port', 'N/A'),
                    "Origin Country": extracted_data.get('origin_country', 'N/A'),
                    "Destination Port": extracted_data.get('destination_port', 'N/A'),
                    "Destination Country": extracted_data.get('destination_country', 'N/A'),
                    "Origin (Full)": extracted_data.get('origin', 'N/A'),
                    "Destination (Full)": extracted_data.get('destination', 'N/A')
                }
                
                for key, value in port_data.items():
                    if value and value != 'N/A':
                        st.markdown(f"**{key}:** {value}")
                
                if not any(v and v != 'N/A' for v in port_data.values()):
                    st.info("No port information extracted")
            
            with col2:
                st.markdown("### 📦 Shipment Details")
                shipment_data = {
                    "Shipment Type": extracted_data.get('shipment_type', 'N/A'),
                    "Container Type": extracted_data.get('container_type', 'N/A'),
                    "Quantity": extracted_data.get('quantity', 'N/A'),
                    "Weight": extracted_data.get('weight', 'N/A'),
                    "Volume": extracted_data.get('volume', 'N/A'),
                    "Shipment Date": extracted_data.get('shipment_date', 'N/A'),
                    "Commodity": extracted_data.get('commodity', 'N/A')
                }
                
                for key, value in shipment_data.items():
                    if value and value != 'N/A':
                        st.markdown(f"**{key}:** {value}")
                
                if not any(v and v != 'N/A' for v in shipment_data.values()):
                    st.info("No shipment details extracted")
            
            # Additional information
            st.markdown("### 📋 Additional Information")
            additional_data = {
                "Customer Name": extracted_data.get('customer_name', 'N/A'),
                "Customer Company": extracted_data.get('customer_company', 'N/A'),
                "Customer Email": extracted_data.get('customer_email', 'N/A'),
                "Dangerous Goods": extracted_data.get('dangerous_goods', 'N/A'),
                "Insurance": extracted_data.get('insurance', 'N/A'),
                "Customs Clearance": extracted_data.get('customs_clearance', 'N/A'),
                "Special Requirements": extracted_data.get('special_requirements', 'N/A'),
                "Packaging": extracted_data.get('packaging', 'N/A'),
                "Delivery Address": extracted_data.get('delivery_address', 'N/A'),
                "Pickup Address": extracted_data.get('pickup_address', 'N/A')
            }
            
            col1, col2, col3 = st.columns(3)
            for i, (key, value) in enumerate(additional_data.items()):
                if value and value != 'N/A':
                    if i % 3 == 0:
                        col1.markdown(f"**{key}:** {value}")
                    elif i % 3 == 1:
                        col2.markdown(f"**{key}:** {value}")
                    else:
                        col3.markdown(f"**{key}:** {value}")
            
            # Show raw extracted data in expander
            with st.expander("🔍 Raw Extracted Data (JSON)"):
                st.json(extracted_data)
        else:
            st.info("No data extracted")
        
        # Enriched data
        st.markdown("## 🔧 Enriched Data")
        
        enriched_data = result.get('final_state', {}).get('enriched_data', {})
        if enriched_data:
            # Port Lookup Results
            if enriched_data.get('port_lookup'):
                st.markdown("### 🏠 Port Lookup Results")
                port_results = enriched_data['port_lookup'].get('results', [])
                if port_results:
                    port_df = pd.DataFrame([
                        {
                            "Port Name": port.get('port_name', 'N/A'),
                            "Port Code": port.get('port_code', 'N/A'),
                            "Country": port.get('country', 'N/A')
                        }
                        for port in port_results
                    ])
                    st.dataframe(port_df, use_container_width=True)
                else:
                    st.info("No port lookup results")
            
            # Container Standardization Results
            if enriched_data.get('container_standardization'):
                st.markdown("### 📦 Container Standardization")
                container_data = enriched_data['container_standardization']
                container_df = pd.DataFrame([
                    {
                        "Original Type": container_data.get('original_type', 'N/A'),
                        "Standard Type": container_data.get('standard_type', 'N/A'),
                        "Status": container_data.get('status', 'N/A')
                    }
                ])
                st.dataframe(container_df, use_container_width=True)
            
            # Rate Data Preparation
            if enriched_data.get('rate_data'):
                st.markdown("### 💰 Rate Data Prepared")
                rate_data = enriched_data['rate_data']
                rate_df = pd.DataFrame([
                    {
                        "Origin Name": rate_data.get('origin_name', 'N/A'),
                        "Origin Code": rate_data.get('origin_code', 'N/A'),
                        "Destination Name": rate_data.get('destination_name', 'N/A'),
                        "Destination Code": rate_data.get('destination_code', 'N/A'),
                        "Container Type": rate_data.get('container_type', 'N/A')
                    }
                ])
                st.dataframe(rate_df, use_container_width=True)
        else:
            st.info("No enriched data available")
        
        # Validation results
        st.markdown("## ✅ Validation Results")
        
        validation_results = result.get('final_state', {}).get('validation_results', {})
        if validation_results:
            port_validation = validation_results.get('validation_results', {})
            if port_validation:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("### 🏠 Origin Port")
                    origin_validation = port_validation.get('origin_port', {})
                    if origin_validation:
                        is_valid = origin_validation.get('is_valid', False)
                        confidence = origin_validation.get('confidence', 0)
                        notes = origin_validation.get('validation_notes', 'N/A')
                        
                        if is_valid:
                            st.success(f"✅ Valid (confidence: {confidence:.1%})")
                        else:
                            st.error(f"❌ Invalid (confidence: {confidence:.1%})")
                        
                        st.info(f"**Notes:** {notes}")
                    else:
                        st.warning("No validation data")
                
                with col2:
                    st.markdown("### 🏠 Destination Port")
                    destination_validation = port_validation.get('destination_port', {})
                    if destination_validation:
                        is_valid = destination_validation.get('is_valid', False)
                        confidence = destination_validation.get('confidence', 0)
                        notes = destination_validation.get('validation_notes', 'N/A')
                        
                        if is_valid:
                            st.success(f"✅ Valid (confidence: {confidence:.1%})")
                        else:
                            st.error(f"❌ Invalid (confidence: {confidence:.1%})")
                        
                        st.info(f"**Notes:** {notes}")
                    else:
                        st.warning("No validation data")
                
                with col3:
                    st.markdown("### 📦 Container Type")
                    container_validation = port_validation.get('container_type', {})
                    if container_validation:
                        is_valid = container_validation.get('is_valid', False)
                        confidence = container_validation.get('confidence', 0)
                        notes = container_validation.get('validation_notes', 'N/A')
                        
                        if is_valid:
                            st.success(f"✅ Valid (confidence: {confidence:.1%})")
                        else:
                            st.error(f"❌ Invalid (confidence: {confidence:.1%})")
                        
                        st.info(f"**Notes:** {notes}")
                    else:
                        st.warning("No validation data")
            else:
                st.info("No port validation results available")
        else:
            st.info("No validation results available")
        
        # Rate recommendation
        st.markdown("## 💰 Rate Recommendation")
        
        rate_recommendation = result.get('final_state', {}).get('rate_recommendation', {})
        if rate_recommendation:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Rate Information")
                indicative_rate = rate_recommendation.get('indicative_rate', 'N/A')
                if indicative_rate:
                    st.success(f"**Indicative Rate:** {indicative_rate}")
                else:
                    st.warning("No indicative rate available")
                
                disclaimer = rate_recommendation.get('disclaimer', 'N/A')
                st.info(f"**Disclaimer:** {disclaimer}")
            
            with col2:
                st.markdown("### 🛣️ Route Information")
                route_info = rate_recommendation.get('route_info', {})
                if route_info:
                    route_data = {
                        "Origin": f"{route_info.get('origin_name', 'N/A')} ({route_info.get('origin_code', 'N/A')})",
                        "Destination": f"{route_info.get('destination_name', 'N/A')} ({route_info.get('destination_code', 'N/A')})",
                        "Container": route_info.get('container_type', 'N/A')
                    }
                    
                    for key, value in route_data.items():
                        st.markdown(f"**{key}:** {value}")
                else:
                    st.info("No route information available")
            
            # Show validation info if available
            validation_info = rate_recommendation.get('validation_info', {})
            if validation_info:
                st.markdown("### ✅ Validation Summary")
                validation_summary = []
                
                origin_val = validation_info.get('origin_port_validation', {})
                if origin_val:
                    is_valid = origin_val.get('is_valid', False)
                    validation_summary.append(f"Origin Port: {'✅ Valid' if is_valid else '❌ Invalid'}")
                
                dest_val = validation_info.get('destination_port_validation', {})
                if dest_val:
                    is_valid = dest_val.get('is_valid', False)
                    validation_summary.append(f"Destination Port: {'✅ Valid' if is_valid else '❌ Invalid'}")
                
                container_val = validation_info.get('container_type_validation', {})
                if container_val:
                    is_valid = container_val.get('is_valid', False)
                    validation_summary.append(f"Container Type: {'✅ Valid' if is_valid else '❌ Invalid'}")
                
                if validation_summary:
                    for summary in validation_summary:
                        st.markdown(f"**{summary}**")
        else:
            st.info("No rate recommendation available")
        
        # Final response details (metadata only, since content is shown in Latest Bot Response)
        st.markdown("## 📊 Response Details")
        
        final_response = result.get('final_response', {})
        if final_response:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### 📋 Response Metadata")
                metadata = {
                    "Response Type": final_response.get('response_type', 'N/A'),
                    "Tone": final_response.get('tone', 'N/A'),
                    "Urgency Level": final_response.get('urgency_level', 'N/A'),
                    "Follow Up Required": "Yes" if final_response.get('follow_up_required', False) else "No",
                    "Estimated Response Time": final_response.get('estimated_response_time', 'N/A')
                }
                
                for key, value in metadata.items():
                    st.markdown(f"**{key}:** {value}")
            
            with col2:
                st.markdown("### 👤 Sales Person Details")
                if 'sales_person_name' in final_response:
                    st.markdown(f"**Name:** {final_response.get('sales_person_name', 'N/A')}")
                    st.markdown(f"**Designation:** {final_response.get('sales_person_designation', 'N/A')}")
                    st.markdown(f"**Company:** {final_response.get('sales_person_company', 'N/A')}")
                    st.markdown(f"**Email:** {final_response.get('sales_person_email', 'N/A')}")
                    st.markdown(f"**Phone:** {final_response.get('sales_person_phone', 'N/A')}")
                else:
                    st.info("No sales person assigned")
            
            with col3:
                st.markdown("### 📈 Key Information")
                key_info = final_response.get('key_information_included', [])
                if key_info:
                    st.markdown("**Included in response:**")
                    for info in key_info:
                        st.markdown(f"• {info}")
                else:
                    st.info("No key information tracked")
        else:
            st.info("No final response generated")
        
        # Latest Bot Response Display
        st.markdown("## 🤖 Latest Bot Response")
        
        if final_response and 'response_body' in final_response:
            # Display the latest bot response prominently
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("### 📝 Response Content")
                st.markdown(final_response['response_body'])
            
            with col2:
                st.markdown("### 📊 Response Details")
                st.markdown(f"**Type:** {final_response.get('response_type', 'unknown')}")
                st.markdown(f"**Tone:** {final_response.get('tone', 'professional')}")
                st.markdown(f"**Urgency:** {final_response.get('urgency_level', 'normal')}")
                st.markdown(f"**Follow-up Required:** {'Yes' if final_response.get('follow_up_required', False) else 'No'}")
                st.markdown(f"**Response Time:** {final_response.get('estimated_response_time', 'N/A')}")
                
                # Sales person info
                if 'sales_person_name' in final_response:
                    st.markdown("### 👤 Assigned Sales Person")
                    st.markdown(f"**Name:** {final_response.get('sales_person_name', 'N/A')}")
                    st.markdown(f"**Email:** {final_response.get('sales_person_email', 'N/A')}")
                    st.markdown(f"**Phone:** {final_response.get('sales_person_phone', 'N/A')}")
        else:
            st.warning("No bot response generated")
        
        # Get current timestamp for bot response
        bot_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Add bot response to structured thread history (most recent first)
        if final_response and 'response_body' in final_response:
            bot_email_entry = {
                "timestamp": bot_timestamp,
                "sender": final_response.get('sales_person_email', 'logistics@company.com'),
                "subject": f"Re: {subject}",
                "content": final_response['response_body'],
                "type": "bot",
                "thread_id": thread_id,
                "response_type": final_response.get('response_type', 'unknown'),
                "next_action": result.get('final_state', {}).get('next_action', 'unknown')
            }
            # Insert bot response at the top (most recent first)
            st.session_state.email_thread_history.insert(0, bot_email_entry)
        
        # Email Thread History
        st.markdown("## 📧 Complete Email Thread History")
        
        if st.session_state.email_thread_history:
            # Show complete thread in chronological order (oldest to newest)
            st.markdown("### 📚 Full Conversation History")
            
            # Create complete thread display with proper numbering
            complete_thread_display = ""
            total_emails = len(st.session_state.email_thread_history)
            
            # Show emails in reverse chronological order (newest first)
            for i, email in enumerate(st.session_state.email_thread_history):
                email_number = i + 1
                
                if email['type'] == 'customer':
                    complete_thread_display += f"""
📧 CUSTOMER EMAIL #{email_number}
From: {email['sender']}
Subject: {email['subject']}
Date: {email['timestamp']}

{email['content']}

"""
                else:  # bot
                    complete_thread_display += f"""
🤖 BOT RESPONSE #{email_number}
From: {email['sender']}
Subject: {email['subject']}
Date: {email['timestamp']}
Type: {email.get('response_type', 'unknown')}
Action: {email.get('next_action', 'unknown')}

{email['content']}

"""
            
            # Add thread summary
            customer_count = len([e for e in st.session_state.email_thread_history if e['type'] == 'customer'])
            bot_count = len([e for e in st.session_state.email_thread_history if e['type'] == 'bot'])
            
            st.markdown(f"**Thread Summary:** {total_emails} total messages ({customer_count} customer emails, {bot_count} bot responses)")
            
            st.text_area(
                "Complete Email Thread",
                value=complete_thread_display.strip(),
                height=500,
                disabled=True,
                help="Complete email conversation history (newest to oldest)"
            )
            
            # Show thread timeline for quick reference
            with st.expander("📅 Thread Timeline", expanded=False):
                st.markdown("**Reverse Chronological Order (Newest to Oldest):**")
                for i, email in enumerate(st.session_state.email_thread_history):
                    email_number = i + 1
                    if email['type'] == 'customer':
                        st.markdown(f"**{email_number}. 📧 Customer** - {email['timestamp']} - {email['subject']}")
                    else:
                        st.markdown(f"**{email_number}. 🤖 Bot** - {email['timestamp']} - {email.get('response_type', 'response')}")
        else:
            st.info("No email thread history available")
        
        # Debug information
        if enable_debug:
            st.markdown("## 🔍 Debug Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                with st.expander("Raw Result Data"):
                    st.json(result)
                
                with st.expander("Final State"):
                    st.json(result.get('final_state', {}))
            
            with col2:
                with st.expander("Structured Thread History"):
                    st.json(st.session_state.email_thread_history)
    
    else:
        # Welcome screen
        st.markdown("## 🎯 Welcome to LangGraph Orchestrator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🚀 What is LangGraph Orchestrator?
            
            The LangGraph Orchestrator is a state-driven workflow system that intelligently 
            orchestrates the logistic AI response system using LangGraph's powerful 
            graph-based workflow engine.
            
            **Key Features:**
            - 🧠 LLM-based decision making
            - 📊 Visual workflow representation
            - 🛡️ Robust error handling
            - 📈 Comprehensive monitoring
            - 🔄 Dynamic routing
            """)
        
        with col2:
            st.markdown("""
            ### 🎯 How to Use
            
            1. **Enter Email Content**: Paste the email content in the sidebar
            2. **Configure Metadata**: Set subject, sender, thread ID, and timestamp
            3. **Process**: Click the "Process Email" button
            4. **Monitor**: Watch the workflow execute in real-time
            5. **Review**: Analyze the results and extracted data
            
            ### 📊 Workflow Nodes
            
            - **EMAIL_INPUT**: Initialize workflow state
            - **CONVERSATION_STATE_ANALYSIS**: Analyze conversation context
            - **CLASSIFICATION**: Classify email type and intent
            - **DATA_EXTRACTION**: Extract shipment details
            - **DATA_ENRICHMENT**: Enrich with additional context
            - **VALIDATION**: Validate data quality
            - **DECISION_NODE**: LLM-based routing decision
            - **Response Nodes**: Generate appropriate responses
            """)
        
        # Sample email
        st.markdown("## 📧 Sample Email")
        
        sample_email = """Hi, I need rates for 2x40HC from Shanghai to Los Angeles.
Cargo: Electronics, weight: 25,000 kg, volume: 35 CBM
Ready date: 20th April 2024

Thanks,
Mike Johnson"""
        
        st.markdown("""
        <div class="email-preview">
        {}
        </div>
        """.format(sample_email.replace('\n', '<br>')), unsafe_allow_html=True)
        
        st.markdown("""
        **Try this sample email or enter your own email content in the sidebar to get started!**
        """)

if __name__ == "__main__":
    main() 