#!/usr/bin/env python3
"""Forwarder assignment based on country matching and route optimization."""

import json
import logging
import os
import random
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ForwarderManager:
    """Manages forwarder assignment and routing"""

    def __init__(self, json_file_path: str = "config/forwarders.json"):
        self.json_file_path = json_file_path
        self.forwarders_data = None
        self.forwarders_by_country = {}
        self.load_forwarders()

    def load_forwarders(self):
        """Load forwarders from JSON file"""
        try:
            if not os.path.exists(self.json_file_path):
                logger.error(f"Forwarder JSON file not found: {self.json_file_path}")
                return

            with open(self.json_file_path, "r") as f:
                data = json.load(f)

            self.forwarders_data = data.get("forwarders", [])
            logger.info(f"Loaded {len(self.forwarders_data)} forwarder entries")

            # Create country-based lookup
            for forwarder in self.forwarders_data:
                country = forwarder["country"].strip()
                if country not in self.forwarders_by_country:
                    self.forwarders_by_country[country] = []

                forwarder_info = {
                    "name": forwarder["name"],
                    "country": country,
                    "operator": forwarder["operator"],
                    "email": forwarder["email"],
                    "company": forwarder.get("company", forwarder["name"]),
                }
                self.forwarders_by_country[country].append(forwarder_info)

            logger.info(f"Created forwarder lookup for {len(self.forwarders_by_country)} countries")

        except Exception as e:
            logger.error(f"Error loading forwarders: {e}")

    def get_forwarders_by_country(self, country: str) -> List[Dict]:
        """Get forwarders for a specific country"""
        country = country.strip()
        return self.forwarders_by_country.get(country, [])

    def assign_forwarder_with_reason(
        self, origin_country: str, destination_country: str
    ) -> Tuple[Optional[Dict], Dict]:
        """
        Assign a forwarder and explain WHY it was chosen.

        Strategy (matches the business rule "fulfilment region, else randomness"):
          Priority 1 — a forwarder serving the DESTINATION fulfilment region.
          Priority 2 — a forwarder serving the ORIGIN fulfilment region.
          Priority 3 — a RANDOM forwarder from the pool (no regional match available).
        When a region has more than one forwarder we pick randomly among them, so load
        is spread rather than always hitting the first entry.

        Returns (forwarder_or_None, reason_dict) where reason_dict carries a machine
        field (`matched_on`) and a human-readable `description` for display.
        """
        origin_country = (origin_country or "").strip()
        destination_country = (destination_country or "").strip()

        logger.info(
            f"Assigning forwarder for route: {origin_country or '?'} -> {destination_country or '?'}"
        )

        # Priority 1: Forwarders serving the destination region
        destination_forwarders = (
            self.get_forwarders_by_country(destination_country) if destination_country else []
        )
        if destination_forwarders:
            selected = random.choice(destination_forwarders)
            reason = {
                "matched_on": "destination_region",
                "matched_country": destination_country,
                "priority": 1,
                "description": (
                    f"Assigned because {selected['name']} serves the destination region "
                    f"({destination_country})."
                ),
            }
            logger.info(
                f"Assigned forwarder from destination region {destination_country}: {selected['name']}"
            )
            return selected, reason

        # Priority 2: Forwarders serving the origin region
        origin_forwarders = self.get_forwarders_by_country(origin_country) if origin_country else []
        if origin_forwarders:
            selected = random.choice(origin_forwarders)
            reason = {
                "matched_on": "origin_region",
                "matched_country": origin_country,
                "priority": 2,
                "description": (
                    f"Assigned because {selected['name']} serves the origin region "
                    f"({origin_country}); no forwarder was available for the destination "
                    f"region ({destination_country or 'unknown'})."
                ),
            }
            logger.info(
                f"Assigned forwarder from origin region {origin_country}: {selected['name']}"
            )
            return selected, reason

        # Priority 3: Random forwarder from the whole pool (no regional match)
        all_forwarders = [
            f for forwarders in self.forwarders_by_country.values() for f in forwarders
        ]
        if all_forwarders:
            selected = random.choice(all_forwarders)
            reason = {
                "matched_on": "random",
                "matched_country": selected.get("country", ""),
                "priority": 3,
                "description": (
                    f"No forwarder serves the requested route "
                    f"({origin_country or 'unknown'} → {destination_country or 'unknown'}); "
                    f"randomly assigned {selected['name']} ({selected.get('country', 'unknown')})."
                ),
            }
            logger.info(
                f"Randomly assigned fallback forwarder: {selected['name']} from {selected.get('country')}"
            )
            return selected, reason

        logger.warning(
            f"No forwarder available for route: {origin_country} -> {destination_country}"
        )
        return None, {
            "matched_on": "none",
            "matched_country": "",
            "priority": 0,
            "description": "No forwarders are configured; none could be assigned.",
        }

    def assign_forwarder_for_route(
        self, origin_country: str, destination_country: str
    ) -> Optional[Dict]:
        """Backward-compatible wrapper that returns only the forwarder (see
        `assign_forwarder_with_reason` for the reasoning)."""
        forwarder, _reason = self.assign_forwarder_with_reason(origin_country, destination_country)
        return forwarder

    def get_forwarder_by_email(self, email: str) -> Optional[Dict]:
        """Get forwarder information by email address"""
        if self.forwarders_data is None:
            return None

        email = email.strip().lower()
        for forwarder in self.forwarders_data:
            if forwarder["email"].strip().lower() == email:
                return {
                    "name": forwarder["name"],
                    "country": forwarder["country"],
                    "operator": forwarder["operator"],
                    "email": forwarder["email"],
                    "company": forwarder.get("company", forwarder["name"]),
                }
        return None

    def is_forwarder_email(self, email: str) -> bool:
        """Check if an email belongs to a forwarder"""
        return self.get_forwarder_by_email(email) is not None

    def get_all_forwarders(self) -> List[Dict]:
        """Get all forwarders"""
        if self.forwarders_data is None:
            return []

        return [
            {
                "name": f["name"],
                "country": f["country"],
                "operator": f["operator"],
                "email": f["email"],
                "company": f.get("company", f["name"]),
            }
            for f in self.forwarders_data
        ]

    def get_forwarders_by_operator(self, operator: str) -> List[Dict]:
        """Get forwarders by operator name"""
        if self.forwarders_data is None:
            return []

        operator = operator.strip()
        return [
            {
                "name": f["name"],
                "country": f["country"],
                "operator": f["operator"],
                "email": f["email"],
                "company": f.get("company", f["name"]),
            }
            for f in self.forwarders_data
            if f["operator"].strip() == operator
        ]

    def get_countries_with_forwarders(self) -> List[str]:
        """Get list of countries that have forwarders"""
        return list(self.forwarders_by_country.keys())

    def get_forwarder_statistics(self) -> Dict:
        """Get forwarder statistics"""
        if self.forwarders_data is None:
            return {}

        total_forwarders = len(self.forwarders_data)
        unique_companies = len(set(f["name"] for f in self.forwarders_data))
        unique_countries = len(self.forwarders_by_country)
        unique_operators = len(set(f["operator"] for f in self.forwarders_data))

        return {
            "total_forwarders": total_forwarders,
            "unique_companies": unique_companies,
            "unique_countries": unique_countries,
            "unique_operators": unique_operators,
            "countries_with_forwarders": list(self.forwarders_by_country.keys()),
        }
