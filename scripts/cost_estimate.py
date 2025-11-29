#!/usr/bin/env python3
"""
Cost Estimation Tool
====================

Estimates LLM API costs for processing threads.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Model pricing (per 1M tokens) - update as needed
MODEL_PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "databricks-claude-3-7-sonnet": {"input": 3.00, "output": 15.00},  # Estimate
    "databricks-meta-llama-3-70b-instruct": {"input": 0.50, "output": 0.50},  # Estimate
}

def estimate_tokens(text: str) -> int:
    """Rough token estimation (4 chars = 1 token)"""
    return len(text) // 4

def estimate_thread_cost(thread_data: Dict[str, Any], model: str = "gpt-4o") -> Dict[str, float]:
    """Estimate cost for processing a thread"""
    if model not in MODEL_PRICING:
        print(f"⚠️  Unknown model: {model}, using gpt-4o pricing")
        model = "gpt-4o"
    
    pricing = MODEL_PRICING[model]
    
    total_input_tokens = 0
    total_output_tokens = 0
    
    # Estimate tokens for each email
    email_chain = thread_data.get("email_chain", [])
    for email in email_chain:
        content = email.get("content", "")
        total_input_tokens += estimate_tokens(content)
        
        # Estimate response tokens (assume response is ~50% of input)
        total_output_tokens += estimate_tokens(content) // 2
    
    # Calculate costs
    input_cost = (total_input_tokens / 1_000_000) * pricing["input"]
    output_cost = (total_output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost
    
    return {
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
        "model": model
    }

def estimate_batch_cost(threads: int, model: str = "gpt-4o", avg_thread_size: int = 5) -> Dict[str, float]:
    """Estimate cost for processing multiple threads"""
    # Average email size (rough estimate)
    avg_email_size = 500  # characters
    avg_response_size = 300  # characters
    
    avg_input_tokens = (avg_email_size * avg_thread_size) // 4
    avg_output_tokens = (avg_response_size * avg_thread_size) // 4
    
    if model not in MODEL_PRICING:
        model = "gpt-4o"
    
    pricing = MODEL_PRICING[model]
    
    total_input_tokens = avg_input_tokens * threads
    total_output_tokens = avg_output_tokens * threads
    
    input_cost = (total_input_tokens / 1_000_000) * pricing["input"]
    output_cost = (total_output_tokens / 1_000_000) * pricing["output"]
    total_cost = input_cost + output_cost
    
    return {
        "threads": threads,
        "avg_input_tokens_per_thread": avg_input_tokens,
        "avg_output_tokens_per_thread": avg_output_tokens,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
        "cost_per_thread": total_cost / threads if threads > 0 else 0,
        "model": model
    }

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Estimate LLM API costs")
    parser.add_argument("--threads", type=int, help="Number of threads to process")
    parser.add_argument("--thread-id", type=str, help="Specific thread ID to analyze")
    parser.add_argument("--model", type=str, default="gpt-4o", help="Model name for pricing")
    
    args = parser.parse_args()
    
    if args.thread_id:
        # Analyze specific thread
        threads_dir = project_root / "data" / "threads"
        thread_file = threads_dir / f"{args.thread_id}.json"
        
        if not thread_file.exists():
            print(f"❌ Thread not found: {thread_file}")
            return
        
        with open(thread_file, 'r') as f:
            thread_data = json.load(f)
        
        cost = estimate_thread_cost(thread_data, args.model)
        
        print(f"💰 Cost Estimate for Thread: {args.thread_id}")
        print(f"   Model: {cost['model']}")
        print(f"   Input Tokens: {cost['input_tokens']:,}")
        print(f"   Output Tokens: {cost['output_tokens']:,}")
        print(f"   Input Cost: ${cost['input_cost']:.4f}")
        print(f"   Output Cost: ${cost['output_cost']:.4f}")
        print(f"   Total Cost: ${cost['total_cost']:.4f}")
    
    elif args.threads:
        # Estimate batch cost
        cost = estimate_batch_cost(args.threads, args.model)
        
        print(f"💰 Batch Cost Estimate")
        print(f"   Threads: {cost['threads']:,}")
        print(f"   Model: {cost['model']}")
        print(f"   Avg Tokens/Thread: {cost['avg_input_tokens_per_thread']:,} input, {cost['avg_output_tokens_per_thread']:,} output")
        print(f"   Total Tokens: {cost['total_input_tokens']:,} input, {cost['total_output_tokens']:,} output")
        print(f"   Input Cost: ${cost['input_cost']:.2f}")
        print(f"   Output Cost: ${cost['output_cost']:.2f}")
        print(f"   Total Cost: ${cost['total_cost']:.2f}")
        print(f"   Cost/Thread: ${cost['cost_per_thread']:.4f}")
    
    else:
        parser.print_help()
        print("\n💡 Examples:")
        print("  python scripts/cost_estimate.py --threads 100 --model gpt-4o")
        print("  python scripts/cost_estimate.py --thread-id thread_20251128_093336 --model databricks-claude-3-7-sonnet")

if __name__ == "__main__":
    main()

