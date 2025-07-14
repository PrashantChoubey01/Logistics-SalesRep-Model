"""Rate recommendation agent for logistics pricing"""

import os
import sys
import pandas as pd
from typing import Dict, Any, Optional
import re
from datetime import datetime
import json

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from base_agent import BaseAgent
except ImportError:
    from agents.base_agent import BaseAgent

class RateRecommendationAgent(BaseAgent):
    """Agent for providing rate recommendations based on Origin_Code, Destination_Code, and Container_Type"""

    def __init__(self):
        super().__init__("rate_recommendation_agent")
        self.rates_df = None
        self.data_loaded = False
        self.data_file_path = None

    def load_context(self) -> bool:
        """Load rate data from CSV file"""
        try:
            possible_paths = [
                "rate_recommendation.csv",
                "data/rate_recommendation.csv",
                os.path.join(os.path.dirname(__file__), "rate_recommendation.csv"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "rate_recommendation.csv"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "rate_recommendation.csv")
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    self.data_file_path = path
                    break
            if not self.data_file_path:
                print("✗ rate_recommendation.csv file not found")
                return False
            self.rates_df = pd.read_csv(self.data_file_path)
            self._clean_rate_data()
            self.data_loaded = True
            print(f"✓ Rate data loaded: {len(self.rates_df)} records from {self.data_file_path}")
            return True
        except Exception as e:
            print(f"✗ Failed to load rate data: {e}")
            return False

    def _clean_rate_data(self):
        """Clean and normalize the rate data"""
        if self.rates_df is None:
            return
        # Clean string columns
        for col in ['Origin_Code', 'Destination_Code', 'Container_Type']:
            if col in self.rates_df.columns:
                self.rates_df[col] = self.rates_df[col].astype(str).str.strip().str.upper()
        # Clean numeric columns
        for col in ['Market_Average', 'Market_Low', 'Market_High']:
            if col in self.rates_df.columns:
                self.rates_df[col] = pd.to_numeric(self.rates_df[col], errors='coerce')

    def _extract_origin(self, input_data: Dict[str, Any]) -> Optional[str]:
        for key in ['Origin_Code', 'origin', 'origin_code', 'from', 'from_port']:
            if key in input_data and input_data[key]:
                return str(input_data[key]).strip().upper()
        return None

    def _extract_destination(self, input_data: Dict[str, Any]) -> Optional[str]:
        for key in ['Destination_Code', 'destination', 'destination_code', 'to', 'to_port']:
            if key in input_data and input_data[key]:
                return str(input_data[key]).strip().upper()
        return None

    def _extract_container_type(self, input_data: Dict[str, Any]) -> Optional[str]:
        for key in ['Container_Type', 'container_type', 'container', 'type']:
            if key in input_data and input_data[key]:
                return str(input_data[key]).strip().upper()
        return None

    def _normalize_container_type(self, container_type: str) -> str:
        mapping = {
            "20GP": "20DC", "40GP": "40DC", "40HQ": "40HC", "40CUBE": "40HC",
            "20RF": "20RE", "40RF": "40RH"
        }
        ct = container_type.upper().strip()
        return mapping.get(ct, ct)

    def _parse_price_range(self, price_range_str: str) -> Optional[str]:
        """Convert '[919,1249]' to '$919 - $1249'"""
        if not price_range_str or not isinstance(price_range_str, str):
            return None
        match = re.match(r"\[(\d+),\s*(\d+)\]", price_range_str.replace(" ", ""))
        if match:
            min_val, max_val = match.groups()
            return f"${int(min_val):,} - ${int(max_val):,}"
        return None

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if not self.data_loaded:
            return {"error": "Rate data not loaded. Please check if rate_recommendation.csv exists."}

        origin = self._extract_origin(input_data)
        destination = self._extract_destination(input_data)
        container_type = self._extract_container_type(input_data)

        if not origin:
            return {"error": "Origin code not provided"}
        if not destination:
            return {"error": "Destination code not provided"}
        if not container_type:
            return {"error": "Container type not provided"}

        container_type = self._normalize_container_type(container_type)
        matches_df = self.rates_df[
            (self.rates_df['Origin_Code'] == origin) &
            (self.rates_df['Destination_Code'] == destination) &
            (self.rates_df['Container_Type'] == container_type)
        ]

        indicative_rate = None
        price_range_str = None
        if not matches_df.empty and 'price_range_recommendation' in matches_df.columns:
            price_range_str = matches_df['price_range_recommendation'].dropna().astype(str).values
            if len(price_range_str) > 0:
                price_range_str = price_range_str[0]
                indicative_rate = self._parse_price_range(price_range_str)

        # Fallback: try to get from any available match (ignore container type)
        if not indicative_rate:
            fallback_df = self.rates_df[
                (self.rates_df['Origin_Code'] == origin) &
                (self.rates_df['Destination_Code'] == destination)
            ]
            if not fallback_df.empty and 'price_range_recommendation' in fallback_df.columns:
                price_range_str = fallback_df['price_range_recommendation'].dropna().astype(str).values
                if len(price_range_str) > 0:
                    price_range_str = price_range_str[0]
                    indicative_rate = self._parse_price_range(price_range_str)

        # Prepare rate_results (minimal for this example)
        if not matches_df.empty:
            match_type = "exact_match"
            total_found = len(matches_df)
            rate_range = indicative_rate
        elif indicative_rate:
            match_type = "route_only"
            total_found = len(fallback_df)
            rate_range = indicative_rate
        else:
            match_type = "no_match"
            total_found = 0
            rate_range = None

        rate_results = {
            "match_type": match_type,
            "total_rates_found": total_found,
            "rate_range": rate_range,
        }

        return {
            "query": {
                "Origin_Code": origin,
                "Destination_Code": destination,
                "Container_Type": container_type
            },
            "rate_recommendation": rate_results,
            "indicative_rate": indicative_rate,
            "data_source": self.data_file_path,
            "total_records_searched": len(self.rates_df)
        }

# =====================================================
#                 🔁 Local Test Harness
# =====================================================

def test_rate_recommendation_agent():
    print("=== Testing Rate Recommendation Agent ===")
    agent = RateRecommendationAgent()
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}")
    test_cases = [
        {
            "Origin_Code": "AEAUH",
            "Destination_Code": "AUBNE",
            "Container_Type": "20DC"
        },
        {
            "origin": "AEAUH",
            "destination": "AUBNE",
            "container_type": "40HC"
        },
        {
            "origin": "AEAUH",
            "destination": "BDCGP",
            "container_type": "20TK"
        },
        {
            "Origin_Code": "INVALID",
            "Destination_Code": "NOTFOUND",
            "Container_Type": "40DC"
        }
    ]
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test}")
        result = agent.run(test)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_rate_recommendation_agent()
