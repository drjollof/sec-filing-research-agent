import os
from dotenv import load_dotenv


load_dotenv()


SEC_USER_AGENT = os.getenv("SEC_USER_AGENT")

if not SEC_USER_AGENT:
    raise ValueError(
        "SEC_USER_AGENT is not set. "
        "Add it to the .env file."
    )


SEC_SUBMISSIONS_BASE_URL = (
    "https://data.sec.gov/submissions"
)

SEC_EFTS_BASE_URL = (
    "https://efts.sec.gov/LATEST/search-index"
)

SEC_COMPANY_FACTS_BASE_URL = (
    "https://data.sec.gov/api/xbrl/companyfacts"
)

SEC_REQUESTS_PER_SECOND = 8

TARGET_FORMS = {"10-K", "10-Q"}


COMPANIES = {
    "AAPL": {
        "name": "Apple",
        "cik": "0000320193",
    },
    "MSFT": {
        "name": "Microsoft",
        "cik": "0000789019",
    },
    "AMZN": {
        "name": "Amazon",
        "cik": "0001018724",
    },
    "GOOGL": {
        "name": "Alphabet",
        "cik": "0001652044",
    },
    "NVDA": {
        "name": "NVIDIA",
        "cik": "0001045810",
    },
    "TSLA": {
        "name": "Tesla",
        "cik": "0001318605",
    },
    "JNJ": {
        "name": "Johnson & Johnson",
        "cik": "0000200406",
    },
    "JPM": {
        "name": "JPMorgan Chase",
        "cik": "0000019617",
    },
}