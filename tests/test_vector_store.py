from pathlib import Path

from src.ingestion.chunk_filing import chunk_filing
from src.ingestion.normalize_filing import normalize_filing
from src.retrieval.embedder import Embedder
from src.retrieval.vector_store import VectorStore


RAW_FILING = Path(
    "data/raw/AAPL/0000320193-25-000079.html"
)


FILING_METADATA = {
    "company": "Apple",
    "ticker": "AAPL",
    "cik": "0000320193",
    "form": "10-K",
    "filing_date": "2025-10-31",
    "report_date": "2025-09-27",
    "accession_number": "0000320193-25-000079",
}


def main():

    print("Normalizing filing...")

    normalized = normalize_filing(
        RAW_FILING,
        FILING_METADATA,
    )

    print(
        f"Sections: "
        f"{len(normalized['sections'])}"
    )

    print("Creating chunks...")

    chunks = chunk_filing(
        normalized
    )

    print(
        f"Chunks: {len(chunks)}"
    )

    print("Loading embedding model...")

    embedder = Embedder()

    print("Generating embeddings...")

    embeddings = embedder.encode(
        [chunk.text for chunk in chunks]
    )

    print(
        f"Embeddings: {len(embeddings)}"
    )

    print(
        f"Dimensions: {len(embeddings[0])}"
    )

    print("Creating ChromaDB collection...")

    store = VectorStore()

    print(
        f"Existing documents: "
        f"{store.count()}"
    )

    print("Adding chunks...")

    store.add_chunks(
        chunks,
        embeddings,
    )

    print(
        f"Documents after insertion: "
        f"{store.count()}"
    )


if __name__ == "__main__":
    main()