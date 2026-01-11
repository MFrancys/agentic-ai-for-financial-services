"""Mock data for testing and demonstration."""

from typing import Dict, List

# Mock customer database
MOCK_CUSTOMERS = {
    "CUST_001": {
        "customer_id": "CUST_001",
        "name": "Maria Santos",
        "occupation": "Restaurant Manager",
        "annual_income": 54000,
        "address": "123 Main Street, Local City, State",
        "account_age_years": 3.5,
        "risk_score": 6.2,
        "previous_sars": 0,
        "previous_ctrs": 2,
        "pep_status": False,
        "high_risk_country": False,
        "negative_news": False,
        "business_type": "Restaurant",
        "cash_intensive_business": True,
    },
    "CUST_002": {
        "customer_id": "CUST_002",
        "name": "John Davidson",
        "occupation": "Import/Export Business Owner",
        "annual_income": 180000,
        "address": "456 Commerce Ave, Business District",
        "account_age_years": 7.2,
        "risk_score": 7.8,
        "previous_sars": 1,
        "previous_ctrs": 15,
        "pep_status": False,
        "high_risk_country": True,
        "negative_news": False,
        "business_type": "Import/Export",
        "cash_intensive_business": True,
    },
    "CUST_003": {
        "customer_id": "CUST_003",
        "name": "Sarah Chen",
        "occupation": "Software Engineer",
        "annual_income": 125000,
        "address": "789 Tech Park Drive, Silicon Valley",
        "account_age_years": 5.0,
        "risk_score": 2.1,
        "previous_sars": 0,
        "previous_ctrs": 0,
        "pep_status": False,
        "high_risk_country": False,
        "negative_news": False,
        "business_type": None,
        "cash_intensive_business": False,
    },
}

# Mock transaction database
MOCK_TRANSACTIONS = {
    "high_risk_account_001": [
        {
            "transaction_id": "TXN_001",
            "date": "2025-09-15",
            "amount": 9800,
            "type": "cash_deposit",
            "location": "Branch_A",
            "method": "cash",
            "description": "Cash deposit",
            "flagged": True,
            "flag_reason": "Below CTR threshold",
        },
        {
            "transaction_id": "TXN_002",
            "date": "2025-09-14",
            "amount": 9750,
            "type": "cash_deposit",
            "location": "Branch_B",
            "method": "cash",
            "description": "Cash deposit",
            "flagged": True,
            "flag_reason": "Below CTR threshold",
        },
        {
            "transaction_id": "TXN_003",
            "date": "2025-09-13",
            "amount": 9900,
            "type": "cash_deposit",
            "location": "Branch_C",
            "method": "cash",
            "description": "Cash deposit",
            "flagged": True,
            "flag_reason": "Below CTR threshold",
        },
        {
            "transaction_id": "TXN_004",
            "date": "2025-09-12",
            "amount": 9850,
            "type": "cash_deposit",
            "location": "Branch_A",
            "method": "cash",
            "description": "Cash deposit",
            "flagged": True,
            "flag_reason": "Below CTR threshold",
        },
        {
            "transaction_id": "TXN_005",
            "date": "2025-09-11",
            "amount": 9600,
            "type": "cash_deposit",
            "location": "Branch_D",
            "method": "cash",
            "description": "Cash deposit",
            "flagged": True,
            "flag_reason": "Below CTR threshold",
        },
    ],
    "business_account_002": [
        {
            "transaction_id": "TXN_101",
            "date": "2025-09-10",
            "amount": 45000,
            "type": "wire_transfer_incoming",
            "location": "International",
            "method": "wire",
            "description": "Wire from overseas supplier",
            "counterparty": "Shanghai Trading Co",
            "country": "China",
            "flagged": True,
            "flag_reason": "High-risk country",
        },
        {
            "transaction_id": "TXN_102",
            "date": "2025-09-08",
            "amount": 38000,
            "type": "wire_transfer_outgoing",
            "location": "International",
            "method": "wire",
            "description": "Payment for goods",
            "counterparty": "Dubai Exports LLC",
            "country": "UAE",
            "flagged": True,
            "flag_reason": "High-risk country",
        },
        {
            "transaction_id": "TXN_103",
            "date": "2025-09-05",
            "amount": 52000,
            "type": "wire_transfer_incoming",
            "location": "International",
            "method": "wire",
            "description": "Customer payment",
            "counterparty": "Hong Kong Industries",
            "country": "Hong Kong",
            "flagged": False,
        },
    ],
    "normal_account": [
        {
            "transaction_id": "TXN_201",
            "date": "2025-09-15",
            "amount": 3200,
            "type": "paycheck_deposit",
            "location": "Direct Deposit",
            "method": "ach",
            "description": "Salary deposit",
            "counterparty": "Tech Corp Inc",
            "flagged": False,
        },
        {
            "transaction_id": "TXN_202",
            "date": "2025-09-10",
            "amount": 1500,
            "type": "rent_payment",
            "location": "Online",
            "method": "check",
            "description": "Monthly rent",
            "flagged": False,
        },
        {
            "transaction_id": "TXN_203",
            "date": "2025-09-05",
            "amount": 250,
            "type": "atm_withdrawal",
            "location": "ATM_Main_St",
            "method": "cash",
            "description": "Cash withdrawal",
            "flagged": False,
        },
    ],
}

# Mock negative news database
MOCK_NEGATIVE_NEWS = {
    "Maria Santos": [],
    "John Davidson": [
        {
            "source": "Financial Times",
            "date": "2024-11-15",
            "headline": "Import company under customs investigation",
            "relevance": "medium",
            "summary": "Company involved in customs valuation dispute",
        }
    ],
    "Sarah Chen": [],
}


def get_mock_customer(customer_id: str) -> Dict:
    """Get mock customer data."""
    return MOCK_CUSTOMERS.get(customer_id, None)


def get_mock_transactions(account_id: str, days: int = 30) -> List[Dict]:
    """Get mock transaction data."""
    return MOCK_TRANSACTIONS.get(account_id, [])


def get_mock_negative_news(customer_name: str) -> List[Dict]:
    """Get mock negative news data."""
    return MOCK_NEGATIVE_NEWS.get(customer_name, [])

