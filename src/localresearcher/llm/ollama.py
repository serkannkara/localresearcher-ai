"""Ollama LLM provider."""

import httpx
import logging
from typing import AsyncIterator
from localresearcher.llm.base import BaseLLMProvider
from localresearcher.core.config import settings
from localresearcher.core.retry import with_retry

logger = logging.getLogger("localresearcher.llm.ollama")


class OllamaError(Exception):
    """Ollama-specific error."""
    pass


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.client = httpx.AsyncClient(timeout=300.0)
        logger.info(f"Initialized Ollama provider: {self.model} @ {self.base_url}")
    
    @with_retry(max_attempts=3, initial_delay=1.0, exceptions=(httpx.HTTPError,))
    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate a response from Ollama."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            logger.debug(f"Generating response with {self.model}")
            
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "message" not in data or "content" not in data["message"]:
                raise OllamaError("Invalid response format from Ollama")
            
            content = data["message"]["content"]
            logger.debug(f"Generated {len(content)} characters")
            
            return content
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Ollama: {e.response.status_code}")
            raise OllamaError(f"Ollama HTTP error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Request error to Ollama: {e}")
            raise OllamaError(f"Failed to connect to Ollama: {e}") from e
        except KeyError as e:
            logger.error(f"Unexpected response format: {e}")
            raise OllamaError("Invalid response format from Ollama") from e
        except Exception as e:
            logger.error(f"Unexpected error in generate: {e}")
            raise
    
    async def generate_stream(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> AsyncIterator[str]:
        """Generate a streaming response from Ollama."""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            logger.debug(f"Streaming response with {self.model}")
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            import json
                            data = json.loads(line)
                            if "message" in data and "content" in data["message"]:
                                yield data["message"]["content"]
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse stream line: {line}")
                            continue
                            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error in stream: {e.response.status_code}")
            raise OllamaError(f"Ollama stream error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Request error in stream: {e}")
            raise OllamaError(f"Failed to connect to Ollama for streaming: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in stream: {e}")
            raise
    
    async def is_available(self) -> bool:
        """Check if Ollama is running and model is available."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags", timeout=5.0)
            response.raise_for_status()
            data = response.json()
            models = [m["name"] for m in data.get("models", [])]
            available = any(self.model in m for m in models)
            
            if available:
                logger.info(f"✓ Model {self.model} is available")
            else:
                logger.warning(f"✗ Model {self.model} not found. Available: {models}")
            
            return available
        except Exception as e:
            logger.error(f"Failed to check Ollama availability: {e}")
            return False
    
    async def close(self) -> None:
        """Close the HTTP client."""
        logger.debug("Closing Ollama client")
        await self.client.aclose()