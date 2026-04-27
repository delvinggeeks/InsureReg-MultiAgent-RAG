"""
InsureReg - Chat Page
💬 Main conversational interface with department tabs, quick-action buttons, and live orchestration trace.
All 5 Motor Insurance agentic concepts are clearly demonstrated and labeled.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from ui.components.styles import get_custom_css
from ui.components.sidebar import render_sidebar
from config.department_config import DEPARTMENT_METADATA

# --- Page Config ---
st.set_page_config(
    page_title="InsureReg | Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

# Extra CSS for concept badges and dept cards
st.markdown("""
<style>
.concept-badge {
    display:inline-block;
    padding:0.2rem 0.55rem;
    border-radius:20px;
    font-size:0.68rem;
    font-weight:700;
    letter-spacing:0.6px;
    text-transform:uppercase;
    margin-bottom:0.3rem;
}
.badge-intent    { background:rgba(139,92,246,0.30); color:#c4b5fd; border:1px solid rgba(139,92,246,0.60); }
.badge-multirag  { background:rgba(59,130,246,0.30);  color:#93c5fd; border:1px solid rgba(59,130,246,0.60); }
.badge-selfeval  { background:rgba(236,72,153,0.30);  color:#f9a8d4; border:1px solid rgba(236,72,153,0.60); }
.badge-memory    { background:rgba(16,185,129,0.30);  color:#6ee7b7; border:1px solid rgba(16,185,129,0.60); }
.badge-tools     { background:rgba(245,158,11,0.30);  color:#fcd34d; border:1px solid rgba(245,158,11,0.60); }
.badge-reg       { background:rgba(148,163,184,0.25); color:#cbd5e1; border:1px solid rgba(148,163,184,0.50); }
.concept-box {
    background:#0f172a;
    border:1px solid rgba(255,255,255,0.18);
    border-radius:10px;
    padding:0.8rem 1rem 0.85rem 1rem;
    margin-bottom:0.6rem;
}
.concept-box h5 { margin:0.25rem 0 0.2rem 0; font-size:0.84rem; font-weight:700; color:#f1f5f9; }
.concept-box p  { margin:0 0 0.55rem 0; font-size:0.76rem; color:#e2e8f0; font-weight:500; line-height:1.5; }
.dept-desc { font-size:0.78rem; color:#94a3b8; margin:0 0 0.7rem 0; line-height:1.5; }
</style>
""", unsafe_allow_html=True)

render_sidebar()

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>💬 Insurance Regulatory Chat</h1>
    <p>Ask anything about insurance — watch the multi-agent orchestration happen live</p>
</div>
""", unsafe_allow_html=True)

# --- Auto-Ingest ---
if "docs_auto_ingested" not in st.session_state:
    st.session_state.docs_auto_ingested = True
    try:
        from rag.retriever_factory import retriever_factory
        from config.settings import DEPARTMENTS
        total_chunks = sum(retriever_factory.get_collection_doc_count(d) for d in DEPARTMENTS)
        if total_chunks == 0:
            with st.spinner("📦 Loading knowledge base from sample regulatory documents..."):
                from rag.document_ingestion import ingestion_pipeline
                ingestion_pipeline.ingest_sample_docs()
            st.toast("✅ Knowledge base ready! All 6 departments loaded.", icon="🛡️")
    except Exception as e:
        st.warning(f"⚠️ Could not load knowledge base: {e}")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False


def _send(query: str):
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.processing = True
    st.rerun()


# ==========================================================================
# SECTION 1 — DEPARTMENT TABS WITH QUICK ACTIONS
# ==========================================================================
st.markdown("### 🗂️ Department Quick Actions")
st.caption(
    "Select a department and click any button to send to the multi-agent pipeline. "
    "The 🚗 Motor Insurance tab shows all 5 agentic concepts."
)

(
    tab_motor, tab_life, tab_health,
    tab_home, tab_travel, tab_business,
) = st.tabs([
    "🚗 Motor Insurance",
    "❤️ Life Insurance",
    "🏥 Health Insurance",
    "🏠 Home & Property",
    "✈️ Travel Insurance",
    "🏢 Business Insurance",
])


# --------------------------------------------------------------------------
# TAB: MOTOR INSURANCE  (5 agentic concepts)
# --------------------------------------------------------------------------
with tab_motor:
    st.caption("👇 Each section below maps to one agentic concept — click a button, then watch the ⚡ Agent Orchestration Trace in the response to see exactly which concept fired.")

    # CONCEPT 1 — Intent Classification + IRDAI Tools
    st.markdown('''
<div class="concept-box">
<span class="concept-badge badge-intent">🧠 Concept 1 — Intent Classification</span>&nbsp;
<span class="concept-badge badge-tools">🔧 Concept 5 — IRDAI Calculator Tools</span>
<h5>Query intent is classified (regulatory / calculation / coverage / claim / general) and the correct
IRDAI tool is selected automatically.</h5>
<p>
Calculation intents trigger bound LangChain tools:
<code>calculate_idv</code> — IDV using IRDAI depreciation schedule (30% at 3 years) &nbsp;·&nbsp;
<code>calculate_ncb</code> — No Claim Bonus up to 50% &nbsp;·&nbsp;
<code>estimate_od_premium</code> — Own-Damage premium (2.0% for 2-wheelers).</p>
<p style="margin:0;font-size:0.72rem;color:#7c8ba1;">
▶ Trace label: <em>🧠 Intent Classification</em> + <em>🔧 Tools Called</em></p>
</div>
''', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔢 IDV — ₹8L car, 3 years old", key="qa_idv", use_container_width=True,
                     help="Intent=calculation → Tool: calculate_idv → 30% depreciation → ₹5,60,000"):
            _send("A car bought for ₹8 lakhs is now 3 years old. What is the IRDAI IDV?")
    with c2:
        if st.button("💰 NCB — 5 claim-free years", key="qa_ncb", use_container_width=True,
                     help="Intent=calculation → Tool: calculate_ncb → maximum 50% discount"):
            _send("I have 5 consecutive claim-free years. What is my NCB percentage per IRDAI?")
    with c3:
        if st.button("📊 OD Premium — ₹6L bike, 20% NCB", key="qa_od", use_container_width=True,
                     help="Intent=calculation → Tool: estimate_od_premium → 2.0% rate for 2-wheelers"):
            _send("Estimate the own-damage premium for a ₹6 lakh bike, 2 years old, with 20% NCB.")

    # CONCEPT 2 — Multi-Query RAG
    st.markdown('''
<div class="concept-box">
<span class="concept-badge badge-multirag">🔍 Concept 2 — Multi-Query RAG</span>
<h5>1 original query → 3 LLM-generated paraphrases → 4 ChromaDB retrievals → MD5 dedup → top-k unique chunks graded for relevance.</h5>
<p>
Technical or ambiguous regulatory queries are paraphrased to diversify retrieval and cover more of the
knowledge base. Duplicate chunks across sub-queries are removed by MD5 hash before the relevance grader runs.
63 total chunks across 6 departments · score = 1 − dist/2 (cosine approx over squared-L2 metric).</p>
<p style="margin:0;font-size:0.72rem;color:#7c8ba1;">
▶ Trace label: <em>🔍 Multi-Query RAG: N paraphrases → M unique chunks</em></p>
</div>
''', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📄 IMT Endorsements", key="qa_imt", use_container_width=True,
                     help="Technical jargon triggers 3 paraphrases for broader chunk coverage"):
            _send("Explain IMT endorsements under IRDAI motor vehicle tariff for private car OD policy.")
    with c2:
        if st.button("🚦 Compulsory PA Cover", key="qa_pa", use_container_width=True,
                     help="Owner-driver PA cover — Multi-Query diversifies retrieval across terminology"):
            _send("What is compulsory personal accident cover for owner-driver under IRDAI motor guidelines?")
    with c3:
        if st.button("🔄 NCB Transfer — new car", key="qa_ncbtransfer", use_container_width=True,
                     help="Multi-Query finds both NCB rules and transfer procedure chunks"):
            _send("How does the no-claim bonus transfer work when I buy a new car?")

    # CONCEPT 3 — Self-Evaluation
    st.markdown('''
<div class="concept-box">
<span class="concept-badge badge-selfeval">🔎 Concept 3 — Self-Evaluation (Corrective RAG)</span>
<h5>After generation, a second LLM call scores the response 1–5 and checks groundedness.
Score &lt; 3 triggers automatic regeneration with a stricter prompt.</h5>
<p>
The evaluator checks (a) completeness — how fully the answer covers the query, and
(b) groundedness — whether every claim is anchored to a retrieved document ("grounded=yes").
Tool-based answers (IDV/NCB) bypass grounding since they are already IRDAI-compliant ground truth.
</p>
<p style="margin:0;font-size:0.72rem;color:#7c8ba1;">
▶ Trace label: <em>🔎 Self-Evaluation: score N/5 · grounded=yes/no</em></p>
</div>
''', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📝 Multi-intent: IDV+NCB+OD+Flood+Add-ons", key="qa_multi", use_container_width=True,
                     help="Complex → self-eval grades completeness → may regenerate"):
            _send("I need: IDV for my ₹7.5 lakh car (2.5 years old), NCB for 3 claim-free years, "
                  "OD premium estimate, whether engine flood damage is covered, and recommended add-ons.")
    with c2:
        if st.button("❓ Vague query → regeneration test", key="qa_vague", use_container_width=True,
                     help="Deliberately vague → low self-eval score → system regenerates with stricter prompt"):
            _send("insurance?")

    # CONCEPT 4 — Conversational Memory
    st.markdown('''
<div class="concept-box">
<span class="concept-badge badge-memory">💬 Concept 4 — Conversational Memory (Rolling k=3 Window)</span>
<h5>Last 3 turns are loaded into LangGraph state, enabling coherent follow-up questions without repeating yourself.</h5>
<p>
Prior messages are injected before retrieval, so pronouns and references
("that IDV", "the premium we discussed") resolve correctly across turns.
Window capped at k=3 to keep context manageable.
<strong>Send Turn 1 → Turn 2 → Turn 3 in sequence to see it in action.</strong>
</p>
<p style="margin:0;font-size:0.72rem;color:#7c8ba1;">
▶ Trace label: <em>💬 Conversational Memory: N prior turn(s) loaded</em></p>
</div>
''', unsafe_allow_html=True)
    st.caption("⚠️ Send Turn 1 → Turn 2 → Turn 3 in order to test rolling memory resolution.")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("💬 Turn 1 — Establish IDV", key="qa_mem1", use_container_width=True):
            _send("My car’s ex-showroom price was ₹7.5 lakhs and it is 2.5 years old. What is my IDV?")
    with c2:
        if st.button("💬 Turn 2 — NCB & OD follow-up", key="qa_mem2", use_container_width=True):
            _send("Based on that IDV, if I have 3 claim-free years what is my NCB and final OD premium?")
    with c3:
        if st.button("💬 Turn 3 — Add-on recommendations", key="qa_mem3", use_container_width=True):
            _send("Given the vehicle value and premium we discussed, which add-on covers should I buy?")

    # Regulatory & Coverage
    st.markdown('''
<div class="concept-box">
<span class="concept-badge badge-reg">⚖️ Regulatory &amp; Coverage Questions</span>
<h5>Standard RAG path (no tool calls) — demonstrates Multi-Query retrieval + generation + Self-Evaluation grounding check.</h5>
<p>These queries exercise intent=regulatory or coverage. Good for verifying 5 relevant chunks are retrieved per query.</p>
</div>
''', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📜 Is 3rd-party mandatory?", key="qa_3p", use_container_width=True):
            _send("Is third-party motor insurance mandatory under the Motor Vehicles Act?")
    with c2:
        if st.button("🌊 Flood / engine damage covered?", key="qa_flood", use_container_width=True):
            _send("Is engine damage due to flooding or waterlogging covered under motor insurance?")
    with c3:
        if st.button("🛡️ Comprehensive — what’s covered?", key="qa_comp", use_container_width=True):
            _send("What does a comprehensive motor insurance policy cover and exclude?")
    c4, c5, c6 = st.columns(3)
    with c4:
        if st.button("🔄 Renewal rules & grace period", key="qa_renew", use_container_width=True):
            _send("What are the IRDAI regulations for motor insurance policy renewal and grace period?")
    with c5:
        if st.button("➕ Recommended add-ons", key="qa_addon", use_container_width=True):
            _send("What add-on covers should I buy with a comprehensive motor insurance policy?")
    with c6:
        if st.button("📋 Documents to file a claim", key="qa_docs", use_container_width=True):
            _send("What documents do I need to submit when filing a motor insurance claim?")

    # CONCEPTS REFERENCE CARD — inside Motor tab only
    with st.expander("📖 Motor Insurance Agent — 5 Agentic Concepts Reference Card", expanded=False):
        st.markdown("#### How the Motor Insurance LangGraph Agent works")
        concepts = [
            ("🧠", "badge-intent",   "Intent Classification",
             "SVM classifier · 129 training samples · 92.3% macro-F1 · <1ms inference",
             "5 intents: regulatory · calculation · coverage · claim · general"),
            ("🔍", "badge-multirag", "Multi-Query RAG",
             "1 original + 3 LLM paraphrases · 4× ChromaDB queries · MD5 dedup · top-k unique",
             "63 chunks (6 depts) · score = 1−dist/2 (cosine approx from squared-L2)"),
            ("🔎", "badge-selfeval", "Self-Evaluation",
             "2nd LLM call scores 1–5 + grounded=yes/no · score<3 → regenerate",
             "Tool queries bypass grounding check — IRDAI ground truth already"),
            ("💬", "badge-memory",   "Conversational Memory",
             "Rolling k=3 window · prior messages injected into LangGraph state",
             "Enables pronoun resolution across turns without repeating context"),
            ("🔧", "badge-tools",    "IRDAI Tools",
             "calculate_idv · calculate_ncb · estimate_od_premium",
             "IDV: 30% at 3yr · NCB: max 50% · OD: 2.0% for 2-wheelers"),
        ]
        cols = st.columns(5)
        for col, (icon, badge_cls, title, desc1, desc2) in zip(cols, concepts):
            with col:
                st.markdown(
                    f"<div class='concept-box' style='height:100%;'>"
                    f"<span class='concept-badge {badge_cls}'>{icon}</span>"
                    f"<h5>{title}</h5>"
                    f"<p>{desc1}</p>"
                    f"<p style='margin:0;font-size:0.72rem;color:#7c8ba1;'>{desc2}</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )


# --------------------------------------------------------------------------
# TAB: LIFE INSURANCE
# --------------------------------------------------------------------------
with tab_life:
    st.caption("Watch the ⚡ Agent Orchestration Trace in each response to see exactly which concept fired.")
    st.markdown("**Policy & Benefits**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🔓 Free-look period for ULIP", key="li_freelook", use_container_width=True):
            _send("What is the free-look period for a ULIP policy?")
    with c2:
        if st.button("💸 Surrender value — endowment plan", key="li_surr", use_container_width=True):
            _send("What are the surrender value rules for an endowment plan?")
    with c3:
        if st.button("⏳ Grace period for premium payment", key="li_grace", use_container_width=True):
            _send("What is the grace period for premium payment in life insurance?")
    st.markdown("**Claims & Regulations**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📋 Nomination rules in term policy", key="li_nom", use_container_width=True):
            _send("How does nomination work in a term life insurance policy?")
    with c2:
        if st.button("💀 Death claim settlement process", key="li_death", use_container_width=True):
            _send("How are death claim settlements processed under life insurance?")
    with c3:
        if st.button("🔄 ULIP fund switching rules", key="li_switch", use_container_width=True):
            _send("What are the IRDAI guidelines for fund switching in ULIP policies?")
    st.markdown("**Product Comparisons**")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("📊 Term vs Endowment vs ULIP", key="li_compare", use_container_width=True):
            _send("What is the difference between term life, endowment, and ULIP policies under IRDAI?")
    with c2:
        if st.button("🏦 Pension plan annuity options", key="li_pension", use_container_width=True):
            _send("What are the annuity payout options available under IRDAI-regulated pension plans?")


# --------------------------------------------------------------------------
# TAB: HEALTH INSURANCE
# --------------------------------------------------------------------------
with tab_health:
    st.caption("Watch the ⚡ Agent Orchestration Trace in each response to see exactly which concept fired.")
    st.markdown("**Coverage & Waiting Periods**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⏳ Pre-existing disease waiting period", key="hi_ped", use_container_width=True):
            _send("What is the waiting period for pre-existing diseases under health insurance?")
    with c2:
        if st.button("👁️ Cataract surgery — covered?", key="hi_cat", use_container_width=True):
            _send("Is cataract surgery covered under a standard health insurance policy?")
    with c3:
        if st.button("🚑 Maternity benefit rules", key="hi_mat", use_container_width=True):
            _send("What are the IRDAI guidelines for maternity benefit coverage in health insurance?")
    st.markdown("**Claims & Procedures**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏥 Cashless claim at network hospital", key="hi_cashless", use_container_width=True):
            _send("How does the cashless claim process work at network hospitals under health insurance?")
    with c2:
        if st.button("📄 Documents for reimbursement claim", key="hi_docs", use_container_width=True):
            _send("What documents are required for health insurance claim reimbursement?")
    with c3:
        if st.button("🔄 Health insurance portability rules", key="hi_port", use_container_width=True):
            _send("What are the portability rules for health insurance under IRDAI?")
    st.markdown("**TPA & Products**")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏦 TPA role and responsibilities", key="hi_tpa", use_container_width=True):
            _send("What is the role of a Third Party Administrator (TPA) in health insurance?")
    with c2:
        if st.button("💊 Critical illness — coverage scope", key="hi_ci", use_container_width=True):
            _send("What critical illnesses are covered under standard critical illness insurance plans?")


# --------------------------------------------------------------------------
# TAB: HOME & PROPERTY INSURANCE
# --------------------------------------------------------------------------
with tab_home:
    st.caption("Watch the ⚡ Agent Orchestration Trace in each response to see exactly which concept fired.")
    st.markdown("**Perils & Coverage**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🌊 Waterlogging / flood damage?", key="ho_flood", use_container_width=True):
            _send("Does home insurance cover damage from waterlogging or flooding?")
    with c2:
        if st.button("🌍 Earthquake damage — covered?", key="ho_eq", use_container_width=True):
            _send("Are earthquake damages covered under standard home insurance?")
    with c3:
        if st.button("🔥 Standard fire policy coverage", key="ho_fire", use_container_width=True):
            _send("What perils are covered under the standard fire and special perils policy in India?")
    st.markdown("**Claims & Valuation**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏠 Structure vs contents insurance", key="ho_str", use_container_width=True):
            _send("What is the difference between structure and contents coverage in home insurance?")
    with c2:
        if st.button("🔓 Burglary claim process", key="ho_burg", use_container_width=True):
            _send("What is the claim process for burglary under home insurance?")
    with c3:
        if st.button("💰 Sum insured — how calculated?", key="ho_si", use_container_width=True):
            _send("How is the sum insured calculated for home insurance under IRDAI guidelines?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏘️ Landlord / tenant policy differences", key="ho_land", use_container_width=True):
            _send("What is the difference between a landlord policy and a tenant content insurance policy?")
    with c2:
        if st.button("🔧 Reinstatement vs market value", key="ho_val", use_container_width=True):
            _send("What is the difference between reinstatement value and market value in property insurance?")


# --------------------------------------------------------------------------
# TAB: TRAVEL INSURANCE
# --------------------------------------------------------------------------
with tab_travel:
    st.caption("Watch the ⚡ Agent Orchestration Trace in each response to see exactly which concept fired.")
    st.markdown("**Coverage & Medical**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("✈️ Is travel insurance Schengen mandatory?", key="tr_sch", use_container_width=True):
            _send("Is travel insurance mandatory for Schengen visa applications?")
    with c2:
        if st.button("🏥 Medical emergency abroad — coverage", key="tr_med", use_container_width=True):
            _send("What medical coverage is included in international travel insurance under IRDAI?")
    with c3:
        if st.button("🧗 Adventure sports exclusions", key="tr_adv", use_container_width=True):
            _send("What are the exclusions in travel insurance for adventure sports activities?")
    st.markdown("**Claims & Cancellation**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🧳 Lost baggage claim process", key="tr_bag", use_container_width=True):
            _send("What is the claim process for lost baggage on an international flight?")
    with c2:
        if st.button("❌ Trip cancellation due to illness", key="tr_cancel", use_container_width=True):
            _send("Does travel insurance cover trip cancellation due to illness?")
    with c3:
        if st.button("⏱️ Travel delay compensation", key="tr_delay", use_container_width=True):
            _send("What compensation does travel insurance provide for flight delays?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🌐 Domestic vs international — difference", key="tr_dom", use_container_width=True):
            _send("What is the difference between domestic and international travel insurance coverage?")
    with c2:
        if st.button("🔒 Pre-existing conditions in travel", key="tr_ped", use_container_width=True):
            _send("Are pre-existing medical conditions covered under travel insurance policies?")


# --------------------------------------------------------------------------
# TAB: BUSINESS INSURANCE
# --------------------------------------------------------------------------
with tab_business:
    st.caption("Watch the ⚡ Agent Orchestration Trace in each response to see exactly which concept fired.")
    st.markdown("**Group Policies**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("👥 Group health — eligibility criteria", key="bi_gh", use_container_width=True):
            _send("What are the eligibility criteria for group health insurance under IRDAI?")
    with c2:
        if st.button("🔢 Minimum group size for life cover", key="bi_gl", use_container_width=True):
            _send("What is the minimum group size required for group life insurance?")
    with c3:
        if st.button("🔑 Keyman insurance — who qualifies?", key="bi_key", use_container_width=True):
            _send("How does keyman insurance work and who can be covered under it?")
    st.markdown("**Commercial & Liability**")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⚖️ Professional liability coverage", key="bi_pl", use_container_width=True):
            _send("What does professional liability insurance cover for businesses?")
    with c2:
        if st.button("🚢 Marine cargo — claim procedure", key="bi_marine", use_container_width=True):
            _send("What are the claim procedures for marine cargo insurance?")
    with c3:
        if st.button("👷 Workers' compensation cover", key="bi_wc", use_container_width=True):
            _send("What does workers' compensation insurance cover under IRDAI regulations?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🏗️ Commercial property — fire & perils", key="bi_prop", use_container_width=True):
            _send("What does commercial property insurance cover for fire and allied perils?")
    with c2:
        if st.button("💻 Cyber liability insurance basics", key="bi_cyber", use_container_width=True):
            _send("What does cyber liability insurance cover for businesses under IRDAI guidelines?")


st.divider()


# ==========================================================================
# ORCHESTRATION TRACE + RUN HELPERS
# ==========================================================================
def render_static_trace(trace: dict):
    """Compact static orchestration summary shown in chat history."""
    dept_id        = trace.get("department", "")
    group_id       = trace.get("group", "")
    reasoning      = trace.get("reasoning", "")
    routing_conf   = trace.get("routing_confidence", trace.get("confidence", 0))
    retrieval_conf = trace.get("retrieval_confidence", routing_conf)
    composite_conf = trace.get("composite_confidence", routing_conf)
    sources_n      = trace.get("sources_count", 0)
    dept_meta      = DEPARTMENT_METADATA.get(dept_id, {"icon": "📄", "name": dept_id})
    group_name     = group_id.replace("_", " ").title()
    dept_icon      = dept_meta.get("icon", "📄")
    dept_name_str  = dept_meta.get("name", dept_id)

    with st.expander("⚡ Agent Orchestration Trace", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📂 Group",      group_name)
        c2.metric("🏢 Department", dept_name_str)
        c3.metric("🎯 Routing",    f"{routing_conf:.0%}")
        c4.metric("📊 Overall",    f"{composite_conf:.0%}",
                  delta=f"retrieval: {retrieval_conf:.0%}", delta_color="off")
        st.divider()

        rows = [
            ("🎯 Orchestrator",     "Query analyzed & routed"),
            ("📂 Group Supervisor", f"Dispatched to {group_name}"),
            (f"{dept_icon} Dept Agent",     f"{dept_name_str} agent invoked"),
            ("🔍 RAG Pipeline",
             f"{sources_n} chunk(s) retrieved from ChromaDB (avg relevance: {retrieval_conf:.0%})"),
            ("✍️ GPT-4o-mini",    "Response generated"),
        ]
        tcols = st.columns([1, 3])
        for icon_label, value in rows:
            tcols[0].markdown(f"✅ **{icon_label}**")
            tcols[1].markdown(value)

        # Motor agent concept signals
        tool_calls      = trace.get("tool_calls", [])
        rewritten_q     = trace.get("rewritten_query", "")
        qi              = trace.get("query_intent", "")
        qic             = trace.get("intent_confidence", 0.0)
        multi_queries   = trace.get("multi_queries", [])
        unique_chunks   = trace.get("unique_chunks", 0)
        self_eval_score = trace.get("self_eval_score", 0)
        self_eval_gnd   = trace.get("self_eval_grounded", "")
        memory_turns    = trace.get("memory_turns", 0)

        if qi or multi_queries or self_eval_score or memory_turns or tool_calls:
            st.divider()
            st.markdown("**🤖 Motor Agent Agentic Concepts Fired**")
            ccols = st.columns([1, 3])
            if qi:
                ccols[0].markdown(
                    "<span class='concept-badge badge-intent'>🧠 Intent</span>",
                    unsafe_allow_html=True)
                ccols[1].markdown(f"`{qi}` — {qic:.0%} confidence")
            if multi_queries:
                ccols[0].markdown(
                    "<span class='concept-badge badge-multirag'>🔍 Multi-Query RAG</span>",
                    unsafe_allow_html=True)
                ccols[1].markdown(
                    f"{len(multi_queries)} paraphrases → {unique_chunks} unique chunks after dedup")
            if self_eval_score:
                gnd_icon = "✅" if self_eval_gnd == "yes" else "⚠️"
                ccols[0].markdown(
                    "<span class='concept-badge badge-selfeval'>🔎 Self-Eval</span>",
                    unsafe_allow_html=True)
                ccols[1].markdown(f"Score **{self_eval_score}/5**  {gnd_icon} grounded={self_eval_gnd}")
            if memory_turns is not None:
                ccols[0].markdown(
                    "<span class='concept-badge badge-memory'>💬 Memory</span>",
                    unsafe_allow_html=True)
                ccols[1].markdown(
                    f"{memory_turns} prior turn(s) loaded" if memory_turns > 0
                    else "First query — no prior turns")
            if tool_calls:
                ccols[0].markdown(
                    "<span class='concept-badge badge-tools'>🔧 Tools</span>",
                    unsafe_allow_html=True)
                ccols[1].markdown(", ".join(f"`{t}`" for t in tool_calls))

        if reasoning:
            st.caption(f"💭 *Routing reasoning: {reasoning}*")
        if rewritten_q:
            st.caption(f"🔄 *Query rewritten for retrieval: \"{rewritten_q}\"*")


def run_with_live_trace(query: str) -> dict:
    """Execute multi-agent pipeline with live st.status() trace."""
    from agents.orchestrator import orchestrator
    from utils.audit import audit_trail

    routing      = None
    agent_result = {}

    with st.status("🔄 Routing your query through the agent pipeline...", expanded=True) as status:
        st.write("🎯 **Orchestrator** — Analyzing your query...")
        routing    = orchestrator.route(query)
        dept_meta  = DEPARTMENT_METADATA.get(routing.department, {"icon": "📄", "name": routing.department})
        group_name = routing.group.replace("_", " ").title()
        dept_name  = f"{dept_meta.get('icon', '')} {dept_meta.get('name', routing.department)}"
        st.write(
            f"🎯 **Orchestrator** — Routed to **{group_name}** → **{dept_name}** "
            f"*(confidence: {routing.confidence:.0%})*"
        )
        st.write(f"📂 **{group_name} Supervisor** — Dispatching to **{dept_name}**...")
        supervisor = orchestrator.supervisors[routing.group]
        agent      = supervisor.agents[routing.department]
        st.write(f"{dept_meta.get('icon','📄')} **{dept_meta.get('name')} Agent** — Searching ChromaDB...")
        st.write("✍️ **GPT-4o-mini** — Generating response from retrieved context...")
        agent_result    = agent.process_query(query)

        sources         = agent_result.get("sources", [])
        response        = agent_result.get("response", "")
        tool_calls      = agent_result.get("tool_calls", [])
        rewritten_query = agent_result.get("rewritten_query", "")
        query_intent    = agent_result.get("query_intent", "")
        intent_conf     = agent_result.get("intent_confidence", 0.0)
        multi_queries   = agent_result.get("multi_queries", [])
        unique_chunks   = len(sources)
        self_eval_score = agent_result.get("self_eval_score", 0)
        self_eval_gnd   = agent_result.get("self_eval_grounded", "")
        memory_turns    = agent_result.get("memory_turns", 0)

        st.write(
            f"{dept_meta.get('icon','📄')} **{dept_meta.get('name')} Agent** — "
            f"Retrieved **{len(sources)} document chunk(s)**"
        )
        if query_intent:
            st.write(f"🧠 **[Concept 1 — Intent Classification]**: `{query_intent}` *(confidence: {intent_conf:.0%})*")
        if multi_queries:
            st.write(
                f"🔍 **[Concept 2 — Multi-Query RAG]**: {len(multi_queries)} paraphrases → "
                f"{unique_chunks} unique chunks after dedup & grading"
            )
        if rewritten_query:
            st.write(f"🔄 **Query rewritten** for retrieval: *\"{rewritten_query[:80]}\"*")
        if memory_turns is not None:
            st.write(
                f"💬 **[Concept 4 — Conversational Memory]**: {memory_turns} prior turn(s) loaded"
                if memory_turns > 0
                else "💬 **[Concept 4 — Conversational Memory]**: first query — no prior context"
            )
        if tool_calls:
            st.write(f"🔧 **[Concept 5 — IRDAI Tools]**: {', '.join(f'`{t}`' for t in tool_calls)}")
        if self_eval_score:
            gnd_icon = "✅" if self_eval_gnd == "yes" else "⚠️"
            st.write(
                f"🔎 **[Concept 3 — Self-Evaluation]**: score **{self_eval_score}/5**  "
                f"{gnd_icon} grounded={self_eval_gnd}"
            )

        avg_score      = (
            sum(s.get("score", 0) for s in sources) / len(sources)
            if sources else 0.0
        )
        composite_conf = round(0.6 * routing.confidence + 0.4 * avg_score, 2)
        status.update(
            label=(
                f"✅ {dept_name} Agent  |  {len(sources)} sources  |  "
                f"Routing: {routing.confidence:.0%}  |  Overall: {composite_conf:.0%}"
            ),
            state="complete",
            expanded=False,
        )

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
        "routing": {
            "group":      routing.group,
            "department": routing.department,
            "reasoning":  routing.reasoning,
            "confidence": composite_conf,
        },
        "trace": {
            "department":           routing.department,
            "group":                routing.group,
            "reasoning":            routing.reasoning,
            "routing_confidence":   routing.confidence,
            "retrieval_confidence": round(avg_score, 2),
            "composite_confidence": composite_conf,
            "sources_count":        len(sources),
            "tool_calls":           tool_calls,
            "rewritten_query":      rewritten_query,
            "query_intent":         query_intent,
            "intent_confidence":    intent_conf,
            "multi_queries":        multi_queries,
            "unique_chunks":        unique_chunks,
            "self_eval_score":      self_eval_score,
            "self_eval_grounded":   self_eval_gnd,
            "memory_turns":         memory_turns,
        },
    }


# ==========================================================================
# SOURCES RENDERER
# ==========================================================================
def render_sources(sources: list):
    """Grouped source display — one header per unique document, passages beneath."""
    if not sources:
        return
    from collections import OrderedDict
    groups: OrderedDict = OrderedDict()
    for src in sources:
        key = src.get("doc_title") or src.get("source", "Unknown Source")
        if key not in groups:
            groups[key] = {"meta": src, "chunks": []}
        groups[key]["chunks"].append(src)

    total_chunks = len(sources)
    unique_docs  = len(groups)
    label = (
        f"📚 Retrieved Sources — {unique_docs} document{'s' if unique_docs > 1 else ''}"
        f", {total_chunks} passage{'s' if total_chunks > 1 else ''}"
    )
    with st.expander(label, expanded=False):
        for doc_idx, (doc_key, group) in enumerate(groups.items(), 1):
            meta      = group["meta"]
            chunks    = group["chunks"]
            doc_title = meta.get("doc_title", "") or doc_key
            authority = meta.get("authority", "")
            company   = meta.get("company", "")
            version   = meta.get("version", "")
            avg_score = sum(c.get("score", 0) for c in chunks) / len(chunks)
            source_file = meta.get("source", "")
            file_path   = meta.get("file_path", "")
            if file_path:
                import pathlib
                try:
                    rel = pathlib.Path(file_path).parts
                    rel_display = "/".join(rel[-3:]) if len(rel) >= 3 else source_file
                except Exception:
                    rel_display = source_file
            else:
                rel_display = source_file

            st.markdown(f"### 📄 {doc_title}")
            if rel_display:
                st.markdown(
                    f"<div style='font-size:0.75rem;color:#6e7681;margin:-6px 0 6px 0;'>"
                    f"📁 <code>data/sample_docs/{source_file}</code></div>",
                    unsafe_allow_html=True,
                )
            meta_parts = []
            if authority: meta_parts.append(f"🏛️ **{authority}**")
            if company:   meta_parts.append(f"🏢 {company}")
            if version:   meta_parts.append(f"📅 {version}")
            meta_parts.append(f"📊 Avg relevance: **{avg_score:.0%}** across {len(chunks)} passage(s)")
            st.caption("   ·   ".join(meta_parts))

            for c_idx, chunk in enumerate(chunks, 1):
                score    = chunk.get("score", 0)
                content  = chunk.get("content", "")
                page     = chunk.get("page_number", "")
                page_lbl = f" · 📃 Page {page}" if page else ""
                first_line = next((ln.strip() for ln in content.splitlines() if ln.strip()), "")
                section_hint = f"*{first_line[:80]}*" if first_line else ""

                st.markdown(
                    f"<div style='margin:6px 0 2px 0;font-size:0.78rem;color:#aaa;'>"
                    f"Passage {c_idx}{page_lbl} &nbsp;·&nbsp; "
                    f"<span style='color:#C9A227;font-weight:600;'>✅ {score:.0%} relevance</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if section_hint:
                    st.markdown(
                        f"<div style='font-size:0.78rem;color:#888;margin-bottom:4px;'>"
                        f"📌 {section_hint}</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    f"<div style='background:#1e1e2e;padding:0.6rem 0.8rem;border-radius:6px;"
                    f"border-left:3px solid #C9A227;font-size:0.8rem;color:#ccc;'>"
                    f"{content[:350].replace(chr(10), '<br>')}{'…' if len(content) > 350 else ''}"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            if doc_idx < unique_docs:
                st.divider()


# ==========================================================================
# SIDEBAR — clear chat
# ==========================================================================
with st.sidebar:
    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.processing = False
        st.rerun()


# ==========================================================================
# CHAT HISTORY
# ==========================================================================
if not st.session_state.messages:
    st.markdown(
        "💡 **Tip:** Select a department tab above and click a Quick Action button to begin, "
        "or type your question in the chat bar below."
    )
    st.markdown("")

for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🛡️"):
            if "trace" in msg:
                render_static_trace(msg["trace"])
            st.markdown(msg["content"])
            render_sources(msg.get("sources", []))


# ==========================================================================
# PROCESS PENDING QUERY
# ==========================================================================
if st.session_state.processing:
    last_user_msg = next(
        (m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"),
        None,
    )
    if last_user_msg:
        with st.chat_message("assistant", avatar="🛡️"):
            try:
                result = run_with_live_trace(last_user_msg)
                render_static_trace(result["trace"])
                st.markdown(result["response"])
                render_sources(result.get("sources", []))
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
    st.rerun()


# ==========================================================================
# CHAT INPUT
# ==========================================================================
user_input = st.chat_input(
    "Ask an insurance regulatory question, or use the department tabs above for quick actions…"
)
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.processing = True
    st.rerun()
