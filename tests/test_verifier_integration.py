from src.agent.evidence import EvidenceNormalizer
from src.agent.generator import OpenRouterGenerator
from src.agent.prompt_builder import PromptBuilder
from src.agent.verifier import EvidenceVerifier
from src.config import OPENROUTER_MODEL
from src.tools.company_facts import CompanyFactsTool


def run_tests():
    company_facts = CompanyFactsTool()

    fact = company_facts.get_metric(
        ticker="AAPL",
        metric="revenue",
        fiscal_year=2025,
    )

    assert fact is not None, (
        "CompanyFacts returned no AAPL FY2025 revenue."
    )

    evidence = EvidenceNormalizer().from_numeric_fact(
        fact
    )

    question = "What was Apple's revenue in 2025?"

    prompt = PromptBuilder().build(
        question,
        [evidence],
    )

    generator = OpenRouterGenerator(
        OPENROUTER_MODEL
    )

    generation = generator.generate(prompt)

    assert generation.answer.strip(), (
        "Generator returned an empty answer."
    )

    verifier = EvidenceVerifier()

    # Test 1: verify the actual LLM response.
    actual_result = verifier.verify(
        generation.answer,
        [evidence],
    )

    print("ACTUAL MODEL:", generation.model)
    print("ACTUAL ANSWER:")
    print(generation.answer)
    print()
    print(
        "ACTUAL VERDICT:",
        actual_result.verdict,
    )

    assert actual_result.verdict == "supported", (
        "The actual generated answer was not fully "
        "supported by the supplied SEC evidence."
    )

    # Test 2: deliberately inject a hallucinated claim.
    hallucinated_answer = (
        f"Apple's revenue was "
        f"${fact.value / 1_000_000_000:.3f} billion, "
        "a 15% increase from the previous year. [E1]"
    )

    hallucinated_result = verifier.verify(
        hallucinated_answer,
        [evidence],
    )

    assert (
        hallucinated_result.verdict
        == "partially_supported"
    ), (
        "Verifier failed to detect the deliberately "
        "unsupported numeric claim."
    )

    assert any(
        issue.issue_type
        == "unsupported_numeric_claim"
        for issue in hallucinated_result.issues
    )

    # Test 3: deliberately use a fake evidence citation.
    fake_citation_answer = (
        f"Apple's revenue was "
        f"${fact.value / 1_000_000_000:.3f} billion. [E99]"
    )

    fake_citation_result = verifier.verify(
        fake_citation_answer,
        [evidence],
    )

    assert fake_citation_result.verdict == "unsupported", (
        "Verifier failed to reject the nonexistent "
        "evidence citation."
    )

    assert any(
        issue.issue_type == "invalid_evidence_id"
        for issue in fake_citation_result.issues
    )

    print()
    print("PASS: 3/3 verifier integration cases passed.")


if __name__ == "__main__":
    run_tests()