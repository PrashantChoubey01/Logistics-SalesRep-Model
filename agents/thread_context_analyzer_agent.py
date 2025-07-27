#!/usr/bin/env python3
"""
Thread Context Analyzer Agent - Specialized LLM Approach

This agent uses a dedicated LLM specifically for analyzing email threads and conversation context.
Separate from classification to prevent confusion and improve accuracy.

Key Features:
1. Dedicated thread analysis LLM
2. Conversation progression tracking
3. Vague response pattern detection
4. Thread state management
5. Context-aware decision making
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent


class ThreadContextAnalyzerAgent(BaseAgent):
    """
    Thread Context Analyzer Agent - Specialized LLM Design
    
    This agent uses a dedicated LLM specifically for thread analysis and conversation context,
    separate from other agents to prevent confusion and improve accuracy.
    
    Design Philosophy:
    - Dedicated LLM for thread analysis only
    - Specialized prompts for conversation understanding
    - Context-aware decision making
    - Vague response pattern detection
    - Thread state progression tracking
    """

    def __init__(self):
        super().__init__("ThreadContextAnalyzerAgent")
        
        # Use a different model for thread analysis (more focused on conversation)
        self.thread_analysis_model = "databricks-meta-llama-3-3-70b-instruct"
        
        # Thread context states
        self.thread_states = {
            "new_thread": "Starting a new conversation",
            "first_response": "First response in thread",
            "clarification": "Clarification or additional information",
            "ongoing": "Ongoing conversation with multiple exchanges",
            "multiple_vague": "Multiple vague responses detected",
            "escalation_needed": "Thread requires escalation",
            "resolved": "Thread has been resolved"
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core thread analysis logic using specialized thread analysis LLM.
        
        Args:
            input_data: Dictionary containing:
                - email_data: Current email content and metadata
                - thread_history: Complete thread history
                - previous_classifications: Previous email classifications
                - customer_context: Customer information
                - forwarder_context: Forwarder information
        
        Returns:
            Dictionary containing thread analysis results
        """
        print(f"🧵 THREAD_ANALYZER: Starting specialized LLM thread analysis...")
        
        # Extract input data
        email_data = input_data.get("email_data", {})
        thread_history = input_data.get("thread_history", [])
        previous_classifications = input_data.get("previous_classifications", [])
        customer_context = input_data.get("customer_context", {})
        forwarder_context = input_data.get("forwarder_context", {})
        
        # Get current email info
        email_text = email_data.get("email_text", "")
        subject = email_data.get("subject", "")
        sender_email = email_data.get("sender", "")
        thread_id = email_data.get("thread_id", "")
        
        print(f"📧 Current Email: {subject[:50]}...")
        print(f"🧵 Thread ID: {thread_id}")
        print(f"📊 Thread Length: {len(thread_history)} previous emails")
        
        # Use specialized thread analysis LLM
        thread_analysis_result = self._specialized_thread_analysis(
            email_text, subject, sender_email, thread_history, 
            previous_classifications, customer_context, forwarder_context
        )
        
        print(f"✅ THREAD_ANALYZER: Specialized LLM analysis complete")
        print(f"   Thread State: {thread_analysis_result['thread_state']}")
        print(f"   Conversation Stage: {thread_analysis_result['conversation_stage']}")
        print(f"   Vague Pattern: {thread_analysis_result['vague_pattern_detected']}")
        
        return thread_analysis_result

    def _specialized_thread_analysis(self, email_text: str, subject: str, sender_email: str,
                                   thread_history: List, previous_classifications: List,
                                   customer_context: Dict, forwarder_context: Dict) -> Dict[str, Any]:
        """
        Use specialized thread analysis LLM for conversation context analysis.
        """
        if not self.client:
            return self._fallback_thread_analysis(thread_history, previous_classifications)
        
        # Prepare thread context for analysis LLM
        thread_summary = self._prepare_detailed_thread_summary(thread_history, previous_classifications)
        conversation_pattern = self._analyze_conversation_pattern(thread_history, previous_classifications)
        vague_response_tracking = self._track_vague_responses(thread_history, previous_classifications)
        
        # Create specialized thread analysis prompt
        prompt = self._create_thread_analysis_prompt(
            email_text, subject, sender_email, thread_history, previous_classifications,
            customer_context, forwarder_context
        )
        
        # Define specialized function schema for thread analysis
        function_schema = {
            "name": "analyze_thread_context",
            "description": "Analyze email thread context and conversation progression",
            "parameters": {
                "type": "object",
                "properties": {
                    "thread_state": {
                        "type": "string",
                        "enum": list(self.thread_states.keys()),
                        "description": "Current state of the email thread"
                    },
                    "conversation_stage": {
                        "type": "string",
                        "enum": ["initial_request", "clarification", "confirmation", "ongoing", "escalation", "resolution"],
                        "description": "Stage of the conversation"
                    },
                    "vague_pattern_detected": {
                        "type": "boolean",
                        "description": "Whether a pattern of vague responses is detected"
                    },
                    "vague_response_count": {
                        "type": "integer",
                        "minimum": 0,
                        "description": "Number of vague responses in thread"
                    },
                    "escalation_needed": {
                        "type": "boolean",
                        "description": "Whether thread requires escalation"
                    },
                    "escalation_reason": {
                        "type": "string",
                        "description": "Reason for escalation if needed"
                    },
                    "next_action": {
                        "type": "string",
                        "enum": ["continue_conversation", "request_clarification", "escalate", "resolve", "wait_for_response"],
                        "description": "Recommended next action"
                    },
                    "thread_priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Priority level of the thread"
                    },
                    "data_override_required": {
                        "type": "boolean",
                        "description": "Whether previous data should be overridden"
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Confidence in thread analysis"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of the thread analysis"
                    }
                },
                "required": ["thread_state", "conversation_stage", "vague_pattern_detected", "escalation_needed", "next_action", "thread_priority", "confidence", "reasoning"]
            }
        }
        
        # Get specialized LLM thread analysis
        llm_result = self._generate_thread_analysis_response(prompt, function_schema)
        
        if "error" in llm_result:
            print(f"⚠️ Specialized LLM thread analysis failed, using fallback: {llm_result['error']}")
            return self._fallback_thread_analysis(thread_history, previous_classifications)
        
        # Enhance result with additional context
        enhanced_result = self._enhance_thread_analysis_result(
            llm_result, thread_history, previous_classifications, email_text, subject
        )
        
        return enhanced_result

    def _create_thread_analysis_prompt(self, email_text: str, subject: str, sender_email: str,
                                     thread_history: List[Dict], previous_classifications: List[Dict],
                                     customer_context: Dict, forwarder_context: Dict) -> str:
        """Create specialized prompt for thread analysis LLM"""
        
        # Build thread context
        thread_context = self._build_thread_context(thread_history, previous_classifications)
        
        prompt = f"""
# THREAD CONTEXT ANALYSIS

## CURRENT EMAIL:
**Subject:** {subject}
**Sender:** {sender_email}
**Content:** {email_text}

## THREAD HISTORY:
{thread_context}

## CUSTOMER CONTEXT:
{customer_context}

## FORWARDER CONTEXT:
{forwarder_context}

## THREAD ANALYSIS TASK:

Analyze the email thread to determine:

### 1. THREAD STATE:
- **new_thread**: First email in conversation
- **follow_up**: Continuation of existing conversation
- **update_request**: Customer updating previous information
- **clarification**: Seeking clarification on previous response
- **confirmation**: Confirming previous details
- **escalation**: Escalating to human intervention

### 2. CONVERSATION STAGE:
- **initial_request**: First shipping inquiry
- **rate_negotiation**: Discussing rates and terms
- **booking_confirmation**: Confirming booking details
- **documentation**: Handling documentation requirements
- **tracking**: Tracking shipment status
- **issue_resolution**: Resolving problems or concerns

### 3. VAGUE PATTERN DETECTION:
- Check if customer responses are unclear or incomplete
- Identify if multiple clarification attempts have been made
- Detect if conversation is going in circles

### 4. ESCALATION ASSESSMENT:
- Determine if human intervention is needed
- Assess urgency and complexity
- Consider customer priority and history

### 5. NEXT ACTION RECOMMENDATION:
- Suggest appropriate next steps
- Identify required information
- Recommend response type

## ANALYSIS GUIDELINES:
- Consider the complete conversation flow
- Look for patterns in customer behavior
- Assess information completeness
- Evaluate response effectiveness
- Consider business context and urgency

Please provide a comprehensive thread analysis following these guidelines.
"""
        return prompt

    def _prepare_detailed_thread_summary(self, thread_history: List, previous_classifications: List) -> str:
        """
        Prepare detailed thread summary for thread analysis LLM.
        """
        if not thread_history:
            return "This is a new email thread with no previous history."
        
        summary_parts = [f"Thread contains {len(thread_history)} previous emails:"]
        
        for i, (email, classification) in enumerate(zip(thread_history, previous_classifications), 1):
            email_type = classification.get("email_type", "unknown")
            subject = email.get("subject", "No subject")
            sender = email.get("sender", "Unknown")
            is_vague = classification.get("is_vague", False)
            
            summary_parts.append(f"  {i}. {email_type} from {sender}: {subject}")
            if is_vague:
                summary_parts.append(f"     ⚠️ Vague response detected")
        
        return "\n".join(summary_parts)

    def _analyze_conversation_pattern(self, thread_history: List, previous_classifications: List) -> str:
        """
        Analyze conversation pattern for thread analysis LLM.
        """
        if not thread_history:
            return "New conversation pattern."
        
        pattern_parts = ["Conversation Pattern Analysis:"]
        
        # Count different types of emails
        email_types = [classification.get("email_type", "unknown") for classification in previous_classifications]
        type_counts = {}
        for email_type in email_types:
            type_counts[email_type] = type_counts.get(email_type, 0) + 1
        
        pattern_parts.append(f"  Email type distribution: {type_counts}")
        
        # Check for patterns
        if len(thread_history) >= 3:
            pattern_parts.append("  Long conversation detected")
        
        if any("vague" in email_type for email_type in email_types):
            pattern_parts.append("  Vague responses present in conversation")
        
        if any("clarification" in email_type for email_type in email_types):
            pattern_parts.append("  Clarification requests present")
        
        return "\n".join(pattern_parts)

    def _track_vague_responses(self, thread_history: List, previous_classifications: List) -> str:
        """
        Track vague responses for thread analysis LLM.
        """
        if not thread_history:
            return "No vague responses to track."
        
        vague_responses = []
        for i, classification in enumerate(previous_classifications, 1):
            if classification.get("is_vague", False):
                vague_responses.append(i)
        
        if not vague_responses:
            return "No vague responses detected in thread."
        
        tracking_parts = [f"Vague Response Tracking:"]
        tracking_parts.append(f"  Total vague responses: {len(vague_responses)}")
        tracking_parts.append(f"  Vague response positions: {vague_responses}")
        
        if len(vague_responses) >= 2:
            tracking_parts.append("  ⚠️ Multiple vague responses detected - escalation may be needed")
        
        return "\n".join(tracking_parts)

    def _build_thread_context(self, thread_history: List[Dict], previous_classifications: List[Dict]) -> str:
        """Build comprehensive thread context for analysis"""
        if not thread_history:
            return "No previous emails in thread."
        
        context_parts = []
        context_parts.append(f"Thread contains {len(thread_history)} previous emails.")
        
        # Analyze thread progression
        for i, email_entry in enumerate(thread_history, 1):
            email_data = email_entry.get("email", {})
            step_results = email_entry.get("step_results", {})
            
            context_parts.append(f"\n--- Email {i} ---")
            context_parts.append(f"Subject: {email_data.get('subject', 'No subject')}")
            context_parts.append(f"Sender: {email_data.get('sender', 'Unknown')}")
            context_parts.append(f"Timestamp: {email_entry.get('timestamp', 'Unknown')}")
            
            # Add classification info
            classification = step_results.get("classification", {})
            if classification and "error" not in classification:
                context_parts.append(f"Type: {classification.get('email_type', 'unknown')}")
                context_parts.append(f"Sender Type: {classification.get('sender_type', 'unknown')}")
            
            # Add extraction info
            extraction = step_results.get("extraction", {})
            if extraction and "error" not in extraction:
                extracted_data = extraction.get("extracted_data", {})
                shipment_details = extracted_data.get("shipment_details", {})
                if shipment_details:
                    context_parts.append("Extracted Info:")
                    for key, value in shipment_details.items():
                        if value:
                            context_parts.append(f"  {key}: {value}")
            
            # Add response info
            response = step_results.get("response", {})
            if response and "error" not in response:
                context_parts.append(f"Response Type: {response.get('response_type', 'unknown')}")
        
        # Add conversation pattern analysis
        if len(thread_history) > 1:
            context_parts.append(f"\n--- Conversation Pattern ---")
            context_parts.append(f"Total exchanges: {len(thread_history)}")
            
            # Check for vague responses
            vague_count = 0
            for classification in previous_classifications:
                if classification.get("email_type") in ["clarification_request", "vague_response"]:
                    vague_count += 1
            
            if vague_count > 0:
                context_parts.append(f"Vague responses detected: {vague_count}")
            
            # Check for escalation patterns
            escalation_count = 0
            for email_entry in thread_history:
                step_results = email_entry.get("step_results", {})
                escalation = step_results.get("escalation", {})
                if escalation and escalation.get("escalation_needed", False):
                    escalation_count += 1
            
            if escalation_count > 0:
                context_parts.append(f"Previous escalations: {escalation_count}")
        
        return "\n".join(context_parts)

    def _enhance_thread_analysis_result(self, llm_result: Dict, thread_history: List,
                                      previous_classifications: List, email_text: str, 
                                      subject: str) -> Dict[str, Any]:
        """
        Enhance LLM result with additional thread context and metadata.
        """
        # Add metadata
        enhanced_result = {
            **llm_result,
            "thread_metadata": {
                "thread_length": len(thread_history),
                "current_email_subject": subject,
                "current_email_word_count": len(email_text.split()),
                "processed_at": datetime.utcnow().isoformat()
            },
            "conversation_analysis": {
                "email_type_distribution": self._get_email_type_distribution(previous_classifications),
                "vague_response_positions": self._get_vague_response_positions(previous_classifications),
                "conversation_progression": self._analyze_conversation_progression(thread_history, previous_classifications)
            },
            "analysis_details": {
                "reasoning": llm_result.get("reasoning", ""),
                "analysis_method": "specialized_thread_llm",
                "confidence_factors": self._extract_thread_confidence_factors(llm_result, thread_history)
            }
        }
        
        # Add escalation details if needed
        if llm_result.get("escalation_needed", False):
            enhanced_result["escalation_details"] = {
                "reason": llm_result.get("escalation_reason", "Unknown"),
                "thread_priority": llm_result.get("thread_priority", "medium"),
                "recommended_action": self._get_thread_escalation_action(llm_result)
            }
        
        return enhanced_result

    def _get_email_type_distribution(self, previous_classifications: List) -> Dict[str, int]:
        """
        Get distribution of email types in thread.
        """
        distribution = {}
        for classification in previous_classifications:
            email_type = classification.get("email_type", "unknown")
            distribution[email_type] = distribution.get(email_type, 0) + 1
        return distribution

    def _get_vague_response_positions(self, previous_classifications: List) -> List[int]:
        """
        Get positions of vague responses in thread.
        """
        positions = []
        for i, classification in enumerate(previous_classifications, 1):
            if classification.get("is_vague", False):
                positions.append(i)
        return positions

    def _analyze_conversation_progression(self, thread_history: List, previous_classifications: List) -> str:
        """
        Analyze conversation progression.
        """
        if not thread_history:
            return "New conversation"
        
        progression_parts = []
        
        # Check for conversation flow
        if len(thread_history) == 1:
            progression_parts.append("Initial exchange")
        elif len(thread_history) == 2:
            progression_parts.append("First response received")
        elif len(thread_history) >= 3:
            progression_parts.append("Ongoing conversation")
        
        # Check for stuck conversations
        vague_count = sum(1 for classification in previous_classifications if classification.get("is_vague", False))
        if vague_count >= 2:
            progression_parts.append("Conversation may be stuck due to vague responses")
        
        return "; ".join(progression_parts)

    def _extract_thread_confidence_factors(self, llm_result: Dict, thread_history: List) -> List[str]:
        """
        Extract factors that influenced thread analysis confidence.
        """
        factors = []
        
        if llm_result.get("confidence", 0) >= 0.8:
            factors.append("High confidence - clear conversation pattern")
        elif llm_result.get("confidence", 0) >= 0.6:
            factors.append("Medium confidence - some uncertainty in thread analysis")
        else:
            factors.append("Low confidence - unclear conversation pattern")
        
        if llm_result.get("vague_pattern_detected", False):
            factors.append("Vague response pattern detected")
        
        if len(thread_history) >= 5:
            factors.append("Long conversation thread")
        elif len(thread_history) <= 1:
            factors.append("Short conversation thread")
        
        return factors

    def _get_thread_escalation_action(self, llm_result: Dict) -> str:
        """
        Determine recommended action for thread escalation.
        """
        if llm_result.get("thread_priority") == "urgent":
            return "Immediate human review required"
        elif llm_result.get("vague_pattern_detected", False):
            return "Human review for vague response pattern"
        elif llm_result.get("thread_state") == "multiple_vague":
            return "Escalate due to multiple vague responses"
        else:
            return "Standard thread escalation process"

    def _fallback_thread_analysis(self, thread_history: List, previous_classifications: List) -> Dict[str, Any]:
        """
        Fallback thread analysis when specialized LLM is not available.
        """
        print("⚠️ Using fallback thread analysis (Specialized LLM not available)")
        
        # Simple fallback logic
        thread_length = len(thread_history)
        vague_count = sum(1 for classification in previous_classifications if classification.get("is_vague", False))
        
        # Determine thread state
        if thread_length == 0:
            thread_state = "new_thread"
        elif thread_length == 1:
            thread_state = "first_response"
        elif vague_count >= 2:
            thread_state = "multiple_vague"
        else:
            thread_state = "ongoing"
        
        # Determine escalation need
        escalation_needed = vague_count >= 3 or thread_length >= 10
        
        return {
            "thread_state": thread_state,
            "conversation_stage": "ongoing" if thread_length > 0 else "initial_request",
            "vague_pattern_detected": vague_count >= 2,
            "vague_response_count": vague_count,
            "escalation_needed": escalation_needed,
            "escalation_reason": "Fallback analysis - multiple vague responses" if vague_count >= 3 else "Fallback analysis - long thread",
            "next_action": "escalate" if escalation_needed else "continue_conversation",
            "thread_priority": "high" if escalation_needed else "medium",
            "data_override_required": False,
            "confidence": 0.5,  # Low confidence for fallback
            "reasoning": "Fallback thread analysis due to specialized LLM unavailability",
            "analysis_method": "fallback"
        }

    def _generate_thread_analysis_response(self, prompt: str, function_schema: Dict) -> Dict[str, Any]:
        """
        Generate response using specialized thread analysis LLM.
        """
        return self._make_llm_call(
            prompt=prompt,
            function_schema=function_schema,
            model_name=self.thread_analysis_model,
            temperature=0.1,
            max_tokens=800
        )


