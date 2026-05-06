from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.logger import get_logger

logger = get_logger("main")

app = FastAPI(
    title="AI-Pass: Agentic Execution Platform",
    description="""
## AI-Pass Multi-Agent System

A policy-aware decision engine powered by LangGraph, RAG, and structured AI reasoning.

1. **POST /run-task** — Submit document as plain text + policy
2. **POST /run-task/upload** — Upload PDF/TXT/DOCX + policy
3. **GET /result/{task_id}** — Poll for result
4. **GET /memory/{session_id}** — Get session memory

### Agent Pipeline
`Ingestion → Retrieval (RAG) → Analysis → Decision`

### Output
Returns: `PASS | FAIL | NEEDS_INFO` with reasons, evidence, and confidence score.
""",
    version="1.0.0",
)

# Enable CORS (Allows your Streamlit frontend to talk to this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your API routes
app.include_router(router)

# A simple root endpoint just so the server doesn't show a 404 if you visit the base URL
@app.get("/", tags=["System"])
def root():
    return {"message": "AI-Pass Backend API is running! Go to /docs for the API documentation."}

logger.info("AI-Pass API started")