#!/usr/bin/env python3
"""
Forwarder Acknowledgment API
============================

API endpoint to generate forwarder acknowledgment emails when UI button is clicked.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.forwarder_response_agent import ForwarderResponseAgent

def generate_forwarder_acknowledgment(forwarder_assignment: Dict[str, Any], customer_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate forwarder acknowledgment emails.
    
    Args:
        forwarder_assignment: Forwarder assignment data from workflow
        customer_data: Customer and shipment data
        
    Returns:
        Dict containing acknowledgment emails and metadata
    """
    try:
        # Initialize the forwarder response agent
        agent = ForwarderResponseAgent()
        agent.load_context()
        
        # Generate acknowledgment emails
        result = agent.generate_forwarder_assignment_acknowledgment(forwarder_assignment, customer_data)
        
        if result.get('status') == 'success':
            return {
                'status': 'success',
                'acknowledgments': result.get('acknowledgments', []),
                'total_forwarders': result.get('total_forwarders', 0),
                'message': f'Generated {result.get("total_forwarders", 0)} forwarder acknowledgment emails',
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'status': 'error',
                'error': result.get('error', 'Failed to generate acknowledgments'),
                'timestamp': datetime.now().isoformat()
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'error': f'Exception occurred: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }

def get_forwarder_mail_trail(customer_thread_history: list, forwarder_acknowledgments: list) -> Dict[str, Any]:
    """
    Generate forwarder mail trail for UI display.
    
    Args:
        customer_thread_history: Customer email conversation history
        forwarder_acknowledgments: Generated forwarder acknowledgment emails
        
    Returns:
        Dict containing both customer and forwarder mail trails
    """
    try:
        # Customer mail trail
        customer_trail = []
        for email in customer_thread_history:
            if email['type'] == 'customer':
                customer_trail.append({
                    'type': 'customer',
                    'sender': email['sender'],
                    'subject': email['subject'],
                    'content': email['content'],
                    'timestamp': email['timestamp']
                })
            elif email['type'] == 'bot':
                customer_trail.append({
                    'type': 'bot',
                    'sender': email['sender'],
                    'subject': email['subject'],
                    'content': email['content'],
                    'timestamp': email['timestamp'],
                    'response_type': email.get('response_type', 'unknown')
                })
        
        # Forwarder mail trail
        forwarder_trail = []
        for ack in forwarder_acknowledgments:
            forwarder_trail.append({
                'type': 'forwarder_acknowledgment',
                'sender': 'SeaRates Team <sales@searates.com>',
                'recipient': f"{ack['forwarder_name']} <{ack['forwarder_email']}>",
                'subject': ack['subject'],
                'content': ack['body'],
                'timestamp': ack['timestamp'],
                'forwarder_name': ack['forwarder_name'],
                'forwarder_email': ack['forwarder_email']
            })
        
        return {
            'status': 'success',
            'customer_trail': customer_trail,
            'forwarder_trail': forwarder_trail,
            'total_customer_emails': len(customer_trail),
            'total_forwarder_emails': len(forwarder_trail),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': f'Exception occurred: {str(e)}',
            'timestamp': datetime.now().isoformat()
        } 