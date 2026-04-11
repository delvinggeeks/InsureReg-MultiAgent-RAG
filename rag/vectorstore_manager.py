"""
InsureReg - ChromaDB Vector Store Manager
Manages persistent ChromaDB collections for each department.
"""

import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

from config.settings import (
    CHROMA_PERSIST_DIR,
    EMBEDDING_MODEL,
    OPENAI_API_KEY,
    DEPARTMENTS,
)
from utils.logger import get_logger

logger = get_logger("VectorStoreManager")


class VectorStoreManager:
    """Manages ChromaDB vector store with per-department collections."""
    
    def __init__(self):
        self._embeddings = None
        self._client = None
        self._stores = {}
    
    @property
    def embeddings(self):
        """Lazy-load OpenAI embeddings."""
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(
                model=EMBEDDING_MODEL,
                openai_api_key=OPENAI_API_KEY,
            )
        return self._embeddings
    
    @property
    def client(self):
        """Lazy-load ChromaDB persistent client."""
        if self._client is None:
            self._client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
            logger.info(f"ChromaDB client initialized at: {CHROMA_PERSIST_DIR}")
        return self._client
    
    def get_vectorstore(self, department: str) -> Chroma:
        """
        Get or create a ChromaDB vector store for a specific department.
        
        Args:
            department: Department identifier (e.g., 'life_insurance')
        
        Returns:
            Chroma vector store instance for the department
        """
        if department not in self._stores:
            collection_name = f"insure_reg_{department}"
            
            self._stores[department] = Chroma(
                client=self.client,
                collection_name=collection_name,
                embedding_function=self.embeddings,
            )
            logger.info(f"Vector store loaded for department: {department} (collection: {collection_name})")
        
        return self._stores[department]
    
    def get_collection_stats(self, department: str) -> dict:
        """Get document count and metadata for a department collection."""
        try:
            store = self.get_vectorstore(department)
            collection = store._collection
            count = collection.count()
            return {
                "department": department,
                "document_count": count,
                "status": "active" if count > 0 else "empty",
            }
        except Exception as e:
            logger.error(f"Error getting stats for {department}: {e}")
            return {
                "department": department,
                "document_count": 0,
                "status": "error",
                "error": str(e),
            }
    
    def get_all_stats(self) -> list:
        """Get collection stats for all departments."""
        return [self.get_collection_stats(dept) for dept in DEPARTMENTS]
    
    def delete_collection(self, department: str):
        """Delete a department's collection (for re-ingestion)."""
        try:
            collection_name = f"insure_reg_{department}"
            self.client.delete_collection(collection_name)
            self._stores.pop(department, None)
            logger.info(f"Deleted collection: {collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection for {department}: {e}")


# Singleton instance
vectorstore_manager = VectorStoreManager()
