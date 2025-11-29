#!/usr/bin/env python3
"""
State Inspector
===============

Inspect workflow state at any point in execution.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def inspect_workflow_state(thread_id: str, step: int = None):
    """Inspect state at a specific step or all steps"""
    threads_dir = project_root / "data" / "threads"
    thread_file = threads_dir / f"{thread_id}.json"
    
    if not thread_file.exists():
        print(f"❌ Thread not found: {thread_file}")
        return
    
    with open(thread_file, 'r') as f:
        thread = json.load(f)
    
    email_chain = thread.get("email_chain", [])
    
    if step is not None:
        if step >= len(email_chain):
            print(f"❌ Step {step} not found (thread has {len(email_chain)} emails)")
            return
        
        inspect_single_step(email_chain[step], step)
    else:
        print(f"📊 Inspecting all {len(email_chain)} steps:")
        print("=" * 80)
        
        for i, email in enumerate(email_chain):
            print(f"\n{'='*80}")
            inspect_single_step(email, i)

def inspect_single_step(email: Dict[str, Any], step: int):
    """Inspect a single step"""
    print(f"\n📧 Step {step}: {email.get('subject', 'No subject')}")
    print(f"   Timestamp: {email.get('timestamp', 'unknown')}")
    print(f"   Sender: {email.get('sender', 'unknown')}")
    print(f"   Direction: {email.get('direction', 'unknown')}")
    
    # Extracted data
    extracted = email.get("extracted_data", {})
    if extracted:
        print(f"\n📦 Extracted Data:")
        print(json.dumps(extracted, indent=2))
    else:
        print(f"\n📦 Extracted Data: None")
    
    # Bot response
    response = email.get("bot_response", {})
    if response:
        print(f"\n📤 Bot Response:")
        print(f"   Type: {response.get('response_type', 'unknown')}")
        print(f"   Subject: {response.get('subject', 'No subject')}")
        body = response.get('body', '')
        if body:
            print(f"   Body: {body[:200]}...")
    else:
        print(f"\n📤 Bot Response: None")
    
    # Workflow metadata
    workflow_id = email.get("workflow_id")
    if workflow_id:
        print(f"\n🔄 Workflow ID: {workflow_id}")
    
    confidence = email.get("confidence_score")
    if confidence:
        print(f"   Confidence: {confidence}")

def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Inspect workflow state")
    parser.add_argument("--thread-id", type=str, required=True, help="Thread ID")
    parser.add_argument("--step", type=int, help="Specific step to inspect (default: all)")
    
    args = parser.parse_args()
    
    inspect_workflow_state(args.thread_id, args.step)

if __name__ == "__main__":
    main()

