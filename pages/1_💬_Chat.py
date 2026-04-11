"""
InsureReg - Chat Page
💬 Main conversational interface with live orchestration trace display.
Uses Streamlit's native st.status() for live agent trace — no raw HTML injection.
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


def render_static_trace(trace: dict):
    """
    Render a compact orchestration summary card after the response is complete.
    Uses only native Streamlit — no raw HTML.
    """
    dept_id    = trace.get("department", "")
    group_id   = trace.get("group", "")
    reasoning  = trace.get("reasoning", "")
    confidence = trace.get("confidence", 0)
    sources_n  = trace.get("sources_count", 0)
    dept_meta  = DEPARTMENT_METADATA.get(dept_id, {"icon": "📄", "name": dept_id})
    group_name = group_id.replace("_", " ").title()
    dept_name  = f"{dept_meta.get('icon','📄')} {dept_meta.get('name', dept_id)}"

    with st.expander("⚡ Agent Orchestration Trace", expanded=False):
        c1, c2, c3 = st.columns(3)
        c1.metric("📂 Group",       group_name)
        c2.metric("🏢 Department",  dept_meta.get("name", dept_id))
        c3.metric("🎯 Confidence",  f"{confidence:.0%}")

        st.divider()

        cols = st.columns([1, 3])
        rows = [
            ("🎯 Orchestrator",  "Query analyzed & routed"),
            ("📂 Group Supervisor", f"Dispatched to {group_name}"),
            (f"{dept_meta.get('icon','📄')} Dept Agent", f"{dept_meta.get('name', dept_id)} agent invoked"),
            ("🔍 RAG Pipeline",  f"{sources_n} chunk(s) retrieved from ChromaDB"),
            ("✍️ GPT-4o-mini",   "Response generated"),
        ]
        for icon_label, value in rows:
            cols[0].markdown(f"✅ **{icon_label}**")
            cols[1].markdown(value)

        if reasoning:
            st.caption(f"💭 *Routing reasoning: {reasoning}*")


def run_with_live_trace(query: str) -> dict:
    """
    Execute the multi-agent pipeline and show a live trace using st.status().
    Returns the full result dict.
    """
    from agents.orchestrator import orchestrator
    from rag.retriever_factory import retriever_factory
    from utils.audit import audit_trail

    routing  = None
    sources  = []
    response = ""

    # ── st.status() gives a native expandable live-updating panel ──
    with st.status("🔄 Routing your query through the agent pipeline...", expanded=True) as status:

        # Step 1 — Orchestrator
        st.write("🎯 **Orchestrator** — Analyzing your query...")
        routing = orchestrator.route(query)
        dept_meta  = DEPARTMENT_METADATA.get(routing.department, {"icon": "📄", "name": routing.department})
        group_name = routing.group.replace("_", " ").title()
        dept_name  = f"{dept_meta.get('icon', '')} {dept_meta.get('name', routing.department)}"
        st.write(f"🎯 **Orchestrator** — Routed to **{group_name}** → **{dept_name}** "
                 f"*(confidence: {routing.confidence:.0%})*")

        # Step 2 — Group Supervisor
        st.write(f"📂 **{group_name} Supervisor** — Selecting department agent...")
        time.sleep(0.15)
        st.write(f"📂 **{group_name} Supervisor** — Dispatched to **{dept_name}**")

        # Step 3 — RAG Retrieval
        st.write(f"{dept_meta.get('icon','📄')} **{dept_meta.get('name')} Agent** — Searching ChromaDB...")
        sources = retriever_factory.retrieve_documents(routing.department, query)
        st.write(f"{dept_meta.get('icon','📄')} **{dept_meta.get('name')} Agent** — "
                 f"Retrieved **{len(sources)} document chunk(s)**")

        # Step 4 — Generate response
        st.write("✍️ **GPT-4o-mini** — Generating response from retrieved context...")

        # Build context
        context_parts = []
        for i, doc in enumerate(sources, 1):
            src  = doc.get("source", "Unknown")
            page = doc.get("page_number", "")
            page_info = f" (Page {page})" if page else ""
            context_parts.append(
                f"[Source {i}: {src}{page_info}] (Relevance: {doc['score']:.1%})\n"
                f"{doc['content']}\n"
            )
        context = "\n".join(context_parts) if context_parts else "No relevant documents found."

        # Call the agent's LLM chain
        supervisor = orchestrator.supervisors[routing.group]
        agent = supervisor.agents[routing.department]
        try:
            response = agent.chain.invoke({"context": context, "query": query})
        except Exception as e:
            response = f"⚠️ Error generating response: {str(e)}"

        # Done
        status.update(
            label=f"✅ Answered by {dept_name} Agent  |  {len(sources)} sources  |  {routing.confidence:.0%} confidence",
            state="complete",
            expanded=False,
        )

    # Audit log
    try:
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
        "routing":  {
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
            # Static trace card (collapsed by default in history)
            if "trace" in msg:
                render_static_trace(msg["trace"])
            st.markdown(msg["content"])
            # Sources expander
            if msg.get("sources"):
                with st.expander(f"📚 Sources ({len(msg['sources'])} documents)"):
                    for src in msg["sources"]:
                        st.markdown(f"**📄 {src.get('source','Unknown')}** — "
                                    f"Relevance: `{src.get('score', 0):.0%}`")
                        st.caption(src.get("content", "")[:250] + "...")
                        st.divider()

# ─── Process Pending Query ─────────────────────────────────
if st.session_state.processing:
    last_user_msg = next(
        (m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"),
        None,
    )

    if last_user_msg:
        with st.chat_message("assistant", avatar="🛡️"):
            try:
                result = run_with_live_trace(last_user_msg)

                # Static trace summary
                render_static_trace(result["trace"])

                # Response
                st.markdown(result["response"])

                # Sources
                if result.get("sources"):
                    with st.expander(f"📚 Sources ({len(result['sources'])} documents)"):
                        for src in result["sources"]:
                            st.markdown(f"**📄 {src.get('source','Unknown')}** — "
                                        f"Relevance: `{src.get('score', 0):.0%}`")
                            st.caption(src.get("content", "")[:250] + "...")
                            st.divider()

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
