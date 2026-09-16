from dataclasses import dataclass

from src.agent.evidence import Evidence


@dataclass
class PromptContext:
    system_prompt: str
    user_prompt: str


class PromptBuilder:
    SYSTEM_PROMPT = """You are a financial research assistant.

Answer the user's question using only the evidence provided.

Rules:
1. Do not use outside knowledge.
2. Do not invent facts, numbers, explanations, or quotations.
3. Every factual claim must be supported by the provided evidence.
4. Every numeric claim must be supported by CompanyFacts evidence.
5. Cite the evidence used for each important claim using its evidence ID. Do not combine citations (e.g., use [E1] [E2], NOT [E1, E2]).
6. If the evidence is insufficient to answer the question, say so clearly.
7. Do not substitute a broader metric for a more specific metric that was requested.
8. For hybrid questions, use both the structured financial evidence and the filing evidence when available.
9. Keep the answer concise and directly answer the question.
"""

    def build(
        self,
        question: str,
        evidence: list[Evidence],
    ) -> PromptContext:

        evidence_blocks = []

        for index, item in enumerate(evidence, start=1):
            evidence_id = f"E{index}"

            provenance = self._format_provenance(
                item.provenance
            )

            block = (
                f"[{evidence_id}]\n"
                f"Source type: {item.source_type}\n"
                f"Content:\n{item.content}\n"
                f"Provenance:\n{provenance}"
            )

            evidence_blocks.append(block)

        if evidence_blocks:
            evidence_text = "\n\n".join(evidence_blocks)
        else:
            evidence_text = "No evidence was retrieved."

        user_prompt = (
            f"Question:\n{question}\n\n"
            f"Evidence:\n{evidence_text}\n\n"
            "Answer the question using only the evidence above. "
            "Include evidence IDs for the claims you make."
        )

        return PromptContext(
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

    @staticmethod
    def _format_provenance(
        provenance: dict,
    ) -> str:

        lines = []

        for key, value in provenance.items():
            lines.append(f"{key}: {value}")

        return "\n".join(lines)