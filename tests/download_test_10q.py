from src.ingestion.discover_filings import discover_filings
from src.ingestion.download_filings import download_filing


ticker = "AAPL"

filings = discover_filings(ticker)

target = next(
    filing
    for filing in filings
    if (
        filing["form"] == "10-Q"
        and filing["filing_date"] == "2026-07-31"
    )
)

output_path, url = download_filing(target)

print("Downloaded filing:")
print(f"Company:   {target['company']}")
print(f"Form:      {target['form']}")
print(f"Filed:     {target['filing_date']}")
print(f"URL:       {url}")
print(f"Saved to:  {output_path}")