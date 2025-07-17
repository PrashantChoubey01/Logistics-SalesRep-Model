## ✅ Modular Product Workflow: **Intelligent Email Processor**

### 🔁 **Workflow Lifecycle**

Each email goes through these stages — independently pluggable:

```
INGEST ➝ CLASSIFY ➝ EXTRACT ➝ VALIDATE ➝ CLARIFY ➝ CONFIRM ➝ ASSIGN ➝ FORWARDER COMM. ➝ RATE COLLECTION ➝ CUSTOMER RESPONSE ➝ ESCALATION (optional)
```

---

## 🧩 **Modular Steps**

### 1. 📥 Email Ingestion

* **Source**: Shared Gmail (customer, CRM, forwarder)
* **Method**: IMAP or Gmail API (external cron or webhook listener)
* **Output**: Email metadata + body saved to `received_replies` table

---

### 2. 🧠 Email Classification

* **Goal**: Label the type of email

* **Labels**:

  * `logistics_request`
  * `clarification_reply`
  * `confirmation_reply`
  * `forwarder_response`
  * `non_logistics`

* **Tool**: LLM or rules

* **Store in**: `received_replies` (add `email_type`, `confidence_score`)

---

### 3. 📦 Shipment Info Extraction

* **Parse from Email**:

  * `origin`, `destination` (port or country)
  * `shipment_type` (FCL/LCL)
  * `container_type`, `quantity`, `weight`, `volume`, `shipment_date`
  * `commodity`, `dangerous_goods`

* **Store in**: `extracted_shipments` table (or add fields to `received_replies`)

---

### 4. ✅ Shipment Info Validation

* **Use**:

  * FAISS vector search for port/container code lookup
  * Fuzzy matching + LLM fallback

* **Validation Rules**:

  * FCL → `container_type + quantity` required
  * LCL → `weight/volume` required
  * DG → ask for docs

* **Output**:

  * `completeness=True/False`
  * `missing_fields=[]`
  * `clarification_message=...`

---

### 5. ✉️ Clarification Handling

* **Trigger**: Missing/invalid/ambiguous data
* **Tool**: Clarification template generator
* **Send To**: Customer
* **Track**: # of clarification loops → stop if max attempts exceeded

---

### 6. ✅ Confirmation Detection

* **Trigger**: Customer replies to clarification or initial email
* **Logic**: LLM or keyword matcher
* **Store in**: `logistics_confirmations`

---

### 7. 🔁 Forwarder Assignment

* **Input**: Validated shipment info
* **Logic**:

  * Match `pol_country` + `pod_country`
  * Use `freight_forwarder_info` with rank by `capacity_score`
* **Output**: Assign `forwarder_id`, store in `booking_assignments`

---

### 8. 📤 Email to Forwarder

* **Goal**: Request rates
* **Info sent**: Validated shipment details
* **Tool**: SMTP send
* **Track**:

  * UUID
  * Email status (sent/delivered/failure)

---

### 9. 💰 Rate Quote Response

* **Read**: Replies from forwarders
* **Classify**: Use keyword/LLM to detect rate response
* **Extract**: Price, terms, transit, currency, validity
* **Store in**: `forwarder_quotes`

---

### 10. 📧 Customer Rate Email

* **Pick**: Best rate quote
* **Send**: Summary email with quote, codes, instructions
* **Log in**: `sent_emails`, `generated_response`

---

### 11. ⚠️ Escalation to Sales

* **Triggers**:

  * Low model confidence
  * Multiple clarification loops
  * Unhandled scenario
* **Send To**: `sales_inbox@example.com`

---
To implement the full **Intelligent Email Processor** product as per your finalized plan, here's a breakdown of the **complete development scope** by components, framework, and where each piece fits (Databricks, external Python app, Streamlit):

---

## ✅ 1. Architecture Overview

| Component                 | Framework / Tool        | Location            |
| ------------------------- | ----------------------- | ------------------- |
| Email reading (IMAP/API)  | `imaplib`, `gmail-api`  | External Python app |
| Email classification      | MLflow + LLM            | Databricks          |
| Shipment extraction       | MLflow + LLM            | Databricks          |
| Port/Container validation | FAISS + LLM fallback    | Databricks          |
| Clarification generator   | LangChain or Jinja2     | Databricks          |
| Confirmation detection    | Regex + LLM             | Databricks          |
| Forwarder assignment      | SQL + pandas + scoring  | Databricks          |
| Email sending (SMTP)      | `smtplib` or Gmail API  | External Python app |
| Rate quote parsing        | Regex + LLM             | Databricks          |
| Logging & DB writes       | PostgreSQL + Delta Lake | Both                |
| UI/debugging              | Streamlit               | Local/Test VM       |

---

## ✅ 2. Development Tasks (Team Checklist)

### 🔌 External Python Agent (for email I/O)

* [ ] Read from shared Gmail (IMAP or Gmail API)
* [ ] Parse subject, sender, and body
* [ ] Store emails in `received_replies`
* [ ] Trigger MLflow endpoint with email content
* [ ] Send emails to forwarders/customers (SMTP)
* [ ] Trigger scheduled run or webhook

### 🧠 ML + LLM Pipeline (Databricks)

* [ ] Build **MLflow model**: classify email intent
* [ ] Build **MLflow model**: extract shipment info
* [ ] Validate info using FAISS port/container embeddings
* [ ] Identify missing fields (FCL/LCL rules + DG)
* [ ] Generate clarification message
* [ ] Detect confirmation from customer replies
* [ ] Assign forwarders based on POL/POD country
* [ ] Generate forwarder email template
* [ ] Parse forwarder quote (rates, validity, currency)
* [ ] Generate final response for customer

