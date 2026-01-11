"""ReACT prompts for financial investigation."""

from ..tools.tool_executor import get_tool_executor


REACT_TEMPLATE = """
You are an expert Financial Crimes Investigator specializing in Anti-Money Laundering (AML) compliance.
You use the ReACT (Reasoning and Acting) framework to conduct thorough, evidence-based investigations.

{tool_descriptions}

INVESTIGATION PROCESS - Use THOUGHT → ACTION → OBSERVATION cycle:

THOUGHT: [Analyze what you know and decide what information you need next]
- What evidence do I have so far?
- What gaps remain in my understanding?
- Which tool would provide the most valuable information?

ACTION: [Execute investigation tools using EXACT JSON format]
```json
{{
  "tool": "tool_name",
  "parameters": {{"param1": "value1", "param2": value2}}
}}
```

OBSERVATION: [Analyze the tool results]
- What does this data tell me?
- Does it support or contradict my hypothesis?
- What patterns or red flags do I see?

REPEAT the cycle until you have sufficient evidence for a conclusion.

FINAL RECOMMENDATION: [After gathering all necessary evidence]
- Summary of findings
- Risk assessment
- SAR filing recommendation with supporting evidence
- Specific regulatory concerns identified
- Next steps and action items

CRITICAL RULES:
1. Always use the EXACT JSON format for tool calls
2. Base your conclusions on ACTUAL DATA from tools, not assumptions
3. Consider both exculpatory and inculpatory evidence
4. Follow regulatory guidelines (CTR threshold: $10,000, structuring indicators)
5. Provide clear reasoning for all recommendations
6. If SAR filing is recommended, clearly state why
"""


def get_system_prompt() -> str:
    """Get the system prompt for ReACT investigation."""
    executor = get_tool_executor()
    tool_descriptions = executor.get_tool_descriptions()
    
    return REACT_TEMPLATE.format(tool_descriptions=tool_descriptions)


def get_investigation_prompt(case_details: str, context: str = "") -> str:
    """
    Get investigation prompt with case details and context.
    
    Args:
        case_details: Details of the case to investigate
        context: Additional context from previous iterations
    
    Returns:
        Complete prompt for investigation
    """
    system_prompt = get_system_prompt()
    
    prompt = f"""{system_prompt}

{'=' * 60}
INVESTIGATION CASE
{'=' * 60}

{case_details}

{'=' * 60}
{f'PREVIOUS INVESTIGATION CONTEXT:{chr(10)}{context}{chr(10)}{chr(61) * 60}' if context else ''}

BEGIN YOUR INVESTIGATION:
Use THOUGHT → ACTION → OBSERVATION to systematically investigate this case.
"""
    
    return prompt


def format_case_details(case: dict) -> str:
    """
    Format case details into investigation prompt.
    
    Args:
        case: Investigation case dictionary
    
    Returns:
        Formatted case details
    """
    details = []
    
    details.append(f"📁 CASE ID: {case.get('case_id', 'Unknown')}")
    details.append(f"🚨 ALERT TYPE: {case.get('alert_type', 'Unknown')}")
    details.append(f"📝 DESCRIPTION: {case.get('description', 'No description')}")
    details.append("")
    details.append("CASE INFORMATION:")
    details.append(f"- Customer ID: {case.get('customer_id', 'Unknown')}")
    details.append(f"- Account ID: {case.get('account_id', 'Unknown')}")
    details.append(f"- Time Period: {case.get('time_period_days', 30)} days")
    details.append(f"- Priority: {case.get('priority', 'medium').upper()}")
    
    if case.get('amount'):
        details.append(f"- Amount: ${case.get('amount'):,.2f}")
    
    if case.get('customer_explanation'):
        details.append(f"- Customer Explanation: \"{case.get('customer_explanation')}\"")
    
    if case.get('alert_source'):
        details.append(f"- Alert Source: {case.get('alert_source')}")
    
    details.append("")
    details.append("YOUR TASK:")
    details.append("Investigate this case thoroughly using available tools and determine:")
    details.append("1. Whether the activity is genuinely suspicious")
    details.append("2. If a Suspicious Activity Report (SAR) should be filed")
    details.append("3. What evidence supports your recommendation")
    details.append("4. Any additional actions required")
    
    return "\n".join(details)

