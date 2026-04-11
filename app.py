"""
InsureReg - Main Streamlit Application
🛡️ AI-Powered Insurance Regulatory Assistant
Multi-Agent System with Orchestrator → Group Supervisor → Department Agent hierarchy.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from ui.components.styles import get_custom_css
from ui.components.sidebar import render_sidebar

# ─── Page Configuration ────────────────────────────────────
st.set_page_config(
    page_title="InsureReg | AI Insurance Regulatory Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "InsureReg — Multi-Agent AI Assistant for Insurance Regulatory Interpretation"
    }
)

# ─── Apply Custom CSS ──────────────────────────────────────
st.markdown(get_custom_css(), unsafe_allow_html=True)

# ─── Render Sidebar ────────────────────────────────────────
render_sidebar()

# ─── Main Landing Page ─────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🛡️ InsureReg</h1>
    <p>AI-Powered Department-Wise Insurance Regulatory Assistant</p>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ─── Hero Section ──────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-value">6</div>
        <div class="stat-label">Insurance Departments</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-value">3</div>
        <div class="stat-label">Group Supervisors</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="stat-card">
        <div class="stat-value">1</div>
        <div class="stat-label">Orchestrator Agent</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")
st.markdown("")

# ─── Architecture Visualization ────────────────────────────
st.markdown("### 🏗️ Multi-Agent Architecture")
st.markdown("")

arch_col1, arch_col2, arch_col3 = st.columns([1, 2, 1])

with arch_col2:
    st.markdown("""
    ```
                    ┌─────────────────────────┐
                    │    🎯 ORCHESTRATOR       │
                    │   Query Analysis &       │
                    │   Department Routing     │
                    └─────────┬───────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ 👤 GROUP A  │ │ 🏠 GROUP B  │ │ ✈️ GROUP C  │
    │ Individual  │ │   Asset     │ │  Specialty  │
    │ Protection  │ │ Protection  │ │  Insurance  │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
      ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
      │         │    │         │    │         │
      ▼         ▼    ▼         ▼    ▼         ▼
    ❤️ Life  🏥Health 🚗Motor 🏠Home  ✈️Travel 🏢Biz
    ```
    """)

st.markdown("")
st.markdown("")

# ─── Department Overview ──────────────────────────────────
st.markdown("### 📋 Insurance Departments")
st.markdown("")

from config.department_config import DEPARTMENT_METADATA

# Display departments in 2 columns of 3
dept_items = list(DEPARTMENT_METADATA.items())

row1_col1, row1_col2, row1_col3 = st.columns(3)
row2_col1, row2_col2, row2_col3 = st.columns(3)
columns = [row1_col1, row1_col2, row1_col3, row2_col1, row2_col2, row2_col3]

for i, (dept_id, meta) in enumerate(dept_items):
    with columns[i]:
        group_label = meta["group"].replace("_", " ").title()
        st.markdown(f"""
        <div class="dept-card">
            <div class="dept-icon">{meta['icon']}</div>
            <div class="dept-name">{meta['name']}</div>
            <div class="dept-desc">{meta['description'][:100]}...</div>
            <div style="margin-top: 0.75rem;">
                <span class="routing-badge group">{group_label}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")
st.markdown("")

# ─── Getting Started ──────────────────────────────────────
st.markdown("### 🚀 Getting Started")
st.markdown("""
1. **Navigate to 💬 Chat** — Ask any insurance regulatory question
2. **Upload Documents** — Add your own department-specific regulatory PDFs
3. **View Department Info** — Check document count and embedding status
4. **Audit Log** — Review all query routing decisions for traceability
""")

st.markdown("")
st.info(
    "💡 **Tip:** The system comes pre-loaded with sample regulatory documents for all 6 departments. "
    "You can start chatting immediately! Upload your own documents for more accurate responses."
)
