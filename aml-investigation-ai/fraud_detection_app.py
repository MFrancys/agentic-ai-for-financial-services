"""
Credit Card Fraud Detection AI - Streamlit Web Application

Interactive web interface for detecting credit card fraud using AI agents.
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

from src.models.fraud_case import FraudCase, FraudType, FraudIndicator
from src.investigators.fraud_agent import FraudDetectionAgent
from src.config import settings

# Page configuration
st.set_page_config(
    page_title="Credit Card Fraud Detection AI",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #dc3545;
        padding: 1rem 0;
    }
    .fraud-confirmed {
        background-color: #dc3545;
        color: white;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.2rem;
        text-align: center;
    }
    .fraud-suspected {
        background-color: #fd7e14;
        color: white;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.2rem;
        text-align: center;
    }
    .legitimate {
        background-color: #28a745;
        color: white;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 1.2rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'fraud_result' not in st.session_state:
    st.session_state.fraud_result = None
if 'investigation_history' not in st.session_state:
    st.session_state.investigation_history = []


# ============================================================================
# HELPER FUNCTIONS - Define these FIRST before using them
# ============================================================================

def display_fraud_results(result):
    """Display fraud detection results."""
    
    st.markdown("## 🎯 AI Agent Decision")
    
    # Main decision
    if result.final_risk_score >= 8:
        st.markdown(f'<div class="fraud-confirmed">🔴 CONFIRMED FRAUD</div>', unsafe_allow_html=True)
    elif result.final_risk_score >= 6:
        st.markdown(f'<div class="fraud-suspected">🟠 SUSPECTED FRAUD</div>', unsafe_allow_html=True)
    elif result.final_risk_score >= 4:
        st.markdown(f'<div class="legitimate">🟡 NEEDS REVIEW</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="legitimate">🟢 LEGITIMATE</div>', unsafe_allow_html=True)
    
    st.markdown("")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Fraud Score", f"{result.final_risk_score}/10")
    with col2:
        st.metric("Evidence Items", len(result.evidence))
    with col3:
        st.metric("Tools Used", len(result.tool_executions))
    with col4:
        st.metric("Duration", f"{result.investigation_duration_seconds:.2f}s")
    
    # Fraud gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=result.final_risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Fraud Risk Level", 'font': {'size': 24}},
        delta={'reference': 5, 'increasing': {'color': "red"}},
        gauge={
            'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 4], 'color': '#90EE90'},
                {'range': [4, 6], 'color': '#FFD700'},
                {'range': [6, 8], 'color': '#FFA500'},
                {'range': [8, 10], 'color': '#FF4500'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 8
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)
    
    # Agent's recommendation
    st.markdown("### 🤖 Agent's Recommendation")
    st.info(result.recommendation)
    
    # Key findings
    if result.key_findings:
        st.markdown("### 🔍 Key Evidence")
        for finding in result.key_findings:
            st.markdown(f"- {finding}")
    
    # Evidence table
    if result.evidence:
        st.markdown("### 📋 Evidence Collected by Agent")
        evidence_data = []
        for ev in result.evidence:
            evidence_data.append({
                'Type': ev.evidence_type,
                'Severity': ev.severity.upper(),
                'Description': ev.description[:80] + '...' if len(ev.description) > 80 else ev.description,
                'Source Tool': ev.source
            })
        df = pd.DataFrame(evidence_data)
        st.dataframe(df, use_container_width=True)
        
        # Evidence severity pie chart
        severity_counts = df['Severity'].value_counts()
        fig = px.pie(values=severity_counts.values, names=severity_counts.index,
                    title='Evidence by Severity',
                    color_discrete_map={'HIGH': 'red', 'MEDIUM': 'orange', 'LOW': 'green'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Actions
    st.markdown("### ✅ Recommended Actions")
    for step in result.next_steps:
        st.markdown(f"- {step}")
    
    # Agent reasoning trace
    with st.expander("🧠 View Agent Reasoning (ReACT Trace)"):
        if result.reasoning_trace:
            for i, trace in enumerate(result.reasoning_trace, 1):
                st.markdown(f"**Iteration {i}:**")
                st.text(trace[:500] + "..." if len(trace) > 500 else trace)
                st.markdown("---")
        else:
            st.info("No reasoning trace available")
    
    # Tool executions
    with st.expander("🔧 Agent Tool Executions"):
        if result.tool_executions:
            tool_data = []
            for tool_exec in result.tool_executions:
                tool_data.append({
                    'Tool': tool_exec.tool_name,
                    'Success': '✅' if tool_exec.success else '❌',
                    'Time (ms)': f"{tool_exec.execution_time_ms:.2f}" if tool_exec.execution_time_ms else 'N/A'
                })
            df_tools = pd.DataFrame(tool_data)
            st.dataframe(df_tools, use_container_width=True)
        else:
            st.info("No tool executions recorded")
    
    # Download report
    report_json = json.dumps(result.model_dump(), indent=2, default=str)
    st.download_button(
        label="📥 Download Full Report (JSON)",
        data=report_json,
        file_name=f"fraud_report_{result.case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


# ============================================================================
# MAIN APP START
# ============================================================================

# Header
st.markdown('<div class="main-header">💳 Credit Card Fraud Detection AI</div>', unsafe_allow_html=True)
st.markdown("### AI Agent-Powered Fraud Detection System")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/bank-cards.png", width=100)
    st.title("🤖 Fraud Detection Agent")
    
    st.markdown("---")
    
    # System info
    st.markdown("### System Status")
    st.success("✅ Agent Active")
    st.info(f"🤖 Model: {settings.model_name}")
    st.info(f"🔄 Max Iterations: {settings.max_iterations}")
    
    st.markdown("---")
    st.markdown("### About Agent")
    st.markdown("""
    **AI Fraud Detection Agent**
    
    Uses ReACT framework to:
    - 🧠 Reason about fraud patterns
    - 🔧 Use detection tools
    - 👁️ Analyze evidence
    - 📊 Make fraud decisions
    
    **Agent Tools:**
    - Velocity analysis
    - Geographic checks
    - Device fingerprinting
    - Behavioral analysis
    - Risk assessment
    """)
    
    st.markdown("---")
    
    # Statistics in sidebar
    if st.session_state.investigation_history:
        st.markdown("### 📊 Statistics")
        fraud_confirmed = sum(1 for inv in st.session_state.investigation_history 
                            if inv['result'].final_risk_score >= 8)
        avg_score = sum(inv['result'].final_risk_score 
                       for inv in st.session_state.investigation_history) / len(st.session_state.investigation_history)
        
        st.metric("Total Cases", len(st.session_state.investigation_history))
        st.metric("Confirmed Fraud", fraud_confirmed)
        st.metric("Avg Score", f"{avg_score:.1f}/10")

# Main content - Custom Case
st.header("🎯 Custom Fraud Case Investigation")
st.markdown("Create and investigate credit card fraud cases using AI agent")

col1, col2 = st.columns(2)

with col1:
    case_id = st.text_input("Case ID", value=f"CUSTOM_{datetime.now().strftime('%Y%m%d%H%M')}")
    customer_id = st.text_input("Customer ID", value="CUST_001")
    account_id = st.text_input("Account ID", value="ACCT_12345")
    
    fraud_type = st.selectbox(
        "Fraud Type",
        [FraudType.CREDIT_CARD_FRAUD, FraudType.ACCOUNT_TAKEOVER, FraudType.PAYMENT_FRAUD]
    )
    
    total_amount = st.number_input("Total Transaction Amount ($)", min_value=0.0, value=1000.0, step=100.0)

with col2:
    priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
    time_window = st.slider("Time Window (hours)", 1, 72, 24)
    device_id = st.text_input("Device ID", value="DEV_UNKNOWN")
    geolocation = st.text_input("Transaction Location", value="Unknown")
    
    # Fraud indicators
    indicators = st.multiselect(
        "Fraud Indicators",
        [
            FraudIndicator.UNUSUAL_VELOCITY,
            FraudIndicator.GEOGRAPHIC_ANOMALY,
            FraudIndicator.NEW_DEVICE,
            FraudIndicator.BEHAVIORAL_CHANGE,
            FraudIndicator.AMOUNT_ANOMALY
        ]
    )

description = st.text_area(
    "Fraud Description",
    placeholder="Describe the suspicious activity...",
    value="Multiple unauthorized transactions detected"
)

customer_response = st.text_area(
    "Customer Response (optional)",
    placeholder="What does the customer say?"
)

if st.button("🚀 Run Fraud Detection", type="primary"):
    if description:
        # Create custom case
        case = FraudCase(
            case_id=case_id,
            customer_id=customer_id,
            account_id=account_id,
            fraud_type=fraud_type,
            description=description,
            priority=priority,
            total_amount=total_amount if total_amount > 0 else None,
            fraud_indicators=indicators if indicators else [],
            time_window_hours=time_window,
            customer_response=customer_response if customer_response else None,
            device_id=device_id,
            geolocation=geolocation,
            transaction_ids=[]
        )
        
        with st.spinner("🤖 AI Agent investigating..."):
            agent = FraudDetectionAgent()
            result = agent.investigate(case, verbose=False)
            
            st.session_state.fraud_result = result
            st.session_state.investigation_history.append({
                'timestamp': datetime.now(),
                'case_id': result.case_id,
                'result': result
            })
        
        st.success("✅ Investigation Complete!")
        display_fraud_results(result)
    else:
        st.error("Please provide a description")

# Investigation History Section (always shown below)
st.markdown("---")
st.header("📜 Investigation History")

if st.session_state.investigation_history:
    # History table
    history_data = []
    for inv in st.session_state.investigation_history:
        result = inv['result']
        
        # Determine decision emoji
        if result.final_risk_score >= 8:
            decision_icon = "🔴"
            decision_text = "CONFIRMED FRAUD"
        elif result.final_risk_score >= 6:
            decision_icon = "🟠"
            decision_text = "SUSPECTED"
        elif result.final_risk_score >= 4:
            decision_icon = "🟡"
            decision_text = "NEEDS REVIEW"
        else:
            decision_icon = "🟢"
            decision_text = "LEGITIMATE"
        
        history_data.append({
            'Timestamp': inv['timestamp'].strftime('%Y-%m-%d %H:%M'),
            'Case ID': result.case_id,
            'Score': f"{result.final_risk_score:.1f}/10",
            'Decision': f"{decision_icon} {decision_text}",
            'Evidence': len(result.evidence),
            'Duration': f"{result.investigation_duration_seconds:.1f}s"
        })
    
    df = pd.DataFrame(history_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        selected_case = st.selectbox(
            "Select case to view details:",
            [inv['result'].case_id for inv in st.session_state.investigation_history],
            key="history_select"
        )
    
    with col2:
        if st.button("📊 View Details", use_container_width=True):
            for inv in st.session_state.investigation_history:
                if inv['result'].case_id == selected_case:
                    st.markdown("---")
                    display_fraud_results(inv['result'])
                    break
    
    with col3:
        if st.button("🗑️ Clear History", use_container_width=True):
            if st.session_state.investigation_history:
                st.session_state.investigation_history = []
                st.rerun()
else:
    st.info("📊 No investigation history yet. Run a fraud detection above to see results here.")


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>💳 Credit Card Fraud Detection AI v1.0 | Powered by AI Agents & ReACT Framework</p>
    <p>🤖 Autonomous fraud detection with explainable AI</p>
</div>
""", unsafe_allow_html=True)

