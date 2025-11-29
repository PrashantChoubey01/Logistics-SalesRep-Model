"""Country Extractor Agent: Extracts country from port code and recommends nearby countries using LLM and country_converter."""

import json
from typing import Dict, Any, List
from base_agent import BaseAgent
import country_converter as coco

# Simple region clusters for "nearby" recommendations
REGION_GROUPS = {
    "North America": ["US", "CA", "MX"],
    "Central America": ["GT", "HN", "SV", "NI", "CR", "PA", "BZ"],
    "Caribbean": ["CU", "JM", "DO", "HT", "TT", "BS", "BB", "AG", "KN", "LC", "VC", "GD", "DM"],
    "South America": ["BR", "AR", "CO", "CL", "PE", "VE", "EC", "BO", "PY", "UY", "GF", "SR", "GY"],
    "Europe": [
        "GB", "IE", "FR", "DE", "NL", "BE", "LU", "CH", "AT", "IT", "ES", "PT", "NO", "SE", "DK", "FI",
        "PL", "CZ", "SK", "HU", "RO", "BG", "GR", "SI", "HR", "RS", "BA", "ME", "MK", "AL", "UA", "BY", "MD", "LT", "LV", "EE"
    ],
    "Russia & CIS": ["RU", "KZ", "UZ", "TM", "KG", "TJ", "AZ", "AM", "GE", "MD", "BY"],
    "Middle East": ["AE", "SA", "QA", "KW", "OM", "BH", "IQ", "IR", "JO", "LB", "SY", "YE", "TR", "IL", "PS"],
    "North Africa": ["MA", "DZ", "TN", "LY", "EG", "SD"],
    "West Africa": ["NG", "GH", "CI", "SN", "GM", "SL", "LR", "GW", "BJ", "TG", "BF", "NE", "ML", "GN", "MR", "CV"],
    "Central Africa": ["CM", "CF", "TD", "GQ", "GA", "CG", "CD", "ST"],
    "East Africa": ["ET", "KE", "UG", "TZ", "RW", "BI", "DJ", "ER", "SO", "SC", "KM", "MG", "MU"],
    "Southern Africa": ["ZA", "BW", "NA", "ZM", "ZW", "MZ", "AO", "MW", "LS", "SZ"],
    "South Asia": ["IN", "PK", "BD", "LK", "NP", "BT", "MV", "AF"],
    "East Asia": ["CN", "JP", "KR", "MN", "HK", "MO", "TW"],
    "Southeast Asia": ["SG", "MY", "TH", "VN", "ID", "PH", "KH", "LA", "MM", "BN", "TL"],
    "Oceania": ["AU", "NZ", "PG", "FJ", "SB", "VU", "NC", "PF", "WS", "TO", "TV", "KI", "FM", "MH", "PW", "NR"],
    "Arctic": ["GL", "SJ"],
    "Antarctica": ["AQ"]
}

def get_region(country_code: str) -> str:
    """Get region for a country code"""
    for region, codes in REGION_GROUPS.items():
        if country_code in codes:
            return region
    return "Other"

def recommend_nearby_countries(country_code: str, top_n: int = 3) -> List[str]:
    """Recommend nearby countries based on region"""
    region = get_region(country_code)
    codes_in_region = REGION_GROUPS.get(region, [])
    
    # Exclude the original country
    nearby = [cc for cc in codes_in_region if cc != country_code]
    
    # If not enough, add from other regions
    if len(nearby) < top_n:
        all_codes = list(set(sum(REGION_GROUPS.values(), [])))
        others = [cc for cc in all_codes if cc not in codes_in_region and cc != country_code]
        nearby += others[:(top_n - len(nearby))]
    
    # Convert to country names
    return [coco.convert(names=cc, to='name_short', not_found=None) for cc in nearby[:top_n] if coco.convert(names=cc, to='name_short', not_found=None)]

