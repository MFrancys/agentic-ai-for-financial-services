"""Certified Financial Planner (CFP) advisor implementation."""

from src.advisors.base_advisor import BaseFinancialAdvisor
from src.prompts.system_prompts import CFP_FULL_PROMPT


class CFPAdvisor(BaseFinancialAdvisor):
    """Certified Financial Planner persona."""
    
    def get_system_prompt(self) -> str:
        """Get CFP system prompt."""
        return CFP_FULL_PROMPT
    
    def get_persona_name(self) -> str:
        """Get persona name."""
        return "Certified Financial Planner (CFP)"


class CFPBasicAdvisor(BaseFinancialAdvisor):
    """CFP with basic prompt (for comparison)."""
    
    def get_system_prompt(self) -> str:
        """Get basic CFP prompt."""
        from src.prompts.system_prompts import CFP_BASIC_PROMPT
        return CFP_BASIC_PROMPT
    
    def get_persona_name(self) -> str:
        """Get persona name."""
        return "CFP (Basic)"


class CFPExpertiseAdvisor(BaseFinancialAdvisor):
    """CFP with expertise-enhanced prompt (for comparison)."""
    
    def get_system_prompt(self) -> str:
        """Get expertise-enhanced CFP prompt."""
        from src.prompts.system_prompts import CFP_EXPERTISE_PROMPT
        return CFP_EXPERTISE_PROMPT
    
    def get_persona_name(self) -> str:
        """Get persona name."""
        return "CFP (Expertise Enhanced)"

