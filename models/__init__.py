"""
Domain models package for the logistics AI workflow.

Maps to PHP: app/Classes/LogisticsAI/Models/*
"""

from .schemas import (  # noqa: F401
    InboundEmail,
    EmailEntryModel,
    ThreadDataModel,
    ShipmentDetails,
    ContainerDetails,
    TimelineInformation,
    RateInformation,
    SpecialRequirements,
    CumulativeExtraction,
    ClassificationResult,
    ValidationResult,
    NextActionDecision,
    ForwarderAssignment,
    WorkflowStateModel,
)

