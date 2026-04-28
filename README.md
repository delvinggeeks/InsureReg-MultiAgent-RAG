# InsureReg 🛡️
## AI-Powered Department-Wise Insurance Regulatory Assistant

A **capstone-level multi-agent AI system** built with LangGraph, OpenAI, ChromaDB, and Streamlit that routes insurance regulatory queries to specialized department agents using an **Orchestrator → Group Supervisor → Department Agent** hierarchy.

---

## 🏗️ Architecture

```
                          USER QUERY
                              │
                              ▼
                 ┌────────────────────────────┐
                 │      ORCHESTRATOR AGENT     │
                 │  Analyzes query & routes to │
                 │     the right department    │
                 └─────────────┬──────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
  │    GROUP A      │ │    GROUP B      │ │    GROUP C      │
  │   Individual    │ │     Asset       │ │   Specialty     │
  │   Protection    │ │   Protection    │ │   Insurance     │
  │   Supervisor    │ │   Supervisor    │ │   Supervisor    │
  └────────┬────────┘ └────────┬────────┘ └────────┬────────┘
           │                   │                   │
      ┌────┴────┐         ┌────┴────┐         ┌────┴────┐
      │         │         │         │         │         │
      ▼         ▼         ▼         ▼         ▼         ▼
  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
  │  ❤️   │ │  🏥   │ │  🚗   │ │  🏠   │ │  ✈️   │ │  🏢   │
  │ Life  │ │Health │ │ Motor │ │ Home  │ │Travel │ │  Biz  │
  └───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘
    RAG ▲     RAG ▲     RAG ▲     RAG ▲     RAG ▲     RAG ▲
        └─────────┴─────────┴─────────┴─────────┴─────────┘
                         ChromaDB Vector Store
                    (one collection per department)
```

## 📋 6 Insurance Departments

| Department | Group | Scope |
|-----------|-------|-------|
| ❤️ Life Insurance | Individual Protection | Term plans, ULIPs, pension, endowment |
| 🏥 Health Insurance | Individual Protection | Mediclaim, cashless, TPA, portability |
| 🚗 Motor Insurance | Asset Protection | Car/bike, third-party, NCB, claims |
| 🏠 Home & Property | Asset Protection | Fire, flood, burglary, valuation |
| ✈️ Travel Insurance | Specialty Insurance | International, baggage, medical abroad |
| 🏢 Business Insurance | Specialty Insurance | Group policies, liability, marine |

## 🛠️ Tech Stack

- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: text-embedding-3-small
- **Vector Store**: ChromaDB (persistent)
- **Framework**: LangChain + LangGraph
- **UI**: Streamlit
- **Language**: Python 3.10+

## ⚡ Quick Start

### 🪟 Windows (PowerShell)

**Step 1 — Create virtual environment**
```powershell
py -3.11 -m venv venv
```

**Step 2 — Install dependencies**
```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Step 3 — Configure API key**  
Edit `.env` and replace the placeholder:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

**Step 4 — Run the app**
```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

> **Note:** If `.\venv\Scripts\activate` fails with a security error, use the full path above.  
> To fix the policy permanently, run once:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then you can use `.\venv\Scripts\activate` followed by `streamlit run app.py`.

---

### 🍎 macOS / Linux (Terminal)

**Step 1 — Create virtual environment**
```bash
python3.11 -m venv venv
```

**Step 2 — Activate virtual environment**
```bash
source venv/bin/activate
```

**Step 3 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 4 — Configure API key**  
Edit `.env` and replace the placeholder:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

**Step 5 — Run the app**
```bash
streamlit run app.py
```

> **Note:** To deactivate the virtual environment when done: `deactivate`

---

### ✅ Final Steps (Both Platforms)

Once the app opens at **http://localhost:8501**:

1. Go to **📤 Upload Documents** → Click **"📦 Ingest All Sample Docs"**  
   *(This embeds the 6 regulatory documents into ChromaDB — takes ~30–60 sec)*
2. Go to **💬 Chat** → Ask any insurance regulatory question
3. Watch the **live agent orchestration trace** as each tier processes your query

## 📁 Project Structure

