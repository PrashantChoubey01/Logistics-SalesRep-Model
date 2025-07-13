"""Forwarder Assignment Agent for matching shipments to forwarders based on country presence"""

import os
import sys
from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from agents.base_agent import BaseAgent
except ImportError:
    from base_agent import BaseAgent

class ForwarderAssignmentAgent(BaseAgent):
    """Agent for assigning forwarders based on POL/POD country presence"""

    def __init__(self):
        super().__init__("forwarder_assignment_agent")
        
        # Forwarder database
        self.forwarders_db = None
        self.country_mapping = {}
        self.forwarder_details = {}
        
        # Load forwarder data
        self._load_forwarder_database()

    def _load_forwarder_database(self):
        """Load forwarder database from CSV file"""
        try:
            # Try multiple possible file locations
            possible_paths = [
                "Forwarders_with_Operators_and_Emails.csv",
                "./Forwarders_with_Operators_and_Emails.csv",
                "../Forwarders_with_Operators_and_Emails.csv",
                "/Users/prashant.choubey/Documents/VSWorkspace/AI-Sales-Bot-V2/Forwarders_with_Operators_and_Emails.csv"
            ]
            
            csv_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    csv_path = path
                    break
            
            if not csv_path:
                self.logger.error("Forwarders CSV file not found. Creating sample data.")
                self._create_sample_forwarder_data()
                return
            
            # Read CSV file
            self.forwarders_db = pd.read_csv(csv_path)
            
            self.logger.info(f"Loaded {len(self.forwarders_db)} forwarder-country records from {csv_path}")
            print(f"✓ Loaded forwarder database: {len(self.forwarders_db)} records")
            
            # Show column names for debugging
            print(f"✓ CSV Columns: {list(self.forwarders_db.columns)}")
            
            # Process country data with the actual CSV structure
            self._process_country_data_from_rows()
            
        except Exception as e:
            self.logger.error(f"Failed to load forwarder database: {e}")
            print(f"✗ Error loading CSV: {e}")
            self._create_sample_forwarder_data()

    def _process_country_data_from_rows(self):
        """Process country data from individual rows (each row = forwarder-country pair)"""
        
        # Expected columns: forwarder_name, country, operator, email
        required_columns = ['forwarder_name', 'country']
        
        # Check if required columns exist
        missing_columns = [col for col in required_columns if col not in self.forwarders_db.columns]
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            print(f"✗ Missing required columns: {missing_columns}")
            return
        
        print(f"✓ Processing CSV with structure: forwarder_name, country, operator, email")
        
        # Process each row
        for idx, row in self.forwarders_db.iterrows():
            forwarder_name = str(row['forwarder_name']).strip()
            country = str(row['country']).strip()
            
            # Skip invalid rows
            if pd.isna(forwarder_name) or pd.isna(country) or not forwarder_name or not country:
                continue
            
            # Create country mapping
            if country not in self.country_mapping:
                self.country_mapping[country] = []
            
            # Check if forwarder already exists for this country
            existing_forwarder = next((f for f in self.country_mapping[country] 
                                     if f['forwarder_name'] == forwarder_name), None)
            
            if not existing_forwarder:
                self.country_mapping[country].append({
                    'forwarder_name': forwarder_name,
                    'country': country,
                    'operator': row.get('operator', ''),
                    'email': row.get('email', ''),
                    'row_index': idx
                })
            
            # Store forwarder details
            if forwarder_name not in self.forwarder_details:
                self.forwarder_details[forwarder_name] = {
                    'countries': [],
                    'operators': [],
                    'emails': []
                }
            
            # Add country if not already present
            if country not in self.forwarder_details[forwarder_name]['countries']:
                self.forwarder_details[forwarder_name]['countries'].append(country)
            
            # Add operator if not already present
            operator = row.get('operator', '')
            if operator and operator not in self.forwarder_details[forwarder_name]['operators']:
                self.forwarder_details[forwarder_name]['operators'].append(operator)
            
            # Add email if not already present
            email = row.get('email', '')
            if email and email not in self.forwarder_details[forwarder_name]['emails']:
                self.forwarder_details[forwarder_name]['emails'].append(email)
        
        print(f"✓ Processed country mapping: {len(self.country_mapping)} countries")
        print(f"✓ Processed forwarder details: {len(self.forwarder_details)} unique forwarders")
        print(f"✓ Sample countries: {list(self.country_mapping.keys())[:10]}")
        
        # Show some statistics
        country_counts = {country: len(forwarders) for country, forwarders in self.country_mapping.items()}
        top_countries = sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"✓ Top countries by forwarder count: {top_countries}")

    def _create_sample_forwarder_data(self):
        """Create sample forwarder data for testing"""
        sample_data = {
            'forwarder_name': [
                'Global Logistics Asia', 'Global Logistics Asia', 'Global Logistics Asia',
                'Euro Freight Solutions', 'Euro Freight Solutions', 'Euro Freight Solutions',
                'Americas Shipping Co', 'Americas Shipping Co', 'Americas Shipping Co'
            ],
            'country': [
                'China', 'Singapore', 'Malaysia',
                'Germany', 'Netherlands', 'Belgium', 
                'USA', 'Canada', 'Mexico'
            ],
            'operator': [
                'COSCO', 'ONE', 'Evergreen',
                'Hapag-Lloyd', 'MSC', 'CMA CGM',
                'Maersk', 'MSC', 'COSCO'
            ],
            'email': [
                'ops@globallogisticsasia.com', 'ops@globallogisticsasia.com', 'ops@globallogisticsasia.com',
                'booking@eurofreight.com', 'booking@eurofreight.com', 'booking@eurofreight.com',
                'quotes@americasshipping.com', 'quotes@americasshipping.com', 'quotes@americasshipping.com'
            ]
        }
        
        self.forwarders_db = pd.DataFrame(sample_data)
        self._process_country_data_from_rows()
        
        self.logger.info("Created sample forwarder database")
        print("✓ Created sample forwarder database")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign forwarders based on POL/POD country presence"""
        
        # Extract shipment data
        validated_data = input_data.get("validated_data", {})
        
        if not validated_data:
            return {"error": "No validated shipment data provided"}
        
        # Extract country information
        origin_country = validated_data.get("origin_country")
        destination_country = validated_data.get("destination_country")
        
        if not origin_country or not destination_country:
            return {"error": "Origin and destination countries are required"}
        
        print(f"DEBUG: Looking for forwarders for {origin_country} → {destination_country}")
        
        # Find matching forwarders
        matching_forwarders = self._find_matching_forwarders(origin_country, destination_country)
        
        if not matching_forwarders:
            return {
                "assigned_forwarders": [],
                "assignment_status": "no_match",
                "reason": f"No forwarders found for {origin_country} to {destination_country}",
                "available_countries": list(self.country_mapping.keys()),
                "suggestions": self._get_country_suggestions(origin_country, destination_country)
            }
        
        return {
            "assigned_forwarders": matching_forwarders,
            "assignment_status": "success",
            "total_matches": len(matching_forwarders),
            "assignment_criteria": {
                "origin_country": origin_country,
                "destination_country": destination_country
            },
            "assignment_summary": self._generate_assignment_summary(matching_forwarders)
        }

    def _find_matching_forwarders(self, origin_country: str, destination_country: str) -> List[Dict[str, Any]]:
        """Find forwarders that have presence in origin or destination country"""
        
        matching_forwarders = []
        processed_forwarders = set()
        
        # Get forwarders present in origin country
        origin_forwarders = self.country_mapping.get(origin_country, [])
        print(f"DEBUG: Found {len(origin_forwarders)} forwarders in origin country ({origin_country})")
        
        # Get forwarders present in destination country  
        destination_forwarders = self.country_mapping.get(destination_country, [])
        print(f"DEBUG: Found {len(destination_forwarders)} forwarders in destination country ({destination_country})")
        
        # Process origin country forwarders
        for forwarder in origin_forwarders:
            forwarder_name = forwarder['forwarder_name']
            if forwarder_name not in processed_forwarders:
                
                # Check if this forwarder also serves destination
                serves_destination = any(f['forwarder_name'] == forwarder_name for f in destination_forwarders)
                
                # Get full forwarder details
                forwarder_details = self.forwarder_details.get(forwarder_name, {})
                
                matching_forwarders.append({
                    'forwarder_name': forwarder_name,
                    'country_presence': 'origin' if not serves_destination else 'both',
                    'origin_coverage': True,
                    'destination_coverage': serves_destination,
                    'match_strength': 'excellent' if serves_destination else 'good',
                    'countries_served': forwarder_details.get('countries', []),
                    'operators': forwarder_details.get('operators', []),
                    'contact_emails': forwarder_details.get('emails', []),
                    'primary_email': forwarder_details.get('emails', [''])[0] if forwarder_details.get('emails') else '',
                    'forwarder_details': forwarder_details
                })
                
                processed_forwarders.add(forwarder_name)
        
        # Process destination country forwarders (not already processed)
        for forwarder in destination_forwarders:
            forwarder_name = forwarder['forwarder_name']
            if forwarder_name not in processed_forwarders:
                
                # Get full forwarder details
                forwarder_details = self.forwarder_details.get(forwarder_name, {})
                
                matching_forwarders.append({
                    'forwarder_name': forwarder_name,
                    'country_presence': 'destination',
                    'origin_coverage': False,
                    'destination_coverage': True,
                    'match_strength': 'good',
                    'countries_served': forwarder_details.get('countries', []),
                    'operators': forwarder_details.get('operators', []),
                    'contact_emails': forwarder_details.get('emails', []),
                    'primary_email': forwarder_details.get('emails', [''])[0] if forwarder_details.get('emails') else '',
                    'forwarder_details': forwarder_details
                })
                
                processed_forwarders.add(forwarder_name)
        
        # Sort by match strength (both countries first)
        matching_forwarders.sort(key=lambda x: (
            x['match_strength'] == 'excellent',  # Both countries first
            len(x['countries_served']),          # More countries second
            x['forwarder_name']                  # Alphabetical third
        ), reverse=True)
        
        return matching_forwarders

    def _get_country_suggestions(self, origin_country: str, destination_country: str) -> List[str]:
        """Get suggestions for similar countries"""
        suggestions = []
        
        # Find countries with similar names
        all_countries = list(self.country_mapping.keys())
        
        for country in all_countries:
            if (origin_country.lower() in country.lower() or 
                destination_country.lower() in country.lower() or
                country.lower() in origin_country.lower() or
                country.lower() in destination_country.lower()):
                suggestions.append(country)
        
        return suggestions[:5]  # Top 5 suggestions

    def _generate_assignment_summary(self, matching_forwarders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of forwarder assignments"""
        
        excellent_matches = [f for f in matching_forwarders if f['match_strength'] == 'excellent']
        good_matches = [f for f in matching_forwarders if f['match_strength'] == 'good']
        
        return {
            "total_forwarders": len(matching_forwarders),
            "excellent_matches": len(excellent_matches),
            "good_matches": len(good_matches),
            "top_recommendation": matching_forwarders[0]['forwarder_name'] if matching_forwarders else None,
            "coverage_analysis": {
                "both_countries": len(excellent_matches),
                "origin_only": len([f for f in matching_forwarders if f['country_presence'] == 'origin']),
                "destination_only": len([f for f in matching_forwarders if f['country_presence'] == 'destination'])
            }
        }

    def get_forwarder_summary(self) -> Dict[str, Any]:
        """Get summary of loaded forwarder database"""
        if self.forwarders_db is None:
            return {"error": "No forwarder database loaded"}
        
        return {
            "total_records": len(self.forwarders_db),
            "unique_forwarders": len(self.forwarder_details),
            "countries_covered": len(self.country_mapping),
            "sample_countries": list(self.country_mapping.keys())[:10],
            "sample_forwarders": list(self.forwarder_details.keys())[:5]
        }

    def get_country_forwarders(self, country: str) -> List[Dict[str, Any]]:
        """Get all forwarders for a specific country"""
        return self.country_mapping.get(country, [])

    def get_forwarder_countries(self, forwarder_name: str) -> List[str]:
        """Get all countries served by a specific forwarder"""
        return self.forwarder_details.get(forwarder_name, {}).get('countries', [])

