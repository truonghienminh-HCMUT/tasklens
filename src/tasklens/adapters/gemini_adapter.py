from __future__ import annotations

import os
import time

from google import genai
from google.genai import types

from tasklens.adapters import ModelResponse


class GeminiAdapter:
    provider = "gemini"

    def __init__(self, model: str):
        self.model = model
        self._client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        # Context của Gemini/Gemma rất lớn, nhưng gói miễn phí của Gemma từ chối (429) một request
        # ~30k token (TC09 ở V1), chờ bao lâu cũng không qua. Giữ tài liệu gửi đi ≤ ~10k token
        # (~3,6 ký tự/token theo count_tokens).
        self.max_input_chars = 36_000 if model.startswith("gemma") else 200_000

    def generate(self, system: str, user: str, json_schema: dict | None = None,
                 max_output_tokens: int | None = None, effort: str | None = None) -> ModelResponse:
        # `effort`: Gemma không có chế độ suy luận điều chỉnh được, nên bỏ qua.
        config = types.GenerateContentConfig(
            system_instruction=system,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )
        if max_output_tokens is not None:
            config.max_output_tokens = max_output_tokens
        # Gemma ở chế độ JSON schema bị suy biến (hết token mà text rỗng, bị chặn RECITATION, nội dung vỡ):
        # xem docs/model-swap-log.md. Với Gemma chỉ dùng hướng dẫn trong prompt + cổng validate bằng code.
        if json_schema is not None and not self.model.startswith("gemma"):
            config.response_mime_type = "application/json"
            config.response_json_schema = json_schema
        started = time.perf_counter()
        response = self._client.models.generate_content(model=self.model, contents=user, config=config)
        latency = time.perf_counter() - started
        usage = response.usage_metadata
        finish = response.candidates[0].finish_reason if response.candidates else None
        return ModelResponse(
            text=response.text or "",
            provider=self.provider,
            model=self.model,
            latency_s=latency,
            input_tokens=getattr(usage, "prompt_token_count", None),
            output_tokens=getattr(usage, "candidates_token_count", None),
            stop_reason=str(finish) if finish is not None else None,
        )
