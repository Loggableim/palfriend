"""
RAG (Retrieval-Augmented Generation) Engine for context-aware responses.
Uses ChromaDB for vector storage and sentence-transformers for embeddings.
"""

import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

log = logging.getLogger("RAGEngine")


class RAGEngine:
    """
    Manages conversational memory using vector embeddings for semantic search.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize RAG engine with ChromaDB.
        
        Args:
            persist_directory: Directory to persist the ChromaDB database
        """
        try:
            self.client = chromadb.Client(Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            ))
            self.collection = self.client.get_or_create_collection(
                name="user_interactions",
                metadata={"hnsw:space": "cosine"}
            )
            log.info(f"RAGEngine initialized with {self.collection.count()} existing memories")
        except Exception as e:
            log.error(f"Failed to initialize RAGEngine: {e}")
            raise
    
    def add_memory(self, user_id: str, text: str, role: str = "user") -> None:
        """
        Store a conversation turn in the vector database.
        
        Args:
            user_id: Unique identifier for the user
            text: The conversation text to store
            role: Role of the speaker ('user' or 'assistant')
        """
        try:
            import uuid
            import datetime
            
            doc_id = f"{user_id}_{role}_{uuid.uuid4().hex[:8]}"
            timestamp = datetime.datetime.now().isoformat()
            
            self.collection.add(
                documents=[text],
                metadatas=[{
                    "user_id": user_id,
                    "role": role,
                    "timestamp": timestamp
                }],
                ids=[doc_id]
            )
            log.debug(f"Added memory for user {user_id}: {text[:50]}...")
        except Exception as e:
            log.error(f"Failed to add memory: {e}")
    
    def get_context(self, query: str, user_id: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from previous interactions.
        
        Args:
            query: The current user query
            user_id: Unique identifier for the user
            n_results: Number of relevant memories to retrieve
        
        Returns:
            List of relevant conversation contexts with metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where={"user_id": user_id}
            )
            
            contexts = []
            if results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    contexts.append({
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results.get('distances') else 0.0
                    })
            
            log.debug(f"Retrieved {len(contexts)} contexts for user {user_id}")
            return contexts
        except Exception as e:
            log.error(f"Failed to get context: {e}")
            return []
    
    def get_memory_summary(self, user_id: str) -> str:
        """
        Get a formatted summary of user's interaction history.
        
        Args:
            user_id: Unique identifier for the user
        
        Returns:
            Formatted string with recent interactions
        """
        try:
            # Get all memories for this user sorted by timestamp
            all_memories = self.collection.get(
                where={"user_id": user_id},
                limit=10
            )
            
            if not all_memories['documents']:
                return "No previous interactions found."
            
            summary_parts = []
            for doc, metadata in zip(all_memories['documents'], all_memories['metadatas']):
                role = metadata.get('role', 'unknown')
                summary_parts.append(f"{role}: {doc}")
            
            return "\n".join(summary_parts[-5:])  # Last 5 interactions
        except Exception as e:
            log.error(f"Failed to get memory summary: {e}")
            return ""
