"""Model Adapter: lớp duy nhất biết đến tên model / SDK cụ thể.

Logic, dữ liệu, evals và guardrails nằm ngoài lớp này, nên đổi model chỉ là đổi
một chuỗi `provider:model` (B12, slide 27).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from tasklens.config import DEFAULT_MODELS, KEY_ENV, has_key


@dataclass
class ModelResponse:
    text: str
    provider: str
    model: str
    latency_s: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    stop_reason: str | None = None


class ModelAdapter(Protocol):
    provider: str
    model: str
    max_input_chars: int  # ngân sách ký tự cho tài liệu gửi đi (giới hạn context / rate limit của gói dịch vụ)

    def generate(self, system: str, user: str, json_schema: dict | None = None,
                 max_output_tokens: int | None = None, effort: str | None = None) -> ModelResponse:
        """Gọi model một lần.

        `json_schema`: bật chế độ output có cấu trúc của nhà cung cấp (nếu hỗ trợ).
        `max_output_tokens`: giới hạn token đầu ra; None = để mặc định của nhà cung cấp (hành vi V1).
        `effort`: mức suy luận "low" | "medium" | "high" cho model có suy luận; model không hỗ trợ thì bỏ qua.
        """
        ...


def get_adapter(spec: str) -> ModelAdapter:
    """spec: 'gemini', 'groq:llama-3.3-70b-versatile', 'openai:gpt-4.1-mini', 'anthropic:claude-opus-5', 'mock'."""
    provider, _, model = spec.partition(":")
    provider = provider.strip().lower()
    model = model.strip() or DEFAULT_MODELS.get(provider, "")
    if provider not in DEFAULT_MODELS:
        raise ValueError(f"Provider không hỗ trợ: {provider}")
    if not has_key(provider):
        raise RuntimeError(f"Chưa có {KEY_ENV[provider]} trong file .env")

    if provider == "gemini":
        from tasklens.adapters.gemini_adapter import GeminiAdapter

        return GeminiAdapter(model)
    if provider == "groq":
        from tasklens.adapters.groq_adapter import GroqAdapter

        return GroqAdapter(model)
    if provider == "openai":
        from tasklens.adapters.openai_adapter import OpenAIAdapter

        return OpenAIAdapter(model)
    if provider == "anthropic":
        from tasklens.adapters.anthropic_adapter import AnthropicAdapter

        return AnthropicAdapter(model)
    from tasklens.adapters.mock_adapter import MockAdapter

    return MockAdapter()
