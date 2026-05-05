# AI-Pass: Agentic Execution Platform

> A policy-aware multi-agent decision system powered by LangGraph, RAG, and structured AI reasoning.

**Live Demo:** https://ai-pass.onrender.com
**GitHub:** `https://github.com/mnabeelasad/ai-pass`

---

## What It Does

AI-Pass takes a **document** + **policy rules** and runs them through a multi-agent pipeline to produce a structured business decision:

```
PASS | FAIL | NEEDS_INFO
```

With supporting reasons, evidence, and confidence score.

---

## Architecture

```
POST /run-task (document + policy)
         │
         ▼
 ┌─────────────────┐
 │ Ingestion Agent │  → chunks document → embeds → stores in ChromaDB
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │ Retrieval Agent │  → queries ChromaDB with policy text → retrieves top-k chunks
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │ Analysis Agent  │  → sends doc + context to LLM → produces analysis summary
 └────────┬────────┘
          │
          ▼
 ┌─────────────────┐
 │ Decision Agent  │  → applies policy rules → returns structured verdict
 └────────┬────────┘
          │
          ▼
GET /result/{task_id} → { decision, reasons, evidence, confidence }
```

---

## Agent Design

| Agent | Role | Tool Used |
|---|---|---|
| **IngestionAgent** | Chunks + embeds document into ChromaDB | — |
| **RetrievalAgent** | RAG retrieval using policy as query | `retrieval_tool` |
| **AnalysisAgent** | Analyzes doc + context via LLM | `analysis_tool` |
| **DecisionAgent** | Applies policy rules → verdict | `decision_tool` |

All agents share a **LangGraph StateGraph** with a common `AgentState` object.

---

## RAG Pipeline

1. **Chunking** — Sliding window (300 words, 30 overlap)
2. **Embedding** — `all-MiniLM-L6-v2` (local) or OpenAI `text-embedding-3-small`
3. **Vector DB** — ChromaDB (persistent, cosine similarity)
4. **Retrieval** — Top-5 chunks by semantic similarity to policy query
5. **Injection** — Retrieved chunks injected into LLM context for analysis

---

## Tools

### `retrieval_tool`
Queries ChromaDB for semantically relevant document chunks. Modular — accepts any collection and query.

### `analysis_tool`
Sends document + context to GPT-4o-mini with a structured prompt. Returns factual analysis summary.

### `decision_tool`
Sends policy + analysis to GPT-4o-mini. Returns strict JSON: `{ decision, reasons, evidence, confidence }`.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/run-task` | Submit document + policy |
| `GET` | `/result/{task_id}` | Get decision result |

### Request: POST /run-task
```json
{
  "document_text": "John Doe is applying for a $50,000 loan...",
  "policy_text": "Rule 1: Income must exceed $40,000. Rule 2: ..."
}
```

### Response: GET /result/{task_id}
```json
{
  "task_id": "abc-123",
  "status": "completed",
  "decision": "PASS",
  "reasons": ["Income of $45,000 meets the $40,000 threshold"],
  "evidence": ["annual income is $45,000"],
  "confidence": 0.92,
  "steps_taken": [
    "ingestion_agent: document chunked and embedded",
    "retrieval_agent: retrieved 5 relevant chunks",
    "analysis_agent: document analyzed with RAG context",
    "decision_agent: verdict=PASS confidence=0.92"
  ]
}
```

---

## What Is Real vs Mocked

| Component | Status |
|---|---|
| LangGraph orchestration | ✅ Real |
| ChromaDB vector store | ✅ Real |
| Document chunking | ✅ Real |
| Sentence-transformer embeddings | ✅ Real |
| LLM analysis (GPT-4o-mini) | ✅ Real (requires API key) |
| LLM decision (GPT-4o-mini) | ✅ Real (requires API key) |
| Result store | In-memory (Redis for production) |
| Auth / rate limiting | Not implemented |

---

## Local Setup

### 1. Clone and install
```bash
git clone https://github.com/your-username/ai-pass.git
cd ai-pass
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Run
```bash
uvicorn app.main:app --reload
```

Open: http://localhost:8000/docs

### 4. Docker
```bash
docker-compose up --build
```

---

## Deployment (Render)

1. Push to GitHub
2. Create new Web Service on [render.com](https://render.com)
3. Connect your repo
4. Render auto-detects `render.yaml`
5. Add `OPENAI_API_KEY` as an environment secret
6. Deploy

---

## Future Improvements

- [ ] Redis result store (replace in-memory)
- [ ] Memory layer (per-session context)
- [ ] Streaming output via WebSockets
- [ ] Multi-document ingestion
- [ ] Qdrant as alternative vector DB
- [ ] LangSmith tracing integration
- [ ] Frontend dashboard (Streamlit)
- [ ] Auth middleware (API keys)

---

## Tech Stack

- **FastAPI** — REST API
- **LangGraph** — Agent orchestration
- **LangChain** — LLM abstraction
- **ChromaDB** — Vector database
- **Sentence-Transformers** — Local embeddings
- **OpenAI GPT-4o-mini** — Analysis + decision LLM
- **Docker** — Containerization
- **Render** — Cloud deployment