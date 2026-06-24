"""
Domain models package for the logistics AI workflow.

Maps to PHP: app/Classes/LogisticsAI/Models/*
"""

from .schemas import (  # noqa: F401
    ClassificationResult,
    ContainerDetails,
    CumulativeExtraction,
    EmailEntryModel,
    ForwarderAssignment,
    InboundEmail,
    NextActionDecision,
    RateInformation,
    ShipmentDetails,
    SpecialRequirements,
    ThreadDataModel,
    TimelineInformation,
    ValidationResult,
    WorkflowStateModel,
)
