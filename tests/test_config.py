"""System prompt gửi cho model phải đúng nguyên văn phần dưới dòng ---PROMPT--- (không dính phần mô tả)."""
from tasklens.config import load_instruction


def test_v1_prompt_is_exactly_the_prompt_section():
    prompt = load_instruction("v1")
    assert prompt.startswith("# ROLE")
    assert "---PROMPT---" not in prompt
    assert "nguyên văn system prompt" not in prompt
