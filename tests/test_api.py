"""
Integration tests for the API layer.
Run with: pytest tests/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

SAMPLE_DOCUMENT = """
John Doe is applying for a loan of $50,000.
His annual income is $45,000.
He has no prior criminal history.
He has been employed for 3 years.
His credit score is 680.
"""

SAMPLE_POLICY = """
Policy Rules:
1. Applicant income must be at least $40,000 annually.
2. Loan amount must not exceed 2x the annual income.
3. Applicant must have no criminal history.
4. Employment duration must be at least 1 year.
5. Credit score must be 650 or above.
"""


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "AI-Pass"


def test_run_task_returns_task_id():
    response = client.post(
        "/run-task",
        json={
            "document_text": SAMPLE_DOCUMENT,
            "policy_text": SAMPLE_POLICY,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "processing"


def test_get_result_pending():
    # Submit first
    run_resp = client.post(
        "/run-task",
        json={
            "document_text": SAMPLE_DOCUMENT,
            "policy_text": SAMPLE_POLICY,
        },
    )
    task_id = run_resp.json()["task_id"]

    # Get result (will be processing or completed)
    result_resp = client.get(f"/result/{task_id}")
    assert result_resp.status_code == 200
    data = result_resp.json()
    assert data["task_id"] == task_id
    assert data["status"] in ["processing", "completed", "error"]


def test_get_result_not_found():
    response = client.get("/result/nonexistent-task-id")
    assert response.status_code == 404