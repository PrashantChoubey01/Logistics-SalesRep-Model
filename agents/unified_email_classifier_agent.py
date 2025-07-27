#!/usr/bin/env python3
"""
Unified Email Classifier Agent - Specialized LLM Approach

This agent uses a dedicated LLM specifically for email classification tasks.
Separate from other agents to prevent confusion and improve accuracy.

Key Features:
1. Dedicated classification LLM
2. Specialized prompts for email understanding
3. Context-aware classification
4. Confidence scoring
5. Vague content detection
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent


class UnifiedEmailClassifierAgent(BaseAgent):
    """
    Unified Email Classifier Agent - Specialized LLM Design
    
    This agent uses a dedicated LLM specifically for email classification,
    separate from other agents to prevent confusion and improve accuracy.
    
    Design Philosophy:
    - Dedicated LLM for classification tasks only
    - Specialized prompts for email understanding
    - Context-aware decision making
    - Robust confidence scoring
    - Clear separation of concerns
    """

    def __init__(self):
        super().__init__("UnifiedEmailClassifierAgent")
        
        # Use a different model for classification (more focused)
        self.classification_model = "databricks-meta-llama-3-3-70b-instruct"
        
        # Load sales team and forwarder data for sender classification
        self.sales_team_manager = None
        self.forwarder_manager = None
        try:
            from utils.sales_team_manager import SalesTeamManager
            self.sales_team_manager = SalesTeamManager()
        except ImportError:
            print("⚠️ SalesTeamManager not available")
        
        try:
            from utils.forwarder_manager import ForwarderManager
            self.forwarder_manager = ForwarderManager()
        except ImportError:
            print("⚠️ ForwarderManager not available")
        
        # Email type categories for classification LLM
        self.email_types = {
            # Customer email types
            "customer_quote_request": "Customer asking for shipping rates or quotes",
            "customer_clarification": "Customer providing missing information or responding to clarification request",
            "customer_confirmation": "Customer confirming extracted details or accepting proposal",
            "customer_follow_up": "Customer asking follow-up questions or checking status",
            "customer_change_request": "Customer changing requirements or modifying request",
            "customer_additional_info": "Customer providing additional specifications or details",
            "customer_vague_response": "Customer providing vague, unclear, or irrelevant information in response",
            "customer_non_logistics": "Customer asking about non-logistics topics (billing, support, etc.)",
            "customer_vague_general": "Customer saying something vague or unclear without context",
            "customer_complaint": "Customer reporting problems, complaints, or issues",
            "customer_urgent": "Customer has urgent or emergency requests",
            
            # Forwarder email types
            "forwarder_rate_quote": "Forwarder providing rate quote or pricing information",
            "forwarder_clarification_request": "Forwarder asking for more details or clarification",
            "forwarder_booking_confirmation": "Forwarder confirming booking or availability",
            "forwarder_problem_report": "Forwarder reporting issues or problems",
            "forwarder_acknowledgment": "Forwarder acknowledging request or providing general response",
            
            # Sales person email types
            "sales_person_inquiry": "Sales person asking for information or clarification",
            "sales_person_update": "Sales person providing updates or information",
            "sales_person_acknowledgment": "Sales person acknowledging or responding to inquiry",
            
            # Special categories
            "confusing_email": "Email is unclear, confusing, or cannot be properly classified",
            "escalation_needed": "Email requires human intervention or escalation",
            "thread_continuation": "Email continues existing conversation",
            "new_thread": "Email starts new conversation"
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify email type based on content and context.
        
        Args:
            input_data: Dictionary containing:
                - email_text: Email content (primary focus)
                - sender: Email sender
                - thread_id: Thread identifier
                - thread_history: Previous emails in thread
                - customer_context: Customer information
                - forwarder_context: Forwarder information
        
        Returns:
            Dictionary containing classification results
        """
        print(f"🔍 UNIFIED_CLASSIFIER: Starting specialized LLM classification...")
        
        # Extract input data - focus on email content, not subject
        email_text = input_data.get("email_text", "")
        sender = input_data.get("sender", "")
        thread_id = input_data.get("thread_id", "")
        thread_history = input_data.get("thread_history", [])
        customer_context = input_data.get("customer_context", {})
        forwarder_context = input_data.get("forwarder_context", {})
        
        print(f"📧 Email: {email_text[:100]}...")
        print(f"👤 Sender: {sender}")
        
        # First, classify the sender type (sales person, forwarder, or customer)
        sender_classification = self._classify_sender_type(sender)
        print(f"🔍 Sender Classification: {sender_classification}")
        print(f"🧵 Thread ID: {thread_id}")
        
        # Analyze input for classification
        print(f"\n🔍 Classification Input Analysis:")
        print(f"   Email Text Length: {len(email_text)} characters")
        print(f"   Thread History: {len(thread_history)} previous emails")
        print(f"   Customer Context: {bool(customer_context)}")
        print(f"   Forwarder Context: {bool(forwarder_context)}")
        
        # Use specialized classification LLM
        try:
            result = self._specialized_classification(
                email_text, sender, thread_id, thread_history, 
                customer_context, forwarder_context, sender_classification
            )
            
            print(f"\n📊 Classification Output:")
            print(f"   Email Type: {result.get('email_type', 'Unknown')}")
            print(f"   Sender Type: {result.get('sender_type', 'Unknown')}")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
            print(f"   Escalation Needed: {result.get('escalation_needed', False)}")
            
            # Add sender classification to result
            result["sender_classification"] = sender_classification
            
            return result
            
        except Exception as e:
            print(f"❌ UNIFIED_CLASSIFIER: Classification failed - {e}")
            return {
                "email_type": "unknown",
                "sender_type": "unknown",
                "sender_classification": sender_classification,
                "confidence": 0.0,
                "escalation_needed": True,
                "error": str(e)
            }

    def _classify_sender_type(self, sender_email: str) -> Dict[str, Any]:
        """
        Classify sender type based on email address.
        Returns: {"type": "sales_person|forwarder|customer", "details": {...}}
        """
        if not sender_email:
            return {"type": "customer", "details": {}, "confidence": 0.0}
        
        sender_email = sender_email.lower().strip()
        
        # Check if sender is a sales person
        if self.sales_team_manager:
            try:
                # Get all sales persons and check their emails
                sales_team = self.sales_team_manager.get_all_sales_persons()
                for sales_person in sales_team:
                    if sales_person.get("email", "").lower() == sender_email:
                        return {
                            "type": "sales_person",
                            "details": sales_person,
                            "confidence": 1.0,
                            "sales_person_id": sales_person.get("id")
                        }
            except Exception as e:
                print(f"⚠️ Error checking sales team: {e}")
        
        # Check if sender is a forwarder
        if self.forwarder_manager:
            try:
                # Get forwarder by email
                forwarder = self.forwarder_manager.get_forwarder_by_email(sender_email)
                if forwarder:
                    return {
                        "type": "forwarder",
                        "details": forwarder,
                        "confidence": 1.0
                    }
            except Exception as e:
                print(f"⚠️ Error checking forwarders: {e}")
        
        # If not found in sales team or forwarders, it's a customer
        return {
            "type": "customer",
            "details": {"email": sender_email},
            "confidence": 0.8
        }

    def _specialized_classification(self, email_text: str, sender_email: str, thread_id: str,
                                  thread_history: List, customer_context: Dict, 
                                  forwarder_context: Dict, sender_classification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use specialized classification LLM for email classification.
        """
        if not self.client:
            return self._escalate_classification_failure(email_text, sender_email, "LLM client not available")
        
        # Prepare context for classification LLM
        thread_summary = self._prepare_thread_summary(thread_history)
        sender_context = self._prepare_sender_context(customer_context, forwarder_context, sender_email)
        
        # Create specialized classification prompt
        prompt = self._create_classification_prompt(
            email_text, sender_email, thread_summary, sender_context, sender_classification
        )
        
        # Define specialized function schema for email classification
        function_schema = {
            "name": "classify_email",
            "description": "Classify email type and sender based on content and context",
            "parameters": {
                "type": "object",
                "properties": {
                    "email_type": {
                        "type": "string",
                        "enum": ["customer_quote_request", "customer_clarification", "customer_confirmation", 
                                "forwarder_rate_quote", "forwarder_acknowledgment", "forwarder_confirmation",
                                "sales_person_inquiry", "sales_person_update", "sales_person_acknowledgment",
                                "escalation_request", "general_inquiry", "complaint", "unknown"],
                        "description": "Type of email based on content"
                    },
                    "sender_type": {
                        "type": "string",
                        "enum": ["customer", "forwarder", "sales_person", "internal", "unknown"],
                        "description": "Type of sender based on content and context"
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Confidence in classification (0.0 to 1.0)"
                    },
                    "escalation_needed": {
                        "type": "boolean",
                        "description": "Whether this email requires escalation"
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Urgency level of the email"
                    },
                    "complexity": {
                        "type": "string",
                        "enum": ["simple", "moderate", "complex"],
                        "description": "Complexity level of the request"
                    },
                    "intent": {
                        "type": "string",
                        "description": "Primary intent of the email"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of classification decision"
                    }
                },
                "required": ["email_type", "sender_type", "confidence", "escalation_needed"]
            }
        }
        
        # Generate classification response
        llm_result = self._generate_classification_response(prompt, function_schema)
        
        if "error" in llm_result:
            print(f"⚠️ Specialized LLM classification failed: {llm_result['error']}")
            return self._escalate_classification_failure(email_text, sender_email, llm_result['error'])
        
        # Enhance result with additional context
        enhanced_result = self._enhance_classification_result(
            llm_result, email_text, sender_email, thread_history
        )
        
        return enhanced_result

    def _create_classification_prompt(self, email_text: str, sender_email: str,
                                    thread_summary: str, sender_context: str, sender_classification: Dict[str, Any]) -> str:
        """
        Create specialized prompt for classification LLM.
        """
        prompt = f"""
You are a specialized email classification expert for a logistics CRM system. Your ONLY job is to classify emails accurately and determine the best course of action.

## EMAIL TO CLASSIFY:
Sender: {sender_email}
Content: {email_text}

## SENDER CLASSIFICATION:
Type: {sender_classification.get('type', 'unknown')}
Confidence: {sender_classification.get('confidence', 0.0)}
Details: {sender_classification.get('details', {})}

## CONTEXT INFORMATION:
{sender_context}

## THREAD HISTORY:
{thread_summary}

## CLASSIFICATION TASK:

Analyze this email and classify it according to the following categories:

### CUSTOMER EMAIL TYPES:
- customer_quote_request: Customer asking for shipping rates or quotes
- customer_clarification: Customer providing missing information or responding to clarification request
- customer_confirmation: Customer confirming extracted details or accepting proposal
- customer_follow_up: Customer asking follow-up questions or checking status
- customer_change_request: Customer changing requirements or modifying request
- customer_additional_info: Customer providing additional specifications or details
- customer_vague_response: Customer providing vague, unclear, or irrelevant information in response
- customer_non_logistics: Customer asking about non-logistics topics (billing, support, etc.)
- customer_vague_general: Customer saying something vague or unclear without context
- customer_complaint: Customer reporting problems, complaints, or issues
- customer_urgent: Customer has urgent or emergency requests

### FORWARDER EMAIL TYPES:
- forwarder_rate_quote: Forwarder providing rate quote or pricing information
- forwarder_clarification_request: Forwarder asking for more details or clarification
- forwarder_booking_confirmation: Forwarder confirming booking or availability
- forwarder_problem_report: Forwarder reporting issues or problems
- forwarder_acknowledgment: Forwarder acknowledging request or providing general response

### SALES PERSON EMAIL TYPES:
- sales_person_inquiry: Sales person asking for information or clarification
- sales_person_update: Sales person providing updates or information
- sales_person_acknowledgment: Sales person acknowledging or responding to inquiry

### SPECIAL CATEGORIES:
- confusing_email: Email is unclear, confusing, or cannot be properly classified
- escalation_needed: Email requires human intervention or escalation

## CLASSIFICATION GUIDELINES:

1. **Sender Type Detection**: Determine if sender is customer or forwarder based on:
   - Email domain patterns
   - Professional language and terminology
   - Content context and intent
   - Previous interactions if available

2. **Vague Content Detection**: Consider content vague if:
   - Uses uncertain language (maybe, perhaps, not sure, etc.)
   - Provides minimal or irrelevant information
   - Lacks specific details when they should be present
   - Contains generic responses without substance

3. **Escalation Triggers**: Escalate if:
   - Confidence is below 0.3
   - Contains urgent/emergency language
   - Multiple vague responses in thread
   - Complaints or complex issues
   - Non-logistics topics requiring human attention

4. **Thread Context**: Consider:
   - Whether this is a new conversation or continuation
   - Previous email types in the thread
   - Pattern of vague responses
   - Conversation progression

5. **Confidence Scoring**: Base confidence on:
   - Clarity of intent and content
   - Specificity of information provided
   - Alignment with expected patterns
   - Quality of language and structure

## YOUR TASK:
Classify this email comprehensively, considering all the above factors. Provide reasoning for your decision and assess confidence level.
"""
        return prompt

    def _prepare_thread_summary(self, thread_history: List) -> str:
        """
        Prepare thread history summary for classification LLM.
        """
        if not thread_history:
            return "This is a new email thread with no previous history."
        
        summary_parts = [f"Thread contains {len(thread_history)} previous emails:"]
        
        for i, email in enumerate(thread_history[-3:], 1):  # Last 3 emails for context
            classification = email.get("classification", {})
            email_type = classification.get("email_type", "unknown")
            subject = email.get("subject", "No subject")
            summary_parts.append(f"  {i}. {email_type}: {subject}")
        
        # Add vague response tracking
        vague_count = sum(1 for email in thread_history 
                         if email.get("classification", {}).get("is_vague", False))
        if vague_count > 0:
            summary_parts.append(f"  Note: {vague_count} previous vague responses in thread")
        
        return "\n".join(summary_parts)

    def _prepare_sender_context(self, customer_context: Dict, forwarder_context: Dict, sender_email: str) -> str:
        """
        Prepare sender context information for classification LLM.
        """
        context_parts = [f"Sender email: {sender_email}"]
        
        # Check if sender is known customer
        if customer_context and sender_email in customer_context.get("known_emails", []):
            context_parts.append("✓ Known customer email")
            customer_info = customer_context.get("customer_info", {})
            if customer_info:
                context_parts.append(f"  Customer: {customer_info.get('name', 'Unknown')}")
                context_parts.append(f"  Company: {customer_info.get('company', 'Unknown')}")
        
        # Check if sender is known forwarder
        elif forwarder_context and sender_email in forwarder_context.get("known_emails", []):
            context_parts.append("✓ Known forwarder email")
            forwarder_info = forwarder_context.get("forwarder_info", {})
            if forwarder_info:
                context_parts.append(f"  Forwarder: {forwarder_info.get('name', 'Unknown')}")
                context_parts.append(f"  Specialties: {forwarder_info.get('specialties', 'Unknown')}")
        
        # Analyze domain patterns
        domain = sender_email.split("@")[-1].lower() if "@" in sender_email else ""
        if any(keyword in domain for keyword in ["logistics", "freight", "shipping", "cargo"]):
            context_parts.append("⚠️ Domain suggests forwarder (logistics-related)")
        elif any(keyword in domain for keyword in ["gmail", "yahoo", "hotmail", "outlook"]):
            context_parts.append("⚠️ Domain suggests customer (personal email)")
        
        return "\n".join(context_parts)

    def _enhance_classification_result(self, llm_result: Dict, email_text: str, 
                                     sender_email: str, 
                                     thread_history: List) -> Dict[str, Any]:
        """
        Enhance LLM result with additional context and metadata.
        """
        # Add metadata
        enhanced_result = {
            **llm_result,
            "email_metadata": {
                "sender": sender_email,
                "word_count": len(email_text.split()),
                "processed_at": datetime.utcnow().isoformat()
            },
            "thread_context": {
                "is_continuation": bool(thread_history),
                "thread_length": len(thread_history),
                "previous_vague_count": sum(1 for email in thread_history 
                                          if email.get("classification", {}).get("is_vague", False))
            },
            "analysis_details": {
                "reasoning": llm_result.get("reasoning", ""),
                "classification_method": "specialized_llm",
                "confidence_factors": self._extract_confidence_factors(llm_result)
            }
        }
        
        # Add escalation details if needed
        if llm_result.get("escalation_needed", False):
            enhanced_result["escalation_details"] = {
                "reason": llm_result.get("escalation_reason", "Unknown"),
                "urgency": llm_result.get("urgency", "medium"),
                "recommended_action": self._get_escalation_action(llm_result)
            }
        
        return enhanced_result

    def _extract_confidence_factors(self, llm_result: Dict) -> List[str]:
        """
        Extract factors that influenced confidence level.
        """
        factors = []
        
        if llm_result.get("confidence", 0) >= 0.8:
            factors.append("High confidence - clear intent and content")
        elif llm_result.get("confidence", 0) >= 0.6:
            factors.append("Medium confidence - some uncertainty in classification")
        else:
            factors.append("Low confidence - unclear or ambiguous content")
        
        if llm_result.get("is_vague", False):
            factors.append("Vague content detected")
        
        if llm_result.get("complexity") == "complex":
            factors.append("Complex request requiring detailed analysis")
        
        return factors

    def _get_escalation_action(self, llm_result: Dict) -> str:
        """
        Determine recommended action for escalation.
        """
        if llm_result.get("urgency") == "high":
            return "Immediate human review required"
        elif llm_result.get("is_vague", False):
            return "Human review for vague content handling"
        elif llm_result.get("email_type") == "customer_non_logistics":
            return "Route to appropriate department"
        else:
            return "Standard escalation process"

    def _escalate_classification_failure(self, email_text: str, sender_email: str, error: str) -> Dict[str, Any]:
        """
        Escalate when classification fails instead of using fallback.
        """
        print(f"🚨 ESCALATING: Classification failed - {error}")
        
        return {
            "email_type": "escalation_needed",
            "sender_type": "unknown",
            "confidence": 0.0,
            "escalation_needed": True,
            "escalation_reason": f"Classification system failure: {error}",
            "urgency": "high",
            "complexity": "complex",
            "is_vague": False,
            "intent": "unknown",
            "thread_context": "new_thread",
            "reasoning": f"Classification system error: {error}",
            "classification_method": "escalation"
        }

    def _generate_classification_response(self, prompt: str, function_schema: Dict) -> Dict[str, Any]:
        """
        Generate response using specialized classification LLM.
        """
        return self._make_llm_call(
            prompt=prompt,
            function_schema=function_schema,
            model_name=self.classification_model,
            temperature=0.1,
            max_tokens=800
        )


# =====================================================
#                 🧪 Test Functions
# =====================================================

def test_specialized_classifier():
    """Test the Specialized LLM-based Unified Email Classifier Agent"""
    print("🧪 Testing Specialized LLM-based Unified Email Classifier Agent")
    print("=" * 60)
    
    # Initialize agent
    classifier = UnifiedEmailClassifierAgent()
    classifier.load_context()
    
    # Test scenarios
    test_cases = [
        {
            "name": "Customer Quote Request",
            "email_data": {
                "email_text": "Hi, I need shipping rates from Shanghai to Los Angeles for a 40HC container. Please provide quotes.",
                "subject": "Shipping Quote Request",
                "sender": "customer@company.com",
                "thread_id": "thread_123"
            }
        },
        {
            "name": "Customer Vague Response (Scenario 2.6)",
            "email_data": {
                "email_text": "Thanks, maybe something like that. Not sure about the details.",
                "subject": "Re: Shipping Quote Request",
                "sender": "customer@company.com",
                "thread_id": "thread_123"
            },
            "thread_history": [
                {"classification": {"email_type": "customer_quote_request"}}
            ]
        },
        {
            "name": "Customer Vague General (Scenario 3.5)",
            "email_data": {
                "email_text": "Hello, just checking in. How are things going?",
                "subject": "General Inquiry",
                "sender": "customer@company.com",
                "thread_id": "thread_456"
            }
        },
        {
            "name": "Forwarder Rate Quote",
            "email_data": {
                "email_text": "Dear SeaRates Team, Please find our competitive rate quote for your Shanghai to Los Angeles shipment. Rate: USD 2,800 per 40HC. Transit time: 16 days.",
                "subject": "Rate Quote - Shanghai to Los Angeles",
                "sender": "rates@logistics-forwarder.com",
                "thread_id": "thread_789"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📧 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        result = classifier.process(test_case)
        
        print(f"✅ Email Type: {result.get('email_type', 'unknown')}")
        print(f"✅ Sender Type: {result.get('sender_type', 'unknown')}")
        print(f"✅ Confidence: {result.get('confidence', 0):.2f}")
        print(f"✅ Escalation: {result.get('escalation_needed', False)}")
        print(f"✅ Intent: {result.get('intent', 'unknown')}")
        print(f"✅ Complexity: {result.get('complexity', 'unknown')}")
        
        if result.get('is_vague', False):
            print(f"⚠️ Vague Content: {result.get('vague_reason', 'Unknown reason')}")
        
        if result.get('escalation_reason'):
            print(f"🚨 Escalation Reason: {result['escalation_reason']}")
        
        if result.get('reasoning'):
            print(f"🧠 Reasoning: {result['reasoning'][:100]}...")
    
    print(f"\n🎉 All tests completed!")


if __name__ == "__main__":
    test_specialized_classifier() 