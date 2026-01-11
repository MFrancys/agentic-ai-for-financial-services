"""Fraud detection specific tools."""

from typing import Dict, List
from datetime import datetime, timedelta
import random


def analyze_transaction_velocity(account_id: str, hours: int = 24) -> Dict:
    """
    Analyze transaction velocity for fraud detection.
    
    Velocity fraud occurs when multiple transactions happen in rapid succession,
    often indicating card testing or account takeover.
    
    Args:
        account_id: Account identifier
        hours: Time window to analyze
    
    Returns:
        Velocity analysis results
    """
    # Mock velocity data (in production, query real database)
    mock_velocities = {
        "ACCT_12345": {
            "transactions_count": 15,
            "unique_merchants": 12,
            "total_amount": 4500.00,
            "time_window_hours": hours,
            "avg_time_between_txns_minutes": 8,
            "transactions": [
                {"time": "2026-01-10 14:23:15", "amount": 299.99, "merchant": "Electronics Store"},
                {"time": "2026-01-10 14:31:42", "amount": 450.00, "merchant": "Jewelry Shop"},
                {"time": "2026-01-10 14:38:19", "amount": 199.99, "merchant": "Online Retailer"},
                {"time": "2026-01-10 14:45:05", "amount": 550.00, "merchant": "Luxury Goods"},
            ]
        },
        "ACCT_67890": {
            "transactions_count": 3,
            "unique_merchants": 3,
            "total_amount": 156.50,
            "time_window_hours": hours,
            "avg_time_between_txns_minutes": 180,
            "transactions": []
        }
    }
    
    data = mock_velocities.get(account_id, {
        "transactions_count": 0,
        "error": "Account not found"
    })
    
    if "error" in data:
        return data
    
    # Calculate velocity indicators
    txns_per_hour = data["transactions_count"] / hours
    
    # Fraud risk assessment
    risk_indicators = []
    fraud_score = 0
    
    if txns_per_hour > 2:
        risk_indicators.append("High transaction frequency")
        fraud_score += 3
    
    if data["avg_time_between_txns_minutes"] < 15:
        risk_indicators.append("Very short time between transactions")
        fraud_score += 2
    
    if data["unique_merchants"] == data["transactions_count"]:
        risk_indicators.append("Each transaction at different merchant")
        fraud_score += 2
    
    if data["total_amount"] > 3000:
        risk_indicators.append("High total transaction value")
        fraud_score += 1
    
    data["fraud_score"] = min(fraud_score, 10)
    data["risk_indicators"] = risk_indicators
    data["fraud_likelihood"] = "high" if fraud_score >= 6 else "medium" if fraud_score >= 3 else "low"
    
    return data


def check_geographic_anomaly(account_id: str, transaction_location: str) -> Dict:
    """
    Check if transaction location is anomalous for this customer.
    
    Args:
        account_id: Account identifier
        transaction_location: Location of suspicious transaction
    
    Returns:
        Geographic anomaly analysis
    """
    # Mock customer location patterns
    customer_patterns = {
        "ACCT_12345": {
            "home_location": "New York, USA",
            "typical_locations": ["New York", "Boston", "Philadelphia"],
            "recent_locations": [
                {"location": "New York", "date": "2026-01-09", "count": 5},
                {"location": "Boston", "date": "2026-01-08", "count": 2}
            ],
            "international_travel": False
        },
        "ACCT_67890": {
            "home_location": "London, UK",
            "typical_locations": ["London", "Manchester", "Paris"],
            "recent_locations": [
                {"location": "London", "date": "2026-01-10", "count": 3}
            ],
            "international_travel": True
        }
    }
    
    pattern = customer_patterns.get(account_id)
    if not pattern:
        return {"error": "Account not found"}
    
    # Check if location is anomalous
    is_typical = transaction_location in pattern["typical_locations"]
    distance_from_home = "far" if not is_typical else "near"
    
    fraud_indicators = []
    risk_score = 0
    
    if not is_typical:
        fraud_indicators.append(f"Transaction in unusual location: {transaction_location}")
        risk_score += 4
    
    # Check for impossible travel (two locations too far apart too quickly)
    if pattern["recent_locations"]:
        last_location = pattern["recent_locations"][0]["location"]
        if last_location != transaction_location and not is_typical:
            fraud_indicators.append("Potential impossible travel scenario")
            risk_score += 3
    
    return {
        "account_id": account_id,
        "transaction_location": transaction_location,
        "home_location": pattern["home_location"],
        "is_typical_location": is_typical,
        "distance_from_home": distance_from_home,
        "recent_locations": pattern["recent_locations"],
        "fraud_indicators": fraud_indicators,
        "risk_score": min(risk_score, 10),
        "fraud_likelihood": "high" if risk_score >= 6 else "medium" if risk_score >= 3 else "low"
    }


