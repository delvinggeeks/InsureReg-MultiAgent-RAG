"""
InsureReg - Upload Documents Page
📤 Upload department-specific regulatory documents for RAG ingestion.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from ui.components.styles import get_custom_css
from ui.components.sidebar import render_sidebar
from config.department_config import DEPARTMENT_METADATA, get_department_names
from config.settings import DEPARTMENTS

# ─── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="InsureReg | Upload Documents",
    page_icon="📤",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)
render_sidebar()

# ─── Header ────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📤 Upload Documents</h1>
    <p>Add department-specific regulatory documents to enhance the knowledge base</p>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ─── Department Selector ──────────────────────────────────
dept_names = get_department_names()
dept_options = {f"{DEPARTMENT_METADATA[d_id]['icon']} {d_name}": d_id for d_id, d_name in dept_names}

selected_display = st.selectbox(
    "🏢 Select Target Department",
    options=list(dept_options.keys()),
    help="Choose which department these documents belong to"
)

selected_dept = dept_options[selected_display]
meta = DEPARTMENT_METADATA[selected_dept]

st.markdown(f"""
<div class="dept-card" style="margin: 1rem 0;">
    <div class="dept-icon">{meta['icon']}</div>
    <div class="dept-name">{meta['name']}</div>
    <div class="dept-desc">{meta['description']}</div>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ─── File Upload ──────────────────────────────────────────
st.markdown("##### 📁 Upload Files")
st.markdown("Supported formats: **PDF**, **TXT**, **MD**")

uploaded_files = st.file_uploader(
    "Choose files to upload",
    type=["pdf", "txt", "md"],
    accept_multiple_files=True,
    key="doc_upload",
    help="Upload regulatory documents, policy PDFs, circulars, or SOPs"
)

if uploaded_files:
    st.markdown(f"**{len(uploaded_files)} file(s) selected**")
    
    if st.button("🚀 Ingest Documents", type="primary", use_container_width=True):
        from rag.document_ingestion import ingestion_pipeline
        
        progress_bar = st.progress(0, text="Starting ingestion...")
        results = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress, text=f"Processing: {uploaded_file.name}...")
            
            result = ingestion_pipeline.ingest_uploaded_file(uploaded_file, selected_dept)
            results.append(result)
        
        progress_bar.progress(1.0, text="✅ Ingestion complete!")
        
        # Display results
        st.markdown("")
        st.markdown("##### 📊 Ingestion Results")
        
        for result in results:
            if result["status"] == "success":
                st.success(
                    f"✅ **{result['file']}** — "
                    f"{result['pages_loaded']} pages, "
                    f"{result['chunks_created']} chunks created"
                )
            else:
                st.error(f"❌ **Error**: {result.get('message', 'Unknown error')}")

st.markdown("")
st.divider()

# ─── Ingest Sample Documents ─────────────────────────────
st.markdown("##### 📦 Sample Documents")
st.markdown(
    "The system includes pre-built sample regulatory documents for all departments. "
    "Click below to ingest them into the knowledge base."
)

col1, col2 = st.columns([1, 3])

with col1:
    if st.button("📦 Ingest All Sample Docs", type="secondary", use_container_width=True):
        from rag.document_ingestion import ingestion_pipeline
        
        with st.spinner("⏳ Ingesting sample documents for all 6 departments..."):
            all_results = ingestion_pipeline.ingest_sample_docs()
        
        st.success("✅ Sample documents ingested for all departments!")
        
        for dept_id, results in all_results.items():
            dept_name = DEPARTMENT_METADATA[dept_id]["name"]
            dept_icon = DEPARTMENT_METADATA[dept_id]["icon"]
            total_chunks = sum(r.get("chunks_created", 0) for r in results if r.get("status") == "success")
            st.markdown(f"{dept_icon} **{dept_name}**: {total_chunks} chunks indexed")

with col2:
    st.info(
        "💡 Sample documents contain synthetic IRDAI-style regulatory guidelines covering "
        "all major topics for each department. These are ideal for testing and demonstration."
    )
