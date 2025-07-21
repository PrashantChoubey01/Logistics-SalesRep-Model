#!/usr/bin/env python3
"""
Demo Email Chain Test Script
============================

Tests the complete email chain to validate all intelligent features.
"""

import json
import time
from datetime import datetime
from langgraph_orchestrator import LangGraphOrchestrator

class EmailChainTester:
    """Test the email chain step by step."""
    
    def __init__(self):
        self.orchestrator = LangGraphOrchestrator()
        self.conversation_history = []
        self.thread_id = "demo-email-chain-test"
        
    def add_email_to_chain(self, email_data):
        """Add email to the conversation chain."""
        # Build the full email chain
        email_text = email_data["content"]
        
        if self.conversation_history:
            # Add previous conversation history
            email_text += "\n\n---\nPrevious Conversation:\n"
            for i, prev_email in enumerate(reversed(self.conversation_history)):
                email_text += f"\nFrom: {prev_email['sender']}\n"
                email_text += f"Subject: {prev_email['subject']}\n"
                email_text += f"Date: {prev_email['timestamp']}\n\n"
                email_text += prev_email['content']
        
        # Create the email object
        email = {
            'email_text': email_text,
            'subject': email_data['subject'],
            'sender': email_data['sender'],
            'thread_id': self.thread_id,
            'timestamp': email_data.get('timestamp', datetime.now().isoformat())
        }
        
        return email
    
    def process_email(self, email_data, expected_intelligence=None):
        """Process a single email and analyze the response."""
        print(f"\n{'='*80}")
        print(f"📧 PROCESSING EMAIL {len(self.conversation_history) + 1}")
        print(f"{'='*80}")
        print(f"From: {email_data['sender']}")
        print(f"Subject: {email_data['subject']}")
        print(f"Expected Intelligence: {expected_intelligence}")
        print(f"{'='*80}")
        
        # Add email to chain
        email = self.add_email_to_chain(email_data)
        
        # Process with orchestrator
        start_time = time.time()
        result = self.orchestrator.orchestrate_workflow(email)
        processing_time = time.time() - start_time
        
        # Store in conversation history
        self.conversation_history.append({
            'sender': email_data['sender'],
            'subject': email_data['subject'],
            'content': email_data['content'],
            'timestamp': email_data.get('timestamp', datetime.now().isoformat())
        })
        
        # Analyze results
        self.analyze_response(result, expected_intelligence, processing_time)
        
        # Store bot response in history
        if result.get('final_response'):
            bot_response = result['final_response']
            self.conversation_history.append({
                'sender': f"{bot_response.get('sales_person_name', 'Bot')}@dpworld.com",
                'subject': bot_response.get('response_subject', 'Re: ' + email_data['subject']),
                'content': bot_response.get('response_body', ''),
                'timestamp': datetime.now().isoformat(),
                'is_bot': True
            })
        
        return result
    
    def analyze_response(self, result, expected_intelligence, processing_time):
        """Analyze the bot's response against expected intelligence."""
        print(f"\n📊 ANALYSIS RESULTS")
        print(f"{'='*50}")
        
        # Basic status
        print(f"✅ Status: {result.get('status', 'unknown')}")
        print(f"⏱️ Processing Time: {processing_time:.2f}s")
        print(f"🔄 Workflow Complete: {result.get('workflow_complete', False)}")
        
        # Get final state
        final_state = result.get('final_state', {})
        
        # Analyze conversation state
        conversation_state = final_state.get('conversation_state', 'unknown')
        print(f"💬 Conversation State: {conversation_state}")
        
        # Analyze email classification
        email_classification = final_state.get('email_classification', {})
        email_type = email_classification.get('email_type', 'unknown')
        confidence = email_classification.get('confidence', 0.0)
        print(f"🏷️ Email Type: {email_type} (confidence: {confidence:.2f})")
        
        # Analyze next action
        decision_result = final_state.get('decision_result', {})
        next_action = decision_result.get('next_action', 'unknown')
        reasoning = decision_result.get('reasoning', 'No reasoning provided')
        print(f"🎯 Next Action: {next_action}")
        print(f"🧠 Reasoning: {reasoning}")
        
        # Analyze extracted data
        extracted_data = final_state.get('extracted_data', {})
        if extracted_data:
            print(f"\n📋 EXTRACTED DATA:")
            print(f"  Origin: {extracted_data.get('origin_name', 'N/A')} ({extracted_data.get('origin_country', 'N/A')})")
            print(f"  Destination: {extracted_data.get('destination_name', 'N/A')} ({extracted_data.get('destination_country', 'N/A')})")
            print(f"  Shipment Type: {extracted_data.get('shipment_type', 'N/A')}")
            print(f"  Container: {extracted_data.get('container_type', 'N/A')}")
            print(f"  Weight: {extracted_data.get('weight', 'N/A')}")
            print(f"  Commodity: {extracted_data.get('commodity', 'N/A')}")
        
        # Analyze validation results
        validation_results = final_state.get('validation_results', {})
        if validation_results:
            overall_validation = validation_results.get('overall_validation', {})
            completeness = overall_validation.get('completeness_score', 0.0)
            confidence_score = overall_validation.get('confidence_score', 0.0)
            missing_fields = overall_validation.get('missing_fields', [])
            print(f"\n✅ VALIDATION:")
            print(f"  Completeness: {completeness:.1%}")
            print(f"  Confidence: {confidence_score:.1%}")
            print(f"  Missing Fields: {missing_fields if missing_fields else 'None'}")
        
        # Analyze forwarder assignment
        forwarder_assignment = final_state.get('forwarder_assignment', {})
        if forwarder_assignment:
            total_forwarders = forwarder_assignment.get('total_forwarders', 0)
            origin_country = forwarder_assignment.get('origin_country', 'N/A')
            destination_country = forwarder_assignment.get('destination_country', 'N/A')
            print(f"\n🔧 FORWARDER ASSIGNMENT:")
            print(f"  Total Forwarders: {total_forwarders}")
            print(f"  Origin Country: {origin_country}")
            print(f"  Destination Country: {destination_country}")
            
            rate_requests = forwarder_assignment.get('rate_requests', [])
            if rate_requests:
                print(f"  Rate Requests Generated: {len(rate_requests)}")
                for i, request in enumerate(rate_requests, 1):
                    print(f"    {i}. {request['forwarder_name']} ({request['forwarder_email']})")
        
        # Analyze bot response
        final_response = result.get('final_response', {})
        if final_response:
            response_type = final_response.get('response_type', 'unknown')
            sales_person = final_response.get('sales_person_name', 'Unknown')
            subject = final_response.get('response_subject', 'No subject')
            print(f"\n🤖 BOT RESPONSE:")
            print(f"  Type: {response_type}")
            print(f"  Sales Person: {sales_person}")
            print(f"  Subject: {subject}")
            print(f"  Body Preview: {final_response.get('response_body', '')[:100]}...")
        
        # Check against expected intelligence
        if expected_intelligence:
            print(f"\n🎯 EXPECTED INTELLIGENCE CHECK:")
            self.check_expected_intelligence(result, expected_intelligence)
        
        print(f"{'='*50}")
    
    def check_expected_intelligence(self, result, expected):
        """Check if the response matches expected intelligence."""
        final_state = result.get('final_state', {})
        
        # Check conversation state
        if 'conversation_state' in expected:
            actual_state = final_state.get('conversation_state', 'unknown')
            expected_state = expected['conversation_state']
            if actual_state == expected_state:
                print(f"  ✅ Conversation State: {actual_state}")
            else:
                print(f"  ❌ Conversation State: Expected {expected_state}, got {actual_state}")
        
        # Check email classification
        if 'email_type' in expected:
            actual_type = final_state.get('email_classification', {}).get('email_type', 'unknown')
            expected_type = expected['email_type']
            if actual_type == expected_type:
                print(f"  ✅ Email Type: {actual_type}")
            else:
                print(f"  ❌ Email Type: Expected {expected_type}, got {actual_type}")
        
        # Check next action
        if 'next_action' in expected:
            actual_action = final_state.get('decision_result', {}).get('next_action', 'unknown')
            expected_action = expected['next_action']
            if actual_action == expected_action:
                print(f"  ✅ Next Action: {actual_action}")
            else:
                print(f"  ❌ Next Action: Expected {expected_action}, got {actual_action}")
        
        # Check response type
        if 'response_type' in expected:
            actual_response_type = result.get('final_response', {}).get('response_type', 'unknown')
            expected_response_type = expected['response_type']
            if actual_response_type == expected_response_type:
                print(f"  ✅ Response Type: {actual_response_type}")
            else:
                print(f"  ❌ Response Type: Expected {expected_response_type}, got {actual_response_type}")

