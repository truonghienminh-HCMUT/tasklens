from __future__ import annotations

import os
import time

import anthropic

from tasklens.adapters import ModelResponse

# Cố định endpoint chính thức: không để biến môi trường ANTHROPIC_BASE_URL của công cụ khác
# (ví dụ proxy nội bộ) âm thầm chuyển hướng request chứa dữ liệu người dùng.
_BASE_URL = os.getenv("TASKLENS_ANTHROPIC_BASE_URL", "https://api.anthropic.com")


class AnthropicAdapter:
    provider = "anthropic"
    max_input_chars = 400_000

    def __init__(self, model: str):
        self.model = model
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], base_url=_BASE_URL)

    def generate(self, system: str, user: str, json_schema: dict | None = None,
                 max_output_tokens: int | None = None, effort: str | None = None) -> ModelResponse:
        kwargs = {}
        output_config = {}
        if json_schema is not None:
            output_config["format"] = {"type": "json_schema", "schema": json_schema}
        if effort:
            output_config["effort"] = effort
        if output_config:
            kwargs["output_config"] = output_config
        started = time.perf_counter()
        with self._client.messages.stream(
            model=self.model,
            max_tokens=max_output_tokens or 32000,
            system=system,
            messages=[{"role": "user", "content": user}],
            **kwargs,
        ) as stream:
            response = stream.get_final_message()
        latency = time.perf_counter() - started
        text = "".join(block.text for block in response.content if block.type == "text")
        return ModelResponse(
            text=text,
            provider=self.provider,
            model=self.model,
            latency_s=latency,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason,
        )
