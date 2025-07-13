"""Configuration for Streamlit app"""

# App settings
APP_TITLE = "Email Workflow Agent"
APP_ICON = "📧"
LAYOUT = "wide"

# Databricks settings
DATABRICKS_TOKEN = "dapi81b45be7f09611a410fc3e5104a8cadf-3"
DATABRICKS_BASE_URL = "https://adb-1825279086009288.8.azuredatabricks.net/serving-endpoints"
MODEL_ENDPOINT_ID = "databricks-meta-llama-3-3-70b-instruct"

# Email type configurations
EMAIL_TYPES = {
    'logistics_request': {
        'color': '#28a745',
        'icon': '📦',
        'description': 'Customer requesting shipping quote or service'
    },
    'confirmation_reply': {
        'color': '#17a2b8',
        'icon': '✅',
        'description': 'Customer confirming or accepting a proposal'
    },
    'forwarder_response': {
        'color': '#ffc107',
        'icon': '💰',
        'description': 'Freight forwarder providing rates or quotes'
    },
    'clarification_reply': {
        'color': '#6f42c1',
        'icon': '💬',
        'description': 'Customer providing requested information'
    },
    'non_logistics': {
        'color': '#6c757d',
        'icon': '📄',
        'description': 'Not related to shipping or logistics'
    }
}

# Action configurations
ACTIONS = {
    'assign_forwarder': {
        'color': '#28a745',
        'icon': '🚚',
        'priority': 'high'
    },
    'request_clarification': {
        'color': '#ffc107',
        'icon': '❓',
        'priority': 'medium'
    },
    'process_confirmation': {
        'color': '#17a2b8',
        'icon': '✅',
        'priority': 'high'
    },
    'parse_quote': {
        'color': '#6f42c1',
        'icon': '💰',
        'priority': 'medium'
    },
    'update_shipment_info': {
        'color': '#20c997',
        'icon': '📝',
        'priority': 'medium'
    },
    'forward_to_support': {
        'color': '#6c757d',
        'icon': '🎧',
        'priority': 'low'
    },
    'escalate_to_human': {
        'color': '#dc3545',
        'icon': '🚨',
        'priority': 'high'
    },
    'manual_review': {
        'color': '#fd7e14',
        'icon': '👁️',
        'priority': 'medium'
    }
}

# Sample emails for testing
SAMPLE_EMAILS = {
    'logistics_request': {
        'subject': 'Shipping Quote Request',
        'content': 'Need quote for 2x40ft FCL from Shanghai to Long Beach, electronics cargo, ready July 15th, 25 tons total weight'
    },
    'confirmation_reply': {
        'subject': 'Re: Booking Confirmation',
        'content': 'Yes, I confirm the booking for the containers. Please proceed with the shipment.'
    },
    'forwarder_response': {
        'subject': 'Rate Quote - Shanghai to Long Beach',
        'content': 'Our rate is $2500 USD for FCL 40ft from Shanghai to Long Beach, valid until month end. Transit time 14 days.'
    },
    'clarification_reply': {
        'subject': 'Re: Missing Shipment Information',
        'content': 'The origin port is Shanghai and destination is Long Beach. Commodity is electronics, weight approximately 20 tons.'
    },
    'non_logistics': {
        'subject': 'Office Party Invitation',
        'content': 'Hello everyone! We are having an office party next Friday. Please let me know if you can attend.'
    }
}