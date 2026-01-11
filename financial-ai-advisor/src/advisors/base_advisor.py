"""
Production-grade base class for financial advisors.

This module provides a robust foundation for AI-powered financial advisors with:
- Comprehensive error handling and retry logic
- Performance monitoring and logging
- Cost tracking and optimization
- Type-safe interfaces with Pydantic models
- Support for multiple LLM providers (OpenAI, Anthropic)
"""

import uuid
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from datetime import datetime

from openai import OpenAI, OpenAIError
from anthropic import Anthropic, AnthropicError

from src.models.client_profile import FinancialScenario, ClientProfile
from src.models.advice_response import AdvisorResponse, ActionItem
from src.prompts.system_prompts import FINANCIAL_DISCLAIMER
from src.config import Config, ModelProvider
from src.utils import (
    LoggerMixin,
    retry_with_backoff,
    timeit,
    log_errors,
    validate_inputs,
)


class AdviceGenerationError(Exception):
    """Raised when advice generation fails."""
    pass


class InvalidModelError(Exception):
    """Raised when an unsupported model is specified."""
    pass


class BaseFinancialAdvisor(ABC, LoggerMixin):
    """
    Base class for all financial advisor personas.
    
    This abstract base class provides the core functionality for generating
    financial advice using large language models. Subclasses must implement
    the get_system_prompt() and get_persona_name() methods to define their
    specific advisor persona.
    
    Features:
        - Automatic retry with exponential backoff
        - Performance monitoring and logging
        - Cost tracking and estimation
        - Support for OpenAI and Anthropic models
        - Type-safe interfaces
        
    Example:
        class MyAdvisor(BaseFinancialAdvisor):
            def get_system_prompt(self) -> str:
                return "You are a financial advisor..."
                
            def get_persona_name(self) -> str:
                return "My Advisor"
    """
    
    def __init__(
        self,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize base advisor.
        
        Args:
            model: LLM model to use (e.g., 'gpt-4o-mini', 'claude-3-sonnet')
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            api_key: API key for LLM provider (defaults to env var)
            
        Raises:
            InvalidModelError: If the specified model is not supported
            ValueError: If configuration validation fails
        """
        self.model = model or Config.DEFAULT_MODEL
        self.temperature = temperature or Config.DEFAULT_TEMPERATURE
        self.max_tokens = max_tokens or Config.DEFAULT_MAX_TOKENS
        
        # Get model configuration
        try:
            self.model_config = Config.get_model_config(self.model)
        except ValueError as e:
            raise InvalidModelError(str(e)) from e
        
        self.provider = self.model_config.provider
        
        # Initialize LLM client
        self.client = self._initialize_client(api_key)
        
        # Metrics
        self.total_requests = 0
        self.total_cost = 0.0
        self.total_tokens = 0
        
        self.logger.info(
            f"Initialized {self.__class__.__name__} with model={self.model}, "
            f"temperature={self.temperature}, max_tokens={self.max_tokens}"
        )
    
    def _initialize_client(self, api_key: Optional[str]) -> Any:
        """
        Initialize the appropriate LLM client based on provider.
        
        Args:
            api_key: Optional API key override
            
        Returns:
            Initialized client (OpenAI or Anthropic)
            
        Raises:
            ValueError: If API key is missing
        """
        if self.provider == ModelProvider.OPENAI:
            key = api_key or Config.OPENAI_API_KEY
            if not key:
                raise ValueError(
                    "OpenAI API key required. Set OPENAI_API_KEY environment "
                    "variable or pass api_key parameter."
                )
            self.logger.debug("Initializing OpenAI client")
            return OpenAI(api_key=key)
        
        elif self.provider == ModelProvider.ANTHROPIC:
            key = api_key or Config.ANTHROPIC_API_KEY
            if not key:
                raise ValueError(
                    "Anthropic API key required. Set ANTHROPIC_API_KEY environment "
                    "variable or pass api_key parameter."
                )
            self.logger.debug("Initializing Anthropic client")
            return Anthropic(api_key=key)
        
        raise InvalidModelError(f"Unsupported provider: {self.provider}")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this advisor persona.
        
        This method must be implemented by subclasses to define their
        specific advisor role and behavior.
        
        Returns:
            System prompt string
        """
        pass
    
    @abstractmethod
    def get_persona_name(self) -> str:
        """
        Get the human-readable name of this advisor persona.
        
        Returns:
            Persona name (e.g., "Certified Financial Planner")
        """
        pass
    
    @timeit
    def generate_user_prompt(self, scenario: FinancialScenario) -> str:
        """
        Generate a structured user prompt from a financial scenario.
        
        Converts the client's financial profile and question into a
        well-formatted prompt that provides context to the LLM.
        
        Args:
            scenario: Client's financial scenario
            
        Returns:
            Formatted user prompt string
        """
        profile = scenario.client_profile
        parts = []
        
        # Header
        parts.append(f"## Client Profile\n")
        parts.append(f"- **Age:** {profile.age}\n")
        if profile.marital_status:
            parts.append(f"- **Marital Status:** {profile.marital_status}\n")
        
        # Income
        parts.append(f"\n## Income\n")
        parts.append(f"- **Annual Salary:** ${profile.income.total_annual:,.2f}\n")
        if scenario.windfall_amount and scenario.windfall_amount > 0:
            parts.append(f"- **Windfall/Bonus:** ${scenario.windfall_amount:,.2f}\n")
        
        # Debts
        if profile.debts.total > 0:
            parts.append(f"\n## Debts (Total: ${profile.debts.total:,.2f})\n")
            debt_items = [
                ("Credit Card", profile.debts.credit_card),
                ("Student Loans", profile.debts.student_loan),
                ("Auto Loan", profile.debts.auto_loan),
                ("Mortgage", profile.debts.mortgage),
            ]
            for name, amount in debt_items:
                if amount > 0:
                    parts.append(f"- **{name}:** ${amount:,.2f}\n")
        
        # Assets
        if profile.assets.total > 0:
            parts.append(f"\n## Assets (Total: ${profile.assets.total:,.2f})\n")
            asset_items = [
                ("Emergency Fund (Checking/Savings)", profile.assets.checking_savings),
                ("401(k)", profile.assets.retirement_401k),
                ("IRA", profile.assets.retirement_ira),
                ("Brokerage Account", profile.assets.brokerage),
            ]
            for name, amount in asset_items:
                if amount > 0:
                    parts.append(f"- **{name}:** ${amount:,.2f}\n")
        
        # Expenses
        parts.append(f"\n## Monthly Expenses: ${profile.expenses.total_monthly:,.2f}\n")
        
        # Employment benefits
        if profile.employer_401k_match and profile.employer_401k_match > 0:
            parts.append(f"- **Employer 401(k) Match:** {profile.employer_401k_match}%\n")
        
        # Goals
        if profile.primary_goals:
            parts.append(f"\n## Financial Goals\n")
            for goal in profile.primary_goals:
                parts.append(f"- {goal.value}\n")
        
        # Additional context
        if scenario.context:
            parts.append(f"\n## Additional Context\n{scenario.context}\n")
        
        # The question
        parts.append(f"\n## Client's Question\n**\"{scenario.question}\"**\n")
        
        prompt = "".join(parts)
        self.logger.debug(f"Generated user prompt ({len(prompt)} chars)")
        
        return prompt
    
    @retry_with_backoff(
        max_retries=3,
        exceptions=(OpenAIError, AnthropicError, ConnectionError),
    )
    @timeit
    @log_errors
    def call_llm(self, system_prompt: str, user_prompt: str) -> tuple[str, Dict[str, int]]:
        """
        Call the LLM with retry logic and error handling.
        
        This method automatically retries on transient failures and tracks
        token usage for cost estimation.
        
        Args:
            system_prompt: System-level instructions
            user_prompt: User's question/context
            
        Returns:
            Tuple of (response_text, usage_dict)
            
        Raises:
            AdviceGenerationError: If advice generation fails after retries
        """
        self.total_requests += 1
        
        try:
            if self.provider == ModelProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                
                text = response.choices[0].message.content
                usage = {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
                
            elif self.provider == ModelProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                )
                
                text = response.content[0].text
                usage = {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                }
            
            else:
                raise AdviceGenerationError(f"Unsupported provider: {self.provider}")
            
            # Update metrics
            self.total_tokens += usage["total_tokens"]
            cost = Config.estimate_cost(
                self.model,
                usage["input_tokens"],
                usage["output_tokens"]
            )
            self.total_cost += cost
            
            self.logger.info(
                f"LLM call successful: {usage['total_tokens']} tokens, "
                f"${cost:.4f} cost"
            )
            
            return text, usage
        
        except (OpenAIError, AnthropicError) as e:
            self.logger.error(f"LLM API error: {e}")
            raise AdviceGenerationError(f"Failed to generate advice: {e}") from e
        
        except Exception as e:
            self.logger.error(f"Unexpected error calling LLM: {e}")
            raise AdviceGenerationError(f"Unexpected error: {e}") from e
    
    def parse_response_to_advice(
        self,
        raw_response: str,
        scenario: FinancialScenario,
        usage: Dict[str, int]
    ) -> AdvisorResponse:
        """
        Parse raw LLM response into structured advice.
        
        Args:
            raw_response: Raw text from LLM
            scenario: Original financial scenario
            usage: Token usage statistics
            
        Returns:
            Structured AdvisorResponse object
        """
        # Extract summary (first paragraph or first 200 chars)
        lines = [l.strip() for l in raw_response.split("\n") if l.strip()]
        summary = lines[0] if lines else raw_response[:200]
        
        # In production, use more sophisticated parsing or structured output
        action_items = [
            ActionItem(
                priority=1,
                action="Review the comprehensive advice provided",
                reasoning="Based on your financial situation analysis",
                timeline="Immediate",
                expected_outcome="Clear understanding of recommended actions",
            )
        ]
        
        cost = Config.estimate_cost(
            self.model,
            usage["input_tokens"],
            usage["output_tokens"]
        )
        
        response = AdvisorResponse(
            response_id=str(uuid.uuid4()),
            persona=self.get_persona_name(),
            model_used=self.model,
            summary=raw_response,  # Store full response
            action_items=action_items,
            disclaimers=[FINANCIAL_DISCLAIMER],
            metadata={
                "tokens_used": usage["total_tokens"],
                "input_tokens": usage["input_tokens"],
                "output_tokens": usage["output_tokens"],
                "estimated_cost": cost,
                "temperature": self.temperature,
                "timestamp": datetime.now().isoformat(),
            }
        )
        
        self.logger.debug(f"Created AdvisorResponse {response.response_id}")
        
        return response
    
    @timeit
    @validate_inputs(
        scenario=lambda s: isinstance(s, FinancialScenario)
    )
    def provide_advice(self, scenario: FinancialScenario) -> AdvisorResponse:
        """
        Generate financial advice for a given scenario.
        
        This is the main entry point for generating advice. It orchestrates
        the entire process: prompt generation, LLM call, response parsing,
        and cost tracking.
        
        Args:
            scenario: Client's financial scenario
            
        Returns:
            Structured advice response
            
        Raises:
            AdviceGenerationError: If advice generation fails
            ValueError: If scenario validation fails
        """
        self.logger.info(
            f"Generating advice for {scenario.client_profile.age}-year-old client"
        )
        
        try:
            # Generate prompts
            system_prompt = self.get_system_prompt()
            user_prompt = self.generate_user_prompt(scenario)
            
            # Call LLM
            raw_response, usage = self.call_llm(system_prompt, user_prompt)
            
            # Parse response
            advice = self.parse_response_to_advice(raw_response, scenario, usage)
            
            self.logger.info(
                f"Successfully generated advice (ID: {advice.response_id})"
            )
            
            return advice
        
        except Exception as e:
            self.logger.error(f"Failed to provide advice: {e}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get performance and cost metrics.
        
        Returns:
            Dictionary with metrics including requests, tokens, and cost
        """
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 4),
            "avg_tokens_per_request": (
                round(self.total_tokens / self.total_requests, 2)
                if self.total_requests > 0 else 0
            ),
            "avg_cost_per_request": (
                round(self.total_cost / self.total_requests, 4)
                if self.total_requests > 0 else 0
            ),
        }
    
    def __repr__(self) -> str:
        """String representation of advisor."""
        return (
            f"{self.__class__.__name__}("
            f"model='{self.model}', "
            f"temperature={self.temperature})"
        )

