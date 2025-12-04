# 🚀 Quick Start Guide - JavaScript UI

## Step-by-Step Instructions

### 1. Activate Virtual Environment

```bash
source venv_ai_model/bin/activate
```

Or if you have the activation script:
```bash
source activate_venv.sh
```

### 2. Install Dependencies (if not already done)
```bash
pip install -r requirements.txt
```

This will install FastAPI, uvicorn, and all other required packages.

### 3. Start the API Server

Open **Terminal 1** and run:
```bash
# Make sure virtual environment is activated
source venv_ai_model/bin/activate

# Start the server
python api_server.py
```

**Or use python3 if python doesn't work:**
```bash
python3 api_server.py
```

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     🚀 Initializing LangGraph Workflow Orchestrator...
INFO:     ✅ Orchestrator initialized successfully
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Keep this terminal open!** The server must be running for the frontend to work.

### 3. Open the Frontend

You have **two options**:

#### Option A: Direct File Open (Simplest)
1. Navigate to the `frontend` folder
2. Double-click `index.html`
3. It will open in your default browser

#### Option B: Local Web Server (Recommended)
Open **Terminal 2** and run:
```bash
cd frontend
python3 -m http.server 8080
```

**Or if you prefer a different port:**
```bash
python3 -m http.server 9000
# Then open http://localhost:9000
```

Then open your browser and go to:
```
http://localhost:8080
```

### 4. Verify Everything Works

1. **Check API Server**: Open http://localhost:8000/health in your browser
   - Should show: `{"status":"healthy","orchestrator_initialized":true,...}`

2. **Check Frontend**: 
   - You should see the "🚢 SeaRates AI" header
   - Thread ID should be displayed
   - Template selector should work

3. **Test Email Processing**:
   - Select a template from dropdown
   - Click "🚀 Process Email"
   - Wait for response (may take 10-30 seconds)
   - Response should appear below the form

## Troubleshooting

### ❌ "API server is not running"
- Make sure `python api_server.py` is running in Terminal 1
- Check http://localhost:8000/health works

### ❌ CORS Errors in Browser Console
- Ensure API server is running on port 8000
- Check browser console for exact error message
- Verify `apiBaseUrl` in `frontend/app.js` matches your server URL

### ❌ "Failed to fetch" or Network Errors
- Check that API server is running
- Verify the URL in browser console matches `http://localhost:8000`
- Try opening http://localhost:8000/health directly

### ❌ Port 8000 Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process (replace PID with actual process ID)
kill -9 <PID>

# Or change port in api_server.py (last line)
uvicorn.run(..., port=8001)  # Change to 8001
```

### ❌ Port 8080 Already in Use (for frontend server)
```bash
# Use a different port
python -m http.server 9000

# Then open http://localhost:9000
```

## Alternative: Using the Quick Start Script

```bash
./start_frontend.sh
```

This script will:
1. Check if API server is running
2. Offer to start it if not running
3. Start the frontend web server automatically

## What You Should See

### When API Server Starts:
```
🚀 Initializing LangGraph Workflow Orchestrator...
✅ Orchestrator initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### When Frontend Loads:
- Blue gradient header with "🚢 SeaRates AI"
- Thread ID displayed (e.g., `demo_thread_20241204_120000`)
- Email template dropdown
- Email form with fields
- Email history section (empty initially)

### When Processing Email:
- Loading spinner appears
- "Processing email through workflow..." message
- After 10-30 seconds, response sections appear:
  - ✅ Response Generated
  - 🚚 Forwarder Assignment (if applicable)
  - 📊 Forwarder Response (if applicable)
  - 📧 Sales Notification (if applicable)

## Next Steps

1. **Try Different Templates**: Select different templates to test various scenarios
2. **Check Email History**: Process multiple emails to see the history grow
3. **Test Forwarder Flow**: Process a complete FCL request, then respond as forwarder
4. **View Responses**: Expand history items to see full email and response details

## Stopping the Servers

- **API Server**: Press `Ctrl+C` in Terminal 1
- **Frontend Server**: Press `Ctrl+C` in Terminal 2 (if using Option B)

## Need Help?

- Check browser console (F12) for JavaScript errors
- Check API server terminal for Python errors
- Verify all dependencies are installed: `pip list | grep fastapi`
- Ensure Python 3.12+ is being used: `python --version`

