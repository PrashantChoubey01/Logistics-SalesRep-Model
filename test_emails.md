# 📧 Test Emails for Logistics AI Workflow

## 🎯 **TEST SCENARIO 1: New Quote Request (Initial Customer Inquiry)**

### **Email 1.1: Basic FCL Request**
```
Subject: Rate Request for FCL Shipment
From: john.smith@techcorp.com
To: sales@dpworld.com

Hi Sarah,

I need a quote for shipping from Shanghai to Los Angeles.

Details:
- Container: 40ft HC
- Weight: 15 tons
- Commodity: Electronics (smartphones and tablets)
- Shipment date: February 15, 2024
- Quantity: 1 container

Please provide your best rates.

Thanks,
John Smith
TechCorp Inc.
```

### **Email 1.2: LCL Request with Special Requirements**
```
Subject: LCL Shipment Quote Needed
From: maria.garcia@importexport.com
To: sales@dpworld.com

Hello,

I need rates for LCL shipment:

Origin: Rotterdam, Netherlands
Destination: Miami, USA
Weight: 500 kg
Volume: 2.5 CBM
Commodity: Fashion accessories
Shipment date: March 1, 2024

Special requirements:
- Insurance required
- Handle with care (fragile items)
- Wooden crates packaging
- Customs clearance assistance needed

Please quote ASAP.

Best regards,
Maria Garcia
ImportExport Solutions
```

### **Email 1.3: Dangerous Goods Request**
```
Subject: DG Shipment Quote Request
From: david.chen@chemicals.com
To: sales@dpworld.com

Hi,

We need to ship dangerous goods:

Origin: Singapore
Destination: Hamburg, Germany
Container: 20ft GP
Weight: 8 tons
Commodity: Chemical products (UN 3082)
Shipment date: February 20, 2024

Special requirements:
- Dangerous goods handling
- IMDG compliance required
- MSDS documentation needed
- DG declaration required

Please provide rates and documentation requirements.

Thanks,
David Chen
Chemical Solutions Ltd.
```

---

## 🎯 **TEST SCENARIO 2: Customer Confirmation (After Bot Extracts Details)**

### **Email 2.1: Simple Confirmation**
```
Subject: Re: Confirmation of Shipment Details
From: john.smith@techcorp.com
To: sales@dpworld.com

Hi James,

Yes, all the details are correct. Please proceed with the booking.

Thanks,
John Smith
TechCorp Inc.
```

### **Email 2.2: Confirmation with Corrections**
```
Subject: Re: Confirmation of Shipment Details
From: maria.garcia@importexport.com
To: sales@dpworld.com

Hi Alex,

Mostly correct, but please update:
- Weight should be 600 kg (not 500 kg)
- Volume is 3.0 CBM (not 2.5 CBM)
- Shipment date: March 5, 2024 (not March 1)

Everything else is correct. Please proceed.

Best regards,
Maria Garcia
ImportExport Solutions
```

### **Email 2.3: Confirmation with Additional Info**
```
Subject: Re: Confirmation of Shipment Details
From: david.chen@chemicals.com
To: sales@dpworld.com

Hi Michael,

Yes, all details are correct. Also, please note:
- Pickup address: 123 Chemical Street, Singapore
- Delivery address: 456 Industrial Zone, Hamburg
- Contact person: Dr. Hans Mueller (Hamburg)

Please proceed with booking.

Thanks,
David Chen
Chemical Solutions Ltd.
```

---

## 🎯 **TEST SCENARIO 3: Customer Clarification (Providing Missing Information)**

### **Email 3.1: Providing Missing Ports**
```
Subject: Re: Missing Information Request
From: john.smith@techcorp.com
To: sales@dpworld.com

Hi James,

Here are the missing details:
- Origin: Shanghai, China
- Destination: Los Angeles, USA
- Container: 40ft HC
- Weight: 15 tons

Please proceed.

Thanks,
John Smith
```

### **Email 3.2: Providing Missing Dates**
```
Subject: Re: Shipment Date Required
From: maria.garcia@importexport.com
To: sales@dpworld.com

Hi Alex,

The shipment date is March 1, 2024.
Ready date is February 25, 2024.

Please update and send confirmation.

Best regards,
Maria Garcia
```

### **Email 3.3: Providing Missing Commodity**
```
Subject: Re: Commodity Information Needed
From: david.chen@chemicals.com
To: sales@dpworld.com

Hi Michael,

The commodity is:
- Chemical products (UN 3082)
- Class 9 dangerous goods
- 100 drums of industrial chemicals

Please proceed with the quote.

Thanks,
David Chen
```

