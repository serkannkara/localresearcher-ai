"""Embedding generation using local models."""

import httpx
import logging
from typing import Sequence
from localresearcher.core.config import settings
from localresearcher.core.retry import with_retry

logger = logging.getLogger("localresearcher.rag.embeddings")


class EmbeddingError(Exception):
    """Embedding generation error."""
    pass


class EmbeddingProvider:
    """Generate embeddings using Ollama."""
    
    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_embedding_model
        self.client = httpx.AsyncClient(timeout=60.0)
        logger.info(f"Initialized embedding provider: {self.model}")
    
    @with_retry(max_attempts=3, initial_delay=1.0, exceptions=(httpx.HTTPError, EmbeddingError))
    async def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        if not text or not text.strip():
            raise EmbeddingError("Cannot embed empty text")
        
        try:
            logger.debug(f"Generating embedding for {len(text)} chars")
            
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text,
                },
            )
            
            response.raise_for_status()
            data = response.json()
            
            if "embedding" not in data:
                raise EmbeddingError("Invalid response: missing 'embedding' field")
            
            embedding = data["embedding"]
            
            if not isinstance(embedding, list) or not embedding:
                raise EmbeddingError("Invalid embedding format")
            
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            
            return embedding
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during embedding: {e.response.status_code}")
            raise EmbeddingError(f"Embedding HTTP error: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Request error during embedding: {e}")
            raise EmbeddingError(f"Failed to connect to embedding service: {e}") from e
        except KeyError as e:
            logger.error(f"Invalid response format: {e}")
            raise EmbeddingError("Invalid response format from embedding service") from e
        except Exception as e:
            logger.error(f"Unexpected error in embed: {e}")
            raise
    
    async def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        if not texts:
            return []
        
        logger.info(f"Generating embeddings for {len(texts)} texts")
        
        embeddings: list[list[float]] = []
        for i, text in enumerate(texts):
            try:
                embedding = await self.embed(text)
                embeddings.append(embedding)
                
                if (i + 1) % 10 == 0:
                    logger.debug(f"Progress: {i + 1}/{len(texts)} embeddings generated")
                    
            except Exception as e:
                logger.error(f"Failed to embed text {i}: {e}")
                # Continue with other texts, return empty embedding for failed one
                embeddings.append([])
        
        successful = sum(1 for e in embeddings if e)
        logger.info(f"Successfully generated {successful}/{len(texts)} embeddings")
        
        return embeddings
    
    async def close(self) -> None:
        """Close the HTTP client."""
        logger.debug("Closing embedding client")
        await self.client.aclose()