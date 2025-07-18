import os
import pandas as pd
from typing import Dict, Any, List

class ForwarderAssignmentAgent:
    def __init__(self, csv_path: str):
        self.forwarders_db = pd.read_csv(csv_path)
        self.country_mapping = self._map_forwarders_by_country()

    def _map_forwarders_by_country(self) -> Dict[str, List[str]]:
        country_map = {}
        for _, row in self.forwarders_db.iterrows():
            forwarder = row["forwarder_name"]
            country = row["country"]
            if pd.notna(forwarder) and pd.notna(country):
                forwarder = forwarder.strip()
                country = country.strip()
                country_map.setdefault(country, []).append(forwarder)
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


# Example
agent = ForwarderAssignmentAgent("/Users/prashant.choubey/Documents/VSWorkspace/AI-Sales-Bot-V2/logistic-ai-response-model/Forwarders_with_Operators_and_Emails.csv")
result = agent.assign_forwarders("Brazil", "USA")

import json
print(json.dumps(result, indent=2))
