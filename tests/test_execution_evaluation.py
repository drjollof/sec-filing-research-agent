import json
from pathlib import Path

from src.agent.router import QuestionRouter
from src.agent.capability import NumericCapabilityResolver
from src.agent.dispatcher import QuestionDispatcher
from src.agent.executor import ToolExecutor, ExecutionContext
from src.tools.company_facts import CompanyFactsTool
from src.retrieval.retriever import Retriever


QUESTIONS_PATH = Path("evaluation/questions.json")


def run_tests():
    with QUESTIONS_PATH.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    router = QuestionRouter()
    capability_resolver = NumericCapabilityResolver()
    dispatcher = QuestionDispatcher()

    company_facts_tool = CompanyFactsTool()
    retriever = Retriever()

    executor = ToolExecutor(
        company_facts_tool=company_facts_tool,
        retriever=retriever,
    )

    results = []

    for question in questions:
        router_result = router.route(question["question"])

        capability_result = None

        if router_result.route.value in {"numeric", "hybrid"}:
            capability_result = capability_resolver.resolve(
                question["question"]
            )

        plan = dispatcher.dispatch(
            router_result=router_result,
            capability_result=capability_result,
        )

        context = ExecutionContext(
            ticker=question["ticker"],
            fiscal_year=question["fiscal_year"],
        )

        execution_result = executor.execute(
            plan=plan,
            question=question["question"],
            context=context,
        )

        evidence_types = [
            evidence.source_type
            for evidence in execution_result.evidence
        ]

        if plan.status == "unsupported":
            expected_status = "unsupported"
            expected_types = []

        elif question["expected_route"] == "numeric":
            expected_status = "success"
            expected_types = ["company_facts"]

        elif question["expected_route"] == "narrative":
            expected_status = "success"
            expected_types = ["filing_chunk"]

        elif question["expected_route"] == "hybrid":
            expected_status = "success"
            expected_types = ["company_facts", "filing_chunk"]

        else:
            expected_status = "unknown"
            expected_types = []
            
        correct = (
            execution_result.status == expected_status
            and all(
                expected_type in evidence_types
                for expected_type in expected_types
            )
        )

        results.append(
            {
                "id": question["id"],
                "question": question["question"],
                "expected_status": expected_status,
                "observed_status": execution_result.status,
                "expected_evidence": expected_types,
                "observed_evidence": evidence_types,
                "evidence_count": len(execution_result.evidence),
                "correct": correct,
            }
        )

    total = len(results)
    correct = sum(result["correct"] for result in results)
    accuracy = correct / total if total else 0.0

    print()
    print("FULL EXECUTION EVALUATION")
    print("=========================")
    print("Corpus: AAPL 2025")
    print(f"Questions evaluated: {total}")
    print(f"Correct: {correct}")
    print(f"Accuracy: {accuracy:.2%}")

    print()
    print("QUESTION RESULTS")
    print("================")

    for result in results:
        status = "PASS" if result["correct"] else "MISS"

        print()
        print(f'{result["id"]} [{status}]')
        print(f'Question: {result["question"]}')
        print(f'Expected status: {result["expected_status"]}')
        print(f'Observed status: {result["observed_status"]}')
        print(f'Expected evidence: {result["expected_evidence"]}')
        print(f'Observed evidence: {result["observed_evidence"]}')
        print(f'Evidence count: {result["evidence_count"]}')

    print()
    print("PASS: full execution evaluation completed.")


if __name__ == "__main__":
    run_tests()