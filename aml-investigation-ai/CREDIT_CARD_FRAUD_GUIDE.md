# Credit Card Fraud Detection - Quick Start

## 🚀 Run the Credit Card Fraud Detection App

### Step 1: Make sure you have your API key set up
```bash
cd /Users/mfrancys/Documents/2026/agentic-ai-for-financial-services/aml-investigation-ai

# Check if .env exists and has your API key
cat .env | grep OPENAI_API_KEY

# If not, create it:
echo "OPENAI_API_KEY=your_actual_key_here" > .env
echo "MODEL_NAME=gpt-4o-mini" >> .env
echo "TEMPERATURE=0.3" >> .env
echo "MAX_ITERATIONS=5" >> .env
echo "ENABLE_MOCK_DATA=true" >> .env
```

### Step 2: Run the Fraud Detection App
```bash
streamlit run fraud_detection_app.py
```

The app will open in your browser at `http://localhost:8501`

## 🎯 Using the App

### Quick Detection Mode
1. Select "Quick Detection" from sidebar
2. Choose a fraud scenario:
   - **Stolen Card - Foreign Country** (High risk)
   - **Account Takeover - New Device** (Medium risk)
   - **Legitimate Transaction - Traveling** (Low risk)
3. Click "🤖 Start AI Agent Investigation"
4. Watch the agent work through the ReACT framework
5. Review the fraud decision and evidence

### Custom Case Mode
1. Select "Custom Case" from sidebar
2. Fill in case details:
   - Customer and account IDs
   - Fraud type
   - Amount and location
   - Select fraud indicators
3. Click "🚀 Run Fraud Detection"
4. Agent investigates autonomously
5. Get detailed results

### What the AI Agent Does

```
🧠 THOUGHT → 🔧 ACTION → 👁️ OBSERVATION → 📊 DECISION
```

**Example:**
```
THOUGHT: "Multiple transactions from new device in foreign country"
ACTION: analyze_transaction_velocity(account_id, hours=2)
OBSERVATION: "15 transactions in 2 hours, avg 8 minutes apart"
THOUGHT: "Need to check device and location"
ACTION: check_geographic_anomaly(account_id, "Romania")
OBSERVATION: "Customer normally in NY, never been to Romania"
ACTION: analyze_device_fingerprint(account_id, "DEV_UNKNOWN_999")
OBSERVATION: "Brand new device, never seen before"
DECISION: 🔴 CONFIRMED FRAUD - Block card immediately
```

## 📊 Fraud Score Scale

- **8-10** 🔴 CONFIRMED FRAUD → Block immediately
- **6-7** 🟠 SUSPECTED FRAUD → Block + verify
- **4-5** 🟡 NEEDS REVIEW → Enhanced monitoring
- **0-3** 🟢 LEGITIMATE → Allow transaction

## 🤖 AI Agent Features

✅ **Autonomous:** Agent decides which tools to use
✅ **Intelligent:** Reasons about complex fraud scenarios  
✅ **Explainable:** Complete reasoning trace for audit
✅ **Fast:** Real-time detection (2-5 seconds)
✅ **Accurate:** Combines multiple fraud signals

## 🔧 Agent's Toolkit

1. **Velocity Analysis** - Detects rapid-fire transactions
2. **Geographic Checks** - Identifies impossible travel
3. **Device Fingerprinting** - Flags new/unknown devices
4. **Behavioral Analysis** - Compares to customer baseline
5. **Risk Assessment** - Aggregates all signals

## 📱 App Features

- 🎨 **Beautiful UI** - Modern, intuitive interface
- 📊 **Real-time Visualization** - Fraud gauge, charts
- 🧠 **Agent Reasoning** - See how agent thinks
- 📥 **Export Reports** - Download JSON reports
- 📜 **History Tracking** - Review past investigations
- 🔍 **Evidence Display** - Organized by severity

## 🐛 Troubleshooting

**App won't start:**
```bash
pip install streamlit plotly
streamlit run fraud_detection_app.py
```

**API Key error:**
```bash
# Make sure .env file exists with your key
cat .env
```

**No fraud cases showing:**
- The app uses predefined mock cases
- Try "Quick Detection" mode first

## 💡 Tips

1. **Try all 3 scenarios** to see agent behavior
2. **Watch the reasoning trace** to understand decisions
3. **Compare different cases** to see pattern recognition
4. **Use custom mode** to test edge cases
5. **Check agent tool usage** in expandable section

## 🎓 Learn More

- **Agent Code:** `src/investigators/fraud_agent.py`
- **Tools:** `src/tools/fraud_detection_tools.py`
- **Prompts:** `src/prompts/fraud_detection_prompts.py`
- **Full Guide:** `FRAUD_DETECTION_README.md`

---

**Ready to detect fraud with AI agents! 🤖💳**

