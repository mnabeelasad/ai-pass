from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Shared state passed between all LangGraph nodes."""

    # Input
    task_id: str
    document_text: str
    policy_text: str

    # RAG
    chunks: List[str] = Field(default_factory=list)
    retrieved_context: List[str] = Field(default_factory=list)

    # Analysis
    analysis_summary: str = ""

    # Decision
    decision: Optional[str] = None          # PASS | FAIL | NEEDS_INFO
    reasons: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    steps_taken: List[str] = Field(default_factory=list)

    # Error tracking
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True