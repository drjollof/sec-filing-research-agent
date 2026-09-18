from src.evaluation.routing_evaluator import RoutingEvaluator


def run_tests():

    evaluator = RoutingEvaluator()

    result = evaluator.evaluate(
        question_id="Q01",
        question="What was Apple's revenue in 2025?",
        expected_route="numeric",
    )

    assert result.correct is True
    assert result.observed_route == "numeric"

    result = evaluator.evaluate(
        question_id="Q02",
        question="Why did Apple's revenue change?",
        expected_route="narrative",
    )

    assert result.correct is True
    assert result.observed_route == "narrative"

    result = evaluator.evaluate(
        question_id="Q03",
        question=(
            "What was Apple's revenue in 2025, "
            "and why did it change?"
        ),
        expected_route="hybrid",
    )

    assert result.correct is True
    assert result.observed_route == "hybrid"

    print("PASS: 3/3 routing evaluator cases passed.")


if __name__ == "__main__":
    run_tests()