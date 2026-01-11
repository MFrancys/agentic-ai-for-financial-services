"""Tools for customer profile and screening."""

from typing import Dict, List
from ..models.customer_profile import CustomerProfile
from ..data.mock_data import get_mock_customer, get_mock_negative_news
from ..config import settings


def get_customer_profile(customer_id: str) -> Dict:
    """
    Get customer profile and risk information.
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        Customer profile data
    """
    # Get customer data (mock or real based on configuration)
    if settings.enable_mock_data:
        customer_data = get_mock_customer(customer_id)
    else:
        # In production, this would query real database
        raise NotImplementedError("Real database integration not implemented")
    
    if not customer_data:
        return {
            "customer_id": customer_id,
            "error": "Customer not found"
        }
    
    return customer_data


def search_negative_news(customer_name: str) -> Dict:
    """
    Search for negative news and adverse media about a customer.
    
    Args:
        customer_name: Customer name to search
    
    Returns:
        Negative news search results
    """
    # Get negative news (mock or real based on configuration)
    if settings.enable_mock_data:
        news_items = get_mock_negative_news(customer_name)
    else:
        # In production, this would use real adverse media screening API
        raise NotImplementedError("Real adverse media screening not implemented")
    
    return {
        "customer_name": customer_name,
        "search_date": "2026-01-10",
        "items_found": len(news_items),
        "news_items": news_items,
        "high_risk_items": [item for item in news_items if item.get("relevance") == "high"],
        "requires_review": len(news_items) > 0
    }


def assess_customer_risk(customer_id: str) -> Dict:
    """
    Comprehensive customer risk assessment.
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        Risk assessment results
    """
    profile = get_customer_profile(customer_id)
    
    if profile.get("error"):
        return profile
    
    # Get customer name and search negative news
    customer_name = profile.get("name", "")
    news = search_negative_news(customer_name)
    
    risk_factors = []
    risk_score = profile.get("risk_score", 0)
    
    # Assess various risk factors
    if profile.get("pep_status"):
        risk_factors.append("Politically Exposed Person (PEP)")
        risk_score += 2
    
    if profile.get("high_risk_country"):
        risk_factors.append("Associated with high-risk jurisdiction")
        risk_score += 1.5
    
    if profile.get("cash_intensive_business"):
        risk_factors.append("Cash-intensive business")
        risk_score += 1
    
    if profile.get("previous_sars", 0) > 0:
        risk_factors.append(f"Previous SARs filed: {profile['previous_sars']}")
        risk_score += profile['previous_sars'] * 2
    
    if news.get("items_found", 0) > 0:
        risk_factors.append(f"Negative news items found: {news['items_found']}")
        risk_score += news['items_found'] * 1.5
    
    # Income vs business type consistency check
    annual_income = profile.get("annual_income", 0)
    if profile.get("business_type") and annual_income < 60000:
        risk_factors.append("Business owner with low reported income")
        risk_score += 0.5
    
    # Cap risk score at 10
    risk_score = min(risk_score, 10.0)
    
    # Determine risk level
    if risk_score >= 8:
        risk_level = "critical"
    elif risk_score >= 6:
        risk_level = "high"
    elif risk_score >= 4:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "customer_id": customer_id,
        "customer_name": customer_name,
        "base_risk_score": profile.get("risk_score", 0),
        "adjusted_risk_score": round(risk_score, 2),
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "negative_news_found": news.get("items_found", 0) > 0,
        "enhanced_due_diligence_required": risk_score >= 7,
        "recommendation": self._get_risk_recommendation(risk_level, risk_score)
    }


def _get_risk_recommendation(risk_level: str, risk_score: float) -> str:
    """Get recommendation based on risk level."""
    if risk_level == "critical":
        return "Immediate enhanced due diligence required. Consider account restrictions pending review."
    elif risk_level == "high":
        return "Enhanced due diligence required. Increase transaction monitoring frequency."
    elif risk_level == "medium":
        return "Standard due diligence with elevated monitoring. Review quarterly."
    else:
        return "Standard monitoring procedures applicable."

