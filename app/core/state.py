from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """
    Shared state passed between all LangGraph nodes.
    Now includes memory context and confidence tracking
    for advanced conditional flow.
    """

    # ── Input ─────────────────────────────────────────
    task_id: str
    document_text: str
    policy_text: str

    # ── Session Memory ────────────────────────────────
    session_id: str = "default"           # groups tasks by user/session
    memory_context: str = ""              # injected summary of past decisions

    # ── RAG ───────────────────────────────────────────
    chunks: List[str] = Field(default_factory=list)
    retrieved_context: List[str] = Field(default_factory=list)

    # ── Analysis ──────────────────────────────────────
    analysis_summary: str = ""
    analysis_confidence: float = 0.0     # estimated confidence from analysis
    retrieval_attempts: int = 0          # tracks how many times we've retrieved

    # ── Decision ──────────────────────────────────────
    decision: Optional[str] = None       # PASS | FAIL | NEEDS_INFO
    reasons: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    steps_taken: List[str] = Field(default_factory=list)

    # ── Error ─────────────────────────────────────────
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True