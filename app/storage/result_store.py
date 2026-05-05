"""
Result Store
Simple in-memory store for task results.
Can be replaced with Redis or a database for production.
"""
from typing import Dict, Optional, Any
import time

_store: Dict[str, Dict[str, Any]] = {}


def save_result(task_id: str, result: Dict[str, Any]):
    _store[task_id] = {
        **result,
        "saved_at": time.time(),
    }


def get_result(task_id: str) -> Optional[Dict[str, Any]]:
    return _store.get(task_id)


def list_results() -> Dict[str, Dict[str, Any]]:
    return dict(_store)