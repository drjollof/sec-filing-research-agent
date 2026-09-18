from src.evaluation.completeness_evaluator import (
    AnswerCompletenessEvaluator,
)


def run_tests():
    evaluator = AnswerCompletenessEvaluator()

    tests = [
        {
            "question_id": "T01",
            "question": "What was Apple's revenue in 2025?",
            "answer": "Apple's revenue was $416.161 billion [E1].",
            "expected_route": "numeric",
            "expected_metric": "revenue",
            "expected": True,
        },
        {
            "question_id": "T02",
            "question": "What was Apple's total assets at the end of 2025?",
            "answer": "Apple reported total assets of $359.241 billion [E1].",
            "expected_route": "numeric",
            "expected_metric": "total_assets",
            "expected": True,
        },
        {
            "question_id": "T03",
            "question": "What was Apple's revenue in 2025?",
            "answer": "The evidence discusses Apple's filing.",
            "expected_route": "numeric",
            "expected_metric": "revenue",
            "expected": False,
        },
        {
            "question_id": "T04",
            "question": "Why did Apple's revenue change?",
            "answer": "User Safety: safe",
            "expected_route": "narrative",
            "expected_metric": None,
            "expected": False,
        },
        {
            "question_id": "T05",
            "question": "Why did Apple's revenue change?",
            "answer": (
                "Revenue increased because iPhone and Services sales "
                "were higher [E1]."
            ),
            "expected_route": "narrative",
            "expected_metric": None,
            "expected": True,
        },
        {
            "question_id": "T06",
            "question": "What was Apple's revenue in 2025 and why did it change?",
            "answer": "Revenue was $416.161 billion because iPhone and Services sales increased [E1].",
            "expected_route": "hybrid",
            "expected_metric": "revenue",
            "expected": True,
        },
        {
            "question_id": "T07",
            "question": "What was Apple's revenue in 2025 and why did it change?",
            "answer": "Apple's revenue was $416.161 billion [E1].",
            "expected_route": "hybrid",
            "expected_metric": "revenue",
            "expected": False,
        },
    ]

    passed = 0

    for test in tests:
        result = evaluator.evaluate(
            question_id=test["question_id"],
            question=test["question"],
            answer=test["answer"],
            expected_route=test["expected_route"],
            expected_metric=test["expected_metric"],
        )

        if result.complete == test["expected"]:
            passed += 1
        else:
            print(
                f'FAIL: {test["question_id"]} '
                f'expected={test["expected"]} '
                f'observed={result.complete}'
            )
            print(f"Reason: {result.reason}")

    print(f"PASS: {passed}/{len(tests)} completeness cases passed.")

    assert passed == len(tests)


if __name__ == "__main__":
    run_tests()