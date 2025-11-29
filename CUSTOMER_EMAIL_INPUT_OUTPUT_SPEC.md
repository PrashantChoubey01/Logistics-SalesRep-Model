# Customer Email Input/Output Specification
## Based on demo_app.py EMAIL_TEMPLATES

This document lists all customer email templates from `demo_app.py` and their expected input/output emails based on the happy flow workflow.

## ⚠️ IMPORTANT: Data Enrichment and Validation

**All customer emails go through data enrichment and validation before response generation:**

1. **Port Information Enrichment:**
   - Customer input: "Shanghai, China" or "Los Angeles, USA"
   - System enriches: "Shanghai (CNSHG)" or "Los Angeles (USLAX)"
   - **Enriched data with port codes is shown to customer for validation**

2. **Container Type Standardization:**
   - Customer input: "40 HC", "forty high cube", "40' High Cube"
   - System standardizes: "40HC"
   - **Standardized format is shown to customer**

3. **Data Validation:**
   - All extracted data (including enriched data) is validated
   - Validation results determine if clarification or confirmation is needed
   - **All validated and enriched data is displayed to customer**

4. **Response Format:**
   - All responses show **enriched port data with port codes** when available
   - All responses show **standardized container types**
   - All responses include **assigned sales person details**
   - Format: `Port Name (PORT_CODE)` for ports
   - Format: Standardized container codes (e.g., "40HC", "20GP")

---

## 1. Customer - Complete Quote Request

### 📥 INPUT EMAIL

**From:** john.doe@techcorp.com  
**Subject:** FCL Shipping Quote - Shanghai to Los Angeles  
**Content:**
```
Hello Searates,

I need a shipping quote for a full container load from Shanghai, China to Los Angeles, USA.

Details:
- Origin: Shanghai, China
- Destination: Los Angeles, USA
- Container Type: 40HC
- Number of Containers: 2
- Commodity: Electronics
- Weight: 20,000 kg per container
- Ready Date: 2024-03-15
- Incoterm: FOB

Please provide rates and transit time.

Best regards,
John Doe
Logistics Manager
TechCorp Inc.
```

### 📤 EXPECTED OUTPUT EMAIL

**Response Type:** Confirmation Request (if all fields extracted and validated) OR Clarification Request (if missing fields)

**To:** john.doe@techcorp.com  
**From:** [Assigned Sales Person Name] <[Assigned Sales Person Email]>  
**Subject:** Please Confirm Your Shipment Details - Shanghai to Los Angeles

**Content (Confirmation Request - Standard Format):**
```
Dear John Doe,

Thank you for providing the details for your shipment from Shanghai to Los Angeles.

I've carefully reviewed your email and extracted the following information. Please take a moment to confirm these details are accurate:

**Shipment Details:**
• Origin: Shanghai, China
• Destination: Los Angeles, USA
• Container Type: 40HC
• Number of Containers: 2
• Commodity: Electronics
• Weight: 20,000 kg per container
• Ready Date: 2024-03-15
• Incoterm: FOB

**Next Steps:**
• If all information above is correct, please reply with 'Confirmed' or 'Yes, that's correct'
• If any information needs correction, please provide the correct details
• If any information is missing, please provide it

Once you confirm these details, I'll proceed with preparing your comprehensive shipping quote.

Best regards,
[Sales Person Name]
[Sales Person Title]
[Sales Person Email]
[Sales Person Phone]
```

**Note:** 
- **Data Enrichment Process:** Port lookup enriches "Shanghai, China" → "Shanghai (CNSHG)" internally
- **Container Standardization:** "40HC" is standardized from various input formats
- **Validation:** All data (including enriched) is validated before display
- **Display:** Confirmation response shows extracted data (enriched data used internally for validation and forwarder assignment)
- **Clarification responses** explicitly show enriched port codes (e.g., "Shanghai (CNSHG)") to help customer validate port identification

