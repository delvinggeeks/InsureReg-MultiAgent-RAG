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

### 1. Create Virtual Environment (Python 3.11)
```powershell
py -3.11 -m venv venv
```

### 2. Install Dependencies
```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Configure API Key
Edit `.env` and replace the placeholder with your real key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. Run the Application
```powershell
.\venv\Scripts\python.exe -m streamlit run app.py
```

> ⚠️ **Windows Note:** If `.\venv\Scripts\activate` fails with a security error, use the full path to the venv Python directly as shown above. Alternatively, run this once to fix it:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 5. Ingest Sample Documents
Navigate to **📤 Upload Documents** page → Click **"📦 Ingest All Sample Docs"**

### 6. Start Chatting!
Navigate to **💬 Chat** page and ask any insurance regulatory question.

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
