from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db, init_db

from src.api.dependencies import AgentService, get_agent_service
from src.api.schemas import (
    QueryRequest,
    QueryResponse,
    VerificationResponse,
)


app = FastAPI(
    title="SEC Filing Research Agent",
    description=(
        "RAG-based SEC filing research API with explicit "
        "tool routing, evidence retrieval, generation, "
        "verification, and request logging."
    ),
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    """
    Ensure the configured database schema exists.
    """

    init_db()


@app.get("/health")
def health():
    """
    Lightweight health-check endpoint.
    """

    return {
        "status": "ok",
    }


@app.post(
    "/query",
    response_model=QueryResponse,
)
def query(
    request: QueryRequest,
    service: AgentService = Depends(
        lambda db=Depends(get_db): get_agent_service(db)
    ),
):
    """
    Execute one SEC filing research request.
    """

    try:
        result = service.query(
            question=request.question,
            ticker=request.ticker,
            fiscal_year=request.fiscal_year,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

    return QueryResponse(
        question=result.question,
        answer=result.answer,
        route=result.route,
        status=result.status,
        model=result.model,
        finish_reason=result.finish_reason,
        verification=VerificationResponse(
            verdict=result.verification_verdict,
            issues=result.verification_issues,
        ),
        completeness=result.completeness,
        completeness_reason=result.completeness_reason,
        evidence=result.evidence,
    )