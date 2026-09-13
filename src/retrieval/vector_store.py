from pathlib import Path

import chromadb

from src.ingestion.chunk_filing import DocumentChunk


CHROMA_DIR = Path("data/chroma")
COLLECTION_NAME = "sec_filings"


class VectorStore:
    """Persistent ChromaDB store for SEC filing chunks."""

    def __init__(
        self,
        path: Path = CHROMA_DIR,
        collection_name: str = COLLECTION_NAME,
    ):
        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.client = chromadb.PersistentClient(
            path=str(path)
        )

        self.collection = (
            self.client.get_or_create_collection(
                name=collection_name,
                configuration={
                    "hnsw": {
                        "space": "cosine"
                    }
                },
            )
        )

    def count(self) -> int:
        """Return the number of stored chunks."""

        return self.collection.count()


    def search(self, query_embedding: list[float], n_results: int = 5,):
        
        """Return the most similar chunks for a query embedding."""

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )

    def add_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ):
        """Add document chunks and their embeddings to ChromaDB."""

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks must match "
                "number of embeddings."
            )

        if not chunks:
            return

        ids = [
            chunk.chunk_id
            for chunk in chunks
        ]

        documents = [
            chunk.text
            for chunk in chunks
        ]

        metadatas = [
            {
                "company": chunk.company,
                "ticker": chunk.ticker,
                "cik": chunk.cik,
                "form": chunk.form,
                "filing_date": chunk.filing_date,
                "report_date": chunk.report_date,
                "accession_number": chunk.accession_number,
                "part": chunk.part or "",
                "item_number": chunk.item_number,
                "item_title": chunk.item_title,
                "content_type": chunk.content_type,
                "chunk_index": chunk.chunk_index,
            }
            for chunk in chunks
        ]

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    