def analyze_device_fingerprint(account_id: str, device_id: str) -> Dict:
    """
    Analyze device fingerprint for fraud detection.
    
    Args:
        account_id: Account identifier
        device_id: Device identifier from transaction
    
    Returns:
        Device analysis results
    """
    # Mock device history
    device_history = {
        "ACCT_12345": {
            "known_devices": ["DEV_ABC123", "DEV_XYZ789"],
            "device_count": 2,
            "new_device_threshold_days": 30,
            "typical_device": "DEV_ABC123"
        }
    }
    
    history = device_history.get(account_id, {"known_devices": []})
    
    is_new_device = device_id not in history.get("known_devices", [])
    
    fraud_indicators = []
    risk_score = 0
    
    if is_new_device:
        fraud_indicators.append("Transaction from new/unknown device")
        risk_score += 5
    
    # Check for device characteristics
    device_info = {
        "account_id": account_id,
        "device_id": device_id,
        "is_new_device": is_new_device,
        "known_devices": history.get("known_devices", []),
        "device_age_days": 0 if is_new_device else 180,
        "fraud_indicators": fraud_indicators,
        "risk_score": risk_score,
        "recommendation": "Block transaction" if risk_score >= 5 else "Allow with monitoring"
    }
    
    return device_info


def check_behavioral_anomalies(account_id: str, current_behavior: Dict) -> Dict:
    """
    Check for behavioral anomalies compared to customer baseline.
    
    Args:
        account_id: Account identifier
        current_behavior: Current transaction behavior
    
    Returns:
        Behavioral analysis
    """
    # Mock customer baselines
    baselines = {
        "ACCT_12345": {
            "avg_transaction_amount": 75.00,
            "avg_transactions_per_day": 2.5,
            "typical_categories": ["groceries", "gas", "restaurants"],
            "typical_transaction_time": "daytime",
            "max_single_transaction": 500.00
        }
    }
    
    baseline = baselines.get(account_id)
    if not baseline:
        return {"error": "Account baseline not found"}
    
    anomalies = []
    risk_score = 0
    
    # Check amount anomaly
    current_amount = current_behavior.get("amount", 0)
    if current_amount > baseline["avg_transaction_amount"] * 5:
        anomalies.append(f"Transaction amount ${current_amount} is 5x normal average")
        risk_score += 3
    
    if current_amount > baseline["max_single_transaction"]:
        anomalies.append(f"Exceeds typical maximum transaction amount")
        risk_score += 2
    
    # Check category anomaly
    current_category = current_behavior.get("category", "")
    if current_category not in baseline["typical_categories"]:
        anomalies.append(f"Unusual merchant category: {current_category}")
        risk_score += 1
    
    # Check time anomaly
    current_time = current_behavior.get("time", "daytime")
    if current_time != baseline["typical_transaction_time"]:
        anomalies.append(f"Transaction at unusual time: {current_time}")
        risk_score += 1
    
    return {
        "account_id": account_id,
        "baseline": baseline,
        "current_behavior": current_behavior,
        "anomalies_detected": anomalies,
        "anomaly_count": len(anomalies),
        "risk_score": min(risk_score, 10),
        "fraud_likelihood": "high" if risk_score >= 6 else "medium" if risk_score >= 3 else "low"
    }


def assess_fraud_probability(indicators: List[Dict]) -> Dict:
    """
    Aggregate multiple fraud indicators into overall fraud probability.
    
    Args:
        indicators: List of indicator results from various tools
    
    Returns:
        Overall fraud assessment
    """
    if not indicators:
        return {"error": "No indicators provided"}
    
    # Aggregate risk scores
    total_risk = 0
    high_risk_count = 0
    all_indicators = []
    
    for indicator in indicators:
        risk_score = indicator.get("risk_score", 0)
        total_risk += risk_score
        
        if indicator.get("fraud_likelihood") == "high":
            high_risk_count += 1
        
        if "fraud_indicators" in indicator:
            all_indicators.extend(indicator["fraud_indicators"])
        if "risk_indicators" in indicator:
            all_indicators.extend(indicator["risk_indicators"])
        if "anomalies_detected" in indicator:
            all_indicators.extend(indicator["anomalies_detected"])
    
    avg_risk = total_risk / len(indicators)
    
    # Determine overall fraud decision
    if avg_risk >= 7 or high_risk_count >= 2:
        decision = "CONFIRMED_FRAUD"
        confidence = "high"
        action = "Block account and contact customer"
    elif avg_risk >= 5:
        decision = "SUSPECTED_FRAUD"
        confidence = "medium"
        action = "Additional verification required"
    elif avg_risk >= 3:
        decision = "NEEDS_REVIEW"
        confidence = "low"
        action = "Enhanced monitoring"
    else:
        decision = "LEGITIMATE"
        confidence = "high"
        action = "No action required"
    
    return {
        "overall_risk_score": round(avg_risk, 2),
        "fraud_decision": decision,
        "confidence": confidence,
        "recommended_action": action,
        "indicators_analyzed": len(indicators),
        "high_risk_indicators": high_risk_count,
        "all_fraud_indicators": list(set(all_indicators)),
        "indicator_count": len(all_indicators)
    }

