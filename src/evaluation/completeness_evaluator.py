from dataclasses import dataclass


@dataclass
class CompletenessEvaluationResult:
    question_id: str
    complete: bool
    reason: str


class AnswerCompletenessEvaluator:
    """
    Lightweight task-alignment checks for generated answers.

    This evaluator does not determine factual truth.
    Evidence verification remains the responsibility of EvidenceVerifier.
    """

    def evaluate(
        self,
        question_id: str,
        question: str,
        answer: str,
        expected_route: str,
        expected_metric: str | None = None,
    ) -> CompletenessEvaluationResult:

        answer = answer.strip()

        if not answer:
            return CompletenessEvaluationResult(
                question_id=question_id,
                complete=False,
                reason="Generated answer is empty.",
            )

        # Unsupported questions should not be expected to contain
        # a substantive financial answer.
        if expected_route == "numeric" and expected_metric:
            metric_aliases = {
                "revenue": (
                    "revenue",
                    "revenues",
                    "net sales",
                    "sales",
                ),
                "total_assets": (
                    "assets",
                    "total assets",
                ),
                "cash": (
                    "cash",
                    "cash and cash equivalents",
                    "cash and due from banks",
                ),
                "net_income": (
                    "net income",
                    "net earnings",
                ),
            }

            aliases = metric_aliases.get(expected_metric, (expected_metric,))

            if not any(alias in answer.lower() for alias in aliases):
                return CompletenessEvaluationResult(
                    question_id=question_id,
                    complete=False,
                    reason=(
                        f"Answer does not appear to address the requested "
                        f"metric '{expected_metric}'."
                    ),
                )

        # Numeric questions should contain a number.
        if expected_route == "numeric":
            if not any(char.isdigit() for char in answer):
                return CompletenessEvaluationResult(
                    question_id=question_id,
                    complete=False,
                    reason="Numeric question received an answer without a numeric value.",
                )

        # Hybrid questions must contain both the requested metric and
        # some explanatory content.
        if expected_route == "hybrid":
            if expected_metric:
                metric_aliases = {
                    "revenue": (
                        "revenue",
                        "revenues",
                        "net sales",
                        "sales",
                    ),
                    "total_assets": (
                        "assets",
                        "total assets",
                    ),
                    "cash": (
                        "cash",
                        "cash and cash equivalents",
                        "cash and due from banks",
                    ),
                    "net_income": (
                        "net income",
                        "net earnings",
                    ),
                }

                aliases = metric_aliases.get(
                    expected_metric,
                    (expected_metric,),
                )

                if not any(alias in answer.lower() for alias in aliases):
                    return CompletenessEvaluationResult(
                        question_id=question_id,
                        complete=False,
                        reason=(
                            f"Hybrid answer does not address the requested "
                            f"metric '{expected_metric}'."
                        ),
                    )

            if not any(char.isdigit() for char in answer):
                return CompletenessEvaluationResult(
                    question_id=question_id,
                    complete=False,
                    reason="Hybrid question received no numeric answer.",
                )

            explanatory_terms = (
                "because",
                "driven",
                "due to",
                "primarily",
                "increased",
                "decreased",
                "higher",
                "lower",
                "offset",
                "factor",
                "reason",
            )

            if not any(
                term in answer.lower()
                for term in explanatory_terms
            ):
                return CompletenessEvaluationResult(
                    question_id=question_id,
                    complete=False,
                    reason=(
                        "Hybrid answer provides the metric but does not "
                        "appear to provide an explanation."
                    ),
                )

        # Narrative questions need substantive text and should not merely
        # return a short non-answer such as "User Safety: safe".
        if expected_route == "narrative":
            if len(answer.split()) < 5:
                return CompletenessEvaluationResult(
                    question_id=question_id,
                    complete=False,
                    reason="Narrative answer is too short to answer the question.",
                )

        return CompletenessEvaluationResult(
            question_id=question_id,
            complete=True,
            reason="Answer appears responsive to the requested task.",
        )