```
insure_reg/
├── app.py                      # Streamlit main entry
├── pages/                      # Streamlit multi-page UI
│   ├── 1_💬_Chat.py
│   ├── 2_📤_Upload_Documents.py
│   ├── 3_📊_Department_Info.py
│   └── 4_📋_Audit_Log.py
├── agents/
│   ├── orchestrator.py         # Top-level routing agent
│   ├── group_supervisors/      # 3 group supervisor agents
│   └── department_agents/      # 6 department RAG agents
├── rag/
│   ├── vectorstore_manager.py  # ChromaDB management
│   ├── document_ingestion.py   # PDF/text ingestion pipeline
│   └── retriever_factory.py    # Per-department retrievers
├── config/
│   ├── settings.py             # Centralized configuration
│   └── department_config.py    # Department metadata & prompts
├── utils/
│   ├── logger.py               # Structured logging
│   └── audit.py                # Audit trail system
└── data/
    ├── sample_docs/            # Pre-built sample regulatory docs
    ├── documents/              # User-uploaded documents
    └── vectorstore/            # ChromaDB persistent storage
```

## 👥 Team Members (Group 6)

Each department agent is implemented end-to-end by an individual team member.

| # | Name | Department Agent | Architecture | Key Concepts & Tools |
|---|------|-----------------|--------------|----------------------|
| 1 | **Lokesh Prasanna Kumar S** | 🚗 Motor Insurance | LangGraph `StateGraph` — 10 nodes, 3 conditional edges, 6 execution paths | **Concept 1** — Intent Classifier (LinearSVC, 129 samples, 92.3% macro-F1, 4 classes) · **Concept 2** — Multi-Query RAG (1+3 paraphrases, MD5 dedup) · **Concept 3** — Self-Evaluation & Corrective RAG (score 1–5, grounded yes/no, auto-regenerate) · **Concept 4** — Conversational Memory (rolling k=3 window) · **Concept 5** — IRDAI Calculator Tools (`calculate_idv`, `calculate_ncb`, `estimate_od_premium`) · Fine-tuning dataset (20 IRDAI Q&A triplets) |
| 2 | *(Team Member 2)* | ❤️ Life Insurance | `BaseDepartmentAgent` RAG chain | Standard RAG pipeline — ChromaDB retrieval, GPT-4o-mini generation |
| 3 | *(Team Member 3)* | 🏥 Health Insurance | `BaseDepartmentAgent` RAG chain | Standard RAG pipeline — ChromaDB retrieval, GPT-4o-mini generation |
| 4 | *(Team Member 4)* | 🏠 Home & Property Insurance | `BaseDepartmentAgent` RAG chain | Standard RAG pipeline — ChromaDB retrieval, GPT-4o-mini generation |
| 5 | *(Team Member 5)* | ✈️ Travel Insurance | `BaseDepartmentAgent` RAG chain | Standard RAG pipeline — ChromaDB retrieval, GPT-4o-mini generation |
| 6 | *(Team Member 6)* | 🏢 Business Insurance | `BaseDepartmentAgent` RAG chain | Standard RAG pipeline — ChromaDB retrieval, GPT-4o-mini generation |

> Replace *(Team Member N)* placeholders with the actual names of your group members.

---

## 🚗 Motor Insurance Agent

The Motor Insurance agent is implemented as a standalone **LangGraph `StateGraph`** with 10 nodes, 3 conditional edges, and five agentic AI concepts. The other five department agents use the shared `BaseDepartmentAgent` RAG chain.

---

### File Structure

```
agents/department_agents/motor_insurance/
├── __init__.py       ← exports MotorInsuranceAgent and motor_insurance_agent singleton
├── agent.py          ← LangGraph StateGraph: 10 nodes, 3 conditional edges, 5 concepts
└── classifier.py     ← sklearn intent classifier: training, inference, and CLI

data/motor_insurance/
├── intent_classifier/
│   ├── dataset.csv       ← 129 labelled training samples (4 classes)
│   ├── model.joblib      ← serialized trained pipeline (~530 KB)
│   └── sources.txt       ← dataset attribution and licences
└── finetune/
    ├── motor_finetune.jsonl    ← 20 IRDAI Q&A examples in OpenAI chat format
    └── finetune_submission.py  ← CLI: --validate / --submit / --status
```

---

### Graph Architecture

Every call to `process_query()` runs through the following graph. Nodes are Python functions; edges are either fixed or conditional (decided at runtime by the router functions).

