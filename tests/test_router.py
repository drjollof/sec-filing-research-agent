from src.agent.router import QuestionRouter, Route


TEST_CASES = [
    # Numeric
    ("What was Apple's revenue in 2025?", Route.NUMERIC),
    ("What was Apple's net income in 2025?", Route.NUMERIC),
    ("What were Apple's total assets in 2025?", Route.NUMERIC),
    ("How much cash did Apple have at the end of 2025?", Route.NUMERIC),
    ("What was Apple's revenue in 2024 and 2025?", Route.NUMERIC),
    ("How much did Apple's revenue increase from 2024 to 2025?", Route.NUMERIC),
    ("Tell me Apple's revenue.", Route.NUMERIC),

    # Narrative
    ("Why did Apple's revenue increase in 2025?", Route.NARRATIVE),
    ("Why did Apple's revenue change in 2025?", Route.NARRATIVE),
    ("What factors affected Apple's revenue in 2025?", Route.NARRATIVE),
    ("What did Apple say about its performance in China?", Route.NARRATIVE),
    ("What risks does Apple identify in its 2025 10-K?", Route.NARRATIVE),
    ("How does Apple describe its business?", Route.NARRATIVE),
    ("What products and services does Apple offer?", Route.NARRATIVE),
    ("Why did Apple's net income differ from the previous year?", Route.NARRATIVE),
    ("Explain Apple's revenue performance.", Route.NARRATIVE),

    # Unknown
    ("Apple", Route.UNKNOWN),
    ("Hello", Route.UNKNOWN),
        # Hybrid
    (
        "What was Apple's revenue in 2025, and why did it change?",
        Route.HYBRID,
    ),
    (
        "What was Apple's net income in 2025, and what caused the change?",
        Route.HYBRID,
    ),
    (
        "How much cash did Apple have in 2025, and why did it change?",
        Route.HYBRID,
    ),
]


def test_router():
    router = QuestionRouter()

    failures = []

    for question, expected_route in TEST_CASES:
        result = router.route(question)

        if result.route != expected_route:
            failures.append(
                {
                    "question": question,
                    "expected": expected_route.value,
                    "actual": result.route.value,
                    "reason": result.reason,
                }
            )

    print("\n" + "=" * 80)
    print("ROUTER TEST")
    print("=" * 80)

    for question, expected_route in TEST_CASES:
        result = router.route(question)

        print(f"\nQuestion:  {question}")
        print(f"Expected:  {expected_route.value}")
        print(f"Actual:    {result.route.value}")
        print(f"Reason:    {result.reason}")

    assert not failures, f"Routing failures:\n{failures}"

    print("\n" + "=" * 80)
    print(f"PASS: {len(TEST_CASES)}/{len(TEST_CASES)} routing cases passed.")
    print("=" * 80)




if __name__ == "__main__":
    test_router()