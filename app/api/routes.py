import uuid
import time
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.api.schemas import RunTaskRequest, RunTaskResponse, DecisionResult, HealthResponse
from app.agents.orchestrator import run_pipeline
from app.storage.result_store import save_result, get_result
from app.core.logger import get_logger, AgentLogger

logger = get_logger(__name__)
router = APIRouter()


def _execute_pipeline(task_id: str, document_text: str, policy_text: str):
    """Background task: runs the full agent pipeline and saves result."""
    agent_logger = AgentLogger(task_id)
    agent_logger.log_step("api", "TASK_STARTED", {"task_id": task_id})

    start = time.time()
    try:
        final_state = run_pipeline(
            task_id=task_id,
            document_text=document_text,
            policy_text=policy_text,
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
            "task_id": task_id,
            "status": "error",
            "decision": None,
            "reasons": [],
            "evidence": [],
            "confidence": 0.0,
            "steps_taken": [],
            "analysis_summary": None,
            "error": str(e),
        })


@router.get("/health", response_model=HealthResponse, tags=["System"])
def health():
    """Health check endpoint."""
    return HealthResponse()


@router.post("/run-task", response_model=RunTaskResponse, tags=["Agent"])
def run_task(request: RunTaskRequest, background_tasks: BackgroundTasks):
    """
    Submit a document + policy for agentic analysis.
    The pipeline runs in the background.
    Returns a task_id to poll for results.
    """
    task_id = str(uuid.uuid4())
    logger.info(f"New task submitted: {task_id}")

    # Save pending state immediately
    save_result(task_id, {
        "task_id": task_id,
        "status": "processing",
        "decision": None,
        "reasons": [],
        "evidence": [],
        "confidence": 0.0,
        "steps_taken": [],
        "analysis_summary": None,
        "error": None,
    })

    background_tasks.add_task(
        _execute_pipeline,
        task_id,
        request.document_text,
        request.policy_text,
    )

    return RunTaskResponse(task_id=task_id)


@router.get("/result/{task_id}", response_model=DecisionResult, tags=["Agent"])
def get_task_result(task_id: str):
    """
    Retrieve the result of a previously submitted task.
    Poll this endpoint after POST /run-task.
    """
    result = get_result(task_id)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found")

    return DecisionResult(**result)