# =====================================================
#                 🧪 Test Functions
# =====================================================

def test_thread_analyzer():
    """Test the Specialized LLM-based Thread Context Analyzer Agent"""
    print("🧪 Testing Specialized LLM-based Thread Context Analyzer Agent")
    print("=" * 60)
    
    # Initialize agent
    analyzer = ThreadContextAnalyzerAgent()
    analyzer.load_context()
    
    # Test scenarios
    test_cases = [
        {
            "name": "New Thread",
            "email_data": {
                "email_text": "Hi, I need shipping rates from Shanghai to Los Angeles.",
                "subject": "Shipping Quote Request",
                "sender": "customer@company.com",
                "thread_id": "thread_123"
            },
            "thread_history": [],
            "previous_classifications": []
        },
        {
            "name": "Thread with Vague Responses",
            "email_data": {
                "email_text": "Maybe something like that. Not sure about the details.",
                "subject": "Re: Shipping Quote Request",
                "sender": "customer@company.com",
                "thread_id": "thread_123"
            },
            "thread_history": [
                {"subject": "Shipping Quote Request", "sender": "customer@company.com"},
                {"subject": "Re: Shipping Quote Request", "sender": "bot@company.com"}
            ],
            "previous_classifications": [
                {"email_type": "customer_quote_request", "is_vague": False},
                {"email_type": "customer_vague_response", "is_vague": True}
            ]
        },
        {
            "name": "Long Thread with Multiple Vague Responses",
            "email_data": {
                "email_text": "I think so, maybe. Not really sure.",
                "subject": "Re: Re: Re: Shipping Quote Request",
                "sender": "customer@company.com",
                "thread_id": "thread_456"
            },
            "thread_history": [
                {"subject": "Shipping Quote Request", "sender": "customer@company.com"},
                {"subject": "Re: Shipping Quote Request", "sender": "bot@company.com"},
                {"subject": "Re: Re: Shipping Quote Request", "sender": "customer@company.com"},
                {"subject": "Re: Re: Re: Shipping Quote Request", "sender": "bot@company.com"}
            ],
            "previous_classifications": [
                {"email_type": "customer_quote_request", "is_vague": False},
                {"email_type": "customer_vague_response", "is_vague": True},
                {"email_type": "customer_vague_response", "is_vague": True},
                {"email_type": "customer_vague_response", "is_vague": True}
            ]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧵 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        result = analyzer.process(test_case)
        
        print(f"✅ Thread State: {result.get('thread_state', 'unknown')}")
        print(f"✅ Conversation Stage: {result.get('conversation_stage', 'unknown')}")
        print(f"✅ Vague Pattern: {result.get('vague_pattern_detected', False)}")
        print(f"✅ Vague Count: {result.get('vague_response_count', 0)}")
        print(f"✅ Escalation: {result.get('escalation_needed', False)}")
        print(f"✅ Next Action: {result.get('next_action', 'unknown')}")
        print(f"✅ Thread Priority: {result.get('thread_priority', 'unknown')}")
        print(f"✅ Confidence: {result.get('confidence', 0):.2f}")
        
        if result.get('escalation_reason'):
            print(f"🚨 Escalation Reason: {result['escalation_reason']}")
        
        if result.get('reasoning'):
            print(f"🧠 Reasoning: {result['reasoning'][:100]}...")
    
    print(f"\n🎉 All tests completed!")


if __name__ == "__main__":
    test_thread_analyzer() 