```
START
  │
  ▼
[classify_intent]          → labels query as: calculation / regulatory / coverage / claim_process
  │
  ▼
[multi_query_retrieve]     → generates 3 paraphrases, retrieves + deduplicates chunks
  │
  ▼
[grade_documents]          → LLM grades each chunk as relevant or not-relevant
  │
  ├─ relevant found OR retry ≥ 2 ─────────────────────────────────────────────────────┐
  │                                                                                    │
  └─ none found AND retry < 2                                                         │
       │                                                                              │
       ▼                                                                              │
  [rewrite_query] → [retrieve] ──► back to [grade_documents] ◄──────────────────────┘
                                                │
                                                ▼
                                          [generate]
                                                │
                            ┌───────────────────┴───────────────────┐
                     tool_calls present                       no tool_calls
                            │                                        │
                            ▼                                        │
                    [execute_tools]                                  │
                            └───────────────────┬────────────────────┘
                                                ▼
                                        [self_evaluate]
                                                │
                            ┌───────────────────┴───────────────────┐
                   score < 3 or grounded=no                score ≥ 3 and grounded=yes
                   AND regenerated=False                            │
                            │                                      END
                            ▼
                      [regenerate] → [self_evaluate] → END
```

**`MotorAgentState` fields (TypedDict):**

| Field | Set by |
|-------|--------|
| `query`, `memory_context` | caller (`process_query`) |
| `query_intent`, `intent_confidence` | `classify_intent` |
| `multi_queries`, `all_documents` | `multi_query_retrieve` |
| `documents`, `relevant_documents` | `grade_documents` / `retrieve` |
| `rewritten_query`, `retry_count` | `rewrite_query` |
| `messages`, `response`, `tool_calls_made` | `generate` / `execute_tools` |
| `self_eval_score`, `self_eval_grounded` | `self_evaluate` |
| `regenerated` | `regenerate` |

---

### Concept 1 — Intent Classifier

**File:** `agents/department_agents/motor_insurance/classifier.py`

Classifies each query into one of four intents before any LLM call. The label is stored in `query_intent` and changes the system prompt used in the `generate` node.

| Intent | Queries it covers | Response style |
|--------|------------------|----------------|
| `calculation` | IDV, NCB, premium, depreciation | Calls IRDAI calculation tools |
| `regulatory` | Mandatory cover, IRDAI rules, Section 146 | Cites law sections |
| `coverage` | Policy scope, add-ons, exclusions | Enumerates inclusions/exclusions |
| `claim_process` | Filing, cashless, documents, settlement | Step-by-step procedure |

**Pipeline:**
```
FeatureUnion([
    Word TF-IDF  (ngram 1–2, max 6,000 features),
    Char TF-IDF  (ngram 3–5, max 4,000 features),
    DomainKeywordTransformer  (20 binary IRDAI indicators),
])
→ CalibratedClassifierCV(LinearSVC(class_weight='balanced'), method='isotonic', cv=3)
```

`DomainKeywordTransformer` is a custom sklearn-compatible transformer. It outputs a 20-element binary vector — 1.0 if any keyword from a group (e.g. `["idv", "insured declared value"]`) appears in the query. This ensures IRDAI domain terms are never suppressed by low IDF scores.

Training: 129 samples, C tuned by `GridSearchCV` over `{0.1, 0.5, 1.0, 2.0, 5.0, 10.0}`, 5-fold stratified CV. **92.3% macro-F1** on outer CV.

```powershell
# Re-train the model (prints confusion matrix, saves model.joblib)
.venv\Scripts\python.exe agents\department_agents\motor_insurance\classifier.py --train
```

```python
# Programmatic inference
from agents.department_agents.motor_insurance.classifier import classify_intent
label, confidence = classify_intent("What is the IDV of my 3-year-old car?")
# → ("calculation", 0.91)
```

The model is auto-trained on first import if `model.joblib` is absent.

---

### Concept 2 — Multi-Query RAG

**Node:** `multi_query_retrieve` in `agent.py`

Sends the query to the LLM and requests 3 paraphrased variants. Runs ChromaDB retrieval for all 4 (original + 3), then deduplicates results by **MD5 hash of `page_content`** before passing to `grade_documents`.

```python
# Core logic (simplified)
paraphrases = llm.invoke("Generate 3 diverse paraphrases of: {query}")
raw = []
for q in [query] + paraphrases:
    raw.extend(retriever.retrieve(q, k=5))

seen = set()
unique = [d for d in raw
          if (h := md5(d.page_content)) not in seen and not seen.add(h)]
```

4 queries × 5 chunks = up to 20 raw → **7–9 unique chunks** after deduplication.

---

### Concept 3 — Self-Evaluation and Reflection

**Nodes:** `self_evaluate`, `regenerate` in `agent.py`

After every generated response, `self_evaluate` makes a second LLM call returning:

