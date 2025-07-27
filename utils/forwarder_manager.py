#!/usr/bin/env python3
"""
Forwarder Manager
================

Manages forwarder assignment based on country matching and route optimization.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
import logging

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
            
            with open(self.json_file_path, 'r') as f:
                data = json.load(f)
            
            self.forwarders_data = data.get('forwarders', [])
            logger.info(f"Loaded {len(self.forwarders_data)} forwarder entries")
            
            # Create country-based lookup
            for forwarder in self.forwarders_data:
                country = forwarder['country'].strip()
                if country not in self.forwarders_by_country:
                    self.forwarders_by_country[country] = []
                
                forwarder_info = {
                    'name': forwarder['name'],
                    'country': country,
                    'operator': forwarder['operator'],
                    'email': forwarder['email'],
                    'company': forwarder.get('company', forwarder['name'])
                }
                self.forwarders_by_country[country].append(forwarder_info)
            
            logger.info(f"Created forwarder lookup for {len(self.forwarders_by_country)} countries")
            
        except Exception as e:
            logger.error(f"Error loading forwarders: {e}")
    
    def get_forwarders_by_country(self, country: str) -> List[Dict]:
        """Get forwarders for a specific country"""
        country = country.strip()
        return self.forwarders_by_country.get(country, [])
    
    def assign_forwarder_for_route(self, origin_country: str, destination_country: str) -> Optional[Dict]:
        """
        Assign forwarder based on origin and destination countries
        Priority: Destination country > Origin country > Any available
        """
        origin_country = origin_country.strip()
        destination_country = destination_country.strip()
        
        logger.info(f"Assigning forwarder for route: {origin_country} → {destination_country}")
        
        # Priority 1: Forwarders in destination country
        destination_forwarders = self.get_forwarders_by_country(destination_country)
        if destination_forwarders:
            selected = destination_forwarders[0]  # Take first available
            logger.info(f"Assigned forwarder from destination country: {selected['name']}")
            return selected
        
        # Priority 2: Forwarders in origin country
        origin_forwarders = self.get_forwarders_by_country(origin_country)
        if origin_forwarders:
            selected = origin_forwarders[0]  # Take first available
            logger.info(f"Assigned forwarder from origin country: {selected['name']}")
            return selected
        
        # Priority 3: Any available forwarder (fallback)
        if self.forwarders_by_country:
            # Get first available forwarder from any country
            for country, forwarders in self.forwarders_by_country.items():
                if forwarders:
                    selected = forwarders[0]
                    logger.info(f"Assigned fallback forwarder: {selected['name']} from {country}")
                    return selected
        
        logger.warning(f"No forwarder available for route: {origin_country} → {destination_country}")
        return None
    
    def get_forwarder_by_email(self, email: str) -> Optional[Dict]:
        """Get forwarder information by email address"""
        if self.forwarders_data is None:
            return None
        
        email = email.strip().lower()
        for forwarder in self.forwarders_data:
            if forwarder['email'].strip().lower() == email:
                return {
                    'name': forwarder['name'],
                    'country': forwarder['country'],
                    'operator': forwarder['operator'],
                    'email': forwarder['email'],
                    'company': forwarder.get('company', forwarder['name'])
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
                'name': f['name'],
                'country': f['country'],
                'operator': f['operator'],
                'email': f['email'],
                'company': f.get('company', f['name'])
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
                'name': f['name'],
                'country': f['country'],
                'operator': f['operator'],
                'email': f['email'],
                'company': f.get('company', f['name'])
            }
            for f in self.forwarders_data
            if f['operator'].strip() == operator
        ]
    
    def get_countries_with_forwarders(self) -> List[str]:
        """Get list of countries that have forwarders"""
        return list(self.forwarders_by_country.keys())
    
    def get_forwarder_statistics(self) -> Dict:
        """Get forwarder statistics"""
        if self.forwarders_data is None:
            return {}
        
        total_forwarders = len(self.forwarders_data)
        unique_companies = len(set(f['name'] for f in self.forwarders_data))
        unique_countries = len(self.forwarders_by_country)
        unique_operators = len(set(f['operator'] for f in self.forwarders_data))
        
        return {
            'total_forwarders': total_forwarders,
            'unique_companies': unique_companies,
            'unique_countries': unique_countries,
            'unique_operators': unique_operators,
            'countries_with_forwarders': list(self.forwarders_by_country.keys())
        } 