"""
Pydantic domain models for the LangGraph logistics workflow.

Maps to PHP: app/Classes/LogisticsAI/Models/*
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, StrictStr, validator


class TimestampedField(BaseModel):
    """Base class for fields with timestamps to track data freshness."""
    value: Any
    timestamp: datetime
    source: Optional[StrictStr] = None  # "customer", "forwarder", "bot", "system"


class ShipmentDetails(BaseModel):
    """Structured shipment fields extracted from customer emails."""

    origin_port: StrictStr = Field(..., description="Port of loading (POL) code or name")
    destination_port: StrictStr = Field(..., description="Port of discharge (POD) code or name")
    origin_country: Optional[StrictStr] = Field(None, description="Country for origin port")
    destination_country: Optional[StrictStr] = Field(None, description="Country for destination port")
    inco_terms: Optional[StrictStr] = Field(None, description="Commercial terms, e.g., FOB, CIF")
    cargo_description: Optional[StrictStr] = Field(None, description="High-level product description")
    weight_kg: Optional[float] = Field(None, ge=0)
    volume_cbm: Optional[float] = Field(None, ge=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    source: Optional[StrictStr] = None  # Track data source for freshness


class ContainerDetails(BaseModel):
    """Normalized container requirements."""

    container_type: StrictStr = Field(..., description="Container type such as 20GP, 40HC")
    container_count: Optional[int] = Field(1, ge=1)
    temperature_controlled: Optional[bool] = False
    hazardous: Optional[bool] = False


class TimelineInformation(BaseModel):
    """Requested or committed schedule windows."""

    ready_date: Optional[datetime]
    etd: Optional[datetime]
    eta: Optional[datetime]
    transit_time_days: Optional[int] = Field(None, ge=0)


class RateInformation(BaseModel):
    """Rate recommendation or forwarder quote details."""

    base_freight_usd: Optional[float]
    surcharge_usd: Optional[float]
    validity_end: Optional[datetime]
    currency: StrictStr = Field("USD")
    reasoning: Optional[StrictStr]


class SpecialRequirements(BaseModel):
    """Optional instructions such as insurance or documentation."""

    notes: List[StrictStr] = Field(default_factory=list)


class CumulativeExtraction(BaseModel):
    """Merged structured data representing the full thread state."""

    shipment_details: Optional[ShipmentDetails]
    container_details: Optional[ContainerDetails]
    timeline_information: Optional[TimelineInformation]
    rate_information: Optional[RateInformation]
    special_requirements: Optional[SpecialRequirements]
    additional_notes: Optional[StrictStr]
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    extraction_version: int = Field(default=1, description="Version counter for tracking updates")


class InboundEmail(BaseModel):
    """Incoming email payload validated at workflow entry."""

    message_id: StrictStr
    thread_id: StrictStr
    from_email: EmailStr
    to_email: EmailStr
    subject: StrictStr
    body_text: StrictStr
    body_html: Optional[StrictStr] = None
    received_at: datetime
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class EmailEntryModel(BaseModel):
    """Thread entry representing inbound or outbound communication."""

    timestamp: datetime
    email_id: StrictStr
    sender: StrictStr
    direction: StrictStr
    subject: StrictStr
    content: StrictStr
    response_type: Optional[StrictStr]
    extracted_data: Optional[CumulativeExtraction]
    bot_response: Optional[Dict[str, Any]]
    workflow_id: Optional[StrictStr]
    confidence_score: Optional[float] = Field(None, ge=0, le=1)


class ThreadDataModel(BaseModel):
    """Persisted conversation context for a thread."""

    thread_id: StrictStr
    email_chain: List[EmailEntryModel] = Field(default_factory=list)
    cumulative_extraction: Optional[CumulativeExtraction]
    last_updated: datetime
    customer_context: Dict[str, Any] = Field(default_factory=dict)
    forwarder_context: Dict[str, Any] = Field(default_factory=dict)
    conversation_state: StrictStr = "new_thread"
    total_emails: int = 0


class ClassificationResult(BaseModel):
    """Output from the unified email classifier agent."""

    email_type: StrictStr
    sender_type: StrictStr
    intent: Optional[StrictStr]
    confidence: float = Field(0.0, ge=0, le=1)
    escalation_needed: bool = False
    sender_classification: Dict[str, Any] = Field(default_factory=dict)


class ValidationResult(BaseModel):
    """Structured validation output summarizing missing fields."""

    is_complete: bool
    missing_fields: List[StrictStr] = Field(default_factory=list)
    invalid_fields: List[StrictStr] = Field(default_factory=list)
    reasoning: Optional[StrictStr]
    confidence: float = Field(0.0, ge=0, le=1)


class NextActionDecision(BaseModel):
    """Decision from NextActionAgent describing workflow branch."""

    next_action: StrictStr
    missing_fields: List[StrictStr] = Field(default_factory=list)
    should_escalate: bool = False
    reasoning: Optional[StrictStr]


class ForwarderAssignment(BaseModel):
    """Assignment metadata for selected forwarder."""

    name: StrictStr
    email: EmailStr
    country: StrictStr
    operator: Optional[StrictStr]
    route_hint: Optional[StrictStr]


class WorkflowStateModel(BaseModel):
    """Pydantic view of workflow state for validation/logging."""

    inbound_email: InboundEmail
    thread: Optional[ThreadDataModel]
    classification_result: Optional[ClassificationResult]
    validation_result: Optional[ValidationResult]
    next_action_result: Optional[NextActionDecision]
    forwarder_assignment: Optional[ForwarderAssignment]
    cumulative_extraction: Optional[CumulativeExtraction]
    workflow_history: List[StrictStr] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @validator("workflow_history", pre=True, always=True)
    def _ensure_history(cls, value: Optional[List[str]]) -> List[str]:
        return value or []

