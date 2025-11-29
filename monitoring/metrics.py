#!/usr/bin/env python3
"""
Prometheus Metrics
==================

Metrics exporters for monitoring agent performance and email quality.
"""

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("⚠️  prometheus_client not installed. Install with: pip install prometheus-client")

if PROMETHEUS_AVAILABLE:
    # Agent metrics
    agent_confidence = Histogram(
        "agent_confidence",
        "Agent confidence scores",
        ["agent_name"],
        buckets=[0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 1.0]
    )
    
    agent_latency = Histogram(
        "agent_latency_seconds",
        "Agent execution latency in seconds",
        ["agent_name"],
        buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 1.0, 2.0, 5.0]
    )
    
    agent_tokens = Histogram(
        "agent_tokens_total",
        "Total tokens used by agent",
        ["agent_name", "type"],  # type: input or output
        buckets=[100, 500, 1000, 2000, 5000, 10000]
    )
    
    # Email quality metrics
    email_processed_total = Counter(
        "email_processed_total",
        "Total emails processed",
        ["result"]  # result: success, clarify, escalate, error
    )
    
    email_hallucination_total = Counter(
        "email_hallucination_total",
        "LLM judge detected invented data",
        ["agent"]
    )
    
    email_grammar_score = Histogram(
        "email_grammar_score",
        "Email grammar quality score",
        buckets=[80, 85, 90, 95, 98, 100]
    )
    
    email_word_count = Histogram(
        "email_word_count",
        "Email word count",
        buckets=[50, 100, 150, 180, 200, 250, 300]
    )
    
    # Thread metrics
    clarification_cycles = Histogram(
        "clarification_cycles_total",
        "Number of clarification cycles per thread",
        buckets=[1, 2, 3, 4, 5, 10]
    )
    
    escalation_rate = Gauge(
        "escalation_rate",
        "Percentage of emails escalated"
    )
    
    # Business metrics
    cost_per_email = Histogram(
        "cost_per_email_usd",
        "Cost per email in USD",
        buckets=[0.01, 0.02, 0.05, 0.08, 0.10, 0.15, 0.20]
    )
    
    forwarder_duplicate_sends = Counter(
        "forwarder_duplicate_sends_total",
        "Duplicate forwarder rate requests detected"
    )
else:
    # Dummy metrics if prometheus_client not available
    class DummyMetric:
        def observe(self, *args, **kwargs): pass
        def inc(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
    
    agent_confidence = DummyMetric()
    agent_latency = DummyMetric()
    agent_tokens = DummyMetric()
    email_processed_total = DummyMetric()
    email_hallucination_total = DummyMetric()
    email_grammar_score = DummyMetric()
    email_word_count = DummyMetric()
    clarification_cycles = DummyMetric()
    escalation_rate = DummyMetric()
    cost_per_email = DummyMetric()
    forwarder_duplicate_sends = DummyMetric()

def record_agent_execution(agent_name: str, confidence: float, latency: float, input_tokens: int = 0, output_tokens: int = 0):
    """Record agent execution metrics"""
    if PROMETHEUS_AVAILABLE:
        agent_confidence.labels(agent_name=agent_name).observe(confidence)
        agent_latency.labels(agent_name=agent_name).observe(latency)
        if input_tokens > 0:
            agent_tokens.labels(agent_name=agent_name, type="input").observe(input_tokens)
        if output_tokens > 0:
            agent_tokens.labels(agent_name=agent_name, type="output").observe(output_tokens)

def record_email_processed(result: str):
    """Record email processing result"""
    if PROMETHEUS_AVAILABLE:
        email_processed_total.labels(result=result).inc()

def record_hallucination(agent_name: str):
    """Record hallucination detection"""
    if PROMETHEUS_AVAILABLE:
        email_hallucination_total.labels(agent=agent_name).inc()

def record_email_quality(grammar_score: float, word_count: int):
    """Record email quality metrics"""
    if PROMETHEUS_AVAILABLE:
        email_grammar_score.observe(grammar_score)
        email_word_count.observe(word_count)

def record_clarification_cycles(cycles: int):
    """Record clarification cycles"""
    if PROMETHEUS_AVAILABLE:
        clarification_cycles.observe(cycles)

def record_escalation_rate(rate: float):
    """Record escalation rate"""
    if PROMETHEUS_AVAILABLE:
        escalation_rate.set(rate)

def record_cost(cost_usd: float):
    """Record cost per email"""
    if PROMETHEUS_AVAILABLE:
        cost_per_email.observe(cost_usd)

def record_duplicate_forwarder():
    """Record duplicate forwarder send"""
    if PROMETHEUS_AVAILABLE:
        forwarder_duplicate_sends.inc()

