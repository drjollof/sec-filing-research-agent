import os
from pathlib import Path

from src.config import COMPANIES
from src.ingestion.discover_filings import discover_filings
from src.ingestion.download_filings import download_filing
from src.ingestion.normalize_filing import normalize_filing
from src.ingestion.chunk_filing import chunk_filing
from src.retrieval.embedder import Embedder
from src.retrieval.vector_store import VectorStore


def main():
    print("=" * 80)
    print("STARTING BULK SEC INGESTION")
    print("=" * 80)

    embedder = Embedder()
    store = VectorStore()

    for ticker in COMPANIES.keys():
        print(f"\n--- Processing {ticker} ---")
        try:
            # 1. Discover filings
            filings = discover_filings(ticker)
            
            # Find the most recent 10-K
            ten_k_filings = [f for f in filings if f["form"] == "10-K"]
            if not ten_k_filings:
                print(f"  [!] No 10-K found for {ticker} in recent submissions.")
                continue
                
            target = ten_k_filings[0]  # The first one is the most recent
            print(f"  Found 10-K (Filed: {target['filing_date']})")

            # 2. Download
            output_path, url = download_filing(target)
            print(f"  Downloaded HTML to {output_path}")

            # 3. Normalize
            normalized = normalize_filing(output_path, target)

            # 4. Chunk
            chunks = chunk_filing(normalized)
            print(f"  Generated {len(chunks)} chunks.")

            # 5. Embed & Store
            print("  Generating embeddings (this may take a minute)...")
            embeddings = embedder.encode([chunk.text for chunk in chunks])
            
            # Safely add to ChromaDB (it will ignore duplicates if AAPL is already there)
            store.add_chunks(chunks, embeddings)
            
            print(f"Successfully added {ticker} to ChromaDB.")
            print(f"Current total chunks in database: {store.count()}")

        except Exception as e:
            print(f"Failed to process {ticker}: {e}")

    print("\n" + "=" * 80)
    print("BULK INGESTION COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    main()