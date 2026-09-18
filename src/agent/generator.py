import os
import time

from dataclasses import dataclass

from openai import OpenAI

from src.agent.prompt_builder import PromptContext


@dataclass
class GenerationResult:
    answer: str
    model: str
    finish_reason: str | None


class OpenRouterGenerator:
    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        max_retries: int = 2,
    ):
        self.model = model
        self.max_retries = max_retries

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

        last_error = None

        for attempt in range(self.max_retries + 1):

            try:
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

                choice = response.choices[0]

                answer = choice.message.content

                if answer and answer.strip():
                    return GenerationResult(
                        answer=answer,
                        model=response.model,
                        finish_reason=choice.finish_reason,
                    )

                last_error = RuntimeError(
                    "OpenRouter returned an empty response."
                )

            except Exception as exc:
                last_error = exc

            if attempt < self.max_retries:
                time.sleep(1)

        raise RuntimeError(
            "OpenRouter generation failed after "
            f"{self.max_retries + 1} attempts."
        ) from last_error