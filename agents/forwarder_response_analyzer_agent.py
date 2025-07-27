#!/usr/bin/env python3
"""
Forwarder Response Analyzer Agent - Specialized LLM Approach

This agent uses a dedicated LLM specifically for analyzing forwarder responses
and extracting key information like rates, conditions, and special requirements.

Key Features:
1. Dedicated forwarder analysis LLM
2. Rate information extraction
3. Special conditions detection
4. Forwarder communication quality assessment
5. Response categorization
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_agent import BaseAgent


class ForwarderResponseAnalyzerAgent(BaseAgent):
    """
    Forwarder Response Analyzer Agent - Specialized LLM Design
    
    This agent uses a dedicated LLM specifically for analyzing forwarder responses,
    separate from other agents to prevent confusion and improve accuracy.
    
    Design Philosophy:
    - Dedicated LLM for forwarder analysis only
    - Specialized prompts for logistics communication understanding
    - Rate and condition extraction
    - Forwarder responsiveness assessment
    - Professional communication analysis
    """

    def __init__(self):
        super().__init__("ForwarderResponseAnalyzerAgent")
        
        # Use a different model for forwarder analysis (more focused on logistics)
        self.forwarder_analysis_model = "databricks-meta-llama-3-3-70b-instruct"
        
        # Forwarder response types
        self.response_types = {
            "rate_quote": "Forwarder providing complete rate quote",
            "partial_quote": "Forwarder providing partial rate information",
            "clarification_request": "Forwarder asking for more details",
            "booking_confirmation": "Forwarder confirming booking availability",
            "problem_report": "Forwarder reporting issues or problems",
            "acknowledgment": "Forwarder acknowledging request",
            "capacity_issue": "Forwarder reporting capacity constraints",
            "rate_change": "Forwarder reporting rate changes"
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core forwarder analysis logic using specialized forwarder analysis LLM.
        
        Args:
            input_data: Dictionary containing:
                - email_data: Forwarder email content and metadata
                - thread_context: Thread analysis results
                - customer_context: Customer information
                - forwarder_context: Forwarder information
                - original_request: Original customer request
        
        Returns:
            Dictionary containing forwarder analysis results
        """
        print(f"📊 FORWARDER_ANALYZER: Starting specialized LLM forwarder analysis...")
        
        # Extract input data
        email_data = input_data.get("email_data", {})
        thread_context = input_data.get("thread_context", {})
        customer_context = input_data.get("customer_context", {})
        forwarder_context = input_data.get("forwarder_context", {})
        original_request = input_data.get("original_request", {})
        
        # Get forwarder email info
        email_text = email_data.get("email_text", "")
        subject = email_data.get("subject", "")
        sender_email = email_data.get("sender", "")
        thread_id = email_data.get("thread_id", "")
        
        print(f"📧 Forwarder Email: {subject[:50]}...")
        print(f"👤 Forwarder: {sender_email}")
        print(f"🧵 Thread ID: {thread_id}")
        
        # Use specialized forwarder analysis LLM
        analysis_result = self._specialized_forwarder_analysis(
            email_text, subject, sender_email, thread_context,
            customer_context, forwarder_context, original_request
        )
        
        print(f"✅ FORWARDER_ANALYZER: Specialized LLM analysis complete")
        print(f"   Response Type: {analysis_result['response_type']}")
        print(f"   Rate Provided: {analysis_result.get('rate_info', {}).get('has_rates', False)}")
        print(f"   Quality Score: {analysis_result.get('communication_quality', 0):.2f}")
        
        return analysis_result

    def _specialized_forwarder_analysis(self, email_text: str, subject: str, sender_email: str,
                                      thread_context: Dict, customer_context: Dict,
                                      forwarder_context: Dict, original_request: Dict) -> Dict[str, Any]:
        """
        Use specialized forwarder analysis LLM for forwarder response analysis.
        """
        if not self.client:
            return self._fallback_forwarder_analysis(email_text, subject, sender_email)
        
        # Prepare context for forwarder analysis LLM
        forwarder_info = self._prepare_forwarder_info(forwarder_context, sender_email)
        customer_summary = self._prepare_customer_summary(customer_context)
        original_request_summary = self._prepare_original_request_summary(original_request)
        
        # Create specialized forwarder analysis prompt
        prompt = self._create_forwarder_analysis_prompt(
            email_text, subject, sender_email, thread_context,
            forwarder_info, customer_summary, original_request_summary
        )
        
        # Define specialized function schema for forwarder analysis
        function_schema = {
            "name": "analyze_forwarder_response",
            "description": "Analyze forwarder response using specialized forwarder analysis logic",
            "parameters": {
                "type": "object",
                "properties": {
                    "response_type": {
                        "type": "string",
                        "enum": list(self.response_types.keys()),
                        "description": "The type of forwarder response"
                    },
                    "rate_info": {
                        "type": "object",
                        "properties": {
                            "has_rates": {"type": "boolean"},
                            "total_rate": {"type": "string"},
                            "currency": {"type": "string"},
                            "rate_breakdown": {"type": "object"},
                            "validity_period": {"type": "string"},
                            "transit_time": {"type": "string"}
                        },
                        "description": "Rate information if provided"
                    },
                    "special_conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Special conditions or requirements"
                    },
                    "communication_quality": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Quality of forwarder communication (0.0 to 1.0)"
                    },
                    "responsiveness": {
                        "type": "string",
                        "enum": ["excellent", "good", "average", "poor"],
                        "description": "Forwarder responsiveness level"
                    },
                    "issues_detected": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Issues or problems reported by forwarder"
                    },
                    "next_steps": {
                        "type": "string",
                        "description": "Recommended next steps based on response"
                    },
                    "escalation_needed": {
                        "type": "boolean",
                        "description": "Whether response requires escalation"
                    },
                    "escalation_reason": {
                        "type": "string",
                        "description": "Reason for escalation if needed"
                    },
                    "confidence": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "description": "Confidence in analysis"
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Brief explanation of the analysis"
                    }
                },
                "required": ["response_type", "communication_quality", "responsiveness", "next_steps", "confidence", "reasoning"]
            }
        }
        
        # Get specialized LLM forwarder analysis
        llm_result = self._generate_forwarder_analysis_response(prompt, function_schema)
        
        if "error" in llm_result:
            print(f"⚠️ Specialized LLM forwarder analysis failed, using fallback: {llm_result['error']}")
            return self._fallback_forwarder_analysis(email_text, subject, sender_email)
        
        # Enhance result with additional context
        enhanced_result = self._enhance_forwarder_analysis_result(
            llm_result, email_text, subject, sender_email, thread_context
        )
        
        return enhanced_result

    def _create_forwarder_analysis_prompt(self, email_text: str, subject: str, sender_email: str,
                                        thread_context: Dict, forwarder_info: str,
                                        customer_summary: str, original_request_summary: str) -> str:
        """
        Create specialized prompt for forwarder analysis LLM.
        """
        prompt = f"""
You are a specialized forwarder response analysis expert for a logistics CRM system. Your ONLY job is to analyze forwarder responses and extract key information.

## FORWARDER EMAIL:
Subject: {subject}
Sender: {sender_email}
Content: {email_text}

## FORWARDER INFORMATION:
{forwarder_info}

## CUSTOMER SUMMARY:
{customer_summary}

## ORIGINAL REQUEST:
{original_request_summary}

## THREAD CONTEXT:
Thread State: {thread_context.get('thread_state', 'unknown')}
Conversation Stage: {thread_context.get('conversation_stage', 'unknown')}

## FORWARDER ANALYSIS TASK:

Analyze this forwarder response and determine:

### RESPONSE TYPE:
- rate_quote: Forwarder providing complete rate quote
- partial_quote: Forwarder providing partial rate information
- clarification_request: Forwarder asking for more details
- booking_confirmation: Forwarder confirming booking availability
- problem_report: Forwarder reporting issues or problems
- acknowledgment: Forwarder acknowledging request
- capacity_issue: Forwarder reporting capacity constraints
- rate_change: Forwarder reporting rate changes

### RATE INFORMATION EXTRACTION:
If rates are provided, extract:
- Total rate amount and currency
- Rate breakdown (ocean freight, THC, documentation, etc.)
- Validity period
- Transit time
- Special charges or fees

### SPECIAL CONDITIONS:
Look for:
- Special handling requirements
- Documentation requirements
- Timing constraints
- Capacity limitations
- Rate conditions or restrictions

### COMMUNICATION QUALITY ASSESSMENT:
Evaluate:
- Professionalism of communication
- Completeness of information
- Clarity of response
- Responsiveness to original request
- Helpfulness of information provided

### ISSUES DETECTION:
Identify:
- Capacity problems
- Rate changes
- Documentation issues
- Timing conflicts
- Special requirements that may cause delays

### ESCALATION TRIGGERS:
Escalate if:
- Complex issues requiring human intervention
- Rate changes that need approval
- Capacity problems requiring alternatives
- Special requirements needing coordination
- Communication quality is poor

## YOUR TASK:
Analyze this forwarder response comprehensively, considering all the above factors. Provide reasoning for your analysis and assess confidence level.
"""
        return prompt

    def _prepare_forwarder_info(self, forwarder_context: Dict, sender_email: str) -> str:
        """
        Prepare forwarder information for forwarder analysis LLM.
        """
        if not forwarder_context:
            return f"Forwarder email: {sender_email}"
        
        forwarder_info = forwarder_context.get("forwarder_info", {})
        if not forwarder_info:
            return f"Forwarder email: {sender_email}"
        
        info_parts = [f"Forwarder Information:"]
        info_parts.append(f"  Name: {forwarder_info.get('name', 'Unknown')}")
        info_parts.append(f"  Email: {sender_email}")
        info_parts.append(f"  Specialties: {forwarder_info.get('specialties', 'Unknown')}")
        info_parts.append(f"  Regions: {forwarder_info.get('regions', 'Unknown')}")
        
        # Add performance metrics if available
        performance = forwarder_context.get("performance", {})
        if performance:
            info_parts.append(f"  Response Time: {performance.get('avg_response_time', 'Unknown')}")
            info_parts.append(f"  Success Rate: {performance.get('success_rate', 'Unknown')}")
        
        return "\n".join(info_parts)

    def _prepare_customer_summary(self, customer_context: Dict) -> str:
        """
        Prepare customer summary for forwarder analysis LLM.
        """
        if not customer_context:
            return "Customer information not available."
        
        customer_info = customer_context.get("customer_info", {})
        if not customer_info:
            return "Customer information not available."
        
        summary_parts = ["Customer Summary:"]
        summary_parts.append(f"  Name: {customer_info.get('name', 'Unknown')}")
        summary_parts.append(f"  Company: {customer_info.get('company', 'Unknown')}")
        summary_parts.append(f"  Priority: {customer_context.get('priority', 'standard')}")
        
        return "\n".join(summary_parts)

    def _prepare_original_request_summary(self, original_request: Dict) -> str:
        """
        Prepare original request summary for forwarder analysis LLM.
        """
        if not original_request:
            return "Original request information not available."
        
        summary_parts = ["Original Request:"]
        
        # Extract key information
        origin = original_request.get("origin", "Unknown")
        destination = original_request.get("destination", "Unknown")
        container_type = original_request.get("container_type", "Unknown")
        commodity = original_request.get("commodity", "Unknown")
        
        summary_parts.append(f"  Route: {origin} to {destination}")
        summary_parts.append(f"  Container: {container_type}")
        summary_parts.append(f"  Commodity: {commodity}")
        
        # Add special requirements
        special_req = original_request.get("special_requirements", [])
        if special_req:
            summary_parts.append(f"  Special Requirements: {', '.join(special_req)}")
        
        return "\n".join(summary_parts)

    def _enhance_forwarder_analysis_result(self, llm_result: Dict, email_text: str,
                                         subject: str, sender_email: str,
                                         thread_context: Dict) -> Dict[str, Any]:
        """
        Enhance LLM result with additional forwarder analysis context and metadata.
        """
        # Add metadata
        enhanced_result = {
            **llm_result,
            "forwarder_metadata": {
                "email_subject": subject,
                "sender_email": sender_email,
                "word_count": len(email_text.split()),
                "analyzed_at": datetime.utcnow().isoformat()
            },
            "thread_context": {
                "thread_state": thread_context.get("thread_state", "unknown"),
                "conversation_stage": thread_context.get("conversation_stage", "unknown"),
                "thread_length": thread_context.get("thread_length", 0)
            },
            "analysis_details": {
                "reasoning": llm_result.get("reasoning", ""),
                "analysis_method": "specialized_forwarder_llm",
                "confidence_factors": self._extract_forwarder_confidence_factors(llm_result)
            }
        }
        
        # Add escalation details if needed
        if llm_result.get("escalation_needed", False):
            enhanced_result["escalation_details"] = {
                "reason": llm_result.get("escalation_reason", "Unknown"),
                "priority": "high" if llm_result.get("communication_quality", 0) < 0.5 else "medium",
                "recommended_action": self._get_forwarder_escalation_action(llm_result)
            }
        
        return enhanced_result

    def _extract_forwarder_confidence_factors(self, llm_result: Dict) -> List[str]:
        """
        Extract factors that influenced forwarder analysis confidence.
        """
        factors = []
        
        if llm_result.get("confidence", 0) >= 0.8:
            factors.append("High confidence - clear forwarder response")
        elif llm_result.get("confidence", 0) >= 0.6:
            factors.append("Medium confidence - some uncertainty in analysis")
        else:
            factors.append("Low confidence - unclear forwarder response")
        
        if llm_result.get("communication_quality", 0) >= 0.8:
            factors.append("High communication quality")
        elif llm_result.get("communication_quality", 0) < 0.5:
            factors.append("Poor communication quality")
        
        if llm_result.get("responsiveness") == "excellent":
            factors.append("Excellent responsiveness")
        elif llm_result.get("responsiveness") == "poor":
            factors.append("Poor responsiveness")
        
        if llm_result.get("rate_info", {}).get("has_rates", False):
            factors.append("Rate information provided")
        
        return factors

    def _get_forwarder_escalation_action(self, llm_result: Dict) -> str:
        """
        Determine recommended action for forwarder escalation.
        """
        if llm_result.get("communication_quality", 0) < 0.3:
            return "Immediate human review - poor communication quality"
        elif llm_result.get("responsiveness") == "poor":
            return "Human review - poor responsiveness"
        elif llm_result.get("escalation_reason", "").startswith("Complex"):
            return "Human coordination required for complex issues"
        else:
            return "Standard forwarder escalation process"

    def _fallback_forwarder_analysis(self, email_text: str, subject: str, sender_email: str) -> Dict[str, Any]:
        """
        Fallback forwarder analysis when specialized LLM is not available.
        """
        print("⚠️ Using fallback forwarder analysis (Specialized LLM not available)")
        
        # Simple fallback logic
        content_lower = email_text.lower()
        subject_lower = subject.lower()
        
        # Basic response type detection
        if "rate" in content_lower or "quote" in content_lower or "price" in content_lower:
            response_type = "rate_quote"
        elif "clarification" in content_lower or "details" in content_lower:
            response_type = "clarification_request"
        elif "confirm" in content_lower or "booking" in content_lower:
            response_type = "booking_confirmation"
        elif "problem" in content_lower or "issue" in content_lower:
            response_type = "problem_report"
        else:
            response_type = "acknowledgment"
        
        # Basic rate detection
        has_rates = any(word in content_lower for word in ["usd", "eur", "rate", "price", "cost"])
        
        return {
            "response_type": response_type,
            "rate_info": {
                "has_rates": has_rates,
                "total_rate": "Not extracted",
                "currency": "Unknown",
                "rate_breakdown": {},
                "validity_period": "Unknown",
                "transit_time": "Unknown"
            },
            "special_conditions": [],
            "communication_quality": 0.6,  # Default quality
            "responsiveness": "average",
            "issues_detected": [],
            "next_steps": "Standard follow-up process",
            "escalation_needed": False,
            "escalation_reason": "",
            "confidence": 0.5,  # Low confidence for fallback
            "reasoning": "Fallback forwarder analysis due to specialized LLM unavailability",
            "analysis_method": "fallback"
        }

    def _generate_forwarder_analysis_response(self, prompt: str, function_schema: Dict) -> Dict[str, Any]:
        """
        Generate response using specialized forwarder analysis LLM.
        """
        if not self.client:
            return {"error": "Specialized forwarder analysis LLM client not available"}
        
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
            
            response = self.client.chat.completions.create(
                model=self.forwarder_analysis_model,  # Use specialized model
                messages=[{"role": "user", "content": prompt}],
                tools=tools,
                tool_choice=tool_choice,
                temperature=0.1,  # Low temperature for consistent analysis
                max_tokens=800
            )
            
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls:
                import json
                return json.loads(tool_calls[0].function.arguments)
            else:
                return {"error": "No tool calls in response"}
                
        except Exception as e:
            return {"error": f"Specialized forwarder analysis LLM call failed: {str(e)}"}


