"""TaskLens V1: một lần gọi model, mọi quy tắc nằm trong system prompt.

Không có sanitize, pre-check hay validate bằng code. Chỉ tách JSON ra khỏi câu trả lời
để hiển thị được.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from pydantic import ValidationError

from tasklens.adapters import ModelAdapter, ModelResponse
from tasklens.config import load_instruction
from tasklens.jsonparse import extract_json
from tasklens.schema import Analysis

DEFAULT_REQUEST = "Phân rã đề bài này và lập kế hoạch thực hiện cho tôi."


@dataclass
class RunResult:
    version: str
    output: dict | None
    raw_text: str
    error: str = ""
    responses: list[ModelResponse] = field(default_factory=list)
    sent: list[str] = field(default_factory=list)  # nguyên văn những gì đã gửi tới model bên ngoài
    notes: list[str] = field(default_factory=list)
    system_prompt: str = ""

    @property
    def latency_s(self) -> float:
        return sum(r.latency_s for r in self.responses)

    @property
    def input_tokens(self) -> int:
        return sum(r.input_tokens or 0 for r in self.responses)

    @property
    def output_tokens(self) -> int:
        return sum(r.output_tokens or 0 for r in self.responses)


def build_user_message(document: str, request: str) -> str:
    return f"Đề bài:\n{document}\n\nYêu cầu của tôi: {request or DEFAULT_REQUEST}"


def parse_output(text: str) -> tuple[dict | None, str]:
    """Tách JSON và kiểm tra schema. Trả về (output, lỗi)."""
    try:
        return Analysis.model_validate(extract_json(text)).model_dump(), ""
    except (ValueError, ValidationError) as exc:
        return None, f"{type(exc).__name__}: {exc}"[:500]


def run(document: str, request: str, adapter: ModelAdapter) -> RunResult:
    system = load_instruction("v1")
    user_message = build_user_message(document, request)
    response = adapter.generate(system, user_message)
    output, error = parse_output(response.text)
    return RunResult(
        version="v1",
        output=output,
        raw_text=response.text,
        error=error,
        responses=[response],
        sent=[user_message],
        system_prompt=system,
    )


def replay(document: str, request: str, raw_text: str, adapter: ModelAdapter | None = None) -> RunResult:
    """Chấm lại từ câu trả lời thô đã lưu, không gọi model (dùng khi sửa bộ chấm/schema)."""
    output, error = parse_output(raw_text)
    return RunResult(
        version="v1",
        output=output,
        raw_text=raw_text,
        error=error,
        sent=[build_user_message(document, request)],
        system_prompt=load_instruction("v1"),
    )
