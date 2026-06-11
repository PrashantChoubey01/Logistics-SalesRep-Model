# 🔍 Debugging Guide - Process Button Not Working

## Steps to Debug

### 1. Open Browser Console
- Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
- Go to the "Console" tab
- Look for any red error messages

### 2. Check for JavaScript Errors
Look for these common issues:

**Error: "Cannot read property 'addEventListener' of null"**
- Means an element wasn't found
- Check if all HTML elements have correct IDs

**Error: "Failed to fetch" or "Network error"**
- API server is not running
- CORS issue
- Wrong API URL

**Error: "Unexpected token" or syntax errors**
- JavaScript syntax issue
- Check console for line numbers

### 3. Verify API Server is Running
```bash
# Check if server is running
curl http://localhost:5001/health

# Should return: {"status":"healthy",...}
```

### 4. Test API Endpoint Directly
```bash
curl -X POST http://localhost:5001/api/process-email \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "test@example.com",
    "subject": "Test",
    "content": "Test content",
    "thread_id": "test123"
  }'
```

### 5. Check Browser Network Tab
- Open DevTools (F12)
- Go to "Network" tab
- Click "Process Email" button
- Look for a request to `/api/process-email`
- Check if it shows:
  - Status: 200 (success) or error code
  - Request payload
  - Response data

### 6. Common Issues and Fixes

#### Issue: Button Click Does Nothing
**Possible causes:**
- JavaScript not loaded
- Event listener not attached
- Form validation failing silently

**Fix:**
- Check console for errors
- Verify `app.js` is loaded (check Network tab)
- Add `console.log('Button clicked')` in handler

#### Issue: "Failed to fetch"
**Possible causes:**
- API server not running
- Wrong URL
- CORS blocking request

**Fix:**
- Start API server: `python3 api_server.py`
- Check `apiBaseUrl` in `app.js` (should be `http://localhost:5001`)
- Check CORS settings in `api_server.py`

#### Issue: "CORS policy" error
**Possible causes:**
- Browser blocking cross-origin requests
- CORS not configured in API server

**Fix:**
- Verify CORS middleware in `api_server.py`
- Check browser console for exact CORS error
- Ensure API server allows your frontend origin

### 7. Test with Console Logging

I've added console logging to help debug. When you click the button, you should see:

```
📧 Form submitted - handleEmailSubmit called
📝 Form data: {sender: "...", subject: "...", ...}
🌐 Calling API: http://localhost:5001/api/process-email
✅ API Response received: {success: true, ...}
```

If you don't see these messages:
- The event listener isn't attached
- JavaScript isn't loading
- There's a syntax error preventing execution

### 8. Quick Test

Add this to browser console to test manually:

```javascript
// Test if state is loaded
console.log('Thread ID:', state.threadId);
console.log('API URL:', state.apiBaseUrl);

// Test API call manually
fetch('http://localhost:5001/api/process-email', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        sender: 'test@example.com',
        subject: 'Test',
        content: 'Test content',
        thread_id: 'test123'
    })
})
.then(r => r.json())
.then(d => console.log('Response:', d))
.catch(e => console.error('Error:', e));
```

### 9. Verify Files Are Loaded

Check browser Network tab for:
- `index.html` - Status 200
- `app.js` - Status 200
- `styles.css` - Status 200

If any show 404, the file path is wrong.

### 10. Check Form HTML

Verify the form has:
- `id="email-form"` on the `<form>` tag
- `type="submit"` on the button
- All required fields have `required` attribute