# =====================================================
#                 🧪 Test Functions
# =====================================================

def test_forwarder_analyzer():
    """Test the Specialized LLM-based Forwarder Response Analyzer Agent"""
    print("🧪 Testing Specialized LLM-based Forwarder Response Analyzer Agent")
    print("=" * 60)
    
    # Initialize agent
    analyzer = ForwarderResponseAnalyzerAgent()
    analyzer.load_context()
    
    # Test scenarios
    test_cases = [
        {
            "name": "Complete Rate Quote",
            "email_data": {
                "email_text": """Dear SeaRates Team,

Thank you for your rate request for Shanghai to Los Angeles shipment.

Please find our competitive quote below:

Rate Details:
- Ocean Freight: USD 2,800 per 40HC
- THC Origin: USD 80
- THC Destination: USD 120
- Documentation: USD 35
- Total: USD 3,035

Validity: Valid until Friday, 15th December 2024
Transit Time: 16 days

Special Requirements:
- Temperature controlled container required
- Customs clearance assistance needed

Please let us know if you need any clarification.

Best regards,
Logistics Solutions Ltd.""",
                "subject": "Rate Quote - Shanghai to Los Angeles",
                "sender": "rates@logistics-solutions.com",
                "thread_id": "thread_123"
            },
            "thread_context": {
                "thread_state": "first_response",
                "conversation_stage": "rate_quote"
            },
            "customer_context": {
                "customer_info": {
                    "name": "John Smith",
                    "company": "Tech Solutions Inc."
                },
                "priority": "high"
            },
            "forwarder_context": {
                "forwarder_info": {
                    "name": "Logistics Solutions Ltd.",
                    "specialties": "Ocean Freight, Temperature Control",
                    "regions": "Asia-Pacific, North America"
                }
            },
            "original_request": {
                "origin": "Shanghai",
                "destination": "Los Angeles",
                "container_type": "40HC",
                "commodity": "Electronics",
                "special_requirements": ["Temperature Control"]
            }
        },
        {
            "name": "Clarification Request",
            "email_data": {
                "email_text": """Dear SeaRates Team,

Thank you for your rate request. We need some clarification before we can provide accurate rates:

1. What is the exact commodity being shipped?
2. Are there any special handling requirements?
3. Do you need door-to-door service or port-to-port only?
4. What is the preferred sailing schedule?

Please provide these details so we can give you the most competitive rates.

Best regards,
Global Shipping Solutions""",
                "subject": "Clarification Required - Rate Request",
                "sender": "clarifications@global-shipping.com",
                "thread_id": "thread_456"
            },
            "thread_context": {
                "thread_state": "first_response",
                "conversation_stage": "clarification"
            },
            "customer_context": {
                "customer_info": {
                    "name": "Jane Doe",
                    "company": "Global Imports Ltd."
                }
            },
            "forwarder_context": {
                "forwarder_info": {
                    "name": "Global Shipping Solutions",
                    "specialties": "Ocean Freight, Project Cargo",
                    "regions": "Global"
                }
            },
            "original_request": {
                "origin": "Rotterdam",
                "destination": "New York",
                "container_type": "40HC",
                "commodity": "Machinery"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📊 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        result = analyzer.process(test_case)
        
        print(f"✅ Response Type: {result.get('response_type', 'unknown')}")
        print(f"✅ Communication Quality: {result.get('communication_quality', 0):.2f}")
        print(f"✅ Responsiveness: {result.get('responsiveness', 'unknown')}")
        print(f"✅ Has Rates: {result.get('rate_info', {}).get('has_rates', False)}")
        print(f"✅ Escalation: {result.get('escalation_needed', False)}")
        print(f"✅ Confidence: {result.get('confidence', 0):.2f}")
        
        if result.get('rate_info', {}).get('has_rates', False):
            rate_info = result['rate_info']
            print(f"💰 Rate Info:")
            print(f"   Total: {rate_info.get('total_rate', 'N/A')}")
            print(f"   Currency: {rate_info.get('currency', 'N/A')}")
            print(f"   Transit Time: {rate_info.get('transit_time', 'N/A')}")
        
        if result.get('special_conditions'):
            print(f"⚠️ Special Conditions: {', '.join(result['special_conditions'])}")
        
        if result.get('issues_detected'):
            print(f"🚨 Issues: {', '.join(result['issues_detected'])}")
        
        if result.get('next_steps'):
            print(f"📋 Next Steps: {result['next_steps']}")
        
        if result.get('reasoning'):
            print(f"🧠 Reasoning: {result['reasoning'][:100]}...")
    
    print(f"\n🎉 All tests completed!")


if __name__ == "__main__":
    test_forwarder_analyzer() 