# =====================================================
#                 🔁 Test Harness
# =====================================================

def test_forwarder_assignment_agent():
    print("=== Testing Forwarder Assignment Agent ===")
    
    agent = ForwarderAssignmentAgent()
    
    # Test cases with real countries from your CSV
    test_cases = [
        {
            "name": "Brazil to USA",
            "validated_data": {
                "origin_country": "Brazil",
                "destination_country": "USA",
                "shipment_type": "FCL"
            }
        },
        {
            "name": "China to Germany", 
            "validated_data": {
                "origin_country": "China",
                "destination_country": "Germany",
                "shipment_type": "LCL"
            }
        },
        {
            "name": "India to UK",
            "validated_data": {
                "origin_country": "India",
                "destination_country": "UK",
                "shipment_type": "FCL"
            }
        },
        {
            "name": "Singapore to Netherlands",
            "validated_data": {
                "origin_country": "Singapore",
                "destination_country": "Netherlands",
                "shipment_type": "FCL"
            }
        },
        {
            "name": "Invalid Countries",
            "validated_data": {
                "origin_country": "Unknown Country",
                "destination_country": "Another Unknown",
                "shipment_type": "FCL"
            }
        }
    ]
    
    # Load context
    context_loaded = agent.load_context()
    print(f"Context loaded: {context_loaded}")
    
    # Show database summary
    summary = agent.get_forwarder_summary()
    print(f"\nForwarder Database Summary:")
    print(f"✓ Total Records: {summary.get('total_records')}")
    print(f"✓ Unique Forwarders: {summary.get('unique_forwarders')}")
    print(f"✓ Countries Covered: {summary.get('countries_covered')}")
    print(f"✓ Sample Countries: {summary.get('sample_countries')}")
    print(f"✓ Sample Forwarders: {summary.get('sample_forwarders')}")
    
    # Test each case
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        
        result = agent.run(test_case)
        
        if result.get("status") == "success":
            assignment_status = result.get("assignment_status")
            print(f"✓ Assignment Status: {assignment_status}")
            
            if assignment_status == "success":
                forwarders = result.get("assigned_forwarders", [])
                print(f"✓ Found {len(forwarders)} matching forwarders:")
                
                for j, forwarder in enumerate(forwarders[:5], 1):  # Show top 5
                    print(f"  {j}. {forwarder['forwarder_name']}")
                    print(f"     - Coverage: {forwarder['country_presence']}")
                    print(f"     - Match: {forwarder['match_strength']}")
                    print(f"     - Countries: {len(forwarder['countries_served'])} ({', '.join(forwarder['countries_served'][:3])}{'...' if len(forwarder['countries_served']) > 3 else ''})")
                    print(f"     - Email: {forwarder['primary_email']}")
                    print(f"     - Operators: {', '.join(forwarder['operators'][:2])}{'...' if len(forwarder['operators']) > 2 else ''}")
                
                # Show summary
                summary = result.get("assignment_summary", {})
                print(f"✓ Summary: {summary.get('excellent_matches')} excellent, {summary.get('good_matches')} good matches")
                print(f"✓ Top Recommendation: {summary.get('top_recommendation')}")
                
            else:
                print(f"✗ No matches found: {result.get('reason')}")
                suggestions = result.get('suggestions', [])
                if suggestions:
                    print(f"💡 Similar countries available: {suggestions}")
        else:
            print(f"✗ Error: {result.get('error')}")

