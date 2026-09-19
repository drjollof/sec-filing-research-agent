from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class RequestLog(Base):
    """
    Database record for one SEC Filing Research Agent request.

    This table is for observability/logging only.
    It is not part of the agent's reasoning pipeline.
    """

    __tablename__ = "request_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    ticker: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    fiscal_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    route: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    model: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    finish_reason: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    verification_verdict: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )

    completeness: Mapped[bool | None] = mapped_column(
        nullable=True,
    )

    latency_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )