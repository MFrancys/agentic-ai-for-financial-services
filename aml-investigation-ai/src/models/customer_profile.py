"""Customer profile models."""

from typing import Optional
from pydantic import BaseModel, Field


class CustomerProfile(BaseModel):
    """Customer profile and risk information."""
    
    customer_id: str = Field(description="Customer identifier")
    name: str = Field(description="Customer name")
    
    # Demographics
    occupation: str = Field(description="Customer occupation")
    annual_income: float = Field(description="Annual income in USD")
    address: str = Field(description="Customer address")
    
    # Account information
    account_age_years: float = Field(description="Years as customer")
    
    # Risk indicators
    risk_score: float = Field(description="Risk score (0-10)", ge=0, le=10)
    previous_sars: int = Field(default=0, description="Number of previous SARs")
    previous_ctrs: int = Field(default=0, description="Number of previous CTRs")
    
    # Additional flags
    pep_status: bool = Field(default=False, description="Politically Exposed Person")
    high_risk_country: bool = Field(default=False, description="From high-risk jurisdiction")
    negative_news: bool = Field(default=False, description="Adverse media found")
    
    # Business information (if applicable)
    business_type: Optional[str] = Field(default=None, description="Type of business")
    cash_intensive_business: bool = Field(default=False, description="Cash-intensive business flag")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "customer_id": "CUST_001",
                "name": "Maria Santos",
                "occupation": "Restaurant Manager",
                "annual_income": 54000,
                "address": "123 Main St, City, State",
                "account_age_years": 3.5,
                "risk_score": 6.2,
                "previous_sars": 0,
                "previous_ctrs": 2,
                "pep_status": False,
                "high_risk_country": False,
                "negative_news": False,
                "business_type": "Restaurant",
                "cash_intensive_business": True
            }
        }

