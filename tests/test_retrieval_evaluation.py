import json
from pathlib import Path

from src.evaluation.retrieval_evaluator import RetrievalEvaluator
from src.retrieval.retriever import Retriever


QUESTIONS_PATH = Path("evaluation/questions.json")


def run_tests():

    with QUESTIONS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        questions = json.load(file)

    retrieval_questions = [
        question
        for question in questions
        if question["expected_support"]
        in {
            "retrieval",
            "company_facts_and_retrieval",
        }
    ]

    retriever = Retriever()
    evaluator = RetrievalEvaluator()

    results = []

    for question in retrieval_questions:

        retrieved_top_5 = retriever.retrieve(
            question["question"],
            top_k=5,
        )

        result = evaluator.evaluate(
            question_id=question["id"],
            retrieved_chunks=retrieved_top_5,
            expected_sections=question["expected_sections"],
        )

        results.append(
            {
                "question_id": question["id"],
                "question": question["question"],
                "hit_at_1": result.hit_at_1,
                "hit_at_3": result.hit_at_3,
                "hit_at_5": result.hit_at_5,
                "expected_sections": result.expected_sections,
                "retrieved_sections": result.retrieved_sections,
            }
        )

    total = len(results)
    
    hits_at_1 = sum(result["hit_at_1"] for result in results)
    hits_at_3 = sum(result["hit_at_3"] for result in results)
    hits_at_5 = sum(result["hit_at_5"] for result in results)

    hit_at_1 = hits_at_1 / total if total else 0.0
    hit_at_3 = hits_at_3 / total if total else 0.0
    hit_at_5 = hits_at_5 / total if total else 0.0

    print()
    print("RETRIEVAL EVALUATION")
    print("====================")
    print(f"Questions evaluated: {total}")
    print(f"Hit@1: {hit_at_1:.2%}")
    print(f"Hit@3: {hit_at_3:.2%}")
    print(f"Hit@5: {hit_at_5:.2%}")

    print()
    print("QUESTION RESULTS")
    print("================")

    for result in results:

        status = "HIT" if result["hit_at_5"] else "MISS"

        print()
        print(f"{result['question_id']} [{status}]")
        print(f"Question: {result['question']}")
        print(f"Expected: {result['expected_sections']}")
        print(f"Retrieved: {result['retrieved_sections']}")
        print(f"Hit@1={result['hit_at_1']} Hit@3={result['hit_at_3']} Hit@5={result['hit_at_5']}")

    print()
    print("PASS: retrieval evaluation completed.")


if __name__ == "__main__":
    run_tests()