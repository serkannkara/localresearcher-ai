"""Writer agent - generates final research reports."""

from localresearcher.llm.base import BaseLLMProvider


class WriterAgent:
    """Agent responsible for writing the final research report."""
    
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm
    
    async def write_report(
        self,
        query: str,
        plan: str,
        findings: str,
        analysis: str,
        critique: str,
        has_external_sources: bool = False,
    ) -> str:
        """Write a comprehensive research report."""
        
        # Different prompts based on evidence availability
        if has_external_sources:
            # Evidence-backed mode
            system_prompt = """You are an expert technical writer creating an evidence-backed research report.

Structure your report with:
1. **Executive Summary** - Key takeaways from the documents
2. **Key Findings** - Main discoveries with source citations
3. **Detailed Analysis** - Deep dive into each finding with evidence
4. **Source Evaluation** - Quality and reliability of sources used
5. **Recommendations** - Actionable insights based on evidence
6. **Conclusion** - Final thoughts

IMPORTANT:
- Cite specific documents and page numbers where applicable
- Use phrases like "According to [source]..." or "Based on the provided documents..."
- Be explicit about which findings come from which sources
- Acknowledge any gaps in the available documents

Use clear markdown formatting with headers, lists, and emphasis where appropriate."""
        else:
            # Knowledge mode (no external sources)
            system_prompt = """You are an expert technical writer creating a knowledge-based explanation.

CRITICAL: This response uses ONLY the language model's internal knowledge. There are NO external sources, documents, web searches, interviews, or empirical data.

Structure your response with:
1. **Overview** - General explanation of the topic
2. **Key Concepts** - Main ideas and definitions
3. **Common Understanding** - Typical perspectives and approaches
4. **Considerations** - Important factors to be aware of
5. **Summary** - Brief recap

STRICT RULES FOR LANGUAGE:
- DO NOT claim to have reviewed literature, case studies, or interviews
- DO NOT say "research shows" or "studies indicate" - you have no sources
- DO NOT use phrases like "evidence-backed" or "source-supported"
- DO NOT cite specific papers, articles, or experts as if you have them
- DO NOT make definitive claims about specific companies/products without noting uncertainty

USE SOFT, HONEST LANGUAGE:
- ✅ "Based on general knowledge..."
- ✅ "Commonly understood as..."
- ✅ "Generally speaking..."
- ✅ "From a theoretical perspective..."
- ✅ "One possible approach is to consider..."
- ✅ "Examples based on commonly known use cases..."
- ✅ "It is often suggested that..."
- ✅ "A typical pattern involves..."

WHEN MENTIONING EXAMPLES:
- Always add: "Examples based on commonly known industry use cases" or similar disclaimer
- Use: "Companies like [X] are known to use..." NOT "Company X uses..."
- Add: "Note: These examples represent general industry knowledge and cannot be verified without sources"

Be honest about limitations:
- Acknowledge this is model knowledge, not live research
- Note that information may be outdated
- Suggest using --files for evidence-backed analysis
- Remind that specific claims cannot be verified

Keep it informative but clearly mark it as model-generated knowledge, NOT research."""
        
        prompt = f"""Query: {query}

Research Plan:
{plan}

Findings:
{findings}

Analysis:
{analysis}

Critical Evaluation:
{critique}

Generate the final {'research report based on the provided documents' if has_external_sources else 'knowledge-based explanation using only model knowledge'}."""
        
        report = await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=3000,
        )
        
        return report