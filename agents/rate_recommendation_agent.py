"""Rate recommendation agent for logistics pricing"""

import os
import sys
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import re
from datetime import datetime, timedelta

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import base agent
try:
    from .base_agent import BaseAgent
except ImportError:
    try:
        from base_agent import BaseAgent
    except ImportError as e:
        import logging
        logging.error(f"Cannot import BaseAgent: {e}")
        # Create minimal fallback
        from abc import ABC, abstractmethod
        class BaseAgent(ABC):
            def __init__(self, name): 
                self.agent_name = name
                self.logger = logging.getLogger(name)
                self.client = None
                self.config = {}
            def load_context(self): return True
            @abstractmethod
            def process(self, input_data): pass
            def run(self, input_data): 
                try:
                    result = self.process(input_data)
                    result["status"] = "success"
                    return result
                except Exception as e:
                    return {"error": str(e), "status": "error"}

class RateRecommendationAgent(BaseAgent):
    """Agent for providing rate recommendations based on Origin_Code, Destination_Code, and Container_Type"""

    def __init__(self):
        super().__init__("rate_recommendation_agent")
        
        # Data storage
        self.rates_df = None
        self.data_loaded = False
        self.data_file_path = None
        
        # Configuration - using exact column names from your data
        self.filter_columns = {
            'origin': 'Origin_Code',
            'destination': 'Destination_Code', 
            'container_type': 'Container_Type'
        }
        
        self.rate_columns = {
            'market_average': 'Market_Average',
            'market_low': 'Market_Low',
            'market_high': 'Market_High',
            'market_midlow': 'Market_Midlow',
            'market_midhigh': 'Market_Midhigh'
        }
        
        self.metadata_columns = {
            'contract_length': 'Contract_Length',
            'contracted_within_day': 'Contracted_WithinDay',
            'rate_quality': 'Rate_Quality',
            'aggregation_level': 'Aggregation_Level',
            'used_origin': 'Used_Origin',
            'used_destination': 'Used_Destination',
            'thc_methodology': 'THC_Methodology',
            'price_range_recommendation': 'price_range_recommendation'
        }
        
        # Container type normalization
        self.container_type_mapping = {
            # Standard containers
            "20DC": "20DC", "40DC": "40DC", "40HC": "40HC",
            
            # Reefer containers (from your data: 20RE, 40RH)
            "20RE": "20RE", "20RF": "20RE",  # Map 20RF to 20RE (your data format)
            "40RH": "40RH", "40RF": "40RH",  # Map 40RF to 40RH (your data format)
            
            # Tank containers
            "20TK": "20TK", "40TK": "40TK",
            
            # Alternative names
            "20GP": "20DC", "40GP": "40DC",
            "40HQ": "40HC", "40CUBE": "40HC"
        }

    def load_context(self) -> bool:
        """Load rate data from CSV file"""
        try:
            # Try multiple possible locations for the CSV file
            possible_paths = [
                "rate_recommendation.csv",
                "data/rate_recommendation.csv",
                "../rate_recommendation.csv",
                "../../rate_recommendation.csv",
                os.path.join(os.path.dirname(__file__), "rate_recommendation.csv"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "rate_recommendation.csv"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "rate_recommendation.csv")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.data_file_path = path
                    break
            
            if not self.data_file_path:
                self.logger.error("rate_recommendation.csv file not found in any expected location")
                print("✗ rate_recommendation.csv file not found")
                return False
            
            # Load the CSV data
            self.rates_df = pd.read_csv(self.data_file_path)
            
            # Validate required columns using exact names
            required_columns = ['Origin_Code', 'Destination_Code', 'Container_Type', 'Market_Average']
            missing_columns = [col for col in required_columns if col not in self.rates_df.columns]
            
            if missing_columns:
                self.logger.error(f"Missing required columns in CSV: {missing_columns}")
                print(f"✗ Missing required columns: {missing_columns}")
                print(f"Available columns: {list(self.rates_df.columns)}")
                return False
            
            # Clean and normalize the data
            self._clean_rate_data()
            
            self.data_loaded = True
            self.logger.info(f"Rate data loaded successfully from {self.data_file_path}")
            print(f"✓ Rate data loaded: {len(self.rates_df)} records from {self.data_file_path}")
            print(f"✓ Available columns: {list(self.rates_df.columns)}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load rate data: {e}")
            print(f"✗ Failed to load rate data: {e}")
            return False

    def _clean_rate_data(self):
        """Clean and normalize the rate data using exact column names"""
        if self.rates_df is None:
            return
        
        # Clean string columns
        string_columns = ['Origin_Code', 'Destination_Code', 'Container_Type', 'Used_Origin', 'Used_Destination']
        for col in string_columns:
            if col in self.rates_df.columns:
                self.rates_df[col] = self.rates_df[col].astype(str).str.strip()
        
        # Normalize container types
        if 'Container_Type' in self.rates_df.columns:
            self.rates_df['Container_Type'] = self.rates_df['Container_Type'].apply(self._normalize_container_type)
        
        # Clean numeric rate columns
        rate_columns = ['Market_Average', 'Market_Low', 'Market_High', 'Market_Midlow', 'Market_Midhigh']
        for col in rate_columns:
            if col in self.rates_df.columns:
                self.rates_df[col] = pd.to_numeric(self.rates_df[col], errors='coerce')
        
        # Parse price range recommendation
        if 'price_range_recommendation' in self.rates_df.columns:
            self.rates_df[['range_min', 'range_max']] = self.rates_df['price_range_recommendation'].apply(self._parse_price_range).apply(pd.Series)
        
        # Remove rows with invalid data
        initial_count = len(self.rates_df)
        self.rates_df = self.rates_df.dropna(subset=['Origin_Code', 'Destination_Code', 'Container_Type', 'Market_Average'])
        final_count = len(self.rates_df)
        
        if initial_count != final_count:
            print(f"✓ Cleaned data: {initial_count} → {final_count} records (removed {initial_count - final_count} invalid rows)")

    def _normalize_container_type(self, container_type: str) -> str:
        """Normalize container type to match your data format"""
        if not isinstance(container_type, str):
            return "40DC"
        
        container_type = container_type.upper().strip()
        return self.container_type_mapping.get(container_type, container_type)

    def _parse_price_range(self, price_range_str: str) -> tuple:
        """Parse price range recommendation like '[919,1249]'"""
        try:
            if pd.isna(price_range_str) or not isinstance(price_range_str, str):
                return None, None
            
            # Remove brackets and split
            clean_range = price_range_str.strip('[]')
            if ',' in clean_range:
                min_val, max_val = clean_range.split(',')
                return float(min_val.strip()), float(max_val.strip())
        except:
            pass
        
        return None, None

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process rate recommendation request using Origin_Code, Destination_Code, Container_Type
        
        Expected input formats:
        - {"origin": "AEAUH", "destination": "AUBNE", "container_type": "20DC"}
        - {"Origin_Code": "AEAUH", "Destination_Code": "AUBNE", "Container_Type": "20DC"}
        """
        
        if not self.data_loaded:
            return {"error": "Rate data not loaded. Please check if rate_recommendation.csv exists."}
        
        # Extract and normalize input parameters
        origin = self._extract_origin(input_data)
        destination = self._extract_destination(input_data)
        container_type = self._extract_container_type(input_data)
        
        if not origin:
            return {"error": "Origin code not provided"}
        
        if not destination:
            return {"error": "Destination code not provided"}
        
        if not container_type:
            return {"error": "Container type not provided"}
        
        # Normalize container type
        container_type = self._normalize_container_type(container_type)
        
        # Find matching rates using exact column names
        rate_results = self._find_matching_rates(origin, destination, container_type)
        
        return {
            "query": {
                "Origin_Code": origin,
                "Destination_Code": destination,
                "Container_Type": container_type
            },
            "rate_recommendation": rate_results,
            "data_source": self.data_file_path,
            "total_records_searched": len(self.rates_df)
        }

    def _extract_origin(self, input_data: Dict[str, Any]) -> Optional[str]:
        """Extract origin from various input formats"""
        possible_keys = ['Origin_Code', 'origin', 'origin_code', 'from', 'from_port']
        
        for key in possible_keys:
            if key in input_data and input_data[key]:
                return str(input_data[key]).strip().upper()
        
        return None

    def _extract_destination(self, input_data: Dict[str, Any]) -> Optional[str]:
        """Extract destination from various input formats"""
        possible_keys = ['Destination_Code', 'destination', 'destination_code', 'to', 'to_port']
        
        for key in possible_keys:
            if key in input_data and input_data[key]:
                return str(input_data[key]).strip().upper()
        
        return None

    def _extract_container_type(self, input_data: Dict[str, Any]) -> Optional[str]:
        """Extract container type from various input formats"""
        possible_keys = ['Container_Type', 'container_type', 'container', 'type']
        
        for key in possible_keys:
            if key in input_data and input_data[key]:
                return str(input_data[key]).strip().upper()
        
        return None

    def _find_matching_rates(self, origin: str, destination: str, container_type: str) -> Dict[str, Any]:
        """Find matching rates using exact column names"""
        
        # Filter data based on exact matches using correct column names
        exact_matches = self.rates_df[
            (self.rates_df['Origin_Code'] == origin) &
            (self.rates_df['Destination_Code'] == destination) &
            (self.rates_df['Container_Type'] == container_type)
        ]
        
        if not exact_matches.empty:
            return self._process_rate_matches(exact_matches, "exact_match")
        
        # Try with fallback container types
        fallback_container = self._get_fallback_container(container_type)
        if fallback_container != container_type:
            fallback_matches = self.rates_df[
                (self.rates_df['Origin_Code'] == origin) &
                (self.rates_df['Destination_Code'] == destination) &
                (self.rates_df['Container_Type'] == fallback_container)
            ]
            
            if not fallback_matches.empty:
                return self._process_rate_matches(fallback_matches, "fallback_container", 
                                                original_container=container_type, 
                                                fallback_container=fallback_container)
        
        # Try origin-destination matches with any container type
        route_matches = self.rates_df[
            (self.rates_df['Origin_Code'] == origin) &
            (self.rates_df['Destination_Code'] == destination)
        ]
        
        if not route_matches.empty:
            return self._process_rate_matches(route_matches, "route_only", 
                                            requested_container=container_type)
        
        # Try similar routes
        similar_routes = self._find_similar_routes(origin, destination, container_type)
        if similar_routes:
            return similar_routes
        
        # No matches found
        return {
            "match_type": "no_match",
            "message": f"No rates found for {origin} → {destination} with {container_type}",
            "suggestions": self._get_alternative_suggestions(origin, destination, container_type)
        }

    def _process_rate_matches(self, matches_df: pd.DataFrame, match_type: str, **kwargs) -> Dict[str, Any]:
        """Process and format rate matches using exact column names"""
        
        # Calculate statistics using Market_Average as primary rate
        market_avg = matches_df['Market_Average'].dropna()
        
        if market_avg.empty:
            return {
                "match_type": "no_valid_rates",
                "message": "No valid Market_Average rates found"
            }
        
        # Primary statistics from Market_Average
        min_rate = float(market_avg.min())
        max_rate = float(market_avg.max())
        avg_rate = float(market_avg.mean())
        median_rate = float(market_avg.median())
        
        # Additional rate statistics
        rate_statistics = {
            "market_average": {
                "min": min_rate,
                "max": max_rate,
                "average": round(avg_rate, 2),
                "median": round(median_rate, 2)
            }
        }
        
        # Add other market rates if available
        other_rate_columns = ['Market_Low', 'Market_High', 'Market_Midlow', 'Market_Midhigh']
        for col in other_rate_columns:
            if col in matches_df.columns:
                values = matches_df[col].dropna()
                if not values.empty:
                    rate_statistics[col.lower()] = {
                        "min": float(values.min()),
                        "max": float(values.max()),
                        "average": round(float(values.mean()), 2),
                        "median": round(float(values.median()), 2)
                    }
        
        # Price range recommendations
        if 'range_min' in matches_df.columns and 'range_max' in matches_df.columns:
            range_mins = matches_df['range_min'].dropna()
            range_maxs = matches_df['range_max'].dropna()
            
            if not range_mins.empty and not range_maxs.empty:
                rate_statistics['price_range_recommendation'] = {
                    "min_range": float(range_mins.min()),
                    "max_range": float(range_maxs.max()),
                    "average_min": round(float(range_mins.mean()), 2),
                    "average_max": round(float(range_maxs.mean()), 2)
                }
        
        # Collect metadata using exact column names
        metadata = {}
        metadata_columns = ['Contract_Length', 'Rate_Quality', 'Aggregation_Level', 
                           'Used_Origin', 'Used_Destination', 'THC_Methodology']
        
        for col in metadata_columns:
            if col in matches_df.columns:
                unique_values = matches_df[col].dropna().unique().tolist()
                if unique_values:
                    metadata[col] = unique_values
        
        # Build result
        result = {
            "match_type": match_type,
            "total_rates_found": len(matches_df),
            "rate_statistics": rate_statistics,
            "rate_range": f"${min_rate:,.0f} - ${max_rate:,.0f}",
            "recommended_rate": round(median_rate, 2),
            "confidence": self._calculate_confidence(match_type, len(matches_df)),
            "metadata": metadata
        }
        
        # Add context-specific information
        if match_type == "fallback_container":
            result["fallback_info"] = {
                "original_container": kwargs.get("original_container"),
                "fallback_container": kwargs.get("fallback_container"),
                "message": f"Using {kwargs.get('fallback_container')} rates as fallback for {kwargs.get('original_container')}"
            }
        elif match_type == "route_only":
            available_containers = matches_df['Container_Type'].unique().tolist()
            result["route_info"] = {
                "requested_container": kwargs.get("requested_container"),
                "available_containers": available_containers,
                "message": f"No {kwargs.get('requested_container')} rates found, showing all container types for this route"
            }
        
        return result

    def _get_fallback_container(self, container_type: str) -> str:
        """Get fallback container type for rate lookup"""
        fallback_mapping = {
            "40RE": "40DC",  # If 40RE doesn't exist, try 40DC
            "40RH": "40DC",  # If 40RH doesn't exist, try 40DC
            "20RE": "20DC",  # If 20RE doesn't exist, try 20DC
            "20TK": "20DC"   # If 20TK doesn't exist, try 20DC
        }
        return fallback_mapping.get(container_type, container_type)

    def _find_similar_routes(self, origin: str, destination: str, container_type: str) -> Optional[Dict[str, Any]]:
        """Find similar routes when exact match is not available"""
        
        # Try same origin, different destinations
        same_origin = self.rates_df[
            (self.rates_df['Origin_Code'] == origin) &
            (self.rates_df['Container_Type'] == container_type)
        ]
        
        # Try same destination, different origins
        same_destination = self.rates_df[
            (self.rates_df['Destination_Code'] == destination) &
            (self.rates_df['Container_Type'] == container_type)
        ]
        
        similar_routes = []
        
        if not same_origin.empty:
            destinations = same_origin['Destination_Code'].unique()[:5]
            for dest in destinations:
                route_rates = same_origin[same_origin['Destination_Code'] == dest]['Market_Average'].dropna()
                if not route_rates.empty:
                    # Get destination name if available
                    dest_name = same_origin[same_origin['Destination_Code'] == dest]['Used_Destination'].iloc[0] if 'Used_Destination' in same_origin.columns else dest
                    similar_routes.append({
                        "route": f"{origin} → {dest}",
                        "route_name": f"{origin} → {dest_name}",
                        "type": "same_origin",
                        "avg_rate": round(float(route_rates.mean()), 2),
                        "rate_count": len(route_rates)
                    })
        
        if not same_destination.empty:
            origins = same_destination['Origin_Code'].unique()[:5]
            for orig in origins:
                route_rates = same_destination[same_destination['Origin_Code'] == orig]['Market_Average'].dropna()
                if not route_rates.empty:
                    # Get origin name if available
                    orig_name = same_destination[same_destination['Origin_Code'] == orig]['Used_Origin'].iloc[0] if 'Used_Origin' in same_destination.columns else orig
                    similar_routes.append({
                        "route": f"{orig} → {destination}",
                        "route_name": f"{orig_name} → {destination}",
                        "type": "same_destination",
                        "avg_rate": round(float(route_rates.mean()), 2),
                        "rate_count": len(route_rates)
                    })
        
        if similar_routes:
            return {
                "match_type": "similar_routes",
                "message": f"No exact match found for {origin} → {destination}. Here are similar routes:",
                "similar_routes": similar_routes[:10],
                "suggestion": "Consider these similar routes for rate estimation"
            }
        
        return None

    def _get_alternative_suggestions(self, origin: str, destination: str, container_type: str) -> Dict[str, Any]:
        """Get alternative suggestions when no matches are found"""
        
        suggestions = {
            "available_origins": [],
            "available_destinations": [],
            "available_containers": [],
            "total_routes_in_database": len(self.rates_df)
        }
        
        # Get available origins
        unique_origins = self.rates_df['Origin_Code'].unique()[:10]
        suggestions["available_origins"] = unique_origins.tolist()
        
        # Get available destinations
        unique_destinations = self.rates_df['Destination_Code'].unique()[:10]
        suggestions["available_destinations"] = unique_destinations.tolist()
        
        # Get available container types
        unique_containers = self.rates_df['Container_Type'].unique()
        suggestions["available_containers"] = unique_containers.tolist()
        
        return suggestions

    def _calculate_confidence(self, match_type: str, rate_count: int) -> str:
        """Calculate confidence level based on match type and data availability"""
        
        confidence_mapping = {
            "exact_match": "high" if rate_count >= 3 else "medium" if rate_count >= 2 else "low",
            "fallback_container": "medium" if rate_count >= 3 else "low",
            "route_only": "low",
            "similar_routes": "very_low",
            "no_match": "none"
        }
        
        return confidence_mapping.get(match_type, "unknown")

    def get_rate_summary(self) -> Dict[str, Any]:
        """Get summary of available rate data"""
        if not self.data_loaded:
            return {"error": "Rate data not loaded"}
        
        summary = {
            "total_records": len(self.rates_df),
            "unique_origins": len(self.rates_df['Origin_Code'].unique()),
            "unique_destinations": len(self.rates_df['Destination_Code'].unique()),
            "unique_routes": len(self.rates_df.groupby(['Origin_Code', 'Destination_Code'])),
            "container_types": self.rates_df['Container_Type'].value_counts().to_dict(),
            "rate_statistics": {
                "min_rate": float(self.rates_df['Market_Average'].min()),
                "max_rate": float(self.rates_df['Market_Average'].max()),
                "average_rate": round(float(self.rates_df['Market_Average'].mean()), 2)
            },
            "data_file": self.data_file_path,
            "last_loaded": datetime.now().isoformat()
        }
        
        # Add metadata summary
        if 'Contract_Length' in self.rates_df.columns:
            summary["contract_lengths"] = self.rates_df['Contract_Length'].value_counts().to_dict()
        
        if 'Rate_Quality' in self.rates_df.columns:
            summary["rate_qualities"] = self.rates_df['Rate_Quality'].value_counts().to_dict()
        
        return summary

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_rate_recommendation_agent():
    """Test with actual data structure using correct column names"""
    print("=== Testing Rate Recommendation Agent ===")
    
    agent = RateRecommendationAgent()
    
    # Test context loading
    print("\n--- Testing Data Loading ---")
    context_loaded = agent.load_context()
    
    if not context_loaded:
        print("✗ Cannot proceed with tests - data loading failed")
        return
    
    # Show data summary
    print("\n--- Data Summary ---")
    summary = agent.get_rate_summary()
    if "error" not in summary:
        print(f"✓ Total records: {summary['total_records']}")
        print(f"✓ Unique origins: {summary['unique_origins']}")
        print(f"✓ Unique destinations: {summary['unique_destinations']}")
        print(f"✓ Unique routes: {summary['unique_routes']}")
        print(f"✓ Container types: {summary['container_types']}")
        print(f"✓ Rate range: ${summary['rate_statistics']['min_rate']:,.0f} - ${summary['rate_statistics']['max_rate']:,.0f}")
        
        if 'contract_lengths' in summary:
            print(f"✓ Contract lengths: {summary['contract_lengths']}")
        if 'rate_qualities' in summary:
            print(f"✓ Rate qualities: {summary['rate_qualities']}")
    
    # Test cases based on your actual data
    test_cases = [
        {
            "name": "UAE to Australia 20DC",
            "input": {"Origin_Code": "AEAUH", "Destination_Code": "AUBNE", "Container_Type": "20DC"},
            "description": "Abu Dhabi to Brisbane 20DC container"
        },
        {
            "name": "UAE to Australia Reefer",
            "input": {"origin": "AEAUH", "destination": "AUBNE", "container_type": "20RE"},
            "description": "Abu Dhabi to Brisbane 20RE reefer container"
        },
        {
            "name": "UAE to Australia 40HC",
            "input": {"Origin_Code": "AEAUH", "Destination_Code": "AUMEL", "Container_Type": "40HC"},
            "description": "Abu Dhabi to Melbourne 40HC high cube"
        },
        {
            "name": "UAE to Bangladesh",
            "input": {"origin": "AEAUH", "destination": "BDCGP", "container_type": "20DC"},
            "description": "Abu Dhabi to Chittagong 20DC"
        },
        {
            "name": "UAE to Belgium",
            "input": {"Origin_Code": "AEAUH", "Destination_Code": "BEANR", "Container_Type": "40DC"},
            "description": "Abu Dhabi to Antwerp 40DC"
        },
        {
            "name": "Tank Container",
            "input": {"origin": "AEAUH", "destination": "BDCGP", "container_type": "20TK"},
            "description": "Abu Dhabi to Chittagong 20TK tank container"
        },
        {
            "name": "Alternative Input Format",
            "input": {"from": "AEAUH", "to": "AUSYD", "type": "40RH"},
            "description": "Alternative input keys - Abu Dhabi to Sydney 40RH"
        },
        {
            "name": "Non-existent Route",
            "input": {"Origin_Code": "INVALID", "Destination_Code": "NOTFOUND", "Container_Type": "40DC"},
            "description": "Route that doesn't exist in database"
        }
    ]
    
    print(f"\n--- Running {len(test_cases)} Test Cases ---")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Description: {test_case['description']}")
        print(f"Input: {test_case['input']}")
        
        result = agent.run(test_case["input"])
        
        if result.get("status") == "success":
            query = result.get("query", {})
            recommendation = result.get("rate_recommendation", {})
            
            print(f"✓ Normalized Query:")
            print(f"  Origin_Code: {query.get('Origin_Code')}")
            print(f"  Destination_Code: {query.get('Destination_Code')}")
            print(f"  Container_Type: {query.get('Container_Type')}")
            
            match_type = recommendation.get("match_type")
            print(f"✓ Match Type: {match_type}")
            
            if match_type == "exact_match":
                print(f"✓ Rate Range: {recommendation.get('rate_range')}")
                print(f"✓ Recommended Rate: ${recommendation.get('recommended_rate'):,.2f}")
                print(f"✓ Total Rates Found: {recommendation.get('total_rates_found')}")
                print(f"✓ Confidence: {recommendation.get('confidence')}")
                
                # Show rate statistics
                rate_stats = recommendation.get("rate_statistics", {})
                if 'market_average' in rate_stats:
                    avg_stats = rate_stats['market_average']
                    print(f"✓ Market Average: ${avg_stats['min']:,.0f} - ${avg_stats['max']:,.0f} (avg: ${avg_stats['average']:,.2f})")
                
                # Show metadata
                metadata = recommendation.get("metadata", {})
                if 'Used_Origin' in metadata and 'Used_Destination' in metadata:
                    print(f"✓ Route Names: {metadata['Used_Origin'][0]} → {metadata['Used_Destination'][0]}")
                if 'Contract_Length' in metadata:
                    print(f"✓ Contract Length: {metadata['Contract_Length']}")
                if 'Rate_Quality' in metadata:
                    print(f"✓ Rate Quality: {metadata['Rate_Quality']}")
                if 'THC_Methodology' in metadata:
                    print(f"✓ THC Methodology: {metadata['THC_Methodology']}")
                
            elif match_type == "fallback_container":
                fallback_info = recommendation.get("fallback_info", {})
                print(f"✓ {fallback_info.get('message')}")
                print(f"✓ Rate Range: {recommendation.get('rate_range')}")
                print(f"✓ Recommended Rate: ${recommendation.get('recommended_rate'):,.2f}")
                
            elif match_type == "route_only":
                route_info = recommendation.get("route_info", {})
                print(f"✓ {route_info.get('message')}")
                print(f"✓ Available Containers: {route_info.get('available_containers')}")
                print(f"✓ Rate Range: {recommendation.get('rate_range')}")
                
            elif match_type == "similar_routes":
                print(f"✓ {recommendation.get('message')}")
                similar_routes = recommendation.get("similar_routes", [])
                for route in similar_routes[:3]:  # Show first 3
                    print(f"  - {route['route_name']}: ${route['avg_rate']:,.2f} ({route['rate_count']} rates)")
                
            elif match_type == "no_match":
                print(f"✓ {recommendation.get('message')}")
                suggestions = recommendation.get("suggestions", {})
                if 'available_origins' in suggestions:
                    print(f"✓ Sample Origins: {suggestions['available_origins'][:5]}")
                if 'available_destinations' in suggestions:
                    print(f"✓ Sample Destinations: {suggestions['available_destinations'][:5]}")
                if 'available_containers' in suggestions:
                    print(f"✓ Available Containers: {suggestions['available_containers']}")
        
        else:
            print(f"✗ Error: {result.get('error')}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Testing Edge Cases ===")
    
    agent = RateRecommendationAgent()
    
    if not agent.load_context():
        print("✗ Cannot run edge case tests - data loading failed")
        return
    
    edge_cases = [
        {
            "name": "Empty Input",
            "input": {},
            "expected_error": "Origin code not provided"
        },
        {
            "name": "Missing Origin",
            "input": {"Destination_Code": "AUBNE", "Container_Type": "20DC"},
            "expected_error": "Origin code not provided"
        },
        {
            "name": "Missing Destination",
            "input": {"Origin_Code": "AEAUH", "Container_Type": "20DC"},
            "expected_error": "Destination code not provided"
        },
        {
            "name": "Missing Container Type",
            "input": {"Origin_Code": "AEAUH", "Destination_Code": "AUBNE"},
            "expected_error": "Container type not provided"
        },
        {
            "name": "Invalid Container Type",
            "input": {"Origin_Code": "AEAUH", "Destination_Code": "AUBNE", "Container_Type": "INVALID"},
            "expected_error": None  # Should handle gracefully
        },
        {
            "name": "Case Sensitivity Test",
            "input": {"origin": "aeauh", "destination": "aubne", "container_type": "20dc"},
            "expected_error": None  # Should normalize to uppercase
        },
        {
            "name": "Whitespace Test",
            "input": {"Origin_Code": " AEAUH ", "Destination_Code": " AUBNE ", "Container_Type": " 20DC "},
            "expected_error": None  # Should trim whitespace
        }
    ]
    
    print(f"Running {len(edge_cases)} edge case tests...")
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n--- Edge Case {i}: {test_case['name']} ---")
        print(f"Input: {test_case['input']}")
        
        result = agent.run(test_case["input"])
        
        if result.get("status") == "error":
            print(f"✓ Error handled: {result.get('error')}")
            if test_case["expected_error"] and test_case["expected_error"] in result.get("error", ""):
                print("✅ Expected error message found")
            else:
                print("⚠️ Unexpected error message")
        else:
            print(f"✓ Result: {result.get('rate_recommendation', {}).get('match_type', 'unknown')}")
            if test_case["expected_error"]:
                print("⚠️ Expected error but got success")

def test_data_validation():
    """Test data validation and cleaning"""
    print("\n=== Testing Data Validation ===")
    
    agent = RateRecommendationAgent()
    
    if not agent.load_context():
        print("✗ Cannot run validation tests - data loading failed")
        return
    
    # Test container type normalization
    print("--- Testing Container Type Normalization ---")
    test_containers = ["20DC", "20re", " 40HC ", "40rf", "20TK", "invalid"]
    
    for container in test_containers:
        normalized = agent._normalize_container_type(container)
        print(f"'{container}' → '{normalized}'")
    
    # Test price range parsing
    print("\n--- Testing Price Range Parsing ---")
    test_ranges = ["[919,1249]", "[1747,2293]", "[invalid]", "", None]
    
    for price_range in test_ranges:
        min_val, max_val = agent._parse_price_range(price_range)
        print(f"'{price_range}' → min: {min_val}, max: {max_val}")

def test_rate_analysis():
    """Test rate analysis and statistics"""
    print("\n=== Testing Rate Analysis ===")
    
    agent = RateRecommendationAgent()
    
    if not agent.load_context():
        print("✗ Cannot run analysis tests - data loading failed")
        return
    
    print("--- Rate Data Analysis ---")
    
    # Most common routes
    route_counts = agent.rates_df.groupby(['Origin_Code', 'Destination_Code']).size().sort_values(ascending=False)
    print(f"✓ Most common routes:")
    for (origin, dest), count in route_counts.head(5).items():
        # Get route names if available
        route_sample = agent.rates_df[
            (agent.rates_df['Origin_Code'] == origin) & 
            (agent.rates_df['Destination_Code'] == dest)
        ].iloc[0]
        
        origin_name = route_sample.get('Used_Origin', origin) if 'Used_Origin' in agent.rates_df.columns else origin
        dest_name = route_sample.get('Used_Destination', dest) if 'Used_Destination' in agent.rates_df.columns else dest
        
        print(f"  {origin} → {dest} ({origin_name} → {dest_name}): {count} rates")
    
    # Container type distribution
    container_dist = agent.rates_df['Container_Type'].value_counts()
    print(f"\n✓ Container type distribution:")
    for container, count in container_dist.items():
        print(f"  {container}: {count} rates")
    
    # Rate statistics by container type
    print(f"\n✓ Average rates by container type:")
    avg_rates = agent.rates_df.groupby('Container_Type')['Market_Average'].mean().sort_values(ascending=False)
    for container, avg_rate in avg_rates.items():
        print(f"  {container}: ${avg_rate:,.2f}")
    
    # Contract length analysis if available
    if 'Contract_Length' in agent.rates_df.columns:
        print(f"\n✓ Contract length distribution:")
        contract_dist = agent.rates_df['Contract_Length'].value_counts()
        for contract, count in contract_dist.items():
            print(f"  {contract}: {count} rates")
    
    # Rate quality analysis if available
    if 'Rate_Quality' in agent.rates_df.columns:
        print(f"\n✓ Rate quality distribution:")
        quality_dist = agent.rates_df['Rate_Quality'].value_counts()
        for quality, count in quality_dist.items():
            print(f"  {quality}: {count} rates")

def test_performance():
    """Test performance with multiple requests"""
    print("\n=== Testing Performance ===")
    
    agent = RateRecommendationAgent()
    
    if not agent.load_context():
        print("✗ Cannot run performance tests - data loading failed")
        return
    
    import time
    
    # Get some actual routes from the data for performance testing
    sample_routes = agent.rates_df.groupby(['Origin_Code', 'Destination_Code', 'Container_Type']).first().reset_index()
    
    # Select first 10 routes for performance testing
    test_requests = []
    for _, row in sample_routes.head(10).iterrows():
        test_requests.append({
            "Origin_Code": row['Origin_Code'],
            "Destination_Code": row['Destination_Code'],
            "Container_Type": row['Container_Type']
        })
    
    print(f"Running {len(test_requests)} rate requests...")
    
    start_time = time.time()
    
    results = []
    for i, request in enumerate(test_requests, 1):
        request_start = time.time()
        result = agent.run(request)
        request_end = time.time()
        
        processing_time = (request_end - request_start) * 1000  # Convert to ms
        results.append({
            "request": i,
            "processing_time_ms": processing_time,
            "success": result.get("status") == "success",
            "match_type": result.get("rate_recommendation", {}).get("match_type", "error"),
            "route": f"{request['Origin_Code']} → {request['Destination_Code']} ({request['Container_Type']})"
        })
    
    end_time = time.time()
    total_time = (end_time - start_time) * 1000
    
    print(f"\n✓ Performance Results:")
    print(f"  Total time: {total_time:.2f}ms")
    print(f"  Average per request: {total_time/len(test_requests):.2f}ms")
    print(f"  Successful requests: {sum(1 for r in results if r['success'])}/{len(results)}")
    
    for result in results:
        status = "✓" if result["success"] else "✗"
        print(f"  {status} {result['route']}: {result['processing_time_ms']:.2f}ms ({result['match_type']})")

def test_batch_processing():
    """Test batch processing of multiple rate requests"""
    print("\n=== Testing Batch Processing ===")
    
    agent = RateRecommendationAgent()
    
    if not agent.load_context():
        print("✗ Cannot run batch tests - data loading failed")
        return
    
    # Create batch requests using actual data
    batch_requests = [
        {"Origin_Code": "AEAUH", "Destination_Code": "AUBNE", "Container_Type": "20DC"},
        {"Origin_Code": "AEAUH", "Destination_Code": "AUBNE", "Container_Type": "20RE"},
        {"Origin_Code": "AEAUH", "Destination_Code": "AUMEL", "Container_Type": "40HC"},
        {"Origin_Code": "AEAUH", "Destination_Code": "BDCGP", "Container_Type": "20TK"},
        {"Origin_Code": "AEAUH", "Destination_Code": "BEANR", "Container_Type": "40DC"},
        {"Origin_Code": "INVALID", "Destination_Code": "NOTFOUND", "Container_Type": "40DC"}  # Should fail
    ]
    
    print(f"Processing batch of {len(batch_requests)} requests...")
    
    batch_results = []
    successful = 0
    failed = 0
    
    for i, request in enumerate(batch_requests, 1):
        print(f"\n--- Batch Request {i} ---")
        print(f"Request: {request}")
        
        result = agent.run(request)
        
        if result.get("status") == "success":
            successful += 1
            recommendation = result.get("rate_recommendation", {})
            match_type = recommendation.get("match_type")
            
            print(f"✓ Success: {match_type}")
            
            if match_type == "exact_match":
                recommended_rate = recommendation.get("recommended_rate")
                rate_range = recommendation.get("rate_range")
                print(f"  Recommended rate: ${recommended_rate:,.2f}")
                print(f"  Rate range: {rate_range}")
            elif match_type == "fallback_container":
                fallback_info = recommendation.get("fallback_info", {})
                print(f"  {fallback_info.get('message')}")
            elif match_type == "similar_routes":
                similar_count = len(recommendation.get("similar_routes", []))
                print(f"  Found {similar_count} similar routes")
            elif match_type == "no_match":
                print(f"  {recommendation.get('message')}")
        else:
            failed += 1
            print(f"✗ Failed: {result.get('error')}")
        
        batch_results.append(result)
    
    print(f"\n--- Batch Summary ---")
    print(f"✓ Successful: {successful}/{len(batch_requests)}")
    print(f"✗ Failed: {failed}/{len(batch_requests)}")
    print(f"Success rate: {successful/len(batch_requests)*100:.1f}%")

def test_comprehensive_scenarios():
    """Test comprehensive real-world scenarios"""
    print("\n=== Testing Comprehensive Scenarios ===")
    
    agent = RateRecommendationAgent()
    
    if not agent.load_context():
        print("✗ Cannot run comprehensive tests - data loading failed")
        return
    
    # Test different input formats
    input_format_tests = [
        {
            "name": "Standard Format",
            "input": {"Origin_Code": "AEAUH", "Destination_Code": "AUBNE", "Container_Type": "20DC"}
        },
        {
            "name": "Lowercase Format",
            "input": {"origin_code": "aeauh", "destination_code": "aubne", "container_type": "20dc"}
        },
        {
            "name": "Alternative Keys",
            "input": {"origin": "AEAUH", "destination": "AUBNE", "container": "20DC"}
        },
        {
            "name": "From/To Format",
            "input": {"from": "AEAUH", "to": "AUBNE", "type": "20DC"}
        }
    ]
    

    print("--- Testing Input Format Flexibility ---")
    for test in input_format_tests:
        print(f"\n{test['name']}: {test['input']}")
        result = agent.run(test['input'])
        
        if result.get("status") == "success":
            query = result.get("query", {})
            print(f"✓ Normalized to: {query}")
            match_type = result.get("rate_recommendation", {}).get("match_type")
            print(f"✓ Match type: {match_type}")
        else:
            print(f"✗ Error: {result.get('error')}")

# =====================================================
#                 🔁 Main Test Runner
# =====================================================

def run_all_tests():
    """Run all test suites"""
    print("🚀 Starting Comprehensive Rate Recommendation Agent Tests")
    print("=" * 60)
    
    try:
        # Basic functionality tests
        test_rate_recommendation_agent()
        
        # Edge case tests
        test_edge_cases()
        
        # Data validation tests
        test_data_validation()
        
        # Rate analysis tests
        test_rate_analysis()
        
        # Performance tests
        test_performance()
        
        # Batch processing tests
        test_batch_processing()
        
        # Comprehensive scenario tests
        test_comprehensive_scenarios()
        
        print("\n" + "=" * 60)
        print("🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

def create_sample_csv():
    """Create a sample CSV file for testing if none exists"""
    sample_data = """Origin_Code,Destination_Code,Container_Type,Contract_Length,Contracted_WithinDay,Market_Average,Market_Low,Market_High,Market_Midlow,Market_Midhigh,Rate_Quality,Aggregation_Level,Used_Origin,Used_Destination,THC_Methodology,price_range_recommendation
AEAUH,AUBNE,20DC,short,all,1109,972,1210,1081,1136,10,+0,Abu Dhabi,Brisbane,none,[919,1249]
AEAUH,AUBNE,20RE,short,all,2066,2055,2102,2055,2085,20,+2,UAE Main,Australia Main,none,[1747,2293]
AEAUH,AUBNE,40DC,short,all,1761,1500,2131,1514,2086,10,+0,Abu Dhabi,Brisbane,none,[1287,2294]
AEAUH,AUBNE,40HC,short,all,1761,1500,2131,1514,2086,10,+0,Abu Dhabi,Brisbane,none,[1287,2294]
AEAUH,AUBNE,40RH,short,all,3418,3386,3476,3410,3440,20,+2,UAE Main,Australia Main,none,[2899,3784]
AEAUH,AUMEL,20DC,short,all,1109,972,1210,1081,1136,10,+0,Abu Dhabi,Melbourne,none,[919,1249]
AEAUH,AUMEL,40HC,short,all,1761,1500,2131,1514,2086,10,+0,Abu Dhabi,Melbourne,none,[1287,2294]
AEAUH,AUSYD,20DC,short,all,1109,972,1210,1081,1136,10,+0,Abu Dhabi,Sydney,none,[919,1249]
AEAUH,AUSYD,40DC,short,all,1761,1500,2131,1514,2086,10,+0,Abu Dhabi,Sydney,none,[1287,2294]
AEAUH,BDCGP,20DC,short,all,1042,362,1433,963,1283,10,+3,Persian Gulf / Gulf of Oman,Chittagong,none,[819,1411]
AEAUH,BDCGP,20TK,short,all,2379,728,5145,934,3921,Less than 10,3,Persian Gulf / Gulf of Oman,Chittagong,none,[794,4313]
AEAUH,BEANR,20DC,short,all,1355,1070,1764,1296,1365,10,+0,Abu Dhabi,Antwerpen,none,[1102,1501]
AEAUH,BEANR,40DC,short,all,1550,1040,2287,1449,1643,10,+0,Abu Dhabi,Antwerpen,none,[1232,1807]
AEAUH,BEANR,40HC,short,all,1550,1040,2287,1449,1643,10,+0,Abu Dhabi,Antwerpen,none,[1232,1807]"""
    
    csv_filename = "rate_recommendation.csv"
    
    if not os.path.exists(csv_filename):
        print(f"Creating sample CSV file: {csv_filename}")
        with open(csv_filename, 'w') as f:
            f.write(sample_data)
        print(f"✓ Sample CSV created with {len(sample_data.split(chr(10)))-1} records")
    else:
        print(f"✓ CSV file already exists: {csv_filename}")

def quick_test():
    """Quick test with a few key scenarios"""
    print("=== Quick Rate Recommendation Test ===")
    
    agent = RateRecommendationAgent()
    
    if not agent.load_context():
        print("✗ Data loading failed")
        return
    
    # Quick test cases
    quick_tests = [
        {"Origin_Code": "AEAUH", "Destination_Code": "AUBNE", "Container_Type": "20DC"},
        {"origin": "AEAUH", "destination": "BDCGP", "container_type": "20TK"},
        {"Origin_Code": "INVALID", "Destination_Code": "NOTFOUND", "Container_Type": "40DC"}
    ]
    
    for i, test in enumerate(quick_tests, 1):
        print(f"\n--- Quick Test {i} ---")
        print(f"Input: {test}")
        
        result = agent.run(test)
        
        if result.get("status") == "success":
            recommendation = result.get("rate_recommendation", {})
            match_type = recommendation.get("match_type")
            
            print(f"✓ Match: {match_type}")
            
            if match_type == "exact_match":
                print(f"✓ Rate: ${recommendation.get('recommended_rate'):,.2f}")
                print(f"✓ Range: {recommendation.get('rate_range')}")
            elif match_type == "no_match":
                print(f"✓ {recommendation.get('message')}")
        else:
            print(f"✗ Error: {result.get('error')}")

if __name__ == "__main__":
    import sys
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            create_sample_csv()
            quick_test()
        elif sys.argv[1] == "create-sample":
            create_sample_csv()
        elif sys.argv[1] == "summary":
            agent = RateRecommendationAgent()
            if agent.load_context():
                summary = agent.get_rate_summary()
                print("=== Rate Data Summary ===")
                for key, value in summary.items():
                    if key != "data_file":
                        print(f"{key}: {value}")
        else:
            print("Usage: python rate_recommendation_agent.py [quick|create-sample|summary]")
    else:
        # Run full test suite
        create_sample_csv()
        run_all_tests()
