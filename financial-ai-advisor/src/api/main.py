"""FastAPI application for Financial AI Advisor."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.advisors.cfp_advisor import CFPAdvisor
from src.models.client_profile import FinancialScenario, ClientProfile, IncomeInfo, ExpensesInfo
from src.models.advice_response import AdvisorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    print("🚀 Financial AI Advisor API starting...")
    
    # Initialize advisors
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("⚠️  Warning: No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
    
    app.state.cfp_advisor = CFPAdvisor(
        model=os.getenv("LLM_MODEL", "gpt-4"),
        api_key=api_key,
    )
    
    print("✅ Financial AI Advisor API ready!")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")


app = FastAPI(
    title="Financial AI Advisor",
    description="Production-grade financial advisory AI system with role-based prompting",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Financial AI Advisor",
        "version": "1.0.0",
    }


# Simple advice request
class SimpleAdviceRequest(BaseModel):
    """Simple advice request for quick testing."""
    question: str
    age: int
    annual_income: float
    monthly_expenses: float
    debt: float = 0
    savings: float = 0


@app.post("/api/v1/advice/simple", response_model=AdvisorResponse)
async def get_simple_advice(request: SimpleAdviceRequest):
    """
    Get financial advice with simple inputs.
    
    Perfect for quick testing without complex profile setup.
    """
    # Create scenario from simple inputs
    profile = ClientProfile(
        age=request.age,
        income=IncomeInfo(annual_salary=request.annual_income),
        expenses=ExpensesInfo(
            housing=request.monthly_expenses * 0.3,
            food=request.monthly_expenses * 0.15,
            transportation=request.monthly_expenses * 0.15,
            other=request.monthly_expenses * 0.4,
        ),
    )
    
    # Add debt if provided
    if request.debt > 0:
        from src.models.client_profile import DebtInfo
        profile.debts = DebtInfo(credit_card=request.debt)
    
    # Add savings if provided
    if request.savings > 0:
        from src.models.client_profile import AssetsInfo
        profile.assets = AssetsInfo(checking_savings=request.savings)
    
    scenario = FinancialScenario(
        client_profile=profile,
        question=request.question,
    )
    
    # Get advice
    try:
        advice = app.state.cfp_advisor.provide_advice(scenario)
        return advice
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/advice", response_model=AdvisorResponse)
async def get_financial_advice(scenario: FinancialScenario):
    """
    Get comprehensive financial advice.
    
    Accepts complete financial scenario with full client profile.
    """
    try:
        advice = app.state.cfp_advisor.provide_advice(scenario)
        return advice
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Example scenarios endpoint
@app.get("/api/v1/examples")
async def get_example_scenarios():
    """Get example scenarios for testing."""
    return {
        "young_professional_with_bonus": {
            "description": "28-year-old with $15k bonus, credit card debt, and student loans",
            "scenario": {
                "age": 28,
                "annual_income": 95000,
                "monthly_expenses": 4200,
                "credit_card_debt": 8000,
                "student_loan": 25000,
                "savings": 2000,
                "bonus": 15000,
                "question": "I just received a $15,000 bonus. How should I use it?",
            },
        },
        "family_planning": {
            "description": "32-year-olds expecting first child",
            "scenario": {
                "age": 32,
                "household_income": 140000,
                "monthly_expenses": 4500,
                "savings": 8000,
                "expecting_child": True,
                "question": "We're expecting our first child. How should we prepare financially?",
            },
        },
        "retirement_planning": {
            "description": "45-year-old worried about retirement readiness",
            "scenario": {
                "age": 45,
                "income": 125000,
                "retirement_401k": 350000,
                "monthly_expenses": 6500,
                "question": "Am I on track for retirement at 62?",
            },
        },
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