---

## 🎯 **TEST SCENARIO 4: Customer Rate Inquiry (Following Up)**

### **Email 4.1: Rate Status Inquiry**
```
Subject: Re: Rate Request Status
From: john.smith@techcorp.com
To: sales@dpworld.com

Hi James,

Any update on the rates for our Shanghai to Los Angeles shipment?
We need to finalize this by end of week.

Thanks,
John Smith
```

### **Email 4.2: Rate Comparison Request**
```
Subject: Re: Rate Comparison Needed
From: maria.garcia@importexport.com
To: sales@dpworld.com

Hi Alex,

Can you provide a breakdown of the rates?
We need to compare with other providers.

Also, what's the transit time?

Best regards,
Maria Garcia
```

---

## 🎯 **TEST SCENARIO 5: Customer Booking Request (Ready to Proceed)**

### **Email 5.1: Direct Booking Request**
```
Subject: Re: Ready to Book
From: john.smith@techcorp.com
To: sales@dpworld.com

Hi James,

We're ready to proceed with the booking.
Please send us the booking confirmation.

Thanks,
John Smith
```

### **Email 5.2: Booking with Specific Requirements**
```
Subject: Re: Booking Confirmation
From: maria.garcia@importexport.com
To: sales@dpworld.com

Hi Alex,

Yes, please proceed with booking. We need:
- Booking confirmation by tomorrow
- Container pickup on February 25
- Delivery by March 10

Please confirm.

Best regards,
Maria Garcia
```

---

## 🎯 **TEST SCENARIO 6: Forwarder Response (Rate Quotes)**

### **Email 6.1: Forwarder Rate Quote**
```
Subject: Re: Rate Request - Shanghai to Los Angeles
From: rates@globallogistics.com
To: sales@dpworld.com

Dear DP World Team,

Thank you for your rate request. Please find our competitive quote:

**Rate Details:**
- Ocean Freight: USD 2,500 per 40HC
- THC Origin: USD 150
- THC Destination: USD 200
- Documentation: USD 50
- Total: USD 2,900

**Transit Time:** 18 days
**Valid Until:** February 28, 2024
**Sailing Date:** February 20, 2024

Please let us know if you need any clarification.

Best regards,
Global Logistics Partners
rates@globallogistics.com
+1-800-555-0123
```

### **Email 6.2: Forwarder Inquiry for More Details**
```
Subject: Re: Rate Request - Additional Information Needed
From: quotes@maritimefreight.com
To: sales@dpworld.com

Dear DP World Team,

We received your rate request. However, we need additional information:

1. Exact commodity description
2. Dangerous goods classification (if any)
3. Special handling requirements
4. Preferred sailing dates

Please provide these details for accurate quoting.

Best regards,
Maritime Freight Solutions
quotes@maritimefreight.com
+1-800-555-0456
```

### **Email 6.3: Forwarder Acknowledgment**
```
Subject: Re: Rate Request Received
From: sales@oceancargo.com
To: sales@dpworld.com

Dear DP World Team,

We have received your rate request for Rotterdam to Miami shipment.

We are processing your request and will provide our competitive quote within 24 hours.

Thank you for considering Ocean Cargo Solutions.

Best regards,
Ocean Cargo Solutions
sales@oceancargo.com
+1-800-555-0789
```

---

## 🎯 **TEST SCENARIO 7: Confusing/Ambiguous Emails**

### **Email 7.1: Vague Response**
```
Subject: Re: Rate Request
From: john.smith@techcorp.com
To: sales@dpworld.com

Hi,

Thanks.

John
```

### **Email 7.2: Mixed Intent**
```
Subject: Re: Shipment Details
From: maria.garcia@importexport.com
To: sales@dpworld.com

Hi Alex,

Maybe we can proceed, but I'm not sure about the rates.
Can you check with someone else?

Also, we might need to change the dates.

Let me think about it.

Maria
```

### **Email 7.3: Unclear Context**
```
Subject: Re: Update
From: david.chen@chemicals.com
To: sales@dpworld.com

Hi,

Will check and get back to you.

David
```

---

## 🎯 **TEST SCENARIO 8: Non-Logistics Emails**

### **Email 8.1: Meeting Invitation**
```
Subject: Team Meeting - Q1 Review
From: hr@techcorp.com
To: sales@dpworld.com

Hi Team,

Please join us for the Q1 review meeting on Friday at 2 PM.

Agenda:
- Q1 performance review
- Q2 planning
- Team updates

Best regards,
HR Team
```

