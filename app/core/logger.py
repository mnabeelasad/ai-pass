import logging
import json
import time
from typing import Any, Dict
from app.core.config import settings


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


class AgentLogger:
    """Structured logger for agent steps, tools, and latency."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.logger = get_logger("agent")
        self.steps: list[Dict[str, Any]] = []
        self.start_time = time.time()

    def log_step(self, agent: str, action: str, detail: Any = None):
        entry = {
            "task_id": self.task_id,
            "agent": agent,
            "action": action,
            "detail": detail,
            "elapsed_ms": round((time.time() - self.start_time) * 1000, 2),
        }
        self.steps.append(entry)
        self.logger.info(json.dumps(entry))

    def log_tool(self, tool_name: str, input_summary: str, output_summary: str):
        self.log_step(
            agent="tool",
            action=f"TOOL:{tool_name}",
            detail={"input": input_summary, "output": output_summary},
        )

    def log_output(self, output: Dict[str, Any]):
        total_ms = round((time.time() - self.start_time) * 1000, 2)
        self.logger.info(
            json.dumps(
                {
                    "task_id": self.task_id,
                    "event": "FINAL_OUTPUT",
                    "total_latency_ms": total_ms,
                    "output": output,
                }
            )
        )

    def get_steps(self) -> list[Dict[str, Any]]:
        return self.steps