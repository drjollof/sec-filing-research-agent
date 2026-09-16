import re
from dataclasses import dataclass, field

from src.agent.claim_extractor import Claim, ClaimExtractor
from src.agent.evidence import Evidence
from src.agent.narrative_verifier import NarrativeVerifier


@dataclass
class VerificationIssue:
    issue_type: str
    message: str
    evidence_id: str | None = None


@dataclass
class VerificationResult:
    verdict: str
    issues: list[VerificationIssue] = field(default_factory=list)
    cited_evidence_ids: list[str] = field(default_factory=list)


class EvidenceVerifier:
    EVIDENCE_ID_PATTERN = re.compile(
        r"(?:\[|【|\()E(\d+)(?:\]|】|\))"
    )

    NUMERIC_CLAIM_PATTERN = re.compile(
        r"""
        (?:
            \$\s*
            (?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)
            \s*
            (?:trillion|billion|million|thousand)?
        )
        |
        (?:
            (?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)
            \s*
            (?:trillion|billion|million|thousand)
        )
        |
        (?:
            \d+(?:\.\d+)?
            \s*%
        )
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    def __init__(self):
        self.claim_extractor = ClaimExtractor()
        self.narrative_verifier = NarrativeVerifier()

    def verify(
        self,
        answer: str,
        evidence: list[Evidence],
    ) -> VerificationResult:

        issues = []

        evidence_map = {
            f"E{index}": item
            for index, item in enumerate(evidence, start=1)
        }

        claims = self.claim_extractor.extract(answer)

        cited_ids = self._collect_cited_ids(claims)

        issues.extend(
            self._validate_evidence_ids(
                cited_ids,
                evidence_map,
            )
        )

        for claim in claims:
            if claim.claim_type == "numeric":
                issues.extend(
                    self._verify_numeric_claim(
                        claim,
                        evidence_map,
                    )
                )

            elif claim.claim_type == "narrative":
                issues.extend(
                    self._verify_narrative_claim(
                        claim,
                        evidence,
                    )
                )

        verdict = self._aggregate_verdict(issues)

        return VerificationResult(
            verdict=verdict,
            issues=issues,
            cited_evidence_ids=cited_ids,
        )

    def _collect_cited_ids(
        self,
        claims: list[Claim],
    ) -> list[str]:

        cited_ids = []

        for claim in claims:
            for evidence_id in claim.evidence_ids:
                if evidence_id not in cited_ids:
                    cited_ids.append(evidence_id)

        return cited_ids

    def _validate_evidence_ids(
        self,
        cited_ids: list[str],
        evidence_map: dict[str, Evidence],
    ) -> list[VerificationIssue]:

        issues = []

        for evidence_id in cited_ids:
            if evidence_id not in evidence_map:
                issues.append(
                    VerificationIssue(
                        issue_type="invalid_evidence_id",
                        message=(
                            f"Answer cites {evidence_id}, "
                            "but that evidence ID does not exist."
                        ),
                        evidence_id=evidence_id,
                    )
                )

        return issues

    def _verify_numeric_claim(
        self,
        claim: Claim,
        evidence_map: dict[str, Evidence],
    ) -> list[VerificationIssue]:

        issues = []

        unsupported_numbers = self._get_unsupported_numbers(
            claim,
            evidence_map,
        )

        for number_text in unsupported_numbers:
            issues.append(
                VerificationIssue(
                    issue_type="unsupported_numeric_claim",
                    message=(
                        f"Numeric claim '{number_text}' could not "
                        "be matched to cited structured evidence."
                    ),
                )
            )

        return issues

    def _verify_narrative_claim(
        self,
        claim: Claim,
        evidence: list[Evidence],
    ) -> list[VerificationIssue]:

        result = self.narrative_verifier.verify(
            claim,
            evidence,
        )

        if result.verdict == "supported":
            return []

        if result.verdict == "unsupported":
            return [
                VerificationIssue(
                    issue_type="unsupported_narrative_claim",
                    message=result.message,
                )
            ]

        return [
            VerificationIssue(
                issue_type="uncertain_narrative_claim",
                message=result.message,
            )
        ]

    def _get_unsupported_numbers(
        self,
        claim: Claim,
        evidence_map: dict[str, Evidence],
    ) -> list[str]:

        unsupported = []

        for match in self.NUMERIC_CLAIM_PATTERN.finditer(
            claim.text
        ):
            number_text = match.group(0).strip()

            # Ignore 4-digit years from being treated as numeric claims
            if re.fullmatch(r"(19|20)\d{2}", number_text):
                continue

            parsed_value = self._parse_number(
                number_text
            )

            if parsed_value is None:
                continue

            matched = False

            for evidence_id in claim.evidence_ids:
                evidence = evidence_map.get(evidence_id)

                if evidence is None:
                    continue

                if evidence.source_type != "company_facts":
                    continue

                evidence_value = evidence.provenance.get(
                    "value"
                )

                if evidence_value is None:
                    continue

                if self._values_match(
                    parsed_value,
                    float(evidence_value),
                ):
                    matched = True
                    break

            if not matched:
                unsupported.append(number_text)

        return unsupported

    @staticmethod
    def _parse_number(
        number_text: str,
    ) -> float | None:

        normalized = (
            number_text.lower()
            .replace("$", "")
            .replace(",", "")
            .strip()
        )

        if normalized.endswith("%"):
            normalized = normalized[:-1].strip()

        multipliers = {
            "thousand": 1_000,
            "million": 1_000_000,
            "billion": 1_000_000_000,
            "trillion": 1_000_000_000_000,
        }

        multiplier = 1

        for word, value in multipliers.items():
            if normalized.endswith(word):
                multiplier = value
                normalized = normalized[
                    :-len(word)
                ].strip()
                break

        try:
            return float(normalized) * multiplier

        except ValueError:
            return None

    @staticmethod
    def _values_match(
        claimed_value: float,
        evidence_value: float,
    ) -> bool:

        tolerance = max(
            abs(evidence_value) * 0.0001,
            1.0,
        )

        return (
            abs(claimed_value - evidence_value)
            <= tolerance
        )

    @staticmethod
    def _aggregate_verdict(
        issues: list[VerificationIssue],
    ) -> str:

        if any(
            issue.issue_type == "invalid_evidence_id"
            for issue in issues
        ):
            return "unsupported"

        if any(
            issue.issue_type == "unsupported_narrative_claim"
            for issue in issues
        ):
            return "partially_supported"

        if any(
            issue.issue_type == "unsupported_numeric_claim"
            for issue in issues
        ):
            return "partially_supported"

        if any(
            issue.issue_type == "uncertain_narrative_claim"
            for issue in issues
        ):
            return "partially_supported"

        return "supported"