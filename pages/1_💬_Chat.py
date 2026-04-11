"""
InsureReg - Chat Page
💬 Main conversational interface with live orchestration trace display.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import time
import streamlit as st
from ui.components.styles import get_custom_css
from ui.components.sidebar import render_sidebar
from config.department_config import DEPARTMENT_METADATA

# ─── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="InsureReg | Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)
render_sidebar()

# ─── Extra CSS for orchestration trace ────────────────────
st.markdown("""
<style>
.trace-container {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(37, 99, 235, 0.25);
    border-radius: 14px;
    padding: 1rem 1.25rem;
    margin: 0.75rem 0;
    font-family: 'Inter', monospace;
    font-size: 0.82rem;
}
.trace-title {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #60A5FA;
    font-weight: 700;
    margin-bottom: 0.75rem;
}
.trace-step {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    padding: 0.45rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.trace-step:last-child { border-bottom: none; }
.trace-icon { font-size: 1rem; min-width: 22px; }
.trace-label {
    color: #94A3B8;
    font-size: 0.75rem;
    min-width: 130px;
}
.trace-value {
    color: #E2E8F0;
    font-size: 0.8rem;
    font-weight: 500;
}
.trace-value.highlight { color: #34D399; font-weight: 600; }
.trace-value.routing  { color: #C9A227; font-weight: 600; }
.trace-value.dept     { color: #60A5FA; font-weight: 600; }
.trace-value.conf-high   { color: #4ADE80; }
.trace-value.conf-medium { color: #FBBF24; }
.trace-value.conf-low    { color: #F87171; }
.trace-arrow {
    color: #334155;
    font-size: 0.7rem;
    padding: 0.4rem 0;
    text-align: center;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# ─── Header ────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>💬 Insurance Regulatory Chat</h1>
    <p>Ask anything about insurance — watch the multi-agent orchestration happen live</p>
</div>
""", unsafe_allow_html=True)

st.markdown("")

# ─── Initialize State ─────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False


def render_orchestration_trace(trace: dict):
    """Render a styled orchestration trace card from a completed result."""
    dept_id   = trace.get("department", "")
    group_id  = trace.get("group", "")
    reasoning = trace.get("reasoning", "")
    confidence= trace.get("confidence", 0)
    sources   = trace.get("sources_count", 0)
    dept_meta = DEPARTMENT_METADATA.get(dept_id, {"icon": "📄", "name": dept_id})
    group_name = group_id.replace("_", " ").title()
    conf_class = "conf-high" if confidence >= 0.8 else ("conf-medium" if confidence >= 0.5 else "conf-low")

    st.markdown(f"""
    <div class="trace-container">
        <div class="trace-title">⚡ Agent Orchestration Trace</div>
        <div class="trace-step">
            <span class="trace-icon">🎯</span>
            <span class="trace-label">Orchestrator</span>
            <span class="trace-value highlight">Query analyzed → routing decision made</span>
        </div>
        <div class="trace-arrow">└── ↓</div>
        <div class="trace-step">
            <span class="trace-icon">📂</span>
            <span class="trace-label">Group Routed</span>
            <span class="trace-value routing">{group_name}</span>
        </div>
        <div class="trace-arrow">└── ↓</div>
        <div class="trace-step">
            <span class="trace-icon">{dept_meta.get('icon','📄')}</span>
            <span class="trace-label">Dept Agent</span>
            <span class="trace-value dept">{dept_meta.get('name', dept_id)}</span>
        </div>
        <div class="trace-arrow">└── ↓</div>
        <div class="trace-step">
            <span class="trace-icon">🔍</span>
            <span class="trace-label">RAG Retrieved</span>
            <span class="trace-value">{sources} document chunk(s) from ChromaDB</span>
        </div>
        <div class="trace-arrow">└── ↓</div>
        <div class="trace-step">
            <span class="trace-icon">🎯</span>
            <span class="trace-label">Confidence</span>
            <span class="trace-value {conf_class}">{confidence:.0%}</span>
        </div>
        <div class="trace-step">
            <span class="trace-icon">💭</span>
            <span class="trace-label">Reasoning</span>
            <span class="trace-value" style="color:#94A3B8;font-style:italic;">{reasoning}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def run_with_live_trace(query: str):
    """
    Execute the multi-agent pipeline while showing a live step-by-step trace.
    Returns the full result dict.
    """
    from agents.orchestrator import orchestrator
    from config.department_config import DEPARTMENT_METADATA

    # Container that will hold the live trace
    trace_box = st.empty()

    def show(step: int, label: str, value: str, icon: str = "⏳"):
        """Update the live trace box with current progress."""
        steps_html = ""
        all_steps = [
            ("🎯", "Orchestrator",  "Analyzing query..."),
            ("📂", "Group Routing", "Identifying group..."),
            ("🏢", "Dept Agent",    "Selecting department..."),
            ("🔍", "RAG Pipeline",  "Retrieving documents..."),
            ("✍️", "Generating",    "Writing response..."),
        ]
        for i, (ico, lbl, placeholder) in enumerate(all_steps):
            if i < step:
                status_icon = "✅"
                val_class   = "highlight"
            elif i == step:
                status_icon = icon
                val_class   = "routing"
            else:
                status_icon = "⏳"
                val_class   = ""

            display_val = value if i == step else (placeholder if i > step else all_steps[i][2])
            if i < step:
                display_val = ["Query analyzed", "Group routed", "Department selected", "Documents retrieved", "Response ready"][i]

            steps_html += f"""
            <div class="trace-step">
                <span class="trace-icon">{status_icon}</span>
                <span class="trace-label">{lbl}</span>
                <span class="trace-value {val_class}">{display_val}</span>
            </div>
            """
            if i < 4:
                steps_html += '<div class="trace-arrow">└── ↓</div>'

        trace_box.markdown(f"""
        <div class="trace-container">
            <div class="trace-title">⚡ Live Agent Orchestration</div>
            {steps_html}
        </div>
        """, unsafe_allow_html=True)

    # ── Step 0: Orchestrator analyzing ─────────────────────
    show(0, "Orchestrator", "Analyzing query...", "🔄")
    routing = orchestrator.route(query)
    dept_meta  = DEPARTMENT_METADATA.get(routing.department, {"icon": "📄", "name": routing.department})
    group_name = routing.group.replace("_", " ").title()
    time.sleep(0.1)

    # ── Step 1: Group routing ───────────────────────────────
    show(1, "Group Routing", f"→ {group_name}", "🔄")
    time.sleep(0.15)

    # ── Step 2: Department selected ─────────────────────────
    show(2, "Dept Agent", f"→ {dept_meta.get('icon','')} {dept_meta.get('name', routing.department)}", "🔄")
    time.sleep(0.1)

    # ── Step 3: RAG retrieval ───────────────────────────────
    show(3, "RAG Pipeline", "Searching ChromaDB...", "🔄")
    from rag.retriever_factory import retriever_factory
    sources = retriever_factory.retrieve_documents(routing.department, query)
    show(3, "RAG Pipeline", f"Retrieved {len(sources)} chunks", "🔄")
    time.sleep(0.1)

    # ── Step 4: Generating response ─────────────────────────
    show(4, "Generating", "Writing response with GPT-4o-mini...", "🔄")

    # Build context from retrieved docs
    context_parts = []
    for i, doc in enumerate(sources, 1):
        source = doc.get("source", "Unknown")
        page   = doc.get("page_number", "")
        page_info = f" (Page {page})" if page else ""
        context_parts.append(
            f"[Source {i}: {source}{page_info}] (Relevance: {doc['score']:.1%})\n"
            f"{doc['content']}\n"
        )
    context = "\n".join(context_parts) if context_parts else "No relevant documents found."

    # Call the department agent's LLM chain directly
    supervisor = orchestrator.supervisors[routing.group]
    agent = supervisor.agents[routing.department]
    try:
        response = agent.chain.invoke({"context": context, "query": query})
    except Exception as e:
        response = f"⚠️ Error generating response: {str(e)}"

    # ── Done: replace live trace with final trace ───────────
    trace_box.empty()

    # Log audit
    try:
        from utils.audit import audit_trail
        audit_trail.log_query(
            query=query,
            group=routing.group,
            department=routing.department,
            confidence=routing.confidence,
            response=response,
            sources=sources,
            routing_reasoning=routing.reasoning,
        )
    except Exception:
        pass

    return {
        "response": response,
        "sources":  sources,
        "routing": {
            "group":      routing.group,
            "department": routing.department,
            "reasoning":  routing.reasoning,
            "confidence": routing.confidence,
        },
        "trace": {
            "department":    routing.department,
            "group":         routing.group,
            "reasoning":     routing.reasoning,
            "confidence":    routing.confidence,
            "sources_count": len(sources),
        },
    }


# ─── Sample Questions ─────────────────────────────────────
if not st.session_state.messages:
    st.markdown("##### 💡 Try asking one of these:")
    sample_qs = [
        ("❤️", "What is the free-look period for a ULIP policy?"),
        ("🏥", "What is the waiting period for pre-existing diseases?"),
        ("🚗", "How does no-claim bonus transfer work when buying a new car?"),
        ("🏠", "Does home insurance cover damage from waterlogging?"),
        ("✈️", "Is travel insurance mandatory for Schengen visa?"),
        ("🏢", "What are the eligibility criteria for group health insurance?"),
    ]
    cols = st.columns(2)
    for i, (icon, question) in enumerate(sample_qs):
        with cols[i % 2]:
            if st.button(f"{icon} {question}", key=f"sample_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": question})
                st.session_state.processing = True
                st.rerun()
    st.markdown("")

# ─── Display Chat History ─────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🛡️"):
            # Orchestration trace (from history)
            if "trace" in msg:
                render_orchestration_trace(msg["trace"])

            st.markdown(msg["content"])

            # Sources
            if "sources" in msg and msg["sources"]:
                with st.expander(f"📚 View Sources ({len(msg['sources'])} documents retrieved)"):
                    for source in msg["sources"]:
                        st.markdown(f"""
                        <div class="source-card">
                            <span class="source-title">📄 {source.get('source', 'Unknown')}</span>
                            <span class="source-score">Relevance: {source.get('score', 0):.0%}</span>
                            <div class="source-content">{source.get('content', '')[:250]}...</div>
                        </div>
                        """, unsafe_allow_html=True)

# ─── Process Pending Query ─────────────────────────────────
if st.session_state.processing:
    last_user_msg = next(
        (m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"),
        None
    )

    if last_user_msg:
        with st.chat_message("assistant", avatar="🛡️"):
            try:
                result = run_with_live_trace(last_user_msg)

                # Render final trace
                render_orchestration_trace(result["trace"])

                # Render response
                st.markdown(result["response"])

                # Sources
                sources = result.get("sources", [])
                if sources:
                    with st.expander(f"📚 View Sources ({len(sources)} documents retrieved)"):
                        for source in sources:
                            st.markdown(f"""
                            <div class="source-card">
                                <span class="source-title">📄 {source.get('source', 'Unknown')}</span>
                                <span class="source-score">Relevance: {source.get('score', 0):.0%}</span>
                                <div class="source-content">{source.get('content', '')[:250]}...</div>
                            </div>
                            """, unsafe_allow_html=True)

                # Save to history
                st.session_state.messages.append({
                    "role":    "assistant",
                    "content": result["response"],
                    "sources": result.get("sources", []),
                    "trace":   result["trace"],
                })

            except Exception as e:
                err = f"⚠️ Error: {str(e)}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})

    st.session_state.processing = False

# ─── Chat Input ───────────────────────────────────────────
user_input = st.chat_input("Ask an insurance regulatory question...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.processing = True
    st.rerun()
