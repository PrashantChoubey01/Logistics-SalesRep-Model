#!/usr/bin/env python3
"""
Comprehensive Test Cases for All Essential Agents
================================================

This module contains test cases for all 13 essential agents in the system.
"""

import sys
import os
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test cases for each agent
AGENT_TEST_CASES = {
    "conversation_state_agent": {
        "name": "Conversation State Agent",
        "description": "Analyzes email threads to determine conversation state and next actions",
        "test_cases": [
            {
                "name": "New Logistics Request - FCL",
                "input": {
                    "email_text": "Hi, I need to ship 2x40ft containers from Shanghai to Long Beach. Ready date is February 15th. Please provide rates.",
                    "subject": "Need quote for FCL shipment",
                    "thread_id": "test-thread-1"
                },
                "expected_state": "new_thread"
            },
            {
                "name": "Clarification Response",
                "input": {
                    "email_text": "Origin is Shanghai, destination is Long Beach. Weight is 25 tons. Commodity is electronics.",
                    "subject": "Re: Clarification needed",
                    "thread_id": "test-thread-2"
                },
                "expected_state": "thread_clarification"
            },
            {
                "name": "Confirmation Response",
                "input": {
                    "email_text": "Yes, all the details are correct. Please proceed with the booking.",
                    "subject": "Re: Please confirm your shipment details",
                    "thread_id": "test-thread-3"
                },
                "expected_state": "thread_confirmation"
            },
            {
                "name": "Forwarder Rate Response",
                "input": {
                    "email_text": "Our rate is USD 2,500 per container. Valid until January 15th. Transit time 25 days.",
                    "subject": "Re: Rate Request - Shanghai to Long Beach",
                    "thread_id": "test-thread-4"
                },
                "expected_state": "thread_forwarder_interaction"
            },
            {
                "name": "Rate Inquiry Follow-up",
                "input": {
                    "email_text": "I confirmed the details yesterday. When can I expect the rates?",
                    "subject": "Re: When will I get the rates?",
                    "thread_id": "test-thread-5"
                },
                "expected_state": "thread_rate_inquiry"
            }
        ]
    },

    "classification_agent": {
        "name": "Classification Agent",
        "description": "Classifies email types and determines workflow routing",
        "test_cases": [
            {
                "name": "Customer Quote Request",
                "input": {
                    "email_text": "Hi, I need a quote for shipping 2 containers from Shanghai to Long Beach.",
                    "subject": "Quote request for FCL shipment",
                    "thread_id": "test-thread-1"
                },
                "expected_type": "customer_quote_request"
            },
            {
                "name": "Customer Clarification",
                "input": {
                    "email_text": "Here are the details: Origin Shanghai, Destination Long Beach, Weight 25 tons.",
                    "subject": "Re: Clarification needed",
                    "thread_id": "test-thread-2"
                },
                "expected_type": "customer_clarification"
            },
            {
                "name": "Forwarder Rate Quote",
                "input": {
                    "email_text": "Thank you for your inquiry. Our rate is USD 2,500 per container.",
                    "subject": "Re: Rate Request",
                    "thread_id": "test-thread-3"
                },
                "expected_type": "forwarder_rate_quote"
            },
            {
                "name": "Customer Confirmation",
                "input": {
                    "email_text": "Yes, the details are correct. Please proceed.",
                    "subject": "Re: Please confirm",
                    "thread_id": "test-thread-4"
                },
                "expected_type": "customer_confirmation"
            },
            {
                "name": "Non-Logistics Email",
                "input": {
                    "email_text": "Thank you for your continued business. Here's our newsletter.",
                    "subject": "Marketing Newsletter",
                    "thread_id": "test-thread-5"
                },
                "expected_type": "non_logistics"
            }
        ]
    },

    "extraction_agent": {
        "name": "Extraction Agent",
        "description": "Extracts shipment information from emails",
        "test_cases": [
            {
                "name": "Complete FCL Shipment",
                "input": {
                    "email_text": "I need to ship 2x40ft containers from Shanghai to Long Beach. Weight is 25 tons each. Commodity is electronics. Ready date is February 15th.",
                    "subject": "FCL shipment request",
                    "thread_id": "test-thread-1"
                },
                "expected_fields": ["origin_name", "destination_name", "shipment_type", "container_type", "quantity", "weight", "commodity", "shipment_date"]
            },
            {
                "name": "LCL Shipment",
                "input": {
                    "email_text": "Need LCL rates for 5 pallets from Mumbai to London. Volume 15 CBM, weight 2.5 tons.",
                    "subject": "LCL shipment quote",
                    "thread_id": "test-thread-2"
                },
                "expected_fields": ["origin_name", "destination_name", "shipment_type", "volume", "weight"]
            },
            {
                "name": "Incomplete Information",
                "input": {
                    "email_text": "I need to ship from China to USA. Please provide rates.",
                    "subject": "Shipping inquiry",
                    "thread_id": "test-thread-3"
                },
                "expected_fields": ["origin_country", "destination_country"]
            },
            {
                "name": "Special Requirements",
                "input": {
                    "email_text": "Need reefer container for frozen food. 1x40ft RF from Hamburg to New York.",
                    "subject": "Reefer shipment",
                    "thread_id": "test-thread-4"
                },
                "expected_fields": ["container_type", "special_requirements"]
            }
        ]
    },

    "port_lookup_agent": {
        "name": "Port Lookup Agent",
        "description": "Converts port codes to names and validates ports",
        "test_cases": [
            {
                "name": "Port Code to Name",
                "input": {
                    "port_code": "CNSHA",
                    "port_name": "Shanghai"
                },
                "expected": "Shanghai"
            },
            {
                "name": "City Name to Port",
                "input": {
                    "port_code": None,
                    "port_name": "Los Angeles"
                },
                "expected": "Los Angeles"
            },
            {
                "name": "Unknown Port Code",
                "input": {
                    "port_code": "UNKNOWN",
                    "port_name": None
                },
                "expected": None
            },
            {
                "name": "Port Validation",
                "input": {
                    "port_code": "DEHAM",
                    "port_name": "Hamburg"
                },
                "expected": "Hamburg"
            }
        ]
    },

    "container_standardization_agent": {
        "name": "Container Standardization Agent",
        "description": "Standardizes container types and validates specifications",
        "test_cases": [
            {
                "name": "Standard Container Types",
                "input": {
                    "container_type": "40GP",
                    "container_details": {}
                },
                "expected": "40GP"
            },
            {
                "name": "Reefer Container",
                "input": {
                    "container_type": "40RF",
                    "container_details": {"temperature": "-18C"}
                },
                "expected": "40RF"
            },
            {
                "name": "High Cube Container",
                "input": {
                    "container_type": "40HC",
                    "container_details": {}
                },
                "expected": "40HC"
            },
            {
                "name": "Open Top Container",
                "input": {
                    "container_type": "40OT",
                    "container_details": {}
                },
                "expected": "40OT"
            }
        ]
    },

    "enhanced_validation_agent": {
        "name": "Enhanced Validation Agent",
        "description": "Validates extracted data for completeness and consistency",
        "test_cases": [
            {
                "name": "Valid FCL Data",
                "input": {
                    "extracted_data": {
                        "origin_name": "Shanghai",
                        "destination_name": "Long Beach",
                        "shipment_type": "FCL",
                        "container_type": "40GP",
                        "quantity": 2,
                        "weight": "25 tons"
                    }
                },
                "expected": "valid"
            },
            {
                "name": "Missing Required Fields",
                "input": {
                    "extracted_data": {
                        "origin_name": "Shanghai",
                        "shipment_type": "FCL"
                    }
                },
                "expected": "missing_fields"
            },
            {
                "name": "Invalid Weight",
                "input": {
                    "extracted_data": {
                        "origin_name": "Shanghai",
                        "destination_name": "Long Beach",
                        "shipment_type": "FCL",
                        "weight": "invalid weight"
                    }
                },
                "expected": "validation_error"
            },
            {
                "name": "LCL Validation",
                "input": {
                    "extracted_data": {
                        "origin_name": "Mumbai",
                        "destination_name": "London",
                        "shipment_type": "LCL",
                        "volume": "15 CBM",
                        "weight": "2.5 tons"
                    }
                },
                "expected": "valid"
            }
        ]
    },

    "rate_recommendation_agent": {
        "name": "Rate Recommendation Agent",
        "description": "Generates rate recommendations based on route and shipment details",
        "test_cases": [
            {
                "name": "FCL Rate Recommendation",
                "input": {
                    "extracted_data": {
                        "origin_name": "Shanghai",
                        "destination_name": "Long Beach",
                        "shipment_type": "FCL",
                        "container_type": "40GP",
                        "quantity": 2
                    }
                },
                "expected_fields": ["indicative_rate", "transit_time", "valid_until"]
            },
            {
                "name": "LCL Rate Recommendation",
                "input": {
                    "extracted_data": {
                        "origin_name": "Mumbai",
                        "destination_name": "London",
                        "shipment_type": "LCL",
                        "volume": "15 CBM"
                    }
                },
                "expected_fields": ["indicative_rate", "transit_time", "valid_until"]
            },
            {
                "name": "Reefer Rate Recommendation",
                "input": {
                    "extracted_data": {
                        "origin_name": "Hamburg",
                        "destination_name": "New York",
                        "shipment_type": "FCL",
                        "container_type": "40RF",
                        "special_requirements": "Frozen food"
                    }
                },
                "expected_fields": ["indicative_rate", "transit_time", "valid_until"]
            }
        ]
    },

    "next_action_agent": {
        "name": "Next Action Agent",
        "description": "Determines next actions based on conversation state and data analysis",
        "test_cases": [
            {
                "name": "Send Clarification Request",
                "input": {
                    "conversation_state": "new_thread",
                    "email_classification": {"email_type": "customer_quote_request"},
                    "extracted_data": {"origin_name": "Shanghai"},
                    "confidence_score": 0.3,
                    "missing_fields": ["destination_name", "weight", "commodity"]
                },
                "expected_action": "send_clarification_request"
            },
            {
                "name": "Send Confirmation Request",
                "input": {
                    "conversation_state": "thread_clarification",
                    "email_classification": {"email_type": "customer_clarification"},
                    "extracted_data": {"origin_name": "Shanghai", "destination_name": "Long Beach", "weight": "25 tons"},
                    "confidence_score": 0.8,
                    "missing_fields": []
                },
                "expected_action": "send_confirmation_request"
            },
            {
                "name": "Assign Forwarders",
                "input": {
                    "conversation_state": "thread_confirmation",
                    "email_classification": {"email_type": "customer_confirmation"},
                    "extracted_data": {"origin_name": "Shanghai", "destination_name": "Long Beach"},
                    "confidence_score": 0.9,
                    "missing_fields": []
                },
                "expected_action": "booking_details_confirmed_assign_forwarders"
            },
            {
                "name": "Escalate to Sales",
                "input": {
                    "conversation_state": "thread_escalation",
                    "email_classification": {"email_type": "confusing_email"},
                    "extracted_data": {},
                    "confidence_score": 0.2,
                    "missing_fields": ["origin_name", "destination_name"]
                },
                "expected_action": "escalate_confusing_email"
            }
        ]
    },

    "response_generator_agent": {
        "name": "Response Generator Agent",
        "description": "Generates customer responses based on conversation state and data",
        "test_cases": [
            {
                "name": "Clarification Request Email",
                "input": {
                    "response_type": "clarification_request",
                    "extracted_data": {"origin_name": "Shanghai"},
                    "missing_fields": ["destination_name", "weight", "commodity"],
                    "email_thread_history": []
                },
                "expected_fields": ["response_body", "subject", "sales_person"]
            },
            {
                "name": "Confirmation Request Email",
                "input": {
                    "response_type": "confirmation_request",
                    "extracted_data": {"origin_name": "Shanghai", "destination_name": "Long Beach", "weight": "25 tons"},
                    "rate_recommendation": {"indicative_rate": "USD 2,500"},
                    "email_thread_history": []
                },
                "expected_fields": ["response_body", "subject", "sales_person"]
            },
            {
                "name": "Confirmation Acknowledgment Email",
                "input": {
                    "response_type": "confirmation_acknowledgment",
                    "extracted_data": {"origin_name": "Shanghai", "destination_name": "Long Beach"},
                    "email_thread_history": []
                },
                "expected_fields": ["response_body", "subject", "sales_person"]
            },
            {
                "name": "Port Confirmation Email",
                "input": {
                    "response_type": "port_confirmation",
                    "extracted_data": {"origin_name": "Shanghai"},
                    "port_details": {"port_name": "Shanghai", "port_code": "CNSHA"},
                    "email_thread_history": []
                },
                "expected_fields": ["response_body", "subject", "sales_person"]
            }
        ]
    },

    "forwarder_assignment_agent": {
        "name": "Forwarder Assignment Agent",
        "description": "Assigns forwarders based on route and generates rate requests",
        "test_cases": [
            {
                "name": "China to USA Route",
                "input": {
                    "extraction_data": {
                        "origin_country": "China",
                        "destination_country": "USA",
                        "shipment_type": "FCL"
                    },
                    "enriched_data": {
                        "port_lookup": {
                            "origin_port": {"name": "Shanghai", "country": "China"},
                            "destination_port": {"name": "Long Beach", "country": "USA"}
                        }
                    }
                },
                "expected_fields": ["assigned_forwarders", "rate_requests"]
            },
            {
                "name": "Germany to USA Route",
                "input": {
                    "extraction_data": {
                        "origin_country": "Germany",
                        "destination_country": "USA",
                        "shipment_type": "FCL"
                    },
                    "enriched_data": {
                        "port_lookup": {
                            "origin_port": {"name": "Hamburg", "country": "Germany"},
                            "destination_port": {"name": "New York", "country": "USA"}
                        }
                    }
                },
                "expected_fields": ["assigned_forwarders", "rate_requests"]
            },
            {
                "name": "LCL Shipment",
                "input": {
                    "extraction_data": {
                        "origin_country": "India",
                        "destination_country": "UK",
                        "shipment_type": "LCL"
                    },
                    "enriched_data": {
                        "port_lookup": {
                            "origin_port": {"name": "Mumbai", "country": "India"},
                            "destination_port": {"name": "London", "country": "UK"}
                        }
                    }
                },
                "expected_fields": ["assigned_forwarders", "rate_requests"]
            }
        ]
    },

    "forwarder_detection_agent": {
        "name": "Forwarder Detection Agent",
        "description": "Detects if an email is from a forwarder",
        "test_cases": [
            {
                "name": "Forwarder Email",
                "input": {
                    "email_text": "Thank you for your rate request. Our rate is USD 2,500 per container.",
                    "sender": "rates@globallogistics.com",
                    "subject": "Re: Rate Request"
                },
                "expected": True
            },
            {
                "name": "Customer Email",
                "input": {
                    "email_text": "I need a quote for shipping from Shanghai to Long Beach.",
                    "sender": "customer@company.com",
                    "subject": "Quote request"
                },
                "expected": False
            },
            {
                "name": "Forwarder Rate Quote",
                "input": {
                    "email_text": "Here are our rates: USD 2,500 per 40ft container. Valid until January 15th.",
                    "sender": "quotes@shippingco.com",
                    "subject": "Rate Quote"
                },
                "expected": True
            },
            {
                "name": "Sales Team Email",
                "input": {
                    "email_text": "Please review this customer inquiry for follow-up.",
                    "sender": "sales@company.com",
                    "subject": "Customer inquiry"
                },
                "expected": False
            }
        ]
    },

    "forwarder_response_agent": {
        "name": "Forwarder Response Agent",
        "description": "Processes forwarder responses and extracts rate information",
        "test_cases": [
            {
                "name": "Rate Quote Response",
                "input": {
                    "email_text": "Thank you for your inquiry. Our rate is USD 2,500 per 40ft container. Transit time 25 days. Valid until January 15th.",
                    "subject": "Re: Rate Request",
                    "sender": "rates@forwarder.com"
                },
                "expected_fields": ["rate_amount", "transit_time", "valid_until"]
            },
            {
                "name": "Rate Inquiry Response",
                "input": {
                    "email_text": "We need more details about your shipment to provide accurate rates. Please specify container type and weight.",
                    "subject": "Re: Rate Request",
                    "sender": "quotes@forwarder.com"
                },
                "expected_fields": ["response_type", "missing_information"]
            },
            {
                "name": "Rate Acknowledgment",
                "input": {
                    "email_text": "We have received your rate request and will provide a quote within 24 hours.",
                    "subject": "Re: Rate Request",
                    "sender": "rates@forwarder.com"
                },
                "expected_fields": ["response_type", "processing_time"]
            },
            {
                "name": "Rate Rejection",
                "input": {
                    "email_text": "We regret to inform you that we cannot provide rates for this route at this time.",
                    "subject": "Re: Rate Request",
                    "sender": "rates@forwarder.com"
                },
                "expected_fields": ["response_type", "rejection_reason"]
            }
        ]
    }
}

def get_agent_test_cases(agent_name):
    """Get test cases for a specific agent."""
    return AGENT_TEST_CASES.get(agent_name, {})

def get_all_agent_names():
    """Get list of all agent names."""
    return list(AGENT_TEST_CASES.keys())

def get_agent_info(agent_name):
    """Get information about a specific agent."""
    agent_data = AGENT_TEST_CASES.get(agent_name, {})
    return {
        "name": agent_data.get("name", agent_name),
        "description": agent_data.get("description", "No description available"),
        "test_count": len(agent_data.get("test_cases", []))
    } 