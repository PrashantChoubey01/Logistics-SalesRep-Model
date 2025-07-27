#!/usr/bin/env python3
"""
Thread Cleanup Utility
======================

Cleans up old threads from JSON files to prevent accumulation of outdated data.
"""

import json
import os
import glob
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ThreadCleanupUtility:
    """Utility for cleaning up old thread data"""
    
    def __init__(self, threads_directory: str = "data/threads"):
        self.threads_directory = threads_directory
    
    def list_all_threads(self) -> List[str]:
        """List all thread files"""
        pattern = os.path.join(self.threads_directory, "*.json")
        thread_files = glob.glob(pattern)
        return thread_files
    
    def get_thread_info(self, thread_file: str) -> Dict[str, Any]:
        """Get information about a thread file"""
        try:
            with open(thread_file, 'r') as f:
                thread_data = json.load(f)
            
            # Extract basic info
            thread_id = os.path.basename(thread_file).replace('.json', '')
            email_count = len(thread_data.get('email_chain', []))
            last_activity = thread_data.get('last_updated', '')
            
            return {
                'file_path': thread_file,
                'thread_id': thread_id,
                'email_count': email_count,
                'last_activity': last_activity,
                'file_size': os.path.getsize(thread_file)
            }
        except Exception as e:
            logger.error(f"Error reading thread file {thread_file}: {e}")
            return {
                'file_path': thread_file,
                'thread_id': os.path.basename(thread_file).replace('.json', ''),
                'email_count': 0,
                'last_activity': '',
                'file_size': 0,
                'error': str(e)
            }
    
    def cleanup_old_threads(self, days_old: int = 30, dry_run: bool = True) -> Dict[str, Any]:
        """Clean up threads older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        cutoff_timestamp = cutoff_date.isoformat()
        
        all_threads = self.list_all_threads()
        threads_to_delete = []
        threads_to_keep = []
        
        for thread_file in all_threads:
            thread_info = self.get_thread_info(thread_file)
            last_activity = thread_info.get('last_activity', '')
            
            if last_activity and last_activity < cutoff_timestamp:
                threads_to_delete.append(thread_info)
            else:
                threads_to_keep.append(thread_info)
        
        # Perform cleanup
        deleted_files = []
        if not dry_run:
            for thread_info in threads_to_delete:
                try:
                    os.remove(thread_info['file_path'])
                    deleted_files.append(thread_info)
                    logger.info(f"Deleted old thread: {thread_info['thread_id']}")
                except Exception as e:
                    logger.error(f"Error deleting thread {thread_info['thread_id']}: {e}")
        
        return {
            'total_threads': len(all_threads),
            'threads_to_delete': len(threads_to_delete),
            'threads_to_keep': len(threads_to_keep),
            'deleted_files': deleted_files if not dry_run else threads_to_delete,
            'cutoff_date': cutoff_timestamp,
            'dry_run': dry_run
        }
    
    def cleanup_by_size(self, max_size_mb: int = 10, dry_run: bool = True) -> Dict[str, Any]:
        """Clean up threads by file size"""
        max_size_bytes = max_size_mb * 1024 * 1024
        
        all_threads = self.list_all_threads()
        threads_to_delete = []
        threads_to_keep = []
        
        for thread_file in all_threads:
            thread_info = self.get_thread_info(thread_file)
            file_size = thread_info.get('file_size', 0)
            
            if file_size > max_size_bytes:
                threads_to_delete.append(thread_info)
            else:
                threads_to_keep.append(thread_info)
        
        # Perform cleanup
        deleted_files = []
        if not dry_run:
            for thread_info in threads_to_delete:
                try:
                    os.remove(thread_info['file_path'])
                    deleted_files.append(thread_info)
                    logger.info(f"Deleted large thread: {thread_info['thread_id']} ({thread_info['file_size']} bytes)")
                except Exception as e:
                    logger.error(f"Error deleting thread {thread_info['thread_id']}: {e}")
        
        return {
            'total_threads': len(all_threads),
            'threads_to_delete': len(threads_to_delete),
            'threads_to_keep': len(threads_to_keep),
            'deleted_files': deleted_files if not dry_run else threads_to_delete,
            'max_size_mb': max_size_mb,
            'dry_run': dry_run
        }
    
    def cleanup_by_email_count(self, max_emails: int = 50, dry_run: bool = True) -> Dict[str, Any]:
        """Clean up threads with too many emails"""
        all_threads = self.list_all_threads()
        threads_to_delete = []
        threads_to_keep = []
        
        for thread_file in all_threads:
            thread_info = self.get_thread_info(thread_file)
            email_count = thread_info.get('email_count', 0)
            
            if email_count > max_emails:
                threads_to_delete.append(thread_info)
            else:
                threads_to_keep.append(thread_info)
        
        # Perform cleanup
        deleted_files = []
        if not dry_run:
            for thread_info in threads_to_delete:
                try:
                    os.remove(thread_info['file_path'])
                    deleted_files.append(thread_info)
                    logger.info(f"Deleted large thread: {thread_info['thread_id']} ({thread_info['email_count']} emails)")
                except Exception as e:
                    logger.error(f"Error deleting thread {thread_info['thread_id']}: {e}")
        
        return {
            'total_threads': len(all_threads),
            'threads_to_delete': len(threads_to_delete),
            'threads_to_keep': len(threads_to_keep),
            'deleted_files': deleted_files if not dry_run else threads_to_delete,
            'max_emails': max_emails,
            'dry_run': dry_run
        }
    
    def get_cleanup_summary(self) -> Dict[str, Any]:
        """Get summary of all threads for cleanup analysis"""
        all_threads = self.list_all_threads()
        thread_infos = [self.get_thread_info(thread_file) for thread_file in all_threads]
        
        total_size = sum(info.get('file_size', 0) for info in thread_infos)
        total_emails = sum(info.get('email_count', 0) for info in thread_infos)
        
        # Find oldest and newest threads
        valid_threads = [info for info in thread_infos if info.get('last_activity')]
        if valid_threads:
            oldest_thread = min(valid_threads, key=lambda x: x.get('last_activity', ''))
            newest_thread = max(valid_threads, key=lambda x: x.get('last_activity', ''))
        else:
            oldest_thread = newest_thread = None
        
        return {
            'total_threads': len(all_threads),
            'total_size_mb': total_size / (1024 * 1024),
            'total_emails': total_emails,
            'oldest_thread': oldest_thread,
            'newest_thread': newest_thread,
            'threads_with_errors': len([info for info in thread_infos if 'error' in info])
        }

def main():
    """Main function for thread cleanup"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean up old thread files')
    parser.add_argument('--days', type=int, default=30, help='Delete threads older than N days')
    parser.add_argument('--max-size', type=int, default=10, help='Delete threads larger than N MB')
    parser.add_argument('--max-emails', type=int, default=50, help='Delete threads with more than N emails')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    parser.add_argument('--summary', action='store_true', help='Show summary of all threads')
    
    args = parser.parse_args()
    
    cleanup_util = ThreadCleanupUtility()
    
    if args.summary:
        summary = cleanup_util.get_cleanup_summary()
        print("📊 THREAD CLEANUP SUMMARY")
        print("=" * 50)
        print(f"Total threads: {summary['total_threads']}")
        print(f"Total size: {summary['total_size_mb']:.2f} MB")
        print(f"Total emails: {summary['total_emails']}")
        if summary['oldest_thread']:
            print(f"Oldest thread: {summary['oldest_thread']['thread_id']} ({summary['oldest_thread']['last_activity']})")
        if summary['newest_thread']:
            print(f"Newest thread: {summary['newest_thread']['thread_id']} ({summary['newest_thread']['last_activity']})")
        print(f"Threads with errors: {summary['threads_with_errors']}")
        return
    
    if args.days > 0:
        print(f"🧹 Cleaning up threads older than {args.days} days...")
        result = cleanup_util.cleanup_old_threads(days_old=args.days, dry_run=args.dry_run)
        print(f"Found {result['threads_to_delete']} threads to delete out of {result['total_threads']} total")
        if not args.dry_run:
            print(f"Deleted {len(result['deleted_files'])} threads")
    
    if args.max_size > 0:
        print(f"🧹 Cleaning up threads larger than {args.max_size} MB...")
        result = cleanup_util.cleanup_by_size(max_size_mb=args.max_size, dry_run=args.dry_run)
        print(f"Found {result['threads_to_delete']} threads to delete out of {result['total_threads']} total")
        if not args.dry_run:
            print(f"Deleted {len(result['deleted_files'])} threads")
    
    if args.max_emails > 0:
        print(f"🧹 Cleaning up threads with more than {args.max_emails} emails...")
        result = cleanup_util.cleanup_by_email_count(max_emails=args.max_emails, dry_run=args.dry_run)
        print(f"Found {result['threads_to_delete']} threads to delete out of {result['total_threads']} total")
        if not args.dry_run:
            print(f"Deleted {len(result['deleted_files'])} threads")

if __name__ == "__main__":
    main() 