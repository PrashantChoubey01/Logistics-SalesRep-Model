#!/usr/bin/env python3
"""
Response Evaluation Agent

This agent evaluates the generated email response against the conversation history
to assess if it's correct, appropriate, and should be sent to the customer.

Key Features:
1. Conversation context analysis
2. Response appropriateness assessment
3. Accuracy validation
4. Send/no-send recommendation
5. Improvement suggestions
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent


class ResponseEvaluationAgent(BaseAgent):
    """
    Response Evaluation Agent - Conversation Analysis & Response Assessment
    
    This agent analyzes the entire conversation thread and the generated response
    to determine if the response is appropriate, accurate, and should be sent.
    
    Design Philosophy:
    - Comprehensive conversation analysis
    - Response appropriateness assessment
    - Accuracy validation against extracted data
    - Clear send/no-send recommendations
    - Actionable improvement suggestions
    """

    def __init__(self):
        super().__init__("ResponseEvaluationAgent")
        
        # Use a specialized model for conversation analysis
        self.evaluation_model = "databricks-meta-llama-3-3-70b-instruct"
        
        # Evaluation criteria
        self.evaluation_criteria = {
            "accuracy": "Response matches extracted data and customer intent",
            "appropriateness": "Response tone and content are suitable for the situation",
            "completeness": "Response addresses all customer concerns and questions",
            "context_awareness": "Response considers conversation history and context",
            "professionalism": "Response maintains professional standards"
        }
        
        # Load LLM context
        self.load_context()

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate the generated response against conversation context.
        
        Args:
            input_data: Dictionary containing:
                - email_data: Current email information
                - thread_history: Complete conversation history
                - extracted_data: Extracted information from current email
                - generated_response: The response to evaluate
                - customer_context: Customer information
                - response_type: Type of response generated (clarification, confirmation, etc.)
        
        Returns:
            Dictionary containing evaluation results and recommendations
        """
        print(f"🔍 RESPONSE_EVALUATOR: Starting response evaluation...")
        
        # Extract input data
        email_data = input_data.get("email_data", {})
        thread_history = input_data.get("thread_history", [])
        extracted_data = input_data.get("extracted_data", {})
        generated_response = input_data.get("generated_response", {})
        customer_context = input_data.get("customer_context", {})
        response_type = input_data.get("response_type", "unknown")
        
        print(f"📧 Email: {email_data.get('subject', 'No subject')}")
        print(f"🧵 Thread History: {len(thread_history)} entries")
        print(f"📝 Response Type: {response_type}")
        
        # Perform comprehensive evaluation
        evaluation_result = self._evaluate_response(
            email_data, thread_history, extracted_data, 
            generated_response, customer_context, response_type
        )
        
        print(f"✅ RESPONSE_EVALUATOR: Evaluation complete")
        print(f"   Should Send: {evaluation_result.get('should_send', False)}")
        print(f"   Confidence: {evaluation_result.get('confidence', 0):.2f}")
        print(f"   Issues Found: {len(evaluation_result.get('issues', []))}")
        
        return evaluation_result

    def _evaluate_response(self, email_data: Dict, thread_history: List[Dict], 
                          extracted_data: Dict, generated_response: Dict,
                          customer_context: Dict, response_type: str) -> Dict[str, Any]:
        """Evaluate the response comprehensively"""
        
        print(f"🔍 Evaluating response against conversation context...")
        
        try:
            # Prepare conversation summary
            conversation_summary = self._prepare_conversation_summary(thread_history)
            
            # Prepare evaluation context
            evaluation_context = self._prepare_evaluation_context(
                email_data, extracted_data, generated_response, customer_context, response_type
            )
            
            # Create evaluation prompt
            prompt = self._create_evaluation_prompt(
                conversation_summary, evaluation_context, response_type
            )
            
            # Define function schema for evaluation
            function_schema = {
                "name": "evaluate_response",
                "description": "Evaluate if the generated response is appropriate and should be sent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "should_send": {
                            "type": "boolean",
                            "description": "Whether the response should be sent to the customer"
                        },
                        "confidence": {
                            "type": "number",
                            "description": "Confidence level in the evaluation (0-1)"
                        },
                        "evaluation_score": {
                            "type": "number",
                            "description": "Overall evaluation score (0-100)"
                        },
                        "accuracy_score": {
                            "type": "number",
                            "description": "Accuracy of response to extracted data (0-100)"
                        },
                        "appropriateness_score": {
                            "type": "number",
                            "description": "Appropriateness of response tone and content (0-100)"
                        },
                        "completeness_score": {
                            "type": "number",
                            "description": "Completeness of response addressing customer needs (0-100)"
                        },
                        "context_awareness_score": {
                            "type": "number",
                            "description": "Response awareness of conversation context (0-100)"
                        },
                        "issues": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of issues found with the response"
                        },
                        "improvements": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Suggested improvements for the response"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Detailed reasoning for the evaluation"
                        },
                        "recommended_action": {
                            "type": "string",
                            "enum": ["send", "modify", "escalate", "clarify"],
                            "description": "Recommended action for this response"
                        }
                    },
                    "required": ["should_send", "confidence", "evaluation_score", "reasoning", "recommended_action"]
                }
            }
            
            # Generate evaluation
            evaluation_result = self._generate_evaluation_response(prompt, function_schema)
            
            # Enhance result with metadata
            enhanced_result = self._enhance_evaluation_result(
                evaluation_result, email_data, thread_history, response_type
            )
            
            return enhanced_result
            
        except Exception as e:
            print(f"❌ Response evaluation failed: {e}")
            return {
                "should_send": False,
                "confidence": 0.0,
                "evaluation_score": 0,
                "issues": [f"Evaluation failed: {e}"],
                "improvements": ["Fix evaluation system"],
                "reasoning": f"Evaluation failed due to error: {e}",
                "recommended_action": "escalate",
                "error": str(e)
            }

    def _prepare_conversation_summary(self, thread_history: List[Dict]) -> str:
        """Prepare a summary of the conversation history"""
        if not thread_history:
            return "No previous conversation history."
        
        summary_parts = []
        summary_parts.append(f"Conversation History ({len(thread_history)} interactions):")
        
        for i, entry in enumerate(thread_history, 1):
            email_data = entry.get("email", {})
            step_results = entry.get("step_results", {})
            
            subject = email_data.get("subject", "No subject")
            sender = email_data.get("sender", "Unknown")
            
            # Get response type if available
            response_type = "unknown"
            if "clarification_response" in step_results:
                response_type = "clarification"
            elif "confirmation_response" in step_results:
                response_type = "confirmation"
            elif "acknowledgment_response" in step_results:
                response_type = "acknowledgment"
            elif "email_response" in step_results:
                response_type = "email_response"
            
            summary_parts.append(f"  {i}. {sender}: {subject} (Response: {response_type})")
            
            # Add key extracted data if available
            extraction = step_results.get("extraction", {})
            if extraction and "extracted_data" in extraction:
                extracted_data = extraction["extracted_data"]
                shipment = extracted_data.get("shipment_details", {})
                if shipment:
                    origin = shipment.get("origin", "")
                    destination = shipment.get("destination", "")
                    if origin and destination:
                        summary_parts.append(f"     Route: {origin} → {destination}")
        
        return "\n".join(summary_parts)

    def _prepare_evaluation_context(self, email_data: Dict, extracted_data: Dict,
                                  generated_response: Dict, customer_context: Dict,
                                  response_type: str) -> str:
        """Prepare context for evaluation"""
        
        context_parts = []
        
        # Current email context
        context_parts.append("CURRENT EMAIL:")
        context_parts.append(f"  Subject: {email_data.get('subject', 'No subject')}")
        context_parts.append(f"  Sender: {email_data.get('sender', 'Unknown')}")
        context_parts.append(f"  Content: {email_data.get('email_text', 'No content')[:200]}...")
        
        # Extracted data
        context_parts.append("\nEXTRACTED DATA:")
        if extracted_data:
            shipment = extracted_data.get("shipment_details", {})
            contact = extracted_data.get("contact_information", {})
            
            if shipment:
                context_parts.append("  Shipment Details:")
                for key, value in shipment.items():
                    if value:
                        context_parts.append(f"    {key}: {value}")
            
            if contact:
                context_parts.append("  Contact Information:")
                for key, value in contact.items():
                    if value:
                        context_parts.append(f"    {key}: {value}")
        else:
            context_parts.append("  No data extracted")
        
        # Generated response
        context_parts.append("\nGENERATED RESPONSE:")
        context_parts.append(f"  Type: {response_type}")
        context_parts.append(f"  Subject: {generated_response.get('subject', 'No subject')}")
        context_parts.append(f"  Content: {generated_response.get('response_body', 'No content')[:300]}...")
        
        # Customer context
        context_parts.append("\nCUSTOMER CONTEXT:")
        customer_info = customer_context.get("customer_info", {})
        context_parts.append(f"  Name: {customer_info.get('name', 'Unknown')}")
        context_parts.append(f"  Company: {customer_info.get('company', 'Unknown')}")
        context_parts.append(f"  Priority: {customer_context.get('priority', 'medium')}")
        
        return "\n".join(context_parts)

    def _create_evaluation_prompt(self, conversation_summary: str, evaluation_context: str,
                                response_type: str) -> str:
        """Create the evaluation prompt"""
        
        return f"""
# RESPONSE EVALUATION

You are an expert email response evaluator for a logistics company. Your job is to assess whether a generated email response is appropriate, accurate, and should be sent to the customer.

## CONVERSATION CONTEXT:
{conversation_summary}

## EVALUATION CONTEXT:
{evaluation_context}

## RESPONSE TYPE: {response_type.upper()}

## EVALUATION CRITERIA:

### 1. ACCURACY (0-100)
- Does the response accurately reflect the extracted data?
- Are the shipment details, contact info, and other data correctly represented?
- Is the response consistent with the customer's request?

### 2. APPROPRIATENESS (0-100)
- Is the tone professional and suitable for the situation?
- Does the response match the customer's urgency and priority level?
- Is the language clear and understandable?

### 3. COMPLETENESS (0-100)
- Does the response address all customer concerns and questions?
- Are all required fields and information included?
- Does it provide clear next steps or actions?

### 4. CONTEXT AWARENESS (0-100)
- Does the response consider the conversation history?
- Is it appropriate for the current stage of the conversation?
- Does it build on previous interactions appropriately?

### 5. PROFESSIONALISM (0-100)
- Does the response maintain professional standards?
- Is the formatting and structure appropriate?
- Are there any unprofessional elements?

## EVALUATION TASK:

Analyze the generated response against the conversation context and extracted data. Determine if the response should be sent, needs modification, or should be escalated.

### CONSIDER:
- Response type appropriateness for the situation
- Data accuracy and completeness
- Professional tone and language
- Conversation flow and context
- Customer needs and expectations

Provide a comprehensive evaluation with specific scores, issues found, and recommendations for improvement.
"""

    def _generate_evaluation_response(self, prompt: str, function_schema: Dict) -> Dict[str, Any]:
        """Generate evaluation response using LLM"""
        
        try:
            # Use the LLM to generate evaluation
            response = self.llm.invoke(
                prompt,
                tools=[function_schema],
                tool_choice={"type": "function", "function": {"name": "evaluate_response"}}
            )
            
            # Extract the evaluation result
            if response.tool_calls:
                tool_call = response.tool_calls[0]
                evaluation_result = json.loads(tool_call.function.arguments)
                return evaluation_result
            else:
                # Fallback evaluation
                return self._fallback_evaluation(prompt)
                
        except Exception as e:
            print(f"❌ LLM evaluation failed: {e}")
            return self._fallback_evaluation(prompt)

    def _fallback_evaluation(self, prompt: str) -> Dict[str, Any]:
        """Fallback evaluation when LLM fails"""
        return {
            "should_send": True,  # Default to sending
            "confidence": 0.5,
            "evaluation_score": 70,
            "accuracy_score": 70,
            "appropriateness_score": 70,
            "completeness_score": 70,
            "context_awareness_score": 70,
            "issues": ["Evaluation system unavailable"],
            "improvements": ["Manual review recommended"],
            "reasoning": "Fallback evaluation due to system issues",
            "recommended_action": "send"
        }

    def _enhance_evaluation_result(self, evaluation_result: Dict, email_data: Dict,
                                 thread_history: List[Dict], response_type: str) -> Dict[str, Any]:
        """Enhance evaluation result with metadata"""
        
        enhanced_result = evaluation_result.copy()
        
        # Add metadata
        enhanced_result.update({
            "evaluation_metadata": {
                "evaluated_at": datetime.utcnow().isoformat(),
                "email_subject": email_data.get("subject", ""),
                "email_sender": email_data.get("sender", ""),
                "thread_length": len(thread_history),
                "response_type": response_type,
                "evaluation_model": self.evaluation_model
            },
            "conversation_analysis": {
                "total_interactions": len(thread_history),
                "response_types_used": self._get_response_types_used(thread_history),
                "conversation_stage": self._determine_conversation_stage(thread_history, response_type)
            }
        })
        
        return enhanced_result

    def _get_response_types_used(self, thread_history: List[Dict]) -> List[str]:
        """Get list of response types used in the conversation"""
        response_types = []
        for entry in thread_history:
            step_results = entry.get("step_results", {})
            if "clarification_response" in step_results:
                response_types.append("clarification")
            elif "confirmation_response" in step_results:
                response_types.append("confirmation")
            elif "acknowledgment_response" in step_results:
                response_types.append("acknowledgment")
            elif "email_response" in step_results:
                response_types.append("email_response")
        return response_types

    def _determine_conversation_stage(self, thread_history: List[Dict], current_response_type: str) -> str:
        """Determine the current stage of the conversation"""
        if not thread_history:
            return "initial"
        
        response_types = self._get_response_types_used(thread_history)
        
        if "acknowledgment" in response_types:
            return "completed"
        elif "confirmation" in response_types:
            return "confirmation"
        elif "clarification" in response_types:
            return "clarification"
        else:
            return "initial"


