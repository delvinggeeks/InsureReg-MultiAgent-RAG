"""
InsureReg - Sidebar Component
Renders the application sidebar with navigation, department info, and branding.
"""

import streamlit as st
from config.department_config import DEPARTMENT_METADATA


def render_sidebar():
    """Render the application sidebar."""
    
    with st.sidebar:
        # ─── Brand Header ──────────────────────
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="
                font-size: 2rem;
                background: linear-gradient(135deg, #1B4F8A, #C9A227);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 0;
                font-weight: 800;
            ">🛡️ InsureReg</h1>
            <p style="
                color: #888;
                font-size: 0.75rem;
                margin-top: 0.25rem;
                letter-spacing: 2px;
                text-transform: uppercase;
            ">AI-Powered Insurance Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # ─── Department Status ─────────────────
        st.markdown("##### 📋 Departments")
        
        for dept_id, meta in DEPARTMENT_METADATA.items():
            st.markdown(
                f"<div style='padding: 0.3rem 0; font-size: 0.85rem;'>"
                f"{meta['icon']} {meta['name']}</div>",
                unsafe_allow_html=True
            )
        
        st.divider()
        
        # ─── Architecture Info ─────────────────
        st.markdown("##### 🏗️ Architecture")
        st.markdown("""
        <div style="font-size: 0.75rem; color: #aaa; line-height: 1.6;">
        <strong>Tier 1:</strong> Orchestrator Agent<br>
        <strong>Tier 2:</strong> 3 Group Supervisors<br>
        <strong>Tier 3:</strong> 6 Department Agents<br>
        <strong>Model:</strong> GPT-4o-mini<br>
        <strong>RAG:</strong> ChromaDB + OpenAI Embeddings
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # ─── Disclaimer ───────────────────────
        st.markdown("""
        <div style="
            font-size: 0.65rem;
            color: #666;
            padding: 0.5rem;
            background: rgba(255,193,7,0.05);
            border-left: 2px solid #C9A227;
            border-radius: 4px;
        ">
        ⚠️ <strong>Disclaimer:</strong> This is a decision-support tool 
        and does not replace regulatory or compliance judgment.
        </div>
        """, unsafe_allow_html=True)
