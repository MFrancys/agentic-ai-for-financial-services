"""Tool execution engine for ReACT framework."""

import json
import re
import time
from typing import Dict, List, Callable, Any, Optional

from .transaction_tools import get_transaction_history, analyze_transaction_patterns
from .customer_tools import get_customer_profile, search_negative_news, assess_customer_risk
from .regulatory_tools import check_regulatory_thresholds, calculate_risk_score, assess_structuring_risk


class ToolExecutor:
    """Executes investigation tools based on LLM actions."""
    
    def __init__(self):
        """Initialize tool executor with available tools."""
        self.tools: Dict[str, Callable] = {
            "get_transaction_history": get_transaction_history,
            "analyze_transaction_patterns": analyze_transaction_patterns,
            "get_customer_profile": get_customer_profile,
            "search_negative_news": search_negative_news,
            "assess_customer_risk": assess_customer_risk,
            "check_regulatory_thresholds": check_regulatory_thresholds,
            "calculate_risk_score": calculate_risk_score,
            "assess_structuring_risk": assess_structuring_risk,
        }
    
    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Parameters for the tool
        
        Returns:
            Tool execution result
        """
        start_time = time.time()
        
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found. Available tools: {', '.join(self.tools.keys())}"
            }
        
        try:
            tool_func = self.tools[tool_name]
            result = tool_func(**parameters)
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                "success": True,
                "tool": tool_name,
                "parameters": parameters,
                "result": result,
                "execution_time_ms": round(execution_time, 2)
            }
        
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "tool": tool_name,
                "parameters": parameters,
                "error": f"Tool execution failed: {str(e)}",
                "execution_time_ms": round(execution_time, 2)
            }
    
    def parse_and_execute(self, llm_response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response for tool calls and execute them.
        
        Args:
            llm_response: LLM response text containing potential tool calls
        
        Returns:
            List of tool execution results
        """
        tool_calls = self._extract_tool_calls(llm_response)
        
        if not tool_calls:
            return []
        
        results = []
        for tool_call in tool_calls:
            result = self.execute(tool_call["tool"], tool_call["parameters"])
            results.append(result)
            
            # Print execution feedback
            if result["success"]:
                print(f"🔧 Executing: {tool_call['tool']}")
                print(f"📝 Parameters: {tool_call['parameters']}")
                print(f"✅ Result: {json.dumps(result['result'], indent=2)}")
            else:
                print(f"❌ Error executing {tool_call['tool']}: {result['error']}")
            print("-" * 40)
        
        return results
    
    def _extract_tool_calls(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract tool calls from LLM response text.
        
        Args:
            text: LLM response text
        
        Returns:
            List of extracted tool calls
        """
        tool_calls = []
        
        # Pattern to match JSON code blocks
        json_pattern = r'```json\s*(\{[\s\S]*?\})\s*```'
        matches = re.finditer(json_pattern, text)
        
        for match in matches:
            try:
                json_str = match.group(1)
                tool_call = json.loads(json_str)
                
                # Validate tool call structure
                if "tool" in tool_call and "parameters" in tool_call:
                    tool_calls.append({
                        "tool": tool_call["tool"],
                        "parameters": tool_call["parameters"]
                    })
            except json.JSONDecodeError as e:
                print(f"⚠️  Failed to parse JSON: {e}")
                continue
        
        return tool_calls
    
    def get_tool_descriptions(self) -> str:
        """Get formatted descriptions of all available tools."""
        descriptions = []
        
        descriptions.append("AVAILABLE INVESTIGATION TOOLS:")
        descriptions.append("")
        descriptions.append("1. get_transaction_history(account_id: str, days: int)")
        descriptions.append("   - Retrieve transaction history for analysis")
        descriptions.append("   - Parameters: account_id (required), days (default: 30)")
        descriptions.append("")
        descriptions.append("2. analyze_transaction_patterns(account_id: str, days: int)")
        descriptions.append("   - Analyze transactions for suspicious patterns")
        descriptions.append("   - Detects: structuring, velocity, round amounts")
        descriptions.append("")
        descriptions.append("3. get_customer_profile(customer_id: str)")
        descriptions.append("   - Get customer demographics and risk information")
        descriptions.append("   - Includes: occupation, income, risk score, previous SARs")
        descriptions.append("")
        descriptions.append("4. assess_customer_risk(customer_id: str)")
        descriptions.append("   - Comprehensive customer risk assessment")
        descriptions.append("   - Combines profile data with negative news")
        descriptions.append("")
        descriptions.append("5. search_negative_news(customer_name: str)")
        descriptions.append("   - Search for adverse media and negative news")
        descriptions.append("   - Checks: PEP status, sanctions, criminal records")
        descriptions.append("")
        descriptions.append("6. check_regulatory_thresholds(transaction_amount: float, transaction_type: str)")
        descriptions.append("   - Check if transaction meets reporting thresholds")
        descriptions.append("   - Evaluates: CTR requirements, structuring indicators")
        descriptions.append("")
        descriptions.append("7. calculate_risk_score(customer_profile: dict, transaction_history: dict)")
        descriptions.append("   - Calculate overall risk score")
        descriptions.append("   - Considers: velocity, amounts, customer factors")
        descriptions.append("")
        descriptions.append("8. assess_structuring_risk(transactions: list)")
        descriptions.append("   - Specific analysis for structuring patterns")
        descriptions.append("   - Identifies: multiple under-threshold transactions")
        
        return "\n".join(descriptions)


# Global executor instance
_executor = None


def get_tool_executor() -> ToolExecutor:
    """Get global tool executor instance."""
    global _executor
    if _executor is None:
        _executor = ToolExecutor()
    return _executor


def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool (convenience function)."""
    executor = get_tool_executor()
    return executor.execute(tool_name, parameters)


def get_available_tools() -> Dict[str, Callable]:
    """Get dictionary of available tools."""
    executor = get_tool_executor()
    return executor.tools

