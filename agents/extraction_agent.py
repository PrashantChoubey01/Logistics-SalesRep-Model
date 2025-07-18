"""Enhanced Extraction Agent with LLM function calling"""

import os
import sys
import json
import logging

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class ExtractionAgent(BaseAgent):
    """Enhanced agent for extracting shipment information from emails"""

    def __init__(self):
        super().__init__("extraction_agent")

    def process(self, input_data):
        """Extract shipment information from email with thread context support"""
        email_text = input_data.get("email_text", "")
        subject = input_data.get("subject", "")
        message_thread = input_data.get("message_thread", [])
        previous_extraction = input_data.get("previous_extraction", {})

        if not email_text:
            return {"error": "No email text provided"}

        if not self.client:
            return {"error": "LLM client not initialized"}

        return self._extract_with_llm(subject, email_text, message_thread, previous_extraction)

    def _extract_with_llm(self, subject, email_text, message_thread=None, previous_extraction=None):
        """Use LLM with function calling for extraction with complete thread context"""
        if message_thread is None:
            message_thread = []
        if previous_extraction is None:
            previous_extraction = {}
        
        # Build complete thread text by concatenating all messages
        complete_thread_text = ""
        if message_thread and len(message_thread) > 1:
            complete_thread_text = "COMPLETE EMAIL THREAD:\n\n"
            for i, msg in enumerate(message_thread):
                complete_thread_text += f"Email {i+1}:\nFrom: {msg.get('sender', 'Unknown')}\nSubject: {msg.get('subject', 'No subject')}\nBody: {msg.get('body', '')}\n\n"
        else:
            # Single email case
            complete_thread_text = email_text
        
        try:
            function_schema = {
                "name": "extract_shipment_info",
                "description": "Extract structured shipment information from customer email",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "origin": {
                            "type": "string",
                            "description": "Origin port or city (e.g., 'Shanghai', 'Hamburg', 'CNSHA')"
                        },
                        "destination": {
                            "type": "string", 
                            "description": "Destination port or city (e.g., 'Long Beach', 'Rotterdam', 'USLGB')"
                        },
                        "shipment_type": {
                            "type": "string",
                            "description": "Shipment type",
                            "enum": ["FCL", "LCL"]
                        },
                        "container_type": {
                            "type": "string",
                            "description": "Container type (e.g., '20GP', '40GP', '40HC', '20RF', '40RF')"
                        },
                        "quantity": {
                            "type": "integer",
                            "description": "Number of containers or packages",
                            "minimum": 1
                        },
                        "weight": {
                            "type": "string",
                            "description": "Weight with unit (e.g., '25 tons', '15000 kg', '30000 lbs')"
                        },
                        "volume": {
                            "type": "string",
                            "description": "Volume with unit (e.g., '67 CBM', '2400 ft3', '15 m3')"
                        },
                        "shipment_date": {
                            "type": "string",
                            "description": "Shipment date, ready date, pickup date, or any date mentioned in the email. Look for dates in shipment details, requirements, or timeline sections. Examples: 'February 15th, 2025', '2024-07-15', 'July 15th', 'next week', '15th June 2025', 'ETD: March 20th'"
                        },
                        "commodity": {
                            "type": "string",
                            "description": "Type of goods (e.g., 'electronics', 'textiles', 'machinery', 'food products')"
                        },
                        "dangerous_goods": {
                            "type": "boolean",
                            "description": "Whether shipment contains dangerous/hazardous goods"
                        },
                        "special_requirements": {
                            "type": "string",
                            "description": "Special handling requirements (e.g., 'refrigerated', 'urgent', 'temperature controlled')"
                        },
                        "customer_name": {
                            "type": "string",
                            "description": "Customer name extracted from email signature or salutation (e.g., 'John Smith', 'Sarah Johnson')"
                        },
                        "customer_company": {
                            "type": "string",
                            "description": "Customer company name from email signature (e.g., 'ABC Electronics Ltd.', 'Global Trading Co.')"
                        },
                        "customer_email": {
                            "type": "string",
                            "description": "Customer email address if found in signature"
                        },
                        "insurance": {
                            "type": "boolean",
                            "description": "Whether customer needs cargo insurance"
                        },
                        "packaging": {
                            "type": "string",
                            "description": "Special packaging requirements (e.g., 'crating', 'palletizing', 'wooden cases')"
                        },
                        "customs_clearance": {
                            "type": "boolean",
                            "description": "Whether customer needs customs clearance services"
                        },
                        "delivery_address": {
                            "type": "string",
                            "description": "Final delivery address if different from destination port"
                        },
                        "pickup_address": {
                            "type": "string",
                            "description": "Pickup address if different from origin port"
                        },
                        "documents_required": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Required documents for dangerous goods or special shipments"
                        }
                    }
                }
            }

            prompt = f"""
Extract structured shipment information from the complete email thread below.

GUIDELINES:
- Extract ALL information mentioned across the entire email thread
- For container types, use standard codes: 20GP, 40GP, 40HC, 20RF, 40RF, etc.
- For shipment type, determine FCL (Full Container Load) or LCL (Less Container Load)
- Set dangerous_goods to true ONLY if explicitly mentioned (hazardous, dangerous, DG, IMDG, UN codes)
- Include units for weight and volume exactly as mentioned
- IMPORTANT: Extract ANY date mentioned in the thread as shipment_date, including:
  * Ready Date, Shipment Date, Pickup Date, Loading Date, ETD (Estimated Time of Departure)
  * Dates in formats like "February 15th, 2025", "15th Feb 2025", "2025-02-15", "next week", "end of month"
  * Look for dates in shipment details, requirements, or timeline sections
- Extract customer name from email signature or salutation (e.g., "Best regards, John Smith" → customer_name: "John Smith")
- Extract company name from signature if available (e.g., "ABC Electronics Ltd." → customer_company: "ABC Electronics Ltd.")
- For LCL shipments, volume is especially important
- Look for insurance, packaging, customs clearance, and address requirements
- For dangerous goods, identify required documents (MSDS, DG declaration, etc.)
- IMPORTANT: Process the ENTIRE thread as one complete message - combine all information from all emails
- If information is provided across multiple emails, merge it into a complete picture
- Look for updates and corrections in follow-up emails

EXAMPLES:
- "2x40ft FCL" → quantity: 2, container_type: "40GP", shipment_type: "FCL"
- "LCL 5 CBM" → shipment_type: "LCL", volume: "5 CBM"
- "Shanghai to Long Beach" → origin: "Shanghai", destination: "Long Beach"
- "Ready Date: February 15th, 2025" → shipment_date: "February 15th, 2025"
- "ready July 15th" → shipment_date: "July 15th"
- "shipment date: 2025-03-20" → shipment_date: "2025-03-20"
- "ETD: next week" → shipment_date: "next week"
- "dangerous goods" → dangerous_goods: true
- "need insurance" → insurance: true
- "wooden crates" → packaging: "wooden crates"
- "customs clearance needed" → customs_clearance: true
- "deliver to warehouse" → delivery_address: "warehouse"
- "Best regards, John Smith" → customer_name: "John Smith"
- "ABC Electronics Ltd." → customer_company: "ABC Electronics Ltd."
- "I want to ship to Jebel Ali" → destination: "Jebel Ali"
- "this commodity is not hazardous" → dangerous_goods: false

COMPLETE EMAIL THREAD:
{complete_thread_text}

Use the extract_shipment_info function to return the extracted data from the complete thread.
"""

            response = self.client.chat.completions.create(
                model=self.config.get("model_name", "databricks-meta-llama-3-3-70b-instruct"),
                messages=[{"role": "user", "content": prompt}],
                tools=[{"type": "function", "function": function_schema}],
                tool_choice={"type": "function", "function": {"name": "extract_shipment_info"}},
                temperature=0.0,
                max_tokens=500
            )

            # Extract function call result
            tool_calls = getattr(response.choices[0].message, "tool_calls", None)
            if not tool_calls:
                return {"error": "No function call in LLM response"}

            # Parse function arguments - FIX: Use proper JSON parsing
            tool_args = tool_calls[0].function.arguments
            if isinstance(tool_args, str):
                try:
                    # Use json.loads instead of eval for proper JSON parsing
                    result = json.loads(tool_args)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON from LLM: {tool_args}")
                    return {"error": f"Invalid JSON from LLM: {str(e)}"}
            else:
                result = tool_args

            # Ensure all expected fields exist
            expected_fields = [
                "origin", "destination", "shipment_type", "container_type", "quantity",
                "weight", "volume", "shipment_date", "commodity", "dangerous_goods", "special_requirements",
                "customer_name", "customer_company", "customer_email", "insurance", "packaging",
                "customs_clearance", "delivery_address", "pickup_address", "documents_required"
            ]
            
            for field in expected_fields:
                if field not in result:
                    result[field] = None

            # Normalize and validate data
            result = self._normalize_extraction(result)
            
            # Set extraction method
            result["extraction_method"] = "databricks_llm_function_call"
            
            # Log successful extraction
            origin = result.get('origin', 'N/A')
            destination = result.get('destination', 'N/A')
            shipment_type = result.get('shipment_type', 'N/A')
            self.logger.info(f"Extracted: {origin} → {destination} ({shipment_type})")
            
            return result

        except Exception as e:
            self.logger.error(f"LLM extraction failed: {e}")
            return {"error": f"LLM extraction failed: {str(e)}"}



    def _normalize_extraction(self, result):
        """Normalize and validate extraction results"""
        # Normalize container type
        if result.get("container_type"):
            container_type = str(result["container_type"]).lower().strip()
            container_mapping = {
                '20ft': '20GP', '40ft': '40GP', '20gp': '20GP', '40gp': '40GP',
                '40hc': '40HC', '20dc': '20DC', '40dc': '40DC',
                '20': '20GP', '40': '40GP', '20rf': '20RF', '40rf': '40RF'
            }
            result["container_type"] = container_mapping.get(container_type, result["container_type"].upper())

        # Normalize shipment type
        if result.get("shipment_type"):
            result["shipment_type"] = result["shipment_type"].upper()

        # Ensure dangerous_goods is boolean
        if not isinstance(result.get("dangerous_goods"), bool):
            result["dangerous_goods"] = False

        # Validate quantity
        if result.get("quantity"):
            if not isinstance(result["quantity"], int) or result["quantity"] < 1:
                try:
                    result["quantity"] = max(1, int(result["quantity"]))
                except (ValueError, TypeError):
                    result["quantity"] = None

        return result

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_extraction_agent():
    """Test the extraction agent with sample emails"""
    print("=== Testing Enhanced Extraction Agent ===")
    
    agent = ExtractionAgent()
    agent.load_context()
    
    test_cases = [
        {
            "email_text": "Need quote for 2x40ft FCL from Shanghai to Long Beach, electronics, ready July 15th, 25 tons total",
            "subject": "Shipping Quote Request",
            "expected_fields": ["origin", "destination", "shipment_type", "container_type", "quantity", "commodity", "weight", "shipment_date"]
        },
        {
            "email_text": "LCL shipment from Hamburg to New York, 5 CBM, machinery parts, dangerous goods included",
            "subject": "LCL Quote",
            "expected_fields": ["origin", "destination", "shipment_type", "volume", "commodity", "dangerous_goods"]
        },
        {
            "email_text": "1x20GP container from Mumbai to Rotterdam, textiles, 15 tons, urgent delivery required",
            "subject": "Container Booking",
            "expected_fields": ["origin", "destination", "container_type", "quantity", "commodity", "weight", "special_requirements"]
        },
        {
            "email_text": "FCL 40HC from Singapore to Los Angeles, food products, refrigerated container needed",
            "subject": "Reefer Shipment",
            "expected_fields": ["origin", "destination", "shipment_type", "container_type", "commodity", "special_requirements"]
        },
        {
            "email_text": "Can you provide rates for 40HC container from CNSHA to USLGB? Cargo is electronics, 20 tons.",
            "subject": "Rate Request",
            "expected_fields": ["origin", "destination", "container_type", "commodity", "weight"]
        }
    ]
    
    successful_extractions = 0
    total_expected_fields = 0
    total_extracted_fields = 0
    
    for i, test_data in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Subject: {test_data['subject']}")
        print(f"Email: {test_data['email_text'][:60]}...")
        
        result = agent.run(test_data)
        
        if result.get("status") == "success":
            print("✅ Extraction successful")
            successful_extractions += 1
            
            # Check expected fields
            expected = test_data["expected_fields"]
            extracted = 0
            
            print("  📋 Extracted fields:")
            for field in expected:
                value = result.get(field)
                if value is not None:
                    print(f"    ✓ {field}: {value}")
                    extracted += 1
                else:
                    print(f"    ✗ {field}: MISSING")
            
            total_expected_fields += len(expected)
            total_extracted_fields += extracted
            
            print(f"  📊 Field extraction: {extracted}/{len(expected)} ({extracted/len(expected)*100:.1f}%)")
            
        else:
            print(f"❌ Error: {result.get('error')}")
    
    print(f"\n📊 Overall Results:")
    print(f"✓ Successful extractions: {successful_extractions}/{len(test_cases)} ({successful_extractions/len(test_cases)*100:.1f}%)")
    print(f"✓ Field extraction rate: {total_extracted_fields}/{total_expected_fields} ({total_extracted_fields/total_expected_fields*100:.1f}%)")

