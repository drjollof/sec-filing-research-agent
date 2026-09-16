from src.agent.claim_extractor import ClaimExtractor


def test_numeric_claim():
    extractor = ClaimExtractor()

    claims = extractor.extract(
        "Apple's revenue was $416.161 billion in fiscal 2025. [E1]"
    )

    assert len(claims) == 1
    assert claims[0].claim_type == "numeric"
    assert claims[0].evidence_ids == ["E1"]


def test_narrative_claim():
    extractor = ClaimExtractor()

    claims = extractor.extract(
        "Apple's Services business grew during fiscal 2025. [E2]"
    )

    assert len(claims) == 1
    assert claims[0].claim_type == "narrative"
    assert claims[0].evidence_ids == ["E2"]


def test_multiple_claims():
    extractor = ClaimExtractor()

    claims = extractor.extract(
        "Apple's revenue was $416.161 billion. [E1] "
        "Services sales increased during the year. [E2]"
    )

    assert len(claims) == 2
    assert claims[0].claim_type == "numeric"
    assert claims[0].evidence_ids == ["E1"]
    assert claims[1].claim_type == "narrative"
    assert claims[1].evidence_ids == ["E2"]


def test_all_citation_formats():
    extractor = ClaimExtractor()

    claims = extractor.extract(
        "Revenue was $416.161 billion. [E1] "
        "Revenue covered fiscal 2025. 【E2】 "
        "Revenue came from Apple. (E3)"
    )

    assert len(claims) == 3
    assert claims[0].evidence_ids == ["E1"]
    assert claims[1].evidence_ids == ["E2"]
    assert claims[2].evidence_ids == ["E3"]


def test_numeric_year_is_not_numeric_claim():
    extractor = ClaimExtractor()

    claims = extractor.extract(
        "Apple's revenue in fiscal 2025 was reported in the filing. [E1]"
    )

    assert len(claims) == 1
    assert claims[0].claim_type == "narrative"


def test_uncited_claim():
    extractor = ClaimExtractor()

    claims = extractor.extract(
        "Apple's Services business grew during fiscal 2025."
    )

    assert len(claims) == 1
    assert claims[0].claim_type == "narrative"
    assert claims[0].evidence_ids == []


def test_introductory_text():
    extractor = ClaimExtractor()

    claims = extractor.extract(
        "Based on the provided evidence, Apple's revenue was $416.161 billion. [E1]"
    )

    assert len(claims) == 1
    assert claims[0].claim_type == "numeric"
    assert claims[0].evidence_ids == ["E1"]


def test_empty_answer():
    extractor = ClaimExtractor()

    assert extractor.extract("") == []
    assert extractor.extract("   ") == []


def run_tests():
    tests = [
        test_numeric_claim,
        test_narrative_claim,
        test_multiple_claims,
        test_all_citation_formats,
        test_numeric_year_is_not_numeric_claim,
        test_uncited_claim,
        test_introductory_text,
        test_empty_answer,
    ]

    for test in tests:
        test()

    print(f"PASS: {len(tests)}/{len(tests)} claim extractor cases passed.")


if __name__ == "__main__":
    run_tests()