**OR Content (Clarification Request - if missing fields, with ENRICHED data shown):**
```
Dear John Doe,

Thank you for your shipping quote request. I've reviewed your email and need some additional details to provide you with an accurate quote.

**Information I've Extracted So Far:**
**Shipment Details:**
• Origin: Shanghai (CNSHG)
• Destination: Los Angeles (USLAX)
• Container Type: 40HC
• Number of Containers: 2
• Commodity: Electronics
• Weight: 20,000 kg per container
• Ready Date: 2024-03-15
• Incoterm: FOB

**Missing Information:**
- [List of missing fields, e.g., "Exact shipment date format", "Commodity HS code", etc.]

**Please provide:**
• [Specific questions about missing fields]

Once I have all the required information, I'll prepare your comprehensive shipping quote.

Best regards,
[Sales Person Name]
[Sales Person Title]
[Sales Person Email]
[Sales Person Phone]
```

**Note:** 
- **Clarification responses explicitly show ENRICHED port data with port codes** (e.g., "Shanghai (CNSHG)") to help customer validate if the system correctly identified the ports
- This allows customer to confirm or correct port identification
- All successfully extracted and enriched data is shown, even when asking for missing fields

### 🔄 WORKFLOW PATH
```
classify_email → conversation_state → analyze_thread → extract_information 
→ validate_data → lookup_ports → standardize_container → recommend_rates 
→ next_action → assign_sales_person → generate_confirmation_response 
OR generate_clarification_response → update_thread
```

---

## 2. Customer - Minimal Information

### 📥 INPUT EMAIL

**From:** jane.smith@imports.com  
**Subject:** Shipping quote needed  
**Content:**
```
Hi,

I need shipping rates from China to USA. Can you help?

Thanks,
Jane Smith
```

### 📤 EXPECTED OUTPUT EMAIL

**Response Type:** Clarification Request (missing critical fields)

**To:** jane.smith@imports.com  
**From:** [Assigned Sales Person Name] <[Assigned Sales Person Email]>  
**Subject:** Additional Information Needed for Your Shipping Quote - China to USA

**Content (with ENRICHED data if ports were identified):**
```
Dear Jane Smith,

Thank you for your shipping quote request. I've reviewed your email and need some additional information to provide you with an accurate quote.

**Information I've Extracted So Far:**
**Shipment Details:**
• Origin: China (country identified)
• Destination: USA (country identified)
• [If ports were identified through enrichment, they would show here with port codes]

**Missing Required Information:**
- Origin port/city (e.g., Shanghai, China or specific port code)
- Destination port/city (e.g., Los Angeles, USA or specific port code)
- Shipment type (FCL - Full Container Load or LCL - Less than Container Load)
- Container type (if FCL: 20GP, 40GP, 40HC, etc.)
- Number of containers (if FCL)
- Weight and volume (if LCL)
- Commodity description
- Ready date / Shipment date
- Incoterms (FOB, CIF, EXW, etc.)

**Please provide:**
• Specific origin and destination ports or cities
• Shipment type and container specifications
• Commodity information
• Preferred shipping dates

Once I have all the required information, I'll prepare your comprehensive shipping quote.

Best regards,
[Sales Person Name]
[Sales Person Title]
[Sales Person Email]
[Sales Person Phone]
```

**Note:** The system attempts to enrich port information even from minimal input. If ports are identified, they are shown with port codes. All enriched data is displayed to help customer understand what was extracted.

### 🔄 WORKFLOW PATH
```
classify_email → conversation_state → analyze_thread → extract_information 
→ validate_data → lookup_ports → standardize_container → recommend_rates 
→ next_action → assign_sales_person → generate_clarification_response 
→ update_thread
```

---

## 3. Customer - Confirmation

### 📥 INPUT EMAIL

**From:** john.doe@techcorp.com  
**Subject:** Re: Shipping Quote - Confirmation  
**Content:**
```
Thank you for the quote. I confirm all the details:

- Origin: Shanghai, China
- Destination: Los Angeles, USA
- Container Type: 40HC
- Number of Containers: 2
- Commodity: Electronics
- Weight: 20,000 kg per container
- Ready Date: 2024-03-15
- Incoterm: FOB

Please proceed with the booking. I also need transit time information.

Best regards,
John Doe
```

### 📤 EXPECTED OUTPUT EMAIL

