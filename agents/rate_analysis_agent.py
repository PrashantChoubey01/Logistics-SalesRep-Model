"""Rate Analysis Agent: Analyzes forwarder rates and provides recommendations using LLM."""

import json
import sys
import os
from typing import Dict, Any, List

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.base_agent import BaseAgent
except ImportError:
    try:
        from base_agent import BaseAgent
    except ImportError:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from agents.base_agent import BaseAgent

class RateAnalysisAgent(BaseAgent):
    """Agent for analyzing forwarder rates and providing recommendations."""

    def __init__(self):
        super().__init__("rate_analysis_agent")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze forwarder rates and provide recommendations.
        
        Expected input:
        - forwarder_rates: List of forwarder rate quotes
        - shipment_details: Shipment information
        - customer_details: Customer information
        - thread_id: Thread identifier
        """
        forwarder_rates = input_data.get("forwarder_rates", [])
        shipment_details = input_data.get("shipment_details", {})
        customer_details = input_data.get("customer_details", {})
        thread_id = input_data.get("thread_id", "")

        if not forwarder_rates:
            return {"error": "No forwarder rates provided"}

        if not self.client:
            return {"error": "LLM client not initialized"}

        return self._analyze_rates(forwarder_rates, shipment_details, customer_details, thread_id)

    def _analyze_rates(self, forwarder_rates: List[Dict[str, Any]], shipment_details: Dict[str, Any], customer_details: Dict[str, Any], thread_id: str) -> Dict[str, Any]:
        """Analyze rates using LLM function calling."""
        try:
            function_schema = {
                "name": "analyze_forwarder_rates",
                "description": "Analyze forwarder rates and provide recommendations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "rate_comparison": {
                            "type": "object",
                            "properties": {
                                "lowest_rate": {"type": "number"},
                                "highest_rate": {"type": "number"},
                                "average_rate": {"type": "number"},
                                "rate_spread": {"type": "number"},
                                "rate_competitiveness": {"type": "string", "enum": ["high", "medium", "low"]}
                            },
                            "description": "Rate comparison analysis"
                        },
                        "recommended_forwarder": {
                            "type": "string",
                            "description": "Recommended forwarder based on analysis"
                        },
                        "recommendation_reason": {
                            "type": "string",
                            "description": "Reason for the recommendation"
                        },
                        "deal_value_estimate": {
                            "type": "number",
                            "description": "Estimated deal value in USD"
                        },
                        "profit_margin_estimate": {
                            "type": "number",
                            "description": "Estimated profit margin percentage"
                        },
                        "risk_assessment": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Risk level assessment"
                        },
                        "key_considerations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key factors to consider"
                        },
                        "sales_recommendations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Recommendations for sales team"
                        },
                        "customer_presentation": {
                            "type": "string",
                            "description": "How to present rates to customer"
                        },
                        "urgency_level": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Urgency level for sales action"
                        }
                    },
                    "required": ["rate_comparison", "recommended_forwarder", "recommendation_reason", "deal_value_estimate", "profit_margin_estimate", "risk_assessment", "key_considerations", "sales_recommendations", "customer_presentation", "urgency_level"]
                }
            }

            # Format rates for analysis
            rates_summary = self._format_rates_for_analysis(forwarder_rates)
            shipment_summary = self._format_shipment_summary(shipment_details)

            prompt = f"""
You are an expert logistics rate analyst. Analyze the forwarder rates and provide comprehensive recommendations.

SHIPMENT DETAILS:
{shipment_summary}

FORWARDER RATES:
{rates_summary}

ANALYSIS REQUIREMENTS:
1. Compare rates and identify the most competitive options
2. Assess rate competitiveness in the market
3. Calculate estimated deal value and profit margins
4. Identify the recommended forwarder with reasoning
5. Assess risk factors and considerations
6. Provide specific recommendations for sales team
7. Suggest how to present rates to customer
8. Determine urgency level for sales action

RATE COMPETITIVENESS FACTORS:
- Rate level compared to market standards
- Transit time and service quality
- Terms and conditions
- Forwarder reliability and performance
- Customer requirements alignment

PROFIT MARGIN CALCULATION:
- Consider rate levels and market conditions
- Factor in operational costs
- Account for customer relationship value
- Consider deal complexity

RISK ASSESSMENT FACTORS:
- Rate validity periods
- Forwarder reliability
- Market volatility
- Customer urgency
- Deal complexity

SALES RECOMMENDATIONS SHOULD INCLUDE:
- Which forwarder to present first
- Rate presentation strategy
- Negotiation points
- Customer communication approach
- Follow-up timing