def test_country_coverage():
    """Test country coverage analysis"""
    print("\n=== Testing Country Coverage ===")
    
    agent = ForwarderAssignmentAgent()
    agent.load_context()
    
    # Test specific countries that should be in your CSV
    test_countries = ["Brazil", "China", "USA", "Germany", "Singapore", "UK", "Japan", "India", "Netherlands", "France"]
    
    print("Country Coverage Analysis:")
    for country in test_countries:
        forwarders = agent.get_country_forwarders(country)
        print(f"  {country}: {len(forwarders)} forwarders")
        
        if forwarders:
            forwarder_names = list(set([f['forwarder_name'] for f in forwarders[:3]]))
            print(f"    └─ {', '.join(forwarder_names)}")

def test_forwarder_details():
    """Test forwarder details lookup"""
    print("\n=== Testing Forwarder Details ===")
    
    agent = ForwarderAssignmentAgent()
    agent.load_context()
    
    # Get sample forwarders
    sample_forwarders = list(agent.forwarder_details.keys())[:5]
    
    print("Forwarder Details Analysis:")
    for forwarder_name in sample_forwarders:
        countries = agent.get_forwarder_countries(forwarder_name)
        details = agent.forwarder_details.get(forwarder_name, {})
        
        print(f"  {forwarder_name}:")
        print(f"    └─ Countries: {len(countries)} ({', '.join(countries[:5])}{'...' if len(countries) > 5 else ''})")
        print(f"    └─ Operators: {', '.join(details.get('operators', [])[:3])}{'...' if len(details.get('operators', [])) > 3 else ''}")
        print(f"    └─ Emails: {', '.join(details.get('emails', [])[:2])}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n=== Testing Edge Cases ===")
    
    agent = ForwarderAssignmentAgent()
    agent.load_context()
    
    edge_cases = [
        {
            "name": "Missing validated_data",
            "input": {}
        },
        {
            "name": "Missing countries",
            "input": {
                "validated_data": {
                    "shipment_type": "FCL"
                }
            }
        },
        {
            "name": "Empty countries",
            "input": {
                "validated_data": {
                    "origin_country": "",
                    "destination_country": "",
                    "shipment_type": "FCL"
                }
            }
        },
        {
            "name": "Case sensitivity test",
            "input": {
                "validated_data": {
                    "origin_country": "brazil",  # lowercase
                    "destination_country": "USA",
                    "shipment_type": "FCL"
                }
            }
        }
    ]
    
    for i, test_case in enumerate(edge_cases, 1):
        print(f"\n--- Edge Case {i}: {test_case['name']} ---")
        
        result = agent.run(test_case['input'])
        
        if result.get("status") == "success":
            if "error" in result:
                print(f"✓ Error handled: {result.get('error')}")
            elif result.get("assignment_status") == "no_match":
                print(f"✓ No match handled: {result.get('reason')}")
            elif result.get("assignment_status") == "success":
                forwarders = result.get("assigned_forwarders", [])
                print(f"✓ Found {len(forwarders)} forwarders")
            else:
                print(f"? Unexpected result: {result}")
        else:
            print(f"✗ Error: {result.get('error')}")