### 📊 Logging / DB (Postgres or Delta)

* [ ] Tables for:

  * `sent_emails`
  * `received_replies`
  * `logistics_confirmations`
  * `booking_assignments`
  * `freight_forwarder_info`
  * `forwarder_quotes`
  * `api_call_logs`
* [ ] Functions to insert/update entries for each step
* [ ] Error logging (try/except + logs)

### 🧪 Streamlit Debug/Test UI

Already exists — to be extended with:

* [ ] `forwarder_quotes` insert/view
* [ ] `api_call_logs` insert/view
* [ ] Trigger MLflow test (simulate classification or extraction)

---

## ✅ 3. Optional Enhancements

* [ ] Agent memory using Redis/Postgres (email thread memory)
* [ ] Retry logic for clarification loop
* [ ] Confidence score-based escalation triggers
* [ ] Streamlit dashboard for:

  * Pending confirmations
  * Forwarder assignment queue
  * Email response tracker



Great! Since you've locked in the final product workflow and want to build each component **step-by-step**, here’s a breakdown of what development needs to be done in **phases**, specifically tailored for your project.

---

## ✅ Phase 1: Email Ingestion Service (External Python App)

### 📌 Goal:

* Read emails from a shared Gmail inbox (customer/forwarder/CRM)
* Extract body, subject, from/to, timestamp
* Save to `received_replies`

### 🔧 Tasks:

1. Create Python script with `imaplib` or `google-api-python-client`
2. Read unread emails (and optionally mark as read)
3. Extract:

   * UUID (from subject if reply, or generate new)
   * `received_from`, `received_at`, `customer_reply`
4. Insert into `received_replies` table via `psycopg2` or your `get_db_connection`

✅ **Output**: Independent script (cron/webhook based)

---

## ✅ Phase 2: MLflow Model – Email Classification (Databricks)

### 📌 Goal:

* Classify intent: `logistics_request`, `confirmation_reply`, etc.
* Return JSON with `classification` and `confidence`

### 🔧 Tasks:

1. Build MLflow model wrapper around OpenAI/Mistral/etc.
2. Log classification result into Delta/Postgres (`email_classifications`)
3. Save to MLflow model registry → for serving endpoint

✅ **Output**: `/classify_email` MLflow model ready for use

---

## ✅ Phase 3: MLflow Model – Shipment Info Extraction

### 📌 Goal:

* Extract and validate structured data from logistics requests

### 🔧 Fields:

* origin, destination (port/country)
* shipment type (FCL/LCL)
* container type & quantity
* weight / volume
* shipment date
* dangerous goods
* commodity

### 🔧 Tasks:

1. Extend MLflow model from Phase 2
2. Use regex or LLM extraction + validation layer
3. Log clarification needs (if any) to DB

✅ **Output**: `/extract_shipment_info` model

---

## ✅ Phase 4: Port & Container Validation (Databricks)

### 📌 Goal:

* Convert input strings → port code & container code
* Return mapping confidence

### 🔧 Tasks:

1. Build FAISS index for ports + container types
2. Add LLM fallback
3. Save mappings in Delta/MLflow artifacts
4. Log `mapping_confidence` in DB

✅ **Output**: Utility function/module

---

## ✅ Phase 5: Clarification Email Generator

### 📌 Goal:

* Auto-generate clarification emails for missing/invalid info

### 🔧 Tasks:

1. LangChain/Jinja2 templating
2. Include port, date, container checks from logic
3. Store in `sent_emails`

✅ **Output**: `/generate_clarification` model or function

---

## ✅ Phase 6: Confirmation Detector (Databricks)

### 📌 Goal:

* Detect confirmation signals in replies

### 🔧 Tasks:

1. Create regex + LLM model
2. Update `logistics_confirmations`
3. Set flags if confirmation=true

✅ **Output**: `/detect_confirmation` model

---

## ✅ Phase 7: Forwarder Assignment Logic

**Already partially done in Streamlit**

### 📌 Goal:

* From confirmed request → assign matching forwarder
* Use country matching or fallback strategy

### 🔧 Tasks:

* Improve scoring logic
* Prevent reassignment
* Create UI for manual override (optional)

✅ **Output**: Forwarder assigned in `booking_assignments`

---

## ✅ Phase 8: Forwarder Email + Quote Parsing

### 📌 Goal:

* Send booking details to forwarder
* Parse rate quotes in replies

### 🔧 Tasks:

* Add quote parsing model (`/parse_rate_quote`)
* Store in `forwarder_quotes`
* Log delivery terms, pricing, validity, etc.

✅ **Output**: Email → Rate → DB

---

## ✅ Phase 9: Final Quote Generator (Customer)

### 📌 Goal:

* Pick best quote and generate response to customer

### 🔧 Tasks:

* Jinja2 or LLM-based response engine
* Embed port codes, price range
* Log into `sent_emails`

✅ **Output**: `/generate_customer_quote` endpoint

---

## ✅ Phase 10: Escalation to Sales

### 📌 Goal:

* If confidence is low or 2+ clarifications sent → flag to sales

### 🔧 Tasks:

* Add escalation rule logic
* Send email to `sales@example.com`
* Log into `escalation_logs`

✅ **Output**: Alerting module

---

## ✅ Phase 11: Logging + Streamlit Monitoring

### 📌 Goal:

* Enable debugging, audit, and logs

### 🔧 Tasks:

* Log every API/model call
* Streamlit UI to view:

  * latest classification
  * confirmation attempts
  * rate logs
  * pending escalations

✅ **Output**: Full admin dashboard