# =====================================================
#                 🧪 Test Functions
# =====================================================

def test_response_evaluator():
    """Test the Response Evaluation Agent"""
    print("🧪 Testing Response Evaluation Agent")
    print("=" * 50)
    
    # Initialize agent
    evaluator = ResponseEvaluationAgent()
    evaluator.load_context()
    
    # Test data
    test_data = {
        "email_data": {
            "subject": "Shipping Quote Request",
            "sender": "john.smith@test.com",
            "email_text": "Hi, I need shipping rates for Shanghai to Los Angeles, 40HC container."
        },
        "thread_history": [
            {
                "email": {"subject": "Initial Request", "sender": "john.smith@test.com"},
                "step_results": {"clarification_response": {}}
            }
        ],
        "extracted_data": {
            "shipment_details": {
                "origin": "Shanghai, China",
                "destination": "Los Angeles, USA",
                "container_type": "40HC"
            }
        },
        "generated_response": {
            "subject": "Confirmation of Shipping Details",
            "response_body": "Dear John, thank you for your request. I can confirm your shipment from Shanghai to Los Angeles with 40HC container."
        },
        "customer_context": {
            "customer_info": {"name": "John Smith", "company": "Test Corp"},
            "priority": "medium"
        },
        "response_type": "confirmation"
    }
    
    # Test evaluation
    result = evaluator.process(test_data)
    
    print(f"✅ Evaluation Result:")
    print(f"   Should Send: {result.get('should_send')}")
    print(f"   Confidence: {result.get('confidence', 0):.2f}")
    print(f"   Evaluation Score: {result.get('evaluation_score', 0)}")
    print(f"   Recommended Action: {result.get('recommended_action', 'unknown')}")
    print(f"   Issues: {result.get('issues', [])}")
    print(f"   Improvements: {result.get('improvements', [])}")

if __name__ == "__main__":
    test_response_evaluator() 