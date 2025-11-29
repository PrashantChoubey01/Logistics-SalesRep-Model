#!/usr/bin/env python3
"""
Thread Cleanup Utility
======================

Utility script to clean up thread history files.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def list_threads(threads_dir: Path) -> List[Path]:
    """List all thread files"""
    if not threads_dir.exists():
        return []
    
    return list(threads_dir.glob("*.json"))


def delete_all_threads(threads_dir: Path, confirm: bool = False) -> int:
    """Delete all thread files"""
    threads = list_threads(threads_dir)
    
    if not threads:
        print("No thread files found.")
        return 0
    
    if not confirm:
        print(f"Found {len(threads)} thread files.")
        response = input("Are you sure you want to delete ALL threads? (yes/no): ")
        if response.lower() != "yes":
            print("Cancelled.")
            return 0
    
    deleted = 0
    for thread_file in threads:
        try:
            thread_file.unlink()
            deleted += 1
        except Exception as e:
            print(f"Error deleting {thread_file.name}: {e}")
    
    print(f"✅ Deleted {deleted} thread files.")
    return deleted


def delete_old_threads(threads_dir: Path, days_old: int = 7, confirm: bool = False) -> int:
    """Delete threads older than specified days"""
    from datetime import datetime, timedelta
    
    threads = list_threads(threads_dir)
    
    if not threads:
        print("No thread files found.")
        return 0
    
    cutoff_date = datetime.now() - timedelta(days=days_old)
    old_threads = []
    
    for thread_file in threads:
        try:
            mtime = datetime.fromtimestamp(thread_file.stat().st_mtime)
            if mtime < cutoff_date:
                old_threads.append(thread_file)
        except Exception as e:
            print(f"Error checking {thread_file.name}: {e}")
    
    if not old_threads:
        print(f"No threads older than {days_old} days found.")
        return 0
    
    if not confirm:
        print(f"Found {len(old_threads)} threads older than {days_old} days.")
        response = input(f"Delete these {len(old_threads)} threads? (yes/no): ")
        if response.lower() != "yes":
            print("Cancelled.")
            return 0
    
    deleted = 0
    for thread_file in old_threads:
        try:
            thread_file.unlink()
            deleted += 1
        except Exception as e:
            print(f"Error deleting {thread_file.name}: {e}")
    
    print(f"✅ Deleted {deleted} old thread files.")
    return deleted


def delete_test_threads(threads_dir: Path, confirm: bool = False) -> int:
    """Delete test thread files (those starting with 'test_' or 'demo_')"""
    threads = list_threads(threads_dir)
    
    if not threads:
        print("No thread files found.")
        return 0
    
    test_threads = [t for t in threads if t.stem.startswith("test_") or t.stem.startswith("demo_")]
    
    if not test_threads:
        print("No test thread files found.")
        return 0
    
    if not confirm:
        print(f"Found {len(test_threads)} test thread files.")
        response = input(f"Delete these {len(test_threads)} test threads? (yes/no): ")
        if response.lower() != "yes":
            print("Cancelled.")
            return 0
    
    deleted = 0
    for thread_file in test_threads:
        try:
            thread_file.unlink()
            deleted += 1
        except Exception as e:
            print(f"Error deleting {thread_file.name}: {e}")
    
    print(f"✅ Deleted {deleted} test thread files.")
    return deleted


def main():
    """Main cleanup function"""
    threads_dir = project_root / "data" / "threads"
    
    print("="*80)
    print("Thread Cleanup Utility")
    print("="*80)
    print(f"\nThreads directory: {threads_dir}")
    
    threads = list_threads(threads_dir)
    print(f"Total threads found: {len(threads)}")
    
    if len(threads) == 0:
        print("No threads to clean up.")
        return
    
    print("\nOptions:")
    print("1. Delete ALL threads")
    print("2. Delete threads older than 7 days")
    print("3. Delete threads older than 30 days")
    print("4. Delete test threads only (test_*, demo_*)")
    print("5. Cancel")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        delete_all_threads(threads_dir)
    elif choice == "2":
        delete_old_threads(threads_dir, days_old=7)
    elif choice == "3":
        delete_old_threads(threads_dir, days_old=30)
    elif choice == "4":
        delete_test_threads(threads_dir)
    elif choice == "5":
        print("Cancelled.")
    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()