### **Email 8.2: Marketing Newsletter**
```
Subject: Monthly Newsletter - March 2024
From: marketing@dpworld.com
To: sales@dpworld.com

Hi,

Check out our latest newsletter with industry updates and company news.

Best regards,
Marketing Team
```

---

## 🎯 **TEST SCENARIO 9: Complex Business Cases**

### **Email 9.1: Multiple Shipments**
```
Subject: Multiple Shipment Quote Request
From: logistics@megacorp.com
To: sales@dpworld.com

Hi,

We need quotes for multiple shipments:

**Shipment 1:**
- Origin: Shanghai to Los Angeles
- Container: 40HC
- Weight: 20 tons
- Date: March 1, 2024

**Shipment 2:**
- Origin: Rotterdam to Miami
- Container: 20GP
- Weight: 10 tons
- Date: March 15, 2024

**Shipment 3:**
- Origin: Singapore to Hamburg
- Container: 40HC
- Weight: 25 tons
- Date: April 1, 2024

Please provide rates for all three shipments.

Thanks,
Logistics Team
MegaCorp International
```

### **Email 9.2: Urgent Shipment**
```
Subject: URGENT - Express Shipment Needed
From: emergency@pharma.com
To: sales@dpworld.com

Hi,

We have an URGENT shipment of pharmaceutical products:

Origin: Frankfurt, Germany
Destination: New York, USA
Container: 20GP
Weight: 5 tons
Commodity: Pharmaceutical products (temperature controlled)
Shipment date: ASAP (within 48 hours)

This is a medical emergency shipment. Please provide express rates and availability.

Thanks,
Emergency Logistics Team
PharmaCorp
```

---

## 🎯 **TEST SCENARIO 10: Edge Cases**

### **Email 10.1: Incomplete Information**
```
Subject: Shipping Quote
From: test@company.com
To: sales@dpworld.com

Hi,

I need a quote for shipping.

Thanks,
Test User
```

### **Email 10.2: Very Long Email**
```
Subject: Comprehensive Shipping Requirements
From: detailed@company.com
To: sales@dpworld.com

Hi Sarah,

I hope this email finds you well. I am writing to request a comprehensive quote for our upcoming shipment that involves multiple components and special requirements.

**Background:**
Our company, Detailed Solutions Inc., has been in the manufacturing business for over 25 years, specializing in precision engineering components. We have been working with various logistics providers over the years, but we are looking for a more reliable and cost-effective solution for our expanding operations.

**Shipment Details:**

**Origin Information:**
- Port: Shanghai, China
- Address: 123 Industrial Park, Shanghai Free Trade Zone
- Contact: Mr. Li Wei (Factory Manager)
- Phone: +86-21-1234-5678
- Email: li.wei@factory.com

**Destination Information:**
- Port: Los Angeles, USA
- Address: 456 Distribution Center, Los Angeles Port Area
- Contact: Mr. John Smith (Logistics Manager)
- Phone: +1-555-123-4567
- Email: john.smith@company.com

**Cargo Details:**
- Container Type: 40ft High Cube (40HC)
- Quantity: 2 containers
- Weight: 30 tons total (15 tons per container)
- Volume: 120 CBM total (60 CBM per container)
- Commodity: Precision engineering components
- HS Code: 8483.40.00

**Special Requirements:**
1. **Temperature Control:** Maintain temperature between 18-22°C
2. **Humidity Control:** Relative humidity 45-55%
3. **Vibration Protection:** Shock-absorbing packaging required
4. **Insurance:** All-risk insurance coverage for full value
5. **Customs Clearance:** Full customs clearance service required
6. **Documentation:** Complete documentation package including:
   - Commercial invoice
   - Packing list
   - Certificate of origin
   - Quality certificates
   - Insurance certificates

**Timeline Requirements:**
- Ready date: March 1, 2024
- Shipment date: March 5, 2024
- Required delivery: March 25, 2024 (maximum)

**Additional Services Needed:**
1. **Pickup Service:** From factory to port
2. **Port Handling:** Loading and securing
3. **Ocean Transport:** Direct service preferred
4. **Port Handling:** Unloading and customs clearance
5. **Delivery Service:** From port to final destination
6. **Tracking:** Real-time shipment tracking
7. **Documentation:** Complete documentation management

**Quality Requirements:**
- ISO 9001 certified handling
- GDP (Good Distribution Practice) compliance
- Temperature monitoring throughout transit
- Regular status updates (daily during transit)

**Budget Considerations:**
- We have a budget of USD 15,000 per container
- Need competitive rates while maintaining quality
- Prefer all-inclusive pricing

**Previous Experience:**
We have had some issues with previous providers regarding:
- Delays in customs clearance
- Temperature fluctuations
- Poor communication
- Hidden charges

**Questions:**
1. Can you provide a detailed breakdown of all costs?
2. What is your transit time guarantee?
3. Do you provide real-time tracking?
4. What is your claims process?
5. Can you provide references from similar shipments?

**Next Steps:**
Please provide a comprehensive quote including:
- Detailed cost breakdown
- Service timeline
- Quality assurance measures
- Insurance coverage details
- Terms and conditions

We are looking to establish a long-term partnership, so please provide your best rates and service commitment.

I look forward to your detailed response.

Best regards,
Sarah Johnson
Senior Logistics Manager
Detailed Solutions Inc.
Email: sarah.johnson@detailed.com
Phone: +1-555-987-6543
Mobile: +1-555-123-4567
```

