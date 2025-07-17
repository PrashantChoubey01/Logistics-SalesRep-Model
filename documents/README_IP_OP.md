Ran tool
Ran tool
Read file: agents/forwarder_assignment_agent.py
Here is a document summarizing the **input and output requirements for each agent** in your `agents/` directory. This is based on class docstrings, method signatures, and code comments.

---

## 1. **ClassificationAgent**
- **Input:**  
  ```python
  {
    "email_text": str,      # Required, raw email content
    "subject": str,         # Required, email subject
    "thread_id": str        # Optional, thread identifier
  }
  ```
- **Output:**  
  ```python
  {
    "email_type": str,      # One of: logistics_request, confirmation_reply, forwarder_response, clarification_reply, non_logistics
    "confidence": float,    # 0.0 - 1.0
    "urgency": str,         # low, medium, high
    "requires_action": bool,
    "key_indicators": list[str],
    "reasoning": str,
    ... # plus agent_name, agent_id, processed_at, status
  }
  ```

---

## 2. **ExtractionAgent**
- **Input:**  
  ```python
  {
    "email_text": str,      # Required
    "subject": str          # Optional
  }
  ```
- **Output:**  
  ```python
  {
    "origin": str,
    "destination": str,
    "shipment_type": str,
    "container_type": str,
    "quantity": str,
    "weight": str,
    "volume": str,
    "shipment_date": str,
    "commodity": str,
    "dangerous_goods": str,
    "special_requirements": str,
    "extraction_method": str,
    ... # plus agent_name, agent_id, processed_at, status
  }
  ```

---

## 3. **ValidationAgent**
- **Input:**  
  ```python
  {
    "extraction_data": dict,    # Required, output from ExtractionAgent
    "email_type": str           # Optional, default: "logistics_request"
  }
  ```
- **Output:**  
  ```python
  {
    "overall_validity": bool,
    "completeness_score": float,
    "validation_details": dict,
    "missing_fields": list[str],
    "invalid_fields": list[str],
    "warnings": list[str],
    "recommendations": list[str],
    "validated_data": dict,
    ... # plus agent_name, agent_id, processed_at, status
  }
  ```

---

## 4. **ClarificationAgent**
- **Input:**  
  ```python
  {
    "extraction_data": dict,    # Output from ExtractionAgent
    "validation": dict,         # Output from ValidationAgent
    "missing_fields": list[str],# Optional, overrides validation["missing_fields"]
    "thread_id": str            # Optional
  }
  ```
- **Output:**  
  ```python
  {
    "clarification_needed": bool,
    "message": str,
    "missing_fields": list[str],
    ... # plus agent_name, agent_id, processed_at, status
  }
  ```

---

## 5. **ConfirmationAgent**
- **Input:**  
  ```python
  {
    "email_text": str,      # Required
    "subject": str,         # Required
    "thread_id": str        # Optional
  }
  ```
- **Output:**  
  ```python
  {
    "confirmation_type": str,   # booking_confirmation, quote_acceptance, shipment_approval, schedule_confirmation, document_approval, no_confirmation
    "confidence": float,
    "reasoning": str,
    ... # plus agent_name, agent_id, processed_at, status
  }
  ```

---

## 6. **PortLookupAgent**
- **Input:**  
  ```python
  {
    "port_name": str,           # For single lookup
    # OR
    "port_names": list[str]     # For multiple lookups
  }
  ```
- **Output:**  
  - For single:
    ```python
    {
      "port_code": str,
      "port_name": str,
      "confidence": float,
      "method": str,
      ... # plus agent_name, agent_id, processed_at, status
    }
    ```
  - For multiple:
    ```python
    {
      "results": list[dict]
    }
    ```

---

## 7. **ContainerStandardizationAgent**
- **Input:**  
  ```python
  {
    "container_description": str,        # For single
    # OR
    "container_descriptions": list[str], # For multiple
    # OR
    "container_type": str                # Alternative key
  }
  ```
