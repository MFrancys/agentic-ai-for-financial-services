# Financial Fraud Detection AI - Agent-Based System

## 🎯 Focus: AI Agents for Fraud Detection

This system uses **autonomous AI agents** with the ReACT (Reasoning and Acting) framework to detect and investigate financial fraud in real-time.

### What Makes This Agent-Based?

**Traditional Rule-Based Systems:**
- ❌ Fixed rules and thresholds
- ❌ Can't adapt to new fraud patterns
- ❌ High false positive rates
- ❌ Manual investigation required

**Our AI Agent System:**
- ✅ **Autonomous reasoning** - Agent thinks through each case
- ✅ **Dynamic tool usage** - Chooses which tools to use
- ✅ **Evidence-based decisions** - Aggregates multiple signals
- ✅ **Explainable AI** - Complete reasoning trace
- ✅ **Adaptive** - Learns from patterns

## 🤖 How the Agent Works

### ReACT Framework

```
┌─────────────────────────────────────────┐
│  FRAUD CASE DETECTED                     │
│  "Multiple transactions from new device" │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  THOUGHT: Agent Reasoning                │
│  "This could be card theft. I should     │
│   check velocity, device, and location"  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  ACTION: Execute Tools                   │
│  → analyze_transaction_velocity()        │
│  → check_geographic_anomaly()            │
│  → analyze_device_fingerprint()          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  OBSERVATION: Analyze Results            │
│  "High velocity + new device +           │
│   foreign country = HIGH RISK"           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  DECISION: CONFIRMED FRAUD               │
│  Action: Block card immediately          │
│  Confidence: HIGH (9/10)                 │
└─────────────────────────────────────────┘
```

## 🛠️ Fraud Detection Tools (Agent's Toolkit)

The AI agent has access to these specialized tools:

### 1. **Transaction Velocity Analysis**
```python
analyze_transaction_velocity(account_id, hours)
```
- Detects rapid-fire transactions
- Identifies card testing patterns
- Calculates velocity risk score

### 2. **Geographic Anomaly Detection**
```python
check_geographic_anomaly(account_id, location)
```
- Detects impossible travel
- Identifies foreign transactions
- Compares to customer patterns

### 3. **Device Fingerprinting**
```python
analyze_device_fingerprint(account_id, device_id)
```
- Identifies new/unknown devices
- Tracks device switching
- Assesses device risk

### 4. **Behavioral Analysis**
```python
check_behavioral_anomalies(account_id, current_behavior)
```
- Compares to customer baseline
- Detects unusual patterns
- Identifies spending anomalies

### 5. **Fraud Probability Assessment**
```python
assess_fraud_probability(indicators)
```
- Aggregates all signals
- Calculates overall fraud score
- Provides final recommendation

## 🚨 Fraud Types Detected

### Credit Card Fraud
- **Indicators**: High velocity, new device, foreign country
- **Agent Strategy**: Check velocity → device → location → decide
- **Actions**: Block card, contact customer, refund

### Account Takeover
- **Indicators**: New device, password change, behavioral shift
- **Agent Strategy**: Analyze behavior → check device → assess risk
- **Actions**: Lock account, verify identity, alert customer

### Payment Fraud
- **Indicators**: Unusual amounts, new beneficiaries, velocity
- **Agent Strategy**: Check patterns → validate beneficiary → decide
- **Actions**: Block payment, additional verification

### Identity Theft
- **Indicators**: New account, synthetic identity signals
- **Agent Strategy**: Verify identity → check documents → assess
- **Actions**: Reject application, investigate further

## 📊 Agent Decision Framework

### Fraud Score Scale (0-10)

**8-10: CONFIRMED FRAUD** 🔴
- Multiple strong indicators
- Agent confidence: HIGH
- Action: Immediate block

**6-7: SUSPECTED FRAUD** 🟠
- Several indicators present
- Agent confidence: MEDIUM-HIGH
- Action: Block + verify

**4-5: NEEDS REVIEW** 🟡
- Some indicators present
- Agent confidence: MEDIUM
- Action: Enhanced monitoring

**0-3: LEGITIMATE** 🟢
- Normal patterns
- Agent confidence: HIGH
- Action: Allow transaction

