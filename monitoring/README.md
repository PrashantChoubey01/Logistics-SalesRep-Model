# Monitoring Setup

## Quick Start

```bash
# Install dependencies
pip install prometheus-client opentelemetry-exporter-prometheus

# Start Prometheus and Grafana
docker-compose up -d prometheus grafana

# Open Grafana
open http://localhost:3000
# Default credentials: admin/admin
```

## Import Dashboard

1. Open Grafana at `http://localhost:3000`
2. Go to Dashboards → Import
3. Upload `monitoring/dashboards/langgraph_email.json`

## Configure Alerts

1. Copy `monitoring/alerts.yaml` to your Prometheus alertmanager config
2. Update alertmanager to use the rules file
3. Configure PagerDuty webhook in alertmanager

## Metrics Available

- `agent_confidence` - Agent confidence scores
- `agent_latency_seconds` - Agent execution time
- `agent_tokens_total` - Token usage
- `email_processed_total` - Email processing results
- `email_hallucination_total` - Hallucination detections
- `email_grammar_score` - Grammar quality
- `email_word_count` - Word count
- `clarification_cycles_total` - Clarification loops
- `escalation_rate` - Escalation percentage
- `cost_per_email_usd` - Cost per email
- `forwarder_duplicate_sends_total` - Duplicate sends

## Alert Thresholds

- Hallucination rate: > 0.01 per second
- Agent confidence: < 0.85
- Latency p95: > 400ms
- Grammar score: < 95
- Cost per email: > $0.08
- Error rate: > 0.01 per second
- Clarification cycles: > 3
- Escalation rate: > 5%

