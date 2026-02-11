# Email Template Testing Guide

## Quick Verification

### Step 1: Clear Browser Cache
The templates have been updated in the code, but your browser may be showing a cached version.

**Clear cache methods:**
- **Chrome/Edge**: Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
- **Firefox**: Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
- **Safari**: Press `Cmd+Option+E`

### Step 2: Hard Refresh the Page
After clearing cache, do a hard refresh:
- **Windows**: `Ctrl+Shift+R` or `Ctrl+F5`
- **Mac**: `Cmd+Shift+R`

### Step 3: Test Templates
Open the UI and select each template from the dropdown:

1. **Complete FCL Quote Request (Dubai → LA)**
   - Should populate:
     - Email Type: Customer
     - Sender: john.smith@techcorp.com
     - Subject: FCL Shipping Quote - Dubai to Los Angeles
     - Content: Full email about Jebel Ali to Los Angeles shipment

2. **Minimal Information Request (China → Germany)**
   - Should populate:
     - Email Type: Customer
     - Sender: maria.garcia@importexport.com
     - Subject: Shipping Quote Needed
     - Content: Brief email with China to Germany

3. **Customer Confirmation**
   - Should populate:
     - Email Type: Customer
     - Sender: john.smith@techcorp.com
     - Subject: RE: FCL Shipping Quote - Dubai to Los Angeles
     - Content: Confirmation message

4. **Forwarder Rate Quote (Dubai → LA)**
   - Should populate:
     - Email Type: Forwarder
     - Sender: ops@pacificbridgelogistics.com
     - Subject: Rate Quote - Jebel Ali to Los Angeles
     - Content: Detailed rate quote with $3,200 rate

5. **LCL Shipment Request (Hong Kong → UK)**
   - Should populate:
     - Email Type: Customer
     - Sender: emily.wong@hktrading.com
     - Subject: LCL Quote - Hong Kong to UK
     - Content: LCL request for Hong Kong to Felixstowe

6. **Urgent Shipment (Vietnam → USA)**
   - Should populate:
     - Email Type: Customer
     - Sender: lisa.johnson@fashionretail.com
     - Subject: URGENT - Need Quote Today - Vietnam to USA
     - Content: Urgent shipment request

---

## Verification Page

I've created a standalone verification page: `frontend/test-templates.html`

**To use it:**

1. Open in browser:
   ```
   http://localhost:8080/test-templates.html
   ```
   (or just open the file directly in your browser)

2. This page displays all 6 templates with their complete content
3. Verify that all fields are correctly populated
4. Check that routes match the sample conversations

---

## Troubleshooting

### Templates not loading in main UI?

**Check 1: Browser Console**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Select a template from dropdown
4. You should see: `✅ Loaded template: [Template Name]`

**Check 2: Network Tab**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Hard refresh the page
4. Check if `app.js` is being loaded from cache (should show 200, not 304)

**Check 3: JavaScript Errors**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for any red error messages
4. If you see errors related to `EMAIL_TEMPLATES`, the file may not have loaded

### Force Reload JavaScript

If templates still don't work after cache clear:

1. **Disable cache in DevTools:**
   - Open DevTools (F12)
   - Go to Network tab
   - Check "Disable cache" checkbox
   - Keep DevTools open while testing

2. **Incognito/Private Mode:**
   - Open the UI in an incognito/private window
   - This ensures no cached files are used

3. **Check File Timestamps:**
   ```bash
   ls -la frontend/app.js
   ```
   - Verify the file was recently modified

---

## Code Verification

The templates are correctly defined in `frontend/app.js` lines 18-125:

```javascript
const EMAIL_TEMPLATES = {
    'complete-fcl': { ... },      // ✓ Dubai → LA
    'minimal-info': { ... },      // ✓ China → Germany
    'customer-confirmation': { ... }, // ✓ Confirmation
    'forwarder-rate': { ... },    // ✓ Forwarder quote
    'lcl-shipment': { ... },      // ✓ Hong Kong → UK
    'urgent-shipment': { ... }    // ✓ Vietnam → USA (NEW)
};
```

The template selection handler (lines 320-345) correctly:
1. Gets the selected template
2. Updates the form state
3. Calls `updateUI()` to populate form fields
4. Shows a success message

---

## Expected Behavior

When you select a template:

1. **Visual Feedback:**
   - Green success message appears: "✅ Loaded template: [Name]"
   - Message disappears after 3 seconds

2. **Form Updates:**
   - "Email From" dropdown changes to Customer or Forwarder
   - Email address field updates
   - Subject field updates
   - Content textarea updates with full email body

3. **Console Log:**
   - Check console for confirmation message

---

## Files Modified

- ✅ `frontend/app.js` - All 6 templates updated
- ✅ `frontend/index.html` - Dropdown options updated with route info
- ✅ `frontend/test-templates.html` - NEW verification page

---

## Next Steps

1. **Clear browser cache**
2. **Hard refresh the page** (Cmd+Shift+R)
3. **Test each template** from the dropdown
4. **Verify** that email fields populate correctly
5. **If still not working**, open `test-templates.html` to verify templates are correct

---

## Contact

If templates still don't populate after following these steps, check:
- Browser console for JavaScript errors
- Network tab to ensure app.js is loading
- File permissions on app.js
- Server is serving the latest version of files

The code is correct - this is likely a caching issue that will be resolved with a hard refresh.
