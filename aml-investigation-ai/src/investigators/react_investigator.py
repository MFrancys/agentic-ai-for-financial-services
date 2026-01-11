"""ReACT-based financial investigation agent."""

import time
import uuid
from datetime import datetime
from typing import Optional
from openai import OpenAI

from ..config import settings
from ..models.investigation_case import InvestigationCase
from ..models.investigation_result import InvestigationResult, ToolExecution, Evidence
from ..tools.tool_executor import get_tool_executor
from ..prompts.react_prompts import get_investigation_prompt, format_case_details


class ReACTInvestigator:
    """
    ReACT-based investigator for financial crimes.
    
    Uses Reasoning and Acting framework to conduct systematic investigations
    by iteratively thinking about the case, using tools to gather evidence,
    and observing results to reach conclusions.
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_iterations: Optional[int] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        """
        Initialize ReACT investigator.
        
        Args:
            model: OpenAI model to use
            temperature: Model temperature
            max_iterations: Maximum ReACT iterations
            api_key: OpenAI API key
            base_url: Optional base URL for OpenAI API
        """
        self.model = model or settings.model_name
        self.temperature = temperature or settings.temperature
        self.max_iterations = max_iterations or settings.max_iterations
        
        # Initialize OpenAI client
        client_params = {
            "api_key": api_key or settings.openai_api_key
        }
        if base_url or settings.openai_base_url:
            client_params["base_url"] = base_url or settings.openai_base_url
        
        self.client = OpenAI(**client_params)
        
        # Initialize tool executor
        self.tool_executor = get_tool_executor()
    
    def investigate(self, case: InvestigationCase, verbose: bool = True) -> InvestigationResult:
        """
        Conduct investigation using ReACT framework.
        
        Args:
            case: Investigation case to analyze
            verbose: Whether to print investigation progress
        
        Returns:
            Complete investigation result with findings and recommendations
        """
        investigation_id = f"INV_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
        start_time = time.time()
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"🚀 STARTING INVESTIGATION: {investigation_id}")
            print(f"{'='*60}")
            print(f"Case ID: {case.case_id}")
            print(f"Alert Type: {case.alert_type}")
            print(f"Description: {case.description}")
            print(f"{'='*60}\n")
        
        # Initialize investigation state
        case_details = format_case_details(case.model_dump())
        context = ""
        all_tool_executions = []
        all_evidence = []
        reasoning_trace = []
        
        # ReACT investigation loop
        for iteration in range(1, self.max_iterations + 1):
            if verbose:
                print(f"\n🔄 ITERATION {iteration}/{self.max_iterations}")
                print("-" * 60)
            
            # Generate investigation prompt
            prompt = get_investigation_prompt(case_details, context)
            
            # Get LLM reasoning and actions
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=settings.max_tokens,
                )
                
                llm_response = response.choices[0].message.content
                
                if verbose:
                    print(f"\n🤖 INVESTIGATOR:\n{llm_response}\n")
                
                reasoning_trace.append(f"Iteration {iteration}: {llm_response}")
                
                # Execute any tool calls found in response
                tool_results = self.tool_executor.parse_and_execute(llm_response)
                
                if tool_results:
                    # Record tool executions
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
                        
                        # Extract evidence from tool results
                        evidence = self._extract_evidence(result)
                        all_evidence.extend(evidence)
                    
                    # Add tool results to context for next iteration
                    context += f"\n\nITERATION {iteration} TOOL RESULTS:\n"
                    for result in tool_results:
                        if result["success"]:
                            context += f"- {result['tool']}: {result['result']}\n"
                        else:
                            context += f"- {result['tool']}: ERROR - {result['error']}\n"
                else:
                    # No tools called - check if final recommendation was made
                    if "FINAL RECOMMENDATION" in llm_response or "SAR" in llm_response.upper():
                        if verbose:
                            print("✅ Investigation complete - final recommendation provided")
                        break
                    else:
                        if verbose:
                            print("⚠️  No tools called - may need more guidance")
            
            except Exception as e:
                print(f"❌ Error in iteration {iteration}: {str(e)}")
                reasoning_trace.append(f"Iteration {iteration}: ERROR - {str(e)}")
                break
        
        # Compile final results
        duration = time.time() - start_time
        result = self._compile_results(
            case=case,
            investigation_id=investigation_id,
            tool_executions=all_tool_executions,
            evidence=all_evidence,
            reasoning_trace=reasoning_trace,
            duration=duration,
            verbose=verbose,
        )
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"🏁 INVESTIGATION COMPLETE")
            print(f"{'='*60}")
            print(f"Duration: {duration:.2f} seconds")
            print(f"Iterations: {len(reasoning_trace)}")
            print(f"Tools Executed: {len(all_tool_executions)}")
            print(f"Evidence Collected: {len(all_evidence)}")
            print(f"\n📊 FINAL RECOMMENDATION:")
            print(f"Risk Score: {result.final_risk_score}/10")
            print(f"SAR Required: {'YES' if result.sar_required else 'NO'}")
            print(f"Recommendation: {result.recommendation}")
            print(f"{'='*60}\n")
        
        return result
    
    def _extract_evidence(self, tool_result: dict) -> list:
        """Extract evidence from tool execution results."""
        evidence = []
        
        if not tool_result.get("success"):
            return evidence
        
        tool_name = tool_result["tool"]
        result_data = tool_result.get("result", {})
        
        # Extract evidence based on tool type
        if tool_name == "analyze_transaction_patterns":
            patterns = result_data.get("patterns_detected", [])
            for pattern in patterns:
                evidence.append(Evidence(
                    evidence_type="transaction_pattern",
                    description=pattern.get("description", ""),
                    severity=pattern.get("severity", "medium"),
                    source=tool_name,
                    data=pattern,
                ))
        
        elif tool_name == "assess_customer_risk":
            risk_factors = result_data.get("risk_factors", [])
            for factor in risk_factors:
                evidence.append(Evidence(
                    evidence_type="risk_factor",
                    description=factor,
                    severity="medium" if "previous" not in factor.lower() else "high",
                    source=tool_name,
                    data={"risk_factor": factor},
                ))
        
        elif tool_name == "assess_structuring_risk":
            if result_data.get("sar_recommended"):
                evidence.append(Evidence(
                    evidence_type="structuring",
                    description=f"Structuring indicators found: {result_data.get('indicators_found', 0)}",
                    severity="critical",
                    source=tool_name,
                    data=result_data,
                ))
        
        elif tool_name == "check_regulatory_thresholds":
            if result_data.get("potential_structuring"):
                evidence.append(Evidence(
                    evidence_type="regulatory",
                    description=f"Transaction ${result_data.get('amount')} below CTR threshold",
                    severity="high",
                    source=tool_name,
                    data=result_data,
                ))
        
        return evidence
    
    def _compile_results(
        self,
        case: InvestigationCase,
        investigation_id: str,
        tool_executions: list,
        evidence: list,
        reasoning_trace: list,
        duration: float,
        verbose: bool = True,
    ) -> InvestigationResult:
        """Compile final investigation results."""
        
        # Calculate final risk score from evidence
        risk_score = self._calculate_final_risk_score(evidence, tool_executions)
        
        # Determine SAR requirement
        sar_required = risk_score >= settings.sar_risk_threshold or any(
            e.severity == "critical" for e in evidence
        )
        
        # Extract key findings
        key_findings = self._extract_key_findings(evidence, tool_executions)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(risk_score, sar_required, evidence)
        
        # Identify risk factors
        risk_factors = [e.description for e in evidence if e.evidence_type == "risk_factor"]
        
        # Determine next steps
        next_steps = self._determine_next_steps(sar_required, risk_score, evidence)
        
        return InvestigationResult(
            case_id=case.case_id,
            investigation_id=investigation_id,
            status="completed",
            completed_at=datetime.now(),
            iterations=len(reasoning_trace),
            tool_executions=tool_executions,
            evidence=evidence,
            key_findings=key_findings,
            final_risk_score=risk_score,
            risk_factors=risk_factors,
            recommendation=recommendation,
            sar_required=sar_required,
            sar_reasoning=self._generate_sar_reasoning(sar_required, evidence) if sar_required else None,
            next_steps=next_steps,
            escalation_required=risk_score >= 9.0,
            reasoning_trace=reasoning_trace,
            investigator_model=self.model,
            investigation_duration_seconds=round(duration, 2),
        )
    
    def _calculate_final_risk_score(self, evidence: list, tool_executions: list) -> float:
        """Calculate final risk score based on evidence."""
        # Check if we have a calculated risk score from tools
        for exec_result in tool_executions:
            if exec_result.tool_name == "calculate_risk_score":
                return exec_result.result.get("final_risk_score", 5.0)
            if exec_result.tool_name == "assess_customer_risk":
                return exec_result.result.get("adjusted_risk_score", 5.0)
        
        # Otherwise, estimate based on evidence severity
        base_score = 5.0
        for e in evidence:
            if e.severity == "critical":
                base_score += 2.0
            elif e.severity == "high":
                base_score += 1.0
            elif e.severity == "medium":
                base_score += 0.5
        
        return min(base_score, 10.0)
    
    def _extract_key_findings(self, evidence: list, tool_executions: list) -> list:
        """Extract key findings from investigation."""
        findings = []
        
        # High and critical severity evidence become key findings
        for e in evidence:
            if e.severity in ["high", "critical"]:
                findings.append(e.description)
        
        # Limit to top 5 findings
        return findings[:5]
    
    def _generate_recommendation(self, risk_score: float, sar_required: bool, evidence: list) -> str:
        """Generate investigation recommendation."""
        if sar_required:
            critical_count = sum(1 for e in evidence if e.severity == "critical")
            if critical_count > 0:
                return f"FILE SAR IMMEDIATELY - Critical evidence detected ({critical_count} critical indicators)"
            return "FILE SAR - Suspicious activity confirmed with substantial evidence"
        
        if risk_score >= 6:
            return "ENHANCED MONITORING - Elevated risk requires increased scrutiny"
        elif risk_score >= 4:
            return "CONTINUED MONITORING - Maintain standard monitoring procedures"
        else:
            return "STANDARD MONITORING - No immediate concerns identified"
    
    def _generate_sar_reasoning(self, sar_required: bool, evidence: list) -> str:
        """Generate reasoning for SAR decision."""
        if not sar_required:
            return None
        
        reasons = []
        for e in evidence:
            if e.severity in ["critical", "high"]:
                reasons.append(f"- {e.description}")
        
        return "SAR filing recommended based on:\n" + "\n".join(reasons[:5])
    
    def _determine_next_steps(self, sar_required: bool, risk_score: float, evidence: list) -> list:
        """Determine recommended next steps."""
        steps = []
        
        if sar_required:
            steps.append("File Suspicious Activity Report (SAR) within required timeframe")
            steps.append("Document all evidence and investigation steps")
            steps.append("Notify compliance management")
        
        if risk_score >= 7:
            steps.append("Enhanced Due Diligence (EDD) required")
            steps.append("Increase transaction monitoring frequency to daily")
        
        if any(e.evidence_type == "structuring" for e in evidence):
            steps.append("Review historical transactions for similar patterns")
            steps.append("Check for related accounts or beneficiaries")
        
        if not steps:
            steps.append("Continue standard monitoring")
            steps.append("Review case in 30 days")
        
        return steps

