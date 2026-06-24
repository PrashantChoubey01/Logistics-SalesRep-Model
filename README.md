# Logistics Sales Assistant

An email-automation system for logistics sales. It processes customer shipping
quote requests, extracts structured data from free-form email, generates
professional replies, and manages multi-turn conversations with cumulative data
merging across a thread. Forwarder responses are parsed for rates and collated
into notifications for the sales team.

The system is built as a [LangGraph](https://github.com/langchain-ai/langgraph)
state machine that orchestrates a set of single-responsibility agents, backed by
a Databricks-hosted Claude model.

## Requirements

- Python 3.12+
- A Databricks model-serving endpoint and access token

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Provide credentials (the token is read from the environment, never committed)
cp .env.example .env
# edit .env and set DATABRICKS_TOKEN
```

Non-secret settings (endpoint base URL and model name) live in
[config/config.json](config/config.json) and can be overridden by the
`DATABRICKS_BASE_URL` and `MODEL_ENDPOINT_ID` environment variables.

## Running

```bash
# API server (:5001) + static frontend (:5002)
./start_servers.sh
# open http://localhost:5002

# Streamlit demo instead
streamlit run demo_app.py
```

For containerized deployment see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## How it works

```
Email → Classification → Conversation State → Thread Analysis →
Information Extraction → Data Validation → Port Lookup →
Container Standardization → Rate Recommendation → Next Action →
Response Generation → Thread Update
```

A LangGraph orchestrator routes each email through single-responsibility agents,
accumulating state across the thread and choosing the outbound action
(clarification, confirmation, forwarder assignment, or sales notification). The
full picture is in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Project structure

```
.
├── agents/                             # Single-responsibility workflow agents
│   └── base_agent.py                   # Shared base class + LLM configuration
├── langgraph_workflow_orchestrator.py  # Main workflow orchestrator
├── api_server.py                       # FastAPI server for the web frontend
├── demo_app.py                         # Streamlit demo UI
├── frontend/                           # Static JS/HTML/CSS frontend
├── utils/                              # Thread, forwarder, and sales-team managers
├── models/schemas.py                   # Pydantic data models
├── config/                             # Non-secret configuration
├── data/                               # Thread state + port embeddings
└── docs/                               # Documentation (see below)
```

## Documentation

| Doc | What it covers |
| --- | --- |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, components, request flow, state & LLM config |
| [docs/AGENTS.md](docs/AGENTS.md) | Every agent and its responsibility |
| [docs/BUSINESS_RULES.md](docs/BUSINESS_RULES.md) | Validation, routing, merge, and rate rules |
| [docs/API.md](docs/API.md) | HTTP API endpoints |
| [docs/UI_GUIDE.md](docs/UI_GUIDE.md) | Using the web frontend |
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Docker / containerized deployment |
| [docs/EMAIL_IO_SPEC.md](docs/EMAIL_IO_SPEC.md) | Email input/output specification |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues |
| [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) | Demo run-of-show |

## Configuration

| File | Purpose |
| --- | --- |
| `config/config.json` | Endpoint base URL and model name (no secrets) |
| `config/sales_team.json` | Sales team assignments |
| `config/forwarders.json` | Forwarder directory |
| `.env` | Secrets (`DATABRICKS_TOKEN`) — not committed |

## License

Internal use only — DP World.