def test_edge_cases():
    """Test edge cases and normalization"""
    print("\n=== Testing Edge Cases ===")
    
    agent = ExtractionAgent()
    agent.load_context()
    
    edge_cases = [
        {
            "name": "Container Type Normalization",
            "email_text": "Need 2x40ft containers from Shanghai to Long Beach",
            "subject": "Container Quote",
            "check_field": "container_type",
            "expected_value": "40GP"
        },
        {
            "name": "Dangerous Goods Detection",
            "email_text": "Shipping dangerous goods from Hamburg to New York, IMDG class 3",
            "subject": "DG Shipment",
            "check_field": "dangerous_goods",
            "expected_value": True
        },
        {
            "name": "LCL Type Detection",
            "email_text": "LCL consolidation needed, 5 CBM from Mumbai to Rotterdam",
            "subject": "LCL Request",
            "check_field": "shipment_type",
            "expected_value": "LCL"
        },
        {
            "name": "Quantity Extraction",
            "email_text": "Need quote for 3 containers from Singapore to Los Angeles",
            "subject": "Multi Container",
            "check_field": "quantity",
            "expected_value": 3
        }
    ]
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n--- Edge Case {i}: {test_case['name']} ---")
        
        result = agent.run({
            "email_text": test_case["email_text"],
            "subject": test_case["subject"]
        })
        
        if result.get("status") == "success":
            actual_value = result.get(test_case["check_field"])
            expected_value = test_case["expected_value"]
            
            if actual_value == expected_value:
                print(f"✅ {test_case['check_field']}: {actual_value} (correct)")
            else:
                print(f"❌ {test_case['check_field']}: {actual_value} (expected {expected_value})")
        else:
            print(f"❌ Error: {result.get('error')}")

def run_all_tests():
    """Run all test suites"""
    print("🚀 Starting Enhanced Extraction Agent Tests")
    print("=" * 50)
    
    try:
        # Basic functionality
        test_extraction_agent()
        
        # Edge cases
        test_edge_cases()
        
        print("\n" + "=" * 50)
        print("🎉 All extraction tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run individual test or all tests
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "basic":
            test_extraction_agent()
        elif sys.argv[1] == "edge":
            test_edge_cases()
        else:
            print("Usage: python extraction_agent.py [basic|edge]")
    else:
        # Run all tests
        run_all_tests()