- **Output:**  
  - For single:
    ```python
    {
      "standardized_container": str,
      ... # plus agent_name, agent_id, processed_at, status
    }
    ```
  - For multiple:
    ```python
    {
      "results": list[dict],
      "total_processed": int
    }
    ```

---

## 8. **CountryExtractorAgent**
- **Input:**  
  ```python
  {
    "port_code": str,                   # Required
    "include_recommendations": bool     # Optional, default True
  }
  ```
- **Output:**  
  ```python
  {
    "country": str,
    "recommended_countries": list[str], # If requested
    ... # plus agent_name, agent_id, processed_at, status
  }
  ```

---

## 9. **RateRecommendationAgent**
- **Input:**  
  ```python
  {
    "Origin_Code": str,         # Required
    "Destination_Code": str,    # Required
    "Container_Type": str       # Required
  }
  ```
- **Output:**  
  ```python
  {
    "query": dict,
    "rate_recommendation": {
      "match_type": str,
      "total_rates_found": int,
      "rate_range": str
    },
    "indicative_rate": str,
    "data_source": str,
    "total_records_searched": int,
    ... # plus agent_name, agent_id, processed_at, status
  }
  ```

---

## 10. **RateParserAgent**
- **Input:**  
  ```python
  {
    "email_text": str,      # Required
    "subject": str          # Optional
  }
  ```
- **Output:**  
  ```python
  {
    "parsed_rates": dict,   # Structure depends on LLM or regex extraction
    ... # plus agent_name, agent_id, processed_at, status
  }
  ```

---

## 11. **ForwarderAssignmentAgent**
- **Input:**  
  ```python
  {
    "origin_country": str,          # Required
    "destination_country": str      # Required
  }
  ```
- **Output:**  
  ```python
  {
    "origin_forwarders": list[str],
    "destination_forwarders": list[str],
    "both_countries": list[str],
    "all_matches": list[str],
    "status": str                   # "success" or "no_match"
  }
  ```

---

## 12. **EscalationAgent**
- **Input:**  
  ```python
  {
    "email_text": str,      # Required
    "subject": str,         # Required
    "prior_results": dict   # Optional, previous agent results
  }
  ```
- **Output:**  
  ```python
  {
    "escalate": bool,
    "reason": str,
    "escalation_type": str,
    "escalation_message": str,
    "suggested_next_action": str,
    ... # plus agent_name, agent_id, processed_at, status
  }
  ```

---

## 13. **ResponseGeneratorAgent**
- **Input:**  
  ```python
  {
    "classification_data": dict,
    "extraction_data": dict,
    "validation_data": dict,
    "clarification_data": dict,
    "confirmation_data": dict,
    "rate_data": dict,
    "port_data": dict,
    "container_data": dict,
    "country_data": dict,
    "subject": str,
    "email_text": str,
    "thread_id": str
  }
  ```
- **Output:**  
  ```python
  {
    "response_type": str,
    "response_subject": str,
    "response_body": str,
    "tone": str,
    "key_information_included": list[str],
    "attachments_needed": list[str],
    "next_steps": str,
    ... # plus agent_name, agent_id, processed_at, status
  }
  ```

---

## 14. **MemoryAgent**
- **Input:**  
  ```python
  {
    "action": "store" | "retrieve" | "clear",
    "thread_id": str,
    "message": dict,    # For store
    "limit": int        # For retrieve (optional)
  }
  ```
- **Output:**  
  - For store:
    ```python
    {
      "status": "stored",
      "thread_id": str,
      "entry": dict
    }
    ```
  - For retrieve:
    ```python
    {
      "status": "retrieved",
      "thread_id": str,
      "history": list[dict]
    }
    ```
  - For clear:
    ```python
    {
      "status": "cleared",
      "thread_id": str
    }
    ```

---

## 15. **LoggingAgent**
- **Input:**  
  ```python
  {
    "event_type": "info" | "error" | "metric" | "audit",
    "message": str,
    "agent_name": str,
    "details": dict (optional)
  }
  ```
- **Output:**  
  ```python
  {
    "status": "logged",
    "log_entry": dict
  }
  ```

---

If you want this as a markdown, PDF, or other format, or want to include/exclude any details, let me know!