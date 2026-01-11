"""Example: Young Professional with Bonus (from notebook)."""

import os
from dotenv import load_dotenv

from src.advisors.cfp_advisor import CFPAdvisor, CFPBasicAdvisor, CFPExpertiseAdvisor
from src.models.client_profile import (
    FinancialScenario,
    ClientProfile,
    IncomeInfo,
    ExpensesInfo,
    DebtInfo,
    AssetsInfo,
    FinancialGoal,
)

# Load environment
load_dotenv()


def create_alex_scenario():
    """Create Alex Chen scenario from notebook."""
    
    # Create client profile
    profile = ClientProfile(
        client_id="ALEX001",
        age=28,
        
        # Income
        income=IncomeInfo(
            annual_salary=95000,
            bonus=0,  # Just received, will add as windfall
        ),
        
        # Expenses
        expenses=ExpensesInfo(
            housing=1400,
            utilities=150,
            food=500,
            transportation=400,
            insurance=200,
            debt_payments=500,
            discretionary=700,
            other=350,
        ),
        
        # Debts
        debts=DebtInfo(
            credit_card=8000,  # 18% APR
            student_loan=25000,  # 5.2% APR
        ),
        
        # Assets
        assets=AssetsInfo(
            checking_savings=2000,
            retirement_401k=0,  # Contributing 6%
        ),
        
        # Employment
        employer_401k_match=4.0,  # Company matches 4%
        job_stability="stable",
        
        # Goals
        primary_goals=[
            FinancialGoal.DEBT_PAYOFF,
            FinancialGoal.EMERGENCY_FUND,
            FinancialGoal.INVESTMENT_GROWTH,
            FinancialGoal.HOME_PURCHASE,
        ],
    )
    
    # Create scenario
    scenario = FinancialScenario(
        client_profile=profile,
        windfall_amount=15000,  # After-tax bonus
        question="""I just got this bonus and I'm not sure what to do with it. 
I know I should pay off debt, but I also want to start investing and build up 
my emergency fund. What would you recommend as the best use of this money?""",
        context="""
Additional Context:
- Alex is financially responsible but new to investing
- Job is stable with good growth prospects
- Lives in a moderate cost-of-living area
- Plans to buy a house in 3-5 years
        """,
    )
    
    return scenario


def main():
    """Run example with multiple personas."""
    
    # Create scenario
    scenario = create_alex_scenario()
    
    # Print scenario
    print("="*80)
    print("CLIENT SCENARIO: Young Professional with Bonus")
    print("="*80)
    print(f"\nAge: {scenario.client_profile.age}")
    print(f"Income: ${scenario.client_profile.income.annual_salary:,.0f}")
    print(f"Bonus Received: ${scenario.windfall_amount:,.0f}")
    print(f"Credit Card Debt: ${scenario.client_profile.debts.credit_card:,.0f}")
    print(f"Student Loan: ${scenario.client_profile.debts.student_loan:,.0f}")
    print(f"Emergency Fund: ${scenario.client_profile.assets.checking_savings:,.0f}")
    print(f"\nQuestion: {scenario.question}")
    print("="*80)
    
    # Test different personas
    personas = [
        ("Basic Advisor", CFPBasicAdvisor),
        ("CFP with Expertise", CFPExpertiseAdvisor),
        ("CFP Full (with Style)", CFPAdvisor),
    ]
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  OPENAI_API_KEY not found in environment!")
        print("Set it in .env file or environment variables to run this example.")
        return
    
    for persona_name, AdvisorClass in personas:
        print(f"\n{'='*80}")
        print(f"RESPONSE FROM: {persona_name}")
        print(f"{'='*80}\n")
        
        # Create advisor
        advisor = AdvisorClass(
            model="gpt-4o-mini",  # Use mini for cost-effective demo
            temperature=0.7,
            api_key=api_key,
        )
        
        # Get advice
        try:
            advice = advisor.provide_advice(scenario)
            print(advice.summary)
            print(f"\n[Model: {advice.model_used}, Persona: {advice.persona}]")
        except Exception as e:
            print(f"Error: {e}")
        
        print("\n")


if __name__ == "__main__":
    main()

