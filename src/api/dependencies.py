import time
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from database.logger import RequestLogger

from src.agent.router import QuestionRouter
from src.agent.capability import NumericCapabilityResolver
from src.agent.dispatcher import QuestionDispatcher, ExecutionPlan
from src.agent.executor import ToolExecutor, ExecutionContext
from src.tools.company_facts import CompanyFactsTool
from src.retrieval.retriever import Retriever
from src.agent.prompt_builder import PromptBuilder
from src.agent.generator import OpenRouterGenerator
from src.agent.verifier import EvidenceVerifier
from src.evaluation.completeness_evaluator import AnswerCompletenessEvaluator
from src.config import OPENROUTER_MODEL


@dataclass
class AgentServiceResult:
    """Stable internal representation returned by AgentService."""
    question: str
    answer: str | None
    route: str | None
    status: str
    model: str | None
    finish_reason: str | None
    verification_verdict: str | None
    verification_issues: list[str]
    completeness: bool | None
    completeness_reason: str | None
    evidence: list[Any]


class PipelineComponents:
    """Singleton container so we don't reload embeddings/models on every request."""
    def __init__(self):
        print("Initializing AI Pipeline Components...")
        self.router = QuestionRouter()
        self.capability = NumericCapabilityResolver()
        self.dispatcher = QuestionDispatcher()
        self.company_facts = CompanyFactsTool()
        self.retriever = Retriever()
        self.executor = ToolExecutor(
            company_facts_tool=self.company_facts,
            retriever=self.retriever,
        )
        self.prompt_builder = PromptBuilder()
        self.generator = OpenRouterGenerator(model=OPENROUTER_MODEL)
        self.verifier = EvidenceVerifier()
        self.completeness = AnswerCompletenessEvaluator()

_PIPELINE = None

def get_pipeline() -> PipelineComponents:
    global _PIPELINE
    if _PIPELINE is None:
        _PIPELINE = PipelineComponents()
    return _PIPELINE


class AgentService:
    def __init__(self, db: Session, pipeline: PipelineComponents):
        self.db = db
        self.p = pipeline 

    def query(
        self,
        *,
        question: str,
        ticker: str | None = None,
        fiscal_year: int | None = None,
    ) -> AgentServiceResult:

        started = time.perf_counter()
        logger = RequestLogger(self.db)

        try:
            result = self._run_existing_agent(
                question=question,
                ticker=ticker,
                fiscal_year=fiscal_year,
            )

            latency_ms = int((time.perf_counter() - started) * 1000)

            logger.log_request(
                question=question,
                ticker=ticker,
                fiscal_year=fiscal_year,
                route=result.route,
                status=result.status,
                answer=result.answer,
                model=result.model,
                finish_reason=result.finish_reason,
                verification_verdict=result.verification_verdict,
                completeness=result.completeness,
                latency_ms=latency_ms,
            )

            return result

        except Exception as exc:
            latency_ms = int((time.perf_counter() - started) * 1000)
            logger.log_request(
                question=question,
                ticker=ticker,
                fiscal_year=fiscal_year,
                status="error",
                latency_ms=latency_ms,
                error_message=str(exc),
            )
            raise

    def _run_existing_agent(
        self,
        *,
        question: str,
        ticker: str | None,
        fiscal_year: int | None,
    ) -> AgentServiceResult:
        
    
        router_result = self.p.router.route(question)
        route_str = router_result.route.value
        
        
        capability_result = None
        if route_str in ("numeric", "hybrid"):
            capability_result = self.p.capability.resolve(question)

        plan = self.p.dispatcher.dispatch(
            router_result=router_result,
            capability_result=capability_result,
        )

        if plan.status in ("unsupported", "unknown", "invalid"):
            return AgentServiceResult(
                question=question,
                answer="I cannot answer this question based on my current supported metrics or evidence.",
                route=route_str,
                status=plan.status,
                model=None,
                finish_reason=None,
                verification_verdict="not_evaluated",
                verification_issues=[],
                completeness=False,
                completeness_reason="Pipeline halted before generation.",
                evidence=[],
            )

    
        context = ExecutionContext(ticker=ticker, fiscal_year=fiscal_year)
        exec_result = self.p.executor.execute(plan, question, context)

        if exec_result.status != "success":
            return AgentServiceResult(
                question=question,
                answer="Failed to retrieve evidence.",
                route=route_str,
                status=exec_result.status,
                model=None,
                finish_reason=None,
                verification_verdict="not_evaluated",
                verification_issues=[],
                completeness=False,
                completeness_reason="Execution failed.",
                evidence=[],
            )

    
        prompt_context = self.p.prompt_builder.build(question, exec_result.evidence)
        gen_result = self.p.generator.generate(prompt_context)

    
        verification = self.p.verifier.verify(gen_result.answer, exec_result.evidence)

    
        comp_result = self.p.completeness.evaluate(
            question_id="api",
            question=question,
            answer=gen_result.answer,
            expected_route=route_str,
            expected_metric=plan.metric,
        )

       
        evidence_dicts = [
            {
                "source_type": ev.source_type,
                "content": ev.content,
                "provenance": ev.provenance
            }
            for ev in exec_result.evidence
        ]
        
        issues_str = [f"[{i.issue_type}] {i.message}" for i in verification.issues]

        return AgentServiceResult(
            question=question,
            answer=gen_result.answer,
            route=route_str,
            status="success",
            model=gen_result.model,
            finish_reason=gen_result.finish_reason,
            verification_verdict=verification.verdict,
            verification_issues=issues_str,
            completeness=comp_result.complete,
            completeness_reason=comp_result.reason,
            evidence=evidence_dicts,
        )


def get_agent_service(db: Session) -> AgentService:
    """FastAPI dependency factory."""
    return AgentService(db, get_pipeline())