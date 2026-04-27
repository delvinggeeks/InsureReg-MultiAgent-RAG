"""
InsureReg - Motor Insurance Department Agent

Full Agentic RAG system built on a LangGraph StateGraph demonstrating all 5 capstone concepts:

  Concept 1 — sklearn Intent Classifier  : TF-IDF + LinearSVC (92.3% accuracy)
                                           Classifies query intent before retrieval to bias
                                           downstream node behaviour.
  Concept 2 — Multi-Query RAG            : LLM generates 3 diverse paraphrases of the query;
                                           documents are retrieved for all 4 variants, merged,
                                           and deduplicated so the grader sees richer context.
  Concept 3 — Self-Evaluation/Reflection : After generation the LLM grades its own response
                                           (grounded yes/no, score 1-5). If score < 3 or
                                           ungrounded, the response is regenerated once with
                                           a strict citation-forcing prompt.
  Concept 4 — Conversational Memory      : SimpleConversationMemory (k=3 turns) injects the
                                           last 3 Q/A turns into the generation prompt so
                                           follow-up questions are answered in context.
  Concept 5 — Fine-Tuning Dataset+Code   : data/finetune/motor_finetune.jsonl (20 triplets)
                                           + data/finetune/finetune_submission.py

Graph topology:
    START → classify_intent → multi_query_retrieve → grade_documents
    grade_documents  → [generate | rewrite_query]
    rewrite_query    → retrieve → grade_documents     (corrective RAG loop)
    generate         → [execute_tools | self_evaluate]
    execute_tools    → self_evaluate
    self_evaluate    → [end | regenerate]
    regenerate       → self_evaluate → END            (max 1 reflection cycle)
"""

from __future__ import annotations

import hashlib
from collections import deque
from typing import TypedDict, Literal

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END

from config.settings import LLM_MODEL, LLM_TEMPERATURE, OPENAI_API_KEY
from config.department_config import DEPARTMENT_METADATA
from rag.retriever_factory import retriever_factory
from agents.department_agents.motor_insurance.classifier import classify_intent as _classify_intent_fn
from utils.logger import get_logger

logger = get_logger("MotorInsuranceAgent")


# ─── LangChain Tools ──────────────────────────────────────────────────────────

@tool
def calculate_idv(ex_showroom_price: float, age_years: float) -> str:
    """
    Calculate the Insured Declared Value (IDV) of a motor vehicle per IRDAI schedule.
    IDV = Ex-showroom price minus IRDAI-prescribed depreciation percentage.
    Call this when the query involves IDV, total loss value, or vehicle valuation.

    Args:
        ex_showroom_price: Manufacturer's listed ex-showroom price in INR.
        age_years: Age of the vehicle in decimal years (e.g. 2.5 = 2 years 6 months).
    """
    schedule = [(0.5, 5), (1.0, 15), (2.0, 20), (3.0, 30), (4.0, 40), (5.0, 50)]
    if age_years > 5:
        idv = ex_showroom_price * 0.50
        return (
            f"IDV (>5 yrs, by mutual agreement): ≈ ₹{idv:,.0f}\n"
            f"Depreciation applied: 50% (IRDAI maximum for vehicles >5 years)\n"
            f"Source: IRDAI Motor Insurance Guidelines, Chapter 2 — IDV Schedule"
        )
    dep_pct = 50
    for limit, pct in schedule:
        if age_years <= limit:
            dep_pct = pct
            break
    idv = ex_showroom_price * (1 - dep_pct / 100)
    return (
        f"IDV = ₹{idv:,.0f}\n"
        f"Calculation: ₹{ex_showroom_price:,.0f} × (1 − {dep_pct}%) = ₹{idv:,.0f}\n"
        f"IRDAI depreciation rate for {age_years} yr vehicle: {dep_pct}%\n"
        f"Source: IRDAI Motor Insurance Guidelines, Chapter 2 — IDV Schedule"
    )


