#!/usr/bin/env python3
"""
Simple Demo App for Testing Workflow
====================================
- Dropdown with 2 email IDs (customer and forwarder)
- Default email content for each
- Process email and see response
- All emails in same thread
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from langgraph_workflow_orchestrator import LangGraphWorkflowOrchestrator

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'thread_id' not in st.session_state:
    # Default to timestamp-based thread ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.thread_id = f"demo_thread_{timestamp}"
if 'email_history' not in st.session_state:
    st.session_state.email_history = []

# Page config
st.set_page_config(page_title="SeaRates Logistics AI Sales Assistant", layout="wide", page_icon="🚢")

# Beautiful formatted title - always visible
st.markdown("""
    <div style="text-align: center; padding: 20px 0; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.15);">
        <h1 style="color: white; margin: 0; font-size: 2.5em; font-weight: 700; letter-spacing: 1px; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
            🚢 SeaRates AI
        </h1>
        <p style="color: #e8f4f8; margin: 10px 0 0 0; font-size: 1.3em; font-weight: 400; letter-spacing: 0.5px;">
            Logistics Sales Assistant
        </p>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# Initialize orchestrator
if st.session_state.orchestrator is None:
    with st.spinner("Initializing workflow orchestrator..."):
        try:
            st.session_state.orchestrator = LangGraphWorkflowOrchestrator()
            st.success("✅ Orchestrator initialized!")
        except Exception as e:
            st.error(f"❌ Failed to initialize: {e}")
            st.stop()

# Thread info
col1, col2 = st.columns([3, 1])
with col1:
    st.info(f"📧 **Thread ID:** `{st.session_state.thread_id}` - All emails will be part of this thread")
with col2:
    if st.button("🔄 Reset Thread"):
        # Create new thread with current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.thread_id = f"demo_thread_{timestamp}"
        st.session_state.email_history = []
        st.rerun()

st.markdown("---")

# Email templates
CUSTOMER_EMAIL = """Hello Searates,

I need a shipping quote for a full container load from Shanghai, China to Los Angeles, USA.

Details:
- Origin: Shanghai, China
- Destination: Los Angeles, USA
- Container Type: 40HC
- Number of Containers: 2
- Commodity: Electronics
- Weight: 20,000 kg per container
- Ready Date: 2024-03-15
- Incoterm: FOB

Please provide rates and transit time.

Best regards,
John Doe
Logistics Manager
TechCorp Inc."""

FORWARDER_EMAIL = """Dear Logistics Team,

Please find our rate quote for the Shanghai to Los Angeles route:

Route: Shanghai (CNSHA) to Los Angeles (USLAX)
Container: 40HC
Rate: $2,850 USD
Transit Time: 18 days
Valid Until: August 31, 2025

Please confirm if you would like to proceed with this rate.

Best regards,
DHL Global Forwarding"""

# Email form
st.subheader("📝 Send Email")

col1, col2 = st.columns([1, 2])

with col1:
    email_type = st.selectbox(
        "Email From:",
        ["Customer", "Forwarder"],
        help="Select who is sending the email"
    )

with col2:
    if email_type == "Customer":
        sender_email = st.text_input("Customer Email", "john.doe@techcorp.com")
        default_content = CUSTOMER_EMAIL
    else:
        sender_email = st.text_input("Forwarder Email", "dhl@dhl.com")
        default_content = FORWARDER_EMAIL

subject = st.text_input("Subject", 
    "FCL Shipping Quote - Shanghai to Los Angeles" if email_type == "Customer" else "Rate Quote - Shanghai to Los Angeles")

content = st.text_area("Email Content", default_content, height=250)

