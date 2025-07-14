"""Agent to extract country from port code and recommend nearby countries using country_converter."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.base_agent import BaseAgent
import country_converter as coco

# Simple region clusters for "nearby" recommendations
REGION_GROUPS = {
    "North America": ["US", "CA", "MX"],
    "Central America": ["GT", "HN", "SV", "NI", "CR", "PA", "BZ"],
    "Caribbean": ["CU", "JM", "DO", "HT", "TT", "BS", "BB", "AG", "KN", "LC", "VC", "GD", "DM"],
    "South America": ["BR", "AR", "CO", "CL", "PE", "VE", "EC", "BO", "PY", "UY", "GF", "SR", "GY"],
    "Europe": [
        "GB", "IE", "FR", "DE", "NL", "BE", "LU", "CH", "AT", "IT", "ES", "PT", "NO", "SE", "DK", "FI",
        "PL", "CZ", "SK", "HU", "RO", "BG", "GR", "SI", "HR", "RS", "BA", "ME", "MK", "AL", "UA", "BY", "MD", "LT", "LV", "EE"
    ],
    "Russia & CIS": ["RU", "KZ", "UZ", "TM", "KG", "TJ", "AZ", "AM", "GE", "MD", "BY"],
    "Middle East": ["AE", "SA", "QA", "KW", "OM", "BH", "IQ", "IR", "JO", "LB", "SY", "YE", "TR", "IL", "PS"],
    "North Africa": ["MA", "DZ", "TN", "LY", "EG", "SD"],
    "West Africa": ["NG", "GH", "CI", "SN", "GM", "SL", "LR", "GW", "BJ", "TG", "BF", "NE", "ML", "GN", "MR", "CV"],
    "Central Africa": ["CM", "CF", "TD", "GQ", "GA", "CG", "CD", "ST"],
    "East Africa": ["ET", "KE", "UG", "TZ", "RW", "BI", "DJ", "ER", "SO", "SC", "KM", "MG", "MU"],
    "Southern Africa": ["ZA", "BW", "NA", "ZM", "ZW", "MZ", "AO", "MW", "LS", "SZ"],
    "South Asia": ["IN", "PK", "BD", "LK", "NP", "BT", "MV", "AF"],
    "East Asia": ["CN", "JP", "KR", "MN", "HK", "MO", "TW"],
    "Southeast Asia": ["SG", "MY", "TH", "VN", "ID", "PH", "KH", "LA", "MM", "BN", "TL"],
    "Oceania": ["AU", "NZ", "PG", "FJ", "SB", "VU", "NC", "PF", "WS", "TO", "TV", "KI", "FM", "MH", "PW", "NR"],
    "Arctic": ["GL", "SJ"],
    "Antarctica": ["AQ"]
}

def get_region(country_code):
    for region, codes in REGION_GROUPS.items():
        if country_code in codes:
            return region
    return "Other"

def recommend_nearby_countries(country_code, top_n=3):
    region = get_region(country_code)
    codes_in_region = REGION_GROUPS.get(region, [])
    # Exclude the original country
    nearby = [cc for cc in codes_in_region if cc != country_code]
    # If not enough, add from other regions
    all_codes = list(set(sum(REGION_GROUPS.values(), [])))
    if len(nearby) < top_n:
        others = [cc for cc in all_codes if cc not in codes_in_region and cc != country_code]
        nearby += others[:(top_n - len(nearby))]
    # Convert to country names
    return [coco.convert(names=cc, to='name_short', not_found=None) for cc in nearby[:top_n]]

class CountryExtractorAgent(BaseAgent):
    """Extracts country from port code and recommends nearby countries."""

    def __init__(self):
        super().__init__("country_extractor_agent")

    def process(self, input_data):
        port_code = input_data.get("port_code", "")
        if not port_code or len(port_code) < 2:
            return {
                "error": "Invalid or missing port code",
                "status": "error"
            }
        country_code = port_code[:2].upper()
        country_name = coco.convert(names=country_code, to='name_short', not_found=None)
        if not country_name or country_name == country_code:
            return {
                "error": f"Unknown country code: {country_code}",
                "status": "error",
                "country_code": country_code,
                "recommended_countries": recommend_nearby_countries(country_code)
            }
        return {
            "country_code": country_code,
            "country_name": country_name,
            "region": get_region(country_code),
            "recommended_countries": recommend_nearby_countries(country_code),
            "status": "success"
        }

# =====================================================
#                 🔁 Local Test Harness
# =====================================================
def test_country_extractor_agent():
    agent = CountryExtractorAgent()
    test_cases = [
        {"port_code": "USLGB"},
        {"port_code": "CNSHA"},
        {"port_code": "INBOM"},
        {"port_code": "DEHAM"},
        {"port_code": "ZZZZZ"},  # Unknown
        {"port_code": ""},       # Blank
    ]
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Input: {test['port_code']}")
        result = agent.run(test)
        print(result)

if __name__ == "__main__":
    test_country_extractor_agent()