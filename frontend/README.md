# SeaRates AI - Frontend Application

Modern JavaScript UI for the Logistics AI Bot, replacing the Streamlit demo app.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ with dependencies installed
- FastAPI server running (see below)

### Running the Application

1. **Start the FastAPI Server** (from project root):
   ```bash
   python api_server.py
   ```
   The server will start on `http://localhost:5001`

2. **Open the Frontend**:
   - Simply open `frontend/index.html` in your web browser
   - Or use a local web server:
     ```bash
     # Python 3
     cd frontend
     python -m http.server 8080
     # Then open http://localhost:8080
     
     # Or Node.js
     npx http-server frontend -p 8080
     ```

3. **Configure API URL** (if needed):
   - Edit `frontend/app.js`
   - Change `apiBaseUrl` in the `state` object if your API is on a different host/port

## 📁 File Structure

```
frontend/
├── index.html      # Main HTML structure
├── styles.css      # All styling
├── app.js          # Application logic
└── README.md       # This file
```

## 🎯 Features

- ✅ **Email Template Selector**: 5 pre-configured templates
- ✅ **Email Form**: Send customer or forwarder emails
- ✅ **Response Display**: Shows all response types with proper formatting
- ✅ **Email History**: Expandable history with full email and response details
- ✅ **Forwarder Response Form**: Conditional form when forwarder is assigned
- ✅ **State Persistence**: Uses localStorage to save thread ID and history
- ✅ **Modern UI**: Responsive design with clean styling
- ✅ **Error Handling**: User-friendly error messages

## 🔧 API Integration

The frontend communicates with the FastAPI server at `/api/process-email`:

**Request:**
```json
{
  "sender": "customer@example.com",
  "subject": "Shipping Quote Request",
  "content": "Email body content...",
  "thread_id": "demo_thread_20241204_120000"
}
```

**Response:**
```json
{
  "success": true,
  "thread_id": "demo_thread_20241204_120000",
  "workflow_id": "workflow_20241204_120000_123456",
  "result": {
    "workflow_state": {...}
  }
}
```

## 🎨 Customization

### Changing API URL
Edit `frontend/app.js`:
```javascript
const state = {
    // ...
    apiBaseUrl: 'http://your-api-host:port'
};
```

### Adding New Templates
Edit `frontend/app.js` and add to `EMAIL_TEMPLATES` object:
```javascript
const EMAIL_TEMPLATES = {
    // ... existing templates
    'my-template': {
        type: 'Customer',
        sender: 'email@example.com',
        subject: 'Subject',
        content: 'Content...'
    }
};
```

Then add option to `index.html`:
```html
<option value="my-template">My Template Name</option>
```

## 🐛 Troubleshooting

### CORS Errors
If you see CORS errors, ensure:
1. FastAPI server has CORS middleware configured (already in `api_server.py`)
2. API URL in `app.js` matches the server URL

### API Connection Failed
- Check that `api_server.py` is running
- Verify the API URL in `app.js` matches your server
- Check browser console for detailed error messages

### State Not Persisting
- Ensure localStorage is enabled in your browser
- Check browser console for any errors

## 📝 Notes

- The frontend uses vanilla JavaScript (no frameworks required)
- State is persisted in browser localStorage
- All styling is in `styles.css` for easy customization
- The UI is fully responsive and works on mobile devices

