"""
Example: Account Takeover Detection

Demonstrates AI agent detecting account takeover through behavioral analysis
and device fingerprinting.
"""

from src.models.fraud_case import FraudCase, FraudType, FraudIndicator
from src.investigators.fraud_agent import FraudDetectionAgent


def main():
    """Run account takeover detection example."""
    
    print("\n" + "="*80)
    print("🚨 FRAUD DETECTION: Account Takeover Investigation")
    print("="*80 + "\n")
    
    # Define account takeover case
    case = FraudCase(
        case_id="FRAUD_ATO_001",
        customer_id="CUST_002",
        account_id="ACCT_67890",
        fraud_type=FraudType.ACCOUNT_TAKEOVER,
        description="Sudden change in behavior: new device, unusual transactions, password changed",
        priority="high",
        transaction_ids=["TXN_201", "TXN_202"],
        total_amount=2800.00,
        fraud_indicators=[
            FraudIndicator.NEW_DEVICE,
            FraudIndicator.BEHAVIORAL_CHANGE,
            FraudIndicator.MULTIPLE_FAILED_ATTEMPTS
        ],
        detection_method="behavioral_analytics",
        time_window_hours=24,
        customer_response=None,  # Customer not yet contacted
        dispute_filed=False,
        device_id="DEV_NEW_555",
        geolocation="Different State",
        ip_address="45.142.xxx.xxx"
    )
    
    print("📋 Account Takeover Case:")
    print(f"   Type: {case.fraud_type.value}")
    print(f"   Amount: ${case.total_amount:,.2f}")
    print(f"   Device: {case.device_id} (NEW)")
    print(f"   Indicators: {', '.join([i.value for i in case.fraud_indicators])}")
    print(f"   Description: {case.description}")
    print()
    
    # Create AI agent
    agent = FraudDetectionAgent()
    
    # Run investigation
    print("🤖 Fraud Detection Agent Analyzing...")
    print("-" * 80)
    result = agent.investigate(case, verbose=True)
    
    # Results
    print("\n" + "="*80)
    print("📊 AGENT ASSESSMENT")
    print("="*80)
    print(f"Fraud Score: {result.final_risk_score}/10")
    print(f"Decision: {result.recommendation}")
    print(f"Confidence: HIGH" if result.final_risk_score >= 7 else "MEDIUM")
    print()
    
    print("Evidence Collected:")
    for evidence in result.evidence[:5]:
        print(f"  • [{evidence.severity.upper()}] {evidence.description}")
    print()
    
    print("Agent's Recommended Actions:")
    for step in result.next_steps:
        print(f"  ✓ {step}")
    
    print("\n" + "="*80)
    print("Account Takeover Investigation Complete")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