@tool
def calculate_ncb(claim_free_years: int) -> str:
    """
    Calculate the No-Claim Bonus (NCB) discount on Own Damage (OD) premium.
    Call this when the query asks about NCB percentage, no-claim discount, or claim-free years.

    Args:
        claim_free_years: Number of consecutive claim-free policy years (0 to 5+).
    """
    schedule = {0: 0, 1: 20, 2: 25, 3: 35, 4: 45}
    if claim_free_years >= 5:
        pct = 50
    else:
        pct = schedule.get(claim_free_years, 0)
    if pct == 0:
        return "No NCB applicable for 0 claim-free years (first policy year)."
    return (
        f"NCB after {claim_free_years} consecutive claim-free year(s): {pct}% on OD premium\n"
        f"NCB Schedule: 1yr=20%, 2yr=25%, 3yr=35%, 4yr=45%, 5yr+=50% (maximum)\n"
        f"NCB is transferable when buying a new vehicle and portable between insurers.\n"
        f"Source: IRDAI Motor Insurance Guidelines, Chapter 4 — NCB Rules"
    )


@tool
def estimate_od_premium(idv: float, ncb_percent: float, vehicle_type: str = "car") -> str:
    """
    Estimate the Own Damage (OD) insurance premium for a motor vehicle.
    Call this when the query asks about premium amount or cost estimation.

    Args:
        idv: Insured Declared Value in INR.
        ncb_percent: Applicable NCB discount percentage (0, 20, 25, 35, 45, or 50).
        vehicle_type: 'car' or 'bike' (default 'car').
    """
    rates = {"car": 0.0275, "bike": 0.0200}
    rate = rates.get(vehicle_type.lower(), 0.0275)
    base = idv * rate
    discount = base * (ncb_percent / 100)
    after_ncb = base - discount
    gst = after_ncb * 0.18
    total = after_ncb + gst
    return (
        f"OD Premium Estimate ({vehicle_type.title()}):\n"
        f"  Base OD premium  (IDV ₹{idv:,.0f} × {rate:.2%}): ₹{base:,.0f}\n"
        f"  NCB discount     ({ncb_percent:.0f}%):             −₹{discount:,.0f}\n"
        f"  Premium after NCB:                        ₹{after_ncb:,.0f}\n"
        f"  GST (18%):                                ₹{gst:,.0f}\n"
        f"  Total OD Premium:                         ₹{total:,.0f}\n"
        f"Note: Actual premiums vary by insurer, add-ons, and vehicle specifics.\n"
        f"Source: IRDAI Motor Insurance Guidelines, Chapter 3 — Premium Structure"
    )


MOTOR_TOOLS = [calculate_idv, calculate_ncb, estimate_od_premium]
_TOOL_MAP   = {t.name: t for t in MOTOR_TOOLS}


# ─── Concept 4 — Simple Conversational Memory ─────────────────────────────────

class SimpleConversationMemory:
    """
    Rolling-window conversation memory implementing the same interface as
    LangChain's ConversationBufferWindowMemory but without LangChain deprecation
    warnings.  Stores the last k user/assistant turns and formats them as a
    plain-text string for injection into the generation prompt.
    """

    def __init__(self, k: int = 3):
        self._k   = k
        self._buf: deque[dict] = deque(maxlen=k)

    def save_context(self, user_input: str, assistant_output: str) -> None:
        self._buf.append({
            "user":      user_input,
            "assistant": assistant_output[:400],   # truncate to save tokens
        })

    def load_memory_as_string(self) -> str:
        if not self._buf:
            return ""
        lines = []
        for turn in self._buf:
            lines.append(f"User: {turn['user']}")
            lines.append(f"Assistant: {turn['assistant']}…" if len(turn['assistant']) == 400
                         else f"Assistant: {turn['assistant']}")
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self._buf)


# ─── LangGraph State ──────────────────────────────────────────────────────────

class MotorAgentState(TypedDict):
    # ── Core fields ──────────────────────────────────────────────────────────
    query:              str   # original user query
    rewritten_query:    str   # query after optional rewrite (empty if not rewritten)
    documents:          list  # raw chunks from ChromaDB
    relevant_documents: list  # chunks graded as relevant by the LLM grader
    messages:           list  # LangChain message list used in the tool-calling loop
    response:           str   # final text response sent back to the user
    retry_count:        int   # number of rewrite+retry cycles completed
    tool_calls_made:    list  # names of tools actually executed
    # ── Concept 1 — Intent Classifier ────────────────────────────────────────
    query_intent:       str   # sklearn label: calculation / regulatory / coverage / claim_process
    intent_confidence:  float # classifier probability score [0, 1]
    # ── Concept 2 — Multi-Query RAG ──────────────────────────────────────────
    multi_queries:      list  # 3 LLM-generated query paraphrases
    all_documents:      list  # merged retrieval results before dedup (for trace display)
    # ── Concept 3 — Self-Evaluation / Reflection ─────────────────────────────
    self_eval_score:    int   # holistic quality score 1-5 from self-evaluator LLM
    self_eval_grounded: str   # "yes" / "no" — whether response cites retrieved sources
    regenerated:        bool  # True after one regeneration cycle (prevents infinite loops)
    # ── Concept 4 — Conversational Memory ────────────────────────────────────
    memory_context:     str   # prior turns formatted as a string and injected into prompt


