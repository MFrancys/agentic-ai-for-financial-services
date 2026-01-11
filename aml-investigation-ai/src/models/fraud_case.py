"""Fraud detection case models."""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class FraudType(str, Enum):
    """Types of fraud scenarios."""
    CREDIT_CARD_FRAUD = "credit_card_fraud"
    ACCOUNT_TAKEOVER = "account_takeover"
    PAYMENT_FRAUD = "payment_fraud"
    IDENTITY_THEFT = "identity_theft"
    TRANSACTION_ANOMALY = "transaction_anomaly"
    MERCHANT_FRAUD = "merchant_fraud"
    REFUND_ABUSE = "refund_abuse"
    CHARGEBACK_FRAUD = "chargeback_fraud"
    VELOCITY_ABUSE = "velocity_abuse"


class FraudIndicator(str, Enum):
    """Common fraud indicators."""
    UNUSUAL_VELOCITY = "unusual_velocity"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    DEVICE_MISMATCH = "device_mismatch"
    TIME_ANOMALY = "time_anomaly"
    AMOUNT_ANOMALY = "amount_anomaly"
    MERCHANT_CATEGORY_UNUSUAL = "merchant_category_unusual"
    MULTIPLE_FAILED_ATTEMPTS = "multiple_failed_attempts"
    NEW_DEVICE = "new_device"
    VPN_USAGE = "vpn_usage"
    BEHAVIORAL_CHANGE = "behavioral_change"


class FraudCase(BaseModel):
    """Fraud detection case details."""
    
    case_id: str = Field(description="Unique case identifier")
    customer_id: str = Field(description="Customer identifier")
    account_id: str = Field(description="Account identifier")
    fraud_type: FraudType = Field(description="Type of suspected fraud")
    description: str = Field(description="Description of suspicious activity")
    
    # Case metadata
    alert_date: datetime = Field(default_factory=datetime.now)
    priority: str = Field(default="medium", description="Case priority: low, medium, high, critical")
    assigned_to: Optional[str] = Field(default=None, description="Investigator assigned")
    
    # Fraud-specific details
    transaction_ids: List[str] = Field(default_factory=list, description="Related transaction IDs")
    total_amount: Optional[float] = Field(default=None, description="Total fraud amount")
    affected_accounts: int = Field(default=1, description="Number of affected accounts")
    
    # Detection context
    fraud_indicators: List[FraudIndicator] = Field(default_factory=list, description="Initial fraud indicators")
    detection_method: str = Field(default="automated", description="How fraud was detected")
    time_window_hours: int = Field(default=24, description="Time window for investigation")
    
    # Customer context
    customer_response: Optional[str] = Field(default=None, description="Customer's response/claim")
    dispute_filed: bool = Field(default=False, description="Whether customer filed dispute")
    
    # Additional data
    ip_address: Optional[str] = Field(default=None, description="IP address if applicable")
    device_id: Optional[str] = Field(default=None, description="Device identifier")
    geolocation: Optional[str] = Field(default=None, description="Transaction location")
    merchant_name: Optional[str] = Field(default=None, description="Merchant involved")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "case_id": "FRAUD_001",
                "customer_id": "CUST_001",
                "account_id": "ACCT_12345",
                "fraud_type": "credit_card_fraud",
                "description": "Multiple high-value transactions from new device in foreign country",
                "priority": "high",
                "transaction_ids": ["TXN_001", "TXN_002", "TXN_003"],
                "total_amount": 4500.00,
                "fraud_indicators": ["geographic_anomaly", "new_device", "unusual_velocity"],
                "detection_method": "rule_engine",
                "time_window_hours": 2,
                "customer_response": "Claims card was stolen",
                "dispute_filed": True,
                "geolocation": "Romania",
                "merchant_name": "Online Electronics Store"
            }
        }


class FraudDecision(str, Enum):
    """Fraud investigation decision outcomes."""
    CONFIRMED_FRAUD = "confirmed_fraud"
    SUSPECTED_FRAUD = "suspected_fraud"
    LEGITIMATE = "legitimate"
    NEEDS_REVIEW = "needs_review"
    INSUFFICIENT_DATA = "insufficient_data"


class FraudAction(str, Enum):
    """Actions to take on fraud cases."""
    BLOCK_CARD = "block_card"
    BLOCK_ACCOUNT = "block_account"
    CONTACT_CUSTOMER = "contact_customer"
    REFUND_CUSTOMER = "refund_customer"
    DECLINE_CLAIM = "decline_claim"
    ESCALATE = "escalate"
    MONITOR = "monitor"
    NO_ACTION = "no_action"

