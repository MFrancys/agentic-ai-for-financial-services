"""Transaction models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Transaction(BaseModel):
    """Individual transaction details."""
    
    transaction_id: str = Field(description="Transaction identifier")
    date: str = Field(description="Transaction date (YYYY-MM-DD)")
    amount: float = Field(description="Transaction amount in USD")
    type: str = Field(description="Transaction type")
    
    # Location and method
    location: Optional[str] = Field(default=None, description="Transaction location")
    method: Optional[str] = Field(default=None, description="Payment method")
    
    # Additional details
    description: Optional[str] = Field(default=None, description="Transaction description")
    counterparty: Optional[str] = Field(default=None, description="Other party in transaction")
    country: Optional[str] = Field(default="USA", description="Transaction country")
    
    # Flags
    flagged: bool = Field(default=False, description="Flagged as suspicious")
    flag_reason: Optional[str] = Field(default=None, description="Reason for flagging")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "transaction_id": "TXN_001",
                "date": "2025-09-15",
                "amount": 9800.0,
                "type": "cash_deposit",
                "location": "Branch_A",
                "method": "cash",
                "description": "Cash deposit",
                "flagged": True,
                "flag_reason": "Below CTR threshold"
            }
        }


class TransactionHistory(BaseModel):
    """Transaction history for an account."""
    
    account_id: str = Field(description="Account identifier")
    period_days: int = Field(description="Time period in days")
    transaction_count: int = Field(description="Number of transactions")
    total_amount: float = Field(description="Total transaction amount")
    
    transactions: List[Transaction] = Field(description="List of transactions")
    
    # Summary statistics
    cash_deposit_count: int = Field(default=0, description="Number of cash deposits")
    cash_withdrawal_count: int = Field(default=0, description="Number of cash withdrawals")
    wire_transfer_count: int = Field(default=0, description="Number of wire transfers")
    
    avg_transaction_amount: float = Field(default=0.0, description="Average transaction amount")
    max_transaction_amount: float = Field(default=0.0, description="Maximum transaction amount")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "account_id": "high_risk_account_001",
                "period_days": 14,
                "transaction_count": 5,
                "total_amount": 48900.0,
                "transactions": [],
                "cash_deposit_count": 5,
                "avg_transaction_amount": 9780.0,
                "max_transaction_amount": 9900.0
            }
        }

