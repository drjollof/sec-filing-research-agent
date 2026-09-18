from src.evaluation.retrieval_evaluator import RetrievalEvaluator
from src.retrieval.retriever import RetrievedChunk


def run_tests():

    evaluator = RetrievalEvaluator()

    chunks = [
        RetrievedChunk(
            chunk_id="chunk-1",
            text="Financial statements.",
            distance=0.10,
            metadata={
                "item_number": "8",
            },
        ),
        RetrievedChunk(
            chunk_id="chunk-2",
            text="Business discussion.",
            distance=0.20,
            metadata={
                "item_number": "7",
            },
        ),
        RetrievedChunk(
            chunk_id="chunk-3",
            text="Risk factors.",
            distance=0.30,
            metadata={
                "item_number": "1A",
            },
        ),
    ]

    result = evaluator.evaluate(
        question_id="Q01",
        retrieved_chunks=chunks,
        expected_sections=["Item 8"],
    )

    assert result.hit_at_1 is True
    assert result.hit_at_3 is True
    assert result.hit_at_5 is True

    result = evaluator.evaluate(
        question_id="Q02",
        retrieved_chunks=chunks,
        expected_sections=["Item 7"],
    )

    assert result.hit_at_1 is False
    assert result.hit_at_3 is True
    assert result.hit_at_5 is True

    result = evaluator.evaluate(
        question_id="Q03",
        retrieved_chunks=chunks,
        expected_sections=["Item 1A"],
    )

    assert result.hit_at_1 is False
    assert result.hit_at_3 is True
    assert result.hit_at_5 is True

    result = evaluator.evaluate(
        question_id="Q04",
        retrieved_chunks=[],
        expected_sections=["Item 1A"],
    )

    assert result.hit_at_1 is False
    assert result.hit_at_3 is False
    assert result.hit_at_5 is False

    print("PASS: 4/4 retrieval evaluator cases passed.")


if __name__ == "__main__":
    run_tests()