"""AI Agent for Fraud Detection using ReACT framework."""

import time
import uuid
from datetime import datetime
from typing import Optional
from openai import OpenAI

from ..config import settings
from ..models.fraud_case import FraudCase, FraudDecision, FraudAction
from ..models.investigation_result import InvestigationResult, ToolExecution, Evidence
from ..tools.fraud_detection_tools import (
    analyze_transaction_velocity,
    check_geographic_anomaly,
    analyze_device_fingerprint,
    check_behavioral_anomalies,
    assess_fraud_probability
)
from ..prompts.fraud_detection_prompts import (
    get_fraud_investigation_prompt,
    format_fraud_case_details
)
import json
import re


class FraudDetectionAgent:
    """
    ReACT-based AI agent for fraud detection.
    
    This autonomous agent investigates potential fraud cases by:
    1. Reasoning about fraud indicators
    2. Taking actions using fraud detection tools
    3. Observing results and updating its understanding
    4. Making evidence-based fraud decisions
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_iterations: Optional[int] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """Initialize fraud detection agent."""
        self.model = model or settings.model_name
        self.temperature = temperature or settings.temperature
        self.max_iterations = max_iterations or settings.max_iterations
        
        # Initialize OpenAI client
        client_params = {"api_key": api_key or settings.openai_api_key}
        if base_url or settings.openai_base_url:
            client_params["base_url"] = base_url or settings.openai_base_url
        
        self.client = OpenAI(**client_params)
        
        # Register fraud detection tools
        self.tools = {
            "analyze_transaction_velocity": analyze_transaction_velocity,
            "check_geographic_anomaly": check_geographic_anomaly,
            "analyze_device_fingerprint": analyze_device_fingerprint,
            "check_behavioral_anomalies": check_behavioral_anomalies,
            "assess_fraud_probability": assess_fraud_probability,
        }
    
    def investigate(self, case: FraudCase, verbose: bool = True) -> InvestigationResult:
        """
        Investigate fraud case using autonomous AI agent.
        
        Args:
            case: Fraud case to investigate
            verbose: Whether to print investigation progress
        
        Returns:
            Complete investigation result with fraud decision
        """
        investigation_id = f"FRAUD_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"🤖 FRAUD DETECTION AGENT ACTIVATED")
            print(f"{'='*70}")
            print(f"Investigation ID: {investigation_id}")
            print(f"Case ID: {case.case_id}")
            print(f"Fraud Type: {case.fraud_type}")
            print(f"Description: {case.description}")
            print(f"{'='*70}\n")
        
        # Initialize investigation state
        case_details = format_fraud_case_details(case.model_dump())
        context = ""
        all_tool_executions = []
        all_evidence = []
        reasoning_trace = []
        fraud_indicators = []
        
        # ReACT agent investigation loop
        for iteration in range(1, self.max_iterations + 1):
            if verbose:
                print(f"\n🔄 AGENT ITERATION {iteration}/{self.max_iterations}")
                print("-" * 70)
            
            # Generate investigation prompt
            prompt = get_fraud_investigation_prompt(case_details, context)
            
            # Agent reasoning and action
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=settings.max_tokens,
                )
                
                agent_response = response.choices[0].message.content
                
                if verbose:
                    print(f"\n🧠 AGENT REASONING:\n{agent_response}\n")
                
                reasoning_trace.append(f"Iteration {iteration}: {agent_response}")
                
                # Execute tools requested by agent
                tool_results = self._parse_and_execute_tools(agent_response)
                
                if tool_results:
                    # Record executions
                    for result in tool_results:
                        tool_exec = ToolExecution(
                            tool_name=result["tool"],
                            parameters=result["parameters"],
                            result=result.get("result", {}),
                            execution_time_ms=result.get("execution_time_ms"),
                            success=result["success"],
                            error=result.get("error"),
                        )
                        all_tool_executions.append(tool_exec)
                        
                        # Extract fraud evidence
                        evidence = self._extract_fraud_evidence(result)
                        all_evidence.extend(evidence)
                        
                        # Collect fraud indicators
                        if result["success"] and "fraud_indicators" in result.get("result", {}):
                            fraud_indicators.extend(result["result"]["fraud_indicators"])
                    
                    # Add results to context
                    context += f"\n\nITERATION {iteration} RESULTS:\n"
                    for result in tool_results:
                        if result["success"]:
                            context += f"- {result['tool']}: {result['result']}\n"
                else:
                    # Check if agent made final decision
                    if "FINAL DECISION" in agent_response or "CONFIRMED" in agent_response.upper():
                        if verbose:
                            print("✅ Agent has reached a decision")
                        break
            
            except Exception as e:
                print(f"❌ Error in iteration {iteration}: {str(e)}")
                reasoning_trace.append(f"Iteration {iteration}: ERROR - {str(e)}")
                break
        
        # Compile fraud investigation results
        duration = time.time() - start_time
        result = self._compile_fraud_results(
            case=case,
            investigation_id=investigation_id,
            tool_executions=all_tool_executions,
            evidence=all_evidence,
            reasoning_trace=reasoning_trace,
            fraud_indicators=fraud_indicators,
            duration=duration,
            verbose=verbose,
        )
        
        if verbose:
            print(f"\n{'='*70}")
            print(f"🏁 FRAUD INVESTIGATION COMPLETE")
            print(f"{'='*70}")
            print(f"Decision: {result.recommendation}")
            print(f"Fraud Score: {result.final_risk_score}/10")
            print(f"Duration: {duration:.2f} seconds")
            print(f"{'='*70}\n")
        
        return result
    
    def _parse_and_execute_tools(self, agent_response: str) -> list:
        """Parse agent response and execute requested tools."""
        tool_results = []
        
        # Extract JSON tool calls
        json_pattern = r'```json\s*(\{[\s\S]*?\})\s*```'
        matches = re.finditer(json_pattern, agent_response)
        
        for match in matches:
            try:
                json_str = match.group(1)
                tool_call = json.loads(json_str)
                
                if "tool" in tool_call and "parameters" in tool_call:
                    result = self._execute_tool(tool_call["tool"], tool_call["parameters"])
                    tool_results.append(result)
                    
                    if result["success"]:
                        print(f"🔧 Tool: {tool_call['tool']}")
                        print(f"✅ Result: {json.dumps(result['result'], indent=2)[:200]}...")
                        print("-" * 70)
            
            except json.JSONDecodeError:
                continue
        
        return tool_results
    
    def _execute_tool(self, tool_name: str, parameters: dict) -> dict:
        """Execute a fraud detection tool."""
        start_time = time.time()
        
        if tool_name not in self.tools:
            return {
                "success": False,
                "tool": tool_name,
                "parameters": parameters,
                "error": f"Tool '{tool_name}' not found"
            }
        
        try:
            tool_func = self.tools[tool_name]
            result = tool_func(**parameters)
            execution_time = (time.time() - start_time) * 1000
            
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
                "error": str(e),
                "execution_time_ms": round(execution_time, 2)
            }
    
    def _extract_fraud_evidence(self, tool_result: dict) -> list:
        """Extract evidence from tool execution."""
        evidence = []
        
        if not tool_result.get("success"):
            return evidence
        
        result_data = tool_result.get("result", {})
        tool_name = tool_result["tool"]
        
        # Extract fraud indicators as evidence
        if "fraud_indicators" in result_data:
            for indicator in result_data["fraud_indicators"]:
                evidence.append(Evidence(
                    evidence_type="fraud_indicator",
                    description=indicator,
                    severity="high" if result_data.get("fraud_likelihood") == "high" else "medium",
                    source=tool_name,
                    data={"indicator": indicator}
                ))
        
        # Extract risk indicators
        if "risk_indicators" in result_data:
            for indicator in result_data["risk_indicators"]:
                evidence.append(Evidence(
                    evidence_type="risk_indicator",
                    description=indicator,
                    severity="medium",
                    source=tool_name,
                    data={"indicator": indicator}
                ))
        
        # Extract anomalies
        if "anomalies_detected" in result_data:
            for anomaly in result_data["anomalies_detected"]:
                evidence.append(Evidence(
                    evidence_type="behavioral_anomaly",
                    description=anomaly,
                    severity="high",
                    source=tool_name,
                    data={"anomaly": anomaly}
                ))
        
        return evidence
    
    def _compile_fraud_results(self, **kwargs) -> InvestigationResult:
        """Compile final fraud investigation results."""
        case = kwargs['case']
        evidence = kwargs['evidence']
        tool_executions = kwargs['tool_executions']
        
        # Calculate fraud score from evidence
        fraud_score = self._calculate_fraud_score(evidence, tool_executions)
        
        # Determine fraud decision
        if fraud_score >= 8:
            decision = "CONFIRMED FRAUD"
            action = "Block account immediately and contact customer"
        elif fraud_score >= 6:
            decision = "SUSPECTED FRAUD - High Probability"
            action = "Block transactions and initiate customer verification"
        elif fraud_score >= 4:
            decision = "SUSPECTED FRAUD - Medium Probability"
            action = "Enhanced monitoring and step-up authentication"
        elif fraud_score >= 2:
            decision = "NEEDS REVIEW"
            action = "Monitor closely for additional indicators"
        else:
            decision = "LEGITIMATE ACTIVITY"
            action = "No action required - continue normal monitoring"
        
        # Extract key findings
        key_findings = [e.description for e in evidence if e.severity in ["high", "critical"]][:5]
        
        return InvestigationResult(
            case_id=case.case_id,
            investigation_id=kwargs['investigation_id'],
            status="completed",
            completed_at=datetime.now(),
            iterations=len(kwargs['reasoning_trace']),
            tool_executions=tool_executions,
            evidence=evidence,
            key_findings=key_findings,
            final_risk_score=fraud_score,
            risk_factors=kwargs['fraud_indicators'],
            recommendation=decision,
            sar_required=fraud_score >= 7,  # In fraud context, SAR = fraud report
            sar_reasoning=f"Fraud score: {fraud_score}/10. {action}" if fraud_score >= 7 else None,
            next_steps=[action],
            escalation_required=fraud_score >= 8,
            reasoning_trace=kwargs['reasoning_trace'],
            investigator_model=self.model,
            investigation_duration_seconds=round(kwargs['duration'], 2),
        )
    
    def _calculate_fraud_score(self, evidence: list, tool_executions: list) -> float:
        """Calculate fraud score from evidence."""
        # Check for fraud assessment tool result
        for exec_result in tool_executions:
            if exec_result.tool_name == "assess_fraud_probability":
                return exec_result.result.get("overall_risk_score", 5.0)
        
        # Otherwise calculate from evidence
        score = 0
        for e in evidence:
            if e.severity == "critical":
                score += 3
            elif e.severity == "high":
                score += 2
            elif e.severity == "medium":
                score += 1
        
        return min(score, 10.0)

