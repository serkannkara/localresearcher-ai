"""Researcher agent - gathers and synthesizes information."""

import logging
from localresearcher.llm.base import BaseLLMProvider
from localresearcher.rag.vector_store import VectorStore

logger = logging.getLogger("localresearcher.agents.researcher")


class ResearcherError(Exception):
    """Researcher agent error."""
    pass


class ResearcherAgent:
    """Agent responsible for research and information gathering."""
    
    def __init__(self, llm: BaseLLMProvider, vector_store: VectorStore):
        self.llm = llm
        self.vector_store = vector_store
        logger.debug("Initialized ResearcherAgent")
    
    async def research(self, query: str, plan: str) -> str:
        """Conduct research based on the plan."""
        try:
            logger.info(f"Researching: {query[:50]}...")
            
            # Retrieve relevant context from vector store
            try:
                contexts = await self.vector_store.search(query, top_k=5)
            except Exception as e:
                logger.warning(f"Vector search failed: {e}, continuing without context")
                contexts = []
            
            context_text = "\n\n---\n\n".join(contexts) if contexts else "No documents available."
            
            logger.debug(f"Retrieved {len(contexts)} context chunks")
            
            system_prompt = """You are an expert researcher. Your job is to gather, synthesize, and present relevant information.

Follow these principles:
1. Extract key facts and insights from available sources
2. Identify patterns and connections
3. Note any gaps or limitations in the data
4. Cite specific information when possible

Be thorough but concise."""
            
            prompt = f"""Research Plan:
{plan}

Query: {query}

Available Context:
{context_text}

Conduct thorough research and provide key findings."""
            
            findings = await self.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.5,
                max_tokens=2000,
            )
            
            if not findings or not findings.strip():
                raise ResearcherError("Generated findings are empty")
            
            logger.info(f"✓ Generated findings ({len(findings)} chars)")
            
            return findings
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            raise ResearcherError(f"Failed to conduct research: {e}") from e