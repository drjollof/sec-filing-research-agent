from src.agent.executor import ToolExecutor, ExecutionContext
from src.agent.dispatcher import ExecutionPlan
from src.tools.company_facts import NumericFact
from src.retrieval.retriever import RetrievedChunk


class FakeCompanyFactsTool:
    def __init__(self):
        self.calls = []

    def get_metric(self, ticker, metric, fiscal_year):
        self.calls.append(
            {
                "ticker": ticker,
                "metric": metric,
                "fiscal_year": fiscal_year,
            }
        )

        return NumericFact(
            company="Apple Inc.",
            ticker=ticker,
            fact_name="RevenueFromContractWithCustomerExcludingAssessedTax",
            label="Revenue",
            value=416161000000,
            unit="USD",
            fiscal_year=fiscal_year,
            fiscal_period="FY",
            form="10-K",
            filing_date="2025-10-31",
            accession_number="0000320193-25-000079",
            period_start="2024-09-29",
            period_end="2025-09-27",
        )


class FakeRetriever:
    def __init__(self):
        self.calls = []

    def retrieve(self, question):
        self.calls.append(question)

        return [
            RetrievedChunk(
                chunk_id="TEST_CHUNK_001",
                text="Apple's revenue increased.",
                distance=0.18,
                metadata={
                    "company": "Apple Inc.",
                    "ticker": "AAPL",
                    "section": "Item 7",
                },
            )
        ]


def build_executor():
    company_facts = FakeCompanyFactsTool()
    retriever = FakeRetriever()

    executor = ToolExecutor(
        company_facts_tool=company_facts,
        retriever=retriever,
    )

    return executor, company_facts, retriever


def test_numeric_execution():
    executor, company_facts, retriever = build_executor()

    plan = ExecutionPlan(
        status="ready",
        tools_to_run=["company_facts"],
        metric="revenue",
    )

    result = executor.execute(
        plan=plan,
        question="What was Apple's revenue in 2025?",
        context=ExecutionContext(
            ticker="AAPL",
            fiscal_year=2025,
        ),
    )

    assert result.status == "success"
    assert len(result.evidence) == 1

    evidence = result.evidence[0]

    assert evidence.source_type == "company_facts"
    assert evidence.content == "Revenue: 416,161,000,000 USD"
    assert evidence.provenance["ticker"] == "AAPL"
    assert evidence.provenance["metric"] == "Revenue"
    assert evidence.provenance["value"] == 416161000000
    assert evidence.provenance["fiscal_year"] == 2025

    assert len(company_facts.calls) == 1
    assert company_facts.calls[0]["metric"] == "revenue"

    assert len(retriever.calls) == 0


def test_narrative_execution():
    executor, company_facts, retriever = build_executor()

    plan = ExecutionPlan(
        status="ready",
        tools_to_run=["retriever"],
        metric=None,
    )

    question = "What products and services does Apple offer?"

    result = executor.execute(
        plan=plan,
        question=question,
        context=ExecutionContext(
            ticker="AAPL",
            fiscal_year=2025,
        ),
    )

    assert result.status == "success"
    assert len(result.evidence) == 1

    evidence = result.evidence[0]

    assert evidence.source_type == "filing_chunk"
    assert evidence.content == "Apple's revenue increased."
    assert evidence.provenance["chunk_id"] == "TEST_CHUNK_001"
    assert evidence.provenance["ticker"] == "AAPL"

    assert len(retriever.calls) == 1
    assert retriever.calls[0] == question

    assert len(company_facts.calls) == 0


def test_hybrid_execution():
    executor, company_facts, retriever = build_executor()

    plan = ExecutionPlan(
        status="ready",
        tools_to_run=[
            "company_facts",
            "retriever",
        ],
        metric="revenue",
    )

    question = (
        "What was Apple's revenue in 2025, "
        "and why did it change?"
    )

    result = executor.execute(
        plan=plan,
        question=question,
        context=ExecutionContext(
            ticker="AAPL",
            fiscal_year=2025,
        ),
    )

    assert result.status == "success"
    assert len(result.evidence) == 2

    source_types = [
        evidence.source_type
        for evidence in result.evidence
    ]

    assert "company_facts" in source_types
    assert "filing_chunk" in source_types

    assert len(company_facts.calls) == 1
    assert len(retriever.calls) == 1
    assert retriever.calls[0] == question


def test_unsupported_execution():
    executor, company_facts, retriever = build_executor()

    plan = ExecutionPlan(
        status="unsupported",
        tools_to_run=[],
        metric=None,
    )

    result = executor.execute(
        plan=plan,
        question="What was Apple's gross profit in 2025?",
        context=ExecutionContext(
            ticker="AAPL",
            fiscal_year=2025,
        ),
    )

    assert result.status == "unsupported"
    assert result.evidence == []

    assert len(company_facts.calls) == 0
    assert len(retriever.calls) == 0


def test_unknown_execution():
    executor, company_facts, retriever = build_executor()

    plan = ExecutionPlan(
        status="unknown",
        tools_to_run=[],
        metric=None,
    )

    result = executor.execute(
        plan=plan,
        question="Apple",
        context=ExecutionContext(
            ticker="AAPL",
            fiscal_year=2025,
        ),
    )

    assert result.status == "unknown"
    assert result.evidence == []

    assert len(company_facts.calls) == 0
    assert len(retriever.calls) == 0


def test_missing_numeric_context():
    executor, company_facts, retriever = build_executor()

    plan = ExecutionPlan(
        status="ready",
        tools_to_run=["company_facts"],
        metric="revenue",
    )

    result = executor.execute(
        plan=plan,
        question="What was Apple's revenue in 2025?",
        context=ExecutionContext(
            ticker=None,
            fiscal_year=2025,
        ),
    )

    assert result.status == "invalid"
    assert result.evidence == []

    assert len(company_facts.calls) == 0
    assert len(retriever.calls) == 0


def test_numeric_output_is_normalized():
    executor, _, _ = build_executor()

    plan = ExecutionPlan(
        status="ready",
        tools_to_run=["company_facts"],
        metric="revenue",
    )

    result = executor.execute(
        plan=plan,
        question="What was Apple's revenue in 2025?",
        context=ExecutionContext(
            ticker="AAPL",
            fiscal_year=2025,
        ),
    )

    evidence = result.evidence[0]

    assert hasattr(evidence, "source_type")
    assert hasattr(evidence, "content")
    assert hasattr(evidence, "provenance")

    assert evidence.source_type == "company_facts"


def test_retriever_output_is_normalized():
    executor, _, _ = build_executor()

    plan = ExecutionPlan(
        status="ready",
        tools_to_run=["retriever"],
        metric=None,
    )

    result = executor.execute(
        plan=plan,
        question="What products does Apple offer?",
        context=ExecutionContext(
            ticker="AAPL",
            fiscal_year=2025,
        ),
    )

    evidence = result.evidence[0]

    assert hasattr(evidence, "source_type")
    assert hasattr(evidence, "content")
    assert hasattr(evidence, "provenance")

    assert evidence.source_type == "filing_chunk"
    assert evidence.provenance["chunk_id"] == "TEST_CHUNK_001"


def run_tests():
    tests = [
        test_numeric_execution,
        test_narrative_execution,
        test_hybrid_execution,
        test_unsupported_execution,
        test_unknown_execution,
        test_missing_numeric_context,
        test_numeric_output_is_normalized,
        test_retriever_output_is_normalized,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print(f"PASS: {passed}/{len(tests)} executor cases passed.")


if __name__ == "__main__":
    run_tests()