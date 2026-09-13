from src.retrieval.retriever import Retriever


def main():

    retriever = Retriever()

    question = (
        "What were Apple's total net sales in 2025?"
    )

    results = retriever.retrieve(
        question,
        top_k=5,
    )

    print(
        f"Retrieved {len(results)} chunks."
    )

    for rank, result in enumerate(
        results,
        start=1,
    ):
        print("\n" + "=" * 80)
        print(f"Rank: {rank}")
        print(f"Chunk ID: {result.chunk_id}")
        print(f"Distance: {result.distance:.4f}")
        print(
            f"Section: "
            f"Item {result.metadata['item_number']} "
            f"- {result.metadata['item_title']}"
        )
        print(
            f"Type: "
            f"{result.metadata['content_type']}"
        )
        print("\n" + result.text[:500])


if __name__ == "__main__":
    main()