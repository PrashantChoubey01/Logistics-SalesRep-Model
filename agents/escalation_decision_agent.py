#!/usr/bin/env python3
"""
Escalation Decision Agent - Specialized LLM Approach

This agent uses a dedicated LLM specifically for determining when and how to escalate issues,
considering multiple factors and context to make intelligent escalation decisions.

Key Features:
1. Dedicated escalation decision LLM
2. Multi-factor escalation analysis
3. Context-aware decision making
4. Escalation type classification
5. Priority and urgency assessment
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent


class EscalationDecisionAgent(BaseAgent):
    """
    Escalation Decision Agent - Specialized LLM Design
    
    This agent uses a dedicated LLM specifically for escalation decisions,
    separate from other agents to prevent confusion and improve accuracy.
    
    Design Philosophy:
    - Dedicated LLM for escalation decisions only
    - Multi-factor analysis for escalation decisions
    - Context-aware decision making
    - Priority and urgency assessment
    - Intelligent escalation routing
    """

    def __init__(self):
        super().__init__("EscalationDecisionAgent")
        
        # Use a different model for escalation decisions (more focused on decision making)
        self.escalation_model = "databricks-meta-llama-3-3-70b-instruct"
        
        # Escalation types
        self.escalation_types = {
            "customer_complaint": "Customer complaint or dissatisfaction",
            "technical_issue": "Technical problem or system issue",
            "complex_request": "Complex request requiring human expertise",
            "vague_communication": "Vague or unclear communication pattern",
            "urgent_request": "Urgent or emergency request",
            "rate_negotiation": "Rate negotiation or pricing issues",
            "capacity_issue": "Capacity or availability problems",
            "documentation_problem": "Documentation or compliance issues",
            "forwarder_problem": "Forwarder-related issues",
            "general_inquiry": "General inquiry requiring human response"
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core escalation decision logic using specialized escalation decision LLM.
        
        Args:
            input_data: Dictionary containing:
                - email_data: Email content and metadata
                - classification_result: Email classification results
                - thread_context: Thread analysis results
                - extraction_result: Information extraction results
                - customer_context: Customer information
                - forwarder_context: Forwarder information
                - escalation_history: Previous escalation history
        
        Returns:
            Dictionary containing escalation decision results
        """
        print(f"🚨 ESCALATION_DECISION: Starting specialized LLM escalation analysis...")
        
        # Extract input data
        email_data = input_data.get("email_data", {})
        classification_result = input_data.get("classification_result", {})
        thread_context = input_data.get("thread_context", {})
        extraction_result = input_data.get("extraction_result", {})
        customer_context = input_data.get("customer_context", {})
        forwarder_context = input_data.get("forwarder_context", {})
        escalation_history = input_data.get("escalation_history", [])
        
        # Get email info
        email_text = email_data.get("email_text", "")
        subject = email_data.get("subject", "")
        sender_email = email_data.get("sender", "")
        thread_id = email_data.get("thread_id", "")
        
        print(f"📧 Email: {subject[:50]}...")
        print(f"👤 Sender: {sender_email}")
        print(f"🧵 Thread ID: {thread_id}")
        
        # Use specialized escalation decision LLM
        escalation_result = self._specialized_escalation_decision(
            email_text, subject, sender_email, classification_result,
            thread_context, extraction_result, customer_context,
            forwarder_context, escalation_history
        )
        
        print(f"✅ ESCALATION_DECISION: Specialized LLM analysis complete")
        print(f"   Escalation Needed: {escalation_result['escalation_needed']}")
        print(f"   Escalation Type: {escalation_result.get('escalation_type', 'N/A')}")
        print(f"   Priority: {escalation_result.get('priority', 'N/A')}")
        
        return escalation_result

    def _specialized_escalation_decision(self, email_text: str, subject: str, sender_email: str,
                                       classification_result: Dict, thread_context: Dict,
                                       extraction_result: Dict, customer_context: Dict,
                                       forwarder_context: Dict, escalation_history: List) -> Dict[str, Any]:
        """
        Use specialized escalation decision LLM for escalation analysis.
        """
        if not self.client:
            return self._fallback_escalation_decision(classification_result, thread_context)
        
        # Prepare context for escalation decision LLM
        escalation_context = self._prepare_escalation_context(escalation_history)
        customer_priority = self._prepare_customer_priority(customer_context)
        forwarder_context_summary = self._prepare_forwarder_context_summary(forwarder_context)
        
        # Create specialized escalation decision prompt
        prompt = self._create_escalation_decision_prompt(
            email_text, subject, sender_email, classification_result,
            thread_context, extraction_result, escalation_context,
            customer_priority, forwarder_context_summary
        )
        
        # Define specialized function schema for escalation decision
        function_schema = {
            "name": "make_escalation_decision",
            "description": "Make escalation decision using specialized escalation decision logic",
            "parameters": {
                "type": "object",
                "properties": {
                    "escalation_needed": {
                        "type": "boolean",
                        "description": "Whether escalation is required"
                    },
                    "escalation_type": {
                        "type": "string",
                        "enum": list(self.escalation_types.keys()),
                        "description": "The type of escalation required"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Priority level of the escalation"
                    },
                    "urgency": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Urgency level of the escalation"
                    },
                    "escalation_reason": {
                        "type": "string",
                        "description": "Detailed reason for escalation"
                    },
                    "recommended_team": {
                        "type": "string",
                        "enum": ["sales", "operations", "technical", "customer_service", "management"],
                        "description": "Recommended team for escalation"
                    },
                    "required_actions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Required actions for escalation"
                    },
                    "timeline": {
                        "type": "string",
                        "description": "Expected timeline for resolution"
                    },
                    "customer_impact": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Impact on customer relationship"
                    },
                    "business_impact": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "Impact on business operations"
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Confidence in escalation decision"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of escalation decision"
                    }
                },
                "required": ["escalation_needed", "priority", "urgency", "escalation_reason", "confidence", "reasoning"]
            }
        }
        
        # Get specialized LLM escalation decision
        llm_result = self._generate_escalation_decision_response(prompt, function_schema)
        
        if "error" in llm_result:
            print(f"⚠️ Specialized LLM escalation decision failed, using fallback: {llm_result['error']}")
            return self._fallback_escalation_decision(classification_result, thread_context)
        
        # Enhance result with additional context
        enhanced_result = self._enhance_escalation_result(
            llm_result, email_text, subject, sender_email, escalation_history
        )
        
        return enhanced_result

    def _create_escalation_decision_prompt(self, email_text: str, subject: str, sender_email: str,
                                         classification_result: Dict, thread_context: Dict,
                                         extraction_result: Dict, escalation_context: str,
                                         customer_priority: str, forwarder_context_summary: str) -> str:
        """
        Create specialized prompt for escalation decision LLM.
        """
        prompt = f"""
You are a specialized escalation decision expert for a logistics CRM system. Your ONLY job is to determine when and how to escalate issues.

## EMAIL TO ANALYZE:
Subject: {subject}
Sender: {sender_email}
Content: {email_text}

## CLASSIFICATION RESULTS:
Email Type: {classification_result.get('email_type', 'unknown')}
Confidence: {classification_result.get('confidence', 0):.2f}
Escalation Flagged: {classification_result.get('escalation_needed', False)}
Escalation Reason: {classification_result.get('escalation_reason', 'N/A')}

## THREAD CONTEXT:
Thread State: {thread_context.get('thread_state', 'unknown')}
Conversation Stage: {thread_context.get('conversation_stage', 'unknown')}
Vague Pattern: {thread_context.get('vague_pattern_detected', False)}
Vague Count: {thread_context.get('vague_response_count', 0)}

## EXTRACTION RESULTS:
Extraction Quality: {extraction_result.get('extraction_quality', 0):.2f}
Missing Fields: {len(extraction_result.get('missing_fields', []))}
Validation Issues: {len(extraction_result.get('validation_issues', []))}

## ESCALATION CONTEXT:
{escalation_context}

## CUSTOMER PRIORITY:
{customer_priority}

## FORWARDER CONTEXT:
{forwarder_context_summary}

## ESCALATION DECISION TASK:

Analyze this situation and determine if escalation is needed:

### ESCALATION TYPES:
- customer_complaint: Customer complaint or dissatisfaction
- technical_issue: Technical problem or system issue
- complex_request: Complex request requiring human expertise
- vague_communication: Vague or unclear communication pattern
- urgent_request: Urgent or emergency request
- rate_negotiation: Rate negotiation or pricing issues
- capacity_issue: Capacity or availability problems
- documentation_problem: Documentation or compliance issues
- forwarder_problem: Forwarder-related issues
- general_inquiry: General inquiry requiring human response

### ESCALATION TRIGGERS:
Escalate if ANY of the following are true:
1. Customer complaint or dissatisfaction
2. Technical issues or system problems
3. Complex requests requiring human expertise
4. Multiple vague responses (3+)
5. Urgent or emergency requests
6. Rate negotiation or pricing issues
7. Capacity or availability problems
8. Documentation or compliance issues
9. Forwarder-related problems
10. General inquiries requiring human response

### PRIORITY ASSESSMENT:
- low: Standard escalation, no urgency
- medium: Moderate urgency, respond within 24 hours
- high: High urgency, respond within 4 hours
- urgent: Critical urgency, respond immediately

### URGENCY ASSESSMENT:
- low: No immediate action required
- medium: Action required within 24 hours
- high: Action required within 4 hours
- critical: Immediate action required

### TEAM ROUTING:
- sales: Customer relationship or sales issues
- operations: Operational or logistics issues
- technical: Technical or system issues
- customer_service: General customer service issues
- management: High-priority or complex issues

## YOUR TASK:
Analyze this situation comprehensively and make an escalation decision. Provide reasoning for your decision and assess confidence level.
"""
        return prompt

    def _prepare_escalation_context(self, escalation_history: List) -> str:
        """
        Prepare escalation history context for escalation decision LLM.
        """
        if not escalation_history:
            return "No previous escalation history."
        
        context_parts = [f"Escalation History ({len(escalation_history)} previous escalations):"]
        
        for i, escalation in enumerate(escalation_history[-3:], 1):  # Last 3 escalations
            escalation_type = escalation.get("escalation_type", "unknown")
            priority = escalation.get("priority", "unknown")
            date = escalation.get("date", "unknown")
            context_parts.append(f"  {i}. {escalation_type} ({priority}) - {date}")
        
        # Check for escalation patterns
        recent_escalations = [e for e in escalation_history if e.get("priority") in ["high", "urgent"]]
        if len(recent_escalations) >= 2:
            context_parts.append("  ⚠️ Multiple high-priority escalations recently")
        
        return "\n".join(context_parts)

    def _prepare_customer_priority(self, customer_context: Dict) -> str:
        """
        Prepare customer priority context for escalation decision LLM.
        """
        if not customer_context:
            return "Customer priority: Standard"
        
        priority = customer_context.get("priority", "standard")
        customer_info = customer_context.get("customer_info", {})
        
        priority_parts = [f"Customer Priority: {priority.title()}"]
        
        if customer_info:
            priority_parts.append(f"Customer: {customer_info.get('name', 'Unknown')}")
            priority_parts.append(f"Company: {customer_info.get('company', 'Unknown')}")
        
        # Add priority-specific information
        if priority == "high":
            priority_parts.append("⚠️ High-priority customer - escalate quickly")
        elif priority == "vip":
            priority_parts.append("🚨 VIP customer - immediate attention required")
        
        return "\n".join(priority_parts)

    def _prepare_forwarder_context_summary(self, forwarder_context: Dict) -> str:
        """
        Prepare forwarder context summary for escalation decision LLM.
        """
        if not forwarder_context:
            return "No forwarder context available."
        
        forwarder_info = forwarder_context.get("forwarder_info", {})
        if not forwarder_info:
            return "No forwarder information available."
        
        summary_parts = ["Forwarder Context:"]
        summary_parts.append(f"  Name: {forwarder_info.get('name', 'Unknown')}")
        summary_parts.append(f"  Specialties: {forwarder_info.get('specialties', 'Unknown')}")
        
        # Add performance metrics if available
        performance = forwarder_context.get("performance", {})
        if performance:
            response_time = performance.get("avg_response_time", "Unknown")
            success_rate = performance.get("success_rate", "Unknown")
            summary_parts.append(f"  Avg Response Time: {response_time}")
            summary_parts.append(f"  Success Rate: {success_rate}")
        
        return "\n".join(summary_parts)

    def _enhance_escalation_result(self, llm_result: Dict, email_text: str,
                                 subject: str, sender_email: str,
                                 escalation_history: List) -> Dict[str, Any]:
        """
        Enhance LLM result with additional escalation context and metadata.
        """
        # Add metadata
        enhanced_result = {
            **llm_result,
            "escalation_metadata": {
                "email_subject": subject,
                "sender_email": sender_email,
                "escalation_count": len(escalation_history),
                "decision_made_at": datetime.utcnow().isoformat()
            },
            "escalation_context": {
                "has_previous_escalations": bool(escalation_history),
                "recent_high_priority": len([e for e in escalation_history[-5:] if e.get("priority") in ["high", "urgent"]])
            },
            "analysis_details": {
                "reasoning": llm_result.get("reasoning", ""),
                "decision_method": "specialized_escalation_llm",
                "confidence_factors": self._extract_escalation_confidence_factors(llm_result)
            }
        }
        
        # Add escalation details if escalation is needed
        if llm_result.get("escalation_needed", False):
            enhanced_result["escalation_details"] = {
                "type": llm_result.get("escalation_type", "unknown"),
                "priority": llm_result.get("priority", "medium"),
                "urgency": llm_result.get("urgency", "medium"),
                "recommended_team": llm_result.get("recommended_team", "customer_service"),
                "required_actions": llm_result.get("required_actions", []),
                "timeline": llm_result.get("timeline", "24 hours"),
                "customer_impact": llm_result.get("customer_impact", "medium"),
                "business_impact": llm_result.get("business_impact", "medium")
            }
        
        return enhanced_result

    def _extract_escalation_confidence_factors(self, llm_result: Dict) -> List[str]:
        """
        Extract factors that influenced escalation decision confidence.
        """
        factors = []
        
        if llm_result.get("confidence", 0) >= 0.8:
            factors.append("High confidence - clear escalation need")
        elif llm_result.get("confidence", 0) >= 0.6:
            factors.append("Medium confidence - some uncertainty in decision")
        else:
            factors.append("Low confidence - unclear escalation need")
        
        if llm_result.get("priority") == "urgent":
            factors.append("Urgent priority escalation")
        elif llm_result.get("priority") == "high":
            factors.append("High priority escalation")
        
        if llm_result.get("urgency") == "critical":
            factors.append("Critical urgency")
        elif llm_result.get("urgency") == "high":
            factors.append("High urgency")
        
        if llm_result.get("customer_impact") == "critical":
            factors.append("Critical customer impact")
        elif llm_result.get("business_impact") == "critical":
            factors.append("Critical business impact")
        
        return factors

    def _fallback_escalation_decision(self, classification_result: Dict, thread_context: Dict) -> Dict[str, Any]:
        """
        Fallback escalation decision when specialized LLM is not available.
        """
        print("⚠️ Using fallback escalation decision (Specialized LLM not available)")
        
        # Simple fallback logic
        escalation_needed = (
            classification_result.get("escalation_needed", False) or
            thread_context.get("vague_pattern_detected", False) or
            thread_context.get("vague_response_count", 0) >= 3
        )
        
        if escalation_needed:
            escalation_type = "vague_communication" if thread_context.get("vague_pattern_detected", False) else "general_inquiry"
            priority = "high" if thread_context.get("vague_response_count", 0) >= 3 else "medium"
        else:
            escalation_type = "none"
            priority = "low"
        
        return {
            "escalation_needed": escalation_needed,
            "escalation_type": escalation_type,
            "priority": priority,
            "urgency": "medium" if escalation_needed else "low",
            "escalation_reason": "Fallback escalation decision due to specialized LLM unavailability",
            "recommended_team": "customer_service",
            "required_actions": ["Manual review required"],
            "timeline": "24 hours",
            "customer_impact": "medium",
            "business_impact": "medium",
            "confidence": 0.5,  # Low confidence for fallback
            "reasoning": "Fallback escalation decision due to specialized LLM unavailability",
            "decision_method": "fallback"
        }

    def _generate_escalation_decision_response(self, prompt: str, function_schema: Dict) -> Dict[str, Any]:
        """
        Generate response using specialized escalation decision LLM.
        """
        if not self.client:
            return {"error": "Specialized escalation decision LLM client not available"}
        
        try:
            # Convert function schema to tools format for Databricks
            tools = [{
                "type": "function",
                "function": function_schema
            }]
            
            tool_choice = {
                "type": "function",
                "function": {"name": function_schema["name"]}
            }
            
            # Use OpenAI client for function calling
            client = self.get_openai_client()
            if not client:
                return {"error": "OpenAI client not available for function calling"}
            
            response = client.chat.completions.create(
                model=self.escalation_model,  # Use specialized model
                messages=[{"role": "user", "content": prompt}],
                tools=tools,
                tool_choice=tool_choice,
                temperature=0.1,  # Low temperature for consistent decisions
                max_tokens=800
            )
            
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls:
                import json
                return json.loads(tool_calls[0].function.arguments)
            else:
                return {"error": "No tool calls in response"}
                
        except Exception as e:
            return {"error": f"Specialized escalation decision LLM call failed: {str(e)}"}


