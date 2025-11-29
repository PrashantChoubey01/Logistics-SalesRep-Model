#!/usr/bin/env python3
"""
State Diff Tool
===============

Shows exactly what changed between two workflow steps.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Set
try:
    from deepdiff import DeepDiff
except ImportError:
    print("⚠️  deepdiff not installed. Install with: pip install deepdiff")
    DeepDiff = None

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_thread_state(thread_id: str, step: int, threads_dir: Path = None) -> Optional[Dict[str, Any]]:
    """Load state at a specific step"""
    if threads_dir is None:
        threads_dir = project_root / "data" / "threads"
    
    thread_file = threads_dir / f"{thread_id}.json"
    
    if not thread_file.exists():
        print(f"❌ Thread file not found: {thread_file}")
        return None
    
    with open(thread_file, 'r') as f:
        thread_data = json.load(f)
    
    # Get email at step
    email_chain = thread_data.get("email_chain", [])
    if step >= len(email_chain):
        print(f"❌ Step {step} not found (thread has {len(email_chain)} emails)")
        return None
    
    email = email_chain[step]
    
    # Extract state from email
    return {
        "extracted_data": email.get("extracted_data", {}),
        "workflow_id": email.get("workflow_id"),
        "timestamp": email.get("timestamp"),
    }

def diff_states(state1: Dict[str, Any], state2: Dict[str, Any]):
    """Compute diff between two states"""
    if DeepDiff is None:
        # Simple fallback diff
        return {"error": "deepdiff not available"}
    return DeepDiff(state1, state2, ignore_order=True, verbose_level=2)

def format_diff(diff: DeepDiff) -> str:
    """Format diff for display"""
    lines = []
    
    if diff:
        lines.append("## Changes Detected")
        lines.append("")
        
        # Added items
        if 'dictionary_item_added' in diff:
            lines.append("### ➕ Added Fields")
            for item in diff['dictionary_item_added']:
                lines.append(f"- {item}")
            lines.append("")
        
        # Removed items
        if 'dictionary_item_removed' in diff:
            lines.append("### ➖ Removed Fields")
            for item in diff['dictionary_item_removed']:
                lines.append(f"- {item}")
            lines.append("")
        
        # Changed values
        if 'values_changed' in diff:
            lines.append("### 🔄 Changed Values")
            for path, change in diff['values_changed'].items():
                lines.append(f"- **{path}**:")
                lines.append(f"  - Old: `{change['old_value']}`")
                lines.append(f"  - New: `{change['new_value']}`")
            lines.append("")
        
        # Type changes
        if 'type_changes' in diff:
            lines.append("### 🔀 Type Changes")
            for path, change in diff['type_changes'].items():
                lines.append(f"- **{path}**: {change['old_type']} → {change['new_type']}")
            lines.append("")
    else:
        lines.append("✅ No changes detected between steps")
        lines.append("")
    
    return "\n".join(lines)

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Show state changes between workflow steps")
    parser.add_argument("--thread", type=str, required=True, help="Thread ID")
    parser.add_argument("--step", type=int, nargs=2, required=True, metavar=("STEP1", "STEP2"),
                       help="Two step numbers to compare")
    parser.add_argument("--output", type=str, help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    step1, step2 = args.step
    
    print(f"🔍 Comparing steps {step1} and {step2} in thread: {args.thread}")
    print()
    
    # Load states
    state1 = load_thread_state(args.thread, step1)
    state2 = load_thread_state(args.thread, step2)
    
    if not state1 or not state2:
        return
    
    # Compute diff
    diff = diff_states(state1, state2)
    
    # Format output
    output = format_diff(diff)
    
    if args.output:
        output_file = Path(args.output)
        output_file.write_text(output)
        print(f"✅ Diff saved to: {output_file}")
    else:
        print(output)

if __name__ == "__main__":
    main()

