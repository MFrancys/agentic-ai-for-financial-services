"""Client profile and financial scenario data models."""

from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class LifeStage(str, Enum):
    """Client life stage categories."""
    YOUNG_PROFESSIONAL = "young_professional"  # 20s-30s
    GROWING_FAMILY = "growing_family"  # 30s-40s
    MID_CAREER = "mid_career"  # 40s-50s
    PRE_RETIREMENT = "pre_retirement"  # 50s-60s
    RETIRED = "retired"  # 60s+


class FinancialGoal(str, Enum):
    """Common financial goals."""
    DEBT_PAYOFF = "debt_payoff"
    EMERGENCY_FUND = "emergency_fund"
    HOME_PURCHASE = "home_purchase"
    RETIREMENT_PLANNING = "retirement_planning"
    INVESTMENT_GROWTH = "investment_growth"
    COLLEGE_SAVINGS = "college_savings"
    WEALTH_PRESERVATION = "wealth_preservation"


class DebtInfo(BaseModel):
    """Debt information."""
    credit_card: float = Field(default=0, ge=0, description="Credit card debt")
    student_loan: float = Field(default=0, ge=0, description="Student loan debt")
    auto_loan: float = Field(default=0, ge=0, description="Auto loan debt")
    mortgage: float = Field(default=0, ge=0, description="Mortgage debt")
    other: float = Field(default=0, ge=0, description="Other debt")
    
    @property
    def total(self) -> float:
        """Calculate total debt."""
        return (
            self.credit_card +
            self.student_loan +
            self.auto_loan +
            self.mortgage +
            self.other
        )


class AssetsInfo(BaseModel):
    """Asset information."""
    checking_savings: float = Field(default=0, ge=0, description="Checking/savings")
    retirement_401k: float = Field(default=0, ge=0, description="401(k) balance")
    retirement_ira: float = Field(default=0, ge=0, description="IRA balance")
    brokerage: float = Field(default=0, ge=0, description="Brokerage account")
    home_equity: float = Field(default=0, ge=0, description="Home equity")
    other_investments: float = Field(default=0, ge=0, description="Other investments")
    
    @property
    def total(self) -> float:
        """Calculate total assets."""
        return (
            self.checking_savings +
            self.retirement_401k +
            self.retirement_ira +
            self.brokerage +
            self.home_equity +
            self.other_investments
        )
    
    @property
    def liquid_assets(self) -> float:
        """Calculate liquid assets."""
        return (
            self.checking_savings +
            self.brokerage
        )


class IncomeInfo(BaseModel):
    """Income information."""
    annual_salary: float = Field(..., gt=0, description="Annual salary")
    bonus: float = Field(default=0, ge=0, description="Annual bonus")
    side_income: float = Field(default=0, ge=0, description="Side income")
    investment_income: float = Field(default=0, ge=0, description="Investment income")
    
    @property
    def total_annual(self) -> float:
        """Calculate total annual income."""
        return (
            self.annual_salary +
            self.bonus +
            self.side_income +
            self.investment_income
        )


class ExpensesInfo(BaseModel):
    """Monthly expenses information."""
    housing: float = Field(..., ge=0, description="Housing costs (rent/mortgage)")
    utilities: float = Field(default=0, ge=0, description="Utilities")
    food: float = Field(default=0, ge=0, description="Food and groceries")
    transportation: float = Field(default=0, ge=0, description="Transportation")
    insurance: float = Field(default=0, ge=0, description="Insurance premiums")
    debt_payments: float = Field(default=0, ge=0, description="Minimum debt payments")
    discretionary: float = Field(default=0, ge=0, description="Discretionary spending")
    other: float = Field(default=0, ge=0, description="Other expenses")
    
    @property
    def total_monthly(self) -> float:
        """Calculate total monthly expenses."""
        return (
            self.housing +
            self.utilities +
            self.food +
            self.transportation +
            self.insurance +
            self.debt_payments +
            self.discretionary +
            self.other
        )


class ClientProfile(BaseModel):
    """Complete client financial profile."""
    
    # Demographics
    client_id: Optional[str] = Field(default=None, description="Client identifier")
    age: int = Field(..., ge=18, le=120, description="Client age")
    marital_status: Optional[str] = Field(default=None, description="Marital status")
    dependents: int = Field(default=0, ge=0, description="Number of dependents")
    location: Optional[str] = Field(default=None, description="Location (for tax context)")
    
    # Financial Information
    income: IncomeInfo = Field(..., description="Income information")
    expenses: ExpensesInfo = Field(..., description="Monthly expenses")
    assets: AssetsInfo = Field(default_factory=AssetsInfo, description="Assets")
    debts: DebtInfo = Field(default_factory=DebtInfo, description="Debts")
    
    # Goals & Context
    life_stage: Optional[LifeStage] = Field(default=None, description="Life stage")
    primary_goals: List[FinancialGoal] = Field(default_factory=list, description="Primary goals")
    risk_tolerance: Optional[str] = Field(default=None, description="Risk tolerance (low/medium/high)")
    
    # Employment
    employer_401k_match: Optional[float] = Field(default=None, ge=0, le=100, description="401(k) match %")
    job_stability: Optional[str] = Field(default=None, description="Job stability assessment")
    
    # Additional Context
    special_circumstances: Optional[str] = Field(default=None, description="Special circumstances")
    
    @property
    def net_worth(self) -> float:
        """Calculate net worth."""
        return self.assets.total - self.debts.total
    
    @property
    def monthly_cash_flow(self) -> float:
        """Calculate monthly cash flow."""
        monthly_income = self.income.total_annual / 12
        return monthly_income - self.expenses.total_monthly
    
    @property
    def emergency_fund_months(self) -> float:
        """Calculate emergency fund coverage in months."""
        if self.expenses.total_monthly == 0:
            return 0
        return self.assets.checking_savings / self.expenses.total_monthly
    
    def infer_life_stage(self) -> LifeStage:
        """Infer life stage from age and dependents."""
        if self.life_stage:
            return self.life_stage
            
        if self.age < 35:
            return LifeStage.YOUNG_PROFESSIONAL
        elif self.age < 45:
            return LifeStage.GROWING_FAMILY if self.dependents > 0 else LifeStage.MID_CAREER
        elif self.age < 55:
            return LifeStage.MID_CAREER
        elif self.age < 65:
            return LifeStage.PRE_RETIREMENT
        else:
            return LifeStage.RETIRED


class FinancialScenario(BaseModel):
    """A specific financial question or scenario."""
    
    client_profile: ClientProfile = Field(..., description="Client financial profile")
    question: str = Field(..., min_length=10, description="Client's question")
    context: Optional[str] = Field(default=None, description="Additional context")
    urgency: Optional[str] = Field(default="normal", description="Urgency level")
    
    # For specific scenarios
    windfall_amount: Optional[float] = Field(default=None, description="Windfall/bonus amount")
    major_purchase_amount: Optional[float] = Field(default=None, description="Major purchase amount")
    life_event: Optional[str] = Field(default=None, description="Life event (marriage, baby, etc.)")

