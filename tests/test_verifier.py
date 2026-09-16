from src.agent.evidence import Evidence
from src.agent.verifier import EvidenceVerifier


def make_numeric_evidence(
    value: int,
) -> Evidence:

    return Evidence(
        source_type="company_facts",
        content=f"Revenue: {value:,} USD",
        provenance={
            "value": value,
            "unit": "USD",
            "ticker": "AAPL",
            "fiscal_year": 2025,
        },
    )


def test_valid_evidence_id():

    verifier = EvidenceVerifier()

    evidence = [
        make_numeric_evidence(
            416_161_000_000
        )
    ]

    result = verifier.verify(
        "Apple's revenue was $416.161 billion. [E1]",
        evidence,
    )

    assert result.verdict == "supported"
    assert result.cited_evidence_ids == ["E1"]
    assert result.issues == []


def test_invalid_evidence_id():

    verifier = EvidenceVerifier()

    evidence = [
        make_numeric_evidence(
            416_161_000_000
        )
    ]

    result = verifier.verify(
        "Apple's revenue was $416.161 billion. [E2]",
        evidence,
    )

    assert result.verdict == "unsupported"
    assert any(
        issue.issue_type == "invalid_evidence_id"
        for issue in result.issues
    )


def test_correct_numeric_value_with_rounding():

    verifier = EvidenceVerifier()

    evidence = [
        make_numeric_evidence(
            416_161_000_000
        )
    ]

    result = verifier.verify(
        "Apple's revenue was $416.16 billion. [E1]",
        evidence,
    )

    assert result.verdict == "supported"


def test_hallucinated_numeric_claim():

    verifier = EvidenceVerifier()

    evidence = [
        make_numeric_evidence(
            416_161_000_000
        )
    ]

    result = verifier.verify(
        (
            "Apple's revenue was $416.161 billion, "
            "a 15% increase from the previous year. [E1]"
        ),
        evidence,
    )

    assert result.verdict == "partially_supported"

    assert any(
        issue.issue_type == "unsupported_numeric_claim"
        for issue in result.issues
    )


def test_uncited_numeric_claim():

    verifier = EvidenceVerifier()

    evidence = [
        make_numeric_evidence(
            416_161_000_000
        )
    ]

    result = verifier.verify(
        "Apple's revenue was $416.161 billion.",
        evidence,
    )

    assert result.verdict == "partially_supported"


def test_unicode_evidence_id():
        verifier = EvidenceVerifier()

        evidence = [
            make_numeric_evidence(
                416_161_000_000
            )
        ]

        result = verifier.verify(
            "Apple's revenue was $416.161 billion. 【E1】",
            evidence,
        )

        assert result.verdict == "supported"
        assert result.cited_evidence_ids == ["E1"]
        assert result.issues == []


def test_fiscal_year_is_not_numeric_claim():
        verifier = EvidenceVerifier()

        evidence = [
            make_numeric_evidence(
                416_161_000_000
            )
        ]

        result = verifier.verify(
            "Apple's revenue in 2025 was $416.161 billion. [E1]",
            evidence,
        )

        assert result.verdict == "supported"
        assert result.issues == []

def test_supported_narrative_claim():
    verifier = EvidenceVerifier()

    evidence = [
        Evidence(
            source_type="retrieved_chunk",
            content=(
                "Services net sales increased during "
                "fiscal 2025."
            ),
            provenance={},
        )
    ]

    result = verifier.verify(
        "Services net sales increased during fiscal 2025. [E1]",
        evidence,
    )

    assert result.verdict == "supported"
    assert result.issues == []


def test_unsupported_narrative_claim():
    verifier = EvidenceVerifier()

    evidence = [
        Evidence(
            source_type="retrieved_chunk",
            content=(
                "Services net sales increased during "
                "fiscal 2025."
            ),
            provenance={},
        )
    ]

    result = verifier.verify(
        "Services growth was caused by stronger cloud demand. [E1]",
        evidence,
    )

    assert result.verdict == "partially_supported"
    assert any(
        issue.issue_type == "uncertain_narrative_claim"
        for issue in result.issues
    )


def test_mixed_numeric_and_narrative_claims():
    verifier = EvidenceVerifier()

    evidence = [
        Evidence(
            source_type="company_facts",
            content=(
                "Revenue from Contract with Customer, "
                "Excluding Assessed Tax: "
                "416,161,000,000 USD"
            ),
            provenance={
                "value": 416_161_000_000,
            },
        ),
        Evidence(
            source_type="retrieved_chunk",
            content=(
                "Services net sales increased during "
                "fiscal 2025."
            ),
            provenance={},
        ),
    ]

    result = verifier.verify(
        "Apple's revenue was $416.161 billion. [E1] "
        "Services net sales increased during fiscal 2025. [E2]",
        evidence,
    )

    assert result.verdict == "supported"
    assert result.issues == []

def test_parentheses_evidence_id():
    verifier = EvidenceVerifier()
    evidence = [make_numeric_evidence(416_161_000_000)]

    result = verifier.verify(
        "Apple's revenue was $416.161 billion. (E1)",
        evidence,
    )

    assert result.verdict == "supported"
    assert result.cited_evidence_ids == ["E1"]
    assert result.issues == []


def run_tests():
    tests = [
        test_valid_evidence_id,
        test_invalid_evidence_id,
        test_correct_numeric_value_with_rounding,
        test_hallucinated_numeric_claim,
        test_uncited_numeric_claim,
        test_unicode_evidence_id,
        test_fiscal_year_is_not_numeric_claim,
        test_parentheses_evidence_id,
        test_supported_narrative_claim,
        test_unsupported_narrative_claim,
        test_mixed_numeric_and_narrative_claims,
    ]

    passed = 0

    for test in tests:
        test()
        passed += 1

    print(f"PASS: {passed}/{len(tests)} verifier cases passed.")


if __name__ == "__main__":
    run_tests()