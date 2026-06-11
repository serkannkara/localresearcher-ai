"""Critic agent - evaluates quality and identifies gaps."""

import logging
from localresearcher.llm.base import BaseLLMProvider

logger = logging.getLogger("localresearcher.agents.critic")


class CriticError(Exception):
    """Critic agent error."""
    pass


class CriticAgent:
    """Agent responsible for critical evaluation."""
    
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm
        logger.debug("Initialized CriticAgent")
    
    async def critique(self, query: str, analysis: str) -> str:
        """Critically evaluate the analysis."""
        try:
            logger.info(f"Critiquing analysis for: {query[:50]}...")
            
            system_prompt = """You are an expert critic. Your job is to evaluate research quality and identify weaknesses.

Evaluate:
1. Logical consistency and reasoning
2. Evidence quality and support
3. Potential biases or blind spots
4. Missing perspectives or data
5. Alternative interpretations

Be constructive and specific."""
            
            prompt = f"""Original Query: {query}

Analysis to Critique:
{analysis}

Provide a critical evaluation. What's strong? What's missing? What could be improved?"""
            
            critique = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1500,
            )
            
            if not critique or not critique.strip():
                raise CriticError("Generated critique is empty")
            
            logger.info(f"✓ Generated critique ({len(critique)} chars)")
            
            return critique
            
        except Exception as e:
            logger.error(f"Critique failed: {e}")
            raise CriticError(f"Failed to critique analysis: {e}") from e