class CountryExtractorAgent(BaseAgent):
    """Agent for extracting country from port code and recommending nearby countries using LLM and fallback logic."""

    def __init__(self):
        super().__init__("country_extractor_agent")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract country from port code and provide recommendations.
        
        Expected input:
        - port_code: Port code (e.g., "USLGB", "CNSHA") (required)
        - include_recommendations: Whether to include nearby countries (optional, default: True)
        """
        port_code = input_data.get("port_code", "").strip().upper()
        include_recommendations = input_data.get("include_recommendations", True)
        
        if not port_code:
            return {"error": "No port code provided"}
        
        if len(port_code) < 2:
            return {"error": "Port code must be at least 2 characters long"}
        
        # Extract country code (first 2 characters)
        country_code = port_code[:2]
        
        # Try LLM enhancement first if available
        if self.client:
            try:
                llm_result = self._llm_country_extraction(port_code, country_code)
                if llm_result.get("success"):
                    # Add recommendations if requested
                    if include_recommendations:
                        llm_result["recommended_countries"] = recommend_nearby_countries(country_code)
                    return llm_result
                else:
                    self.logger.info("LLM extraction failed, using fallback")
            except Exception as e:
                self.logger.warning(f"LLM country extraction failed: {e}, using fallback")
        
        # Fallback to country_converter
        return self._fallback_country_extraction(port_code, country_code, include_recommendations)

    def _llm_country_extraction(self, port_code: str, country_code: str) -> Dict[str, Any]:
        """Use LLM to extract and validate country information"""
        try:
            function_schema = {
                "name": "extract_country_info",
                "description": "Extract country information from port code and validate it",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "country_code": {
                            "type": "string",
                            "description": "2-letter ISO country code"
                        },
                        "country_name": {
                            "type": "string",
                            "description": "Full country name"
                        },
                        "port_name": {
                            "type": "string",
                            "description": "Port name if recognizable from code"
                        },
                        "region": {
                            "type": "string",
                            "description": "Geographic region of the country"
                        },
                        "confidence": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 1.0,
                            "description": "Confidence in country identification (0.0 to 1.0)"
                        },
                        "is_valid_port": {
                            "type": "boolean",
                            "description": "Whether this appears to be a valid port code"
                        },
                        "additional_info": {
                            "type": "string",
                            "description": "Any additional relevant information about the port or country"
                        }
                    },
                    "required": ["country_code", "country_name", "port_name", "region", "confidence", "is_valid_port", "additional_info"]
                }
            }

            prompt = f"""
You are an expert in international shipping and port codes. Analyze this port code and extract country information.

PORT CODE: "{port_code}"
EXTRACTED COUNTRY CODE: "{country_code}"

Port codes typically follow the format: [2-letter country code][3-letter port code]
Examples:
- USLGB = US (United States) + LGB (Long Beach)
- CNSHA = CN (China) + SHA (Shanghai)
- DEHAM = DE (Germany) + HAM (Hamburg)
- SGSIN = SG (Singapore) + SIN (Singapore)

Analyze the port code and provide:
1. Validate the country code
2. Provide the full country name
3. Identify the port name if possible
4. Determine the geographic region
5. Assess confidence in identification
6. Determine if this is a valid port code format

