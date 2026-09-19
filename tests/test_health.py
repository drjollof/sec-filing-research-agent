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
    Test the FastAPI health endpoint.
    """

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data == {
        "status": "ok",
    }

    print("PASS: 1/1 health endpoint test passed.")

    _TEST_DIR.cleanup()


if __name__ == "__main__":
    run_tests()