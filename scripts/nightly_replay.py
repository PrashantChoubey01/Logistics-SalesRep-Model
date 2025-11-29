#!/usr/bin/env python3
"""
Nightly Replay Script
=====================

Picks random prod threads and replays against staging image to detect regressions.
"""

import argparse
import json
import random
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def load_threads(threads_dir: Path, sample_size: int = 50) -> List[str]:
    """Load random sample of thread IDs"""
    thread_files = list(threads_dir.glob("*.json"))
    
    if len(thread_files) < sample_size:
        print(f"⚠️  Only {len(thread_files)} threads available, using all")
        sample_size = len(thread_files)
    
    selected = random.sample(thread_files, sample_size)
    return [f.stem for f in selected]

def replay_thread(thread_id: str, staging: bool = False) -> Dict[str, Any]:
    """Replay a single thread"""
    # This would call the actual replay logic
    # For now, return mock result
    return {
        "thread_id": thread_id,
        "status": "success",
        "diff": {}  # Empty diff means no changes
    }

def compare_results(prod_result: Dict[str, Any], staging_result: Dict[str, Any]) -> Dict[str, Any]:
    """Compare prod vs staging results"""
    # Simple diff check
    prod_body = prod_result.get("response", {}).get("body", "")
    staging_body = staging_result.get("response", {}).get("body", "")
    
    # Remove timestamps for comparison
    import re
    prod_clean = re.sub(r'\d{4}-\d{2}-\d{2}.*?\d{2}:\d{2}:\d{2}', '', prod_body)
    staging_clean = re.sub(r'\d{4}-\d{2}-\d{2}.*?\d{2}:\d{2}:\d{2}', '', staging_body)
    
    has_diff = prod_clean != staging_clean
    
    return {
        "has_diff": has_diff,
        "diff_size": abs(len(prod_clean) - len(staging_clean)) if has_diff else 0
    }

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Nightly replay for regression detection")
    parser.add_argument("--sample", type=int, default=50, help="Number of threads to sample")
    parser.add_argument("--staging", action="store_true", help="Compare against staging")
    parser.add_argument("--output", type=str, help="Output file for results")
    
    args = parser.parse_args()
    
    threads_dir = project_root / "data" / "threads"
    
    print(f"🔄 Loading {args.sample} random threads...")
    thread_ids = load_threads(threads_dir, args.sample)
    
    print(f"✅ Selected {len(thread_ids)} threads")
    
    results = []
    diffs_found = 0
    
    for thread_id in thread_ids:
        print(f"  Replaying: {thread_id}...")
        
        prod_result = replay_thread(thread_id, staging=False)
        
        if args.staging:
            staging_result = replay_thread(thread_id, staging=True)
            diff = compare_results(prod_result, staging_result)
            
            if diff["has_diff"]:
                diffs_found += 1
                print(f"    ⚠️  Diff detected (size: {diff['diff_size']})")
            
            results.append({
                "thread_id": thread_id,
                "diff": diff
            })
        else:
            results.append({
                "thread_id": thread_id,
                "status": prod_result["status"]
            })
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Total Threads: {len(thread_ids)}")
    if args.staging:
        print(f"   Diffs Found: {diffs_found}")
        print(f"   Status: {'❌ FAILED' if diffs_found > 0 else '✅ PASSED'}")
    
    # Save results
    if args.output:
        output_file = Path(args.output)
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"   Results saved: {output_file}")
    
    # Exit with error if diffs found
    if args.staging and diffs_found > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()

