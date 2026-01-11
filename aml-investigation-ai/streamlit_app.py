"""
AML Investigation AI - Streamlit Web Application

Interactive web interface for conducting financial crime investigations.
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

from src.models.investigation_case import InvestigationCase, AlertType
from src.investigators.react_investigator import ReACTInvestigator
from src.tools.transaction_tools import get_transaction_history, analyze_transaction_patterns
from src.tools.customer_tools import get_customer_profile, assess_customer_risk
from src.config import settings

# Page configuration
st.set_page_config(
    page_title="AML Investigation AI",
    page_icon="🔍",
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
        color: #1f77b4;
        padding: 1rem 0;
    }
    .risk-critical {
        background-color: #ff4444;
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .risk-high {
        background-color: #ff8800;
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .risk-medium {
        background-color: #ffbb33;
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .risk-low {
        background-color: #00C851;
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'investigation_result' not in st.session_state:
    st.session_state.investigation_result = None
if 'investigation_history' not in st.session_state:
    st.session_state.investigation_history = []

# Header
st.markdown('<div class="main-header">🔍 AML Investigation AI</div>', unsafe_allow_html=True)
st.markdown("### AI-Powered Anti-Money Laundering Investigation System")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/bank-building.png", width=100)
    st.title("Investigation Console")
    
    # Mode selection
    mode = st.radio(
        "Select Mode",
        ["Quick Investigation", "Custom Investigation", "View Data", "Investigation History"],
        help="Choose how you want to use the system"
    )
    
    st.markdown("---")
    
    # System info
    st.markdown("### System Status")
    st.success("✅ API Connected")
    st.info(f"🤖 Model: {settings.model_name}")
    st.info(f"🔄 Max Iterations: {settings.max_iterations}")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This system uses the **ReACT framework** to conduct 
    intelligent financial crime investigations.
    
    - Evidence-based decisions
    - Real tool integration
    - Automated SAR recommendations
    """)

