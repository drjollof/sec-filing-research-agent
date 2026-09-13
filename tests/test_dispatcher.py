from src.agent.router import QuestionRouter, Route
from src.agent.capability import NumericCapabilityResolver
from src.agent.dispatcher import QuestionDispatcher


router = QuestionRouter()
capability = NumericCapabilityResolver()
dispatcher = QuestionDispatcher()


TEST_CASES = [
    # Numeric + supported
    (
        "What was Apple's revenue in 2025?",
        "ready",
        ["company_facts"],
        "revenue",
    ),
    (
        "What were Apple's total assets in 2025?",
        "ready",
        ["company_facts"],
        "total_assets",
    ),
    (
        "How much cash did Apple have in 2025?",
        "ready",
        ["company_facts"],
        "cash",
    ),
    (
        "What was Apple's net income in 2025?",
        "ready",
        ["company_facts"],
        "net_income",
    ),

    # Numeric + unsupported
    (
        "How much revenue did Apple generate from Services?",
        "unsupported",
        [],
        None,
    ),
    (
        "What were Apple's iPhone sales in 2025?",
        "unsupported",
        [],
        None,
    ),
    (
        "What was Apple's gross profit in 2025?",
        "unsupported",
        [],
        None,
    ),
    (
        "What was Apple's operating income in 2025?",
        "unsupported",
        [],
        None,
    ),
    (
        "What was Apple's free cash flow in 2025?",
        "unsupported",
        [],
        None,
    ),

    # Narrative
    (
        "Why did Apple's revenue increase in 2025?",
        "ready",
        ["retriever"],
        None,
    ),
    (
        "What risks does Apple face?",
        "ready",
        ["retriever"],
        None,
    ),
    (
        "What products and services does Apple offer?",
        "ready",
        ["retriever"],
        None,
    ),
    (
        "Describe Apple's business.",
        "ready",
        ["retriever"],
        None,
    ),

    # Hybrid + supported
    (
        "What was Apple's revenue in 2025, and why did it change?",
        "ready",
        ["company_facts", "retriever"],
        "revenue",
    ),
    (
        "What was Apple's net income in 2025, and what caused the change?",
        "ready",
        ["company_facts", "retriever"],
        "net_income",
    ),
    (
        "How much cash did Apple have in 2025, and why did it change?",
        "ready",
        ["company_facts", "retriever"],
        "cash",
    ),

    # Unknown
    (
        "Apple",
        "unknown",
        [],
        None,
    ),
    (
        "Hello",
        "unknown",
        [],
        None,
    ),
]


def test_dispatcher_pipeline():
    passed = 0

    for question, expected_status, expected_tools, expected_metric in TEST_CASES:
        router_result = router.route(question)

        capability_result = None

        if router_result.route in (Route.NUMERIC, Route.HYBRID):
            capability_result = capability.resolve(question)

        plan = dispatcher.dispatch(
            router_result,
            capability_result,
        )

        assert plan.status == expected_status, (
            f"\nQuestion: {question}"
            f"\nExpected status: {expected_status}"
            f"\nActual status: {plan.status}"
        )

        assert plan.tools_to_run == expected_tools, (
            f"\nQuestion: {question}"
            f"\nExpected tools: {expected_tools}"
            f"\nActual tools: {plan.tools_to_run}"
        )

        assert plan.metric == expected_metric, (
            f"\nQuestion: {question}"
            f"\nExpected metric: {expected_metric}"
            f"\nActual metric: {plan.metric}"
        )

        passed += 1

    print(f"PASS: {passed}/{len(TEST_CASES)} dispatcher cases passed.")



if __name__ == "__main__":
    test_dispatcher_pipeline()