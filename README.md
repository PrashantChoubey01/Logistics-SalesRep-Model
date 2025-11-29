# SeaRates AI - Logistics Sales Assistant

An intelligent email automation system for logistics CRM that processes customer shipping quote requests, extracts structured data, generates professional responses, and manages multi-turn conversations with cumulative data merging.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- OpenAI API key (set in environment or config)

### Installation
```bash
pip install -r requirements.txt
```

### Run Demo UI
```bash
streamlit run demo_app.py
```

## 🏗️ Architecture

### Core Components
- **LangGraph Workflow Orchestrator**: Manages the entire workflow as a state graph
- **20+ Specialized Agents**: Each handles a specific task (classification, extraction, validation, etc.)
- **Thread Manager**: Maintains conversation threads with cumulative data merging
- **Port Lookup**: Enriches port names with port codes and country information

### Main Workflow
```
Email Input → Classification → Conversation State → Thread Analysis → 
Information Extraction → Data Validation → Port Lookup → Container Standardization → 
Rate Recommendation → Next Action → Response Generation → Thread Update
```

## 📁 Project Structure

```
logistic-ai-response-model/
├── agents/                    # All specialized agents
│   ├── base_agent.py         # Base agent class
│   ├── information_extraction_agent.py
│   ├── clarification_response_agent.py
│   ├── confirmation_response_agent.py
│   ├── sales_notification_agent.py
│   └── ...                   # 15+ other agents
├── langgraph_workflow_orchestrator.py  # Main workflow orchestrator
├── demo_app.py               # Streamlit UI for testing
├── utils/
│   ├── thread_manager.py     # Thread and cumulative extraction management
│   ├── sales_team_manager.py
│   └── forwarder_manager.py
├── models/
│   └── schemas.py           # Pydantic models
├── config/                   # Configuration files
└── data/
    ├── threads/              # Thread JSON files
    └── embeddings/          # Port embeddings
```

## 🔑 Key Features

### 1. Intelligent Email Processing
- Classifies emails (customer quote request, forwarder response, etc.)
- Extracts structured data from unstructured email content
- Handles both FCL and LCL shipments with appropriate validation

### 2. Cumulative Data Merging
- Preserves all information across email threads
- Merges new data with existing data (recency priority)
- Never loses information - empty strings treated as "no update"

### 3. Port & Container Standardization
- Enriches port names with port codes (e.g., "Shanghai" → "Shanghai (CNSHG)")
- Standardizes container types (e.g., "40 footer" → "40DC")
- Detects country names vs port names

### 4. Smart Routing
- Clarification Request: When mandatory fields are missing
- Confirmation Request: When all data is complete
- Confirmation Acknowledgment: When customer confirms
- Forwarder Assignment: After confirmation acknowledgment
- Sales Notification: When forwarder rates are received

### 5. Forwarder Integration
- Detects forwarder emails
- Extracts rate information from forwarder responses
- Generates sales notifications with forwarder details and received emails

## 📋 Data Models

### CumulativeExtraction
The most important data structure - contains merged data from entire thread:
- `shipment_details`: Origin, destination, container type, commodity, etc.
- `contact_information`: Customer name, email, phone, company
- `timeline_information`: Shipment dates, transit time, urgency
- `rate_information`: Forwarder rates and quotes
- `special_requirements`: LCL/FCL mentions, special handling

### Merge Rules
1. **Non-empty overrides old**: New non-empty value replaces old
2. **Missing preserves old**: If field is missing, keep old value
3. **Empty strings = no update**: Empty strings preserve existing values
4. **Shipment type conflicts**: LCL clears FCL fields, FCL clears LCL fields

## 🔄 Workflow States

### Email Types
- `customer_quote_request`: Initial customer inquiry
- `customer_clarification`: Customer providing additional info
- `customer_confirmation`: Customer confirming details
- `forwarder_response`: Forwarder sending rates
- `non_logistics`: Non-shipping related emails

### Next Actions
- `send_clarification_request`: Missing mandatory fields
- `send_confirmation_request`: All data complete, awaiting confirmation
- `booking_details_confirmed_assign_forwarders`: Customer confirmed, assign forwarders
- `collate_rates_and_send_to_sales`: Forwarder rates received, notify sales

## 🎯 Validation Rules

### FCL Shipments (Full Container Load)
**Required:**
- Origin (specific port, not just country)
- Destination (specific port, not just country)
- Container Type (e.g., 40HC, 20GP)
- Container Count
- Shipment Date
- Commodity Name

### LCL Shipments (Less than Container Load)
**Required:**
- Origin (specific port, not just country)
- Destination (specific port, not just country)
- Weight
- Volume
- Shipment Date
- Commodity Name

**Note:** Container count is NOT required for LCL shipments.

### Unknown Shipment Type
If shipment type is not explicitly mentioned:
- Ask for: Shipment Type (FCL/LCL), Container Type, Weight, Volume
- Do NOT assume FCL or LCL

## 📧 Email Response Types

### Clarification Request
- Shows all extracted information with enriched ports
- Lists missing mandatory fields
- Asks for specific information

### Confirmation Request
- Shows all validated shipment details
- Requests customer confirmation
- Includes standardized container types and port codes

### Confirmation Acknowledgment
- Acknowledges customer confirmation
- Indicates forwarder assignment in progress
- Uses enriched port data

### Sales Notification
- Includes customer details
- Includes shipment details (NO country information)
- Includes forwarder information (name, email, company, phone)
- Includes forwarder received email (complete email FROM forwarder)
- Includes forwarder rate quotes if available
- Provides actionable steps for sales team

## 🛠️ Development

### Running Tests
```bash
pytest tests/
```

### Key Files
- `langgraph_workflow_orchestrator.py`: Main workflow logic
- `utils/thread_manager.py`: Thread and merge logic
- `agents/information_extraction_agent.py`: Data extraction
- `agents/sales_notification_agent.py`: Sales team notifications

### Configuration
- `config/config.json`: Main configuration
- `config/sales_team.json`: Sales team assignments
- `config/forwarders.json`: Forwarder database

## 📝 Important Rules

1. **Never assume shipment type**: Ask for FCL/LCL if not explicitly mentioned
2. **Never include country info in sales emails**: Only port/city names
3. **Always include forwarder email**: When forwarder sends email, include it in sales notification
4. **Empty strings = no update**: Never delete existing values with empty strings
5. **Ports required, not countries**: Origin/destination must be specific ports, not just countries

## 🔗 Related Documentation

- `CUSTOMER_EMAIL_INPUT_OUTPUT_SPEC.md`: Detailed email templates and expected outputs
- `cursor_rules.md`: Development rules and guidelines

## 📄 License

Internal use only - SeaRates by DP World

