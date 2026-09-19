import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


DEFAULT_SQLITE_URL = "sqlite:///data/sec_agent.db"


def get_database_url() -> str:
    """
    Return DATABASE_URL if configured.

    Otherwise use a local SQLite database.
    """
    return os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)


def _ensure_sqlite_directory(database_url: str) -> None:
    """
    Create the parent directory for a SQLite file database if necessary.
    """

    prefix = "sqlite:///"

    if not database_url.startswith(prefix):
        return

    database_path = database_url[len(prefix):]

    if database_path == ":memory:":
        return

    Path(database_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )


def create_database_engine():
    """
    Create the SQLAlchemy engine.

    Local development:
        SQLite

    Docker/Cloud deployment:
        PostgreSQL via DATABASE_URL
    """

    database_url = get_database_url()

    _ensure_sqlite_directory(database_url)

    connect_args = {}

    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )


engine = create_database_engine()


SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
)


def init_db() -> None:
    """
    Create database tables if they do not already exist.
    """

    from database.models import Base

    Base.metadata.create_all(
        bind=engine,
    )


def get_db():
    """
    Provide a database session and guarantee that it is closed.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()