#!/usr/bin/env python3
"""
LangGraph Orchestrator
=====================

Main orchestrator that runs the workflow.
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from workflow_graph import create_workflow_graph
from workflow_nodes import WorkflowState

class LangGraphOrchestrator:
    """Main orchestrator class."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        print("🚀 Initializing LangGraph Orchestrator...")
        self.workflow = create_workflow_graph()
        self.app = self.workflow.compile()
        print("✅ Orchestrator initialized successfully")
    
    def orchestrate_workflow(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete workflow with detailed logging."""
        print("🔄 Starting workflow execution...")
        start_time = datetime.now()
        
        try:
            # Prepare initial state
            print("📋 Preparing initial workflow state...")
            initial_state: WorkflowState = {
                "email_text": email_data.get("email_text", ""),
                "subject": email_data.get("subject", ""),
                "sender": email_data.get("sender", ""),
                "thread_id": email_data.get("thread_id", ""),
                "timestamp": email_data.get("timestamp", datetime.now().isoformat()),
                "conversation_state": "new_request",
                "confidence_score": 0.5,
                "email_type": "unknown",
                "intent": "unknown",
                "email_classification": {},
                "extracted_data": {},
                "enriched_data": {},
                "validation_results": {},
                "rate_recommendation": {},
                "current_node": "",
                "workflow_history": [],
                "errors": [],
                "next_action": "",
                "decision_result": {},
                "final_response": {},
                "workflow_complete": False
            }
            
            print(f"📧 Processing email from: {initial_state['sender']}")
            print(f"📧 Subject: {initial_state['subject']}")
            print(f"📧 Thread ID: {initial_state['thread_id']}")
            print(f"📧 Email length: {len(initial_state['email_text'])} characters")
            
            # Execute workflow
            print("🚀 Invoking workflow graph...")
            result = self.app.invoke(initial_state)
            
            # Extract final state
            final_state = result.get("__end__", result)
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            print(f"✅ Workflow completed successfully in {execution_time:.2f} seconds")
            print(f"📊 Workflow history: {' → '.join(final_state.get('workflow_history', []))}")
            
            if final_state.get("errors"):
                print(f"⚠️ Workflow completed with {len(final_state['errors'])} errors")
                for error in final_state["errors"]:
                    print(f"   ❌ {error}")
            
            return {
                "status": "success",
                "final_state": final_state,
                "workflow_complete": final_state.get("workflow_complete", False),
                "final_response": final_state.get("final_response", {}),
                "workflow_history": final_state.get("workflow_history", []),
                "errors": final_state.get("errors", [])
            }
            
        except Exception as e:
            print(f"❌ Workflow failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "workflow_complete": False
            }

def test_orchestrator():
    """Test the orchestrator with sample data."""
    print("🧪 Testing LangGraph Orchestrator")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = LangGraphOrchestrator()
    
    # Test email data
    test_email = {
        'email_text': """Hi, I need rates for 2, 20DC containers from jebel ali to mundra.
Cargo: Electronics, weight: 25,000 kg, volume: 35 CBM
Ready date: 20th august 2025

Thanks,
Mike Johnson""",
        'subject': 'Rate Request',
        'sender': 'customer@example.com',
        'thread_id': 'test-thread-1',
        'timestamp': datetime.now().isoformat()
    }
    
    print("🚀 Running workflow...")
    print("🔍 Watch for debug output and pdb breakpoints...")
    print("🔍 Use 'c' to continue at each breakpoint...")
    print("🔍 Use 'p variable_name' to print variables...")
    
    # Run workflow
    result = orchestrator.orchestrate_workflow(test_email)
    
    # Display results
    print("\n📊 Results:")
    print(f"   Status: {result.get('status')}")
    print(f"   Workflow Complete: {result.get('workflow_complete')}")
    print(f"   Errors: {len(result.get('errors', []))}")
    print(f"   Workflow History: {result.get('workflow_history', [])}")
    
    if result.get('errors'):
        print("\n❌ Errors:")
        for error in result['errors']:
            print(f"   - {error}")
    
    if result.get('final_response'):
        print("\n✅ Final Response:")
        final_response = result['final_response']
        print(f"   Type: {final_response.get('response_type', 'N/A')}")
        print(f"   Status: {final_response.get('status', 'N/A')}")
    
    print("\n🎉 Test completed!")

if __name__ == "__main__":
    test_orchestrator() 