# Main content area
if mode == "Quick Investigation":
    st.header("🚀 Quick Investigation")
    st.markdown("Select a predefined case or create a custom investigation")
    
    # Predefined cases
    predefined_cases = {
        "Cash Structuring - Restaurant Owner": {
            "case_id": "QUICK_001",
            "customer_id": "CUST_001",
            "account_id": "high_risk_account_001",
            "alert_type": AlertType.CASH_STRUCTURING,
            "description": "Multiple cash deposits just under $10,000 in 5 consecutive days",
            "priority": "high",
            "time_period_days": 14,
            "customer_explanation": "Restaurant business doing really well lately",
            "alert_source": "Branch manager notification"
        },
        "Wire Transfers - Import/Export Business": {
            "case_id": "QUICK_002",
            "customer_id": "CUST_002",
            "account_id": "business_account_002",
            "alert_type": AlertType.WIRE_TRANSFER,
            "description": "Multiple international wire transfers to/from high-risk countries",
            "priority": "high",
            "amount": 135000.0,
            "time_period_days": 30,
            "customer_explanation": "Normal import/export business transactions",
            "alert_source": "Automated monitoring system"
        },
        "Normal Activity - Software Engineer": {
            "case_id": "QUICK_003",
            "customer_id": "CUST_003",
            "account_id": "normal_account",
            "alert_type": AlertType.UNUSUAL_ACTIVITY,
            "description": "Standard account activity - control case",
            "priority": "low",
            "time_period_days": 30,
            "customer_explanation": "Regular salary deposits and normal expenses",
            "alert_source": "Routine review"
        }
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_case = st.selectbox(
            "Select Investigation Case",
            list(predefined_cases.keys())
        )
        
        case_data = predefined_cases[selected_case]
        
        # Display case details
        st.markdown("#### Case Details")
        details_col1, details_col2 = st.columns(2)
        
        with details_col1:
            st.info(f"**Customer ID:** {case_data['customer_id']}")
            st.info(f"**Account ID:** {case_data['account_id']}")
            st.info(f"**Alert Type:** {case_data['alert_type'].value}")
        
        with details_col2:
            st.info(f"**Priority:** {case_data['priority'].upper()}")
            st.info(f"**Time Period:** {case_data['time_period_days']} days")
            st.info(f"**Source:** {case_data['alert_source']}")
        
        st.markdown(f"**Description:** {case_data['description']}")
        st.markdown(f"**Customer Says:** *\"{case_data['customer_explanation']}\"*")
    
    with col2:
        st.markdown("#### Quick Actions")
        
        if st.button("🔍 Start Investigation", type="primary", use_container_width=True):
            # Create investigation case
            case = InvestigationCase(**case_data)
            
            # Progress indicators
            with st.spinner("🤖 AI Investigator analyzing the case..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Create investigator
                investigator = ReACTInvestigator()
                
                status_text.text("Gathering evidence...")
                progress_bar.progress(25)
                
                status_text.text("Analyzing patterns...")
                progress_bar.progress(50)
                
                status_text.text("Evaluating risk...")
                progress_bar.progress(75)
                
                # Run investigation
                result = investigator.investigate(case, verbose=False)
                
                status_text.text("Investigation complete!")
                progress_bar.progress(100)
                
                # Store result
                st.session_state.investigation_result = result
                st.session_state.investigation_history.append({
                    'timestamp': datetime.now(),
                    'case_id': result.case_id,
                    'result': result
                })
                
            st.success("✅ Investigation Complete!")
            st.balloons()
    
    # Display results if available
    if st.session_state.investigation_result:
        st.markdown("---")
        display_investigation_results(st.session_state.investigation_result)

elif mode == "Custom Investigation":
    st.header("🎯 Custom Investigation")
    st.markdown("Create a custom investigation case")
    
    col1, col2 = st.columns(2)
    
    with col1:
        case_id = st.text_input("Case ID", value=f"CUSTOM_{datetime.now().strftime('%Y%m%d%H%M')}")
        customer_id = st.selectbox("Customer ID", ["CUST_001", "CUST_002", "CUST_003", "Other"])
        if customer_id == "Other":
            customer_id = st.text_input("Enter Customer ID")
        
        account_id = st.selectbox(
            "Account ID", 
            ["high_risk_account_001", "business_account_002", "normal_account", "Other"]
        )
        if account_id == "Other":
            account_id = st.text_input("Enter Account ID")
        
        alert_type = st.selectbox(
            "Alert Type",
            [t.value for t in AlertType]
        )
    
    with col2:
        priority = st.selectbox("Priority", ["low", "medium", "high", "critical"])
        time_period_days = st.slider("Time Period (days)", 1, 90, 30)
        amount = st.number_input("Amount (if applicable)", min_value=0.0, value=0.0, step=1000.0)
        alert_source = st.text_input("Alert Source", value="Manual investigation")
    
    description = st.text_area(
        "Description of Suspicious Activity",
        placeholder="Describe the suspicious activity in detail..."
    )
    
    customer_explanation = st.text_area(
        "Customer Explanation",
        placeholder="What does the customer say about this activity?"
    )
    
    if st.button("🚀 Run Custom Investigation", type="primary"):
        if description:
            # Create custom case
            case = InvestigationCase(
                case_id=case_id,
                customer_id=customer_id,
                account_id=account_id,
                alert_type=AlertType(alert_type),
                description=description,
                priority=priority,
                time_period_days=time_period_days,
                amount=amount if amount > 0 else None,
                customer_explanation=customer_explanation if customer_explanation else None,
                alert_source=alert_source
            )
            
            with st.spinner("🤖 Running investigation..."):
                investigator = ReACTInvestigator()
                result = investigator.investigate(case, verbose=False)
                
                st.session_state.investigation_result = result
                st.session_state.investigation_history.append({
                    'timestamp': datetime.now(),
                    'case_id': result.case_id,
                    'result': result
                })
            
            st.success("✅ Investigation Complete!")
            display_investigation_results(result)
        else:
            st.error("Please provide a description of the suspicious activity")

elif mode == "View Data":
    st.header("📊 Data Explorer")
    
    data_type = st.radio(
        "Select Data Type",
        ["Customer Profiles", "Transaction History", "Risk Analysis"]
    )
    
    if data_type == "Customer Profiles":
        st.subheader("Customer Profiles")
        
        customer_id = st.selectbox("Select Customer", ["CUST_001", "CUST_002", "CUST_003"])
        
        if st.button("Load Profile"):
            profile = get_customer_profile(customer_id)
            
            if "error" not in profile:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Risk Score", f"{profile['risk_score']}/10")
                with col2:
                    st.metric("Account Age", f"{profile['account_age_years']} years")
                with col3:
                    st.metric("Previous SARs", profile['previous_sars'])
                
                st.json(profile)
            else:
                st.error(profile['error'])
    
    elif data_type == "Transaction History":
        st.subheader("Transaction History")
        
        col1, col2 = st.columns(2)
        with col1:
            account_id = st.selectbox(
                "Account ID",
                ["high_risk_account_001", "business_account_002", "normal_account"]
            )
        with col2:
            days = st.slider("Days", 1, 90, 30)
        
        if st.button("Load Transactions"):
            history = get_transaction_history(account_id, days)
            
            if "error" not in history:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Transactions", history['transaction_count'])
                with col2:
                    st.metric("Total Amount", f"${history['total_amount']:,.2f}")
                with col3:
                    st.metric("Cash Deposits", history.get('cash_deposit_count', 0))
                with col4:
                    st.metric("Avg Amount", f"${history.get('avg_transaction_amount', 0):,.2f}")
                
                # Transaction table
                if history['transactions']:
                    df = pd.DataFrame(history['transactions'])
                    st.dataframe(df, use_container_width=True)
                    
                    # Visualization
                    if len(df) > 0:
                        fig = px.bar(df, x='date', y='amount', color='type',
                                   title='Transaction Timeline')
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(history['error'])
    
    elif data_type == "Risk Analysis":
        st.subheader("Pattern Analysis")
        
        col1, col2 = st.columns(2)
        with col1:
            account_id = st.selectbox(
                "Account ID",
                ["high_risk_account_001", "business_account_002", "normal_account"]
            )
        with col2:
            days = st.slider("Analysis Period (days)", 1, 90, 30)
        
        if st.button("Analyze Patterns"):
            patterns = analyze_transaction_patterns(account_id, days)
            
            if "error" not in patterns:
                # Risk level
                risk_level = patterns.get('overall_risk', 'unknown')
                risk_colors = {'low': 'green', 'medium': 'orange', 'high': 'red', 'critical': 'darkred'}
                
                st.markdown(f"### Overall Risk: :{risk_colors.get(risk_level, 'gray')}[{risk_level.upper()}]")
                
                # Patterns detected
                if patterns['patterns_detected']:
                    st.markdown("#### Patterns Detected")
                    for pattern in patterns['patterns_detected']:
                        severity_emoji = {
                            'critical': '🔴',
                            'high': '🟠', 
                            'medium': '🟡',
                            'low': '🟢'
                        }.get(pattern['severity'], '⚪')
                        
                        st.markdown(f"{severity_emoji} **{pattern['pattern']}**: {pattern['description']}")
                
                # Risk indicators
                if patterns['risk_indicators']:
                    st.markdown("#### Risk Indicators")
                    for indicator in patterns['risk_indicators']:
                        st.warning(indicator)
            else:
                st.error(patterns['error'])

elif mode == "Investigation History":
    st.header("📜 Investigation History")
    
    if st.session_state.investigation_history:
        st.markdown(f"**Total Investigations:** {len(st.session_state.investigation_history)}")
        
        # Summary statistics
        sar_count = sum(1 for inv in st.session_state.investigation_history 
                       if inv['result'].sar_required)
        avg_risk = sum(inv['result'].final_risk_score 
                      for inv in st.session_state.investigation_history) / len(st.session_state.investigation_history)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Cases", len(st.session_state.investigation_history))
        with col2:
            st.metric("SARs Required", sar_count)
        with col3:
            st.metric("Avg Risk Score", f"{avg_risk:.1f}/10")
        
        st.markdown("---")
        
        # History table
        history_data = []
        for inv in st.session_state.investigation_history:
            result = inv['result']
            history_data.append({
                'Timestamp': inv['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'Case ID': result.case_id,
                'Risk Score': f"{result.final_risk_score:.1f}",
                'SAR Required': '✅' if result.sar_required else '❌',
                'Duration': f"{result.investigation_duration_seconds:.2f}s"
            })
        
        df = pd.DataFrame(history_data)
        st.dataframe(df, use_container_width=True)
        
        # Select case to view details
        selected_case = st.selectbox(
            "View Details",
            [inv['result'].case_id for inv in st.session_state.investigation_history]
        )
        
        if st.button("Show Details"):
            for inv in st.session_state.investigation_history:
                if inv['result'].case_id == selected_case:
                    display_investigation_results(inv['result'])
                    break
        
        if st.button("Clear History", type="secondary"):
            st.session_state.investigation_history = []
            st.rerun()
    else:
        st.info("No investigations yet. Run an investigation to see history.")


def display_investigation_results(result):
    """Display investigation results in a nice format."""
    
    st.markdown("## 📊 Investigation Results")
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_score = result.final_risk_score
        risk_color = "🔴" if risk_score >= 8 else "🟠" if risk_score >= 6 else "🟡" if risk_score >= 4 else "🟢"
        st.metric("Risk Score", f"{risk_color} {risk_score}/10")
    
    with col2:
        sar_status = "⚠️ YES" if result.sar_required else "✅ NO"
        st.metric("SAR Required", sar_status)
    
    with col3:
        st.metric("Evidence Items", len(result.evidence))
    
    with col4:
        st.metric("Duration", f"{result.investigation_duration_seconds:.2f}s")
    
    # Risk gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=result.final_risk_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Risk Level"},
        gauge={
            'axis': {'range': [None, 10]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 4], 'color': "lightgreen"},
                {'range': [4, 6], 'color': "yellow"},
                {'range': [6, 8], 'color': "orange"},
                {'range': [8, 10], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 7
            }
        }
    ))
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendation
    st.markdown("### 🎯 Recommendation")
    if result.sar_required:
        st.error(f"**{result.recommendation}**")
        if result.sar_reasoning:
            with st.expander("SAR Filing Reasoning"):
                st.markdown(result.sar_reasoning)
    else:
        st.success(f"**{result.recommendation}**")
    
    # Key Findings
    if result.key_findings:
        st.markdown("### 🔍 Key Findings")
        for i, finding in enumerate(result.key_findings, 1):
            st.markdown(f"{i}. {finding}")
    
    # Evidence
    if result.evidence:
        st.markdown("### 📋 Evidence Collected")
        
        evidence_data = []
        for ev in result.evidence:
            evidence_data.append({
                'Type': ev.evidence_type,
                'Severity': ev.severity,
                'Description': ev.description[:100] + '...' if len(ev.description) > 100 else ev.description,
                'Source': ev.source
            })
        
        df = pd.DataFrame(evidence_data)
        st.dataframe(df, use_container_width=True)
        
        # Evidence by severity
        severity_counts = df['Severity'].value_counts()
        fig = px.pie(values=severity_counts.values, names=severity_counts.index,
                    title='Evidence by Severity')
        st.plotly_chart(fig, use_container_width=True)
    
    # Next Steps
    if result.next_steps:
        st.markdown("### ✅ Next Steps")
        for step in result.next_steps:
            st.markdown(f"- {step}")
    
    # Tool Executions
    with st.expander("🔧 Tool Executions"):
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
    
    # Reasoning Trace
    with st.expander("🧠 Reasoning Trace"):
        if result.reasoning_trace:
            for i, trace in enumerate(result.reasoning_trace, 1):
                st.markdown(f"**Iteration {i}:**")
                st.text(trace[:500] + "..." if len(trace) > 500 else trace)
                st.markdown("---")
        else:
            st.info("No reasoning trace available")
    
    # Download button for full report
    report_json = json.dumps(result.model_dump(), indent=2, default=str)
    st.download_button(
        label="📥 Download Full Report (JSON)",
        data=report_json,
        file_name=f"investigation_{result.case_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>AML Investigation AI v1.0 | Powered by ReACT Framework & OpenAI</p>
    <p>⚠️ For demonstration purposes only. Human review required for all SAR filings.</p>
</div>
""", unsafe_allow_html=True)

