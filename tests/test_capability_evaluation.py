import json
from pathlib import Path

from src.agent.capability import NumericCapabilityResolver


QUESTIONS_PATH = Path("evaluation/questions.json")


def run_tests():
    with QUESTIONS_PATH.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    resolver = NumericCapabilityResolver()
    results = []

    # The capability resolver is only invoked for numeric or hybrid routes.
    capability_questions = [
        q for q in questions
        if q["expected_route"] in {"numeric", "hybrid"}
    ]

    for question in capability_questions:
        result = resolver.resolve(question["question"])

        # In our JSON, anything explicitly marked "unsupported" should return False
        expected_supported = question["expected_support"] != "unsupported"

        results.append(
            {
                "id": question["id"],
                "question": question["question"],
                "expected_supported": expected_supported,
                "observed_supported": result.supported,
                "expected_metric": question.get("expected_metric"),
                "observed_metric": result.metric,
                "correct": (
                    result.supported == expected_supported and
                    result.metric == question.get("expected_metric")
                ),
            }
        )

    total = len(results)
    correct = sum(result["correct"] for result in results)
    accuracy = correct / total if total else 0.0

    print()
    print("NUMERIC CAPABILITY EVALUATION")
    print("=============================")
    print(f"Questions evaluated: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2%}")

    print()
    print("QUESTION RESULTS")
    print("================")

    for result in results:
        status = "PASS" if result["correct"] else "MISS"

        print()
        print(f'{result["id"]} [{status}]')
        print(f'Question: {result["question"]}')
        print(f'Expected supported: {result["expected_supported"]}')
        print(f'Observed supported: {result["observed_supported"]}')
        print(f'Expected metric: {result["expected_metric"]}')
        print(f'Observed metric: {result["observed_metric"]}')

    print()
    print("PASS: numeric capability evaluation completed.")


if __name__ == "__main__":
    run_tests()