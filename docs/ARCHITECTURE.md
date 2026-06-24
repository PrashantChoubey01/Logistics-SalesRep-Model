# Architecture

## Overview

The system is a multi-agent email-automation pipeline for logistics sales. An
inbound email enters a [LangGraph](https://github.com/langchain-ai/langgraph)
state machine that routes it through single-responsibility agents and produces
either a drafted reply to the customer/forwarder or a notification to the sales
team. State accumulates across the whole email thread.

## Components

- **Orchestrator** — `langgraph_workflow_orchestrator.py`. Defines the workflow
  state, builds the LangGraph node/edge graph, wires in the agents, and drives
  execution. This is the entry point for processing an email.
- **Agents** — `agents/`. One responsibility each; see [AGENTS.md](AGENTS.md).
  All share `BaseAgent` for LLM access, config, and logging.
- **Managers / utilities** — `utils/`:
  - `thread_manager.py` — persists threads and merges new extractions into the
    running cumulative state (see [BUSINESS_RULES.md](BUSINESS_RULES.md)).
  - `forwarder_manager.py` — forwarder directory and region-based assignment.
  - `sales_team_manager.py` — sales-team assignments.
  - `name_extractor.py`, `logger.py` — helpers.
- **Models** — `models/schemas.py`. Pydantic models describing the domain data
  (emails, shipment details, cumulative extraction, classification/validation
  results). Used as the data contract.
- **Interfaces**:
  - `api_server.py` — FastAPI server exposing `POST /api/process-email`
    (see [API.md](API.md)); serves the static frontend in `frontend/`.
  - `demo_app.py` — Streamlit UI for interactive testing.

## Request flow

```
Email → Classification → Conversation State → Thread Analysis →
Information Extraction → Data Validation → Port Lookup →
Container Standardization → Rate Recommendation → Next Action →
Response Generation → Thread Update
```

The Next Action step selects the outbound path — clarification request,
confirmation request, confirmation acknowledgment, forwarder assignment, or
sales notification — according to the rules in
[BUSINESS_RULES.md](BUSINESS_RULES.md).

## State & persistence

- A single thread accumulates a `CumulativeExtraction`: shipment details,
  contact information, timeline, rate information, and special requirements.
- New emails are merged into the cumulative state with recency priority; empty
  values never overwrite existing data.
- Thread state is persisted as JSON under `data/threads/` (git-ignored).
- Port data lives in `port_names.json` and `data/embeddings/port_data.json`.

## LLM configuration

- Calls go to a Databricks-hosted Claude model via an OpenAI-compatible client.
- The access token is read only from the `DATABRICKS_TOKEN` environment variable
  (loaded from `.env`); the endpoint base URL and model name come from
  `config/config.json` and can be overridden by environment variables.
- See `agents/base_agent.py` for the resolution logic.
