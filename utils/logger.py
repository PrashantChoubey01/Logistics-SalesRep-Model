"""Logging utilities for agents"""

import logging
import sys
from datetime import datetime
from typing import Optional

def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Get configured logger"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, level.upper()))
    
    return logger

def log_agent_action(agent_name: str, action: str, status: str, details: Optional[str] = None):
    """Log agent actions"""
    logger = get_logger(agent_name)
    
    message = f"Action: {action} | Status: {status}"
    if details:
        message += f" | Details: {details}"
    
    if status.lower() == "success":
        logger.info(message)
    elif status.lower() == "error":
        logger.error(message)
    else:
        logger.warning(message)

# Quick test
def test_logger():
    print("=== Testing Logger ===")
    
    # Test logger creation
    logger = get_logger("test_agent")
    print("✓ Logger created")
    
    # Test logging
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    
    # Test agent action logging
    log_agent_action("test_agent", "classify_email", "success", "Email classified as logistics_request")
    print("✓ Agent action logged")

if __name__ == "__main__":
    test_logger()
