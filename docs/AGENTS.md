# Agents

Every agent subclasses `BaseAgent` (`agents/base_agent.py`), which provides the
shared LLM client, configuration, logging, and a common `load_context()` /
`process()` interface. Each agent owns one responsibility and is wired into the
workflow by `langgraph_workflow_orchestrator.py`.

Agents are listed below in roughly the order they participate in the pipeline.

## Classification & conversation context

| Agent | Responsibility |
| --- | --- |
| `UnifiedEmailClassifierAgent` | Classifies the email type and sender (customer vs forwarder) using a dedicated LLM. |
| `ConversationStateAgent` | Analyzes the thread's conversation state and determines where the exchange stands. |
| `ThreadContextAnalyzerAgent` | Tracks conversation progression and detects vague-response patterns across the thread. |

## Extraction & validation

| Agent | Responsibility |
| --- | --- |
| `InformationExtractionAgent` | Extracts structured shipment/contact/timeline data from free-form email, with recency-based priority. |
| `DataValidationAgent` | Validates the extracted data against the FCL/LCL requirement rules. |

## Enrichment

| Agent | Responsibility |
| --- | --- |
| `PortLookupAgent` | Resolves free-form port names to port code, canonical name, and a confidence score (uses `port_names.json` + embeddings). |
| `ContainerStandardizationAgent` | Normalizes container descriptions (e.g. "40 footer" → "40HC") via LLM with fallback logic. |

## Rates

| Agent | Responsibility |
| --- | --- |
| `RateRecommendationAgent` | Recommends a rate from origin/destination/container data and computes a market range (±10% around the market average). |

## Decisioning

| Agent | Responsibility |
| --- | --- |
| `NextActionAgent` | Decides the next workflow action from the conversation state and data completeness. |
| `EscalationDecisionAgent` | Decides when and how a thread should be escalated. |

## Customer responses

| Agent | Responsibility |
| --- | --- |
| `ClarificationResponseAgent` | Drafts a request for the missing mandatory fields. |
| `ConfirmationResponseAgent` | Drafts a confirmation request summarizing the extracted shipment details. |
| `ConfirmationAcknowledgmentAgent` | Drafts the acknowledgment sent once the customer confirms. |
| `AcknowledgmentResponseAgent` | Generates acknowledgment responses tailored to the sender type. |

## Forwarder handling

| Agent | Responsibility |
| --- | --- |
| `ForwarderDetectionAgent` | Detects whether an inbound email is from a forwarder. |
| `ForwarderResponseAgent` | Handles forwarder communications and parses their rate replies. |
| `ForwarderEmailDraftAgent` | Drafts professional rate-request emails to forwarders, with sales-manager signatures. |

## Sales

| Agent | Responsibility |
| --- | --- |
| `SalesNotificationAgent` | Builds the collated sales-team notification with customer, shipment, forwarder, and rate details. |

See [ARCHITECTURE.md](ARCHITECTURE.md) for how these are sequenced and
[BUSINESS_RULES.md](BUSINESS_RULES.md) for the rules they enforce.
