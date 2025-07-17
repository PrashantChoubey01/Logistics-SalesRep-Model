# 🚢 Quick Demo Guide - AI Logistics Response Model

## 🚀 Start the Application

```bash
cd ui
streamlit run streamlit_app.py
```

Open: http://localhost:8501

---

## 📋 Demo Test Cases

### Test 1: Single Email (Basic)
1. Select "Single Email" mode
2. Use default content (already loaded)
3. Click "🚀 Process Email"
4. **Expected**: Logistics request processed with rate info

### Test 2: Thread with Confirmation
1. Select "Email Thread" mode
2. Click "Load Sample" 
3. Click "🚀 Process Thread"
4. **Expected**: Confirmation detected in Message 1, emails generated

### Test 3: Manual Thread
1. Select "Email Thread" mode
2. Add 3 messages manually:
   - **Message 1**: "Yes, I accept the quote. Please proceed."
   - **Message 2**: "Here is your quote: $2500 USD"
   - **Message 3**: "Can you provide a quote for shipping?"
3. Click "🚀 Process Thread"
4. **Expected**: Confirmation found in Message 1

---

## 🔍 Key Features to Show

### Thread Analysis Results:
- **Confirmation Detected**: True/False
- **Message Index**: Which message contains confirmation
- **Sender**: Who sent the confirmation
- **Confidence**: Detection reliability score

### Email Integration:
- **Customer Email**: Acknowledgment sent
- **Forwarder Email**: Notification to logistics partner
- **Safety**: Only test emails sent (no real emails)

### UI Features:
- **Input Mode Toggle**: Single vs Thread
- **Thread Builder**: Add messages with timestamps
- **Sample Loading**: Quick test scenarios
- **Real-time Results**: Live processing feedback

---

## 🎯 Demo Script (5 minutes)

1. **Intro** (30s): "Enhanced AI system that analyzes entire email conversations"
2. **Single Email** (1m): Show basic functionality
3. **Thread Analysis** (2m): Load sample, show confirmation detection
4. **Manual Thread** (1m): Create custom thread
5. **Wrap-up** (30s): Key benefits and next steps

---

## ✅ Success Indicators

- Thread analysis finds confirmations in any message
- Email acknowledgments generated automatically
- UI is intuitive and responsive
- Backward compatibility maintained

**Ready to demo! 🎉** 