from src.agent.capability import NumericCapabilityResolver


SUPPORTED_CASES = [
    ("What was Apple's revenue in 2025?", "revenue"),
    ("What were Apple's revenues in 2025?", "revenue"),
    ("What were Apple's total sales in 2025?", "revenue"),
    ("What were Apple's total assets in 2025?", "total_assets"),
    ("How much cash did Apple have in 2025?", "cash"),
    ("What was Apple's net income in 2025?", "net_income"),
    ("What were Apple's net earnings in 2025?", "net_income"),
]


UNSUPPORTED_CASES = [
    "How much revenue did Apple generate from Services?",
    "What were Apple's iPhone sales in 2025?",
    "What was Apple's gross profit in 2025?",
    "What was Apple's operating income in 2025?",
    "What was Apple's free cash flow in 2025?",
]


def test_numeric_capability():
    resolver = NumericCapabilityResolver()

    failures = []

    print("\n" + "=" * 80)
    print("NUMERIC CAPABILITY TEST")
    print("=" * 80)

    for question, expected_metric in SUPPORTED_CASES:
        result = resolver.resolve(question)

        print(f"\nQuestion:  {question}")
        print(f"Expected:  supported → {expected_metric}")
        print(f"Actual:    {result.supported} → {result.metric}")
        print(f"Reason:    {result.reason}")

        if not result.supported or result.metric != expected_metric:
            failures.append(
                {
                    "question": question,
                    "expected": expected_metric,
                    "actual": result.metric,
                }
            )

    for question in UNSUPPORTED_CASES:
        result = resolver.resolve(question)

        print(f"\nQuestion:  {question}")
        print("Expected:  unsupported")
        print(f"Actual:    {result.supported} → {result.metric}")
        print(f"Reason:    {result.reason}")

        if result.supported:
            failures.append(
                {
                    "question": question,
                    "expected": "unsupported",
                    "actual": result.metric,
                }
            )

    assert not failures, f"Capability failures:\n{failures}"

    total = len(SUPPORTED_CASES) + len(UNSUPPORTED_CASES)

    print("\n" + "=" * 80)
    print(f"PASS: {total}/{total} capability cases passed.")
    print("=" * 80)


if __name__ == "__main__":
    test_numeric_capability()