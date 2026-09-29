"""Groq chạy các model mã nguồn mở (Llama, Qwen...) qua API tương thích OpenAI."""
from __future__ import annotations

import os

from openai import OpenAI

from tasklens.adapters.openai_adapter import OpenAIAdapter

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class GroqAdapter(OpenAIAdapter):
    provider = "groq"
    # Gói miễn phí của Groq giới hạn 8.000 token/phút cho gpt-oss-120b: một request lớn hơn bị từ chối (413).
    # Đo thực tế: tài liệu 14.000 ký tự + system prompt V2 = 9.144 token (413). Giữ tài liệu ≤ 8.000 ký tự.
    max_input_chars = 8_000

    def __init__(self, model: str):
        self.model = model
        self._client = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url=GROQ_BASE_URL)
