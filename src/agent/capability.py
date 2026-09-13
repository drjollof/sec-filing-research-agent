from dataclasses import dataclass

from src.tools.company_facts import METRIC_DEFINITIONS


@dataclass
class CapabilityResult:
    supported: bool
    metric: str | None
    reason: str


class NumericCapabilityResolver:
    """
    Determines whether a numeric question refers to a
    metric currently supported by CompanyFactsTool.
    """

    METRIC_ALIASES = {
        "revenue": (
            "revenue",
            "revenues",
            "sales",
            "total sales",
        ),
        "total_assets": (
            "total assets",
            "assets",
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

    def resolve(self, question: str) -> CapabilityResult:
        question = question.strip().lower()

        unsupported_phrases = (
            "services revenue",
            "revenue from services",
            "from services",
            "iphone sales",
            "iphone revenue",
            "free cash flow",
            "gross profit",
            "operating income",
        )

        if any(
            phrase in question
            for phrase in unsupported_phrases
        ):
            return CapabilityResult(
                supported=False,
                metric=None,
                reason=(
                    "The question requests a numeric metric or "
                    "sub-metric that is not currently supported "
                    "by CompanyFactsTool."
                ),
            )

        for metric, aliases in self.METRIC_ALIASES.items():
            if any(alias in question for alias in aliases):
                if metric in METRIC_DEFINITIONS:
                    return CapabilityResult(
                        supported=True,
                        metric=metric,
                        reason=f"Numeric metric '{metric}' is supported.",
                    )

        return CapabilityResult(
            supported=False,
            metric=None,
            reason=(
                "The question requests a numeric metric that is "
                "not currently supported by CompanyFactsTool."
            ),
        )