"""Investigation result models."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ToolExecution(BaseModel):
    """Record of a tool execution during investigation."""
    
    tool_name: str = Field(description="Name of tool executed")
    parameters: dict = Field(description="Parameters passed to tool")
    result: dict = Field(description="Tool execution result")
    timestamp: datetime = Field(default_factory=datetime.now)
    execution_time_ms: Optional[float] = Field(default=None, description="Execution time in milliseconds")
    success: bool = Field(default=True, description="Whether execution succeeded")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class Evidence(BaseModel):
    """Evidence gathered during investigation."""
    
    evidence_type: str = Field(description="Type of evidence")
    description: str = Field(description="Description of evidence")
    severity: str = Field(description="Severity: low, medium, high, critical")
    source: str = Field(description="Source of evidence")
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Optional[dict] = Field(default=None, description="Supporting data")


class InvestigationResult(BaseModel):
    """Complete investigation result."""
    
    case_id: str = Field(description="Case identifier")
    investigation_id: str = Field(description="Unique investigation ID")
    
    # Status
    status: str = Field(description="Investigation status: in_progress, completed, escalated")
    completed_at: Optional[datetime] = Field(default=None)
    
    # ReACT iterations
    iterations: int = Field(description="Number of ReACT iterations performed")
    tool_executions: List[ToolExecution] = Field(default_factory=list, description="All tool executions")
    
    # Evidence and findings
    evidence: List[Evidence] = Field(default_factory=list, description="Evidence collected")
    key_findings: List[str] = Field(default_factory=list, description="Key findings")
    
    # Risk assessment
    final_risk_score: float = Field(description="Final risk score (0-10)", ge=0, le=10)
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    
    # Recommendations
    recommendation: str = Field(description="Investigation recommendation")
    sar_required: bool = Field(description="Whether SAR filing is required")
    sar_reasoning: Optional[str] = Field(default=None, description="Reasoning for SAR decision")
    
    # Action items
    next_steps: List[str] = Field(default_factory=list, description="Recommended next steps")
    escalation_required: bool = Field(default=False, description="Requires escalation")
    
    # Full reasoning trace
    reasoning_trace: List[str] = Field(default_factory=list, description="Complete reasoning trace")
    
    # Metadata
    investigator_model: str = Field(description="AI model used")
    investigation_duration_seconds: Optional[float] = Field(default=None)
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "case_id": "CASE_001",
                "investigation_id": "INV_20250110_001",
                "status": "completed",
                "iterations": 3,
                "final_risk_score": 8.5,
                "recommendation": "File SAR - Evidence of structuring",
                "sar_required": True,
                "key_findings": [
                    "5 cash deposits in 5 days, all under $10,000",
                    "Total amount $48,900 - suspicious velocity",
                    "Customer risk score elevated at 6.2"
                ],
                "investigator_model": "gpt-4o-mini"
            }
        }

