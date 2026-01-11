"""Tools for regulatory compliance checking."""

from typing import Dict
from ..config import settings


def check_regulatory_thresholds(transaction_amount: float, transaction_type: str) -> Dict:
    """
    Check if transaction meets regulatory reporting thresholds.
    
    Args:
        transaction_amount: Transaction amount in USD
        transaction_type: Type of transaction
    
    Returns:
        Regulatory threshold analysis
    """
    ctr_threshold = settings.ctr_threshold  # $10,000 by default
    
    result = {
        "amount": transaction_amount,
        "type": transaction_type,
        "ctr_threshold": ctr_threshold,
        "ctr_required": False,
        "sar_indicators": [],
        "compliance_notes": []
    }
    
    # CTR (Currency Transaction Report) - transactions >= $10,000
    if transaction_amount >= ctr_threshold:
        result["ctr_required"] = True
        result["compliance_notes"].append(
            f"CTR filing required for transaction amount ${transaction_amount:,.2f}"
        )
    
    # Potential structuring - amounts just under threshold
    if 9000 <= transaction_amount < ctr_threshold:
        result["sar_indicators"].append("potential_structuring")
        result["compliance_notes"].append(
            f"Amount ${transaction_amount:,.2f} is suspiciously close to CTR threshold"
        )
        result["below_ctr_threshold"] = True
        result["potential_structuring"] = True
    
    # Wire transfer monitoring (FinCEN Travel Rule - $3,000+)
    if transaction_type in ["wire_transfer_incoming", "wire_transfer_outgoing", "wire_transfer"]:
        result["wire_monitoring"] = True
        if transaction_amount >= 3000:
            result["compliance_notes"].append(
                "Wire transfer >= $3,000 - Travel Rule recordkeeping required"
            )
        if transaction_amount >= 10000:
            result["compliance_notes"].append(
                "Wire transfer >= $10,000 - Enhanced due diligence required"
            )
    
    # International transactions
    if "international" in transaction_type.lower() or transaction_amount >= 10000:
        result["enhanced_monitoring"] = True
    
    # Cash transactions (higher scrutiny)
    if "cash" in transaction_type.lower():
        result["cash_transaction"] = True
        if transaction_amount >= 5000:
            result["compliance_notes"].append(
                "Large cash transaction - verify source of funds"
            )
    
    # Overall SAR consideration
    if len(result["sar_indicators"]) > 0:
        result["sar_consideration_required"] = True
    
    return result