**Response Type:** Confirmation Acknowledgment → Forwarder Assignment

**To:** john.doe@techcorp.com  
**From:** [Assigned Sales Person Name] <[Assigned Sales Person Email]>  
**Subject:** Confirmation Received - Processing Your Booking

**Content (Confirmation Acknowledgment - Standard Format):**
```
Dear John Doe,

Thank you for confirming your shipment details. I've received your confirmation for:

**Confirmed Shipment Details:**
- Origin: Shanghai, China
- Destination: Los Angeles, USA
- Container Type: 40HC
- Number of Containers: 2
- Commodity: Electronics
- Weight: 20,000 kg per container
- Ready Date: 2024-03-15
- Incoterm: FOB

I'm now proceeding with your booking and will request quotes from our network of forwarders. You'll receive transit time information along with the rate quotes.

I'll keep you updated on the progress.

Best regards,
[Sales Person Name]
[Sales Person Title]
[Sales Person Email]
[Sales Person Phone]
```

**Then System Action:**
- Assigns forwarder(s) based on route using **ENRICHED port codes** (CNSHG to USLAX)
- Uses **ENRICHED and VALIDATED data** for forwarder assignment
- Sends rate request email to forwarder(s) with enriched port codes and standardized container types
- Waits for forwarder response

**Note:** 
- The confirmation acknowledgment shows confirmed data in standard format
- **Internally, the system uses ENRICHED port codes** (CNSHG, USLAX) for forwarder assignment and rate requests
- **Enriched data is what gets sent to forwarders**, not the raw customer input
- Container types are standardized before being used

### 🔄 WORKFLOW PATH
```
classify_email → conversation_state → analyze_thread → extract_information 
→ validate_data → lookup_ports → standardize_container → recommend_rates 
→ next_action → assign_sales_person → generate_confirmation_acknowledgment 
→ assign_forwarders → update_thread
```

---

## 4. Customer - Urgent Request

### 📥 INPUT EMAIL

**From:** urgent@bigcorp.com  
**Subject:** URGENT - Large Shipment Quote Needed ASAP  
**Content:**
```
Hello Searates,

This is URGENT. We need immediate quote for a large shipment:

- Origin: Shanghai, China
- Destination: Los Angeles, USA
- Container Type: 40HC
- Number of Containers: 15
- Commodity: Automotive Parts
- Weight: 300,000 kg total
- Ready Date: 2024-03-10 (URGENT - need to ship ASAP)
- Incoterm: CIF

This is a time-sensitive shipment. We need rates and confirmation within 24 hours.

Please prioritize this request.

Best regards,
Sarah Williams
Procurement Director
BigCorp Industries
```

### 📤 EXPECTED OUTPUT EMAIL

**Response Type:** Confirmation Request (if all fields complete and validated) OR Clarification Request (if missing fields)

**To:** urgent@bigcorp.com  
**From:** [Assigned Sales Person Name] <[Assigned Sales Person Email]>  
**Subject:** Urgent Request Received - Please Confirm Your Shipment Details - Shanghai to Los Angeles

**Content (Confirmation Request - Standard Format):**
```
Dear Sarah Williams,

Thank you for providing the details for your shipment from Shanghai to Los Angeles.

I understand this is time-sensitive and will prioritize your request. I've carefully reviewed your email and extracted the following information. Please take a moment to confirm these details are accurate:

**Shipment Details:**
• Origin: Shanghai, China
• Destination: Los Angeles, USA
• Container Type: 40HC
• Number of Containers: 15
• Commodity: Automotive Parts
• Weight: 300,000 kg total
• Ready Date: 2024-03-10 (URGENT)
• Incoterm: CIF

**Next Steps:**
• If all information above is correct, please reply with 'Confirmed' or 'Yes, that's correct'
• If any information needs correction, please provide the correct details immediately

Given the urgent nature of your request, I'll expedite the quote process once you confirm. I'll work to provide rates and transit time information within 24 hours as requested.

Best regards,
[Sales Person Name]
[Sales Person Title]
[Sales Person Email]
[Sales Person Phone]
```

