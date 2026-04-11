"""
InsureReg - Audit Log Page
📋 View the complete query routing audit trail for regulatory traceability.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from ui.components.styles import get_custom_css
from ui.components.sidebar import render_sidebar
from config.department_config import DEPARTMENT_METADATA

# ─── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="InsureReg | Audit Log",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)
render_sidebar()

# ─── Header ────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📋 Audit Log</h1>
    <p>Complete query routing trail for regulatory traceability and compliance</p>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ─── Load Audit Data ─────────────────────────────────────
try:
    from utils.audit import audit_trail
    logs = audit_trail.get_recent_logs(100)
    dept_stats = audit_trail.get_department_stats()
except Exception as e:
    logs = []
    dept_stats = {}
    st.warning(f"⚠️ Could not load audit logs: {e}")

# ─── Summary Stats ────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{len(logs)}</div>
        <div class="stat-label">Total Queries</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if logs:
        avg_confidence = sum(
            l.get("routing", {}).get("confidence", 0) for l in logs
        ) / len(logs)
    else:
        avg_confidence = 0
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{avg_confidence:.0%}</div>
        <div class="stat-label">Avg Confidence</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    unique_depts = len(dept_stats)
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{unique_depts}</div>
        <div class="stat-label">Departments Used</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# ─── Department Distribution ─────────────────────────────
if dept_stats:
    st.markdown("### 📊 Query Distribution by Department")
    
    # Create a simple bar representation
    max_count = max(dept_stats.values()) if dept_stats else 1
    
    for dept_id, count in sorted(dept_stats.items(), key=lambda x: x[1], reverse=True):
        meta = DEPARTMENT_METADATA.get(dept_id, {"icon": "📄", "name": dept_id})
        pct = count / max_count
        bar_width = int(pct * 100)
        
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; margin: 0.4rem 0; gap: 0.75rem;">
                <span style="width: 180px; font-size: 0.85rem;">{meta.get('icon', '📄')} {meta.get('name', dept_id)}</span>
                <div style="flex: 1; background: rgba(255,255,255,0.05); border-radius: 8px; height: 24px;">
                    <div style="width: {bar_width}%; background: linear-gradient(90deg, #1B4F8A, #2E86DE); 
                                height: 100%; border-radius: 8px; display: flex; align-items: center; 
                                padding-left: 8px; font-size: 0.7rem; color: white; font-weight: 600;">
                        {count}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("")

# ─── Audit Log Entries ────────────────────────────────────
st.markdown("### 📝 Query History")

if not logs:
    st.info("No queries have been processed yet. Go to the Chat page and ask a question!")
else:
    # Filter controls
    filter_col1, filter_col2 = st.columns([2, 1])
    
    with filter_col1:
        search_term = st.text_input("🔍 Search queries", placeholder="Filter by keyword...")
    
    with filter_col2:
        dept_filter = st.selectbox(
            "📂 Filter by Department",
            options=["All"] + [DEPARTMENT_METADATA[d]["name"] for d in DEPARTMENT_METADATA],
        )
    
    # Filter logs
    filtered_logs = logs
    if search_term:
        filtered_logs = [l for l in filtered_logs if search_term.lower() in l.get("query", "").lower()]
    if dept_filter != "All":
        dept_id_filter = None
        for d_id, meta in DEPARTMENT_METADATA.items():
            if meta["name"] == dept_filter:
                dept_id_filter = d_id
                break
        if dept_id_filter:
            filtered_logs = [
                l for l in filtered_logs 
                if l.get("routing", {}).get("department") == dept_id_filter
            ]
    
    st.caption(f"Showing {len(filtered_logs)} of {len(logs)} entries")
    
    # Display entries
    for log in filtered_logs:
        routing = log.get("routing", {})
        dept_id = routing.get("department", "unknown")
        meta = DEPARTMENT_METADATA.get(dept_id, {"icon": "📄", "name": dept_id})
        
        timestamp = log.get("timestamp", "")[:19].replace("T", " ")
        confidence = routing.get("confidence", 0)
        query = log.get("query", "No query")
        response_preview = log.get("response_preview", "")
        reasoning = routing.get("reasoning", "")
        sources_count = log.get("sources_count", 0)
        
        with st.expander(
            f"**#{log.get('id', '?')}** | {meta.get('icon', '📄')} {meta.get('name', dept_id)} | "
            f"🎯 {confidence:.0%} | {timestamp}"
        ):
            st.markdown(f"**🗣️ Query:** {query}")
            st.markdown(f"**📂 Group:** {routing.get('group', '').replace('_', ' ').title()}")
            st.markdown(f"**🏢 Department:** {meta.get('name', dept_id)}")
            st.markdown(f"**🎯 Confidence:** {confidence:.0%}")
            st.markdown(f"**💭 Routing Reasoning:** {reasoning}")
            st.markdown(f"**📚 Sources Used:** {sources_count} documents")
            
            if response_preview:
                st.markdown(f"**📝 Response Preview:**")
                st.text(response_preview)
    
    st.markdown("")

# ─── Clear Logs ──────────────────────────────────────────
st.divider()
col1, col2 = st.columns([3, 1])
with col2:
    if st.button("🗑️ Clear All Logs", type="secondary", use_container_width=True):
        try:
            audit_trail.clear_logs()
            st.success("✅ Audit logs cleared")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {e}")
