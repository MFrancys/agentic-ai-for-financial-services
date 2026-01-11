"""Tests for investigation tools."""

import pytest
from src.tools.transaction_tools import get_transaction_history, analyze_transaction_patterns
from src.tools.customer_tools import get_customer_profile, search_negative_news
from src.tools.regulatory_tools import check_regulatory_thresholds, assess_structuring_risk


def test_get_transaction_history():
    """Test transaction history retrieval."""
    result = get_transaction_history("high_risk_account_001", days=14)
    
    assert result is not None
    assert "account_id" in result
    assert "transactions" in result
    assert result["account_id"] == "high_risk_account_001"
    assert result["transaction_count"] >= 0


def test_get_transaction_history_unknown_account():
    """Test transaction history for unknown account."""
    result = get_transaction_history("unknown_account", days=14)
    
    assert result is not None
    assert "error" in result or result["transaction_count"] == 0


def test_analyze_transaction_patterns():
    """Test transaction pattern analysis."""
    result = analyze_transaction_patterns("high_risk_account_001", days=14)
    
    assert result is not None
    assert "patterns_detected" in result
    assert "risk_indicators" in result
    assert "overall_risk" in result


def test_get_customer_profile():
    """Test customer profile retrieval."""
    result = get_customer_profile("CUST_001")
    
    assert result is not None
    assert "customer_id" in result
    assert "name" in result
    assert "risk_score" in result
    assert result["customer_id"] == "CUST_001"


def test_get_customer_profile_unknown():
    """Test customer profile for unknown customer."""
    result = get_customer_profile("UNKNOWN")
    
    assert result is not None
    assert "error" in result


def test_search_negative_news():
    """Test negative news search."""
    result = search_negative_news("Maria Santos")
    
    assert result is not None
    assert "customer_name" in result
    assert "items_found" in result
    assert "news_items" in result


def test_check_regulatory_thresholds_above_ctr():
    """Test regulatory check for amount above CTR threshold."""
    result = check_regulatory_thresholds(15000, "cash_deposit")
    
    assert result is not None
    assert result["ctr_required"] is True
    assert result["amount"] == 15000


def test_check_regulatory_thresholds_structuring():
    """Test regulatory check for structuring amount."""
    result = check_regulatory_thresholds(9800, "cash_deposit")
    
    assert result is not None
    assert result.get("potential_structuring") is True
    assert "potential_structuring" in result.get("sar_indicators", [])


def test_assess_structuring_risk():
    """Test structuring risk assessment."""
    transactions = [
        {"date": "2025-01-01", "amount": 9800, "type": "cash_deposit"},
        {"date": "2025-01-02", "amount": 9750, "type": "cash_deposit"},
        {"date": "2025-01-03", "amount": 9900, "type": "cash_deposit"},
    ]
    
    result = assess_structuring_risk(transactions)
    
    assert result is not None
    assert "structuring_risk_level" in result
    assert "indicators" in result
    assert result["under_threshold_transactions"] >= 3


def test_assess_structuring_risk_empty():
    """Test structuring assessment with no transactions."""
    result = assess_structuring_risk([])
    
    assert result is not None
    assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

