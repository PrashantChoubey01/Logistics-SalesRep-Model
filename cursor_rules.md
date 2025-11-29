Here’s a set of **clear rules you can paste into Cursor as “Project Rules / Guidelines”** so it always develops & tests this system in a way that keeps the **workflow reliable** and **email responses consistently good**, not just the individual agents.

I’ll write them as if I’m talking directly to Cursor / the coding assistant.

---

# 📏 Global Rules for Development in `logistic-ai-response-model`

## 0. Golden Principles

1. **Never break the workflow graph.**
   Any change to agents, schemas, or utilities **must preserve**:

   * The full LangGraph path described in the overview
   * The inputs/outputs of each step that downstream nodes depend on

2. **Agents are expendable; workflow invariants are not.**
   It is better to:

   * Add guardrails, fallbacks, or “safe defaults”
     Than to:
   * Return no email, crash the graph, or produce an incoherent response.

3. **Always code against the documented specs.**
   You MUST respect:

   * `Customer Email Input/Output Specification`
   * Cumulative merge logic
   * FCL/LCL business rules
   * Clarification vs confirmation behavior
     Do **not** “improvise” new behaviors unless explicitly requested.

---

# 1. Workflow & Orchestrator Rules

### 1.1 Workflow Shape Must Stay Intact

The LangGraph flow **must always preserve** this main path (logistics emails):

```text
classify_email → conversation_state → analyze_thread → extract_information
→ update_cumulative_extraction → validate_data → lookup_ports
→ standardize_container → recommend_rates → next_action
→ assign_sales_person → [one response agent] → update_thread
```

For forwarder + complaint branches, the paths from the spec must also be kept.

**Rules:**

1. Do **not** remove or bypass any of these nodes.
2. If you add extra processing steps:

   * Insert them between existing nodes
   * Make sure their inputs/outputs do not break downstream expectations.
3. `LangGraphWorkflowOrchestrator.process_email()` **must always** return:

   * The generated outbound email (subject + body)
   * The final `WorkflowState` (with `cumulative_extraction`, `conversation_state`, etc.)

### 1.2 Conditional Routing Must Follow Business Logic

When changing or adding conditions:

* **After Classification**

  * `logistics_request` → full workflow path described above
  * `non_logistics` → acknowledgment → `update_thread`
  * `forwarder_response` → forwarder-related path

* **NextActionAgent Output → Routing**

  * `send_clarification_request` → `ClarificationResponseAgent`
  * `send_confirmation_request` → `ConfirmationResponseAgent`
  * `booking_details_confirmed_assign_forwarders` → `ConfirmationAcknowledgmentAgent` → `assign_forwarders`
  * `collate_rates_and_send_to_sales` → `SalesNotificationAgent` → `update_thread`

**MUST:** Keep these mappings **exact** unless explicitly changing business rules, in which case also update tests & docs.

---

# 2. Data Model & Merge Invariants

## 2.1 CumulativeExtraction Rules

For `ThreadManager.merge_with_recency_priority()`:

1. **Rule 1 – Non-empty overrides old:**
   New non-empty value replaces old.
2. **Rule 2 – Missing preserves old:**
   If a field is missing in the new data, keep the old value.
3. **Rule 3 – Missing category preserves old:**
   If a whole section (e.g. `contact_information`) is absent in the new extraction, keep the old section as-is.
4. **Empty strings MUST be treated as “no update”**, same as missing:

   * Do NOT overwrite existing values with empty strings for all business-critical fields.

Add / maintain tests to ensure **all three rules** hold for:

* `shipment_details`
* `container_details`
* `timeline_information`
* `rate_information`
* Any new sections in `CumulativeExtraction`

## 2.2 Extraction Rules

**InformationExtractionAgent MUST:**

1. Extract **only** from `body_text`.

   * Do **not** use `subject` for extraction (only for classification / context).
2. Never infer information not explicitly present in the email body.

   * E.g., do not guess Incoterm, shipment type, or dates.
3. Represent missing fields as **empty strings**, not `null`.

Add tests verifying:

* Subject-only values are NOT extracted.
* Fields never appear in extraction if only implied, not stated.

---

# 3. FCL / LCL & Validation Rules

## 3.1 FCL Logic

For **Full Container Load (FCL)**:

* Required:

  * Origin
  * Destination
  * Container Type (e.g. 20GP, 40GP, 40HC)
  * Shipment Date (Ready date/ETD)
* Not required:

  * Volume
* Weight is **optional** (do not mark as required).
* If `container_type` is present → **assume FCL** and apply FCL rules.

## 3.2 LCL Logic

For **Less Than Container Load (LCL)**:

* Required:

  * Origin
  * Destination
  * Weight
  * Volume
  * Shipment Date
* Not required:

  * Container Type
* Both `weight` AND `volume` must be present to consider LCL complete.

## 3.3 ValidationAgent Rules

`DataValidationAgent` must:

1. Determine missing fields **based on FCL/LCL rules**.
2. Validate dates (format + non-obviously-invalid).
3. Validate ports (ensure enriched ports are valid).
4. Populate `missing_fields` in priority order:

   1. Origin & Destination
   2. Container Type (FCL) & Shipment Date
   3. Commodity, Weight/Volume
   4. Contact info, special requirements

**Never** block forwarder assignment solely because of **non-critical** missing fields after customer confirmation.

---

# 4. Email Response Formatting Rules

## 4.1 Clarification vs Confirmation – Display Rules

**ClarificationResponseAgent MUST:**

