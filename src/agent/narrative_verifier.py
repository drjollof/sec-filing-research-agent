import re
from dataclasses import dataclass

from src.agent.claim_extractor import Claim
from src.agent.evidence import Evidence


@dataclass
class NarrativeVerificationResult:
    verdict: str
    message: str


class NarrativeVerifier:
    STOPWORDS = {
        "a", "an", "and", "are", "as", "at", "be", "been", "being",
        "by", "for", "from", "had", "has", "have", "in", "into", "is",
        "it", "its", "of", "on", "or", "that", "the", "their", "this",
        "to", "was", "were", "will", "with", "during", "according",
        "based", "provided", "evidence",
    }

    NEGATION_WORDS = {
        "not", "no", "never", "neither", "nor", "without",
        "declined", "decreased", "decrease", "fell", "fall",
        "lower", "lowered", "reduced", "reduction",
    }

    POSITIVE_DIRECTION_WORDS = {
        "increased", "increase", "grew", "growth", "higher",
        "rose", "rising", "improved", "improvement",
    }

    NEGATIVE_DIRECTION_WORDS = {
        "decreased", "decrease", "declined", "decline", "fell",
        "fall", "lower", "lowered", "reduced", "reduction",
    }

    def verify(
        self,
        claim: Claim,
        evidence: list[Evidence],
    ) -> NarrativeVerificationResult:

        if claim.claim_type != "narrative":
            return NarrativeVerificationResult(
                verdict="uncertain",
                message="Claim is not classified as narrative.",
            )

        cited_evidence = [
            evidence_id
            for evidence_id in claim.evidence_ids
        ]

        if not cited_evidence:
            return NarrativeVerificationResult(
                verdict="unsupported",
                message="Narrative claim has no cited evidence.",
            )

        evidence_map = {
            f"E{index}": item
            for index, item in enumerate(evidence, start=1)
        }

        valid_evidence = [
            evidence_map[evidence_id]
            for evidence_id in cited_evidence
            if evidence_id in evidence_map
        ]

        if not valid_evidence:
            return NarrativeVerificationResult(
                verdict="unsupported",
                message="Narrative claim cites no valid evidence.",
            )

        claim_tokens = self._content_tokens(claim.text)

        if not claim_tokens:
            return NarrativeVerificationResult(
                verdict="uncertain",
                message="Narrative claim contains no substantive terms.",
            )

        for item in valid_evidence:
            evidence_tokens = self._content_tokens(item.content)

            if self._has_directional_contradiction(
                claim.text,
                item.content,
            ):
                continue

            overlap = claim_tokens.intersection(evidence_tokens)

            if self._is_directly_supported(
                claim_tokens,
                overlap,
            ):
                return NarrativeVerificationResult(
                    verdict="supported",
                    message=(
                        "The cited evidence contains sufficient "
                        "direct lexical support for the narrative claim."
                    ),
                )

        return NarrativeVerificationResult(
            verdict="uncertain",
            message=(
                "The cited evidence does not provide sufficient "
                "direct lexical support to verify the narrative claim."
            ),
        )

    def _is_directly_supported(
        self,
        claim_tokens: set[str],
        overlap: set[str],
    ) -> bool:

        if not claim_tokens:
            return False

        overlap_ratio = len(overlap) / len(claim_tokens)

        return (
            len(overlap) >= 2
            and overlap_ratio >= 0.50
        )

    def _has_directional_contradiction(
        self,
        claim_text: str,
        evidence_text: str,
    ) -> bool:

        claim_positive = bool(
            self.POSITIVE_DIRECTION_WORDS
            & self._content_tokens(claim_text)
        )

        claim_negative = bool(
            self.NEGATIVE_DIRECTION_WORDS
            & self._content_tokens(claim_text)
        )

        evidence_positive = bool(
            self.POSITIVE_DIRECTION_WORDS
            & self._content_tokens(evidence_text)
        )

        evidence_negative = bool(
            self.NEGATIVE_DIRECTION_WORDS
            & self._content_tokens(evidence_text)
        )

        return (
            (claim_positive and evidence_negative)
            or
            (claim_negative and evidence_positive)
        )

    def _content_tokens(self, text: str) -> set[str]:
        tokens = re.findall(
            r"[a-zA-Z]+",
            text.lower(),
        )

        return {
            token
            for token in tokens
            if token not in self.STOPWORDS
            and len(token) > 2
        }