#!/usr/bin/env python3
"""
AML Investigation AI - Command Line Interface

Run investigations from the command line for testing and demonstration.
"""

import argparse
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from src.config import settings, validate_configuration
from src.models.investigation_case import InvestigationCase, AlertType
from src.investigators.react_investigator import ReACTInvestigator

console = Console()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AML Investigation AI - Conduct financial crime investigations using AI"
    )
    parser.add_argument(
        "--case-id",
        type=str,
        help="Predefined case ID to investigate (CASE_001, CASE_002, etc.)"
    )
    parser.add_argument(
        "--customer-id",
        type=str,
        help="Customer ID to investigate"
    )
    parser.add_argument(
        "--account-id",
        type=str,
        help="Account ID to investigate"
    )
    parser.add_argument(
        "--alert-type",
        type=str,
        choices=[t.value for t in AlertType],
        help="Type of alert"
    )
    parser.add_argument(
        "--description",
        type=str,
        help="Description of suspicious activity"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Time period in days (default: 30)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output with full investigation trace"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demo with predefined cases"
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        validate_configuration()
    except ValueError as e:
        console.print(f"[red]Configuration Error: {e}[/red]")
        console.print("[yellow]Please check your .env file and ensure OPENAI_API_KEY is set.[/yellow]")
        return 1
    
    # Show banner
    show_banner()
    
    # Run demo mode
    if args.demo:
        run_demo()
        return 0
    
    # Get case to investigate
    if args.case_id:
        case = get_predefined_case(args.case_id)
        if not case:
            console.print(f"[red]Case {args.case_id} not found[/red]")
            return 1
    elif all([args.customer_id, args.account_id, args.alert_type, args.description]):
        case = InvestigationCase(
            case_id=f"CUSTOM_{args.customer_id}",
            customer_id=args.customer_id,
            account_id=args.account_id,
            alert_type=AlertType(args.alert_type),
            description=args.description,
            time_period_days=args.days,
        )
    else:
        console.print("[yellow]Please provide --case-id or all of: --customer-id, --account-id, --alert-type, --description[/yellow]")
        console.print("\nAvailable predefined cases: CASE_001, CASE_002, CASE_003")
        console.print("\nTry: python app.py --demo")
        return 1
    
    # Run investigation
    investigator = ReACTInvestigator()
    result = investigator.investigate(case, verbose=args.verbose)
    
    # Display results
    display_results(result)
    
    return 0


def show_banner():
    """Display application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         AML INVESTIGATION AI                              ║
    ║         Powered by ReACT Framework                        ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold blue")


def get_predefined_case(case_id: str) -> InvestigationCase:
    """Get predefined test case."""
    cases = {
        "CASE_001": InvestigationCase(
            case_id="CASE_001",
            customer_id="CUST_001",
            account_id="high_risk_account_001",
            alert_type=AlertType.CASH_STRUCTURING,
            description="Multiple cash deposits just under $10,000 in 5 days",
            priority="high",
            time_period_days=14,
            customer_explanation="Restaurant business doing really well",
            alert_source="Branch manager",
        ),
        "CASE_002": InvestigationCase(
            case_id="CASE_002",
            customer_id="CUST_002",
            account_id="business_account_002",
            alert_type=AlertType.WIRE_TRANSFER,
            description="Multiple international wire transfers to high-risk countries",
            priority="high",
            time_period_days=30,
            customer_explanation="Import/export business transactions",
            alert_source="Automated monitoring system",
        ),
        "CASE_003": InvestigationCase(
            case_id="CASE_003",
            customer_id="CUST_003",
            account_id="normal_account",
            alert_type=AlertType.UNUSUAL_ACTIVITY,
            description="Standard account activity - control case",
            priority="low",
            time_period_days=30,
            customer_explanation="Regular salary and expenses",
            alert_source="Random review",
        ),
    }
    return cases.get(case_id)


def display_results(result):
    """Display investigation results in a formatted way."""
    
    # Main result panel
    result_text = f"""
[bold]Case ID:[/bold] {result.case_id}
[bold]Investigation ID:[/bold] {result.investigation_id}
[bold]Duration:[/bold] {result.investigation_duration_seconds:.2f} seconds
[bold]Iterations:[/bold] {result.iterations}
[bold]Tools Used:[/bold] {len(result.tool_executions)}
    """
    console.print(Panel(result_text, title="Investigation Summary", border_style="blue"))
    
    # Risk assessment
    risk_color = "red" if result.final_risk_score >= 7 else "yellow" if result.final_risk_score >= 4 else "green"
    sar_status = "[bold red]YES[/bold red]" if result.sar_required else "[bold green]NO[/bold green]"
    
    risk_text = f"""
[bold]Risk Score:[/bold] [{risk_color}]{result.final_risk_score}/10[/{risk_color}]
[bold]SAR Required:[/bold] {sar_status}
[bold]Recommendation:[/bold] {result.recommendation}
    """
    console.print(Panel(risk_text, title="Risk Assessment", border_style=risk_color))
    
    # Key findings
    if result.key_findings:
        findings_text = "\n".join(f"• {finding}" for finding in result.key_findings)
        console.print(Panel(findings_text, title="Key Findings", border_style="yellow"))
    
    # Evidence table
    if result.evidence:
        table = Table(title="Evidence Collected", show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan")
        table.add_column("Severity", style="yellow")
        table.add_column("Description")
        
        for evidence in result.evidence[:10]:  # Show first 10
            severity_color = {
                "critical": "red",
                "high": "orange1",
                "medium": "yellow",
                "low": "green"
            }.get(evidence.severity, "white")
            
            table.add_row(
                evidence.evidence_type,
                f"[{severity_color}]{evidence.severity}[/{severity_color}]",
                evidence.description[:80] + "..." if len(evidence.description) > 80 else evidence.description
            )
        
        console.print(table)
    
    # Next steps
    if result.next_steps:
        steps_text = "\n".join(f"• {step}" for step in result.next_steps)
        console.print(Panel(steps_text, title="Recommended Next Steps", border_style="green"))
    
    # SAR reasoning
    if result.sar_reasoning:
        console.print(Panel(result.sar_reasoning, title="SAR Filing Reasoning", border_style="red"))


def run_demo():
    """Run demonstration with multiple cases."""
    console.print("\n[bold cyan]Running Demo Mode - Testing 3 Cases[/bold cyan]\n")
    
    cases = ["CASE_001", "CASE_002", "CASE_003"]
    investigator = ReACTInvestigator()
    
    results_summary = []
    
    for case_id in cases:
        console.print(f"\n{'='*60}")
        console.print(f"[bold]Running Investigation: {case_id}[/bold]")
        console.print(f"{'='*60}\n")
        
        case = get_predefined_case(case_id)
        result = investigator.investigate(case, verbose=False)
        
        results_summary.append({
            "case_id": case_id,
            "risk_score": result.final_risk_score,
            "sar_required": result.sar_required,
            "recommendation": result.recommendation,
            "duration": result.investigation_duration_seconds
        })
        
        display_results(result)
    
    # Summary table
    console.print(f"\n{'='*60}")
    console.print("[bold cyan]DEMO SUMMARY[/bold cyan]")
    console.print(f"{'='*60}\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Case")
    table.add_column("Risk Score")
    table.add_column("SAR Required")
    table.add_column("Duration (s)")
    
    for summary in results_summary:
        risk_color = "red" if summary["risk_score"] >= 7 else "yellow" if summary["risk_score"] >= 4 else "green"
        sar_color = "red" if summary["sar_required"] else "green"
        
        table.add_row(
            summary["case_id"],
            f"[{risk_color}]{summary['risk_score']:.1f}/10[/{risk_color}]",
            f"[{sar_color}]{'YES' if summary['sar_required'] else 'NO'}[/{sar_color}]",
            f"{summary['duration']:.2f}"
        )
    
    console.print(table)


if __name__ == "__main__":
    exit(main())

