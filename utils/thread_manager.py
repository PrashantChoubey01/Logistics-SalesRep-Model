#!/usr/bin/env python3
"""
Enhanced Thread Manager for Multi-Party Email Conversations
==========================================================

Manages email threads with mixed information from customer and bot emails,
prioritizing recent information while maintaining conversation context.
"""

import json
import os
import pickle
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class EmailEntry:
    """Represents a single email in a thread"""
    timestamp: str
    email_id: str
    sender: str
    direction: str  # "inbound" (customer/forwarder) or "outbound" (bot)
    subject: str
    content: str
    extracted_data: Optional[Dict[str, Any]] = None
    response_type: Optional[str] = None  # clarification, confirmation, acknowledgment
    bot_response: Optional[Dict[str, Any]] = None
    workflow_id: Optional[str] = None
    confidence_score: Optional[float] = None

@dataclass
class ThreadData:
    """Represents a complete email thread"""
    thread_id: str
    email_chain: List[EmailEntry]
    cumulative_extraction: Dict[str, Any]
    last_updated: str
    customer_context: Dict[str, Any]
    forwarder_context: Dict[str, Any]
    conversation_state: str = "new_thread"
    total_emails: int = 0

class ThreadManager:
    """Enhanced thread manager for mixed customer-bot conversations"""
    
    def __init__(self, storage_dir: str = "data/threads"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        # Enhanced merge strategies for different data types
        self.merge_strategies = {
            "shipment_details": self._merge_shipment_details,
            "contact_information": self._merge_contact_info,
            "timeline_information": self._merge_timeline_info,
            "special_requirements": self._merge_special_requirements,
            "rate_information": self._merge_rate_info,
            "additional_notes": self._merge_additional_notes
        }
        
        logger.info(f"ThreadManager initialized with storage directory: {storage_dir}")

    def _merge_shipment_details(self, new_data: Dict[str, Any], cumulative_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge shipment details with recency priority and handle shipment_type conflicts"""
        # Start with a copy of cumulative_data to preserve all existing keys
        merged = cumulative_data.copy() if cumulative_data else {}
        
        # Log initial state for debugging
        logger.debug(f"🔍 Merge shipment_details - Cumulative keys: {list(cumulative_data.keys()) if cumulative_data else []}, New keys: {list(new_data.keys())}")
        
        # CRITICAL: Check if shipment_type is being set in new data
        new_shipment_type = new_data.get("shipment_type", "").strip().upper() if new_data.get("shipment_type") else ""
        
        # If shipment_type is explicitly set, handle conflicts
        if new_shipment_type:
            merged["shipment_type"] = new_shipment_type
            
            # If shipment_type is LCL, clear FCL-specific fields
            if new_shipment_type == "LCL":
                # Clear container_type and container_count for LCL shipments
                if "container_type" in merged:
                    del merged["container_type"]
                if "container_count" in merged:
                    del merged["container_count"]
                logger.debug(f"Cleared container_type and container_count for LCL shipment")
            
            # If shipment_type is FCL, clear LCL-specific fields
            elif new_shipment_type == "FCL":
                # Clear weight and volume for FCL shipments (they're not required)
                # But only if they're not explicitly provided in new data
                if "weight" not in new_data or not new_data.get("weight", "").strip():
                    if "weight" in merged:
                        del merged["weight"]
                if "volume" not in new_data or not new_data.get("volume", "").strip():
                    if "volume" in merged:
                        del merged["volume"]
                logger.debug(f"Cleared weight/volume for FCL shipment (if not in new data)")
        
        # Merge all other fields with recency priority
        # CRITICAL: Empty strings MUST be treated as "no update" (per Rule 4)
        # Do NOT delete existing values when new_value is empty string
        for key, new_value in new_data.items():
            if key == "shipment_type":
                # Already handled above
                continue
            elif new_value and str(new_value).strip():  # Only update if new value is not empty
                merged[key] = new_value
                logger.debug(f"Updated shipment detail {key}: {new_value}")
            # CRITICAL: Do NOT delete keys when new_value is empty string
            # Empty strings are treated as "no update" - preserve existing value
            # If key is missing from new_data entirely, it's also preserved (handled by starting with cumulative_data.copy())
        
        # Log final state to verify all keys are preserved
        logger.debug(f"✅ Merge shipment_details complete - Final keys: {list(merged.keys())}")
        return merged

    def _merge_contact_info(self, new_data: Dict[str, Any], cumulative_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge contact information with recency priority"""
        # Start with a copy of cumulative_data to preserve all existing keys
        merged = cumulative_data.copy() if cumulative_data else {}
        
        # CRITICAL: Empty strings MUST be treated as "no update" (per Rule 4)
        # Only update if new value is non-empty
        for key, new_value in new_data.items():
            if new_value and str(new_value).strip():
                merged[key] = new_value
                logger.debug(f"Updated contact info {key}: {new_value}")
            # Empty strings are treated as "no update" - preserve existing value
        
        logger.debug(f"✅ Merge contact_info complete - Final keys: {list(merged.keys())}")
        return merged

    def _merge_timeline_info(self, new_data: Dict[str, Any], cumulative_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge timeline information with recency priority"""
        # Start with a copy of cumulative_data to preserve all existing keys
        merged = cumulative_data.copy() if cumulative_data else {}
        
        # CRITICAL: Empty strings MUST be treated as "no update" (per Rule 4)
        # Only update if new value is non-empty
        for key, new_value in new_data.items():
            if new_value and str(new_value).strip():
                merged[key] = new_value
                logger.debug(f"Updated timeline info {key}: {new_value}")
            # Empty strings are treated as "no update" - preserve existing value
        
        logger.debug(f"✅ Merge timeline_info complete - Final keys: {list(merged.keys())}")
        return merged

    def _merge_special_requirements(self, new_data: List[str], cumulative_data: List[str]) -> List[str]:
        """Merge special requirements, avoiding duplicates"""
        if not new_data:
            return cumulative_data
        
        merged = cumulative_data.copy()
        for req in new_data:
            if req and req.strip() and req not in merged:
                merged.append(req)
                logger.debug(f"Added special requirement: {req}")
        
        return merged

    def _merge_rate_info(self, new_data: Dict[str, Any], cumulative_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge rate information with recency priority"""
        # Start with a copy of cumulative_data to preserve all existing keys
        merged = cumulative_data.copy() if cumulative_data else {}
        
        # CRITICAL: Empty strings MUST be treated as "no update" (per Rule 4)
        # Only update if new value is non-empty
        for key, new_value in new_data.items():
            if new_value and str(new_value).strip():
                merged[key] = new_value
                logger.debug(f"Updated rate info {key}: {new_value}")
            # Empty strings are treated as "no update" - preserve existing value
        
        logger.debug(f"✅ Merge rate_info complete - Final keys: {list(merged.keys())}")
        return merged

    def _merge_additional_notes(self, new_data: str, cumulative_data: str) -> str:
        """Merge additional notes, avoiding duplicates and combining similar instructions"""
        if not new_data or not new_data.strip():
            return cumulative_data
        
        if not cumulative_data or not cumulative_data.strip():
            return new_data
        
        # Split into lines and remove duplicates
        existing_lines = set(line.strip() for line in cumulative_data.split('\n') if line.strip())
        new_lines = set(line.strip() for line in new_data.split('\n') if line.strip())
        
        # Combine all unique lines
        all_lines = existing_lines.union(new_lines)
        
        # Filter out common repetitive phrases
        filtered_lines = []
        for line in all_lines:
            # Skip if it's a common repetitive phrase
            if any(phrase in line.lower() for phrase in [
                "please provide the updated quote",
                "please provide these details",
                "please provide the correct details",
                "please provide it in your response"
            ]):
                continue
            filtered_lines.append(line)
        
        # If we have filtered lines, join them
        if filtered_lines:
            merged = '\n'.join(filtered_lines)
        else:
            # If all were filtered, keep the most recent one
            merged = new_data.strip()
        
        logger.debug(f"Merged additional notes: {len(filtered_lines)} unique lines")
        
        return merged

    def merge_with_recency_priority(self, new_data: Dict[str, Any], cumulative_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced merge function that handles mixed customer-bot information
        with priority given to recent information
        """
        if not cumulative_data:
            logger.info("No cumulative data found, using new data as base")
            return new_data.copy()
        
        logger.info(f"Merging new data with cumulative data for thread")
        logger.debug(f"New data keys: {list(new_data.keys())}")
        logger.debug(f"Cumulative data keys: {list(cumulative_data.keys())}")
        
        merged_data = {}
        
        # Merge each category using appropriate strategy
        for category, new_category_data in new_data.items():
            if category in self.merge_strategies:
                cumulative_category_data = cumulative_data.get(category, {})
                merged_data[category] = self.merge_strategies[category](
                    new_category_data, cumulative_category_data
                )
            else:
                # Default merge strategy for unknown categories
                if category in cumulative_data:
                    if isinstance(new_category_data, dict):
                        merged_data[category] = {**cumulative_data[category], **new_category_data}
                    elif isinstance(new_category_data, list):
                        merged_data[category] = cumulative_data[category] + new_category_data
                    else:
                        merged_data[category] = new_category_data
                else:
                    merged_data[category] = new_category_data
        
        # Add any categories from cumulative data that weren't in new data
        # CRITICAL: This ensures all categories from cumulative_data are preserved
        for category, cumulative_category_data in cumulative_data.items():
            if category not in merged_data:
                # Deep copy to avoid modifying the original
                if isinstance(cumulative_category_data, dict):
                    merged_data[category] = cumulative_category_data.copy()
                elif isinstance(cumulative_category_data, list):
                    merged_data[category] = cumulative_category_data.copy()
                else:
                    merged_data[category] = cumulative_category_data
                logger.debug(f"Preserved category from cumulative data: {category}")
        
        # Verify all keys are preserved
        cumulative_keys = set(cumulative_data.keys())
        merged_keys = set(merged_data.keys())
        missing_keys = cumulative_keys - merged_keys
        if missing_keys:
            logger.warning(f"⚠️ Missing keys in merged data: {missing_keys}")
        else:
            logger.debug(f"✅ All cumulative keys preserved: {list(cumulative_keys)}")
        
        logger.info(f"Merge completed. Final data keys: {list(merged_data.keys())}")
        return merged_data

    def load_thread(self, thread_id: str) -> Optional[ThreadData]:
        """Load thread data from storage"""
        file_path = os.path.join(self.storage_dir, f"{thread_id}.json")
        
        if not os.path.exists(file_path):
            logger.info(f"Thread {thread_id} not found")
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Convert back to dataclass
            email_chain = [EmailEntry(**email) for email in data.get('email_chain', [])]
            thread_data = ThreadData(
                thread_id=data['thread_id'],
                email_chain=email_chain,
                cumulative_extraction=data.get('cumulative_extraction', {}),
                last_updated=data.get('last_updated', ''),
                customer_context=data.get('customer_context', {}),
                forwarder_context=data.get('forwarder_context', {}),
                conversation_state=data.get('conversation_state', 'new_thread'),
                total_emails=data.get('total_emails', 0)
            )
            
            logger.info(f"Loaded thread {thread_id} with {len(email_chain)} emails")
            return thread_data
            
        except Exception as e:
            logger.error(f"Error loading thread {thread_id}: {e}")
            return None

    def save_thread(self, thread_data: ThreadData) -> bool:
        """Save thread data to storage"""
        try:
            file_path = os.path.join(self.storage_dir, f"{thread_data.thread_id}.json")
            
            # Convert dataclass to dict for JSON serialization
            data = asdict(thread_data)
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Saved thread {thread_data.thread_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving thread {thread_data.thread_id}: {e}")
            return False

    def create_new_thread(self, thread_id: str, initial_email: EmailEntry) -> ThreadData:
        """Create a new thread with initial email"""
        thread_data = ThreadData(
            thread_id=thread_id,
            email_chain=[initial_email],
            cumulative_extraction={},
            last_updated=datetime.now().isoformat(),
            customer_context={},
            forwarder_context={},
            conversation_state="new_thread",
            total_emails=1
        )
        
        self.save_thread(thread_data)
        logger.info(f"Created new thread {thread_id}")
        return thread_data

    def add_email_to_thread(self, thread_id: str, email_entry: EmailEntry) -> ThreadData:
        """Add email to existing thread and update cumulative extraction"""
        thread_data = self.load_thread(thread_id)
        
        if not thread_data:
            logger.info(f"Thread {thread_id} not found, creating new thread")
            return self.create_new_thread(thread_id, email_entry)
        
        # Add email to chain
        thread_data.email_chain.append(email_entry)
        thread_data.total_emails = len(thread_data.email_chain)
        thread_data.last_updated = datetime.now().isoformat()
        
        # Update cumulative extraction if email has extracted data
        if email_entry.extracted_data:
            logger.info(f"Updating cumulative extraction for thread {thread_id}")
            thread_data.cumulative_extraction = self.merge_with_recency_priority(
                email_entry.extracted_data, 
                thread_data.cumulative_extraction
            )
        
        # Update conversation state based on email direction and response type
        if email_entry.direction == "inbound":
            if thread_data.conversation_state == "new_thread":
                thread_data.conversation_state = "customer_initial_request"
            elif email_entry.response_type:
                thread_data.conversation_state = f"customer_{email_entry.response_type}"
        elif email_entry.direction == "outbound":
            if email_entry.response_type:
                thread_data.conversation_state = f"bot_{email_entry.response_type}"
        
        self.save_thread(thread_data)
        logger.info(f"Added email to thread {thread_id}. Total emails: {thread_data.total_emails}")
        
        return thread_data

    def update_cumulative_extraction(self, thread_id: str, new_extraction: Dict[str, Any]) -> bool:
        """Update cumulative extraction for a thread"""
        thread_data = self.load_thread(thread_id)
        
        if not thread_data:
            logger.warning(f"Thread {thread_id} not found for extraction update")
            return False
        
        thread_data.cumulative_extraction = self.merge_with_recency_priority(
            new_extraction, 
            thread_data.cumulative_extraction
        )
        thread_data.last_updated = datetime.now().isoformat()
        
        success = self.save_thread(thread_data)
        if success:
            logger.info(f"Updated cumulative extraction for thread {thread_id}")
        return success

    def get_thread_summary(self, thread_id: str) -> Dict[str, Any]:
        """Get summary of thread"""
        thread_data = self.load_thread(thread_id)
        
        if not thread_data:
            return {"error": "Thread not found"}
        
        return {
            "thread_id": thread_data.thread_id,
            "total_emails": thread_data.total_emails,
            "conversation_state": thread_data.conversation_state,
            "last_updated": thread_data.last_updated,
            "customer_context": thread_data.customer_context,
            "forwarder_context": thread_data.forwarder_context,
            "extraction_summary": {
                "categories": list(thread_data.cumulative_extraction.keys()),
                "total_fields": sum(len(data) if isinstance(data, dict) else 1 
                                  for data in thread_data.cumulative_extraction.values())
            }
        }

    def get_recent_emails(self, thread_id: str, count: int = 5) -> List[EmailEntry]:
        """Get recent emails from thread"""
        thread_data = self.load_thread(thread_id)
        
        if not thread_data:
            return []
        
        return thread_data.email_chain[-count:]

    def get_cumulative_extraction(self, thread_id: str) -> Dict[str, Any]:
        """Get cumulative extraction for thread"""
        thread_data = self.load_thread(thread_id)
        
        if not thread_data:
            return {}
        
        return thread_data.cumulative_extraction

    def update_context(self, thread_id: str, context_type: str, context_data: Dict[str, Any]) -> bool:
        """Update customer or forwarder context"""
        thread_data = self.load_thread(thread_id)
        
        if not thread_data:
            return False
        
        if context_type == "customer":
            thread_data.customer_context.update(context_data)
        elif context_type == "forwarder":
            thread_data.forwarder_context.update(context_data)
        
        thread_data.last_updated = datetime.now().isoformat()
        return self.save_thread(thread_data)

    def get_mixed_conversation_summary(self, thread_id: str) -> Dict[str, Any]:
        """Get summary of mixed customer-bot conversation"""
        thread_data = self.load_thread(thread_id)
        
        if not thread_data:
            return {"error": "Thread not found"}
        
        # Analyze conversation flow
        customer_emails = [e for e in thread_data.email_chain if e.direction == "inbound"]
        bot_emails = [e for e in thread_data.email_chain if e.direction == "outbound"]
        
        # Get latest information from both customer and bot
        latest_customer_data = {}
        latest_bot_data = {}
        
        for email in reversed(customer_emails):
            if email.extracted_data and not latest_customer_data:
                latest_customer_data = email.extracted_data
        
        for email in reversed(bot_emails):
            if email.bot_response and not latest_bot_data:
                latest_bot_data = email.bot_response
        
        return {
            "thread_id": thread_data.thread_id,
            "conversation_flow": {
                "total_emails": thread_data.total_emails,
                "customer_emails": len(customer_emails),
                "bot_emails": len(bot_emails),
                "conversation_state": thread_data.conversation_state
            },
            "latest_information": {
                "customer_data": latest_customer_data,
                "bot_data": latest_bot_data,
                "cumulative_extraction": thread_data.cumulative_extraction
            },
            "priority_analysis": {
                "recent_customer_info": bool(latest_customer_data),
                "recent_bot_info": bool(latest_bot_data),
                "mixed_conversation": len(customer_emails) > 0 and len(bot_emails) > 0
            }
        } 