if st.button("🚀 Process Email", type="primary"):
    if not content.strip():
        st.error("❌ Email content cannot be empty")
    else:
        with st.spinner("Processing email through workflow..."):
            try:
                # Prepare email data - include thread_id so all emails are in same thread
                email_data = {
                    "sender": sender_email,
                    "subject": subject,
                    "content": content,
                    "thread_id": st.session_state.thread_id
                }
                
                # Process email
                result = asyncio.run(st.session_state.orchestrator.process_email(email_data))
                
                # Extract response
                workflow_state = result.get('result', {})
                
                # Find the response
                response = None
                response_type = None
                
                if workflow_state.get('confirmation_response_result'):
                    response = workflow_state['confirmation_response_result']
                    response_type = "Confirmation"
                elif workflow_state.get('clarification_response_result'):
                    response = workflow_state['clarification_response_result']
                    response_type = "Clarification"
                elif workflow_state.get('confirmation_acknowledgment_result'):
                    response = workflow_state['confirmation_acknowledgment_result']
                    response_type = "Confirmation Acknowledgment"
                elif workflow_state.get('acknowledgment_response_result'):
                    response = workflow_state['acknowledgment_response_result']
                    response_type = "Acknowledgment"
                
                # Get forwarder assignment details if available
                forwarder_assignment = workflow_state.get('forwarder_assignment_result')
                
                # Get forwarder response and sales notification if available
                forwarder_response = workflow_state.get('forwarder_response_result')
                sales_notification = workflow_state.get('sales_notification_result')
                
                # Add to history
                st.session_state.email_history.append({
                    "type": email_type,
                    "sender": sender_email,
                    "subject": subject,
                    "content": content,
                    "response": response,
                    "response_type": response_type,
                    "forwarder_assignment": forwarder_assignment,
                    "forwarder_response": forwarder_response,
                    "sales_notification": sales_notification
                })
                
                # Display response
                st.markdown("---")
                st.subheader(f"✅ Response Generated ({response_type})")
                
                if response:
                    st.markdown(f"**Subject:** {response.get('subject', 'N/A')}")
                    st.markdown("**Body:**")
                    st.text_area("Response Body", response.get('body', 'N/A'), height=300, key=f"response_{len(st.session_state.email_history)}", label_visibility="collapsed")
                else:
                    st.warning("⚠️ No response generated")
                
                # Display forwarder assignment details if available
                if forwarder_assignment:
                    st.markdown("---")
                    st.subheader("🚚 Forwarder Assignment")
                    
                    assigned_forwarder = forwarder_assignment.get('assigned_forwarder', {})
                    rate_request = forwarder_assignment.get('rate_request', {})
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown("**Forwarder Details:**")
                        st.markdown(f"- **Name:** {assigned_forwarder.get('name', 'N/A')}")
                        st.markdown(f"- **Email:** {assigned_forwarder.get('email', 'N/A')}")
                        st.markdown(f"- **Company:** {assigned_forwarder.get('company', 'N/A')}")
                        st.markdown(f"- **Route:** {forwarder_assignment.get('origin_country', 'N/A')} → {forwarder_assignment.get('destination_country', 'N/A')}")
                    
                    with col2:
                        if rate_request:
                            st.markdown("**Rate Request Email:**")
                            st.markdown(f"- **To:** {rate_request.get('to_email', 'N/A')}")
                            st.markdown(f"- **Subject:** {rate_request.get('subject', 'N/A')}")
                            st.markdown("**Body:**")
                            st.text_area("Forwarder Email Body", rate_request.get('body', 'N/A'), height=200, key=f"forwarder_email_{len(st.session_state.email_history)}", disabled=True, label_visibility="collapsed")
                
                # Display forwarder response (rates) if available
                if forwarder_response and not forwarder_response.get('error'):
                    st.markdown("---")
                    st.subheader("📊 Forwarder Response (Rates Received)")
                    
                    rate_info = forwarder_response.get('rate_info', {})
                    if rate_info:
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.markdown("**Rate Information:**")
                            st.markdown(f"- **Rate:** {rate_info.get('rate', 'N/A')}")
                            st.markdown(f"- **Currency:** {rate_info.get('currency', 'N/A')}")
                            st.markdown(f"- **Transit Time:** {rate_info.get('transit_time', 'N/A')}")
                        with col2:
                            st.markdown("**Additional Details:**")
                            st.markdown(f"- **Valid Until:** {rate_info.get('valid_until', 'N/A')}")
                            st.markdown(f"- **Sailing Date:** {rate_info.get('sailing_date', 'N/A')}")
                            if rate_info.get('additional_notes'):
                                st.markdown(f"- **Notes:** {rate_info.get('additional_notes')}")
                
                # Display forwarder acknowledgment if available
                if workflow_state.get('acknowledgment_response_result'):
                    forwarder_ack = workflow_state['acknowledgment_response_result']
                    # Show acknowledgment for forwarder emails
                    if forwarder_ack.get('sender_type') == 'forwarder' or email_type == 'Forwarder':
                        st.markdown("---")
                        st.subheader("🤝 Forwarder Acknowledgment")
                        st.info("Bot's response to forwarder email.")
                        st.markdown(f"**Subject:** {forwarder_ack.get('subject', 'N/A')}")
                        st.markdown(f"**To:** {forwarder_ack.get('sender_email', sender_email)}")
                        st.markdown("**Body:**")
                        st.text_area("Forwarder Acknowledgment Body", forwarder_ack.get('body', 'N/A'), height=200, key=f"forwarder_ack_{len(st.session_state.email_history)}", disabled=True, label_visibility="collapsed")
                
                # Display sales notification (collated email) if available
                if sales_notification and not sales_notification.get('error'):
                    st.markdown("---")
                    st.subheader("📧 Sales Notification (Collated Email)")
                    st.info("This email contains customer requirements and forwarder rate information for the sales team.")
                    
                    st.markdown(f"**Subject:** {sales_notification.get('subject', 'N/A')}")
                    st.markdown(f"**To:** {sales_notification.get('to', 'Sales Team')}")
                    st.markdown(f"**Priority:** {sales_notification.get('priority', 'N/A')}")
                    st.markdown("**Body:**")
                    st.text_area("Sales Notification Body", sales_notification.get('body', 'N/A'), height=400, key=f"sales_notification_{len(st.session_state.email_history)}", disabled=True, label_visibility="collapsed")
                
                # Display final customer quote email if available
                if workflow_state.get('customer_quote_result'):
                    customer_quote = workflow_state['customer_quote_result']
                    if not customer_quote.get('error'):
                        st.markdown("---")
                        st.subheader("📨 Final Customer Quote Email")
                        st.success("This is the final email to be sent to the customer with rates.")
                        st.markdown(f"**Subject:** {customer_quote.get('subject', 'N/A')}")
                        st.markdown(f"**To:** {customer_quote.get('to', 'N/A')}")
                        st.markdown(f"**From:** {customer_quote.get('from', 'N/A')}")
                        st.markdown("**Body:**")
                        st.text_area("Customer Quote Body", customer_quote.get('body', 'N/A'), height=400, key=f"customer_quote_{len(st.session_state.email_history)}", disabled=True, label_visibility="collapsed")
                
                st.success("✅ Email processed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error processing email: {e}")
                import traceback
                st.code(traceback.format_exc())

