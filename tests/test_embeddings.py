from src.retrieval.embedder import Embedder


def main():
    embedder = Embedder()

    texts = [
        "Apple reported strong revenue growth.",
        "Apple's sales increased during the year.",
        "The company discussed cybersecurity risks.",
    ]

    embeddings = embedder.encode(texts)

    print(f"Number of embeddings: {len(embeddings)}")
    print(f"Embedding dimensions: {len(embeddings[0])}")

    print("\nFirst embedding:")
    print(embeddings[0][:10])


if __name__ == "__main__":
    main()