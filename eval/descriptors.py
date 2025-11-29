#!/usr/bin/env python3
"""
Evaluation Descriptors
======================

Reusable scorers for email quality evaluation using Evidently.
"""

from typing import Dict, Any, List
import re

try:
    from evidently.metrics import TextQuality
    from evidently.metrics.text_quality import TextQualityMetric
    EVIDENTLY_AVAILABLE = True
except ImportError:
    EVIDENTLY_AVAILABLE = False
    print("⚠️  Evidently not installed. Install with: pip install evidently evidently[llm]")

def grammar_score(text: str) -> float:
    """Calculate grammar score (0-100)"""
    if not text:
        return 0.0
    
    # Simple heuristic: check for common grammar issues
    issues = 0
    total_words = len(text.split())
    
    if total_words == 0:
        return 0.0
    
    # Check for double spaces
    issues += text.count('  ')
    
    # Check for missing periods at end
    if text.strip() and not text.strip().endswith(('.', '!', '?')):
        issues += 1
    
    # Check for common typos (simplified)
    common_typos = ['teh', 'adn', 'taht', 'recieve']
    for typo in common_typos:
        issues += text.lower().count(typo)
    
    # Normalize to 0-100 scale (fewer issues = higher score)
    score = max(0, 100 - (issues / total_words * 100))
    return min(100, score)

def word_count(text: str) -> int:
    """Count words in text"""
    if not text:
        return 0
    return len(text.split())

def mobile_friendly(text: str, max_words: int = 180) -> bool:
    """Check if text is mobile-friendly (word count <= max_words)"""
    return word_count(text) <= max_words

def hallucination_check(text: str, thread_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Check for hallucination (invented ports, rates, dates).
    This is a simplified version - in production, use LLM-as-Judge.
    """
    if not text:
        return {"has_hallucination": False, "confidence": 0.0, "issues": []}
    
    issues = []
    
    # Extract mentioned ports from text
    port_pattern = r'\b([A-Z]{2,5})\b'  # Simple port code pattern
    mentioned_ports = re.findall(port_pattern, text)
    
    # Extract mentioned rates
    rate_pattern = r'\$[\d,]+|\d+\.\d+\s*(USD|EUR|GBP)'
    mentioned_rates = re.findall(rate_pattern, text)
    
    # Check against thread context if available
    if thread_context:
        # Get valid ports from thread
        valid_ports = thread_context.get("valid_ports", [])
        valid_rates = thread_context.get("valid_rates", [])
        
        # Check for invented ports
        for port in mentioned_ports:
            if port not in valid_ports and len(port) >= 3:
                issues.append(f"Potentially invented port code: {port}")
        
        # Check for invented rates (if rates weren't in thread)
        if mentioned_rates and not valid_rates:
            issues.append("Rates mentioned but not in thread context")
    
    has_hallucination = len(issues) > 0
    confidence = 0.8 if has_hallucination else 0.9
    
    return {
        "has_hallucination": has_hallucination,
        "confidence": confidence,
        "issues": issues
    }

class EmailQualityDescriptor:
    """Descriptor for email quality evaluation"""
    
    def __init__(self):
        self.name = "email_quality"
    
    def evaluate(self, email_body: str, thread_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Evaluate email quality"""
        return {
            "grammar_score": grammar_score(email_body),
            "word_count": word_count(email_body),
            "mobile_friendly": mobile_friendly(email_body),
            "hallucination": hallucination_check(email_body, thread_context)
        }

# Export descriptors
grammar = EmailQualityDescriptor()
mobile_friendly_descriptor = EmailQualityDescriptor()
hallucination_descriptor = EmailQualityDescriptor()

# For Evidently integration (if available)
if EVIDENTLY_AVAILABLE:
    class GrammarMetric:
        """Grammar quality metric for Evidently"""
        def __init__(self):
            self.metric = TextQualityMetric(column_name="email_body")
        
        def calculate(self, data):
            return self.metric.calculate(data)
    
    grammar_metric = GrammarMetric()

