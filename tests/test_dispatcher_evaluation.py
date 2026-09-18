import json
from pathlib import Path

from src.agent.router import QuestionRouter
from src.agent.capability import NumericCapabilityResolver
from src.agent.dispatcher import QuestionDispatcher


QUESTIONS_PATH = Path("evaluation/questions.json")


def run_tests():
    with QUESTIONS_PATH.open("r", encoding="utf-8") as file:
        questions = json.load(file)

    router = QuestionRouter()
    capability_resolver = NumericCapabilityResolver()
    dispatcher = QuestionDispatcher()

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

        expected_route = question["expected_route"]
        expected_support = question["expected_support"]
        expected_metric = question.get("expected_metric")

        if expected_route == "narrative":
            expected_status = "ready"
            expected_tools = ["retriever"]
            expected_metric_value = None

        elif expected_route == "numeric":
            if expected_support == "unsupported":
                expected_status = "unsupported"
                expected_tools = []
                expected_metric_value = None
            else:
                expected_status = "ready"
                expected_tools = ["company_facts"]
                expected_metric_value = expected_metric

        elif expected_route == "hybrid":
            if expected_support == "unsupported":
                expected_status = "unsupported"
                expected_tools = []
                expected_metric_value = None
            else:
                expected_status = "ready"
                expected_tools = ["company_facts", "retriever"]
                expected_metric_value = expected_metric

        else:
            expected_status = "unknown"
            expected_tools = []
            expected_metric_value = None

        correct = (
            plan.status == expected_status
            and plan.tools_to_run == expected_tools
            and plan.metric == expected_metric_value
        )

        results.append(
            {
                "id": question["id"],
                "question": question["question"],
                "expected_status": expected_status,
                "observed_status": plan.status,
                "expected_tools": expected_tools,
                "observed_tools": plan.tools_to_run,
                "expected_metric": expected_metric_value,
                "observed_metric": plan.metric,
                "correct": correct,
            }
        )

    total = len(results)
    correct = sum(result["correct"] for result in results)
    accuracy = correct / total if total else 0.0

    print()
    print("DISPATCHER EVALUATION")
    print("=====================")
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
        print(f'Expected tools: {result["expected_tools"]}')
        print(f'Observed tools: {result["observed_tools"]}')
        print(f'Expected metric: {result["expected_metric"]}')
        print(f'Observed metric: {result["observed_metric"]}')

    print()
    print("PASS: dispatcher evaluation completed.")


if __name__ == "__main__":
    run_tests()