from __future__ import annotations

import os
import time

from openai import OpenAI

from tasklens.adapters import ModelResponse


class OpenAIAdapter:
    provider = "openai"
    max_input_chars = 200_000
    reasoning_models = ("gpt-oss", "o1", "o3", "o4", "gpt-5")  # model nhận tham số reasoning_effort

    def __init__(self, model: str):
        self.model = model
        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def generate(self, system: str, user: str, json_schema: dict | None = None,
                 max_output_tokens: int | None = None, effort: str | None = None) -> ModelResponse:
        kwargs = {}
        if json_schema is not None:
            kwargs["response_format"] = {"type": "json_object"}
        if max_output_tokens is not None:
            kwargs["max_completion_tokens"] = max_output_tokens
        if effort and any(m in self.model for m in self.reasoning_models):
            kwargs["reasoning_effort"] = effort
        started = time.perf_counter()
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            **kwargs,
        )
        latency = time.perf_counter() - started
        choice = response.choices[0]
        usage = response.usage
        return ModelResponse(
            text=choice.message.content or "",
            provider=self.provider,
            model=self.model,
            latency_s=latency,
            input_tokens=getattr(usage, "prompt_tokens", None),
            output_tokens=getattr(usage, "completion_tokens", None),
            stop_reason=choice.finish_reason,
        )
