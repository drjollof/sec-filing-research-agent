from dataclasses import dataclass
from enum import Enum


class Route(str, Enum):
    NUMERIC = "numeric"
    NARRATIVE = "narrative"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


@dataclass
class RouterResult:
    route: Route
    reason: str


class QuestionRouter:
    """
    Deterministic router for SEC filing questions.

    The router classifies questions by the type of evidence
    required to answer them, not merely by the presence of
    financial keywords.
    """

    NUMERIC_PATTERNS = (
        "what was",
        "what were",
        "how much",
        "how many",
        "give me",
        "tell me",
    )

    NARRATIVE_PATTERNS = (
        "why",
        "how did",
        "how does",
        "what factors",
        "what risks",
        "what did",
        'what caused',
        "what ... does",
        "describe",
        "explain",
        "discuss",
        )

    def route(self, question: str) -> RouterResult:
        question = question.strip().lower()

        if not question:
            return RouterResult(
                route=Route.UNKNOWN,
                reason="Question is empty.",
            )

        # Hybrid: quantitative fact + explanation/context
        has_numeric_intent = any(
            question.startswith(pattern)
            or f" {pattern} " in question
            for pattern in self.NUMERIC_PATTERNS
        )

        has_narrative_intent = any(
            question.startswith(pattern)
            or f" {pattern} " in question
            for pattern in self.NARRATIVE_PATTERNS
        )

        if has_numeric_intent and has_narrative_intent:
            return RouterResult(
                route=Route.HYBRID,
                reason=(
                    "Question requires both a structured financial fact and narrative explanation or context."
                    ),
            )

        if question.startswith("what ") and " does " in question:
            return RouterResult(
                route=Route.NARRATIVE,
                reason=(
                    "Question requests descriptive or qualitative information from the filing."
                ),
            )

        if has_narrative_intent:
            return RouterResult(
                route=Route.NARRATIVE,
                reason=(
                    "Question requests explanation, context, or qualitative filing information."
                ),
            )

        if has_numeric_intent:
            return RouterResult(
                route=Route.NUMERIC,
                reason=(
                    "Question requests a specific financial value or quantitative fact."
                ),
            )

        return RouterResult(
            route=Route.UNKNOWN,
            reason="Question does not match a supported routing pattern.",
        )