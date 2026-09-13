from dataclasses import dataclass

from src.retrieval.embedder import Embedder
from src.retrieval.vector_store import VectorStore


@dataclass
class RetrievedChunk:
    """A chunk returned by semantic retrieval."""

    chunk_id: str
    text: str
    distance: float
    metadata: dict


class Retriever:
    """Semantic retrieval interface for SEC filing chunks."""

    def __init__(
        self,
        embedder: Embedder | None = None,
        vector_store: VectorStore | None = None,
    ):
        self.embedder = embedder or Embedder()
        self.vector_store = vector_store or VectorStore()

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Retrieve the most semantically similar chunks."""

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        query_embedding = (
            self.embedder.encode_one(query)
        )

        results = self.vector_store.search(
            query_embedding,
            n_results=top_k,
        )

        retrieved = []

        for i, chunk_id in enumerate(
            results["ids"][0]
        ):
            retrieved.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    text=results["documents"][0][i],
                    distance=results["distances"][0][i],
                    metadata=results["metadatas"][0][i],
                )
            )

        return retrieved