* Show **enriched ports with port codes**:

  * `Shanghai (CNSHG)`
  * `Los Angeles (USLAX)`
* Show **standardized container types** (e.g. `40HC`).
* Display **all successfully extracted + enriched data**, then list missing items.
* Ask **specific, prioritized questions** about missing critical fields.

**ConfirmationResponseAgent MUST:**

* Show:

  * Origin / Destination in clear human-friendly form (e.g., `Shanghai, China`),
  * Container types in standardized format (`40HC`, `20GP`, etc.).
* It is acceptable if port codes are omitted in confirmation emails, but:

  * Internally, the enriched port codes **must be used** for validation & forwarders.

## 4.2 Confirmation Acknowledgment Rules

When `email_type = customer_confirmation` and the customer confirms:

1. `ConfirmationAcknowledgmentAgent` MUST:

   * Restate the confirmed shipment details.
   * Indicate that booking / forwarder assignment is in progress.
2. Workflow MUST:

   * Trigger `assign_forwarders` with **enriched** route (e.g., CNSHG → USLAX).
   * Use standardized container types.

**CRITICAL:**
Customer confirmation **overrides validation issues** except clearly invalid data (e.g., impossible dates).
Do **not** block forwarder assignment due to minor missing fields.

## 4.3 Complaint & Non-Logistics Emails

For complaints (e.g. `COMPLAINT - Poor Service`):

* In happy flow:

  * Generate either:

    * Standard acknowledgment, or
    * A slightly more specific acknowledgment referencing booking ref if extracted.
* Do **not** escalate automatically unless an explicit escalation rule is added.
* Always respond professionally, minimally, and safely.

---

# 5. Forwarder Handling Rules

1. **ForwarderDetectionAgent** must detect forwarders via:

   * Email domain patterns,
   * Signature keywords,
   * Content cues.
2. For `forwarder_response`:

   * Extract rate info (price, currency, basis, transit time).
   * Attach this to `rate_information` in `CumulativeExtraction`.
3. `ForwarderEmailDraftAgent`:

   * Must use **enriched ports** + standardized containers.
   * Must not use incomplete / unvalidated critical fields.

Ensure tests cover:

* Forwarder detection for at least a few realistic domains.
* Rate extraction with different textual patterns.

---

# 6. Quality & Safety: Response Validation

`ResponseValidatorAgent` must be run **before** returning the final email:

* Evaluate:

  * Relevance (email answers the user’s actual need).
  * Accuracy (no fabricated ports, routes, or numbers).
  * Completeness (handles required info for the chosen action).
  * Professionalism (tone, formatting).
* If the validation score < threshold (e.g. 0.7):

  * Try to fix issues in a second pass **without** changing the workflow routing.
  * If still low, return the **safest** professional response (e.g., acknowledgment + request for clarification), not silence or a broken email.

---

# 7. Testing Rules

## 7.1 Must-Write-Tests Policy

**For any change to:**

* Agent logic,
* Workflow routing,
* Schemas,
* Merge logic,
* Response formatting,

You MUST:

1. Add or update unit tests in `tests/`:

   * Agent-specific tests: `test_<agent_name>.py`
   * Workflow-level tests: `test_workflow_validation.py`
2. Ensure:

   * `test_cumulative_merge_aggressive.py` covers any new fields/categories.
   * `test_date_validator.py` covers any new date formats/logic.

## 7.2 Test Scenarios Required

At minimum, for each main flow, maintain tests for:

1. **Complete FCL quote request** → Confirmation request email, no missing fields.
2. **Minimal information** → Clarification email with correct list of missing fields.
3. **Customer confirmation** → Confirmation acknowledgment + forwarder assignment triggered.
4. **Urgent complete request** → Same as complete request, but with “urgent” wording preserved in response.
5. **Complaint email** → Non-broken acknowledgment response.
6. **Forwarder rate email** → Correct detection, extraction, and sales notification.

Each test should:

* Feed realistic `InboundEmail` → `LangGraphWorkflowOrchestrator.process_email`.
* Assert:

  * `email_type`
  * `conversation_state`
  * `next_action`
  * Response subject & key lines in body
  * Critical parts of `cumulative_extraction`.

---

# 8. Logging, Errors & Robustness

1. **No hard crashes in normal flows.**
   If an agent fails:

   * Log the error,
   * Return a safe default,
   * Allow the workflow to still produce a professional response (e.g., a generic acknowledgment or a clarification request).

2. **Log at key stages** (debug/info level):

   * Classification result & confidence
   * Extracted info summary
   * Cumulative merge result
   * Validation result & missing fields
   * Next action decision

3. Do **not** leak raw stack traces or internal JSON to customers.

---

# 9. Prompting Rules for LLM-Based Agents

When editing agent prompts:

1. Make each agent:

   * **Single-responsibility** (classification, extraction, enrichment, etc.).
   * Output strictly in the expected schema (JSON / Pydantic-friendly).
2. Always:

   * Re-state the **business rules** in the prompt (FCL vs LCL, no inference, body-only extraction, etc.).
   * Include examples similar to the Customer Email Input/Output Specification.
3. Explicitly instruct:

   * “If information is not explicitly stated in the email body, leave the field as an empty string.”

---

If you put this file in the repo as something like `CURSOR_RULES.md` and also paste key parts into Cursor’s project rules, Cursor will have a very concrete contract:

* **What it can change**
* **What must never be broken**
* **What every response and test must respect**

If you want, next I can turn this into a shorter **“top 20 checks”** that you or your team can run mentally (or as a CI checklist) before merging any PR.
