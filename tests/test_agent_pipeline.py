from src.agent.router import QuestionRouter
from src.agent.capability import NumericCapabilityResolver
from src.agent.dispatcher import QuestionDispatcher
from src.agent.executor import ToolExecutor, ExecutionContext
from src.tools.company_facts import CompanyFactsTool
from src.retrieval.retriever import Retriever


def build_pipeline():
    router = QuestionRouter()
    capability = NumericCapabilityResolver()
    dispatcher = QuestionDispatcher()

    company_facts = CompanyFactsTool()
    retriever = Retriever()

    executor = ToolExecutor(
        company_facts_tool=company_facts,
        retriever=retriever,
    )

    return router, capability, dispatcher, executor


def run_pipeline(question, ticker="AAPL", fiscal_year=2025):
    (
        router,
        capability,
        dispatcher,
        executor,
    ) = build_pipeline()

    router_result = router.route(question)

    capability_result = None

    if router_result.route.value in ("numeric", "hybrid"):
        capability_result = capability.resolve(question)

    plan = dispatcher.dispatch(
        router_result=router_result,
        capability_result=capability_result,
    )

    result = executor.execute(
        plan=plan,
        question=question,
        context=ExecutionContext(
            ticker=ticker,
            fiscal_year=fiscal_year,
        ),
    )

    return router_result, capability_result, plan, result


def test_real_numeric_pipeline():
    question = "What was Apple's revenue in 2025?"

    router_result, capability_result, plan, result = run_pipeline(
        question
    )

    assert router_result.route.value == "numeric"
    assert capability_result is not None
    assert capability_result.supported is True
    assert capability_result.metric == "revenue"

    assert plan.status == "ready"
    assert plan.tools_to_run == ["company_facts"]
    assert plan.metric == "revenue"

    assert result.status == "success"
    assert len(result.evidence) == 1

    evidence = result.evidence[0]

    assert evidence.source_type == "company_facts"
    assert evidence.provenance["ticker"] == "AAPL"
    assert evidence.provenance["metric"] == "Revenue from Contract with Customer, Excluding Assessed Tax"
    assert evidence.provenance["value"] == 416161000000
    assert evidence.provenance["fiscal_year"] == 2025


def test_real_narrative_pipeline():
    question = "What products and services does Apple offer?"

    router_result, capability_result, plan, result = run_pipeline(
        question
    )

    assert router_result.route.value == "narrative"
    assert capability_result is None

    assert plan.status == "ready"
    assert plan.tools_to_run == ["retriever"]
    assert plan.metric is None

    assert result.status == "success"
    assert len(result.evidence) > 0

    for evidence in result.evidence:
        assert evidence.source_type == "filing_chunk"
        assert evidence.content
        assert "chunk_id" in evidence.provenance


def test_real_hybrid_pipeline():
    question = (
        "What was Apple's revenue in 2025, "
        "and why did it change?"
    )

    router_result, capability_result, plan, result = run_pipeline(
        question
    )

    assert router_result.route.value == "hybrid"

    assert capability_result is not None
    assert capability_result.supported is True
    assert capability_result.metric == "revenue"

    assert plan.status == "ready"
    assert plan.tools_to_run == [
        "company_facts",
        "retriever",
    ]

    assert result.status == "success"

    source_types = {
        evidence.source_type
        for evidence in result.evidence
    }

    assert "company_facts" in source_types
    assert "filing_chunk" in source_types


def test_unsupported_numeric_pipeline():
    question = "What was Apple's gross profit in 2025?"

    router_result, capability_result, plan, result = run_pipeline(
        question
    )

    assert router_result.route.value == "numeric"

    assert capability_result is not None
    assert capability_result.supported is False

    assert plan.status == "unsupported"
    assert plan.tools_to_run == []
    assert plan.metric is None

    assert result.status == "unsupported"
    assert result.evidence == []


def run_tests():
    tests = [
        test_real_numeric_pipeline,
        test_real_narrative_pipeline,
        test_real_hybrid_pipeline,
        test_unsupported_numeric_pipeline,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print(f"PASS: {passed}/{len(tests)} real pipeline cases passed.")


if __name__ == "__main__":
    run_tests()