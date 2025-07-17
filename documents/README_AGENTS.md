# 🤖 Agentic AI System for Intelligent Email Processor

## 🏗️ Multi-Agent Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                          │
│              (Workflow Coordination)                            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼───┐        ┌───▼───┐        ┌───▼───┐
│EMAIL  │        │CLASSI-│        │EXTRAC-│
│INGEST │───────▶│FIER   │───────▶│TION   │
│AGENT  │        │AGENT  │        │AGENT  │
└───────┘        └───────┘        └───────┘
    │                 │                 │
    ▼                 ▼                 ▼
┌───────┐        ┌───────┐        ┌───────┐
│VALIDA-│        │CLARIF-│        │CONFIR-│
│TION   │───────▶│ICATION│───────▶│MATION │
│AGENT  │        │AGENT  │        │AGENT  │
└───────┘        └───────┘        └───────┘
    │                 │                 │
    ▼                 ▼                 ▼
┌───────┐        ┌───────┐        ┌───────┐
│FORWARD│        │RATE   │        │RESPONSE│
│ASSIGN │───────▶│PARSER │───────▶│GENERA-│
│AGENT  │        │AGENT  │        │TOR    │
└───────┘        └───────┘        └───────┘
    │                 │                 │
    ▼                 ▼                 ▼
