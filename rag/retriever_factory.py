"""
InsureReg - Retriever Factory
Creates LangChain retrievers for each department from ChromaDB collections.
"""

from config.settings import RETRIEVAL_K, SIMILARITY_THRESHOLD
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

        Queries ChromaDB's native collection API directly to avoid Pydantic
        Document validation errors that occur with LangChain's wrapper when
        stored chunks have None page_content values.
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

            # Query ChromaDB natively — bypasses LangChain Document Pydantic validation
            n = min(RETRIEVAL_K, max(1, doc_count))
            embedding = vectorstore_manager.embeddings.embed_query(query)
            results = store._collection.query(
                query_embeddings=[embedding],
                n_results=n,
                include=["documents", "metadatas", "distances"],
            )

            raw_docs  = results.get("documents",  [[]])[0]   # list[str | None]
            raw_metas = results.get("metadatas",  [[]])[0]   # list[dict | None]
            raw_dists = results.get("distances",  [[]])[0]   # list[float]

            documents = []
            for content, meta, dist in zip(raw_docs, raw_metas, raw_dists):
                content = content or ""
                meta    = meta or {}
                # ChromaDB default is squared L2 distance (∈ [0, 4] for unit vectors).
                # For unit-normalised OpenAI embeddings: cos_sim ≈ 1 - dist/2
                score   = round(max(0.0, min(1.0, 1.0 - float(dist) / 2.0)), 3)
                documents.append({
                    "content":        content,
                    "source":         meta.get("source", "Unknown"),
                    "display_source": meta.get("display_source") or meta.get("source", "Unknown"),
                    "doc_title":      meta.get("doc_title", ""),
                    "authority":      meta.get("authority", ""),
                    "company":        meta.get("company", ""),
                    "version":        meta.get("version", ""),
                    "file_path":      meta.get("file_path", ""),
                    "page_number":    meta.get("page_number", ""),
                    "score":          score,
                })

            # Apply relevance threshold — filters low-quality chunks when configured
            if SIMILARITY_THRESHOLD > 0.0:
                before    = len(documents)
                documents = [d for d in documents if d["score"] >= SIMILARITY_THRESHOLD]
                dropped   = before - len(documents)
                if dropped:
                    logger.info(
                        f"[{department}] Threshold {SIMILARITY_THRESHOLD} removed "
                        f"{dropped} low-relevance chunk(s)"
                    )

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
