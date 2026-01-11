"""Investigation case models."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class AlertType(str, Enum):
    """Types of AML alerts."""
    CASH_STRUCTURING = "cash_structuring"
    WIRE_TRANSFER = "wire_transfer"
    VELOCITY_CHECK = "velocity_check"
    NEGATIVE_NEWS = "negative_news"
    HIGH_RISK_CUSTOMER = "high_risk_customer"
    UNUSUAL_ACTIVITY = "unusual_activity"
    REGULATORY_THRESHOLD = "regulatory_threshold"


class InvestigationCase(BaseModel):
    """Investigation case details."""
    
    case_id: str = Field(description="Unique case identifier")
    customer_id: str = Field(description="Customer identifier")
    account_id: str = Field(description="Account identifier")
    alert_type: AlertType = Field(description="Type of alert")
    description: str = Field(description="Description of suspicious activity")
    
    alert_date: datetime = Field(default_factory=datetime.now)
    priority: str = Field(default="medium", description="Case priority: low, medium, high, critical")
    assigned_to: Optional[str] = Field(default=None, description="Investigator assigned")
    
    # Additional context
    amount: Optional[float] = Field(default=None, description="Transaction amount if applicable")
    time_period_days: int = Field(default=30, description="Investigation time period")
    customer_explanation: Optional[str] = Field(default=None, description="Customer's explanation")
    alert_source: Optional[str] = Field(default=None, description="Source of alert")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "case_id": "CASE_001",
                "customer_id": "CUST_001",
                "account_id": "high_risk_account_001",
                "alert_type": "cash_structuring",
                "description": "Multiple cash deposits just under $10,000",
                "priority": "high",
                "time_period_days": 14,
                "customer_explanation": "Restaurant business doing really well",
                "alert_source": "Branch manager"
            }
        }

