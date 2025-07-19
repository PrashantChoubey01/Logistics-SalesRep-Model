"""Streamlit Application for Logistics Email Processing POC"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
import time
import re
import os
import sys

# Add agents directory to path
agents_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agents')
if agents_path not in sys.path:
    sys.path.insert(0, agents_path)

# Configure page
st.set_page_config(
    page_title="Logistics AI Response System",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #155724;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #856404;
    }
    .info-box {
        background: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #0c5460;
    }
    .email-preview {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #212529;
    }
    .step-box {
        background: #f8f9fa;
        border-left: 4px solid #1f77b4;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
        color: #212529;
    }
    /* Premium Dark Theme with Sophisticated Colors */
    /* Override any existing styles with !important declarations */
    
    /* Force dark background */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%) !important;
    }
    
    /* Main text - Soft White */
    .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span, .stText {
        color: #e8e8e8 !important;
        background-color: transparent !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    /* Headers - Elegant Blue */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #64b5f6 !important;
        background-color: transparent !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5) !important;
    }
    
    /* JSON and Code - Light Colors for Better Readability */
    .stJson, .stDataFrame, .stCode, .stCode code, .stCode pre {
        color: #ffffff !important;
        background: linear-gradient(145deg, #3a3a5a 0%, #2a2a4a 100%) !important;
        border: 1px solid #5a5a7a !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
    }
    
    /* JSON specific styling for better contrast */
    .stJson {
        color: #e8f4fd !important;
        background: linear-gradient(145deg, #2d4a5a 0%, #1a3a4a 100%) !important;
        border: 1px solid #4a6a7a !important;
    }
    
    /* Code blocks with light text */
    .stCode, .stCode code, .stCode pre {
        color: #f0f8ff !important;
        background: linear-gradient(145deg, #2a4a5a 0%, #1a3a4a 100%) !important;
        border: 1px solid #4a6a7a !important;
    }
    
    /* Data frames with light text */
    .stDataFrame {
        color: #f5f5f5 !important;
        background: linear-gradient(145deg, #3a4a5a 0%, #2a3a4a 100%) !important;
        border: 1px solid #5a6a7a !important;
    }
    
    /* Force all text on blue/dark backgrounds to be light colored */
    .stJson *, .stCode *, .stDataFrame *, .stJson div, .stCode div, .stDataFrame div {
        color: #ffffff !important;
    }
    
    /* All text elements on any background should be light colored */
    .stMarkdown div, .stMarkdown span, .stMarkdown p, .stMarkdown strong, .stMarkdown b, .stMarkdown em, .stMarkdown i {
        color: #ffffff !important;
    }
    
    /* Specific override for any remaining black text */
    .stMarkdown, .stText, .stJson, .stCode, .stDataFrame {
        color: #ffffff !important;
    }
    
    /* Force all text to be white regardless of background */
    * {
        color: #ffffff !important;
    }
    
    /* Override for specific elements that need different colors */
    .main-header, .main-header h1, .main-header p {
        color: #ffffff !important;
    }
    
    .success-box {
        color: #00ff00 !important;
    }
    
    .warning-box {
        color: #ffff00 !important;
    }
    
    .info-box {
        color: #00ffff !important;
    }
    
    .error-box {
        color: #ff4444 !important;
    }
    
    /* Lists - Mint Green */
    .stMarkdown ul, .stMarkdown ol, .stMarkdown li {
        color: #81c784 !important;
        background-color: transparent !important;
    }
    
    /* Bold text - Coral Red */
    .stMarkdown strong, .stMarkdown b {
        color: #ff8a65 !important;
        background-color: transparent !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    /* Main header - White on gradient */
    .main-header, .main-header h1, .main-header p {
        color: #ffffff !important;
        background-color: transparent !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5) !important;
    }
    
    /* Status boxes - Premium colors */
    .success-box {
        color: #4caf50 !important;
        background: linear-gradient(145deg, #1b3a1b 0%, #0f2a0f 100%) !important;
        border: 1px solid #2d5a2d !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
    }
    
    .warning-box {
        color: #ff9800 !important;
        background: linear-gradient(145deg, #3a2a1a 0%, #2a1a0f 100%) !important;
        border: 1px solid #5a3a2d !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
    }
    
    .info-box {
        color: #2196f3 !important;
        background: linear-gradient(145deg, #1a3a3a 0%, #0f2a2a 100%) !important;
        border: 1px solid #2d5a5a !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
    }
    
    /* Streamlit alerts and messages */
    .stAlert, .stSuccess, .stError, .stWarning, .stInfo {
        color: #ffffff !important;
        background-color: transparent !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    /* Expander content */
    .streamlit-expanderContent, .streamlit-expanderHeader {
        color: #64b5f6 !important;
        background-color: transparent !important;
    }
    
    /* Container elements */
    .stContainer {
        color: #e8e8e8 !important;
        background-color: transparent !important;
    }
    
    /* Override any existing styles */
    * {
        color: inherit !important;
    }
    
    /* Ensure proper contrast for all elements */
    .stMarkdown *, .stText *, .stJson *, .stDataFrame * {
        color: inherit !important;
    }
    
    /* Premium UI elements */
    .stSidebar {
        background: linear-gradient(180deg, #2d2d44 0%, #1e1e2e 100%) !important;
        border-right: 1px solid #4a4a6a !important;
    }
    
    .stButton > button {
        background: linear-gradient(145deg, #4a4a6a 0%, #3a3a5a 100%) !important;
        color: #ffffff !important;
        border: 1px solid #6a6a8a !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(145deg, #5a5a7a 0%, #4a4a6a 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.4) !important;
    }
    
    .stTextInput > div > div > input {
        background: linear-gradient(145deg, #2d2d44 0%, #1e1e2e 100%) !important;
        color: #e8e8e8 !important;
        border: 1px solid #4a4a6a !important;
        border-radius: 8px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2) !important;
    }
    
    .stTextArea > div > div > textarea {
        background: linear-gradient(145deg, #2d2d44 0%, #1e1e2e 100%) !important;
        color: #e8e8e8 !important;
        border: 1px solid #4a4a6a !important;
        border-radius: 8px !important;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.2) !important;
    }
    
    /* Additional premium styling */
    .stSelectbox > div > div > div {
        background: linear-gradient(145deg, #2d2d44 0%, #1e1e2e 100%) !important;
        color: #e8e8e8 !important;
        border: 1px solid #4a4a6a !important;
        border-radius: 8px !important;
    }
    
    .stRadio > div > div > div {
        background: transparent !important;
        color: #e8e8e8 !important;
    }
    
    /* Email input and form elements - White text */
    .stTextInput > div > div > input::placeholder {
        color: #cccccc !important;
    }
    
    .stTextArea > div > div > textarea::placeholder {
        color: #cccccc !important;
    }
    
    /* Sidebar headers and labels */
    .stSidebar .stMarkdown h1, .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 {
        color: #ffffff !important;
    }
    
    .stSidebar .stMarkdown p, .stSidebar .stMarkdown div, .stSidebar .stMarkdown span {
        color: #ffffff !important;
    }
    
    /* Radio button labels */
    .stRadio > div > div > div > label {
        color: #ffffff !important;
    }
    
    /* Selectbox labels */
    .stSelectbox > div > div > div > label {
        color: #ffffff !important;
    }
    
    /* All form labels and text in sidebar */
    .stSidebar label, .stSidebar .stMarkdown, .stSidebar .stText {
        color: #ffffff !important;
    }
    
    /* Text area labels */
    .stTextArea > div > div > div > label {
        color: #ffffff !important;
    }
    
    /* Text input labels */
    .stTextInput > div > div > div > label {
        color: #ffffff !important;
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #64b5f6 0%, #2196f3 100%) !important;
        border-radius: 4px !important;
    }
    
    /* Conversation State Step - High text size, bold, white */
    .conversation-state-step {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5) !important;
        background: linear-gradient(135deg, #4a148c 0%, #6a1b9a 100%) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        margin: 1rem 0 !important;
        text-align: center !important;
    }
    
    /* All step headers */
    .step-header {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #ffffff !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3) !important;
    }
    
    /* Comprehensive black to white text conversion */
    /* Force white text on ALL elements */
    * {
        color: #ffffff !important;
    }
    
    /* Override any remaining black text with specific selectors */
    .stMarkdown, .stMarkdown *, .stText, .stText *, .stTextInput, .stTextInput *, .stTextArea, .stTextArea *, 
    .stSelectbox, .stSelectbox *, .stButton, .stButton *, .stProgress, .stProgress *, .stExpander, .stExpander *,
    .stJson, .stJson *, .stCode, .stCode *, .stAlert, .stAlert *, .stSuccess, .stSuccess *, .stError, .stError *,
    .stWarning, .stWarning *, .stInfo, .stInfo *, .stException, .stException *, .stHelp, .stHelp * {
        color: #ffffff !important;
    }
    
    /* Force white text on all Streamlit components */
    div[data-testid="stMarkdown"] *,
    div[data-testid="stText"] *,
    div[data-testid="stTextInput"] *,
    div[data-testid="stTextArea"] *,
    div[data-testid="stSelectbox"] *,
    div[data-testid="stButton"] *,
    div[data-testid="stProgress"] *,
    div[data-testid="stExpander"] *,
    div[data-testid="stJson"] *,
    div[data-testid="stCode"] *,
    div[data-testid="stAlert"] *,
    div[data-testid="stSuccess"] *,
    div[data-testid="stError"] *,
    div[data-testid="stWarning"] *,
    div[data-testid="stInfo"] *,
    div[data-testid="stException"] *,
    div[data-testid="stHelp"] * {
        color: #ffffff !important;
    }
    
    /* Override any remaining black text */
    .stMarkdown strong, .stMarkdown b, .stMarkdown em, .stMarkdown i, .stMarkdown u, .stMarkdown s,
    .stMarkdown code, .stMarkdown pre, .stMarkdown blockquote, .stMarkdown ul, .stMarkdown ol, .stMarkdown li {
        color: #ffffff !important;
    }
    
    /* Force white text on all labels and descriptions */
    label, .stLabel, .stDescription, .stCaption, .stSubheader, .stHeader {
        color: #ffffff !important;
    }
    
    /* Override any inline styles that might set black text */
    [style*="color: black"], [style*="color: #000"], [style*="color: #000000"] {
        color: #ffffff !important;
    }
    
    /* Force white text on all text elements */
    p, span, div, h1, h2, h3, h4, h5, h6, a, li, td, th, label, input, textarea, select, button {
        color: #ffffff !important;
    }
    
    /* Override browser dark mode extensions that might force black text */
    [data-testid="stAppViewContainer"] * {
        color: #ffffff !important;
    }
    
    /* Force white text on all form elements */
    input, textarea, select, option {
        color: #ffffff !important;
    }
    
    /* Override any CSS variables that might set black text */
    :root {
        --text-color: #ffffff !important;
        --color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Import and initialize real agents
def safe_import_agents():
    """Safely import agents with fallback to mock agents if needed."""
    agents = {}
    
    try:
        # Try to import from agents directory
        from agents.conversation_state_agent import ConversationStateAgent
        from agents.next_action_agent import NextActionAgent
        from agents.sales_notification_agent import SalesNotificationAgent
        from agents.rate_analysis_agent import RateAnalysisAgent
        from agents.enhanced_validation_agent import EnhancedValidationAgent
        from agents.classification_agent import ClassificationAgent
        from agents.extraction_agent import ExtractionAgent
        from agents.response_generator_agent import ResponseGeneratorAgent
        from agents.email_sender_agent import EmailSenderAgent
        from agents.port_lookup_agent import PortLookupAgent
        from agents.container_standardization_agent import ContainerStandardizationAgent
        from agents.country_extractor_agent import CountryExtractorAgent
        from agents.rate_recommendation_agent import RateRecommendationAgent
        
        agents = {
            'conversation_state': ConversationStateAgent,
            'next_action': NextActionAgent,
            'sales_notification': SalesNotificationAgent,
            'rate_analysis': RateAnalysisAgent,
            'enhanced_validation': EnhancedValidationAgent,
            'classification': ClassificationAgent,
            'extraction': ExtractionAgent,
            'response_generator': ResponseGeneratorAgent,
            'email_sender': EmailSenderAgent,
            'port_lookup': PortLookupAgent,
            'container_standardization': ContainerStandardizationAgent,
            'country_extractor': CountryExtractorAgent,
            'rate_recommendation': RateRecommendationAgent
        }
        
        st.success("✅ All real agents loaded successfully")
        
    except ImportError as e:
        st.warning(f"Some agents could not be imported: {e}")
        
        try:
            from conversation_state_agent import ConversationStateAgent
            from next_action_agent import NextActionAgent
            from sales_notification_agent import SalesNotificationAgent
            from rate_analysis_agent import RateAnalysisAgent
            from enhanced_validation_agent import EnhancedValidationAgent
            from classification_agent import ClassificationAgent
            from extraction_agent import ExtractionAgent
            from response_generator_agent import ResponseGeneratorAgent
            from email_sender_agent import EmailSenderAgent
            from port_lookup_agent import PortLookupAgent
            from container_standardization_agent import ContainerStandardizationAgent
            from country_extractor_agent import CountryExtractorAgent
            from rate_recommendation_agent import RateRecommendationAgent
            
            agents = {
                'conversation_state': ConversationStateAgent,
                'next_action': NextActionAgent,
                'sales_notification': SalesNotificationAgent,
                'rate_analysis': RateAnalysisAgent,
                'enhanced_validation': EnhancedValidationAgent,
                'classification': ClassificationAgent,
                'extraction': ExtractionAgent,
                'response_generator': ResponseGeneratorAgent,
                'email_sender': EmailSenderAgent,
                'port_lookup': PortLookupAgent,
                'container_standardization': ContainerStandardizationAgent,
                'country_extractor': CountryExtractorAgent,
                'rate_recommendation': RateRecommendationAgent
            }
            
            st.success("✅ All real agents loaded successfully (fallback import)")
            
        except ImportError as e2:
            st.error(f"Failed to import agents: {e2}")
            st.error("Using mock agents for demonstration")
            
            # Create mock agents for demonstration
            class MockAgent:
                def __init__(self, name):
                    self.name = name
                
                def load_context(self):
                    return True
                
                def process(self, input_data):
                    # Return realistic mock data based on agent type
                    if self.name == 'extraction':
                        return {
                            'status': 'success',
                            'origin': 'Jebel Ali',
                            'destination': 'Mundra',
                            'container_type': '20DC',
                            'quantity': 2,
                            'weight': '25,000 kg',
                            'volume': '35 CBM',
                            'shipment_date': '20th April 2024',
                            'commodity': 'Electronics',
                            'customer_name': 'Mike Johnson',
                            'shipment_type': 'FCL'
                        }
                    elif self.name == 'port_lookup':
                        return {
                            'status': 'success',
                            'results': [
                                {
                                    'port_code': 'AEJEA',
                                    'port_name': 'Jebel Ali (Dubai)',
                                    'confidence': 0.867,
                                    'method': 'vector_similarity'
                                },
                                {
                                    'port_code': 'INMUN',
                                    'port_name': 'Mundra',
                                    'confidence': 1.0,
                                    'method': 'exact_name_match'
                                }
                            ]
                        }
                    elif self.name == 'container_standardization':
                        return {
                            'status': 'success',
                            'standard_type': '20DC',
                            'confidence': 100,
                            'success': True,
                            'reasoning': 'Container type matches standard 20DC'
                        }
                    elif self.name == 'rate_recommendation':
                        return {
                            'status': 'success',
                            'query': {
                                'Origin_Code': 'AEJEA',
                                'Destination_Code': 'INMUN',
                                'Container_Type': '20DC'
                            },
                            'rate_recommendation': {
                                'match_type': 'exact_match',
                                'total_rates_found': 3,
                                'rate_range': '$2600 - $2800',
                                'price_range_recommendation': '[2600,2800]',
                                'formatted_rate_range': '$2,600 - $2,800'
                            },
                            'indicative_rate': '$2700',
                            'price_range_recommendation': '[2600,2800]',
                            'formatted_rate_range': '$2,600 - $2,800',
                            'data_source': 'rate_recommendation.csv',
                            'total_records_searched': 144211
                        }
                    elif self.name == 'enhanced_validation':
                        return {
                            'status': 'success',
                            'validation_results': {
                                'origin_port': {
                                    'is_valid': True,
                                    'confidence': 0.9,
                                    'validation_notes': 'AEJEA is a valid port code'
                                },
                                'destination_port': {
                                    'is_valid': True,
                                    'confidence': 0.9,
                                    'validation_notes': 'INMUN is a valid port code'
                                },
                                'container_type': {
                                    'is_valid': True,
                                    'confidence': 0.95,
                                    'validation_notes': '20DC is a standard container type'
                                }
                            },
                            'validation_confidence': 0.9
                        }
                    else:
                        return {
                            'status': 'success',
                            'agent': self.name,
                            'result': f'Mock result from {self.name}',
                            'confidence': 0.8,
                            'message': f'This is a mock response from {self.name} agent'
                        }
            
            agents = {
                'conversation_state': lambda: MockAgent('conversation_state'),
                'next_action': lambda: MockAgent('next_action'),
                'sales_notification': lambda: MockAgent('sales_notification'),
                'rate_analysis': lambda: MockAgent('rate_analysis'),
                'enhanced_validation': lambda: MockAgent('enhanced_validation'),
                'classification': lambda: MockAgent('classification'),
                'extraction': lambda: MockAgent('extraction'),
                'response_generator': lambda: MockAgent('response_generator'),
                'email_sender': lambda: MockAgent('email_sender'),
                'port_lookup': lambda: MockAgent('port_lookup'),
                'container_standardization': lambda: MockAgent('container_standardization'),
                'country_extractor': lambda: MockAgent('country_extractor'),
                'rate_recommendation': lambda: MockAgent('rate_recommendation')
            }
    
    return agents

# Initialize agents
agent_classes = safe_import_agents()

# Processing steps with descriptions
PROCESSING_STEPS = [
    {
        'name': 'conversation_state',
        'description': 'Analyze conversation state and thread context',
        'agent_class': agent_classes.get('conversation_state')
    },
    {
        'name': 'classification',
        'description': 'Classify email type and intent',
        'agent_class': agent_classes.get('classification')
    },
    {
        'name': 'extraction',
        'description': 'Extract shipment details from email',
        'agent_class': agent_classes.get('extraction')
    },
    {
        'name': 'port_lookup',
        'description': 'Look up port codes and names',
        'agent_class': agent_classes.get('port_lookup')
    },
    {
        'name': 'container_standardization',
        'description': 'Standardize container codes',
        'agent_class': agent_classes.get('container_standardization')
    },
    {
        'name': 'country_extractor',
        'description': 'Extract country information',
        'agent_class': agent_classes.get('country_extractor')
    },
    {
        'name': 'enhanced_validation',
        'description': 'Validate extracted data quality',
        'agent_class': agent_classes.get('enhanced_validation')
    },
    {
        'name': 'rate_recommendation',
        'description': 'Get indicative rates',
        'agent_class': agent_classes.get('rate_recommendation')
    },
    {
        'name': 'next_action',
        'description': 'Determine next action',
        'agent_class': agent_classes.get('next_action')
    },
    {
        'name': 'response_generator',
        'description': 'Generate customer response',
        'agent_class': agent_classes.get('response_generator')
    },
    {
        'name': 'sales_notification',
        'description': 'Notify sales team',
        'agent_class': agent_classes.get('sales_notification')
    },
    {
        'name': 'rate_analysis',
        'description': 'Analyze rates and margins',
        'agent_class': agent_classes.get('rate_analysis')
    }
]

# Sample emails for testing
SAMPLE_EMAILS = {
    "Rate Request - Shanghai to LA": """Hi, I need rates for 2x40HC from Shanghai to Los Angeles.
