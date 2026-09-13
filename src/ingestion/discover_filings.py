from src.config import (
    COMPANIES,
    SEC_SUBMISSIONS_BASE_URL,
    TARGET_FORMS,
)

from src.ingestion.sec_client import SECClient


def discover_filings(ticker: str):
    """Discover 10-K and 10-Q filings for a company."""

    company = COMPANIES[ticker]
    cik = company["cik"]

    url = f"{SEC_SUBMISSIONS_BASE_URL}/CIK{cik}.json"

    client = SECClient()

    data = client.get_json(url)

    recent = data["filings"]["recent"]

    filings = []

    for i, form in enumerate(recent["form"]):

        if form not in TARGET_FORMS:
            continue

        accession_number = recent["accessionNumber"][i]
        primary_document = recent["primaryDocument"][i]

        filings.append(
            {
                "company": company["name"],
                "ticker": ticker,
                "cik": cik,
                "form": form,
                "filing_date": recent["filingDate"][i],
                "report_date": recent["reportDate"][i],
                "accession_number": accession_number,
                "primary_document": primary_document,
            }
        )

    return filings


if __name__ == "__main__":

    filings = discover_filings("AAPL")

    print(f"Found {len(filings)} 10-K/10-Q filings.")

    for filing in filings[:10]:
        print(
            filing["form"],
            filing["filing_date"],
            filing["accession_number"],
            filing["primary_document"],
        )