"""
Example: International Wire Transfer Investigation

This example demonstrates investigating suspicious international wire transfers
to high-risk jurisdictions.
"""

from src.models.investigation_case import InvestigationCase, AlertType
from src.investigators.react_investigator import ReACTInvestigator


def main():
    """Run wire transfer investigation example."""
    
    print("\n" + "="*80)
    print("EXAMPLE: International Wire Transfer Investigation")
    print("="*80 + "\n")
    
    # Define the case
    case = InvestigationCase(
        case_id="EXAMPLE_WIRE_001",
        customer_id="CUST_002",
        account_id="business_account_002",
        alert_type=AlertType.WIRE_TRANSFER,
        description="Multiple wire transfers to/from high-risk countries including China and UAE",
        priority="high",
        amount=135000.0,
        time_period_days=30,
        customer_explanation="These are legitimate import/export business transactions",
        alert_source="Automated wire transfer monitoring system",
    )
    
    print("📋 Case Details:")
    print(f"   Customer ID: {case.customer_id}")
    print(f"   Account ID: {case.account_id}")
    print(f"   Alert Type: {case.alert_type}")
    print(f"   Total Amount: ${case.amount:,.2f}")
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
    
    print("Risk Factors:")
    for factor in result.risk_factors:
        print(f"  • {factor}")
    print()
    
    print("Next Steps:")
    for step in result.next_steps:
        print(f"  • {step}")
    
    print("\n" + "="*80)
    print("Investigation Complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()

