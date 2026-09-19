import os
import tempfile
from pathlib import Path
from database.logger import RequestLogger
from database.models import RequestLog
from database.session import SessionLocal, init_db, engine 


# Create an isolated temporary SQLite database for the test.
# This prevents the test from modifying the real application database.
_TEST_DIR = tempfile.TemporaryDirectory()

os.environ["DATABASE_URL"] = (
    "sqlite:///"
    + str(Path(_TEST_DIR.name) / "test.db").replace("\\", "/")
)


from database.logger import RequestLogger
from database.models import RequestLog
from database.session import SessionLocal, init_db


def run_tests():
    """
    Test database creation, logging, persistence, and retrieval.
    """

    # Create the database tables.
    init_db()

    db = SessionLocal()

    try:
        logger = RequestLogger(db)

        # Database should initially be empty.
        assert logger.count() == 0

        # Write one realistic agent request.
        record = logger.log_request(
            question="What was Apple's revenue in 2025?",
            ticker="AAPL",
            fiscal_year=2025,
            route="NUMERIC",
            status="completed",
            answer="Apple reported revenue of $416.161 billion. [E1]",
            model="some/free-model",
            finish_reason="stop",
            verification_verdict="supported",
            completeness=True,
            latency_ms=1250,
        )

        # SQLAlchemy should assign a primary key.
        assert record.id is not None

        # Verify important fields.
        assert record.ticker == "AAPL"
        assert record.fiscal_year == 2025
        assert record.route == "NUMERIC"
        assert record.status == "completed"
        assert record.model == "some/free-model"
        assert record.finish_reason == "stop"
        assert record.verification_verdict == "supported"
        assert record.completeness is True
        assert record.latency_ms == 1250

        # Exactly one request should now be stored.
        assert logger.count() == 1

        # Read the record back from the database.
        stored = db.query(RequestLog).first()

        assert stored is not None
        assert stored.question == "What was Apple's revenue in 2025?"
        assert stored.answer is not None

        print("PASS: 1/1 database logging test passed.")

    finally:
        db.close()
        engine.dispose()
        _TEST_DIR.cleanup()

if __name__ == "__main__":
    run_tests()