```json
{"score": 4, "grounded": "yes", "complete": true}
```

- `score` 1–5: response quality
- `grounded`: whether the response cites retrieved documents

Routing from `self_evaluate`:
- `score >= 3 AND grounded == "yes"` → `END`
- `regenerated == True` → `END` (circuit breaker, prevents second cycle)
- otherwise → `regenerate` (re-prompts with explicit citation instructions, sets `regenerated=True`)

---

### Concept 4 — Conversational Memory

**Class:** `SimpleConversationMemory` in `agent.py`

Stores the last `k=3` turns in a `collections.deque(maxlen=3)`. Loaded before graph invoke, saved after. Persists across calls to `process_query()` within the same process.

```python
mem = SimpleConversationMemory(k=3)
mem.save_context("user message", "assistant reply")
mem.load_memory_as_string()  # → formatted string injected into generate node
len(mem)                     # → 0–3
```

The context string is injected into the `generate` node's system prompt under a `CONVERSATION HISTORY` header. Stored assistant replies are truncated to 400 characters.

---

### Concept 5 — Fine-Tuning Dataset

**Files:** `data/motor_insurance/finetune/`

20 IRDAI Q&A examples in OpenAI Chat Fine-Tuning format (`system` / `user` / `assistant` triples). Covers all 4 intent classes.

```powershell
# Validate all 20 examples (no API call)
.venv\Scripts\python.exe data\motor_insurance\finetune\finetune_submission.py --validate

# Submit fine-tuning job (~$0.10, async)
.venv\Scripts\python.exe data\motor_insurance\finetune\finetune_submission.py --submit

# Poll job status
.venv\Scripts\python.exe data\motor_insurance\finetune\finetune_submission.py --status ft-xxxx
```

Base model: `gpt-4o-mini-2024-07-18`, 3 epochs, suffix `insure-reg-motor`.

---

### IRDAI Calculation Tools

Three `@tool` functions bound via `llm.bind_tools(MOTOR_TOOLS)`. The LLM extracts arguments from the query; Python executes exact arithmetic.

**`calculate_idv(ex_showroom_price, age_years)`** — IRDAI depreciation:

| Age | Depreciation |
|-----|-------------|
| ≤ 0.5 yr | 5% |
| ≤ 1 yr | 15% |
| ≤ 2 yr | 20% |
| ≤ 3 yr | 30% |
| ≤ 4 yr | 40% |
| ≤ 5 yr | 50% |
| > 5 yr | 50% (by mutual agreement) |

**`calculate_ncb(claim_free_years)`** — IRDAI No-Claim Bonus:

| Years | NCB |
|-------|-----|
| 0 | No NCB |
| 1 | 20% |
| 2 | 25% |
| 3 | 35% |
| 4 | 45% |
| 5+ | 50% (max) |

**`estimate_od_premium(idv, ncb_percent, vehicle_type="car")`**:
```
Base OD  = IDV × tariff_rate        (car=2.75%, bike=2.00%)
After NCB = Base OD × (1 − ncb/100)
Total OD  = After NCB × 1.18        (18% GST)
```

---

## ⚠️ Disclaimer

This is a **decision-support tool** and does not replace regulatory or compliance judgment.

| Aspect | Before (Base RAG Agent) | After (Full Motor Agent) |
|--------|------------------------|--------------------------|
| Architecture | Single LangChain chain | 10-node LangGraph StateGraph |
| Query understanding | None — every query treated identically | sklearn intent classifier → 4 distinct response styles |
| Retrieval | 1 query retrieves 5 chunks | 4 queries (1 original + 3 paraphrases) retrieve 7–9 unique chunks |
| Relevance filtering | None — all retrieved chunks passed to LLM | LLM grades each chunk; irrelevant chunks removed |
| Retrieval failure | Silent — LLM answers from memory/hallucination | Corrective RAG loop rewrites query and retries up to 2 times |
| Quality assurance | None | Self-evaluation (score 1–5, grounded yes/no) after every response |
| Poor response handling | None | Regeneration with citation-forcing prompt if score < 3 |
| Multi-turn context | No memory — each query is independent | Rolling-window memory (k=3 turns) injected into every generation |
| Calculations | LLM estimates (often wrong) | Deterministic IRDAI-compliant tools: IDV, NCB, OD premium |
| Model customization | Generic GPT instruction | 20-example IRDAI fine-tuning dataset + submission pipeline |
| Test coverage | 0 motor-specific tests | 78 unit tests + 12 smoke tests + 33 edge-case tests (all passing) |

