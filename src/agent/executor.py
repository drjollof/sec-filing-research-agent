from dataclasses import dataclass

from src.agent.dispatcher import ExecutionPlan
from src.agent.evidence import EvidenceNormalizer


@dataclass
class ExecutionContext:
    ticker: str | None = None
    fiscal_year: int | None = None


@dataclass
class ExecutionResult:
    status: str
    evidence: list


class ToolExecutor:
    def __init__(self, company_facts_tool, retriever):
        self.company_facts_tool = company_facts_tool
        self.retriever = retriever
        self.normalizer = EvidenceNormalizer()

    def execute(
        self,
        plan: ExecutionPlan,
        question: str,
        context: ExecutionContext,
    ) -> ExecutionResult:

        if plan.status != "ready":
            return ExecutionResult(
                status=plan.status,
                evidence=[],
            )

        evidence = []

        if "company_facts" in plan.tools_to_run:
            if context.ticker is None or context.fiscal_year is None:
                return ExecutionResult(
                    status="invalid",
                    evidence=[],
                )

            fact = self.company_facts_tool.get_metric(
                ticker=context.ticker,
                metric=plan.metric,
                fiscal_year=context.fiscal_year,
            )

            if fact is not None:
                evidence.append(
                    self.normalizer.from_numeric_fact(fact)
                )

        if "retriever" in plan.tools_to_run:
            chunks = self.retriever.retrieve(question)

            for chunk in chunks:
                evidence.append(
                    self.normalizer.from_retrieved_chunk(chunk)
                )

        return ExecutionResult(
            status="success",
            evidence=evidence,
        )