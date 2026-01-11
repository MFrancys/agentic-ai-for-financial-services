"""
Example: Cash Structuring Investigation

This example demonstrates how to investigate a classic cash structuring case
where a customer makes multiple deposits just under the $10,000 CTR threshold.
"""

from src.models.investigation_case import InvestigationCase, AlertType
from src.investigators.react_investigator import ReACTInvestigator


def main():
    """Run cash structuring investigation example."""
    
    print("\n" + "="*80)
    print("EXAMPLE: Cash Structuring Investigation")
    print("="*80 + "\n")
    
    # Define the case
    case = InvestigationCase(
        case_id="EXAMPLE_STRUCTURING_001",
        customer_id="CUST_001",
        account_id="high_risk_account_001",
        alert_type=AlertType.CASH_STRUCTURING,
        description="Customer made 5 cash deposits in 5 days, all between $9,600 and $9,900",
        priority="high",
        time_period_days=14,
        customer_explanation="My restaurant has been doing really well lately",
        alert_source="Branch manager noticed the pattern",
    )
    
    print("📋 Case Details:")
    print(f"   Customer ID: {case.customer_id}")
    print(f"   Account ID: {case.account_id}")
    print(f"   Alert Type: {case.alert_type}")
    print(f"   Description: {case.description}")
    print(f"   Customer Says: \"{case.customer_explanation}\"")
    print()
    
    # Create investigator
    investigator = ReACTInvestigator()
    
    # Run investigation
    print("🔍 Starting Investigation...")
    print("-" * 80)
    result = investigator.investigate(case, verbose=True)
    
    # Display summary
    print("\n" + "="*80)
    print("📊 INVESTIGATION SUMMARY")
    print("="*80)
    print(f"Risk Score: {result.final_risk_score}/10")
    print(f"SAR Required: {'YES ⚠️' if result.sar_required else 'NO ✓'}")
    print(f"Recommendation: {result.recommendation}")
    print()
    
    if result.key_findings:
        print("Key Findings:")
        for finding in result.key_findings:
            print(f"  • {finding}")
        print()
    
    if result.sar_reasoning:
        print("SAR Filing Reasoning:")
        print(result.sar_reasoning)
        print()
    
    print("Next Steps:")
    for step in result.next_steps:
        print(f"  • {step}")
    
    print("\n" + "="*80)
    print("Investigation Complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

