"""Nạp cấu hình từ file .env ở thư mục gốc dự án. Không bao giờ ghi key ra log."""
from __future__ import annotations

import os
import re
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
INSTRUCTIONS_DIR = ROOT / "instructions"
LOGS_DIR = ROOT / "logs"

load_dotenv(ROOT / ".env", override=False)

DEFAULT_MODELS = {
    "gemini": os.getenv("GEMINI_MODEL", "gemma-4-26b-a4b-it"),
    "groq": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    "openai": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
    "anthropic": os.getenv("ANTHROPIC_MODEL", "claude-opus-5"),
    "mock": "mock",
}

KEY_ENV = {
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}


def has_key(provider: str) -> bool:
    env = KEY_ENV.get(provider)
    return provider == "mock" or bool(env and os.getenv(env))


def available_providers() -> list[str]:
    return [p for p in ("gemini", "groq", "openai", "anthropic") if has_key(p)]


def load_instruction(version: str) -> str:
    """Đọc system prompt của phiên bản: phần nằm dưới dòng chỉ chứa đúng '---PROMPT---'."""
    text = (INSTRUCTIONS_DIR / f"system-prompt-{version}.md").read_text(encoding="utf-8")
    parts = re.split(r"^---PROMPT---[ \t]*$", text, maxsplit=1, flags=re.MULTILINE)
    return parts[1].strip() if len(parts) == 2 else text.strip()
