from dataclasses import dataclass

from src.config import (
    COMPANIES,
    SEC_COMPANY_FACTS_BASE_URL,
)
from src.ingestion.sec_client import SECClient

METRIC_DEFINITIONS = {
    "revenue": {
        "fact_type": "duration",
        "concepts": [
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "Revenues",
            "SalesRevenueNet",
        ],
    },
    "total_assets": {
        "fact_type": "instant",
        "concepts": [
            "Assets",
        ],
    },
    "cash": {
    "fact_type": "instant",
    "concepts": [
        "CashAndCashEquivalentsAtCarryingValue",
        "CashAndDueFromBanks",
        ],
        },

    "net_income": {
    "fact_type": "duration",
    "concepts": [
        "NetIncomeLoss",
        ],
        },
}


@dataclass
class NumericFact:
    """A structured financial fact retrieved from SEC XBRL data."""

    company: str
    ticker: str
    fact_name: str
    label: str
    value: float
    unit: str
    fiscal_year: int | None
    fiscal_period: str | None
    form: str | None
    filing_date: str | None
    accession_number: str | None
    period_start: str | None
    period_end: str | None


class CompanyFactsTool:
    """Retrieve structured financial facts from SEC CompanyFacts."""

    def __init__(
        self,
        client: SECClient | None = None,
    ):
        self.client = client or SECClient()

    def get_company_facts(
        self,
        ticker: str,
    ) -> dict:
        """Retrieve the complete CompanyFacts dataset for a company."""

        if ticker not in COMPANIES:
            raise ValueError(
                f"Unsupported ticker: {ticker}"
            )

        cik = COMPANIES[ticker]["cik"]

        url = (
            f"{SEC_COMPANY_FACTS_BASE_URL}/"
            f"CIK{cik}.json"
        )

        return self.client.get_json(url)

    def resolve_concept(
        self,
        ticker: str,
        metric: str,
        fiscal_year: int,
        form: str = "10-K",
    ) -> tuple[str, dict, str] | None:
        """
        Resolve a canonical metric to an SEC XBRL concept
        and its best annual observation.
        """

        if metric not in METRIC_DEFINITIONS:
            raise ValueError(
                f"Unsupported metric: {metric}"
                )

        metric_definition = METRIC_DEFINITIONS[metric]
        fact_type = metric_definition["fact_type"]

        data = self.get_company_facts(ticker)

        us_gaap = (
            data.get("facts", {})
            .get("us-gaap", {})
        )


        for concept_name in metric_definition["concepts"]:

            if concept_name not in us_gaap:
                continue

            concept = us_gaap[concept_name]

            units = concept.get("units", {})

            if "USD" not in units:
                continue

            observations = units["USD"]

            observation = self.resolve_observation(
                observations=observations,
                fiscal_year=fiscal_year,
                form=form,
                fact_type=fact_type,
            )

            if observation is None:
                continue

            return (
                concept_name,
                observation,
                concept.get("label", concept_name),
            )

        return None

    def get_metric(
        self,
        ticker: str,
        metric: str,
        fiscal_year: int,
        form: str = "10-K",
    ) -> NumericFact | None:
        """
        Retrieve a canonical financial metric for a fiscal year.
        """

        resolved = self.resolve_concept(
            ticker=ticker,
            metric=metric,
            fiscal_year=fiscal_year,
            form=form,
        )

        if resolved is None:
            return None

        concept_name, observation, label = resolved

        return NumericFact(
            company=COMPANIES[ticker]["name"],
            ticker=ticker,
            fact_name=concept_name,
            label=label,
            value=observation["val"],
            unit="USD",
            fiscal_year=observation.get("fy"),
            fiscal_period=observation.get("fp"),
            form=observation.get("form"),
            filing_date=observation.get("filed"),
            accession_number=observation.get("accn"),
            period_start=observation.get("start"),
            period_end=observation.get("end"),
        )

    def build_evidence(self, fact: NumericFact,) -> dict:
        """
        Convert a NumericFact into a structured evidence object.

        The evidence contains the information needed to trace
        a numeric answer back to its SEC XBRL source.
        """

        return {
            "source": "SEC CompanyFacts",
            "company": fact.company,
            "ticker": fact.ticker,
            "metric": fact.label,
            "concept": fact.fact_name,
            "value": fact.value,
            "unit": fact.unit,
            "fiscal_year": fact.fiscal_year,
            "fiscal_period": fact.fiscal_period,
            "period_start": fact.period_start,
            "period_end": fact.period_end,
            "form": fact.form,
            "filing_date": fact.filing_date,
            "accession_number": fact.accession_number,
        }

    def get_fact(
        self,
        ticker: str,
        fact_name: str,
        fiscal_year: int | None = None,
        form: str | None = None,
    ) -> NumericFact | None:
        """
        Retrieve a specific SEC XBRL concept.

        Kept for direct concept-level access and backwards compatibility.
        """

        data = self.get_company_facts(ticker)

        us_gaap = (
            data.get("facts", {})
            .get("us-gaap", {})
        )

        if fact_name not in us_gaap:
            return None

        fact = us_gaap[fact_name]

        units = fact.get("units", {})

        if not units:
            return None

        if "USD" in units:
            unit_name = "USD"
        else:
            unit_name = next(iter(units))

        observations = units[unit_name]

        candidates = []

        for observation in observations:

            if fiscal_year is not None:
                if observation.get("fy") != fiscal_year:
                    continue

            if form is not None:
                if observation.get("form") != form:
                    continue

            candidates.append(observation)

        if not candidates:
            return None

        observation = candidates[-1]

        return NumericFact(
            company=COMPANIES[ticker]["name"],
            ticker=ticker,
            fact_name=fact_name,
            label=fact.get("label", fact_name),
            value=observation["val"],
            unit=unit_name,
            fiscal_year=observation.get("fy"),
            fiscal_period=observation.get("fp"),
            form=observation.get("form"),
            filing_date=observation.get("filed"),
            accession_number=observation.get("accn"),
            period_start=observation.get("start"),
            period_end=observation.get("end"),
        )


    def resolve_observation(
        self,
        observations: list[dict],
        fiscal_year: int,
        form: str,
        fact_type: str,
    ) -> dict | None:
        """
        Resolve the best observation for a fiscal year.

        Duration facts:
            require start + end and represent activity over a period.

        Instant facts:
            require end only and represent a balance at a point in time.
        """

        candidates = []

        for observation in observations:

            if observation.get("form") != form:
                continue

            if observation.get("fy") != fiscal_year:
                continue

            if fact_type == "duration":
                if not observation.get("start"):
                    continue

                if not observation.get("end"):
                    continue

                if observation.get("fp") != "FY":
                    continue

            elif fact_type == "instant":
                if not observation.get("end"):
                    continue

            else:
                raise ValueError(
                    f"Unsupported fact type: {fact_type}"
                )

            candidates.append(observation)

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda obs: obs["end"],
        )