from src.retrieval.embedder import Embedder
from src.retrieval.vector_store import VectorStore


QUESTIONS = [
    "What were Apple's total net sales in 2025?",
    "What factors could negatively affect Apple's business?",
    "What products does Apple sell?",
    "How did Apple perform in China?",
]


def main():

    embedder = Embedder()
    store = VectorStore()

    print(
        f"Documents in ChromaDB: "
        f"{store.count()}"
    )

    for question in QUESTIONS:

        print("\n" + "=" * 80)
        print(f"QUESTION: {question}")
        print("=" * 80)

        query_embedding = embedder.encode_one(
            question
        )

        results = store.search(
            query_embedding,
            n_results=5,
        )

        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for i in range(len(ids)):

            metadata = metadatas[i]

            print("\n" + "-" * 80)
            print(f"Rank: {i + 1}")
            print(f"Distance: {distances[i]:.4f}")
            print(f"Chunk: {ids[i]}")
            print(
                f"Section: "
                f"Item {metadata['item_number']} "
                f"- {metadata['item_title']}"
            )
            print(
                f"Content type: "
                f"{metadata['content_type']}"
            )
            print("\nTEXT:")
            print(documents[i][:1000])


if __name__ == "__main__":
    main()