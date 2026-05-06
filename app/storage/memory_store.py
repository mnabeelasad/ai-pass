"""
Memory Store
Stores per-session decision history so agents can reference past decisions.
This acts as the memory layer for the multi-agent system.
"""
import time
from typing import Dict, List, Optional, Any

# In-memory store: { session_id: [list of past decisions] }
_memory: Dict[str, List[Dict[str, Any]]] = {}


def save_to_memory(session_id: str, task_id: str, decision: str, reasons: List[str],
                   evidence: List[str], confidence: float, document_preview: str):
    """Save a decision to session memory."""
    if session_id not in _memory:
        _memory[session_id] = []

    entry = {
        "task_id": task_id,
        "decision": decision,
        "reasons": reasons,
        "evidence": evidence,
        "confidence": confidence,
        "document_preview": document_preview[:200],
        "timestamp": time.time(),
    }
    _memory[session_id].append(entry)

    # Keep only last 10 decisions per session
    if len(_memory[session_id]) > 10:
        _memory[session_id] = _memory[session_id][-10:]


def get_memory(session_id: str) -> List[Dict[str, Any]]:
    """Retrieve past decisions for a session."""
    return _memory.get(session_id, [])


def get_memory_summary(session_id: str) -> str:
    """
    Returns a formatted string summary of past decisions.
    This gets injected into agent prompts as context.
    """
    history = get_memory(session_id)
    if not history:
        return "No previous decisions in this session."

    lines = ["Previous decisions in this session:"]
    for i, entry in enumerate(history[-5:], 1):  # last 5 only
        lines.append(
            f"{i}. Decision: {entry['decision']} "
            f"(confidence: {entry['confidence']:.0%}) — "
            f"Document: {entry['document_preview'][:80]}..."
        )
    return "\n".join(lines)


def clear_memory(session_id: str):
    """Clear memory for a session."""
    if session_id in _memory:
        del _memory[session_id]


def list_sessions() -> List[str]:
    """List all active session IDs."""
    return list(_memory.keys())