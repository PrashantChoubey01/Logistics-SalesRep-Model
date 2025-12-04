# 🔧 Troubleshooting: Process Button Not Working

## Quick Diagnosis

### Step 1: Check API Server is Running

**Open a new terminal and run:**
```bash
source venv_ai_model/bin/activate
python3 api_server.py
```

**You should see:**
```
🚀 Initializing LangGraph Workflow Orchestrator...
✅ Orchestrator initialized successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**If you see errors:**
- Check if port 8000 is already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Step 2: Test API Connection

**Open this test page in your browser:**
```
http://localhost:8080/test-api.html
```

**Or test manually:**
```bash
curl http://localhost:5001/health
```

**Expected response:**
```json
{"status":"healthy","orchestrator_initialized":true,...}
```

### Step 3: Check Browser Console

1. Open your browser's Developer Tools (F12 or Cmd+Option+I)
2. Go to the "Console" tab
3. Click the "Process Email" button
4. Look for error messages

**Common errors you might see:**

#### Error: "Failed to fetch" or "NetworkError"
**Cause:** API server is not running or not accessible

**Fix:**
- Start the API server (see Step 1)
- Verify it's running on port 8000
- Check firewall settings

#### Error: "CORS policy" or "Access-Control-Allow-Origin"
**Cause:** Browser blocking cross-origin requests

**Fix:**
- Verify CORS is enabled in `api_server.py` (it should be)
- Check that API server allows your frontend origin
- Try accessing frontend and API from same origin

#### Error: "Cannot read property 'addEventListener' of null"
**Cause:** JavaScript trying to attach to element that doesn't exist

**Fix:**
- Check that `index.html` has all required elements
- Verify JavaScript is loading (check Network tab)
- Look for syntax errors in console

#### No errors, but button does nothing
**Cause:** Event listener not attached or form validation failing

**Fix:**
- Check browser console for initialization messages
- Verify form has required fields filled
- Check that `app.js` loaded successfully

### Step 4: Verify JavaScript is Loading

1. Open Developer Tools (F12)
2. Go to "Network" tab
3. Refresh the page
4. Look for:
   - `index.html` - Status 200 ✅
   - `app.js` - Status 200 ✅
   - `styles.css` - Status 200 ✅

**If any show 404:**
- Check file paths are correct
- Verify you're running the web server from the `frontend` directory

### Step 5: Check Console Logging

I've added detailed console logging. When you click "Process Email", you should see:

```
📧 Form submitted - handleEmailSubmit called
📝 Form data: {sender: "...", subject: "...", ...}
🌐 Calling API: http://localhost:5001/api/process-email
```

**If you don't see these messages:**
- The event listener isn't attached
- JavaScript isn't executing
- There's a syntax error

**If you see the messages but no API response:**
- API server is not running
- Network error
- CORS issue

## Common Issues and Solutions

### Issue 1: API Server Not Running

**Symptoms:**
- "Failed to fetch" error
- Network error in console
- No response from API

**Solution:**
```bash
# Terminal 1: Start API server
source venv_ai_model/bin/activate
python3 api_server.py

# Keep this terminal open!
```

### Issue 2: Wrong Port or URL

**Symptoms:**
- Connection refused
- 404 errors
- API calls going to wrong URL

**Solution:**
- Check `apiBaseUrl` in `frontend/app.js` (should be `http://localhost:5001`)
- Verify API server is on port 8000
- Check browser console for actual URL being called

### Issue 3: CORS Errors

**Symptoms:**
- "Access-Control-Allow-Origin" error
- CORS policy error in console

**Solution:**
- CORS is already configured in `api_server.py`
- If still having issues, check that both frontend and API are on localhost
- Verify CORS middleware is active

### Issue 4: Form Validation Failing Silently

**Symptoms:**
- Button click does nothing
- No console messages
- No errors shown

**Solution:**
- Check that all required fields are filled
- Verify email content is not empty
- Check browser console for validation errors

### Issue 5: JavaScript Not Loading

**Symptoms:**
- No console messages at all
- Page looks broken
- Elements not interactive

**Solution:**
- Check Network tab for 404 errors
- Verify `app.js` file exists and is accessible
- Check for JavaScript syntax errors in console
- Verify script tag in HTML is correct

## Quick Test Commands

```bash
# Test 1: Is API server running?
curl http://localhost:5001/health

# Test 2: Can we process an email?
curl -X POST http://localhost:8000/api/process-email \
  -H "Content-Type: application/json" \
  -d '{"sender":"test@test.com","subject":"Test","content":"Test","thread_id":"test"}'

# Test 3: Check if port is in use
lsof -i :8000
```

## Still Not Working?

1. **Check the test page:** Open `http://localhost:8080/test-api.html`
2. **Check browser console:** Look for specific error messages
3. **Check API server logs:** Look at the terminal running `api_server.py`
4. **Verify files:** Make sure all files are in the correct locations

## Need More Help?

Check the console output - I've added detailed logging that will show exactly where the process is failing.

