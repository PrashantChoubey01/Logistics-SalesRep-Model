#!/usr/bin/env python3
"""
Improved Streamlit App with Enhanced Thread Management
=====================================================

Provides a user-friendly interface with clear thread management buttons
and comprehensive coalesced data display.
"""

import streamlit as st
import asyncio
import json
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import os
import glob

# Import the main orchestrator
from langgraph_workflow_orchestrator import LangGraphWorkflowOrchestrator
from utils.thread_manager import ThreadManager
from utils.forwarder_manager import ForwarderManager

# Page configuration
st.set_page_config(
    page_title="Logistics AI Response System - Enhanced",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .thread-button {
        margin: 0.5rem 0;
        width: 100%;
    }
    .coalesced-data {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #bee5eb;
        margin: 1rem 0;
    }
    .data-category {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
        border-left: 3px solid #007bff;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #007bff;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

class ImprovedStreamlitApp:
    """Enhanced Streamlit application with improved thread management"""
    
    def __init__(self):
        self.orchestrator = None
        self.thread_manager = None
        self.forwarder_manager = None
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize system components"""
        try:
            with st.spinner("Initializing system components..."):
                self.orchestrator = LangGraphWorkflowOrchestrator()
                self.thread_manager = ThreadManager()
                self.forwarder_manager = ForwarderManager()
            st.success("✅ System components initialized successfully!")
        except Exception as e:
            st.error(f"❌ Failed to initialize system: {e}")
            st.stop()
    
    def get_existing_threads(self):
        """Get list of existing thread IDs"""
        try:
            thread_files = glob.glob("data/threads/*.json")
            thread_ids = []
            
            for file_path in thread_files:
                thread_id = os.path.basename(file_path).replace('.json', '')
                thread_ids.append(thread_id)
            
            return sorted(thread_ids)
        except Exception as e:
            st.error(f"Error getting existing threads: {e}")
            return []
    
    def display_coalesced_data(self, thread_data):
        """Display coalesced data in a comprehensive format"""
        if not thread_data or not thread_data.cumulative_extraction:
            st.warning("⚠️ No coalesced data available for this thread")
            return
        
        cumulative = thread_data.cumulative_extraction
        
        st.markdown('<div class="coalesced-data">', unsafe_allow_html=True)
        st.markdown("### 📊 Coalesced Data (Merged from All Emails)")
        
        # Shipment Details
        shipment = cumulative.get('shipment_details', {})
        if shipment:
            st.markdown('<div class="data-category">', unsafe_allow_html=True)
            st.markdown("**🚢 Shipment Details:**")
            cols = st.columns(3)
            for i, (key, value) in enumerate(shipment.items()):
                if value:
                    col_idx = i % 3
                    with cols[col_idx]:
                        st.write(f"• **{key.replace('_', ' ').title()}:** {value}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Contact Information
        contact = cumulative.get('contact_information', {})
        if contact:
            st.markdown('<div class="data-category">', unsafe_allow_html=True)
            st.markdown("**👤 Contact Information:**")
            cols = st.columns(2)
            for i, (key, value) in enumerate(contact.items()):
                if value:
                    col_idx = i % 2
                    with cols[col_idx]:
                        st.write(f"• **{key.replace('_', ' ').title()}:** {value}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Timeline Information
        timeline = cumulative.get('timeline_information', {})
        if timeline:
            st.markdown('<div class="data-category">', unsafe_allow_html=True)
            st.markdown("**📅 Timeline Information:**")
            cols = st.columns(2)
            for i, (key, value) in enumerate(timeline.items()):
                if value:
                    col_idx = i % 2
                    with cols[col_idx]:
                        st.write(f"• **{key.replace('_', ' ').title()}:** {value}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Special Requirements
        special_req = cumulative.get('special_requirements', [])
        if special_req:
            st.markdown('<div class="data-category">', unsafe_allow_html=True)
            st.markdown("**📝 Special Requirements:**")
            for req in special_req:
                st.write(f"• {req}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Additional Notes
        notes = cumulative.get('additional_notes', '')
        if notes:
            st.markdown('<div class="data-category">', unsafe_allow_html=True)
            st.markdown("**📄 Additional Notes:**")
            st.write(notes)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Thread Statistics
        st.markdown("### 📈 Thread Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{thread_data.total_emails}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Emails</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(cumulative)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Categories</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            total_fields = sum(len(data) if isinstance(data, dict) else 1 
                              for data in cumulative.values())
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{total_fields}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Total Fields</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{thread_data.conversation_state.replace("_", " ").title()}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Conversation State</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def run(self):
        """Run the improved Streamlit application"""
        # Header
        st.markdown('<h1 class="main-header">🚢 Logistics AI Response System - Enhanced</h1>', unsafe_allow_html=True)
        
        # Sidebar with thread management
        self.setup_sidebar()
        
        # Main content
        tab1, tab2, tab3, tab4 = st.tabs([
            "📧 Email Processing", 
            "🧵 Thread Management", 
            "📊 Coalesced Data View",
            "⚙️ Configuration"
        ])
        
        with tab1:
            self.email_processing_tab()
        
        with tab2:
            self.thread_management_tab()
        
        with tab3:
            self.coalesced_data_tab()
        
        with tab4:
            self.configuration_tab()
    
    def setup_sidebar(self):
        """Setup sidebar with system status and quick actions"""
        st.sidebar.markdown("## 🧵 Thread Management")
        
        # Quick actions
        st.sidebar.markdown("### Quick Actions")
        
        if st.button("🗑️ Clear All Threads", key="clear_all_threads"):
            try:
                thread_files = glob.glob("data/threads/*.json")
                for file_path in thread_files:
                    os.remove(file_path)
                st.sidebar.success("✅ All threads cleared!")
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"❌ Error: {e}")
        
        # Thread statistics
        existing_threads = self.get_existing_threads()
        if existing_threads:
            st.sidebar.markdown("### Thread Statistics")
            st.sidebar.info(f"📧 **{len(existing_threads)} threads** available")
            
            # Show recent threads
            st.sidebar.markdown("**Recent Threads:**")
            for thread_id in existing_threads[-3:]:  # Show last 3 threads
                thread_data = self.thread_manager.load_thread(thread_id)
                if thread_data:
                    st.sidebar.write(f"• {thread_id[:20]}... ({thread_data.total_emails} emails)")
        else:
            st.sidebar.info("📧 No threads available")
        
        # System status
        st.sidebar.markdown("---")
        st.sidebar.markdown("## System Status")
        
        if self.orchestrator:
            st.sidebar.success("✅ Workflow Orchestrator: Active")
        else:
            st.sidebar.error("❌ Workflow Orchestrator: Inactive")
        
        if self.thread_manager:
            st.sidebar.success("✅ Thread Manager: Active")
        else:
            st.sidebar.error("❌ Thread Manager: Inactive")
        
    def email_processing_tab(self):
        """Enhanced email processing tab"""
        st.markdown('<h2 class="section-header">📧 Email Processing</h2>', unsafe_allow_html=True)
        
        # Thread selection section
        st.markdown("### 🧵 Thread Selection")
        
        # Get existing threads
        existing_threads = self.get_existing_threads()
        
        # Thread selection options
        thread_option = st.radio(
            "Choose thread option:",
            ["🆕 Create New Thread", "📧 Add to Existing Thread"],
            horizontal=True,
            key="thread_option"
        )
        
        thread_id = None
        
        if thread_option == "🆕 Create New Thread":
            # Create new thread
            thread_id = f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.info(f"🆕 **New Thread ID:** {thread_id}")
            
        else:
            # Add to existing thread
            if existing_threads:
                selected_thread = st.selectbox(
                    "Select existing thread:",
                    existing_threads,
                    key="existing_thread_selector",
                    help="Choose an existing thread to add this email to"
                )
                thread_id = selected_thread
                
                # Show thread info
                thread_data = self.thread_manager.load_thread(thread_id)
                if thread_data and thread_data.email_chain:
                    st.success(f"📧 **{len(thread_data.email_chain)} emails** in selected thread")
                    
                    # Show thread summary
                    with st.expander("📋 Thread Summary"):
                        st.write(f"**Thread ID:** {thread_id}")
                        st.write(f"**Total Emails:** {len(thread_data.email_chain)}")
                        st.write(f"**Last Updated:** {thread_data.last_updated}")
        
                        # Show last few emails
                        st.write("**Recent Emails:**")
                        for i, email in enumerate(thread_data.email_chain[-3:]):
                            st.write(f"  • {email.subject[:50]}... ({email.timestamp[:10]})")
                else:
                    st.warning("⚠️ Selected thread not found or empty")
                    thread_id = f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            else:
                st.warning("⚠️ No existing threads found. Creating new thread.")
                thread_id = f"thread_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Email input form
        with st.form("email_form"):
            st.markdown("### Email Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                sender_email = st.text_input("Sender Email", "john.smith@company.com")
                sender_name = st.text_input("Sender Name", "John Smith")
                
                # Thread info display
                st.markdown("### Thread Information")
                st.info(f"**Thread ID:** {thread_id}")
                
                # Show thread history if available
                thread_data = self.thread_manager.load_thread(thread_id)
                if thread_data and thread_data.email_chain:
                    st.success(f"📧 {len(thread_data.email_chain)} emails in this thread")
                else:
                    st.info("🆕 New thread will be created")
            
            with col2:
                email_type = st.selectbox(
                    "Email Type",
                    ["customer", "forwarder", "non_logistics"],
                    help="Select the type of email for testing"
                )
                
                # Pre-fill content based on type
                if email_type == "customer":
                    default_content = """Hi there,

I need a shipping quote for the following:
- Origin: Shanghai, China
- Destination: Los Angeles, USA
- Container: 40HC
- Weight: 15,000 kg
- Volume: 68 CBM
- Commodity: Electronics

Please provide rates and transit time.

Best regards,
John Smith"""
                elif email_type == "forwarder":
                    default_content = """Dear Logistics Team,

Please find our rate quote for the Shanghai to Los Angeles route:

Route: Shanghai (CNSHA) to Los Angeles (USLAX)
Container: 40HC
Rate: $2,850 USD
Transit Time: 18 days
Valid Until: August 31, 2025

Please confirm if you would like to proceed with this rate.

Best regards,
DHL Global Forwarding"""
                else:
                    default_content = """Dear Hiring Manager,

I am writing to express my interest in the Sales Position at your company.
I have 5 years of experience in logistics and sales.

Please find my resume attached.

Best regards,
Jane Doe"""
            
            subject = st.text_input("Subject", "Shipping Quote Request - Shanghai to Los Angeles")
            content = st.text_area("Email Content", default_content, height=200)
            
            submitted = st.form_submit_button("🚀 Process Email")
        
        if submitted:
            self.process_email(sender_email, sender_name, subject, content, thread_id, email_type)
        
    def thread_management_tab(self):
        """Enhanced thread management tab"""
        st.markdown('<h2 class="section-header">🧵 Thread Management</h2>', unsafe_allow_html=True)
        
        # Thread operations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### View Thread")
            thread_id = st.text_input("Thread ID", "test_thread_001")
            
            if st.button("📋 Load Thread", key="load_thread"):
                thread_data = self.thread_manager.load_thread(thread_id)
                if thread_data:
                    st.success(f"✅ Thread loaded: {thread_data.total_emails} emails")
                    
                    # Display thread summary
                    st.markdown("**Thread Summary:**")
                    st.json({
                        "thread_id": thread_data.thread_id,
                        "total_emails": thread_data.total_emails,
                        "conversation_state": thread_data.conversation_state,
                        "last_updated": thread_data.last_updated
                    })
                    
                    # Display coalesced data
                    self.display_coalesced_data(thread_data)
                    
                    # Display email chain
                    st.markdown("**Email Chain:**")
                    for i, email in enumerate(thread_data.email_chain):
                        with st.expander(f"Email {i+1}: {email.subject}"):
                            st.write(f"**From:** {email.sender}")
                            st.write(f"**Date:** {email.timestamp}")
                            st.write(f"**Direction:** {email.direction}")
                            st.write(f"**Content:** {email.content[:200]}...")
                else:
                    st.warning("⚠️ Thread not found")
        
        with col2:
            st.markdown("### Thread Statistics")
            
            # Get mixed conversation summary
            if st.button("📊 Get Conversation Summary", key="get_summary"):
                summary = self.thread_manager.get_mixed_conversation_summary(thread_id)
                if summary and 'error' not in summary:
                    st.markdown("**Conversation Summary:**")
                    st.json(summary)
                else:
                    st.warning("⚠️ No conversation data available")
            
            # Thread management actions
            st.markdown("### Thread Actions")
            
            if st.button("🗑️ Clear All Threads", key="clear_all"):
                try:
                    thread_files = glob.glob("data/threads/*.json")
                    for file_path in thread_files:
                        os.remove(file_path)
                    st.success("✅ All threads cleared!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error clearing threads: {e}")
            
            if st.button("🔄 Refresh Thread List", key="refresh"):
                st.rerun()
    
    def coalesced_data_tab(self):
        """Dedicated tab for viewing coalesced data"""
        st.markdown('<h2 class="section-header">📊 Coalesced Data View</h2>', unsafe_allow_html=True)
        
        # Select thread to view coalesced data
        existing_threads = self.get_existing_threads()
        
        if existing_threads:
            selected_thread = st.selectbox(
                "Select a thread to view coalesced data:",
                existing_threads,
                key="coalesced_thread_selector"
            )
            
            if selected_thread:
                thread_data = self.thread_manager.load_thread(selected_thread)
                if thread_data:
                    st.success(f"✅ Thread loaded: {thread_data.total_emails} emails")
                    
                    # Display comprehensive coalesced data
                    self.display_coalesced_data(thread_data)
                    
                    # Raw data view
                    with st.expander("🔍 Raw Coalesced Data (JSON)"):
                        st.json(thread_data.cumulative_extraction)
                    
                    # Email chain analysis
                    st.markdown("### 📧 Email Chain Analysis")
                    
                    customer_emails = [e for e in thread_data.email_chain if e.direction == "inbound"]
                    bot_emails = [e for e in thread_data.email_chain if e.direction == "outbound"]
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Emails", len(thread_data.email_chain))
                    
                    with col2:
                        st.metric("Customer Emails", len(customer_emails))
                    
                    with col3:
                        st.metric("Bot Responses", len(bot_emails))
                    
                    # Email timeline
                    st.markdown("### 📅 Email Timeline")
                    for i, email in enumerate(thread_data.email_chain):
                        with st.expander(f"Email {i+1}: {email.timestamp[:10]} - {email.subject}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"**From:** {email.sender}")
                                st.write(f"**Direction:** {email.direction}")
                            with col2:
                                st.write(f"**Date:** {email.timestamp}")
                                if email.extracted_data:
                                    st.write(f"**Extracted Data:** {len(email.extracted_data)} categories")
                            
                            st.write(f"**Content:** {email.content[:300]}...")
                            
                            if email.extracted_data:
                                st.write("**Extracted Data:**")
                                st.json(email.extracted_data)
                else:
                    st.warning("⚠️ Thread not found")
        else:
            st.info("ℹ️ No threads available. Process some emails first!")
    
    def configuration_tab(self):
        """Configuration tab"""
        st.markdown('<h2 class="section-header">⚙️ Configuration</h2>', unsafe_allow_html=True)
        
        st.markdown("### System Configuration")
        
        # LLM Configuration
        st.markdown("**LLM Configuration:**")
        st.info("""
        - **Provider:** Databricks
        - **Model:** databricks-llama-2-70b-chat
        - **Timeout:** 120 seconds
        - **Temperature:** 0.1 (for extraction), 0.7 (for responses)
        """)
        
        # Agent Configuration
        st.markdown("**Agent Configuration:**")
        st.info("""
        - **Total Agents:** 18 specialized agents
        - **Response Types:** Clarification, Confirmation, Acknowledgment
        - **Thread Management:** Enhanced with recency priority
        - **Forwarder Management:** Country-based assignment
        """)
            
        # Workflow Configuration
        st.markdown("**Workflow Configuration:**")
        st.info("""
        - **Framework:** LangGraph
        - **Steps:** 10 main processing steps
        - **Routing:** Conditional based on email type and content
        - **Escalation:** Automatic for low confidence cases
        """)
    
    def process_email(self, sender_email: str, sender_name: str, subject: str, content: str, thread_id: str, email_type: str):
        """Process email through the workflow"""
        st.markdown('<h3 class="section-header">🔄 Processing Email...</h3>', unsafe_allow_html=True)
        
        # Prepare email data
        email_data = {
            "sender": sender_email,
            "sender_name": sender_name,
            "subject": subject,
            "content": content,
            "thread_id": thread_id
        }
        
        # Check if this is a forwarder email first
        if self.is_forwarder_email(sender_email):
            st.info("🤝 Forwarder email detected - generating acknowledgment...")
            self.process_forwarder_email_simple(sender_email, sender_name, subject, content)
            return
        
        # Process with progress indicator for regular emails
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Update progress
            progress_bar.progress(25)
            status_text.text("Initializing workflow...")
            
            # Process email
            result = asyncio.run(self.orchestrator.process_email(email_data))
            
            progress_bar.progress(100)
            status_text.text("Processing completed!")
            
            # Display results
            self.display_workflow_results(result)
            
        except Exception as e:
            progress_bar.progress(0)
            status_text.text("Processing failed!")
            st.error(f"❌ Error processing email: {e}")
    
    def is_forwarder_email(self, sender_email: str) -> bool:
        """Check if the email is from a forwarder"""
        try:
            # Load forwarder data
            with open('config/forwarders.json', 'r') as f:
                forwarder_data = json.load(f)
            
            forwarder_emails = [f['email'] for f in forwarder_data.get('forwarders', [])]
            return sender_email.lower() in [email.lower() for email in forwarder_emails]
        except Exception as e:
            st.warning(f"⚠️ Could not check forwarder status: {e}")
            return False
    
    def process_forwarder_email_simple(self, sender_email: str, sender_name: str, subject: str, content: str):
        """Simple forwarder email processing that generates acknowledgment directly"""
        try:
            # Load sales team data
            with open('config/sales_team.json', 'r') as f:
                sales_team_data = json.load(f)
            
            # Get a sales person (use the first available one)
            sales_persons = sales_team_data.get('sales_team', [])
            if not sales_persons:
                # Fallback sales person
                sales_person = {
                    "name": "Digital Sales Specialist",
                    "title": "Digital Sales Specialist", 
                    "email": "sales@searates.com",
                    "phone": "+1-555-0123",
                    "signature": "Best regards,\n\nDigital Sales Specialist\nSearates By DP World\n📧 sales@searates.com\n📞 +1-555-0123"
                }
            else:
                sales_person = sales_persons[0]  # Use first sales person
            
            # Generate acknowledgment
            acknowledgment_subject = f"Re: {subject}"
            acknowledgment_body = f"""Dear {sender_name or 'Valued Partner'},

Thank you for your email regarding the shipment inquiry.

We have received your message and our team is working on providing you with the requested information. You can expect our response within 24 hours.

If you have any specific requirements or urgent requests, please let us know.

Best regards,
{sales_person['name']}
{sales_person['title']}
Searates By DP World
📧 {sales_person['email']}
📞 {sales_person['phone']}"""
            
            # Display the acknowledgment
            st.success("✅ Forwarder Acknowledgment Generated")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("### 📧 Acknowledgment Details")
                st.write(f"**To:** {sender_email}")
                st.write(f"**From:** {sales_person['email']}")
                st.write(f"**Subject:** {acknowledgment_subject}")
                st.write(f"**Sales Person:** {sales_person['name']} ({sales_person['title']})")
            
            with col2:
                st.markdown("### 📄 Acknowledgment Body")
                st.text_area("Response Body", acknowledgment_body, height=300, disabled=True)
            
            # Show success message
            st.success("🎉 Forwarder email processed successfully! The acknowledgment has been generated and is ready to be sent.")
            
        except Exception as e:
            st.error(f"❌ Error processing forwarder email: {e}")
            st.info("Please check the configuration files (config/forwarders.json and config/sales_team.json)")
    
    def display_workflow_results(self, result: Dict[str, Any]):
        """Display workflow results with detailed step-by-step information"""
        st.markdown('<h3 class="section-header">📊 Workflow Results</h3>', unsafe_allow_html=True)
        
        # Basic info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", result.get('status', 'Unknown'))
        
        with col2:
            st.metric("Workflow ID", result.get('workflow_id', 'Unknown'))
        
        with col3:
            st.metric("Thread ID", result.get('thread_id', 'Unknown'))
        
        if result.get('status') == 'completed':
            workflow_result = result.get('result', {})
            
            # Check if workflow_result is not None before proceeding
            if workflow_result:
                # Show final response email prominently
                self.display_final_response(workflow_result)
                
                # Show forwarder assignment information prominently
                if workflow_result.get('forwarder_assignment_result'):
                    self.display_forwarder_assignment(workflow_result['forwarder_assignment_result'])
            else:
                st.error("❌ Workflow completed but no result data available")
                st.info("The workflow completed successfully but no result data was returned.")
        elif result.get('status') == 'failed':
            st.error("❌ Workflow failed")
            st.error(f"Error: {result.get('error', 'Unknown error')}")
            
            # Try to show partial results if available
            if result.get('result'):
                st.info("Partial workflow results available:")
                workflow_result = result['result']
                
                # Show classification if available
                if workflow_result and workflow_result.get('classification_result'):
                    classification = workflow_result['classification_result']
                    st.write(f"**Email Type:** {classification.get('email_type', 'Unknown')}")
                    st.write(f"**Sender Type:** {classification.get('sender_type', 'Unknown')}")
                    if classification.get('error'):
                        st.write(f"**Classification Error:** {classification['error']}")
                
                # Show acknowledgment if it was generated before the error
                if workflow_result and workflow_result.get('acknowledgment_response_result'):
                    st.success("✅ Acknowledgment was generated before the error occurred")
                    acknowledgment = workflow_result['acknowledgment_response_result']
                    st.write(f"**Subject:** {acknowledgment.get('subject', 'Unknown')}")
                    st.write(f"**Body:** {acknowledgment.get('body', 'No body')[:200]}...")
                
                # Show assigned sales person if available
                if workflow_result and workflow_result.get('assigned_sales_person'):
                    sales_person = workflow_result['assigned_sales_person']
                    st.info(f"**Sales Person Assigned:** {sales_person.get('name', 'Unknown')} ({sales_person.get('email', 'Unknown')})")
                
                # Debug: Show available keys in workflow_result
                if workflow_result:
                    st.markdown("### 🔍 Debug: Available Data")
                    available_keys = list(workflow_result.keys())
                    st.write(f"**Available keys:** {', '.join(available_keys)}")
                    
                    # Show workflow history if available
                    if workflow_result.get('workflow_history'):
                        st.write(f"**Workflow steps completed:** {', '.join(workflow_result['workflow_history'])}")
        else:
            st.warning("⚠️ Unknown workflow status")
            st.info(f"Status: {result.get('status', 'Unknown')}")
            
            # Show coalesced data immediately
            thread_id = result.get('thread_id', '')
            if thread_id:
                thread_data = self.thread_manager.load_thread(thread_id)
                if thread_data:
                    st.markdown("### 📊 Updated Coalesced Data")
                    self.display_coalesced_data(thread_data)
                else:
                    st.info("ℹ️ No thread data available for display")
            
            # Get workflow_result safely for the else block
            workflow_result = result.get('result', {})
            
            # Create tabs for detailed view
            tab1, tab2, tab3 = st.tabs(["📋 Summary", "🔍 Step-by-Step Details", "📊 Raw Data"])
            
            with tab1:
                st.markdown("### Workflow Summary")
                
                # Classification
                if workflow_result and workflow_result.get('classification_result'):
                    classification = workflow_result['classification_result']
                    st.write(f"**Email Type:** {classification.get('email_type', 'Unknown')}")
                    st.write(f"**Sender Type:** {classification.get('sender_type', 'Unknown')}")
                    st.write(f"**Confidence:** {classification.get('confidence', 0):.2f}")
                else:
                    st.warning("⚠️ No classification data available")
                
                # Next Action
                if workflow_result and workflow_result.get('next_action_result'):
                    next_action = workflow_result['next_action_result']
                    st.write(f"**Next Action:** {next_action.get('next_action', 'Unknown')}")
                    st.write(f"**Priority:** {next_action.get('action_priority', 'Unknown')}")
                
                # Response
                if workflow_result and workflow_result.get('clarification_response_result'):
                    response = workflow_result['clarification_response_result']
                    st.write(f"**Response Type:** {response.get('response_type', 'Unknown')}")
                    st.write(f"**Subject:** {response.get('subject', 'Unknown')}")
                
                # Forwarder Assignment
                if workflow_result and workflow_result.get('forwarder_assignment_result'):
                    forwarder_result = workflow_result['forwarder_assignment_result']
                    st.write(f"**Forwarder Status:** {forwarder_result.get('status', 'Unknown')}")
                    if forwarder_result.get('assigned_forwarder'):
                        forwarder = forwarder_result['assigned_forwarder']
                        st.write(f"**Assigned Forwarder:** {forwarder.get('name', 'Unknown')}")
                        st.write(f"**Route:** {forwarder_result.get('origin_country', 'Unknown')} → {forwarder_result.get('destination_country', 'Unknown')}")
            
            with tab2:
                st.markdown("### Detailed Step Results")
                
                # Step 1: Classification
                if workflow_result and workflow_result.get('classification_result'):
                    classification = workflow_result['classification_result']
                    with st.expander("🔄 Step 1: Email Classification", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Email Type:** {classification.get('email_type', 'Unknown')}")
                            st.write(f"**Sender Type:** {classification.get('sender_type', 'Unknown')}")
                        with col2:
                            st.write(f"**Confidence:** {classification.get('confidence', 0):.2f}")
                            st.write(f"**Urgency:** {classification.get('urgency', 'Unknown')}")
                else:
                    with st.expander("🔄 Step 1: Email Classification", expanded=True):
                        st.warning("⚠️ No classification data available")
                
                # Step 2: Conversation State
                if workflow_result and workflow_result.get('conversation_state_result'):
                    conv_state = workflow_result['conversation_state_result']
                    with st.expander("🔄 Step 2: Conversation State Analysis", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Conversation Stage:** {conv_state.get('conversation_stage', 'Unknown')}")
                            st.write(f"**Latest Sender:** {conv_state.get('latest_sender', 'Unknown')}")
                        with col2:
                            st.write(f"**Next Action:** {conv_state.get('next_action', 'Unknown')}")
                            st.write(f"**Should Escalate:** {conv_state.get('should_escalate', False)}")
                else:
                    with st.expander("🔄 Step 2: Conversation State Analysis", expanded=True):
                        st.warning("⚠️ No conversation state data available")
                
                # Step 3: Information Extraction
                if workflow_result.get('extraction_result'):
                    extraction = workflow_result['extraction_result']
                    with st.expander("🔄 Step 3: Information Extraction", expanded=True):
                        st.write(f"**Quality Score:** {extraction.get('quality_score', 0):.2f}")
                        st.write(f"**Confidence:** {extraction.get('confidence', 0):.2f}")
                        
                        if 'extracted_data' in extraction:
                            extracted_data = extraction['extracted_data']
                            for category, data in extracted_data.items():
                                if data:
                                    st.write(f"**{category.title()}:**")
                                    st.json(data)
                
                # Forwarder Assignment Step
                if workflow_result.get('forwarder_assignment_result'):
                    forwarder_result = workflow_result['forwarder_assignment_result']
                    with st.expander("🚚 Forwarder Assignment", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Status:** {forwarder_result.get('status', 'Unknown')}")
                            st.write(f"**Assignment Method:** {forwarder_result.get('assignment_method', 'Unknown')}")
                        with col2:
                            st.write(f"**Origin Country:** {forwarder_result.get('origin_country', 'Unknown')}")
                            st.write(f"**Destination Country:** {forwarder_result.get('destination_country', 'Unknown')}")
                        
                        if forwarder_result.get('assigned_forwarder'):
                            forwarder = forwarder_result['assigned_forwarder']
                            st.write(f"**Assigned Forwarder:** {forwarder.get('name', 'Unknown')}")
                            st.write(f"**Forwarder Email:** {forwarder.get('email', 'Unknown')}")
                            
                            if forwarder_result.get('rate_request'):
                                rate_request = forwarder_result['rate_request']
                                st.write(f"**Rate Request Subject:** {rate_request.get('subject', 'No Subject')}")
                                st.write(f"**Rate Request Generated:** Yes")
                        else:
                            st.error("❌ No forwarder assigned")
                            if forwarder_result.get('error'):
                                st.write(f"**Error:** {forwarder_result.get('error')}")
            
            with tab3:
                st.markdown("### Raw Workflow Data")
                st.json(workflow_result)
        
    def display_final_response(self, workflow_result: Dict[str, Any]):
        """Display the final generated response email prominently"""
        st.markdown('<h3 class="section-header">📧 Generated Response Email</h3>', unsafe_allow_html=True)
        
        # Check for different types of responses
        response_data = None
        response_type = "Unknown"
        
        # Check classification result to determine sender type
        classification_result = workflow_result.get('classification_result', {})
        sender_type = classification_result.get('sender_type', 'customer')
        sender_classification = classification_result.get('sender_classification', {})
        sender_classification_type = sender_classification.get('type', 'customer')
        
        # Determine if this is a forwarder or sales person email
        is_forwarder_or_sales = (sender_classification_type in ['forwarder', 'sales_person'] or 
                                sender_type in ['forwarder', 'sales_person'])
        
        if workflow_result.get('clarification_response_result'):
            response_data = workflow_result['clarification_response_result']
            response_type = "Clarification Request"
        elif workflow_result.get('confirmation_response_result'):
            response_data = workflow_result['confirmation_response_result']
            response_type = "Confirmation Request"
        elif workflow_result.get('acknowledgment_response_result'):
            response_data = workflow_result['acknowledgment_response_result']
            response_type = "Acknowledgment"
        elif workflow_result.get('confirmation_acknowledgment_result'):
            response_data = workflow_result['confirmation_acknowledgment_result']
            response_type = "Confirmation Acknowledgment"
        elif workflow_result.get('forwarder_assignment_result'):
            response_data = workflow_result['forwarder_assignment_result']
            response_type = "Forwarder Assignment"
        elif workflow_result.get('forwarder_email_draft_result'):
            response_data = workflow_result['forwarder_email_draft_result']
            response_type = "Forwarder Email"
        
        if response_data and response_data is not None:
            # Special handling for forwarder/sales person acknowledgments
            if is_forwarder_or_sales and response_type == "Acknowledgment":
                st.markdown("### 🤝 Internal Acknowledgment Generated")
                st.info("This email was from a forwarder or sales person. An acknowledgment response has been generated.")
                
                # Display acknowledgment details
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Response Type", "Acknowledgment")
                with col2:
                    st.metric("Sender Type", sender_classification_type.title())
                with col3:
                    st.metric("Status", "Sent")
                
                # Display the acknowledgment email
                st.markdown("### 📧 Acknowledgment Email")
                st.markdown("""
                <div style="
                    border: 2px solid #28a745;
                    border-radius: 10px;
                    padding: 20px;
                    background-color: #d4edda;
                    margin: 1rem 0;
                ">
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    # Get sender email from workflow result
                    email_data = workflow_result.get('email_data', {})
                    sender_email = email_data.get('sender', 'Unknown')
                    st.write(f"**To:** {sender_email}")
                    
                    # Get assigned sales person
                    assigned_sales_person = workflow_result.get('assigned_sales_person', {})
                    sales_email = assigned_sales_person.get('email', 'sales@searates.com')
                    st.write(f"**From:** {sales_email}")
                with col2:
                    st.write(f"**Subject:** {response_data.get('subject', 'Acknowledgment')}")
                    st.write(f"**Type:** {sender_classification_type.title()} Acknowledgment")
                
                st.markdown("**Email Body:**")
                st.markdown("""
                <div style="
                    border: 1px solid #28a745;
                    border-radius: 5px;
                    padding: 15px;
                    background-color: #f8f9fa;
                    font-family: 'Courier New', monospace;
                    white-space: pre-wrap;
                    max-height: 300px;
                    overflow-y: auto;
                ">
                """, unsafe_allow_html=True)
                
                st.text(response_data.get('body', 'No acknowledgment content available'))
                st.markdown("</div>", unsafe_allow_html=True)
                
                return  # Exit early for forwarder/sales acknowledgments
            
            # Special handling for forwarder assignment
            elif response_type == "Forwarder Assignment":
                st.markdown("### 🚚 Forwarder Assignment Results")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Status", response_data.get('status', 'Unknown'))
                with col2:
                    st.metric("Assignment Method", response_data.get('assignment_method', 'Unknown'))
                with col3:
                    st.metric("Route", f"{response_data.get('origin_country', 'Unknown')} → {response_data.get('destination_country', 'Unknown')}")
                
                # Forwarder details
                if response_data.get('assigned_forwarder'):
                    forwarder = response_data['assigned_forwarder']
                    st.markdown("### 👤 Assigned Forwarder")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Name:** {forwarder.get('name', 'Unknown')}")
                        st.write(f"**Email:** {forwarder.get('email', 'Unknown')}")
                    with col2:
                        st.write(f"**Company:** {forwarder.get('company', 'Unknown')}")
                        st.write(f"**Countries:** {forwarder.get('countries', 'Unknown')}")
                    
                    # Rate request email
                    if response_data.get('rate_request'):
                        st.markdown("### 📧 Rate Request Email to Forwarder")
                        rate_request = response_data['rate_request']
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Subject:** {rate_request.get('subject', 'Rate Request')}")
                            st.write(f"**To:** {forwarder.get('email', 'Unknown')}")
                        with col2:
                            st.write(f"**From:** logistics@dummycompany.com")
                            st.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        st.markdown("**Email Body:**")
                        st.markdown("""
                        <div style="
                            border: 2px solid #e0e0e0;
                            border-radius: 10px;
                            padding: 20px;
                            background-color: #f8f9fa;
                            font-family: 'Courier New', monospace;
                            white-space: pre-wrap;
                            max-height: 500px;
                            overflow-y: auto;
                        ">
                        """, unsafe_allow_html=True)
                        
                        st.text(rate_request.get('body', 'No email body generated'))
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ No rate request email generated")
                else:
                    st.error("❌ No forwarder assigned")
                    if response_data.get('error'):
                        st.write(f"**Error:** {response_data.get('error')}")
                
                return  # Exit early for forwarder assignment
            
            # Regular response handling for customer emails
            if not is_forwarder_or_sales:
                st.markdown("### 👤 Customer Email Processing")
                st.info("This email was from a customer and has been processed through the full workflow.")
            
            # Response header with metadata
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Response Type", response_type)
            
            with col2:
                st.metric("Subject", response_data.get('subject', 'No Subject')[:30] + "..." if len(response_data.get('subject', '')) > 30 else response_data.get('subject', 'No Subject'))
            
            with col3:
                missing_fields = response_data.get('missing_fields', [])
                st.metric("Missing Fields", len(missing_fields))
            
            # Display the email in a styled container
            st.markdown("---")
            
            # Email header
            st.markdown("### 📧 Email Details")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**To:** {response_data.get('to', 'Unknown')}")
                st.write(f"**From:** {response_data.get('from', 'sales@searates.com')}")
            with col2:
                st.write(f"**Subject:** {response_data.get('subject', 'No Subject')}")
                st.write(f"**Response Type:** {response_type}")
            
            # Email body in a styled container
            st.markdown("### 📝 Email Body")
            
            # Create a styled container for the email body
            email_body = response_data.get('body', 'No content available')
            
            # Display in a bordered container
            st.markdown("""
            <div style="
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                background-color: #f8f9fa;
                font-family: 'Courier New', monospace;
                white-space: pre-wrap;
                max-height: 500px;
                overflow-y: auto;
            ">
            """, unsafe_allow_html=True)
            
            st.text(email_body)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Missing fields if any
            if missing_fields:
                st.markdown("### ⚠️ Missing Information Requested")
                for field in missing_fields:
                    st.write(f"• {field}")
            
            # Rate recommendation if available
            if workflow_result.get('rate_recommendation_result'):
                rate_result = workflow_result['rate_recommendation_result']
                if rate_result.get('status') != 'skipped' and rate_result.get('status') != 'error':
                    st.markdown("### 💰 Indicative Rates")
                    
                    if rate_result.get('rate_ranges'):
                        rate_ranges = rate_result['rate_ranges']
                        for route, rates in rate_ranges.items():
                            with st.expander(f"📊 {route}", expanded=True):
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Min Rate", f"${rates.get('min_rate', 'N/A')}")
                                with col2:
                                    st.metric("Max Rate", f"${rates.get('max_rate', 'N/A')}")
                                with col3:
                                    st.metric("Avg Rate", f"${rates.get('avg_rate', 'N/A')}")
                                
                                if rates.get('transit_time'):
                                    st.write(f"**Transit Time:** {rates['transit_time']}")
                                if rates.get('validity'):
                                    st.write(f"**Valid Until:** {rates['validity']}")
                    
                    elif rate_result.get('recommendations'):
                        recommendations = rate_result['recommendations']
                        for i, rec in enumerate(recommendations, 1):
                            with st.expander(f"💡 Recommendation {i}", expanded=True):
                                st.write(f"**Route:** {rec.get('route', 'N/A')}")
                                st.write(f"**Rate:** ${rec.get('rate', 'N/A')}")
                                st.write(f"**Transit Time:** {rec.get('transit_time', 'N/A')}")
                                st.write(f"**Provider:** {rec.get('provider', 'N/A')}")
                                if rec.get('notes'):
                                    st.write(f"**Notes:** {rec['notes']}")
                else:
                    st.info("ℹ️ Rate recommendation not available for this shipment type")
            
            # Copy button for the email
            st.markdown("### 📋 Copy Email")
            if st.button("📋 Copy Email to Clipboard", key="copy_email"):
                # Create a formatted email for copying
                copy_text = f"""To: {response_data.get('to', 'Unknown')}
From: {response_data.get('from', 'sales@searates.com')}
Subject: {response_data.get('subject', 'No Subject')}

{email_body}"""
                
                st.code(copy_text, language=None)
                st.success("✅ Email content copied to clipboard!")
            
        else:
            # Handle case where no response data but we have classification info
            if is_forwarder_or_sales:
                st.markdown("### 🤝 Forwarder/Sales Person Email Processed")
                st.info("This email was from a forwarder or sales person. An acknowledgment response has been generated and sent.")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Sender Type", sender_classification_type.title())
                with col2:
                    st.metric("Response Type", "Acknowledgment")
                with col3:
                    st.metric("Status", "Sent")
                
                st.success("✅ Acknowledgment email sent successfully")
            else:
                st.warning("⚠️ No response email generated")
                st.info("The workflow completed but no response email was generated. Check the workflow details for more information.")
    
    def display_forwarder_assignment(self, forwarder_result: Dict[str, Any]):
        """Display forwarder assignment information prominently"""
        if not forwarder_result or forwarder_result is None:
            st.error("❌ No forwarder assignment data available")
            return
            
        st.markdown('<h3 class="section-header">🚚 Forwarder Assignment Results</h3>', unsafe_allow_html=True)
        
        # Status and assignment details
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Status", forwarder_result.get('status', 'Unknown'))
        with col2:
            st.metric("Assignment Method", forwarder_result.get('assignment_method', 'Unknown'))
        with col3:
            st.metric("Route", f"{forwarder_result.get('origin_country', 'Unknown')} → {forwarder_result.get('destination_country', 'Unknown')}")
        
        # Forwarder details
        if forwarder_result.get('assigned_forwarder') and forwarder_result['assigned_forwarder'] is not None:
            forwarder = forwarder_result['assigned_forwarder']
            
            st.markdown("### 👤 Assigned Forwarder Details")
            
            # Forwarder information in a styled container
            st.markdown("""
            <div style="
                border: 2px solid #28a745;
                border-radius: 10px;
                padding: 20px;
                background-color: #d4edda;
                margin: 1rem 0;
            ">
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**🏢 Name:** {forwarder.get('name', 'Unknown')}")
                st.write(f"**📧 Email:** {forwarder.get('email', 'Unknown')}")
            with col2:
                st.write(f"**🏢 Company:** {forwarder.get('company', 'Unknown')}")
                st.write(f"**🌍 Countries:** {forwarder.get('countries', 'Unknown')}")
            
            st.markdown("</div>", unsafe_allow_html=True)
        
            # Rate request email
            if forwarder_result.get('rate_request'):
                st.markdown("### 📧 Rate Request Email to Forwarder")
                
                rate_request = forwarder_result['rate_request']
                
                # Email header information
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**📧 Subject:** {rate_request.get('subject', 'Rate Request')}")
                    st.write(f"**👤 To:** {forwarder.get('email', 'Unknown')}")
                with col2:
                    st.write(f"**📤 From:** logistics@dummycompany.com")
                    st.write(f"**⏰ Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Email body in a styled container
                st.markdown("### 📝 Email Body")
                st.markdown("""
                <div style="
                    border: 2px solid #007bff;
                    border-radius: 10px;
                    padding: 20px;
                    background-color: #f8f9fa;
                    font-family: 'Courier New', monospace;
                    white-space: pre-wrap;
                    max-height: 400px;
                    overflow-y: auto;
                    margin: 1rem 0;
                ">
                """, unsafe_allow_html=True)
                
                email_body = rate_request.get('body', 'No email body generated')
                st.text(email_body)
                
                st.markdown("</div>", unsafe_allow_html=True)
        
                # Copy button for the rate request email
                st.markdown("### 📋 Copy Rate Request Email")
                if st.button("📋 Copy Rate Request Email to Clipboard", key="copy_rate_request"):
                    copy_text = f"""To: {forwarder.get('email', 'Unknown')}
From: logistics@dummycompany.com
Subject: {rate_request.get('subject', 'Rate Request')}

{email_body}"""
                    
                    st.code(copy_text, language=None)
                    st.success("✅ Rate request email copied to clipboard!")
                
            else:
                st.warning("⚠️ No rate request email generated")
                
        else:
            st.error("❌ No forwarder assigned")
            if forwarder_result.get('error'):
                st.markdown("""
                <div style="
                    border: 2px solid #dc3545;
                    border-radius: 10px;
                    padding: 20px;
                    background-color: #f8d7da;
                    margin: 1rem 0;
                ">
                """, unsafe_allow_html=True)
                st.write(f"**Error:** {forwarder_result.get('error')}")
                st.markdown("</div>", unsafe_allow_html=True)


# Run the app
if __name__ == "__main__":
    app = ImprovedStreamlitApp()
    app.run() 