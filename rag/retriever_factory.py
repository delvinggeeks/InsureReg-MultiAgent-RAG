"""
InsureReg - Retriever Factory
Creates LangChain retrievers for each department from ChromaDB collections.
"""

from config.settings import RETRIEVAL_K
from rag.vectorstore_manager import vectorstore_manager
from utils.logger import get_logger

logger = get_logger("RetrieverFactory")


class RetrieverFactory:
    """Factory for creating department-specific retrievers."""

    def __init__(self):
        self._retrievers = {}

    def get_retriever(self, department: str):
        """Get or create a retriever for a specific department."""
        if department not in self._retrievers:
            store = vectorstore_manager.get_vectorstore(department)
            self._retrievers[department] = store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": RETRIEVAL_K},
            )
            logger.info(f"Created retriever for: {department} (k={RETRIEVAL_K})")
        return self._retrievers[department]

    def retrieve_documents(self, department: str, query: str) -> list:
        """
        Retrieve relevant documents for a query.

        Strategy:
          1. Try similarity_search_with_relevance_scores (gives scores for display)
          2. If that returns 0 results, fall back to plain similarity_search
          3. Return list of dicts with content, source, score
        """
        try:
            store = vectorstore_manager.get_vectorstore(department)

            # Check if collection has any documents at all
            try:
                doc_count = store._collection.count()
            except Exception:
                doc_count = -1

            if doc_count == 0:
                logger.warning(
                    f"[{department}] Collection is EMPTY — "
                    "please ingest documents on the Upload Documents page."
                )
                return []

            # Primary: similarity search with scores
            try:
                raw = store.similarity_search_with_relevance_scores(query, k=RETRIEVAL_K)
                documents = [
                    {
                        "content":     doc.page_content,
                        "source":      doc.metadata.get("source", "Unknown"),
                        "file_path":   doc.metadata.get("file_path", ""),
                        "page_number": doc.metadata.get("page_number", ""),
                        "score":       round(float(score), 3),
                    }
                    for doc, score in raw
                ]
            except Exception as e:
                logger.warning(f"[{department}] similarity_search_with_relevance_scores failed: {e}. Falling back.")
                documents = []

            # Fallback: plain similarity_search (no score filtering)
            if not documents:
                logger.info(f"[{department}] Falling back to plain similarity_search")
                raw_docs = store.similarity_search(query, k=RETRIEVAL_K)
                documents = [
                    {
                        "content":     doc.page_content,
                        "source":      doc.metadata.get("source", "Unknown"),
                        "file_path":   doc.metadata.get("file_path", ""),
                        "page_number": doc.metadata.get("page_number", ""),
                        "score":       1.0,  # Score unknown in fallback
                    }
                    for doc in raw_docs
                ]

            logger.info(f"[{department}] Retrieved {len(documents)} chunks for: '{query[:60]}'")
            return documents

        except Exception as e:
            logger.error(f"[{department}] Retrieval error: {e}")
            return []

    def get_collection_doc_count(self, department: str) -> int:
        """Return the number of chunks indexed for a department."""
        try:
            store = vectorstore_manager.get_vectorstore(department)
            return store._collection.count()
        except Exception:
            return 0


# Singleton instance
retriever_factory = RetrieverFactory()
