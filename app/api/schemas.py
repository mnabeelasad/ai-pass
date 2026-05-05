from pydantic import BaseModel, Field
from typing import List, Optional


class RunTaskRequest(BaseModel):
    document_text: str = Field(..., description="The document or text to analyze")
    policy_text: str = Field(..., description="The policy rules to evaluate against")


class RunTaskResponse(BaseModel):
    task_id: str
    status: str = "processing"
    message: str = "Task submitted successfully"


class DecisionResult(BaseModel):
    task_id: str
    status: str  # "completed" | "error" | "not_found"

    # Decision fields
    decision: Optional[str] = None      # PASS | FAIL | NEEDS_INFO
    reasons: List[str] = []
    evidence: List[str] = []
    confidence: float = 0.0
    steps_taken: List[str] = []

    # Metadata
    analysis_summary: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "AI-Pass"
    version: str = "1.0.0"