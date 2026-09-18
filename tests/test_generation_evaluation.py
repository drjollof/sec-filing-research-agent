import json
from pathlib import Path

from src.agent.router import QuestionRouter
from src.agent.capability import NumericCapabilityResolver
from src.agent.dispatcher import QuestionDispatcher
from src.agent.executor import ToolExecutor, ExecutionContext
from src.agent.prompt_builder import PromptBuilder
from src.agent.generator import OpenRouterGenerator
from src.agent.verifier import EvidenceVerifier
from src.tools.company_facts import CompanyFactsTool
from src.retrieval.retriever import Retriever
from src.evaluation.completeness_evaluator import AnswerCompletenessEvaluator


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

    prompt_builder = PromptBuilder()
    generator = OpenRouterGenerator(model="openrouter/free")
    verifier = EvidenceVerifier()
    completeness_evaluator = AnswerCompletenessEvaluator()

    answerable_questions = [
        question
        for question in questions
        if question["expected_support"] != "unsupported"
    ]

    results = []

    for question in answerable_questions:
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

        if execution_result.status != "success":
            results.append(
                {
                    "id": question["id"],
                    "status": "execution_failed",
                    "answer": "",
                    "verdict": "not_evaluated",
                    "issue_count": 0,
                    "model": "none",
                    "finish_reason": "none",
                    "complete": False,
                    "completeness_reason": "Execution failed"
                }
            )
            continue

        prompt_context = prompt_builder.build(
            question=question["question"],
            evidence=execution_result.evidence,
        )

        generation_result = generator.generate(prompt_context)

        verification_result = verifier.verify(
            answer=generation_result.answer,
            evidence=execution_result.evidence,
        )
        
        completeness_result = completeness_evaluator.evaluate(
            question_id=question["id"],
            question=question["question"],
            answer=generation_result.answer,
            expected_route=question["expected_route"],
            expected_metric=question.get("expected_metric"),
        )

        results.append(
            {
                "id": question["id"],
                "status": "generated",
                "answer": generation_result.answer,
                "verdict": verification_result.verdict,
                "issue_count": len(verification_result.issues),
                "issues": verification_result.issues,
                "model": getattr(generation_result, "actual_model", generation_result.model),
                "finish_reason": getattr(generation_result, "finish_reason", "unknown"),
                "complete": completeness_result.complete,
                "completeness_reason": completeness_result.reason,
            }
        )

    print()
    print("END-TO-END GENERATION EVALUATION")
    print("================================")
    print(f"Questions evaluated: {len(results)}")

    supported = sum(
        result["verdict"] == "supported"
        for result in results
    )

    partially_supported = sum(
        result["verdict"] == "partially_supported"
        for result in results
    )

    unsupported = sum(
        result["verdict"] == "unsupported"
        for result in results
    )

    not_evaluated = sum(
        result["verdict"] == "not_evaluated"
        for result in results
    )
    
    complete_count = sum(
        result["complete"]
        for result in results
    )

    print(f"Fully supported: {supported}")
    print(f"Partially supported: {partially_supported}")
    print(f"Unsupported: {unsupported}")
    print(f"Not evaluated: {not_evaluated}")
    print(f"Complete responses: {complete_count}/{len(results)}")

    print()
    print("GENERATED ANSWERS")
    print("=================")

    for result in results:
        print()
        print(f'{result["id"]}')
        print(f'Status: {result["status"]}')
        print(f'Model: {result["model"]}')
        print(f'Finish reason: {result["finish_reason"]}')
        print(f'Verdict: {result["verdict"]}')
        print(f'Issues: {result["issue_count"]}')

        if result.get("issues"):
            for issue in result["issues"]:
                print(f"  - {issue.issue_type}: {issue.message}")
                
        print(f'Completeness: {result["complete"]}')
        print(f'Completeness reason: {result["completeness_reason"]}')
        print(f'Answer: {result["answer"]}')

    print()
    print("PASS: end-to-end generation evaluation completed.")


if __name__ == "__main__":
    run_tests()