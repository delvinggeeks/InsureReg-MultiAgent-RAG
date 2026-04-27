"""
InsureReg - Department Information Page
📊 Dashboard showing all 6 departments with document counts and embedding status.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from ui.components.styles import get_custom_css
from ui.components.sidebar import render_sidebar
from config.department_config import DEPARTMENT_METADATA
from config.settings import DEPARTMENT_GROUPS

# ─── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="InsureReg | Department Info",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)
render_sidebar()

# ─── Header ────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📊 Department Information</h1>
    <p>Overview of all insurance departments, document status, and vector store health</p>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ─── Load Stats ───────────────────────────────────────────
try:
    from rag.vectorstore_manager import vectorstore_manager
    all_stats = vectorstore_manager.get_all_stats()
    stats_dict = {s["department"]: s for s in all_stats}
except Exception as e:
    stats_dict = {}
    st.warning(f"⚠️ Could not load vector store stats: {e}")

# ─── Summary Stats ────────────────────────────────────────
total_docs = sum(s.get("document_count", 0) for s in stats_dict.values())
active_depts = sum(1 for s in stats_dict.values() if s.get("status") == "active")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{len(DEPARTMENT_METADATA)}</div>
        <div class="stat-label">Total Departments</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{active_depts}</div>
        <div class="stat-label">Active (with docs)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{total_docs}</div>
        <div class="stat-label">Total Chunks Indexed</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{len(DEPARTMENT_GROUPS)}</div>
        <div class="stat-label">Group Supervisors</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")
st.markdown("")

# ─── Department Cards by Group ────────────────────────────
group_names = {
    "individual_protection": ("👤 Individual Protection", "Life Insurance + Health Insurance"),
    "asset_protection": ("🏠 Asset Protection", "Motor Insurance + Home & Property Insurance"),
    "specialty_insurance": ("✈️ Specialty Insurance", "Travel Insurance + Business Insurance"),
}

for group_id, dept_ids in DEPARTMENT_GROUPS.items():
    group_display, group_desc = group_names.get(group_id, (group_id, ""))
    
    st.markdown(f"### {group_display}")
    st.caption(group_desc)
    
    cols = st.columns(2)
    
    for i, dept_id in enumerate(dept_ids):
        meta = DEPARTMENT_METADATA[dept_id]
        stats = stats_dict.get(dept_id, {"document_count": 0, "status": "empty"})
        doc_count = stats.get("document_count", 0)
        status = stats.get("status", "empty")
        
        status_class = "status-active" if status == "active" else "status-empty"
        status_text = f"✅ Active — {doc_count} chunks" if status == "active" else "⏳ No documents indexed"
        
        with cols[i]:
            st.markdown(f"""
            <div class="dept-card">
                <div class="dept-icon">{meta['icon']}</div>
                <div class="dept-name">{meta['name']}</div>
                <div class="dept-desc">{meta['description']}</div>
                <div class="dept-status {status_class}">{status_text}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Show sample queries
            with st.expander(f"💡 Sample Queries for {meta['name']}"):
                for q in meta.get("sample_queries", []):
                    st.markdown(f"- {q}")
    
    st.markdown("")
    st.divider()

# ─── Vector Store Management ─────────────────────────────
st.markdown("### ⚙️ Vector Store Management")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Refresh Stats", use_container_width=True):
        st.rerun()

with col2:
    dept_to_reset = st.selectbox(
        "Select department to reset",
        options=[f"{DEPARTMENT_METADATA[d]['icon']} {DEPARTMENT_METADATA[d]['name']}" for d in DEPARTMENT_METADATA],
        key="reset_dept",
        label_visibility="collapsed"
    )
    
    if st.button("🗑️ Reset Selected Department", type="secondary", use_container_width=True):
        # Find dept_id from display name
        for dept_id, meta in DEPARTMENT_METADATA.items():
            if f"{meta['icon']} {meta['name']}" == dept_to_reset:
                try:
                    vectorstore_manager.delete_collection(dept_id)
                    st.success(f"✅ Reset collection for {meta['name']}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                break
