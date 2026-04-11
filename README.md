# InsureReg 🛡️
## AI-Powered Department-Wise Insurance Regulatory Assistant

A **capstone-level multi-agent AI system** built with LangGraph, OpenAI, ChromaDB, and Streamlit that routes insurance regulatory queries to specialized department agents using an **Orchestrator → Group Supervisor → Department Agent** hierarchy.

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌──────────────────────────────────┐
│      🎯 ORCHESTRATOR AGENT       │
│  Analyzes query, routes to group │
└──────────────┬───────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│Group A │ │Group B │ │Group C │
│Individual│ │Asset  │ │Specialty│
│Protection│ │Protection│ │Insurance│
└────┬───┘ └────┬───┘ └────┬───┘
     │          │          │
  ┌──┴──┐   ┌──┴──┐   ┌──┴──┐
  ▼     ▼   ▼     ▼   ▼     ▼
❤️Life 🏥Health 🚗Motor 🏠Home ✈️Travel 🏢Business
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

## ⚠️ Disclaimer

This is a **decision-support tool** and does not replace regulatory or compliance judgment.
