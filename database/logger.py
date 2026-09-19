from sqlalchemy.orm import Session

from database.models import RequestLog


class RequestLogger:
    """
    Persist request/response observability information.

    The logger is deliberately separate from the agent pipeline.
    """

    def __init__(self, db: Session):
        self.db = db

    def log_request(
        self,
        *,
        question: str,
        ticker: str | None = None,
        fiscal_year: int | None = None,
        route: str | None = None,
        status: str,
        answer: str | None = None,
        model: str | None = None,
        finish_reason: str | None = None,
        verification_verdict: str | None = None,
        completeness: bool | None = None,
        latency_ms: int | None = None,
        error_message: str | None = None,
    ) -> RequestLog:
        """
        Store one completed or failed request.
        """

        record = RequestLog(
            question=question,
            ticker=ticker,
            fiscal_year=fiscal_year,
            route=route,
            status=status,
            answer=answer,
            model=model,
            finish_reason=finish_reason,
            verification_verdict=verification_verdict,
            completeness=completeness,
            latency_ms=latency_ms,
            error_message=error_message,
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return record

    def count(self) -> int:
        """
        Return the number of logged requests.
        """

        return self.db.query(RequestLog).count()