**Note:** 
- Even though marked as "URGENT", the happy flow processes it normally through confirmation/clarification, not escalation
- **Data Enrichment:** Port information is enriched internally (Shanghai → CNSHG, Los Angeles → USLAX)
- **Container Standardization:** "40HC" is standardized from various input formats
- **Validation:** All enriched data is validated before being used for forwarder assignment
- **Display:** Confirmation shows standard format; enriched data used internally

### 🔄 WORKFLOW PATH
```
classify_email → conversation_state → analyze_thread → extract_information 
→ validate_data → lookup_ports → standardize_container → recommend_rates 
→ next_action → assign_sales_person → generate_confirmation_response 
OR generate_clarification_response → update_thread
```

---

## 5. Customer - Complaint

### 📥 INPUT EMAIL

**From:** angry.customer@company.com  
**Subject:** COMPLAINT - Poor Service and Delays  
**Content:**
```
Hello Searates,

I am extremely frustrated with your service. My shipment has been delayed multiple times and I have not received proper updates.

Details:
- Booking Reference: #BK-2024-002
- Original Ready Date: 2024-02-15
- Current Status: Still not shipped
- Multiple promises broken

I need:
- Immediate status update
- Explanation for delays
- Compensation for the inconvenience
- Guaranteed shipping date

This is unacceptable. I expect a response within 2 hours.

Best regards,
Robert Anderson
Anderson Trading Co.
```

### 📤 EXPECTED OUTPUT EMAIL

**Response Type:** Acknowledgment (in happy flow, complaints are handled as regular emails)

**To:** angry.customer@company.com  
**From:** [Assigned Sales Person Name] <[Assigned Sales Person Email]>  
**Subject:** Thank you for your email

**Content (Standard Acknowledgment):**
```
Dear Robert Anderson,

Thank you for your email. We have received your message and will respond shortly.

Best regards,

Digital Sales Specialist
Searates By DP World
📧 sales@searates.com
📞 +1-555-0123
🌐 www.searates.com
```

**OR (if system extracts booking reference and enriched data):**

**Subject:** Re: COMPLAINT - Poor Service and Delays - Booking #BK-2024-002

**Content:**
```
Dear Robert Anderson,

Thank you for contacting us regarding booking #BK-2024-002. I understand your frustration and apologize for the delays and lack of communication.

I'm looking into the status of your shipment and will provide you with:
- Current status update
- Explanation for the delays
- Next steps and timeline

I'll get back to you with detailed information as soon as possible.

Best regards,
[Sales Person Name]
[Sales Person Title]
[Sales Person Email]
[Sales Person Phone]
```

