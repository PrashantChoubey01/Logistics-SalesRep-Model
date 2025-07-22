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
    /* Theme-aware color variables */
    :root {
        --primary-color: #667eea;
        --secondary-color: #764ba2;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --error-color: #dc3545;
        --info-color: #17a2b8;
        
        /* Light mode colors */
        --bg-primary: #ffffff;
        --bg-secondary: #f8f9fa;
        --bg-tertiary: #e9ecef;
        --text-primary: #212529;
        --text-secondary: #6c757d;
        --text-muted: #adb5bd;
        --border-color: #dee2e6;
        --shadow-color: rgba(0,0,0,0.1);
        --card-bg: #ffffff;
        --email-bg: #f8f9fa;
        --email-border: #dee2e6;
    }
    
    /* Dark mode colors */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #0e1117;
            --bg-secondary: #262730;
            --bg-tertiary: #1e1e1e;
            --text-primary: #fafafa;
            --text-secondary: #b0b0b0;
            --text-muted: #808080;
            --border-color: #404040;
            --shadow-color: rgba(255,255,255,0.1);
            --card-bg: #262730;
            --email-bg: #1e1e1e;
            --email-border: #404040;
        }
    }
    
    /* Streamlit dark mode detection */
    .stApp[data-testid="stAppViewContainer"] {
        background-color: var(--bg-primary) !important;
    }
    
    .main-header {
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px var(--shadow-color);
    }
    
    .workflow-node {
        background: var(--bg-secondary);
        border: 2px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
        color: var(--text-primary);
    }
    
    .workflow-node.completed {
        background: rgba(40, 167, 69, 0.1);
        border-color: var(--success-color);
        color: var(--text-primary);
    }
    
    .workflow-node.error {
        background: rgba(220, 53, 69, 0.1);
        border-color: var(--error-color);
        color: var(--text-primary);
    }
    
    .workflow-node.current {
        background: rgba(255, 193, 7, 0.1);
        border-color: var(--warning-color);
        box-shadow: 0 0 10px rgba(255, 193, 7, 0.3);
        color: var(--text-primary);
    }
    
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 4px var(--shadow-color);
        color: var(--text-primary);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: var(--primary-color);
    }
    
    .metric-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    /* Email display styling */
    .email-display {
        background: var(--email-bg);
        border: 1px solid var(--email-border);
        border-radius: 8px;
        padding: 20px;
        margin: 10px 0;
        color: var(--text-primary);
    }
    
    .email-header {
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 10px;
        margin-bottom: 15px;
        color: var(--text-primary);
    }
    
    .email-body {
        color: var(--text-primary);
        line-height: 1.6;
    }
    
    /* Section headers */
    .section-header {
        color: var(--text-primary);
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Status indicators */
    .status-success {
        color: var(--success-color);
        background: rgba(40, 167, 69, 0.1);
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        border: 1px solid var(--success-color);
    }
    
    .status-warning {
        color: var(--warning-color);
        background: rgba(255, 193, 7, 0.1);
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        border: 1px solid var(--warning-color);
    }
    
    .status-error {
        color: var(--error-color);
        background: rgba(220, 53, 69, 0.1);
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        border: 1px solid var(--error-color);
    }
    
    .status-info {
        color: var(--info-color);
        background: rgba(23, 162, 184, 0.1);
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        border: 1px solid var(--info-color);
    }
    
    /* Card styling */
    .info-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px var(--shadow-color);
        color: var(--text-primary);
    }
    
    /* Text colors */
    .text-primary {
        color: var(--text-primary) !important;
    }
    
    .text-secondary {
        color: var(--text-secondary) !important;
    }
    
    .text-muted {
        color: var(--text-muted) !important;
    }
    
    /* Background colors */
    .bg-primary {
        background-color: var(--bg-primary) !important;
    }
    
    .bg-secondary {
        background-color: var(--bg-secondary) !important;
    }
    
    .bg-tertiary {
        background-color: var(--bg-tertiary) !important;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
            font-size: 0.9rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
        
        .email-display {
            padding: 15px;
        }
    }
    
    /* Hover effects */
    .workflow-node:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px var(--shadow-color);
    }
    
    .metric-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 8px var(--shadow-color);
    }
    
    /* Animation for status changes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
        .fade-in {
        animation: fadeIn 0.3s ease-in-out;
    }
    
    /* Additional utility classes for dark/light mode compatibility */
    .workflow-graph {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: var(--text-primary);
    }
    
    .email-preview {
        background: var(--email-bg);
        border: 1px solid var(--email-border);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: var(--text-primary);
    }
    
    .sidebar-section {
        background: var(--bg-secondary);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: var(--text-primary);
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
        
        # =====================================================
        #                 🚨 ESCALATION SECTION
        # =====================================================
        
        # Check if workflow was escalated
        final_state = result.get('final_state', {})
        next_action = final_state.get('next_action', '')
        current_node = final_state.get('current_node', '')
        
        if current_node == 'ESCALATION' or 'escalate' in next_action.lower():
            st.markdown("## 🚨 Escalation to Human")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.error("⚠️ **Email Escalated to Human**")
                st.markdown("""
                **Reason for Escalation:**
                - Low confidence in processing
                - Complex or unclear request
                - System error or timeout
                - Manual intervention required
                """)
                
                # Escalation details
                escalation_data = {
                    "Escalation Reason": final_state.get('escalation_reason', 'Low confidence or system error'),
                    "Confidence Score": f"{final_state.get('confidence_score', 0):.1%}",
                    "Escalation Time": bot_timestamp,
                    "Assigned To": "Sales Team",
                    "Priority": "High" if final_state.get('confidence_score', 0) < 0.5 else "Medium"
                }
                
                for key, value in escalation_data.items():
                    st.markdown(f"**{key}:** {value}")
            
            with col2:
                st.markdown("### 📧 Escalation Email Template")
                
                escalation_email = f"""Subject: URGENT - Manual Review Required - {subject}

Dear Sales Team,

An email has been escalated for manual review:

**Customer Details:**
- From: {sender}
- Subject: {subject}
- Thread ID: {thread_id}
- Escalation Time: {bot_timestamp}

**Escalation Reason:**
{escalation_data['Escalation Reason']}

**Original Email Content:**
{email_text[:500]}{'...' if len(email_text) > 500 else ''}

**Required Action:**
Please review this email and respond appropriately to the customer.

Best regards,
AI Logistics System
"""
                
                st.text_area("Escalation Email", value=escalation_email, height=300, disabled=True)
        
        # =====================================================
        #                 🔧 FORWARDER ENGAGEMENT SECTION
        # =====================================================
        
        # Check if forwarders were assigned
        forwarder_assignment = result.get('final_state', {}).get('forwarder_assignment', {})
        
        if forwarder_assignment and forwarder_assignment.get('assigned_forwarders'):
            st.markdown("## 🔧 Forwarder Email Engagement")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 📧 Rate Requests Sent to Forwarders")
                
                # Display forwarder assignment summary
                assignment_summary = {
                    "Total Forwarders": forwarder_assignment.get('total_forwarders', 0),
                    "Origin Country": forwarder_assignment.get('origin_country', 'N/A'),
                    "Destination Country": forwarder_assignment.get('destination_country', 'N/A'),
                    "Assignment Method": forwarder_assignment.get('assignment_method', 'N/A'),
                    "Rate Requests Generated": len(forwarder_assignment.get('rate_requests', []))
                }
                
                for key, value in assignment_summary.items():
                    st.markdown(f"**{key}:** {value}")
                
                # Show forwarder details
                st.markdown("### 🔧 Assigned Forwarders")
                forwarders = forwarder_assignment.get('assigned_forwarders', [])
                
                for i, forwarder in enumerate(forwarders, 1):
                    with st.expander(f"{i}. {forwarder['name']}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"**Email:** {forwarder['email']}")
                            st.markdown(f"**Phone:** {forwarder['phone']}")
                            st.markdown(f"**Operator:** {forwarder.get('operator', 'N/A')}")
                        
                        with col2:
                            st.markdown(f"**Specialties:** {', '.join(forwarder.get('specialties', []))}")
                            st.markdown(f"**Rating:** {forwarder.get('rating', 'N/A')}")
                            st.markdown(f"**Country:** {forwarder.get('country', 'N/A')}")
            
            with col2:
                st.markdown("### 📊 Forwarder Engagement Stats")
                
                # Engagement metrics
                engagement_metrics = {
                    "Rate Requests Sent": len(forwarder_assignment.get('rate_requests', [])),
                    "Response Expected": "24 hours",
                    "Follow-up Required": "Yes",
                    "Status": "Pending Responses"
                }
                
                for key, value in engagement_metrics.items():
                    st.metric(key, value)
                
                # Show rate request preview
                if forwarder_assignment.get('rate_requests'):
                    st.markdown("### 📝 Rate Request Preview")
                    
                    # Show first rate request as example
                    first_request = forwarder_assignment['rate_requests'][0]
                    
                    with st.expander("📧 Sample Rate Request Email", expanded=False):
                        st.markdown(f"**To:** {first_request['forwarder_name']}")
                        st.markdown(f"**Subject:** {first_request['subject']}")
                        st.markdown("**Body:**")
                        st.text_area("Email Content", value=first_request['body'], height=200, disabled=True)
        
        # =====================================================
        #                 📧 FORWARDER RATE REQUEST EMAILS
        # =====================================================
        
        # Display all forwarder rate request emails
        if forwarder_assignment and forwarder_assignment.get('rate_requests'):
            st.markdown("## 📧 Forwarder Rate Request Emails")
            st.markdown("### 📤 Emails to be sent to forwarders for rate procurement")
            
            # Show summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Emails", len(forwarder_assignment['rate_requests']))
            
            with col2:
                st.metric("Origin Country", forwarder_assignment.get('origin_country', 'N/A'))
            
            with col3:
                st.metric("Destination Country", forwarder_assignment.get('destination_country', 'N/A'))
            
            with col4:
                st.metric("Shipment Type", "FCL" if forwarder_assignment.get('rate_requests') else 'N/A')
            
            # Display rate request emails in dropdown format
            st.markdown("### 📧 Rate Request Emails")
            
            # Create a summary table first
            email_summary_data = []
            for i, rate_request in enumerate(forwarder_assignment['rate_requests'], 1):
                shipment_details = rate_request['shipment_details']
                email_summary_data.append({
                    "Email #": i,
                    "Forwarder": rate_request['forwarder_name'],
                    "Email": rate_request['forwarder_email'],
                    "Operator": shipment_details.get('operator', 'N/A'),
                    "Route": f"{shipment_details.get('origin', 'N/A')} → {shipment_details.get('destination', 'N/A')}",
                    "Container": shipment_details.get('container_type', 'N/A'),
                    "Status": "Ready to Send"
                })
            
            # Display summary table
            if email_summary_data:
                summary_df = pd.DataFrame(email_summary_data)
                st.dataframe(summary_df, use_container_width=True)
            
            # Display each email in expandable sections
            for i, rate_request in enumerate(forwarder_assignment['rate_requests'], 1):
                shipment_details = rate_request['shipment_details']
                
                # Create expander title with key information
                expander_title = f"📧 Email #{i}: {rate_request['forwarder_name']} ({shipment_details.get('operator', 'N/A')}) - {shipment_details.get('origin', 'N/A')} → {shipment_details.get('destination', 'N/A')}"
                
                with st.expander(expander_title, expanded=False):
                    # Email header information
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("**📋 Email Details:**")
                        st.markdown(f"**To:** {rate_request['forwarder_name']}")
                        st.markdown(f"**Email:** {rate_request['forwarder_email']}")
                        st.markdown(f"**Subject:** {rate_request['subject']}")
                        st.markdown(f"**Operator:** {shipment_details.get('operator', 'N/A')}")
                        
                        # Shipment details summary
                        st.markdown("**📦 Shipment Details:**")
                        st.markdown(f"- **Route:** {shipment_details.get('origin', 'N/A')} → {shipment_details.get('destination', 'N/A')}")
                        st.markdown(f"- **Container:** {shipment_details.get('container_type', 'N/A')}")
                        st.markdown(f"- **Weight:** {shipment_details.get('weight', 'N/A')}")
                        st.markdown(f"- **Commodity:** {shipment_details.get('commodity', 'N/A')}")
                        st.markdown(f"- **Shipment Date:** {shipment_details.get('shipment_date', 'N/A')}")
                    
                    with col2:
                        # Email status and actions
                        st.markdown("**📊 Status:**")
                        st.success("✅ Ready to Send")
                        
                        st.markdown("**⚡ Quick Actions:**")
                        if st.button(f"📤 Send", key=f"send_email_{i}", use_container_width=True):
                            st.success(f"✅ Email sent to {rate_request['forwarder_name']}!")
                            st.info("Note: This is a demo - emails are not actually sent")
                        
                        if st.button(f"📝 Edit", key=f"edit_email_{i}", use_container_width=True):
                            st.info("Edit functionality would open email editor")
                        
                        if st.button(f"📋 Copy", key=f"copy_email_{i}", use_container_width=True):
                            st.info("Email content copied to clipboard")
                    
                    # Email body in styled format
                    st.markdown("**📝 Email Content:**")
                    
                    # Create a styled email display
                    email_display = f"""
<div class="email-display">
<div class="email-header">
<strong>📧 Rate Request Email</strong><br>
<small>From: DP World Logistics Team &lt;rates@dpworld.com&gt;</small><br>
<small>To: {rate_request['forwarder_name']} &lt;{rate_request['forwarder_email']}&gt;</small><br>
<small>Subject: {rate_request['subject']}</small>
</div>

<div class="email-body">
{rate_request['body'].replace('**', '<strong>').replace('*', '•')}
</div>
</div>
"""
                    
                    st.markdown(email_display, unsafe_allow_html=True)
                    
                    # Forwarder details in a sub-expander
                    with st.expander("🔧 Forwarder Details", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**👤 Forwarder Information:**")
                            st.markdown(f"- **Name:** {rate_request['forwarder_name']}")
                            st.markdown(f"- **Email:** {rate_request['forwarder_email']}")
                            st.markdown(f"- **Phone:** {rate_request['forwarder_phone']}")
                            
                            # Find forwarder details for additional info
                            forwarder_details = next((f for f in forwarder_assignment['assigned_forwarders'] 
                                                    if f['name'] == rate_request['forwarder_name']), None)
                            if forwarder_details:
                                st.markdown(f"- **Operator:** {forwarder_details.get('operator', 'N/A')}")
                                st.markdown(f"- **Specialties:** {', '.join(forwarder_details.get('specialties', []))}")
                        
                        with col2:
                            st.markdown("**📦 Complete Shipment Info:**")
                            for key, value in shipment_details.items():
                                if key != 'operator':  # Already shown above
                                    st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
            
            # Bulk actions with enhanced functionality
            st.markdown("### 🚀 Bulk Actions")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📤 Send All Emails", type="primary", use_container_width=True):
                    st.success("✅ All rate request emails sent!")
                    st.info("Note: This is a demo - emails are not actually sent")
            
            with col2:
                if st.button("📊 Track Responses", use_container_width=True):
                    st.info("📊 Response tracking dashboard would open")
                    st.markdown("**Expected Responses:** 24 hours")
                    st.markdown("**Follow-up Required:** Yes")
            
            with col3:
                if st.button("📋 Export Email List", use_container_width=True):
                    st.info("📋 Email list exported to CSV")
                    st.markdown("**Format:** Forwarder, Email, Subject, Status")
            
            with col4:
                if st.button("🔍 Preview All", use_container_width=True):
                    st.info("🔍 All emails expanded for preview")
                    st.markdown("**Tip:** Use individual expanders for detailed view")
        
        # =====================================================
        #                 📊 FORWARDER RESPONSE TRACKING
        # =====================================================
        
        # Add forwarder response tracking section
        if forwarder_assignment and forwarder_assignment.get('rate_requests'):
            st.markdown("## 📊 Forwarder Response Tracking")
            
            # Create a mock response tracking table
            response_data = []
            for rate_request in forwarder_assignment['rate_requests']:
                response_data.append({
                    "Forwarder": rate_request['forwarder_name'],
                    "Email": rate_request['forwarder_email'],
                    "Subject": rate_request['subject'],
                    "Sent Date": datetime.now().strftime("%Y-%m-%d"),
                    "Status": "Pending",
                    "Expected Response": "24 hours",
                    "Follow-up": "Required",
                    "Operator": rate_request['shipment_details'].get('operator', 'N/A')
                })
            
            # Display as a table
            if response_data:
                df = pd.DataFrame(response_data)
                st.dataframe(df, use_container_width=True)
                
                # Response statistics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Sent", len(response_data))
                
                with col2:
                    st.metric("Pending", len(response_data))
                
                with col3:
                    st.metric("Responses", 0)
                
                with col4:
                    st.metric("Response Rate", "0%")
        
        # =====================================================
        #                 📧 EMAIL RECIPIENT SELECTION
        # =====================================================
        
        # Add email recipient selection interface
        st.markdown("## 📧 Email Recipient Selection")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👤 Send Email To")
            
            # Email recipient options
            recipient_options = ["Customer", "Forwarder", "Sales Team", "Custom"]
            selected_recipient = st.selectbox("Choose Recipient", recipient_options, index=0)
            
            if selected_recipient == "Customer":
                st.info("📧 **Customer Email** - Standard response to customer")
                st.markdown(f"**Recipient:** {sender}")
                st.markdown(f"**Subject:** Re: {subject}")
                
            elif selected_recipient == "Forwarder":
                st.info("🔧 **Forwarder Email** - Rate request or follow-up")
                
                # Show available forwarders
                if forwarder_assignment and forwarder_assignment.get('assigned_forwarders'):
                    forwarder_names = [f['name'] for f in forwarder_assignment['assigned_forwarders']]
                    selected_forwarder = st.selectbox("Select Forwarder", forwarder_names, index=0)
                    
                    # Find selected forwarder details
                    selected_fwd = next((f for f in forwarder_assignment['assigned_forwarders'] if f['name'] == selected_forwarder), None)
                    
                    if selected_fwd:
                        st.markdown(f"**Recipient:** {selected_fwd['email']}")
                        st.markdown(f"**Forwarder:** {selected_fwd['name']}")
                        st.markdown(f"**Operator:** {selected_fwd.get('operator', 'N/A')}")
                else:
                    st.warning("No forwarders assigned yet")
                    
            elif selected_recipient == "Sales Team":
                st.info("🚨 **Sales Team Email** - Escalation or notification")
                st.markdown("**Recipient:** sales@company.com")
                st.markdown("**Subject:** Manual Review Required")
                
            elif selected_recipient == "Custom":
                custom_email = st.text_input("Custom Email Address", placeholder="Enter email address")
                custom_subject = st.text_input("Custom Subject", placeholder="Enter subject")
                if custom_email:
                    st.markdown(f"**Recipient:** {custom_email}")
                    st.markdown(f"**Subject:** {custom_subject}")
        
        with col2:
            st.markdown("### 📝 Email Content")
            
            # Email content options based on recipient
            if selected_recipient == "Customer":
                content_options = ["Confirmation", "Clarification Request", "Rate Quote", "Status Update", "Custom"]
                selected_content = st.selectbox("Email Type", content_options, index=0)
                
                if selected_content == "Confirmation":
                    st.success("✅ Confirmation email template")
                elif selected_content == "Clarification Request":
                    st.warning("❓ Clarification request template")
                elif selected_content == "Rate Quote":
                    st.info("💰 Rate quote template")
                elif selected_content == "Status Update":
                    st.info("📊 Status update template")
                elif selected_content == "Custom":
                    custom_content = st.text_area("Custom Email Content", height=150)
                    
            elif selected_recipient == "Forwarder":
                content_options = ["Rate Request", "Follow-up", "Rate Negotiation", "Custom"]
                selected_content = st.selectbox("Email Type", content_options, index=0)
                
                if selected_content == "Rate Request":
                    st.info("💰 Rate request template")
                elif selected_content == "Follow-up":
                    st.warning("⏰ Follow-up template")
                elif selected_content == "Rate Negotiation":
                    st.info("🤝 Rate negotiation template")
                elif selected_content == "Custom":
                    custom_content = st.text_area("Custom Email Content", height=150)
                    
            elif selected_recipient == "Sales Team":
                content_options = ["Escalation", "Notification", "Custom"]
                selected_content = st.selectbox("Email Type", content_options, index=0)
                
                if selected_content == "Escalation":
                    st.error("🚨 Escalation template")
                elif selected_content == "Notification":
                    st.info("📢 Notification template")
                elif selected_content == "Custom":
                    custom_content = st.text_area("Custom Email Content", height=150)
            
            # Send button
            if st.button("📧 Send Email", type="primary"):
                st.success(f"✅ Email sent to {selected_recipient}!")
                st.info("Note: This is a demo - emails are not actually sent")
        
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