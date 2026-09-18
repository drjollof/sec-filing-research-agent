from dataclasses import dataclass

from src.retrieval.retriever import RetrievedChunk


@dataclass
class RetrievalEvaluationResult:
    question_id: str
    hit_at_1: bool
    hit_at_3: bool
    hit_at_5: bool
    retrieved_sections: list[str]
    expected_sections: list[str]


class RetrievalEvaluator:
    """Evaluate whether retrieval returns relevant filing sections."""

    def evaluate(
        self,
        question_id: str,
        retrieved_chunks: list[RetrievedChunk],
        expected_sections: list[str],
    ) -> RetrievalEvaluationResult:

        retrieved_sections = []

        for chunk in retrieved_chunks:
            item_number = chunk.metadata.get("item_number")

            if item_number:
                section = f"Item {item_number}"

                if section not in retrieved_sections:
                    retrieved_sections.append(section)

        def is_hit(top_k: int) -> bool:
            top_sections = retrieved_sections[:top_k]

            return any(
                section in expected_sections
                for section in top_sections
            )

        return RetrievalEvaluationResult(
            question_id=question_id,
            hit_at_1=is_hit(1),
            hit_at_3=is_hit(3),
            hit_at_5=is_hit(5),
            retrieved_sections=retrieved_sections,
            expected_sections=expected_sections,
        )