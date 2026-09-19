import os
import tempfile
from pathlib import Path


_TEST_DIR = tempfile.TemporaryDirectory()

os.environ["DATABASE_URL"] = (
    "sqlite:///"
    + str(Path(_TEST_DIR.name) / "test.db").replace("\\", "/")
)


from fastapi.testclient import TestClient

from src.api.main import app


def run_tests():
    """
    Test the public API request validation and health contract.
    """

    client = TestClient(app)

    # Valid health request.
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Missing question should be rejected by Pydantic/FastAPI.
    response = client.post(
        "/query",
        json={
            "ticker": "AAPL",
            "fiscal_year": 2025,
        },
    )

    assert response.status_code == 422

    # Invalid fiscal year should be rejected.
    response = client.post(
        "/query",
        json={
            "question": "What was Apple's revenue?",
            "ticker": "AAPL",
            "fiscal_year": 1800,
        },
    )

    assert response.status_code == 422

    print("PASS: 3/3 API contract cases passed.")

    _TEST_DIR.cleanup()


if __name__ == "__main__":
    run_tests()