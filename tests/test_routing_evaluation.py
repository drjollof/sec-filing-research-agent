import json
from pathlib import Path

from src.evaluation.routing_evaluator import RoutingEvaluator


QUESTIONS_PATH = Path("evaluation/questions.json")


def run_tests():

    with QUESTIONS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        questions = json.load(file)

    evaluator = RoutingEvaluator()

    results = []

    for question in questions:

        result = evaluator.evaluate(
            question_id=question["id"],
            question=question["question"],
            expected_route=question["expected_route"],
        )

        results.append(result)

    total = len(results)

    correct = sum(
        result.correct
        for result in results
    )

    accuracy = (
        correct / total
        if total
        else 0.0
    )

    print()
    print("ROUTING EVALUATION")
    print("==================")
    print(f"Questions evaluated: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2%}")

    print()
    print("QUESTION RESULTS")
    print("================")

    for result in results:

        status = (
            "PASS"
            if result.correct
            else "MISS"
        )

        print()
        print(
            f"{result.question_id} [{status}]"
        )
        print(
            f"Expected: {result.expected_route}"
        )
        print(
            f"Observed: {result.observed_route}"
        )

    print()
    print(
        "PASS: routing evaluation completed."
    )


if __name__ == "__main__":
    run_tests()