st.markdown("---")

# Forwarder Response Section (if forwarder was assigned)
if st.session_state.email_history:
    last_email = st.session_state.email_history[-1]
    if last_email.get('forwarder_assignment'):
        st.subheader("📧 Respond as Forwarder")
        st.info("A forwarder has been assigned. You can respond as the forwarder to test the bot's response.")
        
        forwarder_assignment = last_email['forwarder_assignment']
        assigned_forwarder = forwarder_assignment.get('assigned_forwarder', {})
        forwarder_email = assigned_forwarder.get('email', 'forwarder@example.com')
        
        with st.form("forwarder_response_form"):
            forwarder_subject = st.text_input("Subject", "Rate Quote - Shanghai to Los Angeles")
            forwarder_content = st.text_area("Forwarder Response", 
                f"""Dear Logistics Team,

Please find our rate quote:

Route: Shanghai (CNSHG) to Los Angeles (USLAX)
Container: 40HC
Rate: $2,850 USD
Transit Time: 18 days
Valid Until: December 31, 2024

Please confirm if you would like to proceed.

Best regards,
{assigned_forwarder.get('name', 'Forwarder Team')}""", 
                height=200)
            
            if st.form_submit_button("📤 Send Forwarder Response"):
                with st.spinner("Processing forwarder response..."):
                    try:
                        email_data = {
                            "sender": forwarder_email,
                            "subject": forwarder_subject,
                            "content": forwarder_content,
                            "thread_id": st.session_state.thread_id
                        }
                        
                        result = asyncio.run(st.session_state.orchestrator.process_email(email_data))
                        workflow_state = result.get('result', {})
                        
                        # Find response
                        response = None
                        response_type = None
                        
                        if workflow_state.get('sales_notification_result'):
                            response = workflow_state['sales_notification_result']
                            response_type = "Sales Notification"
                        elif workflow_state.get('acknowledgment_response_result'):
                            response = workflow_state['acknowledgment_response_result']
                            response_type = "Acknowledgment"
                        
                        # Add to history
                        st.session_state.email_history.append({
                            "type": "Forwarder",
                            "sender": forwarder_email,
                            "subject": forwarder_subject,
                            "content": forwarder_content,
                            "response": response,
                            "response_type": response_type
                        })
                        
                        st.success("✅ Forwarder response processed!")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                        import traceback
                        st.code(traceback.format_exc())

st.markdown("---")

# Email history
if st.session_state.email_history:
    st.subheader("📜 Email History")
    
    for idx, email in enumerate(reversed(st.session_state.email_history)):
        with st.expander(f"Email #{len(st.session_state.email_history) - idx}: {email['type']} - {email['subject']}", expanded=(idx == 0)):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("**📤 Sent:**")
                st.markdown(f"- **From:** {email['sender']}")
                st.markdown(f"- **Subject:** {email['subject']}")
                st.markdown("**Content:**")
                st.text_area("Email Content", email['content'], height=150, key=f"sent_{idx}", disabled=True, label_visibility="collapsed")
            
            with col2:
                st.markdown(f"**📥 Response ({email['response_type']}):**")
                if email['response']:
                    st.markdown(f"- **Subject:** {email['response'].get('subject', 'N/A')}")
                    st.markdown("**Body:**")
                    st.text_area("Response Body", email['response'].get('body', 'N/A'), height=150, key=f"resp_{idx}", disabled=True, label_visibility="collapsed")
                else:
                    st.info("No response generated")

