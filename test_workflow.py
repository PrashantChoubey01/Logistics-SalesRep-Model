#!/usr/bin/env python3
"""
Test Workflow
============

Simple test script to run the LangGraph workflow with debugging.
"""

from langgraph_orchestrator import LangGraphOrchestrator

def main():
    """Run the workflow test."""
    print("🧪 Testing LangGraph Workflow")
    print("=" * 40)
    
    # Initialize orchestrator
    orchestrator = LangGraphOrchestrator()
    
    # Test data
    test_email = {
        'email_text': "Hi, I need rates for 2 20 feet containers from jebel ali to mundra.",
        'subject': 'Rate Request',
        'sender': 'test@example.com',
        'thread_id': 'debug-test-1'
    }
    
    print("🚀 Running workflow with debugging...")
    print("🔍 You'll hit pdb breakpoints at key points:")
    print("   - DATA_ENRICHMENT: Check extracted data")
    print("   - Before/after port lookup")
    print("   - Before/after container standardization")
    print("   - VALIDATION: Check enriched data")
    print("   - Before/after validation agent")
    print("   - RATE_RECOMMENDATION: Check validation results")
    print("   - Before/after rate recommendation")
    print("\n🔍 Commands to use:")
    print("   c - continue to next breakpoint")
    print("   p variable_name - print variable")
    print("   l - list current code")
    print("   q - quit debugging")
    
    # Run workflow
    result = orchestrator.orchestrate_workflow(test_email)
    
    print(f"\n✅ Test completed! Status: {result.get('status')}")

if __name__ == "__main__":
    main() 