## 🎯 Quick Start Examples

### Example 1: Credit Card Fraud
```python
from src.models.fraud_case import FraudCase, FraudType, FraudIndicator
from src.investigators.fraud_agent import FraudDetectionAgent

# Define fraud case
case = FraudCase(
    case_id="FRAUD_001",
    customer_id="CUST_001",
    account_id="ACCT_12345",
    fraud_type=FraudType.CREDIT_CARD_FRAUD,
    description="15 transactions in 2 hours from new device",
    fraud_indicators=[
        FraudIndicator.UNUSUAL_VELOCITY,
        FraudIndicator.NEW_DEVICE,
        FraudIndicator.GEOGRAPHIC_ANOMALY
    ],
    total_amount=4500.00,
    geolocation="Romania"
)

# Create AI agent
agent = FraudDetectionAgent()

# Agent investigates autonomously
result = agent.investigate(case, verbose=True)

# Review agent's decision
print(f"Decision: {result.recommendation}")
print(f"Fraud Score: {result.final_risk_score}/10")
print(f"Actions: {result.next_steps}")
```

### Example 2: Account Takeover
```python
case = FraudCase(
    case_id="FRAUD_002",
    fraud_type=FraudType.ACCOUNT_TAKEOVER,
    description="New device, password changed, unusual behavior",
    fraud_indicators=[
        FraudIndicator.NEW_DEVICE,
        FraudIndicator.BEHAVIORAL_CHANGE
    ]
)

agent = FraudDetectionAgent()
result = agent.investigate(case)
```

## 🚀 Running the System

### CLI Examples
```bash
# Credit card fraud investigation
python examples/fraud_credit_card.py

# Account takeover investigation
python examples/fraud_account_takeover.py
```

### Interactive Web Interface
```bash
streamlit run streamlit_app.py
```
Then select "Fraud Detection" mode.

## 🧠 Why Agent-Based?

### Traditional Systems:
```
IF velocity > threshold AND amount > limit:
    flag_transaction()
```
- Rigid rules
- High false positives
- Can't explain decisions

### Our AI Agent:
```
THOUGHT: "High velocity detected. Let me check device and location..."
ACTION: check_device_fingerprint(...)
OBSERVATION: "New device from foreign country - high risk!"
DECISION: "CONFIRMED FRAUD - block immediately"
```
- Dynamic reasoning
- Context-aware
- Explainable decisions
- Lower false positives

## 📈 Agent Performance

### Key Metrics:
- **Detection Rate**: Agent catches fraud patterns humans miss
- **False Positive Reduction**: Context-aware decisions reduce false alarms
- **Explainability**: Complete reasoning trace for audit
- **Adaptability**: Learns new fraud patterns

### Agent Advantages:
1. **Autonomous**: No manual rule creation
2. **Intelligent**: Reasons about complex scenarios
3. **Transparent**: Shows all reasoning steps
4. **Accurate**: Combines multiple signals
5. **Fast**: Real-time investigation (2-5 seconds)

## 🔒 Production Considerations

### For Production Deployment:
- ✅ Connect to real transaction databases
- ✅ Integrate with card processing systems
- ✅ Set up alerting and case management
- ✅ Implement human review workflow
- ✅ Monitor agent performance
- ✅ Regular model updates

### Compliance:
- Complete audit trail (ReACT reasoning)
- Explainable AI decisions
- Human oversight required
- Regular validation
- Performance monitoring

## 🎓 Understanding the Agent

The agent is **not** just running predefined rules. It:
1. **Thinks** about what evidence it needs
2. **Chooses** which tools to use
3. **Analyzes** results in context
4. **Decides** based on aggregated evidence
5. **Explains** its reasoning

This is true **autonomous agent behavior** using LLMs for intelligence.

## 📚 Learn More

- **ReACT Framework**: [Paper](https://arxiv.org/abs/2210.03629)
- **Agent Architecture**: See `src/investigators/fraud_agent.py`
- **Tool Implementation**: See `src/tools/fraud_detection_tools.py`
- **Prompts**: See `src/prompts/fraud_detection_prompts.py`

---

**Built with AI Agents, Powered by ReACT, Focused on Fraud** 🤖🔍