Be accurate and provide high confidence only for well-known ports.
"""

            # Use OpenAI client for function calling
            client = self.get_openai_client()
            if not client:
                return {"error": "OpenAI client not available for function calling"}
            
            response = client.chat.completions.create(
                model=self.config.get("model_name"),
                messages=[{"role": "user", "content": prompt}],
                tools=[{
                    "type": "function",
                    "function": function_schema
                }],
                tool_choice={"type": "function", "function": {"name": function_schema["name"]}},
                temperature=0.1,
                max_tokens=400
            )

            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if not tool_calls:
                raise Exception("No tool_calls in LLM response")

            tool_args = tool_calls[0].function.arguments
            if isinstance(tool_args, str):
                tool_args = json.loads(tool_args)

            result = dict(tool_args)
            
            # Add metadata
            result["original_port_code"] = port_code
            result["extraction_method"] = "llm_function_call"
            result["success"] = True
            
            # Validate country code with country_converter
            cc_country_name = coco.convert(names=country_code, to='name_short', not_found=None)
            if cc_country_name and cc_country_name != country_code:
                result["country_converter_validation"] = {
                    "matches_llm": cc_country_name.lower() == result["country_name"].lower(),
                    "cc_country_name": cc_country_name
                }
            
            self.logger.info(f"LLM country extraction successful: {country_code} -> {result['country_name']}")
            return result

        except Exception as e:
            raise Exception(f"LLM country extraction failed: {str(e)}")

    def _fallback_country_extraction(self, port_code: str, country_code: str, include_recommendations: bool) -> Dict[str, Any]:
        """Fallback country extraction using country_converter"""
        
        # Use country_converter to get country name
        country_name = coco.convert(names=country_code, to='name_short', not_found=None)
        
        if not country_name or country_name == country_code:
            # Country code not found
            result = {
                "country_code": country_code,
                "country_name": None,
                "port_name": port_code[2:] if len(port_code) > 2 else None,
                "region": "Unknown",
                "confidence": 0.3,
                "is_valid_port": False,
                "success": False,
                "error": f"Unknown country code: {country_code}",
                "original_port_code": port_code,
                "extraction_method": "country_converter_fallback"
            }
            
            if include_recommendations:
                # Still try to provide some recommendations
                result["recommended_countries"] = recommend_nearby_countries(country_code)
            
            return result
        
        # Successful extraction
        region = get_region(country_code)
        
        result = {
            "country_code": country_code,
            "country_name": country_name,
            "port_name": port_code[2:] if len(port_code) > 2 else None,
            "region": region,
            "confidence": 0.9,  # High confidence for country_converter matches
            "is_valid_port": True,
            "success": True,
            "original_port_code": port_code,
            "extraction_method": "country_converter_fallback",
            "additional_info": f"Country extracted from first 2 characters of port code"
        }
        
        if include_recommendations:
            result["recommended_countries"] = recommend_nearby_countries(country_code)
        
        return result

# =====================================================
#                 🔁 Test Harness
# =====================================================
def test_country_extractor_agent():
    """Test country extractor agent with various port codes"""
    print("=== Testing Country Extractor Agent (Updated) ===")
    
    agent = CountryExtractorAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}, Has LLM: {bool(agent.client)}")

    test_cases = [
        {
            "name": "US Port - Long Beach",
            "port_code": "USLGB",
            "expected_country": "United States"
        },
        {
            "name": "China Port - Shanghai",
            "port_code": "CNSHA",
            "expected_country": "China"
        },
        {
            "name": "India Port - Mumbai",
            "port_code": "INBOM",
            "expected_country": "India"
        },
        {
            "name": "Germany Port - Hamburg",
            "port_code": "DEHAM",
            "expected_country": "Germany"
        },
        {
            "name": "Singapore Port",
            "port_code": "SGSIN",
            "expected_country": "Singapore"
        },
        {
            "name": "UAE Port - Dubai",
            "port_code": "AEDXB",
            "expected_country": "United Arab Emirates"
        },
        {
            "name": "Unknown Country Code",
            "port_code": "ZZZZZ",
            "expected_country": None
        },
        {
            "name": "Short Port Code",
            "port_code": "U",
            "expected_country": None
        },
        {
            "name": "Empty Port Code",
            "port_code": "",
            "expected_country": None
        }
    ]

    results = {"successful": 0, "failed": 0, "total": len(test_cases)}
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Port Code: {test_case['port_code']}")
        print(f"Expected Country: {test_case['expected_country']}")
        
        result = agent.run({
            "port_code": test_case["port_code"],
            "include_recommendations": True
        })
        
        if result.get("status") == "success":
            country_code = result.get("country_code")
            country_name = result.get("country_name")
            port_name = result.get("port_name")
            region = result.get("region")
            confidence = result.get("confidence", 0.0)
            is_valid = result.get("is_valid_port", False)
            method = result.get("extraction_method", "unknown")
            recommendations = result.get("recommended_countries", [])
            
            print(f"✓ Country Code: {country_code}")
            print(f"✓ Country Name: {country_name}")
            print(f"✓ Port Name: {port_name}")
            print(f"✓ Region: {region}")
            print(f"✓ Confidence: {confidence:.2f}")
            print(f"✓ Valid Port: {is_valid}")
            print(f"✓ Method: {method}")
            print(f"✓ Recommendations: {recommendations[:3]}")  # Show first 3
            
            # Check if result matches expectation
            if test_case["expected_country"]:
                if country_name and test_case["expected_country"].lower() in country_name.lower():
                    print("✅ CORRECT")
                    results["successful"] += 1
                else:
                    print("❌ INCORRECT")
                    results["failed"] += 1
            else:
                # For error cases, check if properly handled
                if not result.get("success", True):
                    print("✅ CORRECTLY HANDLED ERROR")
                    results["successful"] += 1
                else:
                    print("❌ SHOULD HAVE FAILED")
                    results["failed"] += 1
        else:
            print(f"✗ Error: {result.get('error')}")
            if not test_case["expected_country"]:
                print("✅ CORRECTLY HANDLED ERROR")
                results["successful"] += 1
            else:
                print("❌ UNEXPECTED ERROR")
                results["failed"] += 1
    
    success_rate = results["successful"] / results["total"] * 100
    print(f"\n📊 Results: {results['successful']}/{results['total']} ({success_rate:.1f}% success rate)")

def test_batch_processing():
    """Test batch processing of multiple port codes"""
    print("\n=== Testing Batch Processing ===")
    
    agent = CountryExtractorAgent()
    agent.load_context()
    
    port_codes = ["USLGB", "CNSHA", "DEHAM", "SGSIN", "AEDXB", "INBOM", "GBLON", "FRLEH", "NLRTM", "BEANR"]
    
    print(f"Processing {len(port_codes)} port codes...")
    
    results = []
    for port_code in port_codes:
        result = agent.run({"port_code": port_code, "include_recommendations": False})
        results.append({
            "port_code": port_code,
            "success": result.get("status") == "success",
            "country": result.get("country_name", "Unknown"),
            "method": result.get("extraction_method", "unknown")
        })
    
    print("\n📊 Batch Results:")
    for result in results:
        status = "✓" if result["success"] else "✗"
        print(f"  {status} {result['port_code']} -> {result['country']} ({result['method']})")
    
    successful = sum(1 for r in results if r["success"])
    print(f"\nSuccess rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")

def test_recommendations():
    """Test country recommendations functionality"""
    print("\n=== Testing Country Recommendations ===")
    
    agent = CountryExtractorAgent()
    agent.load_context()
    
    test_ports = ["USLGB", "CNSHA", "DEHAM", "AEDXB", "SGSIN"]
    
    for port_code in test_ports:
        print(f"\n--- Recommendations for {port_code} ---")
        result = agent.run({"port_code": port_code, "include_recommendations": True})
        
        if result.get("status") == "success":
            country = result.get("country_name", "Unknown")
            region = result.get("region", "Unknown")
            recommendations = result.get("recommended_countries", [])
            
            print(f"✓ Country: {country}")
            print(f"✓ Region: {region}")
            print(f"✓ Nearby countries: {recommendations}")
        else:
            print(f"✗ Error: {result.get('error')}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Testing Edge Cases ===")
    
    agent = CountryExtractorAgent()
    agent.load_context()
    
    edge_cases = [
        {"name": "Empty string", "port_code": ""},
        {"name": "Single character", "port_code": "U"},
        {"name": "Numbers", "port_code": "12345"},
        {"name": "Special characters", "port_code": "US@#$"},
        {"name": "Lowercase", "port_code": "uslgb"},
        {"name": "Mixed case", "port_code": "UsLgB"},
        {"name": "Very long code", "port_code": "USLONGBEACHPORT"},
        {"name": "Invalid country", "port_code": "ZZABC"},
        {"name": "Whitespace", "port_code": "  USLGB  "},
    ]
    
    for case in edge_cases:
        print(f"\n--- {case['name']}: '{case['port_code']}' ---")
        result = agent.run({"port_code": case["port_code"]})
        
        if result.get("status") == "success":
            if result.get("success", False):
                print(f"✓ Country: {result.get('country_name')}")
                print(f"✓ Confidence: {result.get('confidence', 0):.2f}")
            else:
                print(f"✓ Handled gracefully: {result.get('error', 'No error message')}")
        else:
            print(f"✓ Error handled: {result.get('error')}")

def test_llm_vs_fallback():
    """Compare LLM vs fallback performance"""
    print("\n=== Testing LLM vs Fallback Performance ===")
    
    agent = CountryExtractorAgent()
    agent.load_context()
    
    if not agent.client:
        print("✗ Cannot compare - LLM client not available")
        return
    
    test_ports = ["USLGB", "CNSHA", "DEHAM", "SGSIN", "AEDXB"]
    
    print("Port Code | LLM Result | Fallback Result | Match")
    print("-" * 60)
    
    for port_code in test_ports:
        # Test with LLM
        llm_result = agent.run({"port_code": port_code})
        
        # Simulate fallback by temporarily disabling LLM
        original_client = agent.client
        agent.client = None
        fallback_result = agent.run({"port_code": port_code})
        agent.client = original_client
        
        llm_country = llm_result.get("country_name", "Error") if llm_result.get("status") == "success" else "Error"
        fallback_country = fallback_result.get("country_name", "Error") if fallback_result.get("status") == "success" else "Error"
        
        match = "✓" if llm_country == fallback_country else "✗"
        
        print(f"{port_code:8} | {llm_country:10} | {fallback_country:15} | {match}")

def run_all_tests():
    """Run all test suites"""
    print("🚀 Starting Country Extractor Agent Tests")
    print("=" * 50)
    
    try:
        test_country_extractor_agent()
        test_batch_processing()
        test_recommendations()
        test_edge_cases()
        test_llm_vs_fallback()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
