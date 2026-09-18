from dataclasses import dataclass

from src.agent.router import QuestionRouter, Route


@dataclass
class RoutingEvaluationResult:
    question_id: str
    expected_route: str
    observed_route: str
    correct: bool


class RoutingEvaluator:
    """Evaluate question routing against manually defined labels."""

    def __init__(
        self,
        router: QuestionRouter | None = None,
    ):
        self.router = router or QuestionRouter()

    def evaluate(
        self,
        question_id: str,
        question: str,
        expected_route: str,
    ) -> RoutingEvaluationResult:

        result = self.router.route(question)

        observed_route = result.route.value

        return RoutingEvaluationResult(
            question_id=question_id,
            expected_route=expected_route,
            observed_route=observed_route,
            correct=(
                observed_route == expected_route
            ),
        )