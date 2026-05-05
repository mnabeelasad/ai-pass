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

### Flow
1. **POST /run-task** — Submit document + policy text
2. **GET /result/{task_id}** — Poll for result

### Agent Pipeline
`Ingestion → Retrieval (RAG) → Analysis → Decision`

### Output
Returns: `PASS | FAIL | NEEDS_INFO` with reasons, evidence, and confidence score.
""",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

logger.info("AI-Pass API started")