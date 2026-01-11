"""
Example: Credit Card Fraud Detection

Demonstrates AI agent detecting credit card fraud through velocity analysis,
geographic anomalies, and device fingerprinting.
"""

from src.models.fraud_case import FraudCase, FraudType, FraudIndicator
from src.investigators.fraud_agent import FraudDetectionAgent


def main():
    """Run credit card fraud detection example."""
    
    print("\n" + "="*80)
    print("🚨 FRAUD DETECTION: Credit Card Fraud Investigation")
    print("="*80 + "\n")
    
    # Define fraud case
    case = FraudCase(
        case_id="FRAUD_CC_001",
        customer_id="CUST_001",
        account_id="ACCT_12345",
        fraud_type=FraudType.CREDIT_CARD_FRAUD,
        description="15 high-value transactions in 2 hours from new device in foreign country",
        priority="critical",
        transaction_ids=["TXN_001", "TXN_002", "TXN_003", "TXN_004"],
        total_amount=4500.00,
        fraud_indicators=[
            FraudIndicator.UNUSUAL_VELOCITY,
            FraudIndicator.GEOGRAPHIC_ANOMALY,
            FraudIndicator.NEW_DEVICE
        ],
        detection_method="automated_rules",
        time_window_hours=2,
        customer_response="I didn't make these transactions! My card was stolen yesterday.",
        dispute_filed=True,
        device_id="DEV_UNKNOWN_999",
        geolocation="Romania",
        merchant_name="Online Electronics Retailer"
    )
    
    print("📋 Fraud Case Details:")
    print(f"   Type: {case.fraud_type.value}")
    print(f"   Amount: ${case.total_amount:,.2f}")
    print(f"   Location: {case.geolocation}")
    print(f"   Device: {case.device_id}")
    print(f"   Indicators: {', '.join([i.value for i in case.fraud_indicators])}")
    print(f"   Customer: \"{case.customer_response}\"")
    print()
    
    # Create fraud detection agent
    agent = FraudDetectionAgent()
    
    # Run AI agent investigation
    print("🤖 Activating Fraud Detection Agent...")
    print("-" * 80)
    result = agent.investigate(case, verbose=True)
    
    # Display results
    print("\n" + "="*80)
    print("📊 AGENT DECISION")
    print("="*80)
    print(f"Fraud Score: {result.final_risk_score}/10")
    print(f"Decision: {result.recommendation}")
    print(f"Action Required: {'YES - IMMEDIATE' if result.escalation_required else 'YES' if result.sar_required else 'Review'}")
    print()
    
    if result.key_findings:
        print("Key Evidence:")
        for finding in result.key_findings:
            print(f"  🔴 {finding}")
        print()
    
    print("Recommended Actions:")
    for step in result.next_steps:
        print(f"  → {step}")
    
    print("\n" + "="*80)
    print("Investigation Complete - Agent Confident in Assessment")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

