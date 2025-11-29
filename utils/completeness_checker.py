"""
Shared helpers to determine whether collected shipment data is complete.
"""

from __future__ import annotations

from typing import Any, Dict, List

INCOTERM_KEYWORDS = [
    "incoterm",
    "fob",
    "cif",
    "cfr",
    "exw",
    "dap",
    "ddp",
    "dat",
    "fas",
    "fca",
]


def _gather_text_sources(state: Dict[str, Any]) -> List[str]:
    texts = []
    email_data = state.get("email_data", {})
    if email_data:
        texts.append(email_data.get("content", ""))
    for email in state.get("thread_history", []):
        texts.append(email.get("content", ""))
    return [text.lower() for text in texts if text]


def _normalize_shipment(state: Dict[str, Any]) -> Dict[str, Any]:
    cumulative = state.get("cumulative_extraction") or {}
    extracted = state.get("extraction_result", {}).get("extracted_data", {})
    return (
        cumulative.get("shipment_details")
        or extracted.get("shipment_details")
        or {}
    )


def _normalize_timeline(state: Dict[str, Any]) -> Dict[str, Any]:
    cumulative = state.get("cumulative_extraction") or {}
    extracted = state.get("extraction_result", {}).get("extracted_data", {})
    return (
        cumulative.get("timeline_information")
        or extracted.get("timeline_information")
        or {}
    )


def _has_incoterm_reference(shipment: Dict[str, Any], texts: List[str]) -> bool:
    if shipment.get("incoterms"):
        return True
    return any(
        keyword in text
        for text in texts
        for keyword in INCOTERM_KEYWORDS
    )


def _has_stackable_reference(shipment: Dict[str, Any], texts: List[str]) -> bool:
    if shipment.get("cargo_nature"):
        return True
    return any(term in text for term in ["stackable", "non-stackable"] for text in texts)


def is_information_complete(state: Dict[str, Any]) -> bool:
    """
    Determine if the cumulative shipment information satisfies business requirements.
    """

    shipment = _normalize_shipment(state)
    timeline = _normalize_timeline(state)
    texts = _gather_text_sources(state)

    origin = shipment.get("origin") or shipment.get("pol")
    destination = shipment.get("destination") or shipment.get("pod")
    container_type = shipment.get("container_type")
    if isinstance(container_type, dict):
        container_type = container_type.get("standardized_type") or container_type.get("standard_type")

    cargo_description = shipment.get("cargo_description") or shipment.get("commodity")
    shipment_type = shipment.get("shipment_type")
    if not shipment_type:
        if container_type:
            shipment_type = "FCL"
        elif shipment.get("total_weight") or shipment.get("package_count"):
            shipment_type = "LCL"

    weight_value = (
        shipment.get("weight_per_container")
        or shipment.get("weight")
        or shipment.get("total_weight")
    )
    volume_value = shipment.get("volume") or shipment.get("total_volume")

    missing = []

    if not origin:
        missing.append("origin")
    if not destination:
        missing.append("destination")
    if not cargo_description:
        missing.append("cargo_description")
    if not container_type:
        missing.append("container_type")

    if shipment_type == "FCL":
        if not shipment.get("container_count"):
            missing.append("container_count")
        if not weight_value:
            missing.append("weight")
    elif shipment_type == "LCL":
        if not shipment.get("package_count"):
            missing.append("package_count")
        if not weight_value:
            missing.append("total_weight")
        if not shipment.get("dimensions"):
            missing.append("dimensions")
    else:
        if not weight_value and not volume_value:
            missing.append("weight_or_volume")

    if shipment.get("cargo_type") in {"Dangerous Goods", "dangerous_goods", "dg"} and not shipment.get("msds_available"):
        missing.append("msds")
    if shipment.get("cargo_type") in {"Perishable Goods", "perishable", "reefer"} and not shipment.get("temperature_control"):
        missing.append("temperature_control")
    if not _has_stackable_reference(shipment, texts):
        missing.append("cargo_nature")

    if not _has_incoterm_reference(shipment, texts):
        missing.append("incoterms")

    if not (
        timeline.get("ready_date")
        or timeline.get("etd")
        or timeline.get("requested_dates")
    ):
        missing.append("timeline")

    if shipment.get("door_delivery") and not shipment.get("delivery_address"):
        missing.append("delivery_address")

    return len([item for item in missing if item not in {"cargo_nature"}]) == 0