# =====================================================
#                 🧪 Test Functions
# =====================================================

def test_escalation_decision():
    """Test the Specialized LLM-based Escalation Decision Agent"""
    print("🧪 Testing Specialized LLM-based Escalation Decision Agent")
    print("=" * 60)
    
    # Initialize agent
    decision_agent = EscalationDecisionAgent()
    decision_agent.load_context()
    
    # Test scenarios
    test_cases = [
        {
            "name": "Customer Complaint",
            "email_data": {
                "email_text": "I'm very dissatisfied with your service. My shipment has been delayed for a week and no one is responding to my emails. This is unacceptable and I want to speak to a manager immediately.",
                "subject": "Complaint - Delayed Shipment",
                "sender": "angry.customer@company.com",
                "thread_id": "thread_123"
            },
            "classification_result": {
                "email_type": "customer_complaint",
                "confidence": 0.9,
                "escalation_needed": True,
                "escalation_reason": "Customer complaint"
            },
            "thread_context": {
                "thread_state": "ongoing",
                "conversation_stage": "complaint",
                "vague_pattern_detected": False,
                "vague_response_count": 0
            },
            "extraction_result": {
                "extraction_quality": 0.8,
                "missing_fields": [],
                "validation_issues": []
            },
            "customer_context": {
                "priority": "high",
                "customer_info": {
                    "name": "John Smith",
                    "company": "Tech Solutions Inc."
                }
            },
            "forwarder_context": {},
            "escalation_history": []
        },
        {
            "name": "Multiple Vague Responses",
            "email_data": {
                "email_text": "Maybe something like that. Not sure about the details.",
                "subject": "Re: Re: Re: Shipping Quote Request",
                "sender": "customer@company.com",
                "thread_id": "thread_456"
            },
            "classification_result": {
                "email_type": "customer_vague_response",
                "confidence": 0.7,
                "escalation_needed": False,
                "escalation_reason": ""
            },
            "thread_context": {
                "thread_state": "multiple_vague",
                "conversation_stage": "ongoing",
                "vague_pattern_detected": True,
                "vague_response_count": 3
            },
            "extraction_result": {
                "extraction_quality": 0.3,
                "missing_fields": ["origin", "destination", "container_type"],
                "validation_issues": ["Vague information"]
            },
            "customer_context": {
                "priority": "standard",
                "customer_info": {
                    "name": "Jane Doe",
                    "company": "Small Business Ltd."
                }
            },
            "forwarder_context": {},
            "escalation_history": []
        },
        {
            "name": "Urgent Request",
            "email_data": {
                "email_text": "URGENT: I need immediate assistance with a critical shipment. This is an emergency and I need someone to call me right away at +1-555-123-4567.",
                "subject": "URGENT - Emergency Shipment",
                "sender": "urgent.customer@company.com",
                "thread_id": "thread_789"
            },
            "classification_result": {
                "email_type": "customer_urgent",
                "confidence": 0.95,
                "escalation_needed": True,
                "escalation_reason": "Urgent request"
            },
            "thread_context": {
                "thread_state": "new_thread",
                "conversation_stage": "urgent",
                "vague_pattern_detected": False,
                "vague_response_count": 0
            },
            "extraction_result": {
                "extraction_quality": 0.6,
                "missing_fields": ["origin", "destination"],
                "validation_issues": []
            },
            "customer_context": {
                "priority": "vip",
                "customer_info": {
                    "name": "VIP Customer",
                    "company": "Large Corporation"
                }
            },
            "forwarder_context": {},
            "escalation_history": []
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🚨 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        result = decision_agent.process(test_case)
        
        print(f"✅ Escalation Needed: {result.get('escalation_needed', False)}")
        print(f"✅ Escalation Type: {result.get('escalation_type', 'N/A')}")
        print(f"✅ Priority: {result.get('priority', 'N/A')}")
        print(f"✅ Urgency: {result.get('urgency', 'N/A')}")
        print(f"✅ Confidence: {result.get('confidence', 0):.2f}")
        
        if result.get('escalation_needed', False):
            escalation_details = result.get('escalation_details', {})
            print(f"📋 Recommended Team: {escalation_details.get('recommended_team', 'N/A')}")
            print(f"⏰ Timeline: {escalation_details.get('timeline', 'N/A')}")
            print(f"👤 Customer Impact: {escalation_details.get('customer_impact', 'N/A')}")
            print(f"🏢 Business Impact: {escalation_details.get('business_impact', 'N/A')}")
            
            required_actions = escalation_details.get('required_actions', [])
            if required_actions:
                print(f"📝 Required Actions: {', '.join(required_actions)}")
        
        if result.get('escalation_reason'):
            print(f"📝 Escalation Reason: {result['escalation_reason']}")
        
        if result.get('reasoning'):
            print(f"🧠 Reasoning: {result['reasoning'][:100]}...")
    
    print(f"\n🎉 All tests completed!")


if __name__ == "__main__":
    test_escalation_decision() 