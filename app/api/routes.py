import uuid
import time
from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File, Form
from typing import Optional
from app.api.schemas import RunTaskRequest, RunTaskResponse, DecisionResult, HealthResponse
from app.agents.orchestrator import run_pipeline
from app.storage.result_store import save_result, get_result
from app.storage.memory_store import get_memory, clear_memory
from app.rag.document_loader import load_document
from app.core.logger import get_logger, AgentLogger

logger = get_logger(__name__)
router = APIRouter()

PENDING_STATE = {
    "status": "processing", "decision": None,
    "reasons": [], "evidence": [], "confidence": 0.0,
    "steps_taken": [], "analysis_summary": None,
    "error": None, "latency_ms": None,
}


def _execute_pipeline(task_id: str, document_text: str,
                      policy_text: str, session_id: str):
    agent_logger = AgentLogger(task_id)
    agent_logger.log_step("api", "TASK_STARTED", {
        "task_id": task_id, "session_id": session_id
    })
    start = time.time()
    try:
        final_state = run_pipeline(
            task_id=task_id,
            document_text=document_text,
            policy_text=policy_text,
            session_id=session_id,
        )
        latency_ms = round((time.time() - start) * 1000, 2)
        result = {
            "task_id": task_id,
            "status": "completed",
            "decision": final_state.decision,
            "reasons": final_state.reasons,
            "evidence": final_state.evidence,
            "confidence": final_state.confidence,
            "steps_taken": final_state.steps_taken,
            "analysis_summary": final_state.analysis_summary,
            "error": final_state.error,
            "latency_ms": latency_ms,
        }
        agent_logger.log_output(result)
        save_result(task_id, result)
        logger.info(f"Task {task_id} completed in {latency_ms}ms")
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        save_result(task_id, {
            "task_id": task_id, "status": "error",
            "decision": None, "reasons": [], "evidence": [],
            "confidence": 0.0, "steps_taken": [], "analysis_summary": None,
            "error": str(e), "latency_ms": None,
        })


@router.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    """Health check endpoint."""
    return HealthResponse()


@router.post("/run-task", response_model=RunTaskResponse, tags=["Agent"])
def run_task(
    request: RunTaskRequest,
    background_tasks: BackgroundTasks,
):
    """
    Submit document as plain text + policy for agentic analysis.
    Include session_id in the request body for memory context.
    Same session_id = agents remember past decisions.
    """
    task_id = str(uuid.uuid4())
    session_id = request.session_id or "default"   # reads from request body
    logger.info(f"New task (text): {task_id} | session: {session_id}")
    save_result(task_id, {"task_id": task_id, **PENDING_STATE})
    background_tasks.add_task(
        _execute_pipeline, task_id,
        request.document_text, request.policy_text, session_id
    )
    return RunTaskResponse(task_id=task_id)


@router.post("/run-task/upload", response_model=RunTaskResponse, tags=["Agent"])
async def run_task_with_file(
    background_tasks: BackgroundTasks,
    policy_text: str = Form(..., description="Policy rules to evaluate against"),
    document_file: Optional[UploadFile] = File(None, description="Upload PDF, TXT, or DOCX"),
    document_text: Optional[str] = Form(None, description="Or paste document text directly"),
    session_id: Optional[str] = Form(None, description="Session ID for memory context"),
):
    """
    Submit a FILE (PDF, TXT, DOCX) + policy for analysis.
    File takes priority over text if both are provided.
    Pass session_id to enable memory across tasks.
    """
    final_text = None

    if document_file and document_file.filename:
        file_bytes = await document_file.read()
        try:
            final_text = load_document(file_bytes, document_file.filename)
            logger.info(f"File uploaded: {document_file.filename} ({len(file_bytes)} bytes)")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    elif document_text:
        final_text = document_text

    if not final_text or not final_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Provide either a document file or document text."
        )

    task_id = str(uuid.uuid4())
    sid = session_id or "default"
    logger.info(f"New task (upload): {task_id} | session: {sid}")
    save_result(task_id, {"task_id": task_id, **PENDING_STATE})
    background_tasks.add_task(
        _execute_pipeline, task_id, final_text, policy_text, sid
    )
    return RunTaskResponse(task_id=task_id)


@router.get("/result/{task_id}", response_model=DecisionResult, tags=["Agent"])
def get_task_result(task_id: str):
    """
    Retrieve result of a previously submitted task.
    Poll this after POST /run-task or POST /run-task/upload.
    """
    result = get_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")
    return DecisionResult(**result)


@router.get("/memory/{session_id}", tags=["Memory"])
def get_session_memory(session_id: str):
    """
    Get all past decisions for a session.
    Use this to verify memory is being saved correctly.
    """
    history = get_memory(session_id)
    return {
        "session_id": session_id,
        "total": len(history),
        "history": history,
    }


@router.delete("/memory/{session_id}", tags=["Memory"])
def clear_session_memory(session_id: str):
    """Clear all memory for a session."""
    clear_memory(session_id)
    return {"session_id": session_id, "status": "cleared"}