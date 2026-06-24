#!/usr/bin/env python3
"""Detects if an email is from a forwarder by checking against the forwarder database."""

import json
import logging
import os
from typing import Any, Dict, List

from agents.base_agent import BaseAgent


class ForwarderDetectionAgent(BaseAgent):
    """Agent for detecting if an email is from a forwarder."""

    def __init__(self):
        super().__init__("forwarder_detection_agent")
        self.logger = logging.getLogger(__name__)

        self.forwarder_emails = self._load_forwarder_emails_from_json()

    def _load_forwarder_emails_from_json(self) -> List[str]:
        """Load forwarder emails from JSON file."""
        try:
            json_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "config", "forwarders.json"
            )

            if not os.path.exists(json_path):
                self.logger.warning(f"Forwarder JSON file not found at {json_path}")
                return []

            with open(json_path, "r") as f:
                data = json.load(f)

            forwarders = data.get("forwarders", [])
            self.logger.info(f"Loaded {len(forwarders)} forwarder records from JSON")

            forwarder_emails = list(set(f["email"] for f in forwarders if f.get("email")))

            self.logger.info(f"Found {len(forwarder_emails)} unique forwarder email addresses")
            return forwarder_emails

        except Exception as e:
            self.logger.error(f"Error loading forwarder emails from JSON: {str(e)}")
            return []

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process forwarder detection."""
        print("FORWARDER_DETECTION: Starting forwarder detection...")

        try:
            email_data = input_data.get("email_data", {})
            sender_email = email_data.get("sender", "").lower().strip()

            is_forwarder = sender_email in [
                email.lower().strip() for email in self.forwarder_emails
            ]

            forwarder_details = None
            if is_forwarder:
                forwarder_details = self._get_forwarder_details(sender_email)

            result = {
                "is_forwarder": is_forwarder,
                "sender_email": sender_email,
                "forwarder_details": forwarder_details,
                "detection_method": "json_database_check",
                "total_forwarders_in_db": len(self.forwarder_emails),
                "agent_name": self.agent_name,
                "agent_id": self.agent_id,
                "processed_at": self._now_iso(),
                "status": "success",
            }

            print(f"FORWARDER_DETECTION: Email from forwarder = {is_forwarder}")
            if is_forwarder and forwarder_details:
                print(f"   Forwarder: {forwarder_details.get('name', 'Unknown')}")

            return result

        except Exception as e:
            self.logger.error(f"Error in forwarder detection: {str(e)}")
            return {
                "is_forwarder": False,
                "sender_email": input_data.get("email_data", {}).get("sender", ""),
                "forwarder_details": None,
                "error": str(e),
                "agent_name": self.agent_name,
                "agent_id": self.agent_id,
                "processed_at": self._now_iso(),
                "status": "error",
            }

    def _get_forwarder_details(self, sender_email: str) -> Dict[str, Any] | None:
        """Get forwarder details from JSON database."""
        try:
            json_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "config", "forwarders.json"
            )

            if not os.path.exists(json_path):
                return None

            with open(json_path, "r") as f:
                data = json.load(f)

            forwarders = data.get("forwarders", [])

            sender_email = sender_email.lower().strip()
            for forwarder in forwarders:
                if forwarder.get("email", "").lower().strip() == sender_email:
                    return {
                        "name": forwarder["name"],
                        "country": forwarder["country"],
                        "operator": forwarder["operator"],
                        "email": forwarder["email"],
                        "company": forwarder.get("company", forwarder["name"]),
                    }

            return None

        except Exception as e:
            self.logger.error(f"Error getting forwarder details: {str(e)}")
            return None

    def _now_iso(self):
        """Get current timestamp in ISO format."""
        from datetime import datetime

        return datetime.now().isoformat()


def test_forwarder_detection_agent():
    """Test the forwarder detection agent."""

    print("Testing Forwarder Detection Agent")
    print("=" * 50)

    agent = ForwarderDetectionAgent()

    # Test cases
    test_cases = [
        {
            "name": "Forwarder Email",
            "email": {
                "sender": "rates@globallogistics.com",
                "subject": "Rate Quote",
                "email_text": "Test email",
            },
        },
        {
            "name": "Customer Email",
            "email": {
                "sender": "john.smith@techcorp.com",
                "subject": "Rate Request",
                "email_text": "Test email",
            },
        },
        {
            "name": "Unknown Email",
            "email": {
                "sender": "unknown@example.com",
                "subject": "Test",
                "email_text": "Test email",
            },
        },
    ]

    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"   Sender: {test_case['email']['sender']}")

        result = agent.process({"email_data": test_case["email"]})

        print(f"   Is Forwarder: {result['is_forwarder']}")
        if result["forwarder_details"]:
            print(f"   Forwarder Name: {result['forwarder_details']['name']}")
            print(f"   Country: {result['forwarder_details']['country']}")

    print("\nForwarder Detection Test Completed")


if __name__ == "__main__":
    test_forwarder_detection_agent()
