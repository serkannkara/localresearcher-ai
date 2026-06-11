"""Text chunking utilities."""

from typing import Sequence


class TextChunker:
    """Simple text chunker with overlap."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk(self, text: str) -> list[str]:
        """Split text into overlapping chunks."""
        if not text or len(text) <= self.chunk_size:
            return [text] if text else []
        
        chunks: list[str] = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary (., !, ?, \n)
            if end < len(text):
                # Look for sentence endings
                last_period = chunk.rfind(".")
                last_exclamation = chunk.rfind("!")
                last_question = chunk.rfind("?")
                last_newline = chunk.rfind("\n")
                
                # Find the best break point
                break_point = max(last_period, last_exclamation, last_question, last_newline)
                
                # Only break if we found a good point in the second half of the chunk
                if break_point > self.chunk_size // 2:
                    chunk = chunk[: break_point + 1]
                    end = start + len(chunk)
            
            # Add non-empty chunks
            cleaned_chunk = chunk.strip()
            if cleaned_chunk:
                chunks.append(cleaned_chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Safety: prevent infinite loops
            if start >= len(text):
                break
        
        return chunks