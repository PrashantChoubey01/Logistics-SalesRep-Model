# Logistics AI Bot - Comprehensive Project Documentation

**Version:** 1.0.0  
**Last Updated:** February 10, 2026  
**Branch:** demo-version (from development)

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Technology Stack](#technology-stack)
4. [System Components](#system-components)
5. [Workflow & State Management](#workflow--state-management)
6. [Agent System](#agent-system)
7. [Data Models & Schemas](#data-models--schemas)
8. [API & Endpoints](#api--endpoints)
9. [Frontend Application](#frontend-application)
10. [Configuration Management](#configuration-management)
11. [Utilities & Helpers](#utilities--helpers)
12. [Testing & Evaluation](#testing--evaluation)
13. [Monitoring & Observability](#monitoring--observability)
14. [Deployment & Operations](#deployment--operations)
15. [Development Workflow](#development-workflow)
16. [Key Features](#key-features)
17. [Business Rules](#business-rules)
18. [File Structure](#file-structure)

---

## 📖 Project Overview

### Purpose
The **Logistics AI Bot** (SeaRates AI) is an intelligent email automation system designed for logistics CRM operations. It processes customer shipping quote requests, extracts structured data, generates professional responses, and manages multi-turn conversations with cumulative data merging.

### Core Capabilities
- **Intelligent Email Classification**: Automatically categorizes emails (customer quotes, forwarder responses, confirmations, complaints)
- **Information Extraction**: Extracts structured shipping data from unstructured email content
- **Multi-Turn Conversations**: Maintains conversation context across email threads with cumulative data merging
- **Smart Response Generation**: Creates appropriate responses (clarification, confirmation, acknowledgment)
- **Forwarder Management**: Detects forwarder emails, extracts rates, and manages forwarder assignments
- **Sales Team Integration**: Routes requests to appropriate sales personnel
- **Port & Container Standardization**: Enriches port names with codes and standardizes container types

### Business Value
- Automates 80%+ of routine customer inquiry responses
- Reduces response time from hours to seconds
- Maintains data consistency across email threads
- Provides structured data for CRM integration
- Ensures professional, brand-consistent communication

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  JavaScript UI (index.html + app.js + styles.css)   │  │
│  │  - Email composition interface                       │  │
│  │  - Template selection                                │  │
│  │  - Response visualization                            │  │
│  │  - Thread history display                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI Server (api_server.py)                      │  │
│  │  - /health, /ready endpoints                         │  │
│  │  - /api/process-email (POST)                         │  │
│  │  - CORS middleware                                   │  │
│  │  - Request/Response validation                       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  Orchestration Layer                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  LangGraph Workflow Orchestrator                     │  │
│  │  - State graph management                            │  │
│  │  - Agent coordination                                │  │
│  │  - Conditional routing                               │  │
│  │  - Checkpoint management                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     Agent Layer (20+ Agents)                │
│  ┌──────────────┬──────────────┬──────────────┬─────────┐  │
│  │ Classification│ Extraction   │ Validation   │ Port    │  │
│  │ Agent         │ Agent        │ Agent        │ Lookup  │  │
│  ├──────────────┼──────────────┼──────────────┼─────────┤  │
│  │ Container    │ Rate         │ Next Action  │ Response│  │
│  │ Standard     │ Recommend    │ Agent        │ Agents  │  │
│  ├──────────────┼──────────────┼──────────────┼─────────┤  │
│  │ Forwarder    │ Sales        │ Escalation   │ Thread  │  │
│  │ Agents       │ Notification │ Agent        │ Context │  │
│  └──────────────┴──────────────┴──────────────┴─────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Data & Utilities Layer                   │
│  ┌──────────────┬──────────────┬──────────────┬─────────┐  │
│  │ Thread       │ Forwarder    │ Sales Team   │ Name    │  │
│  │ Manager      │ Manager      │ Manager      │ Extract │  │
│  ├──────────────┼──────────────┼──────────────┼─────────┤  │
│  │ Logger       │ DateTime     │ Completeness │ Cleanup │  │
│  │              │ Serializer   │ Checker      │ Utils   │  │
│  └──────────────┴──────────────┴──────────────┴─────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Storage & External                       │
│  ┌──────────────┬──────────────┬──────────────┬─────────┐  │
│  │ Thread JSON  │ Port         │ Config       │ LLM     │  │
│  │ Files        │ Embeddings   │ Files        │ APIs    │  │
│  │ (data/)      │ (data/)      │ (config/)    │ (Azure) │  │
│  └──────────────┴──────────────┴──────────────┴─────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Design Principles

1. **LLM-Native Architecture**: Built on LangGraph state machine with deterministic agent functions
2. **Immutable State**: Pydantic models ensure data immutability once created
3. **Append-Only Thread Storage**: Thread JSON files are append-only; no overwrites
4. **Zero Hallucination Tolerance**: Agents return None if confidence < 0.85
5. **Reproducible & Testable**: Every agent has deterministic test cases
6. **Graceful Degradation**: System continues with safe defaults on agent failures

---

## 🛠️ Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Workflow Engine** | LangGraph | ≥0.5.3 | State graph orchestration |
| **LLM Framework** | LangChain | ≥0.3.27 | LLM integration & chains |
| **LLM Providers** | OpenAI, Anthropic | Latest | Claude 3.7 Sonnet (primary) |
| **API Framework** | FastAPI | ≥0.115.0 | REST API server |
| **Web Server** | Uvicorn | ≥0.30.0 | ASGI server |
| **Data Validation** | Pydantic | ≥2.11.9 | Schema validation |
| **Frontend** | Vanilla JS | - | Web interface |
| **Python** | Python | 3.12+ | Runtime environment |

### Supporting Libraries

- **numpy** (≥2.2.6): Data processing
- **country-converter** (≥1.3.1): Country code standardization
- **databricks-sdk** (≥0.58.0): Databricks integration
- **nest-asyncio** (≥1.6.0): Async support
- **pytest** (≥8.0.0): Testing framework

### Infrastructure

- **LLM Endpoint**: Azure Databricks (Claude 3.7 Sonnet)
- **Storage**: Local JSON files (thread data)
- **Monitoring**: Prometheus + Grafana (optional)
- **Deployment**: Docker-ready (docker-compose.monitoring.yml)

---

## 🧩 System Components

### 1. LangGraph Workflow Orchestrator

**File**: `langgraph_workflow_orchestrator.py`

The central orchestrator that manages the entire email processing workflow as a state graph.

**Key Responsibilities**:
- Initialize all 20+ agents
- Build and manage the workflow state graph
- Handle conditional routing between agents
- Manage workflow state and checkpoints
- Coordinate parallel agent execution
- Handle errors and fallbacks

**Main Workflow Path** (Logistics Emails):
```
classify_email 
  → conversation_state 
  → analyze_thread 
  → extract_information
  → update_cumulative_extraction 
  → validate_data 
  → lookup_ports
  → standardize_container 
  → recommend_rates 
  → next_action
  → assign_sales_person 
  → [response_agent] 
  → update_thread
```

**Conditional Branches**:
- **Forwarder Detection**: Separate path for forwarder responses
- **Escalation**: Automatic escalation for complex cases
- **Next Action Routing**: 
  - `send_clarification_request` → ClarificationResponseAgent
  - `send_confirmation_request` → ConfirmationResponseAgent
  - `booking_details_confirmed_assign_forwarders` → ForwarderAssignmentAgent
  - `collate_rates_and_send_to_sales` → SalesNotificationAgent

**State Management**:
- Uses `WorkflowState` TypedDict with 30+ fields
- Implements reducers for concurrent updates
- Maintains immutable email_data
- Tracks workflow history and metadata

---

### 2. Agent System (20+ Specialized Agents)

All agents inherit from `BaseAgent` class and implement the `process()` method.

#### Core Processing Agents

| Agent | File | Purpose |
|-------|------|---------|
| **UnifiedEmailClassifierAgent** | `unified_email_classifier_agent.py` | Classifies email type and sender type |
| **ConversationStateAgent** | `conversation_state_agent.py` | Determines conversation state |
| **ThreadContextAnalyzerAgent** | `thread_context_analyzer_agent.py` | Analyzes thread history |
| **InformationExtractionAgent** | `information_extraction_agent.py` | Extracts structured data from email |
| **DataValidationAgent** | `data_validation_agent.py` | Validates extracted data completeness |
| **PortLookupAgent** | `port_lookup_agent.py` | Enriches ports with codes & countries |
| **ContainerStandardizationAgent** | `container_standardization_agent.py` | Standardizes container types |
| **RateRecommendationAgent** | `rate_recommendation_agent.py` | Recommends rates from database |
| **NextActionAgent** | `next_action_agent.py` | Decides next workflow action |

#### Response Generation Agents

| Agent | File | Purpose |
|-------|------|---------|
| **ClarificationResponseAgent** | `clarification_response_agent.py` | Generates clarification requests |
| **ConfirmationResponseAgent** | `confirmation_response_agent.py` | Generates confirmation requests |
| **ConfirmationAcknowledgmentAgent** | `confirmation_acknowledgment_agent.py` | Acknowledges customer confirmation |
| **AcknowledgmentResponseAgent** | `acknowledgment_response_agent.py` | Generic acknowledgment responses |

#### Forwarder & Sales Agents

| Agent | File | Purpose |
|-------|------|---------|
| **ForwarderDetectionAgent** | `forwarder_detection_agent.py` | Detects forwarder emails |
| **ForwarderResponseAgent** | `forwarder_response_agent.py` | Processes forwarder rate responses |
| **ForwarderEmailDraftAgent** | `forwarder_email_draft_agent.py` | Drafts emails to forwarders |
| **ForwarderAssignmentAgent** | `forwarder_assignment_agent.py` | Assigns forwarders to shipments |
| **SalesNotificationAgent** | `sales_notification_agent.py` | Notifies sales team |

#### Support Agents

| Agent | File | Purpose |
|-------|------|---------|
| **EscalationDecisionAgent** | `escalation_decision_agent.py` | Decides if escalation needed |
| **ResponseValidatorAgent** | `response_validator_agent.py` | Validates response quality |
| **EmailSenderAgent** | `email_sender_agent.py` | Sends emails (future integration) |

---

### 3. BaseAgent Architecture

**File**: `agents/base_agent.py`

All agents inherit from this base class, which provides:

**Core Features**:
- LLM client initialization (ChatOpenAI + OpenAI)
- Configuration management
- Logging setup
- Function calling support
- Error handling
- Status reporting

**Key Methods**:
```python
class BaseAgent(ABC):
    def __init__(self, agent_name: str)
    def load_context(self) -> bool
    def _make_llm_call(self, prompt, function_schema) -> Dict
    @abstractmethod
    def process(self, input_data: Dict) -> Dict
    def run(self, input_data: Dict) -> Dict
    def get_status(self) -> Dict
```

**LLM Configuration**:
- Loads from `config/config.json`
- Supports Databricks endpoints
- Uses Claude 3.7 Sonnet by default
- Temperature: 0.1 (deterministic)
- Max tokens: 800 (configurable)

---

## 🔄 Workflow & State Management

### WorkflowState Schema

The `WorkflowState` TypedDict contains all data flowing through the workflow:

```python
class WorkflowState(TypedDict):
    # Email data (immutable)
    email_data: Dict[str, Any]
    thread_history: List[Dict[str, Any]]
    
    # Agent results (30+ fields)
    classification_result: Optional[Dict]
    extraction_result: Optional[Dict]
    validation_result: Optional[Dict]
    port_lookup_result: Optional[Dict]
    # ... (20+ more result fields)
    
    # Context
    customer_context: Dict[str, Any]
    forwarder_context: Dict[str, Any]
    market_data: Dict[str, Any]
    
    # Decision flags
    should_escalate: bool
    is_forwarder_email: bool
    workflow_completed: bool
    
    # Thread management
    thread_id: str
    cumulative_extraction: Dict[str, Any]
    
    # Metadata
    workflow_id: str
    timestamp: str
    assigned_sales_person: Optional[Dict]
    workflow_history: List[str]
```

### State Reducers

LangGraph uses reducers to handle concurrent state updates:

```python
# Escalation reducer - takes first non-None value
def _escalation_reducer(x, y) -> Optional[Dict]:
    return x if x is not None else y

# Boolean OR reducer - True if either is True
def _should_escalate_reducer(x: bool, y: bool) -> bool:
    return x or y
```

### Conditional Routing Logic

**After Classification**:
```python
def route_after_classification(state):
    email_type = state["classification_result"]["email_type"]
    
    if email_type == "forwarder_response":
        return "forwarder_response_agent"
    elif email_type == "non_logistics":
        return "acknowledgment_response_agent"
    else:
        return "conversation_state_agent"
```

**After Next Action**:
```python
def route_after_next_action(state):
    next_action = state["next_action_result"]["next_action"]
    
    if next_action == "send_clarification_request":
        return "clarification_response_agent"
    elif next_action == "send_confirmation_request":
        return "confirmation_response_agent"
    elif next_action == "booking_details_confirmed_assign_forwarders":
        return "confirmation_acknowledgment_agent"
    # ... more routing logic
```

---

## 📊 Data Models & Schemas

**File**: `models/schemas.py`

All data models use Pydantic for validation and type safety.

### Core Models

#### 1. ShipmentDetails
```python
class ShipmentDetails(BaseModel):
    origin_port: str
    destination_port: str
    origin_country: Optional[str]
    destination_country: Optional[str]
    inco_terms: Optional[str]
    cargo_description: Optional[str]
    weight_kg: Optional[float]
    volume_cbm: Optional[float]
    last_updated: datetime
    source: Optional[str]
```

#### 2. ContainerDetails
```python
class ContainerDetails(BaseModel):
    container_type: str  # 20GP, 40HC, etc.
    container_count: Optional[int] = 1
    temperature_controlled: Optional[bool] = False
    hazardous: Optional[bool] = False
```

#### 3. TimelineInformation
```python
class TimelineInformation(BaseModel):
    ready_date: Optional[datetime]
    etd: Optional[datetime]
    eta: Optional[datetime]
    transit_time_days: Optional[int]
```

#### 4. RateInformation
```python
class RateInformation(BaseModel):
    base_freight_usd: Optional[float]
    surcharge_usd: Optional[float]
    validity_end: Optional[datetime]
    currency: str = "USD"
    reasoning: Optional[str]
```

#### 5. CumulativeExtraction
```python
class CumulativeExtraction(BaseModel):
    shipment_details: Optional[ShipmentDetails]
    container_details: Optional[ContainerDetails]
    timeline_information: Optional[TimelineInformation]
    rate_information: Optional[RateInformation]
    special_requirements: Optional[SpecialRequirements]
    additional_notes: Optional[str]
    last_updated: datetime
    extraction_version: int = 1
```

#### 6. InboundEmail
```python
class InboundEmail(BaseModel):
    message_id: str
    thread_id: str
    from_email: EmailStr
    to_email: EmailStr
    subject: str
    body_text: str
    body_html: Optional[str]
    received_at: datetime
    raw_metadata: Dict[str, Any]
```

#### 7. EmailEntry & ThreadData
```python
@dataclass
class EmailEntry:
    timestamp: str
    email_id: str
    sender: str
    direction: str  # "inbound" or "outbound"
    subject: str
    content: str
    extracted_data: Optional[Dict]
    response_type: Optional[str]
    bot_response: Optional[Dict]
    workflow_id: Optional[str]
    confidence_score: Optional[float]

@dataclass
class ThreadData:
    thread_id: str
    email_chain: List[EmailEntry]
    cumulative_extraction: Dict[str, Any]
    last_updated: str
    customer_context: Dict[str, Any]
    forwarder_context: Dict[str, Any]
    conversation_state: str = "new_thread"
    total_emails: int = 0
```

---

## 🌐 API & Endpoints

**File**: `api_server.py`

FastAPI server providing REST endpoints for email processing.

### Endpoints

#### 1. Root Endpoint
```
GET /
```
Returns API information and available endpoints.

**Response**:
```json
{
  "service": "SeaRates Logistics AI API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "ready": "/ready",
    "process_email": "/api/process-email",
    "docs": "/docs"
  },
  "timestamp": "2026-02-10T12:00:00"
}
```

#### 2. Health Check
```
GET /health
```
Returns server health status.

**Response**:
```json
{
  "status": "healthy",
  "orchestrator_initialized": true,
  "timestamp": "2026-02-10T12:00:00"
}
```

#### 3. Readiness Check
```
GET /ready
```
Returns readiness status (checks if orchestrator is initialized).

**Response**:
```json
{
  "status": "ready",
  "timestamp": "2026-02-10T12:00:00"
}
```

#### 4. Process Email (Main Endpoint)
```
POST /api/process-email
```

**Request Body**:
```json
{
  "sender": "customer@example.com",
  "subject": "Shipping Quote Request",
  "content": "I need a quote for shipping 2x40HC from Shanghai to Los Angeles...",
  "thread_id": "demo_thread_20260210_120000"
}
```

**Success Response**:
```json
{
  "success": true,
  "thread_id": "demo_thread_20260210_120000",
  "workflow_id": "workflow_20260210_120000_abc123",
  "result": {
    "workflow_state": {
      "classification_result": {...},
      "extraction_result": {...},
      "confirmation_response_result": {...},
      "forwarder_assignment_result": {...}
    }
  },
  "error": null
}
```

**Error Response**:
```json
{
  "success": false,
  "thread_id": "demo_thread_20260210_120000",
  "workflow_id": "unknown",
  "result": {},
  "error": "Error message here"
}
```

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Server Configuration

- **Host**: 0.0.0.0 (all interfaces)
- **Port**: 5001 (configurable)
- **Reload**: Enabled in development
- **Log Level**: INFO

---

## 💻 Frontend Application

**Location**: `frontend/`

### Files

1. **index.html**: Main HTML structure
2. **app.js**: JavaScript application logic
3. **styles.css**: Styling and responsive design
4. **test-api.html**: API testing interface

### Features

#### 1. Email Composition Interface
- Sender type selection (Customer/Forwarder)
- Email address input
- Subject line input
- Rich text content area
- Template selector with pre-filled examples

#### 2. Email Templates
Pre-configured templates for testing:
- Complete FCL Quote Request
- Minimal Information Request
- Customer Confirmation
- Forwarder Rate Quote
- LCL Shipment Request
- Urgent Shipment Request
- Complaint Email

#### 3. Response Visualization
Displays workflow results in organized sections:
- **Response Generated**: Bot's email response
- **Forwarder Assignment**: Assigned forwarders (if applicable)
- **Forwarder Response**: Rate information from forwarders
- **Sales Notification**: Internal sales team notification

#### 4. Thread History
- Chronological display of all emails in thread
- Expandable email entries
- Shows sender, timestamp, subject
- Displays full email content and bot responses

#### 5. Real-Time Processing
- Loading indicators during processing
- Error handling with user-friendly messages
- Automatic thread ID generation
- Thread reset functionality

### API Integration

```javascript
const apiBaseUrl = 'http://localhost:5001';

async function processEmail(emailData) {
  const response = await fetch(`${apiBaseUrl}/api/process-email`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(emailData)
  });
  return await response.json();
}
```

### Responsive Design
- Mobile-friendly layout
- Gradient header design
- Card-based UI components
- Smooth animations and transitions

---

## ⚙️ Configuration Management

**Location**: `config/`

### Configuration Files

#### 1. config.json (Main Configuration)
```json
{
  "api_key": "dapibc1b1ba3a4f522480e6d9307d351c252-3",
  "base_url": "https://adb-2252852771922438.18.azuredatabricks.net/serving-endpoints/",
  "model_name": "databricks-claude-3-7-sonnet"
}
```

**Purpose**: LLM endpoint configuration

#### 2. sales_team.json (Sales Team Database)
```json
{
  "sales_team": [
    {
      "id": "sales_001",
      "name": "John Smith",
      "email": "john.smith@searates.com",
      "phone": "+1-555-0101",
      "specialization": ["FCL", "Asia-Pacific"],
      "languages": ["English", "Mandarin"]
    }
  ]
}
```

**Purpose**: Sales team member information and assignment rules

#### 3. forwarders.json (Forwarder Database)
```json
{
  "forwarders": [
    {
      "id": "fwd_001",
      "name": "Global Freight Solutions",
      "email": "quotes@globalfreight.com",
      "country": "China",
      "operator": "Ocean Freight",
      "routes": ["CNSHG-USLAX", "CNSHG-USNYC"]
    }
  ]
}
```

**Purpose**: Forwarder contact information and capabilities

#### 4. email_config.json (Email Server Config)
```json
{
  "smtp_server": "smtp.example.com",
  "smtp_port": 587,
  "use_tls": true,
  "sender_email": "noreply@searates.com",
  "sender_name": "SeaRates AI Assistant"
}
```

**Purpose**: Email sending configuration (future use)

### Template Files

For security, sensitive configuration files are not tracked in Git:
- `sales_team.template.json`
- `forwarders.template.json`
- `email_config.template.json`

**Setup Process**:
```bash
cp config/sales_team.template.json config/sales_team.json
cp config/forwarders.template.json config/forwarders.json
cp config/email_config.template.json config/email_config.json
```

---

## 🛠️ Utilities & Helpers

**Location**: `utils/`

### 1. ThreadManager

**File**: `utils/thread_manager.py`

**Purpose**: Manages email threads with cumulative data merging

**Key Features**:
- Load/save thread data to JSON files
- Merge new extractions with cumulative data
- Recency-based priority merging
- Shipment type conflict resolution
- Empty string handling (no-update semantics)

**Merge Strategies**:
```python
merge_strategies = {
    "shipment_details": _merge_shipment_details,
    "contact_information": _merge_contact_info,
    "timeline_information": _merge_timeline_info,
    "special_requirements": _merge_special_requirements,
    "rate_information": _merge_rate_info,
    "additional_notes": _merge_additional_notes
}
```

**Merge Rules**:
1. **Non-empty overrides old**: New non-empty value replaces old
2. **Missing preserves old**: If field is missing, keep old value
3. **Empty strings = no update**: Empty strings preserve existing values
4. **Shipment type conflicts**: LCL clears FCL fields, FCL clears LCL fields

### 2. ForwarderManager

**File**: `utils/forwarder_manager.py`

**Purpose**: Manages forwarder database and assignments

**Key Methods**:
```python
def load_forwarders(self) -> List[Dict]
def find_forwarders_by_route(self, origin, destination) -> List[Dict]
def find_forwarders_by_country(self, country) -> List[Dict]
def get_forwarder_by_id(self, forwarder_id) -> Optional[Dict]
```

### 3. SalesTeamManager

**File**: `utils/sales_team_manager.py`

**Purpose**: Manages sales team assignments

**Key Methods**:
```python
def assign_sales_person(self, shipment_details) -> Dict
def get_sales_person_by_id(self, sales_id) -> Optional[Dict]
def get_available_sales_team(self) -> List[Dict]
```

### 4. NameExtractor

**File**: `utils/name_extractor.py`

**Purpose**: Extracts customer names from email data

**Key Functions**:
```python
def extract_first_name(email: str, full_name: Optional[str]) -> str
def extract_name_from_email_data(email_data: dict) -> str
```

**Logic**:
- Extracts from full name if available
- Falls back to email address parsing
- Handles various email formats
- Returns "Valued Customer" as fallback

### 5. Logger

**File**: `utils/logger.py`

**Purpose**: Centralized logging configuration

**Key Functions**:
```python
def setup_logging(level=logging.INFO, log_file=None)
def get_logger(name: str, level=None) -> logging.Logger
```

**Features**:
- Structured logging format
- Configurable log levels
- File and console output
- Agent-specific loggers

### 6. DateTimeSerializer

**File**: `utils/datetime_serializer.py`

**Purpose**: Handles datetime serialization for JSON

**Key Functions**:
```python
def serialize_for_json(obj: Any) -> Any
def safe_json_dumps(obj: Any, **kwargs) -> str
def find_datetime_objects(obj: Any, path: str) -> List[str]
```

### 7. CompletenessChecker

**File**: `utils/completeness_checker.py`

**Purpose**: Checks if shipment information is complete

**Key Function**:
```python
def is_information_complete(state: Dict[str, Any]) -> bool
```

**Validation Logic**:
- FCL: Requires origin, destination, container_type, shipment_date
- LCL: Requires origin, destination, weight, volume, shipment_date
- Unknown: Requires shipment_type determination

### 8. ThreadCleanup

**File**: `utils/cleanup_threads.py`

**Purpose**: Utilities for managing thread files

**Key Functions**:
```python
def list_threads(threads_dir: Path) -> List[Path]
def delete_all_threads(threads_dir: Path, confirm: bool) -> int
def delete_old_threads(threads_dir: Path, days_old: int) -> int
def delete_test_threads(threads_dir: Path, confirm: bool) -> int
```

---

## 🧪 Testing & Evaluation

### Test Structure

**Location**: `tests/`, `agent_tests/`

### Agent Testing

**File**: `agent_tests/agent_test_runner.py`

**Purpose**: Automated testing framework for individual agents

**Test Cases**: `test_cases/classification_test_cases.json`

### Evaluation Framework

**Location**: `eval/`

#### 1. BenchmarkRunner

**File**: `eval/benchmark_runner.py`

**Purpose**: Runs benchmark tests on complete workflows

#### 2. Descriptors

**File**: `eval/descriptors.py`

**Purpose**: Defines evaluation metrics and descriptors

### Test Scenarios

1. **Complete FCL Quote Request**: All fields present, should generate confirmation
2. **Minimal Information**: Missing fields, should generate clarification
3. **Customer Confirmation**: Confirmed details, should assign forwarders
4. **Forwarder Rate Response**: Rate extraction and sales notification
5. **Complaint Email**: Non-logistics handling
6. **Urgent Request**: Priority handling

---

## 📈 Monitoring & Observability

**Location**: `monitoring/`

### Components

#### 1. Prometheus Configuration

**File**: `monitoring/prometheus.yml`

**Metrics Collected**:
- `email_processed_total{result=success|clarify|escalate|error}`
- `agent_hallucination_total{agent=<name>}`
- `agent_confidence{agent=<name>}`
- `workflow_duration_seconds`

#### 2. Alert Rules

**File**: `monitoring/alerts.yaml`

**Critical Alerts**:
- Error rate > 1% (5-minute window)
- Average agent confidence < 0.85
- Grammar score < 95%

#### 3. Grafana Dashboard

**File**: `monitoring/dashboards/langgraph_email.json`

**Visualizations**:
- Email processing throughput
- Agent performance metrics
- Error rate trends
- Confidence score distribution

#### 4. Metrics Module

**File**: `monitoring/metrics.py`

**Purpose**: Prometheus metrics instrumentation

### Docker Compose

**File**: `docker-compose.monitoring.yml`

**Services**:
- Prometheus
- Grafana
- Alertmanager

**Usage**:
```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

---

## 🚀 Deployment & Operations

### Local Development

#### 1. Environment Setup

```bash
# Activate virtual environment
source venv_ai_model/bin/activate

# Or use helper script
source activate_venv.sh
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Start Services

**Option A: Individual Terminals**
```bash
# Terminal 1: API Server
python api_server.py

# Terminal 2: Frontend Server
cd frontend
python -m http.server 8080
```

**Option B: Helper Scripts**
```bash
# Start both servers
./start_servers.sh

# Or individually
./run_api.sh
./run_frontend.sh
```

### Production Deployment

#### Health Checks

- **Health Probe**: `GET /health` (returns 200 if orchestrator initialized)
- **Readiness Probe**: `GET /ready` (checks DB, Redis, model endpoint)

#### Graceful Shutdown

- Wait for running graph to finish (max 30s)
- Then SIGKILL

#### Request Timeouts

- NGINX: 25s
- FastAPI: 20s
- Agent HTTP calls: 15s

### Environment Variables

```bash
# LLM Configuration
DATABRICKS_TOKEN=your_token_here
DATABRICKS_BASE_URL=https://your-databricks-url
MODEL_ENDPOINT_ID=databricks-claude-3-7-sonnet

# API Configuration
API_HOST=0.0.0.0
API_PORT=5001

# Frontend Configuration
FRONTEND_PORT=8080
```

---

## 💼 Development Workflow

### Git Workflow

**Current Branch**: `demo-version` (from `development`)

**Branch Strategy**:
- `main`: Production-ready code
- `development`: Integration branch
- `demo-version`: Demo/presentation branch
- Feature branches: `feature/feature-name`

### Code Quality Standards

#### 1. Typing
- Every public method has type hints
- Private methods start with `_`

#### 2. Testing
- Every agent gets `test_<agent>.py`
- Minimum 3 deterministic test cases
- Use `mock_openai_response` for testing

#### 3. Logging
- Use `structlog` (or standard logging)
- Never use `print()` statements
- Format: `<agent>:<action>:<confidence>`

#### 4. Secrets Management
- Load via `pydantic-settings SecretStr`
- Never use `os.getenv` directly
- Keep sensitive files out of Git

### Development Rules

#### Strict Iterative Workflow

1. **PLAN**: List files touched, agents impacted, test strategy
2. **CONFIRM**: Wait for "go", "implement", or "confirm"
3. **IMPLEMENT**: Make changes
4. **TEST**: Run tests and verify
5. **COMMIT**: Create commit with descriptive message

#### Read Before Write

- Summarize target in ≤5 bullets
- List impacted symbols
- Understand context before editing

#### Minimal Diff

- Unified patch or changed function only
- ≤50 lines per PR
- Focus on single responsibility

---

## 🎯 Key Features

### 1. Intelligent Email Processing

**Classification**:
- Customer quote requests
- Customer clarifications
- Customer confirmations
- Forwarder responses
- Non-logistics emails
- Complaints

**Extraction**:
- Origin/destination ports
- Container types and counts
- Shipment dates
- Cargo description
- Weight and volume
- Special requirements
- Contact information

### 2. Cumulative Data Merging

**Merge Logic**:
- Preserves all information across threads
- Recency priority for conflicts
- Empty strings treated as "no update"
- Shipment type conflict resolution

**Example**:
```
Email 1: Origin=Shanghai, Destination=Los Angeles
Email 2: Container=40HC, Date=2026-03-01
Email 3: Commodity=Electronics

Cumulative: All three pieces of information preserved
```

### 3. Port & Container Standardization

**Port Enrichment**:
- Input: "Shanghai"
- Output: "Shanghai (CNSHG)"
- Includes country: "Shanghai, China"

**Container Standardization**:
- Input: "40 footer high cube"
- Output: "40HC"
- Supported: 20GP, 40GP, 40HC, 45HC, 20RF, 40RF

### 4. Smart Routing

**Decision Tree**:
```
Classification
  ├─ Logistics Request
  │   ├─ Incomplete Data → Clarification Request
  │   ├─ Complete Data → Confirmation Request
  │   └─ Confirmed → Forwarder Assignment
  ├─ Forwarder Response → Rate Extraction → Sales Notification
  └─ Non-Logistics → Acknowledgment
```

### 5. Forwarder Integration

**Capabilities**:
- Detect forwarder emails by domain/signature
- Extract rate information (price, currency, transit time)
- Assign forwarders based on route
- Draft rate request emails
- Notify sales team with forwarder details

### 6. Multi-Turn Conversations

**Thread Management**:
- Maintains conversation context
- Tracks email history
- Preserves cumulative extraction
- Handles clarification loops
- Supports confirmation workflows

---

## 📜 Business Rules

### FCL (Full Container Load) Rules

**Required Fields**:
- Origin port (specific port, not just country)
- Destination port (specific port, not just country)
- Container type (e.g., 40HC, 20GP)
- Container count
- Shipment date
- Commodity name

**Optional Fields**:
- Weight (not required for FCL)
- Volume (not required for FCL)

### LCL (Less than Container Load) Rules

**Required Fields**:
- Origin port
- Destination port
- Weight
- Volume
- Shipment date
- Commodity name

**Not Required**:
- Container type (LCL doesn't use full containers)
- Container count

### Validation Rules

1. **Ports Required, Not Countries**: Must specify specific ports (e.g., "Shanghai"), not just countries (e.g., "China")

2. **Never Assume Shipment Type**: If not explicitly mentioned, ask for FCL/LCL

3. **Empty Strings = No Update**: Never delete existing values with empty strings

4. **Shipment Type Conflicts**: 
   - If LCL is set, clear container_type and container_count
   - If FCL is set, weight and volume become optional

5. **Customer Confirmation Overrides**: Customer confirmation overrides validation issues except clearly invalid data

### Email Response Rules

1. **Clarification Requests**:
   - Show all extracted information with enriched ports
   - List missing mandatory fields
   - Ask specific questions in priority order

2. **Confirmation Requests**:
   - Show all validated shipment details
   - Include standardized container types and port codes
   - Request explicit confirmation

3. **Confirmation Acknowledgment**:
   - Acknowledge customer confirmation
   - Indicate forwarder assignment in progress
   - Use enriched port data

4. **Sales Notifications**:
   - Include customer details
   - Include shipment details (NO country information)
   - Include forwarder information (name, email, company, phone)
   - Include forwarder received email (complete email FROM forwarder)
   - Include forwarder rate quotes if available

### Escalation Rules

**Automatic Escalation Triggers**:
- Agent confidence < 0.85
- Multiple clarification loops (>3)
- Complaint emails
- Urgent requests with missing critical data
- Invalid or conflicting data

---

## 📁 File Structure

```
logistics-ai-bot/
├── .cursor/                          # Cursor IDE rules
│   └── rules/
│       ├── logistics-ai-bot-rules.mdc
│       └── priority-rules.mdc
│
├── agents/                           # 20+ specialized agents
│   ├── base_agent.py                # Base agent class
│   ├── unified_email_classifier_agent.py
│   ├── information_extraction_agent.py
│   ├── data_validation_agent.py
│   ├── port_lookup_agent.py
│   ├── container_standardization_agent.py
│   ├── rate_recommendation_agent.py
│   ├── next_action_agent.py
│   ├── clarification_response_agent.py
│   ├── confirmation_response_agent.py
│   ├── confirmation_acknowledgment_agent.py
│   ├── acknowledgment_response_agent.py
│   ├── forwarder_detection_agent.py
│   ├── forwarder_response_agent.py
│   ├── forwarder_email_draft_agent.py
│   ├── forwarder_assignment_agent.py
│   ├── sales_notification_agent.py
│   ├── escalation_decision_agent.py
│   ├── response_validator_agent.py
│   ├── email_sender_agent.py
│   ├── conversation_state_agent.py
│   └── thread_context_analyzer_agent.py
│
├── config/                          # Configuration files
│   ├── config.json                  # Main LLM configuration
│   ├── sales_team.json              # Sales team database
│   ├── forwarders.json              # Forwarder database
│   ├── email_config.json            # Email server config
│   ├── sales_team.template.json    # Template
│   ├── forwarders.template.json    # Template
│   └── README.md                    # Config documentation
│
├── data/                            # Data storage
│   ├── threads/                     # Thread JSON files
│   ├── embeddings/                  # Port embeddings
│   │   └── port_data.json
│   └── offline_eval/                # Evaluation data
│
├── eval/                            # Evaluation framework
│   ├── benchmark_runner.py
│   └── descriptors.py
│
├── frontend/                        # Web UI
│   ├── index.html                   # Main HTML
│   ├── app.js                       # JavaScript logic
│   ├── styles.css                   # Styling
│   ├── test-api.html                # API testing page
│   ├── README.md                    # Frontend docs
│   └── DEBUG.md                     # Debug guide
│
├── models/                          # Data models
│   ├── __init__.py
│   └── schemas.py                   # Pydantic models
│
├── monitoring/                      # Monitoring setup
│   ├── prometheus.yml               # Prometheus config
│   ├── alertmanager.yml             # Alert config
│   ├── alerts.yaml                  # Alert rules
│   ├── metrics.py                   # Metrics module
│   ├── dashboards/
│   │   └── langgraph_email.json    # Grafana dashboard
│   └── README.md
│
├── scripts/                         # Utility scripts
│   ├── cost_estimate.py             # Cost estimation
│   ├── create_port_embeddings.py   # Port embedding generation
│   ├── diff_state.py                # State diff tool
│   ├── draw_graph.py                # Graph visualization
│   ├── inspect_state.py             # State inspector
│   ├── nightly_replay.py            # Nightly replay tests
│   ├── repo_map.py                  # Repository mapper
│   ├── trace_data_flow.py           # Data flow tracer
│   └── visualize_execution.py       # Execution visualizer
│
├── tests/                           # Test suite
│   ├── test_outputs/                # Test output files
│   └── .gitkeep
│
├── agent_tests/                     # Agent-specific tests
│   ├── agent_test_runner.py
│   └── README.md
│
├── test_cases/                      # Test case definitions
│   └── classification_test_cases.json
│
├── utils/                           # Utility modules
│   ├── __init__.py
│   ├── thread_manager.py            # Thread management
│   ├── forwarder_manager.py         # Forwarder management
│   ├── sales_team_manager.py        # Sales team management
│   ├── name_extractor.py            # Name extraction
│   ├── logger.py                    # Logging setup
│   ├── datetime_serializer.py       # DateTime handling
│   ├── completeness_checker.py      # Completeness validation
│   ├── thread_cleanup.py            # Thread cleanup
│   └── cleanup_threads.py           # Cleanup utilities
│
├── cli/                             # CLI tools
│   └── replay_thread.py             # Thread replay tool
│
├── venv_ai_model/                   # Virtual environment
│
├── langgraph_workflow_orchestrator.py  # Main orchestrator
├── api_server.py                    # FastAPI server
├── demo_app.py                      # Streamlit demo (legacy)
│
├── requirements.txt                 # Python dependencies
├── requirements-monitoring.txt      # Monitoring dependencies
│
├── start_servers.sh                 # Start all servers
├── run_api.sh                       # Start API server
├── run_frontend.sh                  # Start frontend server
├── activate_venv.sh                 # Activate virtual env
├── activate_dpw.sh                  # Activate DPW env
│
├── docker-compose.monitoring.yml    # Docker compose for monitoring
│
├── port_names.json                  # Port database
├── workflow_graph.png               # Workflow visualization
│
├── README.md                        # Main documentation
├── API_README.md                    # API documentation
├── HOW_TO_USE_UI.md                # UI usage guide
├── QUICK_START.md                   # Quick start guide
├── TROUBLESHOOTING.md               # Troubleshooting guide
├── VERIFICATION_STEPS.md            # Verification steps
├── TEST_RESULTS.md                  # Test results
│
├── .env                             # Environment variables
├── .gitignore                       # Git ignore rules
│
└── PROJECT_DOCUMENTATION.md         # This file
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. API Server Not Starting

**Symptoms**: Error on `python api_server.py`

**Solutions**:
- Check if port 5001 is already in use: `lsof -i :5001`
- Verify virtual environment is activated
- Check if all dependencies are installed: `pip list`
- Verify LLM credentials in `config/config.json`

#### 2. Frontend Not Loading

**Symptoms**: Blank page or connection errors

**Solutions**:
- Ensure web server is running: `python -m http.server 8080`
- Check browser console for errors (F12)
- Verify API server is running: `curl http://localhost:5001/health`
- Check CORS configuration in `api_server.py`

#### 3. Process Button Not Working

**Symptoms**: No response when clicking "Process Email"

**Solutions**:
- Check browser console for JavaScript errors
- Verify API endpoint is accessible: `curl http://localhost:5001/health`
- Check network tab in browser dev tools
- Ensure all form fields are filled

#### 4. LLM Connection Errors

**Symptoms**: "LLM client not available" errors

**Solutions**:
- Verify API key in `config/config.json`
- Check Databricks endpoint URL
- Test connection: `python agents/base_agent.py`
- Check network connectivity to Databricks

#### 5. Thread Data Not Persisting

**Symptoms**: Thread history lost between requests

**Solutions**:
- Check `data/threads/` directory exists
- Verify write permissions
- Check for JSON serialization errors in logs
- Ensure thread_id is consistent across requests

---

## 📚 Additional Resources

### Documentation Files

- **README.md**: Main project overview
- **API_README.md**: API endpoint documentation
- **HOW_TO_USE_UI.md**: Step-by-step UI guide
- **QUICK_START.md**: Quick start instructions
- **TROUBLESHOOTING.md**: Detailed troubleshooting
- **VERIFICATION_STEPS.md**: Verification procedures
- **TEST_RESULTS.md**: Test result summaries

### Configuration Documentation

- **config/README.md**: Configuration setup guide
- **frontend/README.md**: Frontend documentation
- **frontend/DEBUG.md**: Frontend debugging guide
- **monitoring/README.md**: Monitoring setup guide

### Scripts & Tools

- **scripts/draw_graph.py**: Visualize workflow graph
- **scripts/inspect_state.py**: Inspect workflow state
- **scripts/trace_data_flow.py**: Trace data flow through workflow
- **scripts/cost_estimate.py**: Estimate LLM costs
- **cli/replay_thread.py**: Replay thread for debugging

---

## 🎓 Learning Path

### For New Developers

1. **Start Here**:
   - Read this documentation
   - Review `README.md`
   - Follow `QUICK_START.md`

2. **Understand Architecture**:
   - Study `langgraph_workflow_orchestrator.py`
   - Review `agents/base_agent.py`
   - Examine `models/schemas.py`

3. **Run Examples**:
   - Start servers with `./start_servers.sh`
   - Use frontend to process sample emails
   - Review thread JSON files in `data/threads/`

4. **Explore Agents**:
   - Read agent implementations in `agents/`
   - Run agent tests in `agent_tests/`
   - Modify and test a simple agent

5. **Deep Dive**:
   - Study thread merging logic in `utils/thread_manager.py`
   - Understand conditional routing in orchestrator
   - Review state management and reducers

### For Integration

1. **API Integration**:
   - Review `api_server.py`
   - Test endpoints with `frontend/test-api.html`
   - Implement client in your application

2. **Email Integration**:
   - Configure `config/email_config.json`
   - Implement email sending in `agents/email_sender_agent.py`
   - Test with real email server

3. **Database Integration**:
   - Replace JSON storage with database
   - Implement ThreadManager database backend
   - Add connection pooling

---

## 📞 Support & Contact

### Internal Resources

- **Project Repository**: [Internal Git Repository]
- **Documentation**: This file and related docs
- **Issue Tracker**: [Internal Issue Tracker]

### Key Contacts

- **Project Owner**: Staff Engineer (Logistics AI)
- **Technical Lead**: [Name]
- **Product Manager**: [Name]

---

## 📝 Version History

### Version 1.0.0 (Current - demo-version branch)
- Complete 20-agent LangGraph workflow
- FastAPI REST API server
- JavaScript frontend UI
- Cumulative data merging
- Forwarder integration
- Sales team notifications
- Port and container standardization
- Multi-turn conversation support
- Comprehensive documentation

### Previous Versions
- 0.9.x: Beta testing phase
- 0.8.x: Initial agent implementation
- 0.7.x: Proof of concept

---

## 🔮 Future Roadmap

### Planned Features

1. **Email Server Integration**
   - Real-time email monitoring
   - Automatic email sending
   - Email threading detection

2. **Database Backend**
   - Replace JSON storage with PostgreSQL
   - Add caching layer (Redis)
   - Implement connection pooling

3. **Advanced Analytics**
   - Customer sentiment analysis
   - Rate trend prediction
   - Demand forecasting

4. **Multi-Language Support**
   - Detect email language
   - Respond in customer's language
   - Translation integration

5. **Enhanced Monitoring**
   - Real-time dashboards
   - Anomaly detection
   - Performance optimization

6. **Mobile Application**
   - Native mobile apps
   - Push notifications
   - Offline support

---

## 📄 License

**Internal Use Only - SeaRates by DP World**

This software is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited.

---

## 🙏 Acknowledgments

- **LangGraph Team**: For the excellent workflow framework
- **Anthropic**: For Claude 3.7 Sonnet LLM
- **FastAPI Team**: For the high-performance API framework
- **SeaRates Team**: For domain expertise and requirements

---

**End of Documentation**

*For questions or clarifications, please contact the project team.*

---

**Document Metadata**:
- **Created**: February 10, 2026
- **Last Updated**: February 10, 2026
- **Version**: 1.0.0
- **Branch**: demo-version
- **Total Pages**: Comprehensive (40+ sections)
- **Word Count**: ~8,000+ words
