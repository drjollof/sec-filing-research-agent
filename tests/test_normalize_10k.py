from pathlib import Path

from src.ingestion.normalize_filing import normalize_filing


FILING_PATH = Path(
    "data/raw/AAPL/0000320193-25-000079.html"
)


metadata = {
    "company": "Apple",
    "ticker": "AAPL",
    "cik": "0000320193",
    "form": "10-K",
    "filing_date": "2025-10-31",
    "report_date": "2025-09-27",
    "accession_number": "0000320193-25-000079",
}


result = normalize_filing(
    FILING_PATH,
    metadata,
)


print("=" * 80)
print("NORMALIZED 10-K")
print("=" * 80)

print(
    f"\nCompany: {result['metadata']['company']}"
)

print(
    f"Form: {result['metadata']['form']}"
)

print(
    f"Sections found: {len(result['sections'])}"
)


for i, section in enumerate(
    result["sections"],
    start=1,
):

    print("\n" + "-" * 80)

    print(
        f"{i}. {section['part']} | "
        f"Item {section['item_number']} | "
        f"{section['title']}"
    )

    print(
        f"Text length: "
        f"{len(section['text']):,} characters"
    )

    print(
        f"Tables: "
        f"{len(section['tables'])}"
    )

    print(
        f"Preview:\n"
        f"{section['text'][:500]}"
    )

    if section["tables"]:

        print("\nFirst table preview:")

        print(
            section["tables"][0][:1000]
        )