**Note:** 
- In happy flow, complaints are processed normally, not escalated
- The system extracts booking reference (#BK-2024-002) and any shipment details
- If shipment details are extracted, they may be enriched with port codes if applicable
- Response acknowledges the complaint but follows normal flow

### 🔄 WORKFLOW PATH
```
classify_email → conversation_state → analyze_thread → extract_information 
→ validate_data → lookup_ports → standardize_container → recommend_rates 
→ next_action → assign_sales_person → generate_acknowledgment_response 
OR generate_clarification_response → update_thread
```

---

## Summary Table

| Email Template | Input Completeness | Expected Output Type | Key Fields Extracted & Enriched |
|---------------|-------------------|---------------------|-------------------------------|
| **Complete Quote Request** | Complete | Confirmation Request | Origin (with port code), Destination (with port code), Container Type (standardized), Quantity, Commodity, Weight, Date, Incoterm - All enriched and validated |
| **Minimal Information** | Incomplete | Clarification Request | Origin/Destination countries (may be enriched to ports with codes if identifiable) - needs all other fields |
| **Confirmation** | Complete + Confirmation | Confirmation Acknowledgment → Forwarder Assignment | All shipment details confirmed with enriched port codes → triggers forwarder assignment using enriched data |
| **Urgent Request** | Complete | Confirmation Request | All fields + urgency markers - Ports enriched with codes, container standardized (processed normally in happy flow) |
| **Complaint** | Complaint/Status Query | Acknowledgment | Booking reference, complaint details - Any shipment details extracted may be enriched (processed normally, no escalation) |

---

## Happy Flow Decision Logic

### When to Generate Confirmation Request:
- ✅ All required fields are extracted and validated
- ✅ No missing critical information
- ✅ Data quality is acceptable

### When to Generate Clarification Request:
- ❌ Missing critical fields (origin, destination, container type, date, etc.)
- ❌ Incomplete information
- ⚠️ Low confidence in extracted data (but still tries clarification, not escalation)

### When to Generate Confirmation Acknowledgment:
- ✅ Customer explicitly confirms details
- ✅ Conversation state indicates "confirmation" or "confirmed"
- ✅ Triggers forwarder assignment automatically

### When to Generate Acknowledgment:
- ✅ Sales person or forwarder emails
- ✅ General inquiries without specific shipment details
- ✅ Complaints (in happy flow, handled as regular acknowledgment)

---

## Data Enrichment and Validation Process

### Port Information Enrichment
When customer enters port-related information (e.g., "Shanghai, China" or "Los Angeles, USA"):
1. **Extraction:** System extracts raw port names from email
2. **Port Lookup:** Port lookup agent enriches with port codes:
   - "Shanghai, China" → "Shanghai (CNSHG)"
   - "Los Angeles, USA" → "Los Angeles (USLAX)"
3. **Display:** Enriched port data (with port codes) is shown in confirmation/clarification responses
4. **Validation:** All enriched data is validated before being shown to customer

### Container Type Standardization
When customer enters container information:
1. **Extraction:** System extracts container type (e.g., "40HC", "40 HC", "forty high cube")
2. **Standardization:** Container standardization agent normalizes to standard format:
   - "40 HC" → "40HC"
   - "forty high cube" → "40HC"
   - "40' High Cube" → "40HC"
3. **Display:** Standardized container type is shown in responses

### Data Validation Flow
1. **Extract:** Raw data extracted from customer email
2. **Enrich:** Port lookup and container standardization enrich the data
3. **Validate:** Data validation agent checks all fields (including enriched data)
4. **Display:** All enriched and validated data is shown to customer for confirmation
5. **Confirm:** Customer confirms enriched/validated data
6. **Use:** Confirmed enriched data is used for forwarder assignment and rate requests

### What Gets Shown to Customer vs. Used Internally

**Clarification Responses:**
- ✅ **Explicitly show ENRICHED port data with port codes** (e.g., "Shanghai (CNSHG)")
- ✅ **Standardized container types** (e.g., "40HC")
- ✅ **All extracted and enriched fields** that passed validation
- ✅ **Purpose:** Help customer validate if system correctly identified ports

**Confirmation Responses:**
- ✅ **Show standard format** (e.g., "Shanghai, China")
- ✅ **Standardized container types** (e.g., "40HC")
- ✅ **All extracted fields** that passed validation
- ✅ **Internally uses ENRICHED data** (port codes) for validation and forwarder assignment

**Key Point:**
- **All data is enriched and validated** before being shown or used
- **Clarification responses** explicitly show enriched ports with codes to help customer validate
- **Confirmation responses** show standard format, but enriched data is used internally
- **Forwarder assignment** uses enriched port codes (e.g., CNSHG, USLAX) and standardized container types
- **Missing fields** are listed for clarification
- **Low confidence fields** may be shown with validation indicators

## Notes

1. **No Escalation in Happy Flow:** All customer emails follow the normal processing path without escalation, even for urgent requests or complaints.

2. **Thread Continuity:** All emails in the same thread maintain conversation context and cumulative extraction data.

3. **Sales Person Assignment:** All customer emails get assigned a sales person before response generation.

4. **Forwarder Assignment:** Only triggered after customer confirmation, not on initial request. Uses enriched/validated data.

5. **Response Personalization:** All responses include assigned sales person's name, title, email, and phone number.

6. **Data Enrichment:** Port information is always enriched with port codes when available, and shown to customer for validation.

7. **Standardized Output:** Container types, dates, and other fields are standardized before being shown to customer.

8. **Validation Before Display:** All data (including enriched data) is validated before being shown to customer for confirmation.

