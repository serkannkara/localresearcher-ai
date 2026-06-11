"""Intent detection and classification."""

from enum import Enum
from pydantic import BaseModel


class IntentType(str, Enum):
    """Types of user intents."""
    
    GREETING = "greeting"
    SMALL_TALK = "small_talk"
    RESEARCH = "research"
    QUESTION = "question"
    UNKNOWN = "unknown"


class Intent(BaseModel):
    """Detected user intent."""
    
    type: IntentType
    confidence: float  # 0.0 - 1.0
    reasoning: str
    requires_documents: bool = False
    requires_research: bool = False


class IntentDetectionResult(BaseModel):
    """Result of intent detection."""
    
    query: str
    intent: Intent
    suggested_response: str | None = None