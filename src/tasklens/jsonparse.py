"""Tách khối JSON từ câu trả lời của model (có thể bọc trong ```json ... ``` hoặc kèm lời chào)."""
from __future__ import annotations

import json
import re

_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def extract_json(text: str) -> dict:
    """Trả về dict; ném ValueError nếu không tìm thấy JSON object hợp lệ."""
    text = (text or "").strip()
    candidates = [text]
    candidates += _FENCE.findall(text)
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start : end + 1])
    for candidate in candidates:
        try:
            value = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise ValueError("Không tìm thấy JSON object hợp lệ trong câu trả lời của model")
