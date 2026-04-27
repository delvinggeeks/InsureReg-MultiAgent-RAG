"""
InsureReg - Document Ingestion Pipeline
Loads, chunks, embeds, and stores documents into ChromaDB per department.
"""

import os
from pathlib import Path
from typing import List, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from config.settings import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    DOCUMENTS_DIR,
    SAMPLE_DOCS_DIR,
    DEPARTMENTS,
)
from rag.vectorstore_manager import vectorstore_manager
from utils.logger import get_logger

logger = get_logger("DocumentIngestion")


class DocumentIngestionPipeline:
    """Handles loading, chunking, and embedding documents into ChromaDB."""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
    
    def _parse_doc_header(self, content: str, file_name: str) -> dict:
        """
        Extract title, authority, company reference and version from the first
        few lines of an IRDAI guideline document.
        Returns a metadata dict with human-readable display_source.
        """
        lines = [l.strip() for l in content.splitlines() if l.strip()][:10]
        title = authority = company = version = ""
        for line in lines:
            if line.startswith("==") or not line:
                continue
            if not title and line.isupper() and len(line) > 10:
                title = line.title()
            elif "Applicable Authority:" in line:
                authority = line.split("Applicable Authority:", 1)[-1].strip()
            elif "Company Reference:" in line:
                company = line.split("Company Reference:", 1)[-1].strip()
            elif "Document Version:" in line:
                version = line.split("Document Version:", 1)[-1].strip()
        # Build display_source using only ASCII-safe separators (avoid em dash encoding issues)
        parts = [title or file_name]
        if authority:
            parts.append(authority)
        if company:
            parts.append(company)
        if version:
            parts.append(version)
        display = " | ".join(parts)
        return {
            "source":         file_name,
            "display_source": display,
            "doc_title":      title or file_name,
            "authority":      authority,
            "company":        company,
            "version":        version,
        }

    def load_text_file(self, file_path: Path) -> List[Document]:
        """Load a plain text file as a LangChain Document."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            header_meta = self._parse_doc_header(content, file_path.name)
            doc = Document(
                page_content=content,
                metadata={
                    **header_meta,
                    "file_path": str(file_path),
                    "file_type": file_path.suffix,
                },
            )
            return [doc]
        except Exception as e:
            logger.error(f"Error loading text file {file_path}: {e}")
            return []
    
    def load_pdf_file(self, file_path: Path) -> List[Document]:
        """Load a PDF file as LangChain Documents (one per page)."""
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(str(file_path))
            documents = []
            
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    header_meta = self._parse_doc_header(text, file_path.name) if i == 0 else {"source": file_path.name}
                    doc = Document(
                        page_content=text,
                        metadata={
                            **header_meta,
                            "file_path": str(file_path),
                            "file_type": ".pdf",
                            "page_number": i + 1,
                        },
                    )
                    documents.append(doc)
            
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF file {file_path}: {e}")
            return []
    
    def load_file(self, file_path: Path) -> List[Document]:
        """Load a file based on its extension."""
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            return self.load_pdf_file(file_path)
        elif suffix in [".txt", ".md", ".text"]:
            return self.load_text_file(file_path)
        else:
            logger.warning(f"Unsupported file type: {suffix} for file {file_path}")
            return []
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks for embedding."""
        chunks = self.text_splitter.split_documents(documents)
        logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
        return chunks
    
    def ingest_file(self, file_path: Path, department: str) -> dict:
        """
        Full pipeline: load → chunk → embed → store for a single file.
        
        Args:
            file_path: Path to the document file
            department: Department to store the document under
        
        Returns:
            Dict with ingestion results
        """
        logger.info(f"Ingesting file: {file_path.name} → Department: {department}")
        
        # Load
        documents = self.load_file(file_path)
        if not documents:
            return {"status": "error", "message": f"Could not load file: {file_path.name}"}
        
        # Add department metadata
        for doc in documents:
            doc.metadata["department"] = department
        
        # Chunk
        chunks = self.chunk_documents(documents)
        
        # Embed and store
        try:
            store = vectorstore_manager.get_vectorstore(department)
            store.add_documents(chunks)
            
            result = {
                "status": "success",
                "file": file_path.name,
                "department": department,
                "pages_loaded": len(documents),
                "chunks_created": len(chunks),
            }
            logger.info(f"Successfully ingested: {result}")
            return result
        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            return {"status": "error", "message": str(e)}
    
    def ingest_directory(self, directory: Path, department: str) -> List[dict]:
        """Ingest all supported files from a directory for a department."""
        results = []
        
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return results
        
        for file_path in sorted(directory.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in [".pdf", ".txt", ".md"]:
                result = self.ingest_file(file_path, department)
                results.append(result)
        
        return results
    
    def ingest_sample_docs(self) -> dict:
        """Ingest all sample documents for all departments."""
        all_results = {}
        
        for department in DEPARTMENTS:
            dept_dir = SAMPLE_DOCS_DIR / department
            if dept_dir.exists():
                results = self.ingest_directory(dept_dir, department)
                all_results[department] = results
                logger.info(f"Ingested {len(results)} files for {department}")
            else:
                logger.warning(f"No sample docs directory for: {department}")
                all_results[department] = []
        
        return all_results
    
    def ingest_uploaded_file(self, uploaded_file, department: str) -> dict:
        """
        Ingest a Streamlit uploaded file.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            department: Target department
        
        Returns:
            Ingestion result dict
        """
        # Save uploaded file to department directory
        dept_dir = DOCUMENTS_DIR / department
        dept_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = dept_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        logger.info(f"Saved uploaded file: {file_path}")
        
        # Ingest the saved file
        return self.ingest_file(file_path, department)


# Singleton instance
ingestion_pipeline = DocumentIngestionPipeline()
