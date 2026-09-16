import os
from dataclasses import dataclass

from openai import OpenAI

from src.agent.prompt_builder import PromptContext


@dataclass
class GenerationResult:
    answer: str
    model: str


class OpenRouterGenerator:
    def __init__(
        self,
        model: str,
        api_key: str | None = None,
    ):
        self.model = model

        api_key = api_key or os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def generate(
        self,
        prompt_context: PromptContext,
    ) -> GenerationResult:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": prompt_context.system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt_context.user_prompt,
                },
            ],
            temperature=0,
        )

        answer = response.choices[0].message.content

        if not answer:
            raise RuntimeError(
                "OpenRouter returned an empty response."
            )

        return GenerationResult(
            answer=answer,
            model=response.model,
        )