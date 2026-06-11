"""Intent classification agent."""

from localresearcher.llm.base import BaseLLMProvider
from localresearcher.core.intent import Intent, IntentType, IntentDetectionResult


class IntentClassifier:
    """Classifies user intent before routing to pipeline."""
    
    # Simple pattern matching for common cases
    GREETING_PATTERNS = {
        "hello", "hi", "hey", "greetings", "good morning", 
        "good afternoon", "good evening", "good night"
    }
    
    FAREWELL_PATTERNS = {
        "bye", "goodbye", "see you", "farewell", "take care"
    }
    
    GRATITUDE_PATTERNS = {
        "thanks", "thank you", "thanks a lot", "much appreciated",
        "appreciate it", "thx"
    }
    
    SMALL_TALK_PATTERNS = {
        "how are you", "what can you do", "who are you",
        "what are you", "help", "what is this", "explain yourself"
    }
    
    RESEARCH_KEYWORDS = {
        "analyze", "research", "summarize", "compare", "find",
        "investigate", "explore", "examine", "review", "evaluate",
        "assess", "study", "extract", "identify", "determine",
        "what is", "what are", "explain", "describe", "tell me about"
    }
    
    def __init__(self, llm: BaseLLMProvider):
        self.llm = llm
    
    async def classify(
        self,
        query: str,
        has_documents: bool = False
    ) -> IntentDetectionResult:
        """Classify user intent."""
        query_lower = query.lower().strip()
        
        # CRITICAL: If files provided, it's ALWAYS document analysis
        if has_documents:
            return IntentDetectionResult(
                query=query,
                intent=Intent(
                    type=IntentType.RESEARCH,
                    confidence=0.95,
                    reasoning="Files provided - document analysis mode",
                    requires_documents=True,
                    requires_research=True,
                ),
            )
        
        # Only check greeting/small-talk if NO files provided
        # Fast path: Pattern matching for common intents
        if self._is_greeting(query_lower):
            return IntentDetectionResult(
                query=query,
                intent=Intent(
                    type=IntentType.GREETING,
                    confidence=0.95,
                    reasoning="Query matches greeting pattern",
                    requires_documents=False,
                    requires_research=False,
                ),
                suggested_response=self._get_greeting_response(),
            )
        
        if self._is_farewell(query_lower):
            return IntentDetectionResult(
                query=query,
                intent=Intent(
                    type=IntentType.GREETING,
                    confidence=0.95,
                    reasoning="Query matches farewell pattern",
                    requires_documents=False,
                    requires_research=False,
                ),
                suggested_response=self._get_farewell_response(),
            )
        
        if self._is_gratitude(query_lower):
            return IntentDetectionResult(
                query=query,
                intent=Intent(
                    type=IntentType.GREETING,
                    confidence=0.95,
                    reasoning="Query matches gratitude pattern",
                    requires_documents=False,
                    requires_research=False,
                ),
                suggested_response=self._get_gratitude_response(),
            )
        
        if self._is_small_talk(query_lower):
            return IntentDetectionResult(
                query=query,
                intent=Intent(
                    type=IntentType.SMALL_TALK,
                    confidence=0.90,
                    reasoning="Query is conversational",
                    requires_documents=False,
                    requires_research=False,
                ),
                suggested_response=await self._get_small_talk_response(query),
            )
        
        # Check if it's clearly a research query
        if self._is_research_query(query_lower) or has_documents:
            return IntentDetectionResult(
                query=query,
                intent=Intent(
                    type=IntentType.RESEARCH,
                    confidence=0.85,
                    reasoning="Query contains research keywords or has documents",
                    requires_documents=has_documents,
                    requires_research=True,
                ),
            )
        
        # Ambiguous case: Use LLM for classification
        return await self._classify_with_llm(query, has_documents)
    
    def _is_greeting(self, query: str) -> bool:
        """Check if query is a greeting."""
        return any(pattern in query for pattern in self.GREETING_PATTERNS)
    
    def _is_farewell(self, query: str) -> bool:
        """Check if query is a farewell."""
        return any(pattern in query for pattern in self.FAREWELL_PATTERNS)
    
    def _is_gratitude(self, query: str) -> bool:
        """Check if query is gratitude."""
        return any(pattern in query for pattern in self.GRATITUDE_PATTERNS)
    
    def _is_small_talk(self, query: str) -> bool:
        """Check if query is small talk."""
        return any(pattern in query for pattern in self.SMALL_TALK_PATTERNS)
    
    def _is_research_query(self, query: str) -> bool:
        """Check if query is a research request."""
        return any(keyword in query for keyword in self.RESEARCH_KEYWORDS)
    
    def _get_greeting_response(self) -> str:
        """Generate greeting response."""
        return """Hello! 👋

How can I help you today?

I can assist you with:
• **Analyzing documents** - Deep analysis of PDFs, Markdown, and text files
• **Research tasks** - Comprehensive research on any topic
• **Comparing files** - Side-by-side comparison and contradiction detection
• **Generating reports** - Executive summaries and detailed reports
• **Summarizing content** - Extract key insights from large documents

**Examples:**

• Analyze a PDF:
  `localresearcher ask "Analyze Apple's AI strategy" --files report.pdf`

• Summarize Markdown files:
  `localresearcher ask "Summarize key findings" --files docs/*.md`

• Compare reports:
  `localresearcher ask "Compare quarterly reports" --files Q1.pdf Q2.pdf`

What would you like to explore?"""
    
    def _get_farewell_response(self) -> str:
        """Generate farewell response."""
        return """Goodbye! 👋

Thank you for using LocalResearcherAI. Feel free to come back anytime you need research assistance!"""
    
    def _get_gratitude_response(self) -> str:
        """Generate gratitude response."""
        return """You're welcome! 😊

Happy to help. If you have any more questions or need further research, just ask!"""
    
    async def _get_small_talk_response(self, query: str) -> str:
        """Generate small talk response."""
        system_prompt = """You are LocalResearcherAI, a local-first research assistant.

Keep responses brief, friendly, and helpful. If asked what you can do, explain your research capabilities.

Your key features:
- 100% local processing (privacy-first)
- Multi-agent research pipeline
- Evidence-based analysis
- Support for PDF, Markdown, and text files"""
        
        response = await self.llm.generate(
            prompt=query,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=200,
        )
        
        return response
    
    async def _classify_with_llm(
        self,
        query: str,
        has_documents: bool
    ) -> IntentDetectionResult:
        """Use LLM to classify ambiguous queries."""
        system_prompt = """You are an intent classifier. Classify the user's query into one of these categories:

- GREETING: Casual greetings, thanks, farewells
- SMALL_TALK: Conversational questions about you or capabilities
- RESEARCH: Requests for analysis, research, or investigation
- QUESTION: Simple factual questions

Respond in this exact format:
INTENT: [category]
CONFIDENCE: [0.0-1.0]
REASONING: [brief explanation]"""
        
        prompt = f"""Query: "{query}"
Has documents: {has_documents}

Classify the intent."""
        
        response = await self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=100,
        )
        
        # Parse response
        intent_type = self._parse_intent_from_response(response)
        confidence = self._parse_confidence_from_response(response)
        reasoning = self._parse_reasoning_from_response(response)
        
        # If has documents, it's likely research
        if has_documents and intent_type != IntentType.GREETING:
            intent_type = IntentType.RESEARCH
            confidence = max(confidence, 0.8)
        
        return IntentDetectionResult(
            query=query,
            intent=Intent(
                type=intent_type,
                confidence=confidence,
                reasoning=reasoning,
                requires_documents=has_documents,
                requires_research=(intent_type == IntentType.RESEARCH),
            ),
        )
    
    def _parse_intent_from_response(self, response: str) -> IntentType:
        """Parse intent type from LLM response."""
        response_lower = response.lower()
        
        if "research" in response_lower:
            return IntentType.RESEARCH
        elif "greeting" in response_lower:
            return IntentType.GREETING
        elif "small_talk" in response_lower or "small talk" in response_lower:
            return IntentType.SMALL_TALK
        elif "question" in response_lower:
            return IntentType.QUESTION
        else:
            return IntentType.UNKNOWN
    
    def _parse_confidence_from_response(self, response: str) -> float:
        """Parse confidence score from LLM response."""
        try:
            for line in response.split("\n"):
                if "confidence:" in line.lower():
                    # Extract number
                    import re
                    match = re.search(r"(\d+\.?\d*)", line)
                    if match:
                        return float(match.group(1))
        except Exception:
            pass
        
        return 0.7  # Default confidence
    
    def _parse_reasoning_from_response(self, response: str) -> str:
        """Parse reasoning from LLM response."""
        try:
            for line in response.split("\n"):
                if "reasoning:" in line.lower():
                    return line.split(":", 1)[1].strip()
        except Exception:
            pass
        
        return "Classified by LLM"