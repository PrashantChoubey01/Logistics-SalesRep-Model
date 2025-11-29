#!/usr/bin/env python3
"""
Enhanced Information Extraction Agent
====================================

Extracts structured information from emails with recency-based priority
and cumulative coalescing using thread management.
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .base_agent import BaseAgent
from utils.thread_manager import ThreadManager, EmailEntry

logger = logging.getLogger(__name__)


class InformationExtractionAgent(BaseAgent):
    """Enhanced agent for extracting information with recency-based priority"""
    
    def __init__(self):
        super().__init__("information_extraction_agent")
        self.thread_manager = ThreadManager()
        
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process email for information extraction with recency-based priority
        
        Args:
            input_data: Dictionary containing:
                - email_text: Email content
                - sender: Email sender
                - thread_id: Thread identifier
                - timestamp: Email timestamp
                - subject: Email subject
                - customer_context: Customer context
                - forwarder_context: Forwarder context
                - prioritize_recent: Whether to prioritize recent data
                
        Returns:
            Dictionary with extraction results
        """
        try:
            print(f"🔍 INFORMATION_EXTRACTOR: Starting enhanced LLM information extraction...")
            
            email_text = input_data.get("email_text", "")
            sender = input_data.get("sender", "")
            thread_id = input_data.get("thread_id", "")
            timestamp = input_data.get("timestamp", datetime.utcnow().isoformat())
            subject = input_data.get("subject", "")
            customer_context = input_data.get("customer_context", {})
            forwarder_context = input_data.get("forwarder_context", {})
            prioritize_recent = input_data.get("prioritize_recent", True)
            
            print(f"📧 Email: {subject[:50]}...")
            print(f"👤 Sender: {sender}")
            print(f"🧵 Thread ID: {thread_id}")
            print(f"🔍 Enhanced Information Extraction Process:")
            print(f"   Thread History Length: {self._get_thread_length(thread_id)}")
            print(f"   Prioritize Recent: {prioritize_recent}")
            
            # Step 1: Extract from new email
            print(f"\n📧 Step 1: Extracting from new email...")
            new_email_extraction = self._extract_from_new_email_only(email_text, subject, sender)
            
            if not new_email_extraction:
                print(f"   ❌ New email extraction failed")
                return self._create_error_result("New email extraction failed")
            
            print(f"   ✅ New email extraction completed")
            
            # Step 2: Get cumulative extraction from thread or workflow state
            print(f"\n📚 Step 2: Getting cumulative extraction from thread...")
            cumulative_extraction = input_data.get("cumulative_extraction", {})
            
            if not cumulative_extraction:
                cumulative_extraction = self.thread_manager.get_cumulative_extraction(thread_id)
            
            if cumulative_extraction:
                print(f"   ✅ Cumulative extraction found: {len(cumulative_extraction)} categories")
            else:
                print(f"   ℹ️ No cumulative extraction found (new thread)")
            
            # Step 3: Merge with recency priority
            print(f"\n🔄 Step 3: Merging with recency priority...")
            final_extraction = self.thread_manager.merge_with_recency_priority(
                new_data=new_email_extraction,
                cumulative_data=cumulative_extraction
            )
            
            # Step 4: Update cumulative extraction in thread
            print(f"\n💾 Step 4: Updating cumulative extraction...")
            update_success = self.thread_manager.update_cumulative_extraction(
                thread_id=thread_id,
                new_extraction=new_email_extraction
            )
            
            if update_success:
                print(f"   ✅ Cumulative extraction updated")
            else:
                print(f"   ⚠️ Failed to update cumulative extraction")
            
            # Step 5: Add email to thread
            print(f"\n📝 Step 5: Adding email to thread...")
            email_entry = EmailEntry(
                timestamp=timestamp,
                email_id=f"email_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}",
                sender=sender,
                direction="inbound",
                subject=subject,
                content=email_text,
                extracted_data=new_email_extraction
            )
            
            self.thread_manager.add_email_to_thread(thread_id, email_entry)
            print(f"   ✅ Email added to thread")
            
            # Calculate quality metrics
            quality_score = self._calculate_extraction_quality(final_extraction)
            confidence = self._calculate_confidence(final_extraction)
            
            print(f"\n✅ INFORMATION_EXTRACTOR: Enhanced LLM extraction complete")
            print(f"   Categories Extracted: {len(final_extraction)}")
            print(f"   Quality Score: {quality_score:.2f}")
            print(f"   Confidence: {confidence:.2f}")
            
            return {
                "status": "success",
                "extracted_data": final_extraction,
                "new_email_extraction": new_email_extraction,
                "cumulative_extraction": cumulative_extraction,
                "quality_score": quality_score,
                "confidence": confidence,
                "thread_id": thread_id,
                "timestamp": timestamp,
                "prioritize_recent": prioritize_recent,
                "merge_strategy": "recency_based",
                "categories_extracted": len(final_extraction),
                "extraction_metadata": {
                    "new_email_fields": self._count_fields(new_email_extraction),
                    "cumulative_fields": self._count_fields(cumulative_extraction),
                    "final_fields": self._count_fields(final_extraction),
                    "thread_length": self._get_thread_length(thread_id)
                }
            }
            
        except Exception as e:
            logger.error(f"Enhanced information extraction failed: {e}")
            return self._create_error_result(f"Enhanced extraction failed: {str(e)}")
    
    def _extract_from_new_email_only(self, email_text: str, subject: str, sender: str) -> Optional[Dict[str, Any]]:
        """Extract information from new email only"""
        try:
            if not self.client:
                print(f"   ⚠️ LLM not loaded, attempting to load...")
                self.load_context()
            
            if not self.client:
                print(f"   ❌ LLM not available")
                return None
            
            print(f"   🔍 Using LLM for extraction...")
            
            # Enhanced prompt with clear instructions
            prompt = self._create_enhanced_extraction_prompt(email_text, subject, sender)
            print(f"   📝 Prompt length: {len(prompt)} characters")
            
            # Enhanced function schema with required fields for better LLM performance
            function_schema = {
                "type": "function",
                "function": {
                    "name": "extract_information",
                    "description": "Extract shipping and contact information from email",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origin": {"type": "string", "description": "Origin port/city"},
                            "destination": {"type": "string", "description": "Destination port/city"},
                            "container_type": {"type": "string", "description": "Container type (20GP, 40GP, 40HC, etc.)"},
                            "container_count": {"type": "string", "description": "Number of containers"},
                            "commodity": {"type": "string", "description": "Type of goods/commodity"},
                            "weight": {"type": "string", "description": "Weight of shipment"},
                            "volume": {"type": "string", "description": "Volume of shipment"},
                            "contact_name": {"type": "string", "description": "Customer/contact name"},
                            "email": {"type": "string", "description": "Email address"},
                            "phone": {"type": "string", "description": "Phone number"},
                            "whatsapp": {"type": "string", "description": "WhatsApp number (optional)"},
                            "company": {"type": "string", "description": "Company name"},
                            "requested_dates": {"type": "string", "description": "Requested shipping dates"},
                            "transit_time": {"type": "string", "description": "Transit time requirements"},
                            "urgency": {"type": "string", "description": "Urgency level"},
                            "deadline": {"type": "string", "description": "Deadline requirements"},
                            "incoterm": {"type": "string", "description": "Incoterm (FOB, CIF, EXW, etc.)"},
                            "special_requirements": {"type": "array", "items": {"type": "string"}, "description": "Special handling requirements"},
                            "additional_notes": {"type": "string", "description": "Additional notes or comments"}
                        },
                        "required": []
                    }
                }
            }
            
            # Make LLM call using OpenAI client for function calling
            client = self.get_openai_client()
            if not client:
                return {"error": "OpenAI client not available for function calling"}
            
            response = client.chat.completions.create(
                model=self.config.get("model_name"),
                messages=[{"role": "user", "content": prompt}],
                tools=[function_schema],
                tool_choice={"type": "function", "function": {"name": "extract_information"}},
                temperature=0.1,
                max_tokens=2000
            )
            
            print(f"   📨 LLM Response received")
            print(f"   📊 Response choices: {len(response.choices)}")
            
            if response.choices and response.choices[0].message.tool_calls:
                tool_call = response.choices[0].message.tool_calls[0]
                print(f"   🔧 Tool call found: {tool_call.function.name}")
                
                try:
                    # Try to parse the arguments as JSON
                    extracted_data = json.loads(tool_call.function.arguments)
                    print(f"   📄 Arguments: {json.dumps(extracted_data, indent=2)}")
                except json.JSONDecodeError as e:
                    print(f"   ❌ JSON Parse Error: {e}")
                    print(f"   📄 Raw arguments: {tool_call.function.arguments}")
                    
                    # Try to fix common JSON issues
                    try:
                        # Remove any trailing text after the JSON
                        raw_args = tool_call.function.arguments.strip()
                        if raw_args.endswith('.'):
                            raw_args = raw_args[:-1]
                        
                        # Try to find valid JSON in the response
                        start_idx = raw_args.find('{')
                        end_idx = raw_args.rfind('}') + 1
                        if start_idx != -1 and end_idx > start_idx:
                            json_str = raw_args[start_idx:end_idx]
                            extracted_data = json.loads(json_str)
                            print(f"   ✅ Fixed JSON parsing: {json.dumps(extracted_data, indent=2)}")
                        else:
                            print(f"   ❌ Could not find valid JSON in response")
                            return None
                    except Exception as fix_error:
                        print(f"   ❌ Failed to fix JSON: {fix_error}")
                        return None
                
                # Convert flattened structure to nested format
                nested_data = {
                    "shipment_details": {
                        "origin": extracted_data.get("origin", ""),
                        "destination": extracted_data.get("destination", ""),
                        "container_type": extracted_data.get("container_type", ""),
                        "container_count": extracted_data.get("container_count", ""),
                        "commodity": extracted_data.get("commodity", ""),
                        "weight": extracted_data.get("weight", ""),
                        "volume": extracted_data.get("volume", ""),
                        "incoterm": extracted_data.get("incoterm", "")
                    },
                    "contact_information": {
                        "name": extracted_data.get("contact_name", ""),
                        "email": extracted_data.get("email", ""),
                        "phone": extracted_data.get("phone", ""),
                        "company": extracted_data.get("company", ""),
                        "whatsapp": extracted_data.get("whatsapp", "")
                    },
                    "timeline_information": {
                        "requested_dates": extracted_data.get("requested_dates", ""),
                        "transit_time": extracted_data.get("transit_time", ""),
                        "urgency": extracted_data.get("urgency", ""),
                        "deadline": extracted_data.get("deadline", "")
                    },
                    "special_requirements": extracted_data.get("special_requirements", []),
                    "additional_notes": extracted_data.get("additional_notes", "")
                }
                
                print(f"   ✅ Parsed data: {nested_data}")
                return nested_data
            else:
                print(f"   ❌ No tool call found in response")
                # Return a safe default structure instead of None
                return {
                    "shipment_details": {
                        "origin": "",
                        "destination": "",
                        "container_type": "",
                        "container_count": "",
                        "commodity": "",
                        "weight": "",
                        "volume": "",
                        "incoterm": ""
                    },
                    "contact_information": {
                        "name": "",
                        "email": "",
                        "phone": "",
                        "company": "",
                        "whatsapp": ""
                    },
                    "timeline_information": {
                        "requested_dates": "",
                        "transit_time": "",
                        "urgency": "",
                        "deadline": ""
                    },
                    "special_requirements": [],
                    "additional_notes": ""
                }
                
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            print(f"   ❌ LLM extraction failed: {e}")
            # Return a safe default structure instead of None
            return {
                "shipment_details": {
                    "origin": "",
                    "destination": "",
                    "container_type": "",
                    "container_count": "",
                    "commodity": "",
                    "weight": "",
                    "volume": "",
                    "incoterm": ""
                },
                "contact_information": {
                    "name": "",
                    "email": "",
                    "phone": "",
                    "company": "",
                    "whatsapp": ""
                },
                "timeline_information": {
                    "requested_dates": "",
                    "transit_time": "",
                    "urgency": "",
                    "deadline": ""
                },
                "special_requirements": [],
                "additional_notes": ""
            }
    
    def _create_enhanced_extraction_prompt(self, email_text: str, subject: str, sender: str) -> str:
        """Create enhanced extraction prompt"""
        return f"""
You are an expert logistics information extractor. Extract shipping information from the following email with high precision.

EMAIL SUBJECT: {subject}
SENDER: {sender}
EMAIL CONTENT:
{email_text}

EXTRACTION INSTRUCTIONS:
1. Extract ONLY information that is explicitly mentioned in the email
2. Do NOT infer or assume any information
3. If a field is not mentioned, leave it empty (use empty string "")
4. Prioritize information from the email content over the subject
5. Be precise with port names, container types, and measurements
6. Return ONLY valid JSON format - no additional text or explanations
7. Use empty strings for missing values, not null or undefined
8. Pay special attention to structured responses with "Field: Value" format

EXTRACTION SECTIONS:

1. SHIPMENT DETAILS:
   - Origin: Port/city/country where shipment originates
   - Destination: Port/city/country where shipment is going
   - Container Type: Type of container (20GP, 40GP, 40HC, etc.)
   - Container Count: Number of containers
   - Commodity: Type of goods being shipped
   - Weight: Weight of shipment (include units)
   - Volume: Volume of shipment (include units)
   - Incoterm: Incoterms (FOB, CIF, EXW, etc.)

2. CONTACT INFORMATION:
   - Name: Contact person name
   - Email: Contact email address
   - Phone: Contact phone number
   - Company: Company name

3. TIMELINE INFORMATION:
   - Requested Dates: When shipment is needed
   - Transit Time: Required transit time
   - Urgency: How urgent the shipment is
   - Deadline: Specific deadline if mentioned

4. SPECIAL REQUIREMENTS:
   - List any special requirements or instructions

5. ADDITIONAL NOTES:
   - Any other relevant information

EXAMPLES:
- "I need to ship 2 containers from Shanghai to Los Angeles" → Origin: Shanghai, Destination: Los Angeles, Container Count: 2
- "40HC container with 15,000 kg" → Container Type: 40HC, Weight: 15,000 kg
- "Need it by August 25th" → Requested Dates: August 25th
- "Destination: Los Angeles, USA" → Destination: Los Angeles, USA
- "Commodity: Electronics" → Commodity: Electronics
- "Quantity: 2 containers" → Container Count: 2

STRUCTURED RESPONSE PATTERNS:
- "Destination: [value]" → Extract as destination
- "Origin: [value]" → Extract as origin
- "Commodity: [value]" → Extract as commodity
- "Quantity: [value]" → Extract as container_count
- "Weight: [value]" → Extract as weight
- "Volume: [value]" → Extract as volume
- "Container Type: [value]" → Extract as container_type
- "Incoterm: [value]" → Extract as incoterm

CONTAINER TYPE DETECTION:
- If customer mentions "containers" or "container" → This indicates FCL shipment
- If customer provides quantity (e.g., "2 containers") → This is FCL shipment
- If no specific container type is mentioned but "containers" is used → Set container_type to "Standard" or leave empty
- If customer mentions weight and volume without containers → This is LCL shipment

EXAMPLES:
- "Quantity: 2 containers" → container_count: "2", container_type: "" (FCL shipment)
- "2x40ft containers" → container_count: "2", container_type: "40GP" (FCL shipment)
- "Weight: 5000 kg, Volume: 20 CBM" → weight: "5000 kg", volume: "20 CBM" (LCL shipment)

Extract the information accurately and return it in the specified format.
"""
    
    def _get_thread_length(self, thread_id: str) -> int:
        """Get the length of a thread"""
        thread_data = self.thread_manager.load_thread(thread_id)
        return len(thread_data.email_chain) if thread_data else 0
    
    def _count_fields(self, data: Dict[str, Any]) -> int:
        """Count the number of fields in extracted data"""
        if not data:
            return 0
        
        count = 0
        for category, category_data in data.items():
            if isinstance(category_data, dict):
                count += len([v for v in category_data.values() if v])
            elif isinstance(category_data, list):
                count += len(category_data)
            elif category_data:
                count += 1
        
        return count
    
    def _calculate_extraction_quality(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate quality score for extraction"""
        if not extracted_data:
            return 0.0
        
        total_fields = 0
        filled_fields = 0
        
        for category, category_data in extracted_data.items():
            if isinstance(category_data, dict):
                for field, value in category_data.items():
                    total_fields += 1
                    if value and str(value).strip():
                        filled_fields += 1
            elif isinstance(category_data, list):
                total_fields += 1
                if category_data:
                    filled_fields += 1
            elif category_data:
                total_fields += 1
                if str(category_data).strip():
                    filled_fields += 1
        
        return filled_fields / total_fields if total_fields > 0 else 0.0
    
    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence score for extraction"""
        quality = self._calculate_extraction_quality(extracted_data)
        
        # Base confidence on quality
        confidence = quality * 0.8
        
        # Bonus for having key fields
        key_fields = ["origin", "destination", "container_type"]
        key_fields_present = 0
        
        shipment_details = extracted_data.get("shipment_details", {})
        for field in key_fields:
            if shipment_details.get(field):
                key_fields_present += 1
        
        confidence += (key_fields_present / len(key_fields)) * 0.2
        
        return min(confidence, 1.0)
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """Create error result"""
        return {
            "status": "error",
            "error": error_message,
            "extracted_data": {},
            "quality_score": 0.0,
            "confidence": 0.0
        } 