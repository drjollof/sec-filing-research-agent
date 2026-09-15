from src.agent.evidence import EvidenceNormalizer
from src.tools.company_facts import NumericFact
from src.retrieval.retriever import RetrievedChunk


normalizer = EvidenceNormalizer()


def test_numeric_fact_normalization():
    fact = NumericFact(
        company="Apple Inc.",
        ticker="AAPL",
        fact_name="RevenueFromContractWithCustomerExcludingAssessedTax",
        label="Revenue",
        value=416161000000,
        unit="USD",
        fiscal_year=2025,
        fiscal_period="FY",
        form="10-K",
        filing_date="2025-10-31",
        accession_number="0000320193-25-000079",
        period_start="2024-09-29",
        period_end="2025-09-27",
    )

    evidence = normalizer.from_numeric_fact(fact)

    assert evidence.source_type == "company_facts"

    assert evidence.content == (
        "Revenue: 416,161,000,000 USD"
    )

    assert evidence.provenance["ticker"] == "AAPL"
    assert evidence.provenance["fiscal_year"] == 2025
    assert (
        evidence.provenance["concept"]
        == "RevenueFromContractWithCustomerExcludingAssessedTax"
    )
    assert (
        evidence.provenance["accession_number"]
        == "0000320193-25-000079"
    )


def test_retrieved_chunk_normalization():
    chunk = RetrievedChunk(
        chunk_id="AAPL_0000320193-25-000079_item7_chunk001",
        text="Apple's Services business grew during 2025.",
        distance=0.18,
        metadata={
            "ticker": "AAPL",
            "company": "Apple Inc.",
            "form": "10-K",
            "fiscal_year": 2025,
            "section": "Item 7",
        },
    )

    evidence = normalizer.from_retrieved_chunk(chunk)

    assert evidence.source_type == "filing_chunk"

    assert (
        evidence.content
        == "Apple's Services business grew during 2025."
    )

    assert (
        evidence.provenance["chunk_id"]
        == "AAPL_0000320193-25-000079_item7_chunk001"
    )

    assert evidence.provenance["ticker"] == "AAPL"
    assert evidence.provenance["section"] == "Item 7"


def run_tests():
    tests = [
        test_numeric_fact_normalization,
        test_retrieved_chunk_normalization,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print(
        f"PASS: {passed}/{len(tests)} evidence cases passed."
    )


if __name__ == "__main__":
    run_tests()