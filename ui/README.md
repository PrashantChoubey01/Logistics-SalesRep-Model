# AI Logistics Response Model - Streamlit UI

A simple and clean Streamlit interface for the AI Logistics Response Model.

## Features

- 📧 **Email Processing**: Input email content and subject for AI processing
- 🔍 **Information Extraction**: Automatically extracts logistics details from emails
- 📊 **Classification**: Categorizes emails by type and urgency
- ✅ **Validation**: Validates extracted information and provides completeness scores
- 💰 **Indicative Rates**: Provides shipping rate estimates in email responses when possible
- 🚢 **Smart Forwarder Assignment**: Uses CountryExtractorAgent to extract countries from port codes and assigns appropriate forwarders
- 📤 **Response Generation**: Generates appropriate responses based on email content

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements_streamlit.txt
   ```

2. **Run the App**:
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Open Browser**: The app will open automatically at `http://localhost:8501`

## Usage

1. **Enter Email Details**: 
   - Fill in the email subject
   - Paste the email content in the text area

2. **Configure Settings** (optional):
   - Set sender email address
   - Modify thread ID
   - Enable debug information

3. **Process Email**: Click the "Process Email" button

4. **View Results**: 
   - Generated response
   - Classification results
   - Extracted information
   - Validation results
   - Rate recommendations (if applicable)

## Example Email

Try this sample logistics request:

**Subject**: Rate request for container shipment

**Content**: 
```
We want to ship from Jebel Ali to Mundra using 20DC containers. 
The total quantity is 99, total weight is 26 Metric Ton, shipment type is FCL, 
and the shipment date is 20th June 2025. The cargo is electronics.
```

## Architecture

The app integrates with the following AI agents:
- Classification Agent
- Extraction Agent  
- Validation Agent
- Container Standardization Agent
- Port Lookup Agent
- Rate Recommendation Agent
- Response Generator Agent

## Troubleshooting

- **Import Errors**: Ensure you're running from the project root directory
- **Agent Errors**: Check that all agent dependencies are installed
- **Memory Issues**: The app processes emails through multiple AI agents, which may take time

## Development

The app is built with:
- **Streamlit**: For the web interface
- **Python**: Backend processing
- **Custom CSS**: For styling and layout 