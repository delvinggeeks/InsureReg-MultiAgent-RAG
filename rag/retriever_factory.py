"""
InsureReg - Retriever Factory
Creates LangChain retrievers for each department from ChromaDB collections.
"""

from langchain_core.retrievers import BaseRetriever

from config.settings import RETRIEVAL_K, SIMILARITY_THRESHOLD
from rag.vectorstore_manager import vectorstore_manager
from utils.logger import get_logger

logger = get_logger("RetrieverFactory")


class RetrieverFactory:
    """Factory for creating department-specific retrievers."""
    
    def __init__(self):
        self._retrievers = {}
    
    def get_retriever(self, department: str) -> BaseRetriever:
        """
        Get or create a retriever for a specific department.
        Uses MMR (Maximum Marginal Relevance) for diverse retrieval.
        
        Args:
            department: Department identifier
        
        Returns:
            LangChain retriever instance
        """
        if department not in self._retrievers:
            store = vectorstore_manager.get_vectorstore(department)
            
            self._retrievers[department] = store.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": RETRIEVAL_K,
                    "fetch_k": RETRIEVAL_K * 3,  # Fetch more, then diversify
                },
            )
            logger.info(f"Created MMR retriever for department: {department} (k={RETRIEVAL_K})")
        
        return self._retrievers[department]
    
    def retrieve_documents(self, department: str, query: str) -> list:
        """
        Retrieve relevant documents for a query from a department's collection.
        
        Args:
            department: Department identifier
            query: User's search query
        
        Returns:
            List of dicts with 'content', 'source', and 'score' keys
        """
        try:
            store = vectorstore_manager.get_vectorstore(department)
            
            # Use similarity search with scores for transparency
            results = store.similarity_search_with_relevance_scores(
                query, k=RETRIEVAL_K
            )
            
            documents = []
            for doc, score in results:
                if score >= SIMILARITY_THRESHOLD:
                    documents.append({
                        "content": doc.page_content,
                        "source": doc.metadata.get("source", "Unknown"),
                        "file_path": doc.metadata.get("file_path", ""),
                        "page_number": doc.metadata.get("page_number", ""),
                        "score": round(score, 3),
                    })
            
            logger.info(
                f"Retrieved {len(documents)} documents for '{query[:50]}...' "
                f"from {department} (filtered from {len(results)} results)"
            )
            return documents
            
        except Exception as e:
            logger.error(f"Error retrieving documents from {department}: {e}")
            return []


# Singleton instance
retriever_factory = RetrieverFactory()
