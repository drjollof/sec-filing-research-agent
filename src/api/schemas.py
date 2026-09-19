from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """
    Public request schema for the SEC Filing Research Agent.
    """

    question: str = Field(
        ...,
        min_length=3,
        description="The user's SEC filing research question.",
    )

    ticker: str | None = Field(
        default=None,
        min_length=1,
        max_length=10,
        description="Optional company ticker, e.g. AAPL.",
    )

    fiscal_year: int | None = Field(
        default=None,
        ge=1900,
        le=2100,
        description="Optional fiscal year.",
    )


class VerificationResponse(BaseModel):
    """
    Public representation of verifier output.
    """

    verdict: str | None = None
    issues: list[str] = Field(default_factory=list)


class QueryResponse(BaseModel):
    """
    Public response returned by POST /query.
    """

    question: str
    answer: str | None = None

    route: str | None = None
    status: str

    model: str | None = None
    finish_reason: str | None = None

    verification: VerificationResponse

    completeness: bool | None = None
    completeness_reason: str | None = None

    evidence: list[Any] = Field(default_factory=list)