Provide comprehensive analysis that helps the sales team make informed decisions and present rates effectively to the customer.
"""

            response = self.client.chat.completions.create(
                model=self.config.get("model_name"),
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "function",
                    "function": function_schema
                }],
                tool_choice={"type": "function", "function": {"name": function_schema["name"]}},
                temperature=0.1,
                max_tokens=800
            )

            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if not tool_calls:
                raise Exception("No tool_calls in LLM response")

            tool_args = tool_calls[0].function.arguments
            if isinstance(tool_args, str):
                tool_args = json.loads(tool_args)

            result = dict(tool_args)
            result["analysis_method"] = "llm_function_call"
            result["thread_id"] = thread_id
            result["forwarder_count"] = len(forwarder_rates)
            
            # Validate and correct result if needed
            if result.get("risk_assessment") not in ["low", "medium", "high"]:
                result["risk_assessment"] = "medium"

            if result.get("urgency_level") not in ["low", "medium", "high", "urgent"]:
                result["urgency_level"] = "medium"

            # Ensure numerical values are reasonable
            deal_value = result.get("deal_value_estimate", 0)
            if deal_value < 0:
                result["deal_value_estimate"] = 0

            profit_margin = result.get("profit_margin_estimate", 0)
            if not (0 <= profit_margin <= 100):
                result["profit_margin_estimate"] = max(0, min(100, profit_margin))

            self.logger.info(f"Rate analysis completed successfully: {result['recommended_forwarder']} (deal value: ${result['deal_value_estimate']})")
            
            return result

        except Exception as e:
            self.logger.error(f"Rate analysis failed: {e}")
            return {"error": f"Rate analysis failed: {str(e)}"}

    def _format_rates_for_analysis(self, forwarder_rates: List[Dict[str, Any]]) -> str:
        """Format forwarder rates for analysis."""
        if not forwarder_rates:
            return "No rates available"
        
        summary_parts = []
        for i, rate in enumerate(forwarder_rates, 1):
            rate_parts = []
            for key, value in rate.items():
                if value and str(value).strip():
                    rate_parts.append(f"{key}: {value}")
            if rate_parts:
                summary_parts.append(f"Forwarder {i}: {', '.join(rate_parts)}")
        
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "No valid rates available"

    def _format_shipment_summary(self, shipment_details: Dict[str, Any]) -> str:
        """Format shipment details for analysis."""
        if not shipment_details:
            return "No shipment details available"
        
        summary_parts = []
        for key, value in shipment_details.items():
            if value and str(value).strip():
                summary_parts.append(f"- {key}: {value}")
        
        if summary_parts:
            return "\n".join(summary_parts)
        else:
            return "No shipment details available"

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_rate_analysis_agent():
    print("=== Testing Rate Analysis Agent ===")
    agent = RateAnalysisAgent()
    
    if not agent.load_context():
        print("✗ Failed to load context")
        return
    
    # Test cases
    test_cases = [
        {
            "name": "Multiple Forwarder Rates",
            "forwarder_rates": [
                {
                    "forwarder": "DHL Global Forwarding",
                    "rate": 2500,
                    "currency": "USD",
                    "valid_until": "2024-01-15",
                    "transit_time": "25 days",
                    "terms": "FOB, 14 days credit"
                },
                {
                    "forwarder": "Kuehne + Nagel",
                    "rate": 2800,
                    "currency": "USD",
                    "valid_until": "2024-01-20",
                    "transit_time": "28 days",
                    "terms": "FOB, 30 days credit"
                },
                {
                    "forwarder": "DB Schenker",
                    "rate": 2300,
                    "currency": "USD",
                    "valid_until": "2024-01-10",
                    "transit_time": "30 days",
                    "terms": "FOB, 7 days credit"
                }
            ],
            "shipment_details": {
                "origin": "Shanghai",
                "destination": "Long Beach",
                "container_type": "40GP",
                "quantity": 2,
                "commodity": "electronics"
            },
            "customer_details": {
                "name": "John Smith",
                "company": "ABC Electronics"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing: {test_case['name']} ---")
        result = agent.run({
            "forwarder_rates": test_case["forwarder_rates"],
            "shipment_details": test_case["shipment_details"],
            "customer_details": test_case["customer_details"],
            "thread_id": "test-thread-1"
        })
        
        if result.get("status") == "success":
            recommended = result.get("recommended_forwarder")
            deal_value = result.get("deal_value_estimate")
            profit_margin = result.get("profit_margin_estimate")
            risk = result.get("risk_assessment")
            urgency = result.get("urgency_level")
            
            print(f"✓ Recommended Forwarder: {recommended}")
            print(f"✓ Deal Value: ${deal_value}")
            print(f"✓ Profit Margin: {profit_margin}%")
            print(f"✓ Risk Level: {risk}")
            print(f"✓ Urgency: {urgency}")
            print(f"✓ Key Considerations: {len(result.get('key_considerations', []))}")
            print(f"✓ Sales Recommendations: {len(result.get('sales_recommendations', []))}")
        else:
            print(f"✗ Test failed: {result.get('error')}")

if __name__ == "__main__":
    test_rate_analysis_agent() 