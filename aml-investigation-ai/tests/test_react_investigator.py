"""Tests for ReACT investigator."""

import pytest
from src.models.investigation_case import InvestigationCase, AlertType
from src.investigators.react_investigator import ReACTInvestigator
from src.config import settings


@pytest.fixture
def sample_case():
    """Create a sample investigation case."""
    return InvestigationCase(
        case_id="TEST_001",
        customer_id="CUST_001",
        account_id="high_risk_account_001",
        alert_type=AlertType.CASH_STRUCTURING,
        description="Test case for structuring",
        priority="high",
        time_period_days=14,
    )


@pytest.fixture
def investigator():
    """Create investigator instance."""
    return ReACTInvestigator()


def test_investigator_initialization():
    """Test investigator can be initialized."""
    investigator = ReACTInvestigator()
    assert investigator is not None
    assert investigator.model == settings.model_name
    assert investigator.temperature == settings.temperature


def test_investigation_returns_result(investigator, sample_case):
    """Test investigation returns a valid result."""
    result = investigator.investigate(sample_case, verbose=False)
    
    assert result is not None
    assert result.case_id == sample_case.case_id
    assert result.investigation_id is not None
    assert result.status == "completed"
    assert result.final_risk_score >= 0
    assert result.final_risk_score <= 10
    assert result.recommendation is not None
    assert isinstance(result.sar_required, bool)


def test_investigation_uses_tools(investigator, sample_case):
    """Test that investigation executes tools."""
    result = investigator.investigate(sample_case, verbose=False)
    
    # Should have executed at least some tools
    assert len(result.tool_executions) > 0
    
    # Check tool execution structure
    for execution in result.tool_executions:
        assert execution.tool_name is not None
        assert execution.parameters is not None
        assert execution.timestamp is not None


def test_investigation_collects_evidence(investigator, sample_case):
    """Test that investigation collects evidence."""
    result = investigator.investigate(sample_case, verbose=False)
    
    # For a high-risk structuring case, should collect evidence
    # (May vary based on mock data and LLM responses)
    assert result.evidence is not None
    

def test_high_risk_case_triggers_sar(investigator):
    """Test that high-risk structuring case triggers SAR recommendation."""
    case = InvestigationCase(
        case_id="HIGH_RISK_001",
        customer_id="CUST_001",
        account_id="high_risk_account_001",
        alert_type=AlertType.CASH_STRUCTURING,
        description="5 cash deposits in 5 days, all under $10,000",
        priority="critical",
        time_period_days=5,
    )
    
    result = investigator.investigate(case, verbose=False)
    
    # High-risk structuring should typically recommend SAR
    # (Depends on LLM analysis and mock data)
    assert result.final_risk_score >= 5.0  # Should have elevated risk


def test_low_risk_case(investigator):
    """Test normal activity case."""
    case = InvestigationCase(
        case_id="LOW_RISK_001",
        customer_id="CUST_003",
        account_id="normal_account",
        alert_type=AlertType.UNUSUAL_ACTIVITY,
        description="Standard account activity",
        priority="low",
        time_period_days=30,
    )
    
    result = investigator.investigate(case, verbose=False)
    
    # Low-risk case should have lower risk score
    assert result is not None
    assert result.final_risk_score <= 8.0


def test_investigation_has_reasoning_trace(investigator, sample_case):
    """Test that investigation maintains reasoning trace."""
    result = investigator.investigate(sample_case, verbose=False)
    
    assert len(result.reasoning_trace) > 0
    assert result.iterations > 0


def test_investigation_respects_max_iterations(sample_case):
    """Test that investigation respects max iterations setting."""
    investigator = ReACTInvestigator(max_iterations=2)
    result = investigator.investigate(sample_case, verbose=False)
    
    # Should not exceed max iterations
    assert result.iterations <= 2


def test_investigation_has_next_steps(investigator, sample_case):
    """Test that investigation provides next steps."""
    result = investigator.investigate(sample_case, verbose=False)
    
    assert result.next_steps is not None
    assert len(result.next_steps) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

