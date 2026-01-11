"""Tests for CFP Advisor."""

import pytest
from unittest.mock import Mock, patch

from src.advisors.cfp_advisor import CFPAdvisor
from src.models.client_profile import (
    FinancialScenario,
    ClientProfile,
    IncomeInfo,
    ExpensesInfo,
    DebtInfo,
    AssetsInfo,
)


@pytest.fixture
def sample_profile():
    """Create a sample client profile for testing."""
    return ClientProfile(
        age=28,
        income=IncomeInfo(annual_salary=95000),
        expenses=ExpensesInfo(
            housing=1400,
            food=500,
            transportation=400,
            other=1900,
        ),
        debts=DebtInfo(
            credit_card=8000,
            student_loan=25000,
        ),
        assets=AssetsInfo(
            checking_savings=2000,
        ),
        employer_401k_match=4.0,
    )


@pytest.fixture
def sample_scenario(sample_profile):
    """Create a sample scenario."""
    return FinancialScenario(
        client_profile=sample_profile,
        windfall_amount=15000,
        question="I just received a $15,000 bonus. What should I do with it?",
    )


class TestCFPAdvisor:
    """Test CFP Advisor functionality."""
    
    def test_initialization(self):
        """Test advisor initializes correctly."""
        advisor = CFPAdvisor(model="gpt-4", api_key="test-key")
        
        assert advisor.model == "gpt-4"
        assert advisor.provider == "openai"
        assert advisor.get_persona_name() == "Certified Financial Planner (CFP)"
    
    def test_system_prompt_not_empty(self):
        """Test system prompt is defined."""
        advisor = CFPAdvisor(api_key="test-key")
        prompt = advisor.get_system_prompt()
        
        assert len(prompt) > 100
        assert "CFP" in prompt or "Certified Financial Planner" in prompt
    
    def test_user_prompt_generation(self, sample_scenario):
        """Test user prompt generation from scenario."""
        advisor = CFPAdvisor(api_key="test-key")
        prompt = advisor.generate_user_prompt(sample_scenario)
        
        # Check key information is included
        assert "28-year-old" in prompt
        assert "$95,000" in prompt or "95000" in prompt
        assert "$15,000" in prompt or "15000" in prompt
        assert "bonus" in prompt.lower()
        assert "credit card" in prompt.lower() or "8000" in prompt
    
    def test_profile_calculations(self, sample_profile):
        """Test client profile calculations."""
        # Net worth
        net_worth = sample_profile.net_worth
        assert net_worth == 2000 - 8000 - 25000  # assets - debts
        
        # Monthly cash flow
        monthly_income = sample_profile.income.total_annual / 12
        cash_flow = monthly_income - sample_profile.expenses.total_monthly
        assert cash_flow == sample_profile.monthly_cash_flow
        
        # Emergency fund months
        ef_months = sample_profile.emergency_fund_months
        assert ef_months == 2000 / sample_profile.expenses.total_monthly
    
    @patch('src.advisors.base_advisor.OpenAI')
    def test_provide_advice_mock(self, mock_openai, sample_scenario):
        """Test advice generation with mocked LLM."""
        # Mock LLM response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test advice response"))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create advisor and get advice
        advisor = CFPAdvisor(api_key="test-key")
        advice = advisor.provide_advice(sample_scenario)
        
        # Verify response structure
        assert advice.response_id is not None
        assert advice.persona == "Certified Financial Planner (CFP)"
        assert advice.model_used == "gpt-4"
        assert len(advice.summary) > 0
        assert len(advice.action_items) > 0


class TestClientProfile:
    """Test client profile model."""
    
    def test_life_stage_inference(self):
        """Test life stage inference from age."""
        # Young professional
        profile = ClientProfile(
            age=25,
            income=IncomeInfo(annual_salary=60000),
            expenses=ExpensesInfo(housing=1000, other=2000),
        )
        assert profile.infer_life_stage().value == "young_professional"
        
        # Mid-career
        profile.age = 45
        assert profile.infer_life_stage().value == "mid_career"
        
        # Pre-retirement
        profile.age = 58
        assert profile.infer_life_stage().value == "pre_retirement"
        
        # Retired
        profile.age = 67
        assert profile.infer_life_stage().value == "retired"
    
    def test_debt_totals(self):
        """Test debt calculations."""
        debts = DebtInfo(
            credit_card=5000,
            student_loan=20000,
            auto_loan=10000,
        )
        assert debts.total == 35000
    
    def test_asset_totals(self):
        """Test asset calculations."""
        assets = AssetsInfo(
            checking_savings=5000,
            retirement_401k=50000,
            brokerage=20000,
        )
        assert assets.total == 75000
        assert assets.liquid_assets == 25000  # checking + brokerage


def test_scenario_validation():
    """Test scenario validation."""
    # Valid scenario should not raise
    profile = ClientProfile(
        age=30,
        income=IncomeInfo(annual_salary=80000),
        expenses=ExpensesInfo(housing=1500, other=2500),
    )
    scenario = FinancialScenario(
        client_profile=profile,
        question="What should I do?",
    )
    assert scenario.question == "What should I do?"
    
    # Question too short should raise
    with pytest.raises(ValueError):
        FinancialScenario(
            client_profile=profile,
            question="Help",  # Too short
        )

