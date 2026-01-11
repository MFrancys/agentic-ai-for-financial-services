"""Advice response data models."""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime


class ActionItem(BaseModel):
    """A single actionable recommendation."""
    
    priority: int = Field(..., ge=1, le=5, description="Priority (1=highest)")
    action: str = Field(..., min_length=10, description="Action to take")
    reasoning: str = Field(..., description="Why this action is recommended")
    timeline: str = Field(..., description="When to complete this action")
    expected_outcome: str = Field(..., description="Expected result")
    estimated_impact: Optional[str] = Field(default=None, description="Quantified impact if possible")
    
    # Optional details
    steps: Optional[List[str]] = Field(default=None, description="Sub-steps if complex")
    resources: Optional[List[str]] = Field(default=None, description="Helpful resources")
    potential_risks: Optional[List[str]] = Field(default=None, description="Risks to consider")


class FinancialMetrics(BaseModel):
    """Key financial metrics and improvements."""
    
    current_emergency_fund_months: float = Field(..., description="Current coverage")
    target_emergency_fund_months: float = Field(..., description="Target coverage")
    
    current_debt_to_income: Optional[float] = Field(default=None, description="Current DTI ratio")
    target_debt_to_income: Optional[float] = Field(default=None, description="Target DTI ratio")
    
    current_savings_rate: Optional[float] = Field(default=None, description="Current savings %")
    target_savings_rate: Optional[float] = Field(default=None, description="Target savings %")
    
    projected_improvements: Optional[Dict[str, str]] = Field(default=None, description="Expected improvements")


class AdvisorResponse(BaseModel):
    """Complete response from financial advisor."""
    
    # Metadata
    response_id: str = Field(..., description="Unique response ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    persona: str = Field(..., description="Advisor persona used")
    model_used: str = Field(..., description="LLM model used")
    
    # Core Response
    summary: str = Field(..., description="Executive summary of advice")
    action_items: List[ActionItem] = Field(..., description="Prioritized action items")
    
    # Additional Insights
    key_insights: List[str] = Field(default_factory=list, description="Key insights")
    warnings: List[str] = Field(default_factory=list, description="Important warnings")
    opportunities: List[str] = Field(default_factory=list, description="Opportunities identified")
    
    # Metrics
    metrics: Optional[FinancialMetrics] = Field(default=None, description="Financial metrics")
    
    # Supporting Information
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made")
    disclaimers: List[str] = Field(default_factory=list, description="Legal disclaimers")
    next_steps: Optional[str] = Field(default=None, description="What to do after this advice")
    
    # Metadata
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1, description="Confidence in advice")
    estimated_reading_time_minutes: Optional[int] = Field(default=None, description="Reading time")
    
    # Follow-up
    suggested_follow_up_questions: List[str] = Field(default_factory=list, description="Follow-up questions")


class ConversationTurn(BaseModel):
    """A single turn in a conversation."""
    
    turn_id: int = Field(..., ge=1, description="Turn number")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_message: str = Field(..., description="User's message")
    advisor_response: AdvisorResponse = Field(..., description="Advisor's response")


class Conversation(BaseModel):
    """Complete conversation thread."""
    
    conversation_id: str = Field(..., description="Unique conversation ID")
    client_id: Optional[str] = Field(default=None, description="Client identifier")
    persona: str = Field(..., description="Advisor persona")
    started_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    turns: List[ConversationTurn] = Field(default_factory=list, description="Conversation turns")
    
    # Context
    client_profile: Optional[Dict] = Field(default=None, description="Client profile snapshot")
    context_summary: Optional[str] = Field(default=None, description="Conversation context")
    
    # Status
    is_active: bool = Field(default=True, description="Is conversation active")
    requires_human_review: bool = Field(default=False, description="Needs human advisor review")
    
    @property
    def turn_count(self) -> int:
        """Get number of turns."""
        return len(self.turns)
    
    def add_turn(self, user_message: str, advisor_response: AdvisorResponse) -> None:
        """Add a new turn to the conversation."""
        turn = ConversationTurn(
            turn_id=self.turn_count + 1,
            user_message=user_message,
            advisor_response=advisor_response,
        )
        self.turns.append(turn)
        self.updated_at = datetime.utcnow()

