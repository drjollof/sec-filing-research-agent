from pathlib import Path

from src.config import COMPANIES
from src.ingestion.sec_client import SECClient
from src.ingestion.discover_filings import discover_filings


SEC_ARCHIVES_BASE_URL = (
    "https://www.sec.gov/Archives/edgar/data"
)

RAW_DATA_DIR = Path("data/raw")


def build_filing_url(cik: str, accession_number: str, primary_document: str):
    """Build the SEC EDGAR URL for a filing's primary document."""

    cik_without_leading_zeros = str(int(cik))
    accession_without_dashes = accession_number.replace("-", "")

    return (
        f"{SEC_ARCHIVES_BASE_URL}/"
        f"{cik_without_leading_zeros}/"
        f"{accession_without_dashes}/"
        f"{primary_document}"
    )


def download_filing(filing: dict):
    """Download one filing and save the raw HTML."""

    url = build_filing_url(
        filing["cik"],
        filing["accession_number"],
        filing["primary_document"],
    )

    client = SECClient()

    response = client.session.get(
        url,
        timeout=60,
    )

    if response.status_code != 200:
        response.raise_for_status()

    company_dir = RAW_DATA_DIR / filing["ticker"]
    company_dir.mkdir(parents=True, exist_ok=True)

    accession = filing["accession_number"]

    output_path = (
        company_dir
        / f"{accession}.html"
    )

    output_path.write_text(
        response.text,
        encoding="utf-8",
    )

    return output_path, url


if __name__ == "__main__":

    ticker = "AAPL"

    filings = discover_filings(ticker)

    # Find Apple's 2025 10-K.
    target = next(
        filing
        for filing in filings
        if (
            filing["form"] == "10-K"
            and filing["filing_date"] == "2025-10-31"
        )
    )

    output_path, url = download_filing(target)

    print("Downloaded filing:")
    print(f"Company:   {target['company']}")
    print(f"Form:      {target['form']}")
    print(f"Filed:     {target['filing_date']}")
    print(f"URL:       {url}")
    print(f"Saved to:  {output_path}")