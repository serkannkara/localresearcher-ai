"""Vector store using ChromaDB."""

import chromadb
import logging
from pathlib import Path
from typing import Sequence
from localresearcher.core.config import settings
from localresearcher.core.schemas import Document
from localresearcher.rag.chunker import TextChunker
from localresearcher.rag.embeddings import EmbeddingProvider

logger = logging.getLogger("localresearcher.rag.vector_store")


class VectorStoreError(Exception):
    """Vector store operation error."""
    pass


class VectorStore:
    """ChromaDB-based vector store."""
    
    def __init__(
        self,
        persist_directory: Path | None = None,
        collection_name: str = "documents",
    ):
        self.persist_directory = persist_directory or settings.vector_store_path
        self.collection_name = collection_name
        
        try:
            self.client = chromadb.PersistentClient(path=str(self.persist_directory))
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"Initialized vector store at {self.persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise VectorStoreError(f"Failed to initialize vector store: {e}") from e
        
        self.chunker = TextChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        self.embedding_provider = EmbeddingProvider()
    
    async def add_document(self, document: Document) -> None:
        """Add a document to the vector store."""
        try:
            logger.info(f"Adding document: {document.path}")
            
            chunks = self.chunker.chunk(document.content)
            
            if not chunks:
                logger.warning(f"No chunks generated for {document.path}")
                return
            
            logger.debug(f"Generated {len(chunks)} chunks")
            
            embeddings = await self.embedding_provider.embed_batch(chunks)
            
            # Filter out failed embeddings
            valid_data = [
                (chunk, emb, i)
                for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
                if emb  # Skip empty embeddings
            ]
            
            if not valid_data:
                raise VectorStoreError("No valid embeddings generated")
            
            chunks_valid, embeddings_valid, indices = zip(*valid_data)
            
            ids = [f"{document.id}_{i}" for i in indices]
            metadatas = [
                {
                    "doc_id": str(document.id),
                    "path": document.path,
                    "file_type": document.file_type,
                    "chunk_index": i,
                }
                for i in indices
            ]
            
            self.collection.add(
                ids=ids,
                embeddings=list(embeddings_valid),
                documents=list(chunks_valid),
                metadatas=metadatas,
            )
            
            logger.info(f"✓ Added {len(ids)} chunks from {document.path}")
            
        except Exception as e:
            logger.error(f"Failed to add document {document.path}: {e}")
            raise VectorStoreError(f"Failed to add document: {e}") from e
    
    async def search(self, query: str, top_k: int | None = None) -> list[str]:
        """Search for relevant document chunks."""
        try:
            top_k = top_k or settings.top_k_retrieval
            
            logger.debug(f"Searching for: {query[:50]}...")
            
            query_embedding = await self.embedding_provider.embed(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )
            
            if not results["documents"]:
                logger.warning("No results found")
                return []
            
            documents = results["documents"][0]
            logger.debug(f"Found {len(documents)} results")
            
            return documents
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise VectorStoreError(f"Search failed: {e}") from e
    
    async def clear(self) -> None:
        """Clear all documents from the collection."""
        try:
            logger.info("Clearing vector store")
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("✓ Vector store cleared")
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            raise VectorStoreError(f"Failed to clear: {e}") from e
    
    async def close(self) -> None:
        """Close the embedding provider."""
        logger.debug("Closing vector store")
        await self.embedding_provider.close()