Cargo: Electronics, weight: 25,000 kg, volume: 35 CBM
Ready date: 20th April 2024

Thanks,
Mike Johnson""",
    
    "Booking Request - Shenzhen to NYC": """Hello, I would like to book 1x40GP from Shenzhen to New York.
Cargo: Textiles, weight: 15,000 kg, volume: 25 CBM
Ready date: 15th May 2024

Best regards,
Sarah Chen""",
    
    "General Inquiry - Guangzhou to Chicago": """Hi there, I'm looking for shipping options from Guangzhou to Chicago.
We have machinery to ship, approximately 30,000 kg, 40 CBM.
Ready date: 10th June 2024

Regards,
David Smith""",
    
    "Rate Request - Jebel Ali to Mundra": """Hi, I need rates for 2x40HC from jebel ali to mundra.
Cargo: Machinery, weight: 25,000 kg, volume: 35 CBM
Ready date: 20th April 2024

Thanks,
Mike Johnson"""
}

def process_email_with_agents(email_content):
    """Process email through all agents in sequence with proper data flow"""
    results = {}
    current_data = {'email_text': email_content}
    
    # Create a container for agent loading status
    loading_container = st.container()
    
    for step in PROCESSING_STEPS:
        step_name = step['name']
        agent_class = step['agent_class']
        
        try:
            # Display agent loading status in UI
            with loading_container:
                st.info(f"🔄 Loading {step_name.replace('_', ' ').title()} agent...")
            
            # Initialize agent
            if callable(agent_class):
                agent = agent_class()
            else:
                agent = agent_class()
            
            # Load context for real agents
            if hasattr(agent, 'load_context'):
                with loading_container:
                    st.info(f"⚙️ Initializing {step_name.replace('_', ' ').title()} agent context...")
                context_loaded = agent.load_context()
                with loading_container:
                    if context_loaded:
                        st.success(f"✅ {step_name.replace('_', ' ').title()} agent loaded successfully")
                    else:
                        st.warning(f"⚠️ {step_name.replace('_', ' ').title()} agent loaded with warnings")
            
            # Special handling for country extractor - process both origin and destination
            if step_name == 'country_extractor':
                port_result = results.get('port_lookup', {})
                if 'results' in port_result and len(port_result['results']) >= 2:
                    # Process origin country
                    origin_port_code = port_result['results'][0].get('port_code', '')
                    destination_port_code = port_result['results'][1].get('port_code', '')
                    
                    if origin_port_code and destination_port_code:
                        # Process origin
                        with loading_container:
                            st.info(f"🔄 Processing origin country ({origin_port_code[:2]})...")
                        origin_input = prepare_agent_input(step_name, current_data, results)
                        origin_input['port_code'] = origin_port_code[:2]
                        origin_input['port_type'] = 'origin'
                        origin_input['full_port_code'] = origin_port_code
                        origin_result = agent.process(origin_input)
                        
                        # Process destination
                        with loading_container:
                            st.info(f"🔄 Processing destination country ({destination_port_code[:2]})...")
                        destination_input = prepare_agent_input(step_name, current_data, results)
                        destination_input['port_code'] = destination_port_code[:2]
                        destination_input['port_type'] = 'destination'
                        destination_input['full_port_code'] = destination_port_code
                        destination_result = agent.process(destination_input)
                        
                        # Combine results
                        combined_result = {
                            'origin_country': origin_result,
                            'destination_country': destination_result,
                            'status': 'success',
                            'message': 'Both origin and destination countries extracted'
                        }
                        results[step_name] = combined_result
                        current_data.update(combined_result)
                        
                        # Show completion status
                        with loading_container:
                            st.success(f"✅ Country Extractor completed - Origin: {origin_port_code[:2]}, Destination: {destination_port_code[:2]}")
                        continue
                else:
                    # Single port case - use normal processing
                    agent_input = prepare_agent_input(step_name, current_data, results)
                    result = agent.process(agent_input)
                    results[step_name] = result
                    if isinstance(result, dict):
                        current_data.update(result)
                    continue
            
            # Normal processing for other agents
            with loading_container:
                st.info(f"🔄 Processing with {step_name.replace('_', ' ').title()} agent...")
            
            agent_input = prepare_agent_input(step_name, current_data, results)
            result = agent.process(agent_input)
            
            # Store result
            results[step_name] = result
            
            # Update current data for next agent
            if isinstance(result, dict):
                current_data.update(result)
            
            # Show processing completion status with detailed agent status
            with loading_container:
                # Extract status and confidence from agent output
                status = result.get('status', 'unknown')
                confidence = result.get('confidence', None)
                method = result.get('method', None)
                success = result.get('success', None)
                
                # Display status based on agent output
                if status == 'success':
                    st.success(f"✅ {step_name.replace('_', ' ').title()} - Status: SUCCESS")
                elif status == 'error' or status == 'failure':
                    st.error(f"❌ {step_name.replace('_', ' ').title()} - Status: FAILED")
                elif status == 'warning':
                    st.warning(f"⚠️ {step_name.replace('_', ' ').title()} - Status: WARNING")
                elif status == 'partial':
                    st.warning(f"⚠️ {step_name.replace('_', ' ').title()} - Status: PARTIAL")
                elif status == 'unknown':
                    st.info(f"ℹ️ {step_name.replace('_', ' ').title()} - Status: UNKNOWN")
                else:
                    st.info(f"ℹ️ {step_name.replace('_', ' ').title()} - Status: {status.upper()}")
                
                # Display confidence if available from agent
                if confidence is not None:
                    if isinstance(confidence, (int, float)):
                        st.info(f"📊 Confidence: {confidence:.1f}%")
                    else:
                        st.info(f"📊 Confidence: {confidence}")
                
                # Display method if available from agent
                if method:
                    st.info(f"🔧 Method: {method}")
                
                # Display success flag if available from agent
                if success is not None:
                    if success:
                        st.success(f"✅ Agent Success: True")
                    else:
                        st.error(f"❌ Agent Success: False")
            
            # Special handling for extraction agent
            if step_name == 'extraction' and isinstance(result, dict):
                # Add extracted data directly to current_data
                for key, value in result.items():
                    if key not in ['status', 'error', 'message', 'confidence', 'agent_name', 'agent_id', 'processed_at']:
                        current_data[key] = value
            
        except Exception as e:
            st.error(f"Error in {step_name}: {str(e)}")
            results[step_name] = {
                'status': 'error',
                'error': str(e),
                'message': f'Error processing {step_name}'
            }
    
    # Show final processing summary
    with loading_container:
        successful_agents = sum(1 for result in results.values() if result.get('status') == 'success')
        total_agents = len(results)
        success_rate = (successful_agents / total_agents) * 100 if total_agents > 0 else 0
        
        st.markdown("---")
        st.markdown(f"## 📊 Processing Summary")
        st.success(f"✅ **{successful_agents}/{total_agents}** agents completed successfully ({success_rate:.1f}% success rate)")
        
        # Show failed agents if any
        failed_agents = [name for name, result in results.items() if result.get('status') == 'error']
        if failed_agents:
            st.error(f"❌ Failed agents: {', '.join(failed_agents)}")
    
    return results

def prepare_agent_input(step_name, current_data, results):
    """Prepare input data for each agent based on previous results"""
    agent_input = current_data.copy()
    
    if step_name == 'port_lookup':
        # Extract port names from extraction results
        extraction_result = results.get('extraction', {})
        origin = extraction_result.get('origin')
        destination = extraction_result.get('destination')
        
        if origin and destination:
            agent_input['port_names'] = [origin, destination]
        elif origin:
            agent_input['port_name'] = origin
        elif destination:
            agent_input['port_name'] = destination
    
    elif step_name == 'country_extractor':
        # Extract port codes from port lookup results and get first 2 characters
        port_result = results.get('port_lookup', {})
        if 'results' in port_result and len(port_result['results']) >= 2:
            # Multiple ports case - process both origin and destination
            origin_port_code = port_result['results'][0].get('port_code', '')
            destination_port_code = port_result['results'][1].get('port_code', '')
            
            if origin_port_code and destination_port_code:
                # Process origin country first
                origin_country_code = origin_port_code[:2]
                agent_input['port_code'] = origin_country_code
                agent_input['port_type'] = 'origin'
                agent_input['full_port_code'] = origin_port_code
        elif 'port_code' in port_result:
            # Single port case - get first 2 characters
            port_code = port_result['port_code']
            if port_code:
                agent_input['port_code'] = port_code[:2]
    
    elif step_name == 'enhanced_validation':
        # Pass validated and standardized data from all previous agents
        extraction_result = results.get('extraction', {})
        port_result = results.get('port_lookup', {})
        container_result = results.get('container_standardization', {})
        
        # Create comprehensive validation data
        validation_data = {
            'origin': extraction_result.get('origin'),
            'destination': extraction_result.get('destination'),
            'container_type': container_result.get('standard_type') or extraction_result.get('container_type'),
            'shipment_type': extraction_result.get('shipment_type'),
            'quantity': extraction_result.get('quantity'),
            'weight': extraction_result.get('weight'),
            'volume': extraction_result.get('volume'),
            'shipment_date': extraction_result.get('shipment_date'),
            'commodity': extraction_result.get('commodity'),
            'customer_name': extraction_result.get('customer_name'),
            'customer_email': extraction_result.get('customer_email'),
            'customer_company': extraction_result.get('customer_company')
        }
        
        # Add both port codes and port names from port lookup for comprehensive validation
        if 'results' in port_result and len(port_result['results']) >= 2:
            # Origin port data
            validation_data['origin_port_code'] = port_result['results'][0].get('port_code', '')
            validation_data['origin_port_name'] = port_result['results'][0].get('port_name', '')
            validation_data['origin_port_confidence'] = port_result['results'][0].get('confidence', 0)
            validation_data['origin_port_method'] = port_result['results'][0].get('method', '')
            
            # Destination port data
            validation_data['destination_port_code'] = port_result['results'][1].get('port_code', '')
            validation_data['destination_port_name'] = port_result['results'][1].get('port_name', '')
            validation_data['destination_port_confidence'] = port_result['results'][1].get('confidence', 0)
            validation_data['destination_port_method'] = port_result['results'][1].get('method', '')
            
        elif 'results' in port_result and len(port_result['results']) == 1:
            # Single port case
            validation_data['origin_port_code'] = port_result['results'][0].get('port_code', '')
            validation_data['origin_port_name'] = port_result['results'][0].get('port_name', '')
            validation_data['origin_port_confidence'] = port_result['results'][0].get('confidence', 0)
            validation_data['origin_port_method'] = port_result['results'][0].get('method', '')
        
        # Also include original extracted port names for comparison
        validation_data['extracted_origin'] = extraction_result.get('origin', '')
        validation_data['extracted_destination'] = extraction_result.get('destination', '')
        
        # Add container standardization info
        if container_result:
            validation_data['standardized_container_type'] = container_result.get('standard_type')
            validation_data['container_confidence'] = container_result.get('confidence')
            validation_data['container_success'] = container_result.get('success')
        
        agent_input['validation_data'] = validation_data
        
        # Debug validation input
        st.info(f"🔍 Enhanced Validation Input: {validation_data}")
        
        # Also pass the data directly to the agent for compatibility
        agent_input.update(validation_data)
    
    elif step_name == 'rate_recommendation':
        # Prepare rate recommendation input
        extraction_result = results.get('extraction', {})
        port_result = results.get('port_lookup', {})
        container_result = results.get('container_standardization', {})
        
        # Get port codes from port lookup results (not port names)
        origin_code = ''
        destination_code = ''
        
        # Get standardized container type from container standardization agent
        # The container standardization agent returns 'standard_type' field
        container_type = container_result.get('standard_type') or container_result.get('standardized_container_type') or container_result.get('container_type') or extraction_result.get('container_type')
        
        # Debug container standardization result
        if container_result:
            st.info(f"📦 Container Standardization: {container_result.get('standard_type', 'Not found')} (Success: {container_result.get('success', False)})")
        
        # FCL shipment logic: If quantity is mentioned but no container type, assume 20ft
        if not container_type:
            # Check if this is an FCL shipment with quantity mentioned
            shipment_type = extraction_result.get('shipment_type', '').upper()
            quantity = extraction_result.get('quantity', 0)
            
            if shipment_type in ['FCL', 'FULL CONTAINER', 'FULL CONTAINER LOAD'] and quantity and quantity > 0:
                st.info(f"📦 FCL shipment detected with quantity {quantity}. Assuming 20ft containers.")
                container_type = '20DC'  # Assume 20ft dry container for FCL
            else:
                st.warning(f"⚠️ Missing container type for rate recommendation. Using fallback.")
                container_type = '40HC'  # Default fallback
        else:
            st.success(f"✅ Using container type: {container_type}")
        
        # Use the port codes from port lookup results
        if 'results' in port_result and len(port_result['results']) >= 2:
            # Use the actual port codes from port lookup
            origin_code = port_result['results'][0].get('port_code', '')
            destination_code = port_result['results'][1].get('port_code', '')
            
            # Debug: Show what we're getting from port lookup
            st.info(f"🔍 Port Lookup Origin: {port_result['results'][0]}")
            st.info(f"🔍 Port Lookup Destination: {port_result['results'][1]}")
            
            # Ensure we're using the correct port codes (not port names)
            if origin_code and len(origin_code) <= 5 and origin_code.isupper():
                st.success(f"✅ Using origin port code: {origin_code}")
            else:
                st.error(f"❌ Invalid origin port code: {origin_code}")
                
            if destination_code and len(destination_code) <= 5 and destination_code.isupper():
                st.success(f"✅ Using destination port code: {destination_code}")
            else:
                st.error(f"❌ Invalid destination port code: {destination_code}")
            
        elif 'results' in port_result and len(port_result['results']) == 1:
            # Single port case
            origin_code = port_result['results'][0].get('port_code', '')
            st.info(f"🔍 Port Lookup Single: {port_result['results'][0]}")
        elif 'port_code' in port_result:
            # Fallback for single port case
            origin_code = port_result.get('port_code', '')
            st.info(f"🔍 Port Lookup Fallback: {port_result}")
        else:
            # No port lookup results
            origin_code = ''
            destination_code = ''
            st.warning("⚠️ No port lookup results found")
        
        # Validate that we have valid port codes
        if not origin_code or not destination_code:
            st.warning(f"⚠️ Missing port codes for rate recommendation. Origin: '{origin_code}', Destination: '{destination_code}'")
        
        # Show final port codes being used
        st.info(f"🎯 Final Port Codes - Origin: '{origin_code}', Destination: '{destination_code}'")
        
        agent_input['origin_code'] = origin_code
        agent_input['destination_code'] = destination_code
        agent_input['container_type'] = container_type
        
        # Debug information
        st.info(f"🔍 Rate Recommendation Input: Origin='{origin_code}', Destination='{destination_code}', Container='{container_type}'")
        
        # Additional debugging for container standardization
        if container_result:
            st.info(f"📦 Container Standardization Result: {container_result.get('standard_type', 'Not found')} (Confidence: {container_result.get('confidence', 0):.1f}%)")
        else:
            st.warning("⚠️ No container standardization result found")
        
        # Debug port lookup results
        if port_result:
            st.info(f"🌊 Port Lookup Results: {port_result}")
        else:
            st.warning("⚠️ No port lookup result found")
        
        # Comprehensive debugging - show all available data
        st.markdown("### 🔍 Comprehensive Data Debug")
        st.info(f"**Extraction Result:** {extraction_result}")
        st.info(f"**Port Result:** {port_result}")
        st.info(f"**Container Result:** {container_result}")
        st.info(f"**Final Agent Input:** Origin='{origin_code}', Destination='{destination_code}', Container='{container_type}'")
        
        # Validate the data being passed
        if origin_code == "SHANGHAI" or destination_code == "LOS ANGELES":
            st.error(f"❌ ERROR: Wrong port codes detected! Origin='{origin_code}', Destination='{destination_code}'")
            st.error(f"❌ Expected: Origin='AEJEA', Destination='INMUN'")
        elif origin_code == "AEJEA" and destination_code == "INMUN":
            st.success(f"✅ Correct port codes: Origin='{origin_code}', Destination='{destination_code}'")
        else:
            st.warning(f"⚠️ Unexpected port codes: Origin='{origin_code}', Destination='{destination_code}'")
        
        if container_type == "40HC":
            st.error(f"❌ ERROR: Wrong container type detected! Container='{container_type}'")
            st.error(f"❌ Expected: Container='20DC'")
        elif container_type == "20DC":
            st.success(f"✅ Correct container type: Container='{container_type}'")
        else:
            st.warning(f"⚠️ Unexpected container type: Container='{container_type}'")
    
    elif step_name == 'response_generator':
        # Prepare response generator input
        extraction_result = results.get('extraction', {})
        classification_result = results.get('classification', {})
        rate_result = results.get('rate_recommendation', {})
        
        agent_input['extraction_data'] = extraction_result
        agent_input['classification_data'] = classification_result
        agent_input['rate_data'] = rate_result
        
        # Debug rate data being passed to response generator
        if rate_result:
            st.info(f"💰 Rate Data for Response: {rate_result.get('indicative_rate', 'No rate')} | Range: {rate_result.get('formatted_rate_range', 'No range')}")
        else:
            st.warning("⚠️ No rate data available for response generator")
    
    elif step_name == 'sales_notification':
        # Prepare sales notification input
        extraction_result = results.get('extraction', {})
        classification_result = results.get('classification', {})
        
        agent_input['notification_type'] = 'new_inquiry'
        agent_input['email_type'] = classification_result.get('email_type', 'general_inquiry')
        agent_input['customer_name'] = extraction_result.get('customer_name', 'Unknown')
        agent_input['commodity'] = extraction_result.get('commodity', 'Unknown')
        agent_input['value_estimate'] = 5000  # Default estimate
    
    elif step_name == 'rate_analysis':
        # Prepare rate analysis input
        rate_result = results.get('rate_recommendation', {})
        extraction_result = results.get('extraction', {})
        
        # Create mock forwarder rates for analysis
        forwarder_rates = [
            {
                'forwarder': 'DHL Global Forwarding',
                'rate': 2800,
                'transit_time': '18-22 days',
                'service_level': 'Premium'
            },
            {
                'forwarder': 'Kuehne + Nagel',
                'rate': 2600,
                'transit_time': '20-25 days',
                'service_level': 'Standard'
            },
            {
                'forwarder': 'DB Schenker',
                'rate': 2700,
                'transit_time': '19-23 days',
                'service_level': 'Premium'
            }
        ]
        
        agent_input['forwarder_rates'] = forwarder_rates
        agent_input['customer_requirements'] = extraction_result
    
    return agent_input

def validate_data_flow(results):
    """Validate and display data flow between agents"""
    flow_issues = []
    flow_success = []
    
    # Check extraction to port lookup flow
    extraction = results.get('extraction', {})
    port_lookup = results.get('port_lookup', {})
    
    if extraction.get('origin') and extraction.get('destination'):
        if 'error' in port_lookup:
            flow_issues.append(f"❌ Port Lookup failed: {port_lookup.get('error')}")
        else:
            flow_success.append("✅ Origin/Destination → Port Lookup")
    else:
        flow_issues.append("❌ Extraction missing origin/destination")
    
    # Check port lookup to country extractor flow
    if 'results' in port_lookup and len(port_lookup['results']) >= 2:
        country_extractor = results.get('country_extractor', {})
        if 'error' in country_extractor:
            flow_issues.append(f"❌ Country Extractor failed: {country_extractor.get('error')}")
        else:
            flow_success.append("✅ Port Codes (first 2 chars) → Country Extractor")
    
    # Check extraction to validation flow
    if extraction:
        validation = results.get('enhanced_validation', {})
        if 'error' in validation:
            flow_issues.append(f"❌ Validation failed: {validation.get('error')}")
        else:
            flow_success.append("✅ Extracted Data → Validation")
    
    # Check rate recommendation flow
    rate_rec = results.get('rate_recommendation', {})
    if 'error' in rate_rec:
        flow_issues.append(f"❌ Rate Recommendation failed: {rate_rec.get('error')}")
    elif rate_rec.get('indicative_rate'):
        flow_success.append("✅ Port Codes + Container → Rate Recommendation")
    
    # Check sales notification flow
    sales_notif = results.get('sales_notification', {})
    if 'error' in sales_notif:
        flow_issues.append(f"❌ Sales Notification failed: {sales_notif.get('error')}")
    else:
        flow_success.append("✅ Customer Info → Sales Notification")
    
    # Check rate analysis flow
    rate_analysis = results.get('rate_analysis', {})
    if 'error' in rate_analysis:
        flow_issues.append(f"❌ Rate Analysis failed: {rate_analysis.get('error')}")
    else:
        flow_success.append("✅ Forwarder Rates → Rate Analysis")
    
    return flow_success, flow_issues

def main():
    st.markdown('<div class="main-header"><h1>🚢 Logistics AI Response System</h1><p>Intelligent Email Processing with Multi-Agent Architecture</p></div>', unsafe_allow_html=True)
    
    # Sidebar for input
    with st.sidebar:
        st.header("📧 Email Input")
        
        # Email input method
        input_method = st.radio(
            "Choose input method:",
            ["Enter Email", "Sample Emails"],
            index=0
        )
        
        if input_method == "Enter Email":
            email_content = st.text_area(
                "Enter email content:",
                height=300,
                placeholder="Paste your email content here..."
            )
        else:
            selected_sample = st.selectbox(
                "Select sample email:",
                list(SAMPLE_EMAILS.keys())
            )
            email_content = SAMPLE_EMAILS[selected_sample]
            st.text_area("Sample email content:", email_content, height=200, disabled=True)
        
        # Process button
        if st.button("🚀 Process Email", type="primary", use_container_width=True):
            if email_content.strip():
                st.session_state.email_content = email_content
                st.session_state.processing = True
                st.session_state.results = {}
                st.session_state.current_step = 0
                st.rerun()
            else:
                st.error("Please enter email content")
    
    # Main content area
    if 'email_content' in st.session_state and st.session_state.email_content:
        st.markdown('<div class="email-preview"><h3>📧 Email Content</h3></div>', unsafe_allow_html=True)
        st.text_area("Email to process:", st.session_state.email_content, height=150, disabled=True)
        
        # Processing section
        if st.session_state.get('processing', False):
            st.markdown('<div class="conversation-state-step"><h3>🔄 Processing Pipeline</h3></div>', unsafe_allow_html=True)
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Create a container for real-time updates
            with st.container():
                st.markdown("### 📋 Agent Processing Status")
                
                # Process email
                results = process_email_with_agents(st.session_state.email_content)
                st.session_state.results = results
                st.session_state.processing = False
                
                # Update progress
                progress_bar.progress(100)
                status_text.text("✅ All processing completed!")
            
            st.rerun()
        
        # Display results
        if 'results' in st.session_state and st.session_state.results:
            st.markdown('<div class="step-box"><h3>📊 Processing Results</h3></div>', unsafe_allow_html=True)
            
            # Data flow validation
            flow_success, flow_issues = validate_data_flow(st.session_state.results)
            
            # Display data flow status
            col1, col2 = st.columns(2)
            
            with col1:
                if flow_success:
                    st.markdown('<div class="success-box"><h4>✅ Successful Data Flows</h4></div>', unsafe_allow_html=True)
                    for success in flow_success:
                        st.markdown(f"• {success}")
            
            with col2:
                if flow_issues:
                    st.markdown('<div class="warning-box"><h4>⚠️ Data Flow Issues</h4></div>', unsafe_allow_html=True)
                    for issue in flow_issues:
                        st.markdown(f"• {issue}")
            
            if not flow_success and not flow_issues:
                st.info("No data flow validation available")
            
            # Display each step result
            for i, step in enumerate(PROCESSING_STEPS):
                step_name = step['name']
                step_description = step['description']
                result = st.session_state.results.get(step_name, {})
                
                with st.expander(f"Step {i+1}: {step_name.replace('_', ' ').title()} - {step_description}", expanded=True):
                    if result:
                        # Extract status and confidence from agent output
                        status = result.get('status', 'unknown')
                        confidence = result.get('confidence', None)
                        method = result.get('method', None)
                        success = result.get('success', None)
                        message = result.get('message', None)
                        
                        # Status display with proper formatting
                        if status == 'success':
                            st.success(f"**Status:** {status.upper()}")
                        elif status == 'error' or status == 'failure':
                            st.error(f"**Status:** {status.upper()}")
                        elif status == 'warning':
                            st.warning(f"**Status:** {status.upper()}")
                        elif status == 'partial':
                            st.warning(f"**Status:** {status.upper()}")
                        elif status == 'unknown':
                            st.info(f"**Status:** {status.upper()}")
                        else:
                            st.info(f"**Status:** {status.upper()}")
                        
                        # Message display
                        if message:
                            st.info(f"**Message:** {message}")
                        
                        # Confidence display
                        if confidence is not None:
                            if isinstance(confidence, (int, float)):
                                st.info(f"**Confidence:** {confidence:.1f}%")
                            else:
                                st.info(f"**Confidence:** {confidence}")
                        
                        # Method display
                        if method:
                            st.info(f"**Method:** {method}")
                        
                        # Success flag display
                        if success is not None:
                            if success:
                                st.success(f"**Agent Success:** True")
                            else:
                                st.error(f"**Agent Success:** False")
                        
                        # Display specific data based on agent type
                        if step_name == 'extraction':
                            st.markdown("**Extracted Data:**")
                            # Display all extraction fields
                            for key, value in result.items():
                                if key not in ['status', 'error', 'message', 'confidence', 'agent_name', 'agent_id', 'processed_at', 'extraction_method'] and value:
                                    st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
                        
                        elif step_name == 'port_lookup':
                            if 'results' in result:
                                st.markdown("**Port Lookup Results:**")
                                for i, port_data in enumerate(result['results']):
                                    st.markdown(f"**Port {i+1}:**")
                                    for key, value in port_data.items():
                                        if value:
                                            st.markdown(f"  - **{key.replace('_', ' ').title()}:** {value}")
                            elif 'port_code' in result:
                                st.markdown("**Port Data:**")
                                for key, value in result.items():
                                    if key not in ['status', 'error', 'message', 'confidence', 'agent_name', 'agent_id', 'processed_at'] and value:
                                        st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
                        
                        elif step_name == 'container_standardization':
                            st.markdown("**Container Information:**")
                            for key, value in result.items():
                                if key not in ['status', 'error', 'message', 'confidence', 'agent_name', 'agent_id', 'processed_at'] and value:
                                    st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
                        
                        elif step_name == 'country_extractor':
                            st.markdown("**Country Data:**")
                            if 'origin_country' in result and 'destination_country' in result:
                                # Combined result with both origin and destination
                                st.markdown("**Origin Country:**")
                                origin = result['origin_country']
                                if isinstance(origin, dict):
                                    for key, value in origin.items():
                                        if key not in ['status', 'error', 'message', 'confidence', 'agent_name', 'agent_id', 'processed_at'] and value:
                                            st.markdown(f"  - **{key.replace('_', ' ').title()}:** {value}")
                                
                                st.markdown("**Destination Country:**")
                                destination = result['destination_country']
                                if isinstance(destination, dict):
                                    for key, value in destination.items():
                                        if key not in ['status', 'error', 'message', 'confidence', 'agent_name', 'agent_id', 'processed_at'] and value:
                                            st.markdown(f"  - **{key.replace('_', ' ').title()}:** {value}")
                            else:
                                # Single country result
                                for key, value in result.items():
                                    if key not in ['status', 'error', 'message', 'confidence', 'agent_name', 'agent_id', 'processed_at'] and value:
                                        st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
                        
                        elif step_name == 'enhanced_validation':
                            st.markdown("**Validation Results:**")
                            for key, value in result.items():
                                if key not in ['status', 'error', 'message', 'confidence', 'agent_name', 'agent_id', 'processed_at'] and value:
                                    st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
                        
                        elif step_name == 'rate_recommendation':
                            st.markdown("**Rate Information:**")
                            if 'query' in result:
                                st.markdown("**Query:**")
                                for key, value in result['query'].items():
                                    if value:
                                        st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
                            
                            if 'rate_recommendation' in result:
                                st.markdown("**Recommendation:**")
                                rec = result['rate_recommendation']
                                for key, value in rec.items():
                                    if value:
                                        st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
                            
                            if 'indicative_rate' in result:
                                st.markdown(f"- **Indicative Rate:** {result['indicative_rate']}")
                            
                            if 'formatted_rate_range' in result:
                                st.markdown(f"- **Formatted Rate Range:** {result['formatted_rate_range']}")
                            
                            if 'price_range_recommendation' in result:
                                st.markdown(f"- **Price Range Recommendation:** {result['price_range_recommendation']}")
                        
                        elif step_name == 'response_generator':
                            if 'response_body' in result:
                                st.markdown("**Generated Response:**")
                                st.text_area("Response:", result['response_body'], height=200, disabled=True)
                        
                        elif step_name == 'sales_notification':
                            st.markdown("**Sales Notification:**")
                            for key, value in result.items():
                                if key not in ['status', 'error', 'message', 'confidence', 'agent_name', 'agent_id', 'processed_at'] and value:
                                    st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
                        
                        elif step_name == 'rate_analysis':
                            st.markdown("**Rate Analysis:**")
                            for key, value in result.items():
                                if key not in ['status', 'error', 'message', 'confidence', 'agent_name', 'agent_id', 'processed_at'] and value:
                                    st.markdown(f"- **{key.replace('_', ' ').title()}:** {value}")
                        
                        # Show full result as JSON for debugging
                        with st.expander("View Full Result (JSON)"):
                            st.code(json.dumps(result, indent=2, default=str), language="json")
                    else:
                        st.warning("No result available for this step")
            
            # Download results
            st.markdown('<div class="step-box"><h3>💾 Export Results</h3></div>', unsafe_allow_html=True)
            
            # Create downloadable JSON
            results_json = json.dumps(st.session_state.results, indent=2, default=str)
            st.download_button(
                label="📥 Download Results (JSON)",
                data=results_json,
                file_name=f"logistics_processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
            
            # Create summary report
            summary_data = []
            for step in PROCESSING_STEPS:
                step_name = step['name']
                result = st.session_state.results.get(step_name, {})
                summary_data.append({
                    'Step': step_name.replace('_', ' ').title(),
                    'Status': result.get('status', 'unknown'),
                    'Confidence': result.get('confidence', 0),
                    'Message': result.get('message', 'No message')
                })
            
            summary_df = pd.DataFrame(summary_data)
            csv_data = summary_df.to_csv(index=False)
            st.download_button(
                label="📊 Download Summary (CSV)",
                data=csv_data,
                file_name=f"logistics_processing_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    main() 