from src.agent.evidence import Evidence
from src.agent.prompt_builder import PromptBuilder


def test_numeric_prompt():
    evidence = [
        Evidence(
            source_type="company_facts",
            content="Revenue: 416,161,000,000 USD",
            provenance={
                "company": "Apple Inc.",
                "ticker": "AAPL",
                "metric": "Revenue",
                "concept": (
                    "RevenueFromContractWithCustomerExcludingAssessedTax"
                ),
                "value": 416161000000,
                "unit": "USD",
                "fiscal_year": 2025,
                "fiscal_period": "FY",
                "form": "10-K",
                "filing_date": "2025-10-31",
                "accession_number": "0000320193-25-000079",
            },
        )
    ]

    builder = PromptBuilder()

    context = builder.build(
        question="What was Apple's revenue in 2025?",
        evidence=evidence,
    )

    assert "What was Apple's revenue in 2025?" in context.user_prompt
    assert "[E1]" in context.user_prompt
    assert "Revenue: 416,161,000,000 USD" in context.user_prompt
    assert "AAPL" in context.user_prompt
    assert "416161000000" in context.user_prompt

    assert "Do not invent facts" in context.system_prompt
    assert "numeric claim" in context.system_prompt


def test_narrative_prompt():
    evidence = [
        Evidence(
            source_type="filing_chunk",
            content=(
                "Apple designs, manufactures, and markets "
                "smartphones, personal computers, tablets, "
                "wearables, and related services."
            ),
            provenance={
                "chunk_id": "AAPL_TEST_001",
                "ticker": "AAPL",
                "section": "Item 1",
            },
        )
    ]

    builder = PromptBuilder()

    context = builder.build(
        question="What products does Apple offer?",
        evidence=evidence,
    )

    assert "[E1]" in context.user_prompt
    assert "Apple designs" in context.user_prompt
    assert "AAPL_TEST_001" in context.user_prompt
    assert "Item 1" in context.user_prompt


def test_hybrid_prompt():
    evidence = [
        Evidence(
            source_type="company_facts",
            content="Revenue: 416,161,000,000 USD",
            provenance={
                "ticker": "AAPL",
                "metric": "Revenue",
                "value": 416161000000,
                "fiscal_year": 2025,
            },
        ),
        Evidence(
            source_type="filing_chunk",
            content="Services net sales increased during 2025.",
            provenance={
                "chunk_id": "AAPL_TEST_002",
                "ticker": "AAPL",
                "section": "Item 7",
            },
        ),
    ]

    builder = PromptBuilder()

    context = builder.build(
        question=(
            "What was Apple's revenue in 2025, "
            "and why did it change?"
        ),
        evidence=evidence,
    )

    assert "[E1]" in context.user_prompt
    assert "[E2]" in context.user_prompt

    assert "416,161,000,000" in context.user_prompt
    assert "Services net sales increased" in context.user_prompt

    assert "company_facts" in context.user_prompt
    assert "filing_chunk" in context.user_prompt


def test_empty_evidence():
    builder = PromptBuilder()

    context = builder.build(
        question="What was Apple's revenue in 2025?",
        evidence=[],
    )

    assert "No evidence was retrieved." in context.user_prompt
    assert "What was Apple's revenue in 2025?" in context.user_prompt

    assert "If the evidence is insufficient" in context.system_prompt


def test_multiple_evidence_ids_are_unique():
    evidence = [
        Evidence(
            source_type="filing_chunk",
            content="Evidence one.",
            provenance={"chunk_id": "CHUNK_001"},
        ),
        Evidence(
            source_type="filing_chunk",
            content="Evidence two.",
            provenance={"chunk_id": "CHUNK_002"},
        ),
        Evidence(
            source_type="company_facts",
            content="Revenue: 100 USD",
            provenance={"ticker": "AAPL"},
        ),
    ]

    builder = PromptBuilder()

    context = builder.build(
        question="Test question",
        evidence=evidence,
    )

    assert "[E1]" in context.user_prompt
    assert "[E2]" in context.user_prompt
    assert "[E3]" in context.user_prompt

    assert context.user_prompt.count("[E1]") == 1
    assert context.user_prompt.count("[E2]") == 1
    assert context.user_prompt.count("[E3]") == 1


def run_tests():
    tests = [
        test_numeric_prompt,
        test_narrative_prompt,
        test_hybrid_prompt,
        test_empty_evidence,
        test_multiple_evidence_ids_are_unique,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print(
        f"PASS: {passed}/{len(tests)} prompt builder cases passed."
    )


if __name__ == "__main__":
    run_tests()