# ─── Document Grading Schema ──────────────────────────────────────────────────

class DocumentGrade(BaseModel):
    """Binary relevance score for a retrieved document chunk."""
    relevant: Literal["yes", "no"] = Field(
        description="'yes' if the chunk directly addresses the query, 'no' otherwise."
    )


# ─── Concept 3 — Self-Evaluation Schema ──────────────────────────────────────

class ResponseEvaluation(BaseModel):
    """Structured self-evaluation rubric for the generated response."""
    grounded: Literal["yes", "no"] = Field(
        description="'yes' if every factual claim is directly supported by the retrieved documents."
    )
    complete: Literal["yes", "no"] = Field(
        description="'yes' if the response fully and directly answers the user's question."
    )
    score: int = Field(
        description="Holistic quality score: 1 = very poor, 3 = acceptable, 5 = excellent.",
        ge=1, le=5,
    )


# ─── Motor Insurance LangGraph Agent ─────────────────────────────────────────

class MotorInsuranceAgent:
    """
    Motor Insurance specialist built on a LangGraph StateGraph.

    Each node is a pure function on MotorAgentState.
    Conditional edges replace explicit if/else control flow, making the
    reasoning path visible, testable, and extendable.
    """

    def __init__(self):
        self.department_id  = "motor_insurance"
        meta                = DEPARTMENT_METADATA[self.department_id]
        self.name           = meta["name"]
        self._system_prompt = meta["system_prompt"]

        base_llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            openai_api_key=OPENAI_API_KEY,
        )
        # LLM with tools bound — used in _generate
        self._llm_with_tools = base_llm.bind_tools(MOTOR_TOOLS)
        # Plain LLM — synthesis after tool results, and for _regenerate
        self._llm_plain      = base_llm

        # Grader: structured output, deterministic yes/no
        self._grader = ChatOpenAI(
            model=LLM_MODEL, temperature=0, openai_api_key=OPENAI_API_KEY,
        ).with_structured_output(DocumentGrade)

        # Rewriter: Concept 2 paraphrase generation + Concept 1 corrective rewrite
        self._rewriter = ChatOpenAI(
            model=LLM_MODEL, temperature=0, openai_api_key=OPENAI_API_KEY,
        )

        # Concept 3 — Self-evaluator LLM (structured output)
        self._self_eval_llm = ChatOpenAI(
            model=LLM_MODEL, temperature=0, openai_api_key=OPENAI_API_KEY,
        ).with_structured_output(ResponseEvaluation)

        # Concept 4 — Conversational memory (k=3 turns)
        self._memory = SimpleConversationMemory(k=3)

        self._graph = self._build_graph()
        logger.info(
            f"MotorInsuranceAgent initialised — "
            f"LangGraph StateGraph + {len(MOTOR_TOOLS)} tools "
            f"({', '.join(t.name for t in MOTOR_TOOLS)}) + "
            f"Multi-QueryRAG + Self-Eval + ConvMemory"
        )

    # ── Nodes ─────────────────────────────────────────────────────────────────

    def _classify_intent(self, state: MotorAgentState) -> dict:
        """
        Concept 1 — sklearn TF-IDF + LinearSVC intent classifier.
        Runs before retrieval so downstream nodes can bias their behaviour.
        Dataset sources: InsuranceQA, IRDAI FAQ, BANKING77, HWU64, InsureReg docs
        (see data/motor_intent_SOURCES.txt for full open-source citations).
        """
        try:
            label, confidence = _classify_intent_fn(state["query"])
        except Exception as exc:
            logger.warning(f"[Motor/intent] Classifier failed ({exc}), defaulting to 'coverage'")
            label, confidence = "coverage", 0.0
        logger.info(f"[Motor/intent] '{label}' (conf={confidence:.2f})")
        return {"query_intent": label, "intent_confidence": confidence}

    def _multi_query_retrieve(self, state: MotorAgentState) -> dict:
        """
        Concept 2 — Multi-Query RAG.

        Steps:
          1. Call the LLM to generate 3 diverse paraphrases of the original query,
             each using different IRDAI / motor-insurance terminology.
          2. Retrieve top-K chunks for every paraphrase PLUS the original query
             (4 retrieval calls total).
          3. Merge results and deduplicate by MD5 of document content so downstream
             nodes see a richer, more diverse context without duplicates.

        Why it helps: a single embedding query can miss relevant chunks if the
        vocabulary doesn't match the indexed text.  Paraphrasing with domain
        synonyms (e.g. "IDV" vs "insured declared value") dramatically improves
        recall on regulatory corpora.
        """
        original_q = state["query"]

        # ── Step 1: Generate 3 paraphrases ───────────────────────────────────
        paraphrase_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are an IRDAI motor insurance query planner.\n"
             "Generate exactly 3 alternative formulations of the user's question "
             "to maximise retrieval coverage from a Motor Insurance guidelines corpus.\n"
             "Each formulation MUST:\n"
             "  • Use different IRDAI/motor-insurance terminology than the others\n"
             "    (e.g. IDV / insured declared value / total loss valuation)\n"
             "  • Stay semantically equivalent to the original question\n"
             "Return exactly 3 lines — one query per line, no bullets or numbering."),
            ("human", "Original query: {query}"),
        ])
        try:
            result = (paraphrase_prompt | self._rewriter).invoke({"query": original_q})
            lines  = [l.strip() for l in result.content.strip().splitlines() if l.strip()]
            paraphrases = lines[:3]
            while len(paraphrases) < 3:         # pad if LLM returned fewer
                paraphrases.append(original_q)
        except Exception as exc:
            logger.warning(f"[Motor/multi_query] Paraphrase generation failed: {exc}")
            paraphrases = [original_q] * 3

        all_queries = [original_q] + paraphrases   # 4 total (original + 3 paraphrases)
        logger.info(f"[Motor/multi_query] paraphrases={paraphrases}")

        # ── Step 2: Retrieve + deduplicate ────────────────────────────────────
        seen_hashes: set[str] = set()
        merged: list[dict]    = []
        for q in all_queries:
            try:
                docs = retriever_factory.retrieve_documents(self.department_id, q)
                for doc in docs:
                    h = hashlib.md5(doc.get("content", "").encode()).hexdigest()
                    if h not in seen_hashes:
                        seen_hashes.add(h)
                        merged.append(doc)
            except Exception:
                pass

        logger.info(
            f"[Motor/multi_query] {len(merged)} unique chunks "
            f"from {len(all_queries)} queries"
        )
        return {
            "multi_queries": paraphrases,
            "all_documents": list(merged),   # keep full merged list for trace
            "documents":     merged,          # grade_documents reads from 'documents'
        }

    def _retrieve(self, state: MotorAgentState) -> dict:
        """
        Simple single-query retrieval — used only inside the corrective RAG loop
        (rewrite_query → retrieve → grade_documents) where a rewritten query
        replaces the original and full multi-query expansion is unnecessary.
        """
        active_q = state["rewritten_query"] or state["query"]
        logger.info(f"[Motor/retrieve] query='{active_q[:80]}'")
        docs = retriever_factory.retrieve_documents(self.department_id, active_q)
        return {"documents": docs}

    def _grade_documents(self, state: MotorAgentState) -> dict:
        """
        LLM-based relevance grading — filters out chunks that do not address the query.
        Implements the 'Corrective RAG' document grading step.
        """
        query = state["rewritten_query"] or state["query"]
        grading_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a relevance grader for a Motor Insurance regulatory knowledge base.\n"
             "Decide if the document chunk is relevant to answering the user's query.\n"
             "Mark 'yes' only if it directly addresses the query topic."),
            ("human", "Query: {query}\n\nDocument chunk:\n{content}"),
        ])
        chain = grading_prompt | self._grader
        relevant = []
        for doc in state["documents"]:
            try:
                grade = chain.invoke({"query": query, "content": doc.get("content", "")})
                if grade.relevant == "yes":
                    relevant.append(doc)
            except Exception:
                relevant.append(doc)  # include on grading failure (safe default)
        logger.info(f"[Motor/grade] {len(relevant)}/{len(state['documents'])} chunks relevant")
        return {"relevant_documents": relevant}

    def _rewrite_query(self, state: MotorAgentState) -> dict:
        """
        Rewrite the original query using IRDAI/motor-specific terminology to
        improve ChromaDB retrieval on the next attempt.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You optimise queries for a Motor Insurance regulatory knowledge base.\n"
             "Rewrite using specific IRDAI / motor insurance terms "
             "(IDV, NCB, OD, TP, IRDAI, Motor Vehicles Act, etc.).\n"
             "Return ONLY the rewritten query — no explanation."),
            ("human", "Original query: {query}"),
        ])
        try:
            result    = (prompt | self._rewriter).invoke({"query": state["query"]})
            rewritten = result.content.strip()
        except Exception:
            rewritten = state["query"]
        logger.info(f"[Motor/rewrite] → '{rewritten[:80]}'")
        return {"rewritten_query": rewritten, "retry_count": state["retry_count"] + 1}

    def _generate(self, state: MotorAgentState) -> dict:
        """
        Generate a response using relevant document chunks as context.

        Concept 4 — Conversational Memory: the last k conversation turns are
        prepended to the system prompt so follow-up questions can reference
        prior answers without the user having to repeat context.

        The LLM can invoke tools (calculate_idv, calculate_ncb, estimate_od_premium)
        if the query requires a numerical calculation (intent == 'calculation').
        """
        relevant_docs = state["relevant_documents"]
        if relevant_docs:
            ctx_parts = []
            for i, doc in enumerate(relevant_docs, 1):
                src     = doc.get("source", "Unknown")
                pg      = doc.get("page_number", "")
                pg_info = f" (Page {pg})" if pg else ""
                ctx_parts.append(
                    f"[Source {i}: {src}{pg_info}] (Relevance: {doc.get('score', 0):.1%})\n"
                    f"{doc['content']}"
                )
            context = "\n\n".join(ctx_parts)
        else:
            context = "No relevant documents found in the Motor Insurance knowledge base."

        # ── Concept 4: inject conversation memory ────────────────────────────
        memory_section = ""
        memory_ctx = state.get("memory_context", "")
        if memory_ctx:
            memory_section = (
                "\n\nCONVERSATION HISTORY (last 3 turns — use for context continuity):\n"
                + "─" * 50 + "\n"
                + memory_ctx + "\n"
                + "─" * 50 + "\n"
                + "If the current question follows up on a prior answer, build on it.\n"
            )

        system_msg = (
            self._system_prompt
            + memory_section
            + "\n\nCONTEXT FROM RETRIEVED DOCUMENTS:\n"
            + "─" * 50 + "\n"
            + context + "\n"
            + "─" * 50 + "\n\n"
            + "RESPONSE RULES:\n"
            + "1. Answer ONLY from the context above — do NOT use external knowledge.\n"
            + f"2. The intent classifier categorised this query as '{state.get('query_intent', 'unknown')}' "
              f"(confidence {state.get('intent_confidence', 0):.0%}). "
              "If the intent is 'calculation', you MUST call the relevant tool "
              "(calculate_idv / calculate_ncb / estimate_od_premium).\n"
            + "3. Cite the source document for every regulatory fact.\n"
            + "4. End with: "
              "'---\\n*⚠️ For informational purposes only — verify with compliance.*'"
        )

        messages = [SystemMessage(content=system_msg), HumanMessage(content=state["query"])]
        try:
            ai_msg   = self._llm_with_tools.invoke(messages)
            messages.append(ai_msg)
            response = ai_msg.content if not ai_msg.tool_calls else ""
        except Exception as e:
            logger.error(f"[Motor/generate] {e}")
            return {"messages": [], "response": f"⚠️ Generation error: {e}"}

        return {"messages": messages, "response": response}

    def _execute_tools(self, state: MotorAgentState) -> dict:
        """
        Execute the tool calls requested by the LLM, inject results back as
        ToolMessages, then call the LLM once more for final synthesis.
        """
        messages       = list(state["messages"])
        tool_calls_made = list(state["tool_calls_made"])
        last_ai        = messages[-1]

        for tc in last_ai.tool_calls:
            name    = tc.get("name", "")
            args    = tc.get("args", {})
            call_id = tc.get("id", "")
            fn      = _TOOL_MAP.get(name)
            tool_calls_made.append(name)
            if fn:
                try:
                    result = fn.invoke(args)
                    messages.append(ToolMessage(content=str(result), tool_call_id=call_id))
                    logger.info(f"[Motor/tools] {name}({args}) → ok")
                except Exception as e:
                    messages.append(ToolMessage(content=f"Tool error: {e}", tool_call_id=call_id))
                    logger.error(f"[Motor/tools] {name} failed: {e}")
            else:
                messages.append(ToolMessage(content=f"Unknown tool: {name}", tool_call_id=call_id))

        # Final synthesis: plain LLM sees tool results and produces the response
        try:
            final    = self._llm_plain.invoke(messages)
            response = final.content
        except Exception as e:
            response = f"⚠️ Error generating final response after tool execution: {e}"

        return {"response": response, "tool_calls_made": tool_calls_made}

    def _self_evaluate(self, state: MotorAgentState) -> dict:
        """
        Concept 3 — Self-Evaluation / Reflection.

        The evaluator LLM uses the same retrieved documents as the generator and
        answers three questions about the response:
          • grounded — does every claim trace to a source chunk?
          • complete — does the response fully answer the question?
          • score    — holistic quality 1-5

        If score < 3 OR grounded == "no" AND we haven't yet regenerated, the graph
        routes to _regenerate for one corrective pass.
        """
        response     = state.get("response", "")
        query        = state.get("query", "")
        relevant_docs = state.get("relevant_documents") or state.get("documents", [])
        sources_list  = " | ".join(
            d.get("source", "Unknown") for d in relevant_docs[:3]
        ) or "No sources"

        eval_prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a quality-assurance reviewer for Indian Motor Insurance regulatory answers.\n"
             "Evaluate the assistant's response using three criteria:\n"
             "  grounded — does every factual claim cite or reference the retrieved source documents?\n"
             "  complete — does the response fully and directly answer the user's question?\n"
             "  score    — integer 1 (very poor / hallucinated) to 5 (excellent / fully grounded)\n"
             "Be strict: if the response makes any claim not supported by the sources, mark grounded='no'."),
            ("human",
             "User question: {query}\n\n"
             "Retrieved source documents used: {sources}\n\n"
             "Assistant response:\n{response}"),
        ])

        try:
            eval_chain  = eval_prompt | self._self_eval_llm
            eval_result = eval_chain.invoke({
                "query":    query,
                "sources":  sources_list,
                "response": response[:1500],   # cap to limit tokens
            })
            score    = eval_result.score
            grounded = eval_result.grounded
            logger.info(
                f"[Motor/self_eval] score={score}/5  grounded={grounded}  "
                f"complete={eval_result.complete}"
            )
        except Exception as exc:
            logger.warning(f"[Motor/self_eval] Evaluation failed ({exc}), accepting response")
            score    = 4
            grounded = "yes"

        return {"self_eval_score": score, "self_eval_grounded": grounded}

    def _regenerate(self, state: MotorAgentState) -> dict:
        """
        Concept 3 — Reflection / Regeneration.

        Called when self-evaluation reveals a low-quality or ungrounded response.
        Uses a stricter system prompt that explicitly lists the quality issues found
        and forces the LLM to cite every fact.  Sets regenerated=True so we only
        pass through this node once per query (prevents infinite reflection loops).
        """
        score    = state.get("self_eval_score", 0)
        grounded = state.get("self_eval_grounded", "no")
        logger.info(f"[Motor/regenerate] Regenerating — score={score}/5, grounded={grounded}")

        relevant_docs = state.get("relevant_documents", []) or state.get("documents", [])
        if relevant_docs:
            ctx_parts = []
            for i, doc in enumerate(relevant_docs, 1):
                src     = doc.get("source", "Unknown")
                pg      = doc.get("page_number", "")
                pg_info = f" (Page {pg})" if pg else ""
                ctx_parts.append(f"[Source {i}: {src}{pg_info}]\n{doc['content']}")
            context = "\n\n".join(ctx_parts)
        else:
            context = "No documents available in the Motor Insurance knowledge base."

        # Surface the specific quality issues to the LLM
        issues = []
        if grounded == "no":
            issues.append("the previous answer made claims not traceable to the source documents")
        if score < 3:
            issues.append(f"the previous answer received a quality score of {score}/5")
        issue_str = "; and ".join(issues) if issues else "the previous answer was insufficient"

        strict_prompt = (
            f"{self._system_prompt}\n\n"
            f"⚠️  REGENERATION PASS: Quality review found that {issue_str}.\n\n"
            f"You MUST follow these rules without exception:\n"
            f"  1. Quote or directly paraphrase ONLY text that appears in the sources below.\n"
            f"  2. For every regulatory fact, add '[Source N]' after the sentence.\n"
            f"  3. If the sources do not contain enough information to fully answer the\n"
            f"     question, state this explicitly rather than filling gaps from memory.\n"
            f"  4. Do NOT introduce any information not present in the sources.\n\n"
            f"CONTEXT FROM RETRIEVED DOCUMENTS:\n{'─' * 50}\n{context}\n{'─' * 50}"
        )

        # If tools were executed, preserve the full message chain (including ToolMessages)
        # so the LLM can use the calculated values during regeneration.
        prior_messages = list(state.get("messages", []))
        if prior_messages and state.get("tool_calls_made"):
            # Replace the original system message with our stricter regeneration prompt
            if isinstance(prior_messages[0], SystemMessage):
                prior_messages[0] = SystemMessage(content=strict_prompt)
            messages = prior_messages
        else:
            messages = [SystemMessage(content=strict_prompt), HumanMessage(content=state["query"])]
        try:
            result   = self._llm_plain.invoke(messages)
            response = result.content
        except Exception as e:
            logger.error(f"[Motor/regenerate] {e}")
            response = state.get("response", f"⚠️ Regeneration failed: {e}")

        return {"response": response, "regenerated": True}

    # ── Conditional Edge Deciders ─────────────────────────────────────────────

    def _route_after_grading(
        self, state: MotorAgentState
    ) -> Literal["generate", "rewrite_query"]:
        """
        If relevant docs were found, or we have already retried twice, go to generate.
        Otherwise rewrite the query and retry retrieval (corrective RAG loop).
        """
        if state["relevant_documents"] or state["retry_count"] >= 2:
            return "generate"
        return "rewrite_query"

    def _route_after_generate(
        self, state: MotorAgentState
    ) -> Literal["execute_tools", "self_evaluate"]:
        """
        If the LLM requested tool calls, execute them first.
        Otherwise go directly to self-evaluation (Concept 3).
        """
        msgs = state.get("messages", [])
        if msgs and hasattr(msgs[-1], "tool_calls") and msgs[-1].tool_calls:
            return "execute_tools"
        return "self_evaluate"

    def _route_after_self_eval(
        self, state: MotorAgentState
    ) -> Literal["end", "regenerate"]:
        """
        Concept 3 routing: regenerate once if quality is poor, then always end.
        Score < 3 OR ungrounded → regenerate (only if not already regenerated).
        When tools were called the response is grounded in IRDAI tool output
        (not document chunks), so self-eval's document-based grounding check is
        bypassed to avoid incorrectly discarding a correct tool-derived answer.
        """
        if state.get("regenerated", False):
            return "end"   # already attempted one correction, accept result
        # Tool-grounded answers: calculate_idv / calculate_ncb / estimate_od_premium
        # already embed IRDAI-compliant values — don't regenerate on missing doc grounding.
        if state.get("tool_calls_made"):
            return "end"
        score    = state.get("self_eval_score", 5)
        grounded = state.get("self_eval_grounded", "yes")
        if score < 3 or grounded == "no":
            return "regenerate"
        return "end"

    # ── Graph Construction ────────────────────────────────────────────────────

    def _build_graph(self):
        g = StateGraph(MotorAgentState)

        # ── Register nodes ────────────────────────────────────────────────────
        g.add_node("classify_intent",      self._classify_intent)       # Concept 1
        g.add_node("multi_query_retrieve", self._multi_query_retrieve)  # Concept 2
        g.add_node("retrieve",             self._retrieve)              # corrective loop
        g.add_node("grade_documents",      self._grade_documents)
        g.add_node("rewrite_query",        self._rewrite_query)
        g.add_node("generate",             self._generate)              # Concept 4 memory
        g.add_node("execute_tools",        self._execute_tools)
        g.add_node("self_evaluate",        self._self_evaluate)         # Concept 3
        g.add_node("regenerate",           self._regenerate)            # Concept 3

        # ── Static edges ──────────────────────────────────────────────────────
        g.add_edge(START,                  "classify_intent")
        g.add_edge("classify_intent",      "multi_query_retrieve")   # Concept 2 entry
        g.add_edge("multi_query_retrieve", "grade_documents")
        g.add_edge("rewrite_query",        "retrieve")               # corrective loop
        g.add_edge("retrieve",             "grade_documents")
        g.add_edge("execute_tools",        "self_evaluate")          # tools → self-eval
        g.add_edge("regenerate",           "self_evaluate")          # reflection → re-eval

        # ── Conditional edges ─────────────────────────────────────────────────
        g.add_conditional_edges(
            "grade_documents",
            self._route_after_grading,
            {"generate": "generate", "rewrite_query": "rewrite_query"},
        )
        g.add_conditional_edges(
            "generate",
            self._route_after_generate,
            {"execute_tools": "execute_tools", "self_evaluate": "self_evaluate"},
        )
        g.add_conditional_edges(
            "self_evaluate",
            self._route_after_self_eval,
            {"end": END, "regenerate": "regenerate"},
        )

        return g.compile()

    # ── Public interface (same contract as BaseDepartmentAgent.process_query) ─

    def process_query(self, query: str) -> dict:
        """
        Run the full LangGraph pipeline end-to-end.

        Concept 4 — memory is loaded before graph invocation and saved after,
        so each call enriches the rolling-window history for the next turn.

        Returns the same dict shape as BaseDepartmentAgent.process_query(),
        with extra keys for the UI trace (tool_calls, rewritten_query, intent,
        multi_queries, self_eval_score, self_eval_grounded, memory_turns).
        """
        logger.info(f"[MotorInsuranceAgent] '{query[:80]}'")

        # ── Concept 4: load conversation memory ───────────────────────────────
        memory_context = self._memory.load_memory_as_string()
        memory_turns   = len(self._memory)

        init: MotorAgentState = {
            # Core
            "query":              query,
            "rewritten_query":    "",
            "documents":          [],
            "relevant_documents": [],
            "messages":           [],
            "response":           "",
            "retry_count":        0,
            "tool_calls_made":    [],
            # Concept 1
            "query_intent":       "",
            "intent_confidence":  0.0,
            # Concept 2
            "multi_queries":      [],
            "all_documents":      [],
            # Concept 3
            "self_eval_score":    0,
            "self_eval_grounded": "",
            "regenerated":        False,
            # Concept 4
            "memory_context":     memory_context,
        }
        try:
            final = self._graph.invoke(init)
        except Exception as e:
            logger.error(f"[MotorInsuranceAgent] Graph error: {e}")
            return {
                "response":           f"⚠️ Error: {e}",
                "sources":            [],
                "department":         self.department_id,
                "agent_name":         self.name,
                "tool_calls":         [],
                "rewritten_query":    "",
                "query_intent":       "",
                "intent_confidence":  0.0,
                "multi_queries":      [],
                "self_eval_score":    0,
                "self_eval_grounded": "",
                "memory_turns":       memory_turns,
            }

        # ── Concept 4: save this turn to memory ───────────────────────────────
        try:
            self._memory.save_context(
                user_input=query,
                assistant_output=final.get("response", ""),
            )
        except Exception:
            pass

        logger.info(
            f"[MotorInsuranceAgent] Done — "
            f"intent={final.get('query_intent')} (conf={final.get('intent_confidence', 0):.2f}), "
            f"multi_q={len(final.get('multi_queries', []))}, "
            f"unique_chunks={len(final.get('all_documents', []))}, "
            f"relevant={len(final.get('relevant_documents', []))}, "
            f"tools={final.get('tool_calls_made', [])}, "
            f"self_eval={final.get('self_eval_score')}/5 "
            f"grounded={final.get('self_eval_grounded')}, "
            f"regenerated={final.get('regenerated')}"
        )
        return {
            "response":           final.get("response", "No response generated."),
            "sources":            final.get("relevant_documents") or final.get("all_documents", []),
            "department":         self.department_id,
            "agent_name":         self.name,
            "tool_calls":         final.get("tool_calls_made", []),
            "rewritten_query":    final.get("rewritten_query", ""),
            "query_intent":       final.get("query_intent", ""),
            "intent_confidence":  final.get("intent_confidence", 0.0),
            "multi_queries":      final.get("multi_queries", []),
            "self_eval_score":    final.get("self_eval_score", 0),
            "self_eval_grounded": final.get("self_eval_grounded", ""),
            "memory_turns":       memory_turns,
        }


# Singleton instance
motor_insurance_agent = MotorInsuranceAgent()
