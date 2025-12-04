# 🖥️ How to Access and Use the UI

## Step 1: Start the Frontend Web Server

You need to run a web server to access the UI. Choose one method:

### Method A: Using Python (Easiest)

**Open a terminal and run:**
```bash
cd frontend
python3 -m http.server 8080
```

**You should see:**
```
Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

### Method B: Using the Helper Script

```bash
./run_frontend.sh
```

### Method C: Direct File Open (Limited)

1. Navigate to the `frontend` folder
2. Double-click `index.html`
3. **Note:** This may have limitations with API calls due to CORS

## Step 2: Open the UI in Your Browser

Once the web server is running, open your browser and go to:

```
http://localhost:8080
```

**Or if using IPv6:**
```
http://[::1]:8080
```

## Step 3: Using the UI - Step by Step

### 1. You'll See the Header
- Blue gradient header with "🚢 SeaRates AI - Logistics Sales Assistant"
- Thread ID displayed (e.g., `demo_thread_20241204_120000`)

### 2. Email Template Selector (Top Section)
- **Dropdown menu** labeled "Select an email template to load:"
- Click the dropdown and choose one:
  - "Complete FCL Quote Request"
  - "Minimal Information Request"
  - "Customer Confirmation"
  - "Forwarder Rate Quote"
  - "LCL Shipment Request"
- **After selecting:** The form fields below will automatically fill with template data

### 3. Email Form (Main Section)

#### Field 1: "Email From" (Dropdown)
- Select either:
  - **Customer** (default)
  - **Forwarder**

#### Field 2: "Customer Email" or "Forwarder Email" (Text Input)
- Enter an email address
- Example: `john.doe@techcorp.com`
- This field is **required**

#### Field 3: "Subject" (Text Input)
- Enter the email subject
- Example: `FCL Shipping Quote - Shanghai to Los Angeles`
- This field is **required**

#### Field 4: "Email Content" (Large Text Area)
- Enter the email body content
- This is a large text box where you type the email message
- This field is **required**

### 4. Process Email Button
- **Big blue button** labeled "🚀 Process Email"
- Click this after filling in the form
- The button will show a loading spinner while processing

## Quick Start Example

1. **Select a template:**
   - Click the template dropdown
   - Choose "Complete FCL Quote Request"
   - Form fields will auto-fill

2. **Review the filled fields:**
   - Email From: Customer
   - Customer Email: john.doe@techcorp.com
   - Subject: FCL Shipping Quote - Shanghai to Los Angeles
   - Email Content: (pre-filled with template content)

3. **Click "🚀 Process Email"**
   - Wait 10-30 seconds
   - Response will appear below

4. **View the Response:**
   - Response sections will appear
   - Email history will update

## Troubleshooting: Can't See the UI

### Issue: "This site can't be reached" or "Connection refused"

**Solution:**
- Make sure the web server is running
- Check the terminal for errors
- Verify you're using the correct URL: `http://localhost:8080`

### Issue: Page is blank or shows file listing

**Solution:**
- Make sure you're accessing `http://localhost:8080` (not a file path)
- Check that `index.html` exists in the `frontend` folder
- Try refreshing the page (F5 or Cmd+R)

### Issue: Form fields are not visible

**Solution:**
- Check browser console for errors (F12)
- Verify `styles.css` is loading (check Network tab)
- Try a different browser

### Issue: Can't type in form fields

**Solution:**
- Make sure JavaScript is enabled in your browser
- Check browser console for JavaScript errors
- Try refreshing the page

## Visual Guide

```
┌─────────────────────────────────────────┐
│  🚢 SeaRates AI                        │
│  Logistics Sales Assistant              │
└─────────────────────────────────────────┘

📧 Thread ID: demo_thread_20241204_120000
[🔄 Reset Thread]

───────────────────────────────────────────

📋 Email Templates
[Dropdown: Select a template ▼]

───────────────────────────────────────────

📝 Send Email

Email From: [Customer ▼]  Customer Email: [john.doe@techcorp.com]

Subject: [FCL Shipping Quote - Shanghai to Los Angeles]

Email Content:
┌─────────────────────────────────────────┐
│ Hello Searates,                        │
│                                         │
│ I need a shipping quote...             │
│                                         │
└─────────────────────────────────────────┘

[🚀 Process Email]  ← Click this button!
```

## Still Having Issues?

1. **Check if web server is running:**
   ```bash
   # In terminal, you should see:
   Serving HTTP on :: port 8080
   ```

2. **Check browser console:**
   - Press F12
   - Look for red error messages
   - Check if files are loading (Network tab)

3. **Verify files exist:**
   ```bash
   ls frontend/
   # Should show: index.html, app.js, styles.css
   ```

4. **Try a different port:**
   ```bash
   python3 -m http.server 9000
   # Then open: http://localhost:9000
   ```

## Need Help?

If you still can't access the UI, share:
1. What you see when you open `http://localhost:8080`
2. Any error messages from the terminal
3. Any error messages from browser console (F12)

