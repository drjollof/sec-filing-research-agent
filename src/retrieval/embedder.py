from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class Embedder:
    """Generate semantic embeddings for SEC filing text."""

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def encode(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Convert text into embedding vectors."""

        embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
        )

        return embeddings.tolist()

    def encode_one(self, text: str) -> list[float]:
        """Generate an embedding for a single text."""

        embedding = self.model.encode(
            [text]
        )[0]

        return embedding.tolist()