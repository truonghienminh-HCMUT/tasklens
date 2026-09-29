"""Kiểm tra file .env: key nào đã có, key có dùng được không, model cấu hình có gọi được không.
Gọi API liệt kê model và một lời gọi thử rất ngắn (vài token); không in key ra màn hình.

    python scripts/check_setup.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tasklens.adapters import get_adapter  # noqa: E402
from tasklens.config import DEFAULT_MODELS, KEY_ENV, ROOT, has_key  # noqa: E402


def list_models(provider: str) -> list[str]:
    if provider == "gemini":
        from google import genai

        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        return [m.name.removeprefix("models/") for m in client.models.list()]
    if provider in ("openai", "groq"):
        from openai import OpenAI

        from tasklens.adapters.groq_adapter import GROQ_BASE_URL

        base_url = GROQ_BASE_URL if provider == "groq" else None
        return [m.id for m in OpenAI(api_key=os.environ[KEY_ENV[provider]], base_url=base_url).models.list()]
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"],
                                 base_url=os.getenv("TASKLENS_ANTHROPIC_BASE_URL", "https://api.anthropic.com"))
    return [m.id for m in client.models.list()]


def main() -> None:
    print(f"File .env: {'có' if (ROOT / '.env').exists() else 'CHƯA CÓ (sao chép .env.example thành .env)'}")
    ready = 0
    for provider, env in KEY_ENV.items():
        if not has_key(provider):
            print(f"- {provider:9s}: chưa điền {env}")
            continue
        try:
            models = list_models(provider)
        except Exception as exc:
            print(f"- {provider:9s}: KEY LỖI → {type(exc).__name__}: {str(exc)[:150]}")
            continue
        configured = DEFAULT_MODELS[provider]
        ok = in_list = configured in models
        if ok:
            # Có trong danh sách chưa chắc gọi được (model ngừng cấp cho tài khoản mới, quá tải...): gọi thử 1 câu.
            try:
                reply = get_adapter(provider).generate("Trả lời ngắn gọn.", "Trả lời đúng một từ: OK")
                status = f"gọi thử OK ({reply.latency_s:.1f}s) ✔"
            except Exception as exc:
                ok, status = False, f"có trong danh sách nhưng gọi thử LỖI ✘ → {str(exc)[:120]}"
        else:
            status = "KHÔNG tìm thấy ✘"
        ready += ok
        print(f"- {provider:9s}: key hợp lệ; model '{configured}' {status}")
        if not in_list:
            hints = [m for m in models if any(k in m for k in ("flash", "pro", "gpt", "claude", "mini", "llama", "qwen"))]
            print(f"    Gợi ý model: {', '.join(sorted(hints)[:15])}")
    print(f"\nSẵn sàng: {ready} nhà cung cấp. Model Swap Test cần ít nhất 2.")


if __name__ == "__main__":
    main()