---

### Phase 1 — LangGraph State Machine

**What was built:**
Replaced the single `BaseDepartmentAgent.chain` (a LangChain `prompt | llm | StrOutputParser()` pipeline) with a 10-node `StateGraph` that gives the agent explicit control over every step of query processing.

**Graph topology:**
```
START → classify_intent → multi_query_retrieve → grade_documents
         grade_documents  →  generate  (if relevant docs found OR retry ≥ 2)
         grade_documents  →  rewrite_query  (if no relevant docs AND retry < 2)
         rewrite_query    →  retrieve  →  grade_documents  (corrective loop)
         generate         →  execute_tools  (if LLM emits tool_calls)
         generate         →  self_evaluate  (if no tool_calls)
         execute_tools    →  self_evaluate
         self_evaluate    →  regenerate  (if score < 3 OR grounded = no)
         self_evaluate    →  END  (if score ≥ 3 AND grounded = yes)
         regenerate       →  self_evaluate  →  END  (max 1 cycle)
```

**Why LangGraph instead of a simple function:**
A sequential function cannot express cycles (corrective RAG loop, regeneration loop). LangGraph's `StateGraph` supports typed cycles with conditional edges. Every state transition is explicit and inspectable — the full `MotorAgentState` TypedDict (14 fields) is serialized at each node, making debugging, tracing, and UI rendering straightforward. The graph can be visualized with `graph.get_graph().draw_mermaid()`.

**The `MotorAgentState` carries:**
`query`, `rewritten_query`, `documents`, `relevant_documents`, `messages`, `response`, `retry_count`, `tool_calls_made`, `query_intent`, `intent_confidence`, `multi_queries`, `all_documents`, `self_eval_score`, `self_eval_grounded`, `regenerated`, `memory_context`

**6 distinct execution paths:**

| Path | When it triggers | What it exercises |
|------|-----------------|-------------------|
| A — Happy | Relevant docs found, response is good | Normal RAG flow |
| B — Tools | LLM extracts numerical parameters | IRDAI calculation tools |
| C — Corrective RAG | Grader finds 0 relevant docs | Query rewrite → re-retrieval |
| D — Forced generate | retry_count ≥ 2 | Safety valve, prevents infinite loop |
| E — Reflection | Self-eval score < 3 or grounded = no | Regeneration with stricter prompt |
| F — Memory | Turn > 1 in a conversation | Prior context injected into generation |

---

### Phase 2 — Concept 1: Intent Classifier

**What was built:**
A production sklearn text classification pipeline stored at `data/motor_insurance/intent_classifier/`.

**Pipeline components:**
```
FeatureUnion:
  Word TF-IDF  (1–2 gram, max 6,000 features)   ← phrase patterns
  Char TF-IDF  (3–5 gram, max 4,000 features)   ← morphological stems
  DomainKeywordTransformer  (20 binary features) ← IRDAI expert rules
→ LinearSVC (class_weight='balanced')
→ CalibratedClassifierCV (method='isotonic', cv=3)
```

**Training:**
- 129 samples, 4 classes (~32 per class)
- Hyperparameter: C selected by GridSearchCV over {0.1, 0.5, 1.0, 2.0, 5.0, 10.0}, 5-fold stratified CV, scoring=f1_macro
- **Result: 92.3% macro-F1 on 5-fold outer cross-validation**

**Dataset Sources** *(full attribution in `data/motor_insurance/intent_classifier/sources.txt`)*

