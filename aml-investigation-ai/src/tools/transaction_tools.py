"""Tools for transaction history and analysis."""

from typing import Dict, List
from ..models.transaction import Transaction, TransactionHistory
from ..data.mock_data import get_mock_transactions
from ..config import settings


def get_transaction_history(account_id: str, days: int = 30) -> Dict:
    """
    Get transaction history for an account.
    
    Args:
        account_id: Account identifier
        days: Number of days to look back
    
    Returns:
        Transaction history with summary statistics
    """
    # Get transactions (mock or real based on configuration)
    if settings.enable_mock_data:
        transactions = get_mock_transactions(account_id, days)
    else:
        # In production, this would query real database
        raise NotImplementedError("Real database integration not implemented")
    
    if not transactions:
        return {
            "account_id": account_id,
            "period_days": days,
            "transaction_count": 0,
            "total_amount": 0,
            "transactions": [],
            "error": "No transactions found for this account"
        }
    
    # Calculate summary statistics
    total_amount = sum(t["amount"] for t in transactions)
    cash_deposits = [t for t in transactions if t["type"] == "cash_deposit"]
    cash_withdrawals = [t for t in transactions if t["type"] == "cash_withdrawal"]
    wire_transfers = [t for t in transactions if "wire" in t["type"]]
    
    amounts = [t["amount"] for t in transactions]
    
    return {
        "account_id": account_id,
        "period_days": days,
        "transaction_count": len(transactions),
        "total_amount": total_amount,
        "transactions": transactions,
        "cash_deposit_count": len(cash_deposits),
        "cash_withdrawal_count": len(cash_withdrawals),
        "wire_transfer_count": len(wire_transfers),
        "avg_transaction_amount": total_amount / len(transactions) if transactions else 0,
        "max_transaction_amount": max(amounts) if amounts else 0,
        "min_transaction_amount": min(amounts) if amounts else 0,
    }


def analyze_transaction_patterns(account_id: str, days: int = 30) -> Dict:
    """
    Analyze transaction patterns for suspicious activity.
    
    Args:
        account_id: Account identifier
        days: Number of days to analyze
    
    Returns:
        Pattern analysis results
    """
    history = get_transaction_history(account_id, days)
    
    if history.get("error"):
        return history
    
    transactions = history["transactions"]
    patterns = {
        "account_id": account_id,
        "analysis_period_days": days,
        "patterns_detected": [],
        "risk_indicators": [],
    }
    
    # Check for structuring pattern (multiple transactions under $10,000)
    under_threshold = [t for t in transactions if t["amount"] < 10000 and t["amount"] > 9000]
    if len(under_threshold) >= 3:
        patterns["patterns_detected"].append({
            "pattern": "potential_structuring",
            "description": f"Found {len(under_threshold)} transactions between $9,000 and $10,000",
            "severity": "high",
            "transactions": len(under_threshold)
        })
        patterns["risk_indicators"].append("Structuring to avoid CTR reporting")
    
    # Check for velocity (many transactions in short period)
    if len(transactions) > 10 and days <= 14:
        patterns["patterns_detected"].append({
            "pattern": "high_velocity",
            "description": f"{len(transactions)} transactions in {days} days",
            "severity": "medium",
            "transactions": len(transactions)
        })
        patterns["risk_indicators"].append("Unusual transaction velocity")
    
    # Check for round amounts (common in suspicious activity)
    round_amounts = [t for t in transactions if t["amount"] % 100 == 0]
    if len(round_amounts) / len(transactions) > 0.7:
        patterns["patterns_detected"].append({
            "pattern": "round_amounts",
            "description": f"{len(round_amounts)} of {len(transactions)} are round amounts",
            "severity": "low",
            "transactions": len(round_amounts)
        })
    
    # Check for same-day multiple transactions
    dates = [t["date"] for t in transactions]
    date_counts = {}
    for date in dates:
        date_counts[date] = date_counts.get(date, 0) + 1
    
    multiple_per_day = [date for date, count in date_counts.items() if count > 1]
    if len(multiple_per_day) >= 2:
        patterns["patterns_detected"].append({
            "pattern": "multiple_daily_transactions",
            "description": f"Multiple transactions on same day detected on {len(multiple_per_day)} days",
            "severity": "medium",
            "days": len(multiple_per_day)
        })
    
    # Overall risk assessment
    high_risk_patterns = sum(1 for p in patterns["patterns_detected"] if p["severity"] == "high")
    medium_risk_patterns = sum(1 for p in patterns["patterns_detected"] if p["severity"] == "medium")
    
    if high_risk_patterns > 0:
        patterns["overall_risk"] = "high"
    elif medium_risk_patterns >= 2:
        patterns["overall_risk"] = "high"
    elif medium_risk_patterns > 0:
        patterns["overall_risk"] = "medium"
    else:
        patterns["overall_risk"] = "low"
    
    return patterns

