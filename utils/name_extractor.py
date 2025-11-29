#!/usr/bin/env python3
"""
Name Extractor Utility
======================

Extracts first name from email addresses or full names.
Per Rule IV: Greeting should be "Dear <FirstName>," not "Dear Valued Customer,"
"""

import re
from typing import Optional


def extract_first_name(email: str, full_name: Optional[str] = None) -> str:
    """
    Extract first name from email address or full name.
    
    Examples:
        "john.doe@techcorp.com" -> "John"
        "jane.smith@example.com" -> "Jane"
        "John Doe" -> "John"
        "jane@example.com" -> "Jane"
        "unknown@example.com" -> "Valued Customer" (fallback)
    
    Args:
        email: Email address (e.g., "john.doe@techcorp.com")
        full_name: Optional full name (e.g., "John Doe")
    
    Returns:
        First name with proper capitalization, or "Valued Customer" if cannot extract
    """
    # Try full name first if provided
    if full_name and full_name.strip():
        name_parts = full_name.strip().split()
        if name_parts:
            first_name = name_parts[0]
            # Capitalize properly (e.g., "john" -> "John", "JOHN" -> "John")
            return first_name.capitalize()
    
    # Extract from email address
    if not email or not isinstance(email, str):
        return "Valued Customer"
    
    # Remove email domain
    local_part = email.split('@')[0] if '@' in email else email
    
    # Try to extract first name from common patterns
    # Pattern 1: firstname.lastname (e.g., "john.doe" -> "john")
    if '.' in local_part:
        first_part = local_part.split('.')[0]
        if first_part and len(first_part) > 1:
            return first_part.capitalize()
    
    # Pattern 2: firstnamelastname (e.g., "johndoe" -> "john" if we can detect)
    # This is harder, so we'll just use the whole local part if it's reasonable
    if local_part and len(local_part) > 1:
        # If it's all lowercase and reasonable length, capitalize it
        if local_part.islower() and len(local_part) <= 20:
            return local_part.capitalize()
        # If it's already capitalized, use as is
        elif local_part[0].isupper():
            return local_part
        else:
            return local_part.capitalize()
    
    # Fallback
    return "Valued Customer"


def extract_name_from_email_data(email_data: dict) -> str:
    """
    Extract first name from email data dictionary.
    
    Checks in order:
    1. sender_name field
    2. from_name field
    3. sender email address
    4. from_email address
    
    Args:
        email_data: Dictionary containing email information
    
    Returns:
        First name with proper capitalization, or "Valued Customer" if cannot extract
    """
    # Try sender_name first
    sender_name = email_data.get("sender_name") or email_data.get("from_name")
    if sender_name:
        return extract_first_name("", sender_name)
    
    # Try sender email
    sender_email = email_data.get("sender") or email_data.get("from_email")
    if sender_email:
        return extract_first_name(sender_email)
    
    # Fallback
    return "Valued Customer"

