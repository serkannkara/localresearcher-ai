"""Base LLM provider interface."""

from abc import ABC, abstractmethod
from typing import AsyncIterator


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        """Generate a streaming response from the LLM."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the LLM provider is available."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the provider and cleanup resources."""
        pass