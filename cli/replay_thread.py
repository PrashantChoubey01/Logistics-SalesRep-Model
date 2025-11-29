#!/usr/bin/env python3
"""
Thread Replay CLI
=================

Replays a production thread for debugging and testing.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from langgraph_workflow_orchestrator import LangGraphWorkflowOrchestrator
from utils.thread_manager import ThreadManager

def load_thread(thread_id: str, threads_dir: Path = None) -> Optional[Dict[str, Any]]:
    """Load thread data from JSON file"""
    if threads_dir is None:
        threads_dir = project_root / "data" / "threads"
    
    thread_file = threads_dir / f"{thread_id}.json"
    
    if not thread_file.exists():
        print(f"❌ Thread file not found: {thread_file}")
        return None
    
    with open(thread_file, 'r') as f:
        return json.load(f)

def replay_thread(thread_id: str, step: Optional[int] = None, mock_llm: bool = False):
    """Replay a thread"""
    print(f"🔄 Replaying thread: {thread_id}")
    
    # Load thread
    thread_data = load_thread(thread_id)
    if not thread_data:
        return
    
    # Get the last email from thread
    email_chain = thread_data.get("email_chain", [])
    if not email_chain:
        print("❌ No emails in thread")
        return
    
    last_email = email_chain[-1]
    
    # Prepare email data
    email_data = {
        "sender": last_email.get("sender", ""),
        "subject": last_email.get("subject", ""),
        "content": last_email.get("content", "")
    }
    
    print(f"📧 Email: {email_data['subject']}")
    print(f"👤 From: {email_data['sender']}")
    print(f"📝 Content: {email_data['content'][:100]}...")
    print()
    
    if mock_llm:
        print("⚠️  Mock LLM mode - using test responses")
        # TODO: Implement mock LLM mode
    else:
        print("🤖 Using real LLM")
    
    # Initialize orchestrator
    try:
        orchestrator = LangGraphWorkflowOrchestrator()
        
        # Process email
        import asyncio
        result = asyncio.run(orchestrator.process_email(email_data))
        
        print("\n✅ Replay complete")
        print(f"📊 Result: {result.get('status', 'unknown')}")
        
        if step:
            print(f"📍 Stopped at step: {step}")
        
    except Exception as e:
        print(f"❌ Error during replay: {e}")
        import traceback
        traceback.print_exc()

def list_threads(threads_dir: Path = None):
    """List all available threads"""
    if threads_dir is None:
        threads_dir = project_root / "data" / "threads"
    
    thread_files = sorted(threads_dir.glob("*.json"))
    
    print(f"📋 Found {len(thread_files)} threads:")
    print()
    
    for thread_file in thread_files[:20]:  # Show first 20
        thread_id = thread_file.stem
        with open(thread_file, 'r') as f:
            thread_data = json.load(f)
            email_count = len(thread_data.get("email_chain", []))
            last_updated = thread_data.get("last_updated", "unknown")
            print(f"  - {thread_id} ({email_count} emails, updated: {last_updated})")
    
    if len(thread_files) > 20:
        print(f"  ... and {len(thread_files) - 20} more")

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Replay production threads for debugging")
    parser.add_argument("--thread-id", type=str, help="Thread ID to replay")
    parser.add_argument("--step", type=int, help="Stop at specific step")
    parser.add_argument("--mock-llm", action="store_true", help="Use mock LLM responses")
    parser.add_argument("--list", action="store_true", help="List all available threads")
    
    args = parser.parse_args()
    
    if args.list:
        list_threads()
    elif args.thread_id:
        replay_thread(args.thread_id, args.step, args.mock_llm)
    else:
        parser.print_help()
        print("\n💡 Tip: Use --list to see available threads")

if __name__ == "__main__":
    main()