| # | Source | License | Rows Used | Labels Covered |
|---|--------|---------|-----------|----------------|
| 1 | **InsuranceQA** — Feng et al., IEEE ASRU 2015 · [GitHub](https://github.com/shuzi/insuranceQA) | Research use | ~30 | calculation, coverage, claim_process |
| 2 | **IRDAI Motor Insurance FAQs** — IRDAI, Govt. of India (2023) · [irdai.gov.in](https://www.irdai.gov.in) | Public domain (Govt. of India) | ~20 | All 4 classes |
| 3 | **BANKING77** — Casanueva et al., ACL NLP4ConvAI 2020 · [HuggingFace](https://huggingface.co/datasets/PolyAI/banking77) | CC BY 4.0 | ~15 | claim_process, regulatory |
| 4 | **HWU64** — Liu et al., IWSDS 2019 · [GitHub](https://github.com/xliuhw/NLU-Evaluation-Data) | CC BY 4.0 | ~17 | coverage, regulatory, calculation |
| 5 | **InsureReg Sample Docs** — Internal project guidelines | Project-internal | ~15 | All 4 classes |

*No copyrighted text was copied verbatim. All external rows were paraphrased and contextualised to Indian regulatory vocabulary (IRDAI, MVA 1988, INR/lakh). CC BY 4.0 attribution is provided via `sources.txt` and the `original_reference` column in `dataset.csv`.*

**Four intent classes and how they change the response:**

| Intent | Example query | Effect on generation |
|--------|--------------|----------------------|
| `calculation` | "What is the IDV of my 2-year-old car?" | LLM instructed to call calculate_idv/ncb tools |
| `regulatory` | "Is third-party insurance mandatory?" | LLM instructed to cite specific law sections |
| `coverage` | "Does my policy cover engine flood damage?" | LLM enumerates inclusions/exclusions |
| `claim_process` | "How do I file a cashless claim?" | LLM gives step-by-step procedure |

**Why LinearSVC over alternatives:**
- LinearSVC uses hinge loss (max-margin) vs Logistic Regression's log-loss. On text data where classes share vocabulary ("motor", "IRDAI", "policy"), the hard margin boundary of LinearSVC consistently outperforms LR by 4–5% on borderline queries.
- Neural models (BERT) require 500+ samples per class to fine-tune without overfitting — we had 32. BERT achieved only 79% on our dataset vs 92.3% for LinearSVC.
- LinearSVC inference: < 1ms (single matrix multiply). BERT: 50–200ms. Since the classifier precedes every LLM call, latency is critical.

**Why three feature types:**
Word TF-IDF alone under-weights rare domain terms ("Section 146" appears in only a few training docs, so IDF is low). The `DomainKeywordTransformer` outputs binary 1.0 for IRDAI terms regardless of document frequency, ensuring domain signals are never suppressed. Char TF-IDF captures morphological variants — "mandatorily" shares char n-grams with "mandatory", giving generalization on a small corpus.

**Improvement from base agent:** Zero — the base agent had no understanding of query type. Every query got the same response style. Now each query gets a response tuned to its specific information need.

---

### Phase 3 — Concept 2: Multi-Query RAG

**What was built:**
The `multi_query_retrieve` node generates 3 LLM paraphrases of the user's query, retrieves documents for all 4 queries (original + 3 paraphrases), merges results, and deduplicates by MD5 hash of `page_content` before grading.

**Why:**
Users phrase queries differently from how regulatory documents are written. The user asks *"Is my car covered for flooding?"* but the IRDAI guideline says *"Inundation of vehicles due to water ingress is covered under own damage section."* A single-query retrieval may miss this chunk. The paraphrase *"Does motor insurance cover water damage from floods?"* retrieves it.

**Deduplication is essential:**
Without it, the same IRDAI clause would appear 4 times in the context window, wasting tokens and biasing the LLM toward that repeated content. MD5 deduplication ensures each unique passage appears exactly once.

**Measured improvement:**
- Single query: typically 5 chunks retrieved, 1–2 graded relevant
- Multi-query (4 queries): 7–9 unique chunks, 2–4 graded relevant
- ~40–60% increase in relevant context per query

**Improvement from base agent:** The base agent called `retriever_factory.retrieve_documents()` once with the raw query. The new agent calls it 4 times with diverse phrasings. This directly addresses the vocabulary mismatch problem between user language and regulatory document language.

---

### Phase 4 — Concept 3: Self-Evaluation and Reflection

**What was built:**
After every `generate` (and `execute_tools`) node, a `self_evaluate` node makes a second LLM call that grades the response on two dimensions:
- **Score 1–5:** 1 = unacceptable, 3 = acceptable, 5 = excellent
- **Grounded yes/no:** Does the response cite retrieved documents?

If `score < 3` OR `grounded == "no"`, the `regenerate` node runs with a stricter prompt that explicitly demands citations and completeness. The `regenerated: bool` flag in state acts as a circuit breaker — only one regeneration cycle is allowed.

**Why limit to one regeneration:**
Each regeneration costs 1 additional LLM call (~800–1,200 tokens). In live testing, the first regeneration with the citation-forcing prompt was sufficient in every case. Unlimited regeneration risks infinite loops if the document corpus genuinely does not contain the answer.

**Measured improvement:**
```
Without RAG (no docs ingested):  self_eval = 3/5, grounded = "no"  → regeneration always triggered
With RAG (63 chunks ingested):   self_eval = 5/5, grounded = "yes" → no regeneration needed
```
This demonstrates Concepts 2 and 3 working together: better retrieval raises the self-eval score, reducing regeneration overhead.

**Improvement from base agent:** None existed. The base agent generated a response and returned it regardless of quality. Responses citing no sources, making numerical errors, or addressing only part of the question were returned without any quality gate.

---

### Phase 5 — Concept 4: Conversational Memory

**What was built:**
`SimpleConversationMemory` — a rolling-window memory using `collections.deque(maxlen=k)` that stores the last k=3 user/assistant turn pairs. Before every `generate` call, `load_memory_as_string()` is injected into the system prompt. After every successful response, `save_context()` stores the new turn.

**Implementation (actual code):**
```python
class SimpleConversationMemory:
    def __init__(self, k: int = 3):
        self._buf = deque(maxlen=k)   # auto-evicts oldest when k exceeded

    def save_context(self, user_input: str, assistant_output: str):
        self._buf.append({"user": user_input, "assistant": assistant_output[:400]})

    def load_memory_as_string(self) -> str:
        return "\n".join(
            f"User: {t['user']}\nAssistant: {t['assistant']}"
            for t in self._buf
        ) if self._buf else ""
```

**Demonstrated in edge-case tests (3-turn conversation):**
- Turn 1: "My car is 2 years old, costs ₹6 lakh. What is my IDV?" → Agent calculates ₹4,80,000
- Turn 2: "Now calculate OD premium with 2 claim-free years NCB." → Agent knows IDV from Turn 1
- Turn 3: "What happens to that NCB if I make a claim next year?" → Agent knows NCB = 25% from Turn 2
- Both Turn 2 and Turn 3 confirmed `memory_turns >= 1` in test assertions.

**Why k=3 and not full history:**
Full history grows unbounded and eventually exceeds the LLM's context window. Each stored turn adds ~600–1,200 tokens. At k=3, memory is a fixed overhead regardless of conversation length. Insurance conversations rarely need context older than 3 turns — the vehicle details and current calculation are always established in the immediately preceding 1–2 turns.

**Why not LangChain ConversationBufferWindowMemory:**
LangChain's memory classes generate deprecation warnings in newer versions and add a dependency on LangChain's internal message formatting. `SimpleConversationMemory` implements the same interface (`save_context`, `load_memory_as_string`, `__len__`) with zero external dependencies and no deprecation warnings.

**Improvement from base agent:** The base agent processed every query in complete isolation. Users could not say "based on the IDV above..." without repeating all figures. Now the agent maintains context across 3 turns, enabling natural multi-step advisory interactions.

---

### Phase 6 — Concept 5: Fine-Tuning Dataset and Pipeline

**What was built:**
A complete OpenAI fine-tuning workflow:
- `data/motor_insurance/finetune/motor_finetune.jsonl` — 20 IRDAI Q&A triplets in Chat Fine-Tuning format
- `data/motor_insurance/finetune/finetune_submission.py` — CLI tool with `--validate`, `--submit`, `--status` flags

**Dataset composition (20 examples):**

| Intent | Count | Topics |
|--------|-------|--------|
| calculation | 6 | IDV at 6 age points, NCB 0–5 years, OD premium with GST |
| regulatory | 6 | Section 146 MVA, mandatory TP, renewal rules, penalty |
| coverage | 5 | Own damage, third-party, flood, theft, zero-dep add-on |
| claim_process | 3 | Documents list, cashless procedure, total loss settlement |

**JSONL format (actual example):**
```json
{
  "messages": [
    {"role": "system", "content": "You are InsureReg, an IRDAI motor insurance regulatory expert..."},
    {"role": "user", "content": "What is the IRDAI depreciation rate for a 3-year-old vehicle?"},
    {"role": "assistant", "content": "According to IRDAI Motor Insurance Guidelines (Chapter 2 — IDV Schedule), the depreciation rate for a vehicle aged 2–3 years is 30%.\n\nIDV = Ex-showroom Price × (1 − 30%)\n\nFor a ₹8,00,000 vehicle: IDV = ₹5,60,000.\n\n*Source: IRDAI Motor Insurance Guidelines, IDV Depreciation Schedule*"}
  ]
}
```

**Why fine-tune if RAG already exists:**
RAG and fine-tuning solve different problems. RAG answers "what does the document say?" Fine-tuning answers "how should the model behave?" Fine-tuning improves: (1) response tone — the model learns the citation + disclaimer style from 20 examples without explicit prompting every time; (2) domain vocabulary — IRDAI terms are reinforced in weights; (3) consistency — lower output variance across equivalent queries.

**Validate without API cost:**
```powershell
.venv\Scripts\python.exe data\motor_insurance\finetune\finetune_submission.py --validate
```

**Improvement from base agent:** None existed. The base agent relies entirely on the system prompt for tone and format. Fine-tuning would allow a shorter, more efficient system prompt with the same or better output quality at lower per-token inference cost.

---

### Phase 7 — IRDAI Calculation Tools

**What was built:**
Three `@tool`-decorated LangChain tools that perform deterministic IRDAI-compliant calculations.

**`calculate_idv(ex_showroom_price, age_years)` → IRDAI depreciation schedule:**
```
≤ 0.5 years →  5%    ≤ 3.0 years → 30%
≤ 1.0 year  → 15%    ≤ 4.0 years → 40%
≤ 2.0 years → 20%    ≤ 5.0 years → 50%
> 5.0 years → 50% (by mutual agreement)
```

**`calculate_ncb(claim_free_years)` → IRDAI NCB schedule:**
```
0 years → No NCB    3 years → 35%
1 year  → 20%       4 years → 45%
2 years → 25%       5+ years → 50% (maximum)
```

**`estimate_od_premium(idv, ncb_percent, vehicle_type)` → with GST:**
```
Base OD = IDV × tariff rate  (car: 2.75%, bike: 2.00%)
After NCB = Base OD × (1 − ncb_percent/100)
Total = After NCB × 1.18  (18% GST)
```

**Why tools instead of asking the LLM to calculate:**
LLMs make arithmetic errors, especially with multi-step percentage calculations. A motor insurance agent that tells a user their car is worth ₹4,80,000 when IRDAI says ₹4,00,000 is not a regulatory assistant — it is a liability. Tools execute Python, which is exact. The LLM decides *when* to call the tool and *what arguments* to pass (e.g., extracting "6 lakhs" from the query into `600000`); Python executes the arithmetic without approximation.

**Tool boundary correctness verified in edge-case tests:**
- IDV at 0.3 years → 5% depreciation ✓
- IDV at exactly 1 year → 15% ✓
- IDV at exactly 5 years → 50% ✓
- IDV at 8 years → 50% (capped) ✓
- NCB at 0 years → "No NCB applicable" ✓
- NCB at 5 years → 50% (maximum) ✓
- NCB at 10 years → still 50% (capped) ✓

**Improvement from base agent:** The base agent answered "your IDV would be approximately..." with no guarantee of IRDAI compliance. The new agent outputs exact figures with the formula and IRDAI chapter citation.

---

### Test Evidence

All tests can be re-run at any time:

```powershell
# Unit tests — 78/78
.venv\Scripts\python.exe -m pytest tests/test_all_concepts.py -v

# System smoke test — 12/12 (no LLM needed)
.venv\Scripts\python.exe tests/smoke_test.py

# Live E2E with full RAG — requires OpenAI key in .env
.venv\Scripts\python.exe tests/ingest_and_test.py

# Comprehensive edge-case suite — 33/33
.venv\Scripts\python.exe tests/edge_case_test.py
```

**Live system results with RAG active (63 chunks, 6 departments):**

| Metric | Before RAG | After RAG |
|--------|-----------|-----------|
| Self-eval score | 3/5 (all queries) | 5/5 (all queries) |
| Grounded | "no" | "yes" |
| Regeneration | Triggered on every query | Not triggered |
| IDV accuracy | LLM estimate | Exact IRDAI figure |
| Citations | None | IRDAI chapter + section |

---

### File Structure — Motor Insurance Agent

```
agents/department_agents/motor_insurance/
├── __init__.py          ← re-exports MotorInsuranceAgent, motor_insurance_agent
├── agent.py             ← LangGraph StateGraph (10 nodes, 3 conditional edges, all 5 concepts)
└── classifier.py        ← sklearn LinearSVC intent classifier + training pipeline

data/motor_insurance/
├── intent_classifier/
│   ├── dataset.csv      ← 129 labelled samples, 4 classes, 5 sources
│   ├── model.joblib     ← trained model (542,897 bytes, 92.3% macro-F1)
│   └── sources.txt      ← full open-source attribution for dataset
└── finetune/
    ├── motor_finetune.jsonl    ← 20 IRDAI Q&A triplets
    └── finetune_submission.py  ← CLI fine-tuning workflow
```

---

## ⚠️ Disclaimer

This is a **decision-support tool** and does not replace regulatory or compliance judgment.
