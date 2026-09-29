"""Adapter giả, chỉ dùng để kiểm tra đường ống (UI, runner, grader) khi chưa có API key.

Kết quả từ mock KHÔNG được đưa vào báo cáo kiểm thử.
"""
from __future__ import annotations

import json

from tasklens.adapters import ModelResponse

_CANNED = {
    "status": "OK",
    "summary": "[MOCK] Đây là output giả để kiểm tra đường ống, không phải kết quả của model.",
    "deadline": None,
    "requirements": [{"content": "[MOCK] yêu cầu", "quote": ""}],
    "constraints": [],
    "deliverables": [],
    "grading_criteria": [],
    "missing_info": [],
    "questions": [],
    "ambiguities": [],
    "contradictions": [],
    "invalid_data": [],
    "injection_flags": [],
    "refusal_reason": "",
    "plan": [{"step": 1, "task": "[MOCK] bước 1", "due": ""}],
}


class MockAdapter:
    provider = "mock"
    model = "mock"
    max_input_chars = 200_000

    def generate(self, system: str, user: str, json_schema: dict | None = None,
                 max_output_tokens: int | None = None, effort: str | None = None) -> ModelResponse:
        return ModelResponse(
            text=json.dumps(_CANNED, ensure_ascii=False),
            provider=self.provider,
            model=self.model,
            latency_s=0.0,
            input_tokens=0,
            output_tokens=0,
            stop_reason="mock",
        )
