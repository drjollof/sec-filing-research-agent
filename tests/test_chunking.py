from pathlib import Path

from src.ingestion.chunk_filing import chunk_filing
from src.ingestion.normalize_filing import normalize_filing


FILING_PATH = Path(
    "data/raw/AAPL/0000320193-25-000079.html"
)


METADATA = {
    "company": "Apple",
    "ticker": "AAPL",
    "cik": "0000320193",
    "form": "10-K",
    "filing_date": "2025-10-31",
    "report_date": "2025-09-27",
    "accession_number": "0000320193-25-000079",
}


normalized = normalize_filing(
    FILING_PATH,
    METADATA,
)


chunks = chunk_filing(
    normalized,
)


print("=" * 80)
print("CHUNKING TEST")
print("=" * 80)

print(
    f"\nTotal chunks: {len(chunks)}"
)


narrative_count = sum(
    chunk.content_type == "narrative"
    for chunk in chunks
)

table_count = sum(
    chunk.content_type == "table"
    for chunk in chunks
)


print(
    f"Narrative chunks: {narrative_count}"
)

print(
    f"Table chunks:     {table_count}"
)


print("\nFIRST 10 CHUNKS")
print("-" * 80)

for chunk in chunks[:10]:

    print(
        f"\nID: {chunk.chunk_id}"
    )

    print(
        f"Section: "
        f"Item {chunk.item_number} "
        f"| {chunk.item_title}"
    )

    print(
        f"Type: {chunk.content_type}"
    )

    print(
        f"Length: {len(chunk.text)} characters"
    )

    print(
        f"Text: {chunk.text[:300]}"
    )


print("\nTABLE CHUNK EXAMPLE")
print("-" * 80)

table_chunk = next(
    (
        chunk
        for chunk in chunks
        if chunk.content_type == "table"
    ),
    None,
)

if table_chunk:

    print(
        f"ID: {table_chunk.chunk_id}"
    )

    print(
        f"Section: "
        f"Item {table_chunk.item_number} "
        f"| {table_chunk.item_title}"
    )

    print(
        table_chunk.text[:1000]
    )