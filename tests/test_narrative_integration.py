from src.agent.evidence import EvidenceNormalizer
from src.agent.generator import OpenRouterGenerator
from src.agent.prompt_builder import PromptBuilder
from src.agent.verifier import EvidenceVerifier
from src.config import OPENROUTER_MODEL
from src.retrieval.retriever import Retriever


def run_tests():
    retriever = Retriever()

    question = (
        "What risks does Apple identify related to "
        "its business and operations?"
    )

    retrieved_chunks = retriever.retrieve(question)

    assert retrieved_chunks, (
        "Retriever returned no evidence for the narrative question."
    )

    normalizer = EvidenceNormalizer()

    evidence = [
        normalizer.from_retrieved_chunk(chunk)
        for chunk in retrieved_chunks
    ]

    prompt = PromptBuilder().build(
        question,
        evidence,
    )

    generator = OpenRouterGenerator(
        OPENROUTER_MODEL
    )

    generation = generator.generate(prompt)

    assert generation.answer.strip(), (
        "Generator returned an empty answer."
    )

    verifier = EvidenceVerifier()

    result = verifier.verify(
        generation.answer,
        evidence,
    )

    print("MODEL:", generation.model)

    print()
    print("RETRIEVED EVIDENCE:", len(evidence))

    print()
    print("ANSWER:")
    print(generation.answer)

    print()
    print("VERDICT:", result.verdict)

    print()
    print("CITED EVIDENCE:", result.cited_evidence_ids)

    if result.issues:
        print()
        print("ISSUES:")

        for issue in result.issues:
            print(
                f"- {issue.issue_type}: "
                f"{issue.message}"
            )

    print()
    print("PASS: narrative end-to-end pipeline executed successfully.")


if __name__ == "__main__":
    run_tests()