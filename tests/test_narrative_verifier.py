from src.agent.claim_extractor import Claim
from src.agent.evidence import Evidence
from src.agent.narrative_verifier import NarrativeVerifier


def make_claim(
    text: str,
    evidence_ids: list[str],
) -> Claim:
    return Claim(
        text=text,
        claim_type="narrative",
        evidence_ids=evidence_ids,
    )


def make_evidence(
    content: str,
) -> Evidence:
    return Evidence(
        source_type="retrieved_chunk",
        content=content,
        provenance={},
    )


def test_direct_support():
    verifier = NarrativeVerifier()

    claim = make_claim(
        "Services net sales increased during fiscal 2025.",
        ["E1"],
    )

    evidence = [
        make_evidence(
            "Services net sales increased during fiscal 2025."
        )
    ]

    result = verifier.verify(claim, evidence)

    assert result.verdict == "supported"


def test_direct_paraphrase_is_uncertain():
    verifier = NarrativeVerifier()

    claim = make_claim(
        "Apple experienced top-line growth.",
        ["E1"],
    )

    evidence = [
        make_evidence(
            "Total net sales increased during fiscal 2025."
        )
    ]

    result = verifier.verify(claim, evidence)

    assert result.verdict == "uncertain"


def test_contradictory_direction_is_not_supported():
    verifier = NarrativeVerifier()

    claim = make_claim(
        "Apple's revenue increased during fiscal 2025.",
        ["E1"],
    )

    evidence = [
        make_evidence(
            "Apple's revenue decreased during fiscal 2025."
        )
    ]

    result = verifier.verify(claim, evidence)

    assert result.verdict == "uncertain"


def test_unsupported_claim():
    verifier = NarrativeVerifier()

    claim = make_claim(
        "Apple's revenue increased because of stronger cloud demand.",
        ["E1"],
    )

    evidence = [
        make_evidence(
            "Apple reported higher Services net sales during fiscal 2025."
        )
    ]

    result = verifier.verify(claim, evidence)

    assert result.verdict == "uncertain"


def test_missing_citation():
    verifier = NarrativeVerifier()

    claim = make_claim(
        "Apple's Services business grew during fiscal 2025.",
        [],
    )

    evidence = [
        make_evidence(
            "Apple's Services business grew during fiscal 2025."
        )
    ]

    result = verifier.verify(claim, evidence)

    assert result.verdict == "unsupported"


def test_invalid_citation():
    verifier = NarrativeVerifier()

    claim = make_claim(
        "Apple's Services business grew during fiscal 2025.",
        ["E99"],
    )

    evidence = [
        make_evidence(
            "Apple's Services business grew during fiscal 2025."
        )
    ]

    result = verifier.verify(claim, evidence)

    assert result.verdict == "unsupported"


def test_multiple_evidence_items():
    verifier = NarrativeVerifier()

    claim = make_claim(
        "Services net sales increased during fiscal 2025.",
        ["E1", "E2"],
    )

    evidence = [
        make_evidence(
            "Apple reported information about its products."
        ),
        make_evidence(
            "Services net sales increased during fiscal 2025."
        ),
    ]

    result = verifier.verify(claim, evidence)

    assert result.verdict == "supported"


def test_numeric_claim_is_not_verified_here():
    verifier = NarrativeVerifier()

    claim = Claim(
        text="Apple's revenue was $416.161 billion.",
        claim_type="numeric",
        evidence_ids=["E1"],
    )

    evidence = [
        make_evidence(
            "Apple's revenue was $416.161 billion."
        )
    ]

    result = verifier.verify(claim, evidence)

    assert result.verdict == "uncertain"


def run_tests():
    tests = [
        test_direct_support,
        test_direct_paraphrase_is_uncertain,
        test_contradictory_direction_is_not_supported,
        test_unsupported_claim,
        test_missing_citation,
        test_invalid_citation,
        test_multiple_evidence_items,
        test_numeric_claim_is_not_verified_here,
    ]

    for test in tests:
        test()

    print(
        f"PASS: {len(tests)}/{len(tests)} "
        "narrative verifier cases passed."
    )


if __name__ == "__main__":
    run_tests()