def calculate_risk_score(customer_profile: Dict, transaction_history: Dict) -> Dict:
    """
    Calculate risk score based on customer profile and transaction patterns.
    
    Args:
        customer_profile: Customer profile data
        transaction_history: Transaction history data
    
    Returns:
        Risk score calculation
    """
    base_score = customer_profile.get("risk_score", 5.0)
    adjustments = []
    
    # Transaction velocity adjustment
    txn_count = transaction_history.get("transaction_count", 0)
    period_days = transaction_history.get("period_days", 30)
    txns_per_day = txn_count / period_days if period_days > 0 else 0
    
    if txns_per_day > 2:
        adjustment = min(txns_per_day - 2, 2.0)
        adjustments.append({
            "factor": "high_velocity",
            "adjustment": adjustment,
            "reason": f"High transaction velocity: {txns_per_day:.1f} transactions/day"
        })
        base_score += adjustment
    
    # Large cash transactions
    cash_deposit_count = transaction_history.get("cash_deposit_count", 0)
    if cash_deposit_count >= 5:
        adjustment = min(cash_deposit_count * 0.3, 2.0)
        adjustments.append({
            "factor": "frequent_cash_deposits",
            "adjustment": adjustment,
            "reason": f"Frequent cash deposits: {cash_deposit_count} deposits"
        })
        base_score += adjustment
    
    # Transaction amounts
    avg_amount = transaction_history.get("avg_transaction_amount", 0)
    annual_income = customer_profile.get("annual_income", 1)
    
    if avg_amount > annual_income / 12:
        adjustment = 1.5
        adjustments.append({
            "factor": "transactions_exceed_income",
            "adjustment": adjustment,
            "reason": f"Average transaction ${avg_amount:,.0f} exceeds monthly income"
        })
        base_score += adjustment
    
    # Previous SARs
    previous_sars = customer_profile.get("previous_sars", 0)
    if previous_sars > 0:
        adjustment = previous_sars * 1.0
        adjustments.append({
            "factor": "previous_sars",
            "adjustment": adjustment,
            "reason": f"Previous SARs filed: {previous_sars}"
        })
        base_score += adjustment
    
    # Cap at 10
    final_score = min(base_score, 10.0)
    
    # Risk level determination
    if final_score >= 8:
        risk_level = "critical"
        recommendation = "Immediate SAR filing recommended"
    elif final_score >= 6:
        risk_level = "high"
        recommendation = "Enhanced monitoring and potential SAR filing"
    elif final_score >= 4:
        risk_level = "medium"
        recommendation = "Continued monitoring required"
    else:
        risk_level = "low"
        recommendation = "Standard monitoring"
    
    return {
        "base_risk_score": customer_profile.get("risk_score", 5.0),
        "adjustments": adjustments,
        "total_adjustment": sum(adj["adjustment"] for adj in adjustments),
        "final_risk_score": round(final_score, 2),
        "risk_level": risk_level,
        "sar_recommended": final_score >= settings.sar_risk_threshold,
        "recommendation": recommendation
    }


def assess_structuring_risk(transactions: list) -> Dict:
    """
    Assess risk of structuring (breaking up transactions to avoid reporting).
    
    Args:
        transactions: List of transactions to analyze
    
    Returns:
        Structuring risk assessment
    """
    if not transactions:
        return {"error": "No transactions provided"}
    
    ctr_threshold = settings.ctr_threshold
    structuring_indicators = []
    
    # Check for multiple transactions under threshold
    under_threshold = [t for t in transactions if 
                      t.get("amount", 0) < ctr_threshold and 
                      t.get("amount", 0) > ctr_threshold * 0.9]
    
    if len(under_threshold) >= 2:
        structuring_indicators.append({
            "indicator": "multiple_under_threshold",
            "count": len(under_threshold),
            "description": f"{len(under_threshold)} transactions between ${ctr_threshold*0.9:,.0f} and ${ctr_threshold:,.0f}"
        })
    
    # Check if total would exceed threshold
    total_amount = sum(t.get("amount", 0) for t in under_threshold)
    if total_amount >= ctr_threshold and len(under_threshold) >= 2:
        structuring_indicators.append({
            "indicator": "total_exceeds_threshold",
            "total_amount": total_amount,
            "description": f"Combined amount ${total_amount:,.2f} exceeds CTR threshold"
        })
    
    # Check for same-day transactions
    dates = {}
    for t in under_threshold:
        date = t.get("date")
        if date:
            dates[date] = dates.get(date, 0) + 1
    
    same_day_count = sum(1 for count in dates.values() if count > 1)
    if same_day_count > 0:
        structuring_indicators.append({
            "indicator": "same_day_transactions",
            "count": same_day_count,
            "description": f"Multiple under-threshold transactions on {same_day_count} day(s)"
        })
    
    # Risk level determination
    if len(structuring_indicators) >= 3:
        risk_level = "critical"
    elif len(structuring_indicators) >= 2:
        risk_level = "high"
    elif len(structuring_indicators) >= 1:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "structuring_risk_level": risk_level,
        "indicators_found": len(structuring_indicators),
        "indicators": structuring_indicators,
        "transactions_analyzed": len(transactions),
        "under_threshold_transactions": len(under_threshold),
        "total_amount": total_amount if under_threshold else 0,
        "sar_recommended": risk_level in ["critical", "high"]
    }

