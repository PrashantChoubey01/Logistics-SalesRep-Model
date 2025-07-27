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
        # First check if port_codes dictionary is provided
        if 'port_codes' in input_data and input_data['port_codes']:
            port_codes = input_data['port_codes']
            if 'origin' in port_codes and port_codes['origin']:
                return str(port_codes['origin']).strip().upper()
        
        # Then check direct keys
        for key in ['origin_code', 'Origin_Code', 'from_port', 'from', 'origin']:
            if key in input_data and input_data[key]:
                return str(input_data[key]).strip().upper()
        return None

    def _extract_destination(self, input_data: Dict[str, Any]) -> Optional[str]:
        # First check if port_codes dictionary is provided
        if 'port_codes' in input_data and input_data['port_codes']:
            port_codes = input_data['port_codes']
            if 'destination' in port_codes and port_codes['destination']:
                return str(port_codes['destination']).strip().upper()
        
        # Then check direct keys
        for key in ['destination_code', 'Destination_Code', 'to_port', 'to', 'destination']:
            if key in input_data and input_data[key]:
                return str(input_data[key]).strip().upper()
        return None

    def _extract_container_type(self, input_data: Dict[str, Any]) -> Optional[str]:
        # Check if shipment_details is provided
        if 'shipment_details' in input_data and input_data['shipment_details']:
            shipment_details = input_data['shipment_details']
            if 'container_type' in shipment_details:
                container_type = shipment_details['container_type']
                # Handle both string and dict formats
                if isinstance(container_type, dict):
                    # If it's a standardized container type dict, get the standard_type
                    if 'standard_type' in container_type:
                        return str(container_type['standard_type']).strip().upper()
                    elif 'standardized_type' in container_type:
                        return str(container_type['standardized_type']).strip().upper()
                else:
                    return str(container_type).strip().upper()
        
        # Then check direct keys
        for key in ['Container_Type', 'container_type', 'container', 'type']:
            if key in input_data and input_data[key]:
                container_type = input_data[key]
                # Handle both string and dict formats
                if isinstance(container_type, dict):
                    if 'standard_type' in container_type:
                        return str(container_type['standard_type']).strip().upper()
                    elif 'standardized_type' in container_type:
                        return str(container_type['standardized_type']).strip().upper()
                else:
                    return str(container_type).strip().upper()
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

        # Debug: Print all input data to see what's being passed
        print(f"🔍 Rate Recommendation Agent Input Data: {input_data}")
        
        origin = self._extract_origin(input_data)
        destination = self._extract_destination(input_data)
        container_type = self._extract_container_type(input_data)
        
        # Debug: Print what was extracted
        print(f"🔍 Extracted - Origin: '{origin}', Destination: '{destination}', Container: '{container_type}'")

        if not origin:
            return {"status": "no_data", "message": "Origin code not provided", "origin_code": None, "destination_code": None, "container_type": None}
        if not destination:
            return {"status": "no_data", "message": "Destination code not provided", "origin_code": origin, "destination_code": None, "container_type": container_type}
        if not container_type:
            return {"status": "no_data", "message": "Container type not provided", "origin_code": origin, "destination_code": destination, "container_type": None}

        container_type = self._normalize_container_type(container_type)
        
        # Check if rates_df is loaded
        if self.rates_df is None:
            return {"status": "error", "message": "Rate data not loaded", "origin_code": origin, "destination_code": destination, "container_type": container_type}
            
        matches_df = self.rates_df[
            (self.rates_df['Origin_Code'] == origin) &
            (self.rates_df['Destination_Code'] == destination) &
            (self.rates_df['Container_Type'] == container_type)
        ]

        indicative_rate = None
        price_range_str = None
        if not matches_df.empty and 'price_range_recommendation' in matches_df.columns:
            price_range_series = matches_df['price_range_recommendation'].dropna()
            if len(price_range_series) > 0:
                price_range_str = str(price_range_series.iloc[0])
                indicative_rate = self._parse_price_range(price_range_str)

        # Fallback: try to get from any available match (ignore container type)
        if not indicative_rate:
            fallback_df = self.rates_df[
                (self.rates_df['Origin_Code'] == origin) &
                (self.rates_df['Destination_Code'] == destination)
            ]
            if not fallback_df.empty and 'price_range_recommendation' in fallback_df.columns:
                price_range_series = fallback_df['price_range_recommendation'].dropna()
                if len(price_range_series) > 0:
                    price_range_str = str(price_range_series.iloc[0])
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

        # Get the raw price range recommendation and market data from CSV
        price_range_recommendation = None
        market_average = None
        market_low = None
        market_high = None
        market_midlow = None
        market_midhigh = None
        rate_quality = None
        contract_length = None
        day = None
        
        # Get data from exact match first, then fallback
        source_df = matches_df if not matches_df.empty else fallback_df
        
        if not source_df.empty:
            # Get price range recommendation
            if 'price_range_recommendation' in source_df.columns:
                price_range_series = source_df['price_range_recommendation'].dropna()
            if len(price_range_series) > 0:
                price_range_recommendation = str(price_range_series.iloc[0])

            # Get market data
            if 'Market_Average' in source_df.columns:
                market_avg_series = source_df['Market_Average'].dropna()
                if len(market_avg_series) > 0:
                    market_average = str(market_avg_series.iloc[0])
            
            if 'Market_Low' in source_df.columns:
                market_low_series = source_df['Market_Low'].dropna()
                if len(market_low_series) > 0:
                    market_low = str(market_low_series.iloc[0])
            
            if 'Market_High' in source_df.columns:
                market_high_series = source_df['Market_High'].dropna()
                if len(market_high_series) > 0:
                    market_high = str(market_high_series.iloc[0])
            
            if 'Market_Midlow' in source_df.columns:
                market_midlow_series = source_df['Market_Midlow'].dropna()
                if len(market_midlow_series) > 0:
                    market_midlow = str(market_midlow_series.iloc[0])
            
            if 'Market_Midhigh' in source_df.columns:
                market_midhigh_series = source_df['Market_Midhigh'].dropna()
                if len(market_midhigh_series) > 0:
                    market_midhigh = str(market_midhigh_series.iloc[0])
            
            if 'Rate_Quality' in source_df.columns:
                rate_quality_series = source_df['Rate_Quality'].dropna()
                if len(rate_quality_series) > 0:
                    rate_quality = str(rate_quality_series.iloc[0])
            
            if 'Contract_Length' in source_df.columns:
                contract_length_series = source_df['Contract_Length'].dropna()
                if len(contract_length_series) > 0:
                    contract_length = str(contract_length_series.iloc[0])
            
            if 'Day' in source_df.columns:
                day_series = source_df['Day'].dropna()
                if len(day_series) > 0:
                    day = str(day_series.iloc[0])

        return {
            # Status and query information
            "status": "success" if indicative_rate else "no_data",
            "message": "Rate data found" if indicative_rate else "No rate data available for this route",
            "origin_code": origin,
            "destination_code": destination,
            "container_type": container_type,
            
            # Market data (expected by workflow)
            "market_average": market_average,
            "market_low": market_low,
            "market_high": market_high,
            "market_midlow": market_midlow,
            "market_midhigh": market_midhigh,
            "price_range_recommendation": price_range_recommendation,
            "rate_quality": rate_quality,
            "contract_length": contract_length,
            "day": day,
            
            # Additional data
            "match_type": match_type,
            "total_rates_found": total_found,
            "indicative_rate": indicative_rate,
            "formatted_rate_range": rate_range,
            "data_source": self.data_file_path,
            "total_records_searched": len(self.rates_df) if self.rates_df is not None else 0
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