def test_csv_file_detection():
    """Test CSV file detection and loading"""
    print("\n=== Testing CSV File Detection ===")
    
    # Check if CSV file exists
    possible_paths = [
        "Forwarders_with_Operators_and_Emails.csv",
        "./Forwarders_with_Operators_and_Emails.csv", 
        "../Forwarders_with_Operators_and_Emails.csv",
        "/Users/prashant.choubey/Documents/VSWorkspace/AI-Sales-Bot-V2/Forwarders_with_Operators_and_Emails.csv"
    ]
    
    print("Checking CSV file locations:")
    for path in possible_paths:
        exists = os.path.exists(path)
        print(f"  {path}: {'✓ Found' if exists else '✗ Not found'}")
        
        if exists:
            try:
                df = pd.read_csv(path)
                print(f"    └─ Rows: {len(df)}, Columns: {list(df.columns)}")
                
                # Show sample data
                sample_data = df.head(3).to_dict('records')
                for i, record in enumerate(sample_data, 1):
                    print(f"    └─ Sample {i}: {record}")
                
                # Show unique countries
                unique_countries = df['country'].unique()[:10]
                print(f"    └─ Sample countries: {list(unique_countries)}")
                
                # Show unique forwarders
                unique_forwarders = df['forwarder_name'].unique()[:5]
                print(f"    └─ Sample forwarders: {list(unique_forwarders)}")
                
                break
            except Exception as e:
                print(f"    └─ Error reading: {e}")

