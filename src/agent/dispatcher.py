from dataclasses import dataclass

from src.agent.router import Route, RouterResult
from src.agent.capability import CapabilityResult


@dataclass
class ExecutionPlan:
    status: str
    tools_to_run: list[str]
    metric: str | None


class QuestionDispatcher:
    def dispatch(
        self,
        router_result: RouterResult,
        capability_result: CapabilityResult | None = None,
    ) -> ExecutionPlan:

        if router_result.route == Route.UNKNOWN:
            return ExecutionPlan(
                status="unknown",
                tools_to_run=[],
                metric=None,
            )

        if router_result.route == Route.NARRATIVE:
            return ExecutionPlan(
                status="ready",
                tools_to_run=["retriever"],
                metric=None,
            )

        if router_result.route == Route.NUMERIC:
            if capability_result is None:
                return ExecutionPlan(
                    status="invalid",
                    tools_to_run=[],
                    metric=None,
                )

            if not capability_result.supported:
                return ExecutionPlan(
                    status="unsupported",
                    tools_to_run=[],
                    metric=None,
                )

            return ExecutionPlan(
                status="ready",
                tools_to_run=["company_facts"],
                metric=capability_result.metric,
            )

        if router_result.route == Route.HYBRID:
            if capability_result is None:
                return ExecutionPlan(
                    status="invalid",
                    tools_to_run=[],
                    metric=None,
                )

            if not capability_result.supported:
                return ExecutionPlan(
                    status="unsupported",
                    tools_to_run=[],
                    metric=None,
                )

            return ExecutionPlan(
                status="ready",
                tools_to_run=[
                    "company_facts",
                    "retriever",
                ],
                metric=capability_result.metric,
            )

        return ExecutionPlan(
            status="invalid",
            tools_to_run=[],
            metric=None,
        )