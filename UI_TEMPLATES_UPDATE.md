# UI Email Templates Update

**Date**: February 10, 2026  
**Purpose**: Align frontend email templates with sample conversations using real rate recommendation data

---

## Summary of Changes

Updated all email templates in the frontend UI (`frontend/app.js` and `frontend/index.html`) to match the routes and scenarios documented in `SAMPLE_CONVERSATIONS.md`. All templates now use port pairs that have actual rate recommendation data in the CSV file.

---

## Updated Templates

### 1. Complete FCL Quote Request (Happy Path)
**Route**: Jebel Ali (AEJEA) → Los Angeles (USLAX)  
**Rate Data Available**: Yes ($1,951 - $4,837, Market Avg: $3,364)

**Changes**:
- Changed from: Shanghai → Los Angeles
- Changed to: Jebel Ali, Dubai → Los Angeles
- Updated sender: `john.smith@techcorp.com`
- Updated commodity: Electronics (Consumer Goods)
- Updated date: March 15, 2026
- Matches: **Conversation 1** in SAMPLE_CONVERSATIONS.md

**Template Key**: `complete-fcl`

---

### 2. Minimal Information Request
**Route**: China → Germany (will be clarified to Shanghai → Hamburg)  
**Rate Data Available**: Yes (CNSGH → DEHAM: $1,464 - $2,862, Market Avg: $2,237)

**Changes**:
- Changed from: USA → China
- Changed to: China → Germany
- Updated sender: `maria.garcia@importexport.com`
- Updated company: Import/Export Solutions Ltd
- Matches: **Conversation 2** in SAMPLE_CONVERSATIONS.md

**Template Key**: `minimal-info`

---

### 3. Customer Confirmation
**Route**: Jebel Ali (AEJEA) → Los Angeles (USLAX)  
**Context**: Follows the complete FCL request

**Changes**:
- Updated to match Conversation 1 confirmation response
- Changed sender: `john.smith@techcorp.com`
- Updated subject: RE: FCL Shipping Quote - Dubai to Los Angeles
- Added reference to indicative rates
- Matches: **Conversation 1, Email 2** in SAMPLE_CONVERSATIONS.md

**Template Key**: `customer-confirmation`

---

### 4. Forwarder Rate Quote
**Route**: Jebel Ali (AEJEA) → Los Angeles (USLAX)  
**Rate Data Available**: Yes ($1,951 - $4,837, Market Avg: $3,364)

**Changes**:
- Changed from: Shanghai → Los Angeles
- Changed to: Jebel Ali → Los Angeles
- Updated rate: $3,200 USD (within market range)
- Updated transit time: 21 days
- Updated validity: March 31, 2026
- Added forwarder name: Michael Chen, Pacific Bridge Logistics
- Matches: **Conversation 1, Email 4** in SAMPLE_CONVERSATIONS.md

**Template Key**: `forwarder-rate`

---

### 5. LCL Shipment Request
**Route**: Hong Kong (HKHKG) → Felixstowe (GBFXT)  
**Rate Data Available**: N/A (LCL shipment - no CSV data needed)

**Changes**:
- Changed from: Singapore → New York
- Changed to: Hong Kong → Felixstowe, UK
- Updated sender: `emily.wong@hktrading.com`
- Updated commodity: Fashion Accessories
- Simplified format (minimal info style)
- Matches: **Conversation 3** in SAMPLE_CONVERSATIONS.md

**Template Key**: `lcl-shipment`

---

### 6. Urgent Shipment (NEW)
**Route**: Vietnam → Los Angeles (will be clarified to Ho Chi Minh → LA)  
**Rate Data Available**: Yes (VNSGN → USLAX: $2,125 - $4,620, Market Avg: $3,252)

**Changes**:
- **NEW TEMPLATE** added to match urgent scenario
- Sender: `lisa.johnson@fashionretail.com`
- Subject: URGENT - Need Quote Today - Vietnam to USA
- Country-only origin (requires clarification)
- 2 containers of garments
- Urgent tone and timeline
- Matches: **Conversation 5** in SAMPLE_CONVERSATIONS.md

**Template Key**: `urgent-shipment`

---

## HTML Dropdown Updates

Updated `frontend/index.html` template selector to include route information:

```html
<option value="complete-fcl">Complete FCL Quote Request (Dubai → LA)</option>
<option value="minimal-info">Minimal Information Request (China → Germany)</option>
<option value="customer-confirmation">Customer Confirmation</option>
<option value="forwarder-rate">Forwarder Rate Quote (Dubai → LA)</option>
<option value="lcl-shipment">LCL Shipment Request (Hong Kong → UK)</option>
<option value="urgent-shipment">Urgent Shipment (Vietnam → USA)</option>
```

---

## Default Form State

Updated default form state in `app.js`:

```javascript
formState: {
    emailType: 'Customer',
    senderEmail: 'john.smith@techcorp.com',
    subject: 'FCL Shipping Quote - Dubai to Los Angeles',
    content: ''
}
```

---

## Rate Recommendation Data Alignment

All templates now use port pairs that exist in `data/rate_recommendation.csv`:

| Template | Origin Code | Destination Code | Container | Rate Range | Market Avg |
|----------|-------------|------------------|-----------|------------|------------|
| Complete FCL | AEJEA | USLAX | 40HC | $1,951-$4,837 | $3,364 |
| Minimal Info | CNSGH | DEHAM | 40HC | $1,464-$2,862 | $2,237 |
| Forwarder Rate | AEJEA | USLAX | 40HC | $1,951-$4,837 | $3,364 |
| LCL Shipment | HKHKG | GBFXT | N/A | N/A (LCL) | N/A |
| Urgent | VNSGN | USLAX | 40HC | $2,125-$4,620 | $3,252 |

---

## Testing Workflow

Users can now test the complete workflow with real rate data:

1. **Select "Complete FCL Quote Request (Dubai → LA)"**
   - Bot will return confirmation request with market rates: $1,951-$4,837
   - Select "Customer Confirmation" template
   - Bot will acknowledge and assign forwarders
   - Select "Forwarder Rate Quote (Dubai → LA)" template
   - Bot will send sales notification with rate comparison

2. **Select "Minimal Information Request (China → Germany)"**
   - Bot will request clarification for missing fields
   - Manually provide: Shanghai port, Hamburg, 40HC, furniture, March date
   - Bot will return confirmation with market rates: $1,464-$2,862

3. **Select "Urgent Shipment (Vietnam → USA)"**
   - Bot will acknowledge urgency and request port clarification
   - Manually provide: Ho Chi Minh port, 40HC, February 20
   - Bot will return confirmation with market rates: $2,125-$4,620

---

## Files Modified

1. **frontend/app.js**
   - Updated `EMAIL_TEMPLATES` object (all 5 existing templates + 1 new)
   - Updated default `formState`
   - Lines modified: ~108 lines in templates section

2. **frontend/index.html**
   - Updated template dropdown options with route information
   - Added new "Urgent Shipment" option
   - Lines modified: 6 options in template selector

---

## Verification Checklist

- [x] All templates use port pairs from rate_recommendation.csv
- [x] Template routes match SAMPLE_CONVERSATIONS.md scenarios
- [x] Dropdown labels include route information for clarity
- [x] New urgent template added for Conversation 5 scenario
- [x] Default form state updated to match Conversation 1
- [x] Forwarder template uses realistic rate within market range
- [x] LCL template simplified to match minimal-info style
- [x] Customer confirmation template references indicative rates

---

*This update ensures the frontend UI demo uses the same realistic data and workflows documented in the sample conversations, providing a consistent experience for testing and demonstration.*
