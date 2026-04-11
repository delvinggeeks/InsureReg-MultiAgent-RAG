"""
InsureReg - Centralized Configuration Settings
All model parameters, paths, and system constants.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ─── Paths ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTORSTORE_DIR = DATA_DIR / "vectorstore"
SAMPLE_DOCS_DIR = DATA_DIR / "sample_docs"
AUDIT_LOG_DIR = DATA_DIR / "audit_logs"

# Create directories if they don't exist
for directory in [DOCUMENTS_DIR, VECTORSTORE_DIR, SAMPLE_DOCS_DIR, AUDIT_LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ─── OpenAI Configuration ──────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Model for all agents (cost-effective)
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.2  # Low temperature for regulatory accuracy

# Embedding model
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536

# ─── RAG Pipeline Settings ─────────────────────────────
CHUNK_SIZE = 1000          # Characters per chunk
CHUNK_OVERLAP = 200        # Overlap between chunks
RETRIEVAL_K = 5            # Number of chunks to retrieve
SIMILARITY_THRESHOLD = 0.0  # Accept all top-k results (no score cutoff)

# ─── ChromaDB Settings ─────────────────────────────────
CHROMA_PERSIST_DIR = str(VECTORSTORE_DIR)

# ─── Department List ───────────────────────────────────
DEPARTMENTS = [
    "life_insurance",
    "health_insurance",
    "motor_insurance",
    "home_property_insurance",
    "travel_insurance",
    "business_insurance",
]

# ─── Group Mapping ─────────────────────────────────────
DEPARTMENT_GROUPS = {
    "individual_protection": ["life_insurance", "health_insurance"],
    "asset_protection": ["motor_insurance", "home_property_insurance"],
    "specialty_insurance": ["travel_insurance", "business_insurance"],
}

# ─── UI Settings ───────────────────────────────────────
APP_TITLE = "InsureReg"
APP_SUBTITLE = "AI-Powered Insurance Regulatory Assistant"
APP_ICON = "🛡️"