def test_integration_with_validation():
    """Test integration with validation agent output"""
    print("\n=== Testing Integration with Validation Agent ===")
    
    agent = ForwarderAssignmentAgent()
    agent.load_context()
    
    # Simulate validation agent output with countries that should exist in your CSV
    validation_output = {
        "validated_data": {
            "origin_code": "BRSSZ",
            "origin_name": "Santos", 
            "origin_country": "Brazil",
            "destination_code": "USLAX",
            "destination_name": "Los Angeles",
            "destination_country": "USA",
            "shipment_type": "FCL",
            "container_type": "40DC",
            "quantity": 2
        },
        "overall_validity": True,
        "completeness_score": 0.9
    }
    
    print("Input from validation agent:")
    print(f"  Route: {validation_output['validated_data']['origin_name']} → {validation_output['validated_data']['destination_name']}")
    print(f"  Countries: {validation_output['validated_data']['origin_country']} → {validation_output['validated_data']['destination_country']}")
    
    result = agent.run(validation_output)
    
    if result.get("status") == "success":
        if result.get("assignment_status") == "success":
            forwarders = result.get("assigned_forwarders", [])
            print(f"✓ Successfully assigned {len(forwarders)} forwarders")
            
            if forwarders:
                top_forwarder = forwarders[0]
                print(f"✓ Top recommendation: {top_forwarder['forwarder_name']}")
                print(f"✓ Coverage: {top_forwarder['country_presence']}")
                print(f"✓ Match strength: {top_forwarder['match_strength']}")
                print(f"✓ Countries served: {len(top_forwarder['countries_served'])}")
                print(f"✓ Primary email: {top_forwarder['primary_email']}")
        else:
            print(f"✗ Assignment failed: {result.get('reason')}")
            suggestions = result.get('suggestions', [])
            if suggestions:
                print(f"💡 Suggestions: {suggestions}")
    else:
        print(f"✗ Error: {result.get('error')}")

if __name__ == "__main__":
    # Run all tests
    test_csv_file_detection()
    test_forwarder_assignment_agent()
    test_country_coverage()
    test_forwarder_details()
    test_edge_cases()
    test_integration_with_validation()
    
    print("\n" + "="*50)
    print("✅ ALL FORWARDER ASSIGNMENT TESTS COMPLETED")
    print("="*50)

