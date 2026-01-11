"""
Financial AI Advisor - Streamlit Application

Interactive web interface for personalized financial advice with:
- Real-time advice generation
- Interactive visualizations
- A/B testing framework
- Cost tracking
"""

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment
load_dotenv('.env')

# Page config
st.set_page_config(
    page_title="Financial AI Advisor",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our classes
from src.advisors.cfp_advisor import CFPAdvisor, CFPBasicAdvisor, CFPExpertiseAdvisor
from src.models.client_profile import (
    FinancialScenario,
    ClientProfile,
    IncomeInfo,
    ExpensesInfo,
    DebtInfo,
    AssetsInfo,
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'total_cost' not in st.session_state:
    st.session_state.total_cost = 0.0
if 'total_tokens' not in st.session_state:
    st.session_state.total_tokens = 0
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv('OPENAI_API_KEY', '')

# Helper function for cost estimation
def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate API cost based on token usage."""
    pricing = {
        'gpt-4o-mini': {'input': 0.00015 / 1000, 'output': 0.0006 / 1000},
        'gpt-4o': {'input': 0.005 / 1000, 'output': 0.015 / 1000},
        'gpt-4': {'input': 0.03 / 1000, 'output': 0.06 / 1000},
    }
    rates = pricing.get(model, pricing['gpt-4o-mini'])
    return (input_tokens * rates['input']) + (output_tokens * rates['output'])

# Header
st.markdown('<h1 class="main-header">💰 Financial AI Advisor</h1>', unsafe_allow_html=True)
st.markdown("### Production-Grade AI System for Personal Financial Planning")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key
    api_key = st.text_input(
        "OpenAI API Key",
        value=st.session_state.api_key,
        type="password",
        help="Your OpenAI API key"
    )
    if api_key:
        st.session_state.api_key = api_key
        os.environ['OPENAI_API_KEY'] = api_key
    
    # Model selection
    model = st.selectbox(
        "Model",
        ["gpt-4o-mini", "gpt-4o", "gpt-4"],
        help="Select the OpenAI model to use"
    )
    
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher = more creative, Lower = more focused"
    )
    
    # Advisor persona
    st.header("🎭 Advisor Persona")
    persona_choice = st.selectbox(
        "Select Advisor Type",
        ["CFP Full (Recommended)", "CFP with Expertise", "Basic Advisor"]
    )
    
    persona_map = {
        "CFP Full (Recommended)": CFPAdvisor,
        "CFP with Expertise": CFPExpertiseAdvisor,
        "Basic Advisor": CFPBasicAdvisor
    }
    
    AdvisorClass = persona_map[persona_choice]
    
    # Usage stats
    st.header("📊 Usage Stats")
    st.metric("Total Requests", len(st.session_state.conversation_history))
    st.metric("Total Tokens", f"{st.session_state.total_tokens:,}")
    st.metric("Estimated Cost", f"${st.session_state.total_cost:.4f}")
    
    if st.button("🔄 Reset Stats"):
        st.session_state.conversation_history = []
        st.session_state.total_cost = 0.0
        st.session_state.total_tokens = 0
        st.rerun()

# Main content tabs
tab1, tab2, tab3 = st.tabs([
    "💡 Get Advice",
    "🔬 A/B Test Prompts",
    "📜 Conversation History"
])

# TAB 1: Get Advice
with tab1:
    st.header("Get Personalized Financial Advice")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Personal Information")
        age = st.number_input("Age", min_value=18, max_value=100, value=28)
        
        st.subheader("💵 Income")
        annual_salary = st.number_input("Annual Salary ($)", min_value=0, value=95000, step=1000)
        
        st.subheader("💳 Debts")
        credit_card = st.number_input("Credit Card Debt ($)", min_value=0, value=8000, step=100)
        student_loans = st.number_input("Student Loans ($)", min_value=0, value=0, step=1000)
    
    with col2:
        st.subheader("💰 Assets")
        checking_savings = st.number_input("Checking + Savings ($)", min_value=0, value=2000, step=100)
        retirement_401k = st.number_input("401(k) Balance ($)", min_value=0, value=0, step=1000)
        
        st.subheader("🏠 Monthly Expenses")
        housing = st.number_input("Housing ($)", min_value=0, value=1400, step=50)
        food = st.number_input("Food ($)", min_value=0, value=500, step=50)
        transportation = st.number_input("Transportation ($)", min_value=0, value=400, step=50)
        other_expenses = st.number_input("Other Expenses ($)", min_value=0, value=1900, step=50)
    
    st.subheader("❓ Your Financial Question")
    
    # Quick scenarios
    quick_scenarios = [
        "Custom question...",
        "I received a $15,000 bonus. What should I do with it?",
        "Should I invest in a Roth IRA or Traditional IRA?",
        "How much should I save for retirement?",
        "Should I pay off debt or invest?",
        "How can I build an emergency fund?",
    ]
    
    selected_scenario = st.selectbox("Select a scenario or write your own:", quick_scenarios)
    
    if selected_scenario == "Custom question...":
        question = st.text_area("Your question:", height=100)
    else:
        question = st.text_area("Your question:", value=selected_scenario, height=100)
    
    windfall = st.number_input("Windfall Amount (optional, $)", min_value=0, value=0, step=1000,
                               help="One-time amount like bonus, inheritance, etc.")
    
    if st.button("🚀 Get Financial Advice", type="primary", use_container_width=True):
        if not api_key:
            st.error("⚠️ Please enter your OpenAI API key in the sidebar!")
        elif not question:
            st.error("⚠️ Please enter a financial question!")
        else:
            # Create profile
            profile = ClientProfile(
                age=age,
                income=IncomeInfo(annual_salary=annual_salary),
                expenses=ExpensesInfo(
                    housing=housing,
                    food=food,
                    transportation=transportation,
                    other=other_expenses
                ),
                debts=DebtInfo(
                    credit_card=credit_card,
                    student_loan=student_loans
                ),
                assets=AssetsInfo(
                    checking_savings=checking_savings,
                    retirement_401k=retirement_401k
                )
            )
            
            scenario = FinancialScenario(
                client_profile=profile,
                windfall_amount=windfall if windfall > 0 else None,
                question=question
            )
            
            # Get advice
            with st.spinner("🤔 Analyzing your financial situation..."):
                try:
                    advisor = AdvisorClass(
                        model=model,
                        temperature=temperature,
                        api_key=api_key
                    )
                    
                    advice = advisor.provide_advice(scenario)
                    
                    # Estimate cost (approximate)
                    est_input_tokens = len(question.split()) * 1.3
                    est_output_tokens = len(advice.summary.split()) * 1.3
                    cost = estimate_cost(model, est_input_tokens, est_output_tokens)
                    
                    st.session_state.total_cost += cost
                    st.session_state.total_tokens += int(est_input_tokens + est_output_tokens)
                    st.session_state.conversation_history.append({
                        'timestamp': datetime.now(),
                        'question': question,
                        'advice': advice.summary,
                        'persona': advice.persona,
                        'model': advice.model_used,
                        'cost': cost
                    })
                    
                    # Display results
                    st.success("✅ Financial advice generated!")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Model", advice.model_used)
                    with col2:
                        st.metric("Persona", advice.persona)
                    with col3:
                        st.metric("Est. Cost", f"${cost:.4f}")
                    
                    st.markdown("---")
                    st.markdown(advice.summary)
                    
                    # Download button
                    st.download_button(
                        "📄 Download Advice as Text",
                        data=advice.summary,
                        file_name=f"financial_advice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Make sure your API key is valid and you have available credits.")

# TAB 2: A/B Testing
with tab2:
    st.header("🔬 A/B Test Different Prompts")
    st.markdown("Compare how different advisor personas handle the same scenario")
    
    st.subheader("Test Scenario")
    test_question = st.text_area(
        "Financial Question:",
        value="I have $10,000 to invest. Should I put it in stocks, bonds, or a high-yield savings account?",
        height=100
    )
    
    # Simple test profile
    test_profile = ClientProfile(
        age=30,
        income=IncomeInfo(annual_salary=80000),
        expenses=ExpensesInfo(housing=1500, food=500, transportation=300, other=1500),
        debts=DebtInfo(credit_card=3000),
        assets=AssetsInfo(checking_savings=10000)
    )
    
    if st.button("🧪 Run A/B Test", use_container_width=True):
        if not api_key:
            st.error("⚠️ Please enter your OpenAI API key in the sidebar!")
        else:
            scenario = FinancialScenario(
                client_profile=test_profile,
                question=test_question
            )
            
            personas = [
                ("Basic Advisor", CFPBasicAdvisor),
                ("CFP with Expertise", CFPExpertiseAdvisor),
                ("CFP Full", CFPAdvisor)
            ]
            
            results = []
            
            progress_bar = st.progress(0)
            
            for idx, (name, AdvisorClass) in enumerate(personas):
                with st.spinner(f"Testing {name}..."):
                    try:
                        advisor = AdvisorClass(
                            model=model,
                            temperature=temperature,
                            api_key=api_key
                        )
                        
                        advice = advisor.provide_advice(scenario)
                        
                        results.append({
                            'persona': name,
                            'advice': advice.summary,
                            'length': len(advice.summary),
                            'word_count': len(advice.summary.split())
                        })
                        
                    except Exception as e:
                        st.error(f"Error with {name}: {str(e)}")
                
                progress_bar.progress((idx + 1) / len(personas))
            
            # Display comparison
            st.success("✅ A/B Test Complete!")
            
            # Metrics comparison
            df_metrics = pd.DataFrame([
                {
                    'Persona': r['persona'],
                    'Word Count': r['word_count'],
                    'Character Length': r['length']
                }
                for r in results
            ])
            
            st.dataframe(df_metrics, use_container_width=True)
            
            # Side-by-side comparison
            st.subheader("Response Comparison")
            
            cols = st.columns(len(results))
            for idx, result in enumerate(results):
                with cols[idx]:
                    st.markdown(f"### {result['persona']}")
                    st.markdown(result['advice'])

# TAB 3: History
with tab3:
    st.header("📜 Conversation History")
    
    if not st.session_state.conversation_history:
        st.info("No conversations yet. Get some advice in the first tab!")
    else:
        for idx, conv in enumerate(reversed(st.session_state.conversation_history)):
            with st.expander(
                f"💬 {conv['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - {conv['question'][:50]}...",
                expanded=(idx == 0)
            ):
                st.markdown(f"**Model:** {conv['model']} | **Persona:** {conv['persona']} | **Cost:** ${conv['cost']:.4f}")
                st.markdown("**Question:**")
                st.markdown(conv['question'])
                st.markdown("**Advice:**")
                st.markdown(conv['advice'])
                
                st.download_button(
                    "📄 Download",
                    data=conv['advice'],
                    file_name=f"advice_{idx}.txt",
                    key=f"download_{idx}"
                )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>💰 Financial AI Advisor | Built with OpenAI GPT & Streamlit</p>
    <p>Showcasing: Role-based Prompting, Interactive UI, Real-time Advice, A/B Testing</p>
</div>
""", unsafe_allow_html=True)
