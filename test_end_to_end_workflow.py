#!/usr/bin/env python3
"""
Test script to verify end-to-end workflow with all agents
"""

import sys
import os
import json
from datetime import datetime

# Add the agents directory to the path
agents_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agents")
sys.path.insert(0, agents_path)

try:
    from agents.langgraph_orchestrator import run_workflow
except ImportError as e:
    print(f"Error importing orchestrator: {e}")
    sys.exit(1)

def test_end_to_end_workflow():
    """Test the complete end-to-end workflow"""
    
    print("🚀 Testing End-to-End Workflow")
    print("=" * 50)
    
    # Test cases with different scenarios
    test_cases = [
        {
            "name": "Complete FCL Request",
            "subject": "Rate request for container shipment",
            "email": """Hi,

We need to ship 50 containers from Jebel Ali to Mundra. 
Details as follows:
- Container type: 20DC
- Total quantity: 50 containers
- Weight: 15 metric tons per container
- Shipment type: FCL
- Cargo: Electronics
- Shipment date: 15th December 2024

Please provide rates and transit time.

Best regards,
John Smith
ABC Electronics Ltd.""",
            "expected_agents": ["classification", "extraction", "validation", "smart_clarification", "confirmation", "container_standardization", "port_lookup", "rate_parser", "rate_recommendation", "forwarder_assignment", "response"]
        },
        {
            "name": "LCL Request with Missing Info",
            "subject": "LCL shipment quote needed",
            "email": """Hello,

I need to ship some goods from Shanghai to Los Angeles.
It's LCL shipment, around 5 CBM.

Please provide a quote.

Thanks,
Sarah Johnson""",
            "expected_agents": ["classification", "extraction", "validation", "smart_clarification", "confirmation", "container_standardization", "port_lookup", "rate_parser", "rate_recommendation", "forwarder_assignment", "response"]
        },
        {
            "name": "Confirmation Email",
            "subject": "Re: Rate request - Confirming details",
            "email": """Hi Sarah,

Yes, that's correct. Please proceed with the booking for 50 containers from Jebel Ali to Mundra.
20DC containers, electronics cargo, shipping on 15th December.

Thanks,
John""",
            "expected_agents": ["classification", "extraction", "validation", "smart_clarification", "confirmation", "container_standardization", "port_lookup", "rate_parser", "rate_recommendation", "forwarder_assignment", "response"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📧 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Run the workflow with message thread format
            message_thread = [{
                "sender": "test@example.com",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "body": test_case['email'],
                "subject": test_case['subject']
            }]
            
            result = run_workflow(
                message_thread=message_thread,
                subject=test_case['subject'],
                thread_id=f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{i}"
            )
            
            # Check if all expected agents are present
            print("✅ Workflow completed successfully")
            
            # Display agent results
            print("\n🔍 Agent Results:")
            for agent_name in test_case['expected_agents']:
                if agent_name in result:
                    print(f"  ✅ {agent_name}: Present")
                    
                    # Show key information for important agents
                    if agent_name == "classification":
                        email_type = result[agent_name].get('email_type', 'N/A')
                        confidence = result[agent_name].get('confidence', 'N/A')
                        print(f"     - Email Type: {email_type} (Confidence: {confidence})")
                    
                    elif agent_name == "extraction":
                        origin = result[agent_name].get('origin', 'N/A')
                        destination = result[agent_name].get('destination', 'N/A')
                        print(f"     - Origin: {origin}, Destination: {destination}")
                    
                    elif agent_name == "smart_clarification":
                        clarification_needed = result[agent_name].get('clarification_needed', False)
                        questions = result[agent_name].get('questions', [])
                        print(f"     - Clarification Needed: {clarification_needed}")
                        if questions:
                            print(f"     - Questions: {len(questions)} questions")
                            for j, q in enumerate(questions[:3], 1):  # Show first 3 questions
                                print(f"       {j}. {q}")
                            if len(questions) > 3:
                                print(f"       ... and {len(questions) - 3} more")
                    
                    elif agent_name == "confirmation":
                        is_confirmation = result[agent_name].get('is_confirmation', False)
                        confirmation_type = result[agent_name].get('confirmation_type', 'N/A')
                        print(f"     - Is Confirmation: {is_confirmation}")
                        print(f"     - Confirmation Type: {confirmation_type}")
                    
                    elif agent_name == "response":
                        response_type = result[agent_name].get('response_type', 'N/A')
                        response_subject = result[agent_name].get('response_subject', 'N/A')
                        print(f"     - Response Type: {response_type}")
                        print(f"     - Subject: {response_subject}")
                        
                        # Show response body preview
                        response_body = result[agent_name].get('response_body', '')
                        if response_body:
                            preview = response_body[:100] + "..." if len(response_body) > 100 else response_body
                            print(f"     - Body Preview: {preview}")
                else:
                    print(f"  ❌ {agent_name}: Missing")
            
            # Check rate information
            if 'rate' in result:
                rate = result['rate']
                if rate and isinstance(rate, dict):
                    indicative_rate = rate.get('indicative_rate', 'Not available')
                    print(f"\n💰 Rate Information:")
                    print(f"  - Indicative Rate: {indicative_rate}")
                    
                    if 'rate_recommendation' in rate:
                        rec = rate['rate_recommendation']
                        rate_range = rec.get('rate_range', 'Not available')
                        match_type = rec.get('match_type', 'Not available')
                        print(f"  - Rate Range: {rate_range}")
                        print(f"  - Match Type: {match_type}")
            
            # Check for any errors or warnings
            print(f"\n📊 Summary:")
            total_agents = len(test_case['expected_agents'])
            present_agents = sum(1 for agent in test_case['expected_agents'] if agent in result)
            print(f"  - Agents Present: {present_agents}/{total_agents}")
            print(f"  - Success Rate: {(present_agents/total_agents)*100:.1f}%")
            
            if present_agents == total_agents:
                print("  ✅ All agents executed successfully")
            else:
                print("  ⚠️  Some agents are missing")
            
        except Exception as e:
            print(f"❌ Error in test case {i}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🏁 End-to-End Workflow Testing Complete")

if __name__ == "__main__":
    test_end_to_end_workflow() 