from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def run_tests():
    print("Testing POST /query (Full API Integration)...")
    print("This will execute the agent and query OpenRouter, please wait...\n")

    response = client.post(
        "/query",
        json={
            "question": "What was Apple's total assets at the end of 2025?",
            "ticker": "AAPL",
            "fiscal_year": 2025,
        },
    )

    assert response.status_code == 200, f"Error: {response.text}"

    data = response.json()

    print("=" * 80)
    print("API RESPONSE")
    print("=" * 80)
    print(f"Status:       {data['status']}")
    print(f"Route:        {data['route']}")
    print(f"Verdict:      {data['verification']['verdict']}")
    print(f"Model:        {data['model']}")
    print(f"Completeness: {data['completeness']}")
    print(f"\nAnswer:       {data['answer']}")
    print("=" * 80)

    print("\nPASS: API successfully served the RAG pipeline end-to-end!")


if __name__ == "__main__":
    run_tests()