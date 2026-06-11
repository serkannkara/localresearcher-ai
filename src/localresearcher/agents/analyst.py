"""Analyst agent - interprets and analyzes research findings."""

import logging
from localresearcher.llm.base import BaseLLMProvider

logger = logging.getLogger("localresearcher.agents.analyst")


class AnalystError(Exception):
    """Analyst agent error."""
    pass


class AnalystAgent:
    """Agent responsible for analysis and interpretation."""
    
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm
        logger.debug("Initialized AnalystAgent")
    
    async def analyze(self, query: str, plan: str, findings: str) -> str:
        """Analyze research findings."""
        try:
            logger.info(f"Analyzing findings for: {query[:50]}...")
            
            system_prompt = """You are an expert analyst. Your job is to interpret research findings and extract insights.

Your analysis should:
1. Identify key patterns and trends
2. Draw meaningful conclusions
3. Highlight important implications
4. Connect findings to the original query
5. Provide actionable insights

Be objective and evidence-based."""
            
            prompt = f"""Original Query: {query}

Research Plan:
{plan}

Research Findings:
{findings}

Analyze these findings and provide deep insights."""
            
            analysis = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.6,
                max_tokens=2000,
            )
            
            if not analysis or not analysis.strip():
                raise AnalystError("Generated analysis is empty")
            
            logger.info(f"✓ Generated analysis ({len(analysis)} chars)")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise AnalystError(f"Failed to analyze findings: {e}") from e