---

## 🎯 **HOW TO USE THESE TEST EMAILS**

### **1. Sequential Testing (Recommended for Demo)**
```python
# Test the complete workflow
test_sequence = [
    "1.1 Basic FCL Request",      # New thread, customer_quote_request
    "2.1 Simple Confirmation",    # thread_confirmation, customer_confirmation
    "6.1 Forwarder Rate Quote",   # thread_forwarder_interaction, forwarder_rate_quote
]

# Expected flow:
# Email 1.1 → send_confirmation_request
# Email 2.1 → booking_details_confirmed_assign_forwarders
# Email 6.1 → send_forwarder_response_to_customer
```

### **2. Individual Agent Testing**
```python
# Test specific agents
classification_tests = ["1.1", "2.1", "3.1", "4.1", "5.1", "6.1", "7.1", "8.1"]
extraction_tests = ["1.2", "1.3", "9.1", "10.2"]  # Rich data emails
validation_tests = ["1.2", "1.3", "2.2"]  # Emails with special requirements
```

### **3. Edge Case Testing**
```python
# Test system robustness
edge_cases = ["7.1", "7.2", "7.3", "8.1", "8.2", "10.1", "10.2"]
```

### **4. Demo Script**
```python
# Perfect demo sequence
demo_sequence = [
    {
        "email": "1.1 Basic FCL Request",
        "expected": "new_thread → customer_quote_request → send_confirmation_request",
        "highlight": "Data extraction and professional response"
    },
    {
        "email": "2.1 Simple Confirmation", 
        "expected": "thread_confirmation → customer_confirmation → booking_details_confirmed_assign_forwarders",
        "highlight": "Forwarder assignment and rate request emails"
    },
    {
        "email": "6.1 Forwarder Rate Quote",
        "expected": "thread_forwarder_interaction → forwarder_rate_quote → send_forwarder_response_to_customer", 
        "highlight": "Forwarder response handling"
    }
]
```

---

## 🎯 **EXPECTED OUTCOMES**

### **For Each Email Type:**

1. **New Requests (1.x)**: Should trigger data extraction → validation → confirmation request
2. **Confirmations (2.x)**: Should trigger forwarder assignment → rate request emails
3. **Clarifications (3.x)**: Should trigger additional extraction → validation → confirmation
4. **Rate Inquiries (4.x)**: Should trigger rate status response
5. **Booking Requests (5.x)**: Should trigger booking confirmation
6. **Forwarder Responses (6.x)**: Should trigger customer notification
7. **Confusing Emails (7.x)**: Should trigger escalation to human
8. **Non-Logistics (8.x)**: Should be classified as non-logistics
9. **Complex Cases (9.x)**: Should handle multiple shipments or urgent cases
10. **Edge Cases (10.x)**: Should handle gracefully with appropriate responses

### **Key Testing Points:**
- ✅ **Classification Accuracy**: Correct email type detection
- ✅ **Extraction Quality**: Complete data extraction
- ✅ **Validation Logic**: Business rule compliance
- ✅ **Response Generation**: Professional, context-aware responses
- ✅ **Forwarder Assignment**: Appropriate forwarder selection
- ✅ **Escalation Logic**: Human handoff for complex cases
- ✅ **Error Handling**: Graceful handling of edge cases

Use these emails to thoroughly test your system and demonstrate its capabilities during your demo! 🚀 