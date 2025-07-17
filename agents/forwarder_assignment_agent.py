import os
import pandas as pd
from typing import Dict, Any, List

class ForwarderAssignmentAgent:
    """
    Agent to assign forwarders based on origin and destination country.
    Expects input as a dict with 'origin_country' and 'destination_country' keys.
    Returns a dict with forwarders for origin, destination, both, and all.
    """
    def __init__(self, csv_path: str):
        self.forwarders_db = pd.read_csv(csv_path)
        self.country_mapping = self._map_forwarders_by_country()

    def _map_forwarders_by_country(self) -> Dict[str, List[str]]:
        country_map = {}
        for _, row in self.forwarders_db.iterrows():
            forwarder = row['forwarder_name']
            country = row['country']
            if hasattr(forwarder, 'item'):
                forwarder = forwarder.item()
            if hasattr(country, 'item'):
                country = country.item()
            if pd.notna(forwarder) and pd.notna(country):
                forwarder_str = str(forwarder).strip()
                country_str = str(country).strip()
                if forwarder_str and country_str:
                    country_map.setdefault(country_str, []).append(forwarder_str)
        return country_map

    def assign_forwarders(self, origin_country: str, destination_country: str) -> Dict[str, Any]:
        origin_forwarders = set(self.country_mapping.get(origin_country, []))
        destination_forwarders = set(self.country_mapping.get(destination_country, []))
        both = origin_forwarders & destination_forwarders
        either = origin_forwarders | destination_forwarders
        return {
            "origin_forwarders": list(origin_forwarders),
            "destination_forwarders": list(destination_forwarders),
            "both_countries": list(both),
            "all_matches": list(either),
            "status": "success" if either else "no_match"
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expects input_data to have 'origin_country' and 'destination_country'.
        Returns a dict of forwarders for each region.
        """
        origin_country = input_data.get("origin_country")
        destination_country = input_data.get("destination_country")
        if not origin_country or not destination_country:
            return {"status": "error", "error": "origin_country and destination_country are required"}
        return self.assign_forwarders(origin_country, destination_country)

def main():
    import argparse
    import json
    parser = argparse.ArgumentParser(description="Assign forwarders by country.")
    parser.add_argument("--csv", required=True, help="Path to the forwarders CSV file.")
    parser.add_argument("--origin", required=True, help="Origin country.")
    parser.add_argument("--destination", required=True, help="Destination country.")
    args = parser.parse_args()

    agent = ForwarderAssignmentAgent(args.csv)
    result = agent.assign_forwarders(args.origin, args.destination)
    print(json.dumps(result, indent=2))


def test_forwarder_assignment_agent():
    csv_path = "Forwarders_with_Operators_and_Emails.csv"  # Update with your CSV path
    input_data = {
        "origin_country": "Brazil",
        "destination_country": "USA"
    }
    print("Input format:")
    print(input_data)
    agent = ForwarderAssignmentAgent(csv_path)
    output = agent.process(input_data)
    print("\nOutput format:")
    print(output)

if __name__ == "__main__":
    # Example usage for testing
    test_forwarder_assignment_agent()
    
