#!/usr/bin/env python3
"""
Sales Team Manager - Handles sales person assignment and signature management
"""

import json
import os
import random
from typing import Any, Dict, List, Optional


class SalesTeamManager:
    """Manages sales team assignment and signature handling"""

    def __init__(self, config_file: str = "config/sales_team.json"):
        self.config_file = config_file
        self.sales_team = self._load_sales_team()
        self.assignment_history = {}

    def _load_sales_team(self) -> Dict[str, Any]:
        """Load sales team configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    return json.load(f)
            else:
                print(f"Sales team config not found: {self.config_file}")
                return self._get_default_sales_team()
        except Exception as e:
            print(f"Error loading sales team config: {e}")
            return self._get_default_sales_team()

    def _get_default_sales_team(self) -> Dict[str, Any]:
        """Get default sales team configuration with 8 consistent sales managers"""
        return {
            "sales_team": [
                {
                    "id": "SP001",
                    "name": "Sarah Johnson",
                    "title": "Senior Sales Manager",
                    "email": "sarah.johnson@logistics-company.com",
                    "phone": "+1-555-0101",
                    "whatsapp": "+1-555-0101",
                    "specialization": "Asia-Pacific Routes",
                    "signature": "Best regards,\n\nSarah Johnson\nSenior Sales Manager\nLogistics Solutions Inc.\n📧 sarah.johnson@logistics-company.com\n📞 +1-555-0101\n🌐 www.logistics-company.com",
                },
                {
                    "id": "SP002",
                    "name": "Michael Chen",
                    "title": "Account Executive",
                    "email": "michael.chen@freight-solutions.com",
                    "phone": "+1-555-0202",
                    "whatsapp": "+1-555-0202",
                    "specialization": "Europe-Middle East Routes",
                    "signature": "Best regards,\n\nMichael Chen\nAccount Executive\nFreight Solutions Inc.\n📧 michael.chen@freight-solutions.com\n📞 +1-555-0202\n🌐 www.freight-solutions.com",
                },
                {
                    "id": "SP003",
                    "name": "Emily Rodriguez",
                    "title": "Business Development Manager",
                    "email": "emily.rodriguez@global-shipping.com",
                    "phone": "+1-555-0303",
                    "whatsapp": "+1-555-0303",
                    "specialization": "Americas Routes",
                    "signature": "Best regards,\n\nEmily Rodriguez\nBusiness Development Manager\nGlobal Shipping Solutions\n📧 emily.rodriguez@global-shipping.com\n📞 +1-555-0303\n🌐 www.global-shipping.com",
                },
                {
                    "id": "SP004",
                    "name": "David Kim",
                    "title": "Client Relations Manager",
                    "email": "david.kim@cargo-experts.com",
                    "phone": "+1-555-0404",
                    "whatsapp": "+1-555-0404",
                    "specialization": "Africa Routes",
                    "signature": "Best regards,\n\nDavid Kim\nClient Relations Manager\nCargo Experts Ltd.\n📧 david.kim@cargo-experts.com\n📞 +1-555-0404\n🌐 www.cargo-experts.com",
                },
                {
                    "id": "SP005",
                    "name": "Lisa Thompson",
                    "title": "Sales Consultant",
                    "email": "lisa.thompson@supply-chain.com",
                    "phone": "+1-555-0505",
                    "whatsapp": "+1-555-0505",
                    "specialization": "Ocean Freight",
                    "signature": "Best regards,\n\nLisa Thompson\nSales Consultant\nSupply Chain Solutions\n📧 lisa.thompson@supply-chain.com\n📞 +1-555-0505\n🌐 www.supply-chain.com",
                },
                {
                    "id": "SP006",
                    "name": "Alex Martinez",
                    "title": "Regional Sales Manager",
                    "email": "alex.martinez@trade-logistics.com",
                    "phone": "+1-555-0606",
                    "whatsapp": "+1-555-0606",
                    "specialization": "Air Freight",
                    "signature": "Best regards,\n\nAlex Martinez\nRegional Sales Manager\nTrade Logistics Inc.\n📧 alex.martinez@trade-logistics.com\n📞 +1-555-0606\n🌐 www.trade-logistics.com",
                },
                {
                    "id": "SP007",
                    "name": "Rachel Green",
                    "title": "Key Account Manager",
                    "email": "rachel.green@shipping-partners.com",
                    "phone": "+1-555-0707",
                    "whatsapp": "+1-555-0707",
                    "specialization": "Express Shipping",
                    "signature": "Best regards,\n\nRachel Green\nKey Account Manager\nShipping Partners Ltd.\n📧 rachel.green@shipping-partners.com\n📞 +1-555-0707\n🌐 www.shipping-partners.com",
                },
                {
                    "id": "SP008",
                    "name": "James Wilson",
                    "title": "International Sales Manager",
                    "email": "james.wilson@freight-forwarders.com",
                    "phone": "+1-555-0808",
                    "whatsapp": "+1-555-0808",
                    "specialization": "Project Cargo",
                    "signature": "Best regards,\n\nJames Wilson\nInternational Sales Manager\nFreight Forwarders Inc.\n📧 james.wilson@freight-forwarders.com\n📞 +1-555-0808\n🌐 www.freight-forwarders.com",
                },
            ],
            "default_sales_person": {
                "id": "SP001",
                "name": "Sarah Johnson",
                "title": "Senior Sales Manager",
                "email": "sarah.johnson@logistics-company.com",
                "phone": "+1-555-0101",
                "whatsapp": "+1-555-0101",
                "specialization": "Asia-Pacific Routes",
            },
        }

    def get_sales_person_by_id(self, sales_person_id: str) -> Optional[Dict[str, Any]]:
        """Get sales person by ID"""
        for person in self.sales_team.get("sales_team", []):
            if person.get("id") == sales_person_id:
                return person
        return None

    def get_sales_person_signature(self, sales_person_id: str) -> str:
        """Get sales person signature"""
        person = self.get_sales_person_by_id(sales_person_id)
        if person:
            return person.get("signature", "")
        return self._get_default_signature()

    def _get_default_signature(self) -> str:
        """Get default signature"""
        return """Best regards,

Logistics Solutions Inc.
📧 info@logistics-company.com
📞 +1-555-0000
🌐 www.logistics-company.com"""

    def assign_sales_person(
        self, route_info: Dict[str, Any], customer_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assign appropriate sales person based on route and customer context"""

        # Get all available sales persons
        available_persons = self.sales_team.get("sales_team", [])

        if not available_persons:
            # Fallback to default
            return self.sales_team.get("default_sales_person", {})

        # Select a random sales person from the 8 available
        selected_person = random.choice(available_persons)

        # Update assignment history
        self._update_assignment_history(selected_person, route_info)

        return selected_person

    def _update_assignment_history(self, sales_person: Dict[str, Any], route_info: Dict[str, Any]):
        """Update assignment history for load balancing"""
        person_id = sales_person.get("id")
        if person_id not in self.assignment_history:
            self.assignment_history[person_id] = 0
        self.assignment_history[person_id] += 1

    def get_all_sales_persons(self) -> List[Dict[str, Any]]:
        """Get all sales persons"""
        return self.sales_team.get("sales_team", [])

    def get_sales_person_stats(self) -> Dict[str, Any]:
        """Get sales person assignment statistics"""
        return self.assignment_history