def run_demo_email_chain():
    """Run the complete demo email chain test."""
    print("🚀 DEMO EMAIL CHAIN TEST")
    print("="*80)
    print("Testing all intelligent features step by step...")
    print("="*80)
    
    tester = EmailChainTester()
    
    # Email 1: Initial Request (Countries Only)
    email1 = {
        'sender': 'john.smith@techcorp.com',
        'subject': 'Need shipping quote for electronics',
        'content': '''Hi,

I need to ship some electronics from China to USA. Can you provide a quote?

Thanks,
John Smith
TechCorp Inc.''',
        'timestamp': '2024-01-15T10:30:00'
    }
    
    expected1 = {
        'conversation_state': 'new_request',
        'email_type': 'logistics_request',
        'next_action': 'send_clarification_request',
        'response_type': 'clarification_request'
    }
    
    result1 = tester.process_email(email1, expected1)
    
    # Email 2: Clarification Response (Specific Ports)
    email2 = {
        'sender': 'john.smith@techcorp.com',
        'subject': 'Re: Need shipping quote for electronics',
        'content': '''Hi Sarah,

Thanks for your quick response. Here are the details:

Origin: Shanghai, China
Destination: Los Angeles, USA
Container: 40ft HC
Weight: 15 tons
Shipment date: February 15, 2024
Commodity: Electronics (smartphones and tablets)

Please let me know the rates.

Best regards,
John Smith
TechCorp Inc.''',
        'timestamp': '2024-01-15T14:45:00'
    }
    
    expected2 = {
        'conversation_state': 'clarification_response',
        'email_type': 'logistics_request',
        'next_action': 'send_confirmation_request',
        'response_type': 'confirmation_response'
    }
    
    result2 = tester.process_email(email2, expected2)
    
    # Email 3: Confirmation Response
    email3 = {
        'sender': 'john.smith@techcorp.com',
        'subject': 'Re: Need shipping quote for electronics',
        'content': '''Hi Sarah,

Yes, all the details are correct. Please proceed with the booking.

Also, what about insurance coverage for the electronics?

Thanks,
John Smith
TechCorp Inc.''',
        'timestamp': '2024-01-15T16:20:00'
    }
    
    expected3 = {
        'conversation_state': 'confirmation_reply',
        'email_type': 'confirmation_reply',
        'next_action': 'booking_details_confirmed_assign_forwarders',
        'response_type': 'confirmation_acknowledgment'
    }
    
    result3 = tester.process_email(email3, expected3)
    
    # Email 4: Forwarder Response (Rates)
    email4 = {
        'sender': 'rates@globalfreight.com',
        'subject': 'Re: Quote Request - Shanghai to Los Angeles',
        'content': '''Dear Sarah,

Thank you for your inquiry. Please find our rates below:

40ft HC Container
Shanghai to Los Angeles
Rate: USD 3,200 (freight only)
Valid until: January 30, 2024
Transit time: 18-22 days

Insurance coverage available at 0.3% of cargo value.

Please let us know if you need any additional information.

Best regards,
Michael Chen
Global Freight Solutions''',
        'timestamp': '2024-01-16T09:15:00'
    }
    
    expected4 = {
        'conversation_state': 'forwarder_response',
        'email_type': 'forwarder_response',
        'next_action': 'collate_rates_and_send_to_sales',
        'response_type': 'forwarder_acknowledgment'
    }
    
    result4 = tester.process_email(email4, expected4)
    
    # Email 5: Confusing Customer Email
    email5 = {
        'sender': 'john.smith@techcorp.com',
        'subject': 'Re: Need shipping quote for electronics',
        'content': '''Hi,

Ok, thanks. Will check and get back to you.

John''',
        'timestamp': '2024-01-16T11:30:00'
    }
    
    expected5 = {
        'conversation_state': 'confusing_response',
        'email_type': 'confusing_email',
        'next_action': 'escalate_confusing_email',
        'response_type': 'escalation_response'
    }
    
    result5 = tester.process_email(email5, expected5)
    
    # Email 6: Clear Follow-up
    email6 = {
        'sender': 'john.smith@techcorp.com',
        'subject': 'Re: Need shipping quote for electronics',
        'content': '''Hi Sarah,

I've reviewed the rates and they look good. I'd like to proceed with the booking.

Can you please confirm the insurance coverage details and send me the booking confirmation?

Thanks,
John Smith
TechCorp Inc.''',
        'timestamp': '2024-01-16T15:45:00'
    }
    
    expected6 = {
        'conversation_state': 'booking_request',
        'email_type': 'booking_request',
        'next_action': 'notify_sales_team',
        'response_type': 'sales_notification'
    }
    
    result6 = tester.process_email(email6, expected6)
    
    # Email 7: Non-Logistics Email
    email7 = {
        'sender': 'john.smith@techcorp.com',
        'subject': 'Meeting Request',
        'content': '''Hi Sarah,

I'd like to schedule a meeting to discuss our future shipping needs.

Are you available for a call next week?

Thanks,
John Smith
TechCorp Inc.''',
        'timestamp': '2024-01-17T10:00:00'
    }
    
    expected7 = {
        'conversation_state': 'non_logistics',
        'email_type': 'non_logistics',
        'next_action': 'route_to_appropriate_department',
        'response_type': 'standard_response'
    }
    
    result7 = tester.process_email(email7, expected7)
    
    # Email 8: Mixed Intent Email
    email8 = {
        'sender': 'john.smith@techcorp.com',
        'subject': 'Re: Need shipping quote for electronics',
        'content': '''Hi Sarah,

Thanks for the rates. I have a few questions:

1. Can you also quote for LCL shipment?
2. What about customs clearance services?
3. Do you handle door-to-door delivery?

Also, I might need to ship some machinery next month.

Best regards,
John Smith
TechCorp Inc.''',
        'timestamp': '2024-01-17T14:20:00'
    }
    
    expected8 = {
        'conversation_state': 'logistics_request',
        'email_type': 'logistics_request',
        'next_action': 'send_clarification_request',
        'response_type': 'clarification_request'
    }
    
    result8 = tester.process_email(email8, expected8)
    
    # Email 9: Vague Response
    email9 = {
        'sender': 'john.smith@techcorp.com',
        'subject': 'Re: Need shipping quote for electronics',
        'content': '''Hi,

Maybe. Let me think about it.

John''',
        'timestamp': '2024-01-17T16:30:00'
    }
    
    expected9 = {
        'conversation_state': 'confusing_response',
        'email_type': 'confusing_email',
        'next_action': 'escalate_confusing_email',
        'response_type': 'escalation_response'
    }
    
    result9 = tester.process_email(email9, expected9)
    
    # Final Summary
    print(f"\n{'='*80}")
    print(f"🎯 FINAL TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total Emails Processed: {len(tester.conversation_history)}")
    print(f"Thread ID: {tester.thread_id}")
    print(f"Conversation History Length: {len(tester.conversation_history)}")
    
    print(f"\n📊 CONVERSATION TIMELINE:")
    for i, email in enumerate(tester.conversation_history, 1):
        sender_type = "🤖 BOT" if email.get('is_bot') else "👤 CUSTOMER"
        print(f"  {i}. {sender_type}: {email['sender']} - {email['subject']}")
    
    print(f"\n✅ DEMO EMAIL CHAIN TEST COMPLETED!")
    print(f"{'='*80}")

if __name__ == "__main__":
    run_demo_email_chain() 