┌───────┐        ┌───────┐        ┌───────┐
│ESCALA-│        │MEMORY │        │LOGGING│
│TION   │        │AGENT  │        │AGENT  │
│AGENT  │        │       │        │       │
└───────┘        └───────┘        └───────┘
```

---

## 🎯 Agent Specifications

### 1. 📧 **Email Ingestion Agent**
- **Purpose**: Monitor and ingest emails from multiple sources
- **Model**: `cdpz_datascience.ml_models.email_ingestion_agent`
- **Capabilities**:
  - IMAP/Gmail API monitoring
  - Email parsing and metadata extraction
  - Duplicate detection
  - Thread tracking
- **Output**: Structured email data to orchestrator

### 2. 🧠 **Classification Agent**
- **Purpose**: Classify email intent and urgency
- **Model**: `cdpz_datascience.ml_models.email_classifier_agent`
- **Capabilities**:
  - Intent classification (logistics_request, confirmation, etc.)
  - Confidence scoring
  - Urgency detection
  - Language detection
- **Output**: Classification results with confidence scores

### 3. 📦 **Extraction Agent**
- **Purpose**: Extract structured shipment information
- **Model**: `cdpz_datascience.ml_models.shipment_extraction_agent`
- **Capabilities**:
  - NER for logistics entities
  - Port/container code recognition
  - Date/quantity parsing
  - Commodity classification
- **Output**: Structured shipment data

### 4. ✅ **Validation Agent**
- **Purpose**: Validate and enrich extracted data
- **Model**: `cdpz_datascience.ml_models.validation_agent`
- **Capabilities**:
  - Port code validation via FAISS
  - Container type validation
  - Date feasibility checks
  - Completeness scoring
- **Output**: Validation results and missing fields

### 5. ❓ **Clarification Agent**
- **Purpose**: Generate clarification requests
- **Model**: `cdpz_datascience.ml_models.clarification_agent`
- **Capabilities**:
  - Smart question generation
  - Context-aware templates
  - Multi-language support
  - Escalation triggers
- **Output**: Clarification emails and tracking

### 6. ✅ **Confirmation Agent**
- **Purpose**: Detect and process confirmations
- **Model**: `cdpz_datascience.ml_models.confirmation_agent`
- **Capabilities**:
  - Confirmation signal detection
  - Intent matching
  - Status updates
  - Workflow progression
- **Output**: Confirmation status and next actions

### 7. 🚚 **Forwarder Assignment Agent**
- **Purpose**: Match shipments to optimal forwarders
- **Model**: `cdpz_datascience.ml_models.forwarder_assignment_agent`
- **Capabilities**:
  - Route optimization
  - Capacity matching
  - Performance scoring
  - Load balancing
- **Output**: Forwarder assignments with reasoning

### 8. 💰 **Rate Parser Agent**
- **Purpose**: Parse and analyze rate quotes
- **Model**: `cdpz_datascience.ml_models.rate_parser_agent`
- **Capabilities**:
  - Quote extraction
  - Currency normalization
  - Terms analysis
  - Competitive comparison
- **Output**: Structured rate data

### 9. 📝 **Response Generator Agent**
- **Purpose**: Generate customer responses
- **Model**: `cdpz_datascience.ml_models.response_generator_agent`
- **Capabilities**:
  - Personalized responses
  - Multi-format output
  - Brand voice consistency
  - Attachment handling
- **Output**: Customer-ready responses

### 10. ⚠️ **Escalation Agent**
- **Purpose**: Handle complex scenarios and escalations
- **Model**: `cdpz_datascience.ml_models.escalation_agent`
- **Capabilities**:
  - Anomaly detection
  - Confidence thresholding
  - Human handoff
  - Priority routing
- **Output**: Escalation decisions and routing

### 11. 🧠 **Memory Agent**
- **Purpose**: Maintain conversation context and history
- **Model**: `cdpz_datascience.ml_models.memory_agent`
- **Capabilities**:
  - Conversation threading
  - Context retrieval
  - Relationship mapping
  - Historical analysis
- **Output**: Context-enriched data

### 12. 📊 **Logging Agent**
- **Purpose**: Comprehensive system monitoring and logging
- **Model**: `cdpz_datascience.ml_models.logging_agent`
- **Capabilities**:
  - Performance monitoring
  - Error tracking
  - Audit trails
  - Analytics generation
- **Output**: Logs and metrics

### 13. 🎭 **Orchestrator Agent**
- **Purpose**: Coordinate all agents and manage workflow
- **Model**: `cdpz_datascience.ml_models.orchestrator_agent`
- **Capabilities**:
  - Workflow management
  - Agent coordination
  - State management
  - Error recovery
- **Output**: Workflow decisions and routing





# 📧 Agentic Email Processor: Orchestrator Workflow (Textual, End-to-End)

---

## **1. Email Ingestion**
- New email arrives (from customer or forwarder).
- Orchestrator receives: subject, body, thread ID, and any prior context.

---

## **2. Classification**
- **Call:** Classification Agent
- **Result:**  
  - `logistics_request` (customer asking for quote/shipping)
  - `forwarder_response` (forwarder sending quote/rate)
  - `confirmation_reply` (customer confirming)
  - `clarification_reply` (customer providing missing info)
  - `non_logistics` (ignore or forward to support)

---

## **3. If Email is from Customer (`logistics_request`):**

### a. **Extraction**
- **Call:** Extraction Agent
- **Result:** Extract shipment details (origin, destination, type, etc.)

### b. **Validation**
- **Call:** Validation Agent
- **Result:** Check for completeness and correctness.

### c. **Decision: Is the request complete?**
- **If complete and valid:**
    1. **Forwarder Assignment**
        - **Call:** Forwarder Assignment Agent
        - **Result:** Select best forwarder(s) for the shipment.
    2. **Send Rate Request to Forwarder(s)**
        - **Call:** Response Generator Agent
        - **Action:**  
            - Generate and send an email to the selected forwarder(s), including:
                - All customer shipment requirements.
                - Any special instructions/context.
                - **CC the sales person**.
            - Subject: “Rate Request: [Origin] to [Destination] for [Customer/Company]”
            - Body: Clearly state shipment details and request a quote/rate.
    3. **Notify Sales (optional)**
        - **Call:** Response Generator Agent
        - **Action:** Notify sales that rate request was sent.
    4. **STOP** and wait for forwarder’s reply.
- **If missing/unclear info:**
    - **If this is the first time clarification is needed:**
        1. **Clarification**
            - **Call:** Clarification Agent
            - **Action:** Send a single clarification request to the customer.
            - Mark `clarification_attempted = True` for this thread.
        2. **STOP** and wait for customer reply.
    - **If clarification already attempted or confidence is low:**
        1. **Escalation**
            - **Call:** Escalation Agent
            - **Action:** Escalate to human (sales person) with all context and summary of missing/unclear info.
        2. **STOP** further bot actions for this thread.

---

## **4. If Email is from Customer (`clarification_reply`):**
- **Repeat Extraction and Validation.**
- If now complete, proceed as above (forwarder assignment, etc.).
- If still incomplete and clarification already attempted, escalate to human.

---

## **5. If Email is from Forwarder (`forwarder_response`):**

### a. **Rate Parsing**
- **Call:** Rate Parser Agent
- **Result:** Extract quote/rate details.

### b. **Validation (optional)**
- **Call:** Validation Agent (optional)
- **Result:** Validate quote/rate against requirements.

### c. **Notify Sales**
- **Call:** Response Generator Agent
- **Action:**  
    - Generate and send an email to the sales person, including:
        - Forwarder’s quote/rate details.
        - Any validation results.
    - Sales person will connect with customer to share quote or clarify further.

### d. **STOP** and wait for customer confirmation or further questions.

---

## **6. If Email is from Customer (`confirmation_reply`):**

### a. **Confirmation**
- **Call:** Confirmation Agent
- **Result:** Detect/process confirmation.

### b. **Notify Customer, Sales, and/or Forwarder**
- **Call:** Response Generator Agent
- **Action:**  
    - Send acknowledgment to customer.
    - Notify sales and/or forwarder as needed.

---

## **7. If Email is `non_logistics`:**
- **Forward to support or ignore.**

---

## **8. Logging and Memory**
- At each step, log actions and results via **Logging Agent**.
- Store/retrieve conversation context via **Memory Agent**.

---

## **9. Escalation**
- At any point, if:
    - The bot cannot understand the customer’s requirements after one clarification attempt,
    - Confidence is low,
    - An error or anomaly is detected,
- **Call:** Escalation Agent
- **Action:** Escalate to human (sales person), providing all context and a summary of the issue.

---

# 📝 **Summary Table**

| Step | Email Type           | Agent(s) Called                | Action/Decision/Output                                   |
|------|----------------------|-------------------------------|----------------------------------------------------------|
| 1    | Any                  | Classification                | Determine email type                                     |
| 2    | logistics_request    | Extraction, Validation        | Extract & validate shipment info                         |
| 3    | logistics_request    | Clarification (if needed)     | Ask customer for missing info (only once)                |
| 4    | logistics_request    | Escalation (if needed)        | Escalate to human if still unclear after clarification   |
| 5    | logistics_request    | Forwarder Assignment          | Assign best forwarder(s)                                 |
| 6    | logistics_request    | Response Generator            | **Send rate request email to forwarder(s), CC sales, with all customer requirements** |
| 7    | logistics_request    | Response Generator (optional) | Notify sales that rate request was sent                  |
| 8    | forwarder_response   | Rate Parser, Validation       | Parse quote/rate, validate                               |
| 9    | forwarder_response   | Response Generator            | Notify sales with forwarder’s quote                      |
| 10   | confirmation_reply   | Confirmation                  | Detect/process confirmation                              |
| 11   | confirmation_reply   | Response Generator            | Acknowledge to customer, notify sales/forwarder          |
| 12   | clarification_reply  | Extraction, Validation        | Re-extract/validate, proceed or escalate as above        |
| 13   | non_logistics        | -                             | Forward to support/ignore                                |
| 14   | Any                  | Logging, Memory               | Log all actions, store/retrieve context                  |
| 15   | Any                  | Escalation                    | Escalate to human if error, anomaly, or low confidence   |

---

**This is your full, end-to-end orchestrator workflow.**  
It ensures:
- No endless clarification loops.
- Forwarders only contacted when requirements are complete.
- Sales is always in the loop.
- All actions are logged and context is maintained.
- Escalation to human happens if the bot cannot resolve after one clarification.

---

Let me know if you want the orchestrator agent code for this flow!