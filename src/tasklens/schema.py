"""Hợp đồng output chung cho mọi phiên bản pipeline (V1, V2) và mọi model.

Giữ một schema duy nhất để bộ Evals chấm V1 và V2 trên cùng một thước đo.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Status = Literal["OK", "NEED_INFO", "REFUSED", "INVALID_INPUT"]


class _Lenient(BaseModel):
    """`null` ở trường tùy chọn nghĩa là "không áp dụng": chuyển thành chuỗi/danh sách rỗng.

    Trường bắt buộc (status, content, task...) vẫn phải có giá trị thật.
    """

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _null_means_empty(cls, data):
        if not isinstance(data, dict):
            return data
        cleaned = dict(data)
        for name, field in cls.model_fields.items():
            if cleaned.get(name, 0) is None and not field.is_required():
                default = field.get_default(call_default_factory=True)
                if default is not None:
                    cleaned[name] = default
        return cleaned


class Item(_Lenient):
    model_config = ConfigDict(extra="ignore")

    content: str = Field(description="Nội dung đã diễn giải ngắn gọn")
    quote: str = Field(default="", description="Trích dẫn NGUYÊN VĂN từ đề bài làm căn cứ")


class Deadline(_Lenient):
    model_config = ConfigDict(extra="ignore")

    value: str = Field(description="Hạn nộp chính thức, dạng dd/mm/yyyy (kèm giờ nếu có)")
    quote: str = Field(default="", description="Câu nguyên văn trong đề chứa hạn nộp")


class Contradiction(_Lenient):
    model_config = ConfigDict(extra="ignore")

    description: str
    quote_a: str = ""
    quote_b: str = ""


class PlanStep(_Lenient):
    model_config = ConfigDict(extra="ignore")

    step: int
    task: str
    due: str = Field(default="", description="Mốc hoàn thành, dd/mm/yyyy")


class Analysis(_Lenient):
    model_config = ConfigDict(extra="ignore")

    status: Status
    summary: str = ""
    deadline: Deadline | None = None
    requirements: list[Item] = Field(default_factory=list)
    constraints: list[Item] = Field(default_factory=list)
    deliverables: list[Item] = Field(default_factory=list)
    grading_criteria: list[Item] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)
    ambiguities: list[Item] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    invalid_data: list[Item] = Field(default_factory=list)
    injection_flags: list[Item] = Field(default_factory=list)
    refusal_reason: str = ""
    plan: list[PlanStep] = Field(default_factory=list)


def json_schema() -> dict:
    """JSON Schema của Analysis, đã inline mọi $ref (một số nhà cung cấp không hỗ trợ $defs)."""
    raw = Analysis.model_json_schema()
    defs = raw.pop("$defs", {})

    def inline(node, is_properties_map=False):
        if isinstance(node, dict):
            if "$ref" in node:
                return inline(defs[node["$ref"].split("/")[-1]])
            if is_properties_map:  # khóa ở đây là TÊN TRƯỜNG (có trường tên "description"): giữ nguyên
                return {k: inline(v) for k, v in node.items()}
            return {k: inline(v, is_properties_map=(k == "properties")) for k, v in node.items()
                    if k not in ("title", "description", "default")}
        if isinstance(node, list):
            return [inline(v) for v in node]
        return node

    return inline(raw)


OUTPUT_EXAMPLE = """{
  "status": "OK | NEED_INFO | REFUSED | INVALID_INPUT",
  "summary": "Tóm tắt đề bài trong 2-3 câu",
  "deadline": {"value": "dd/mm/yyyy hh:mm", "quote": "câu nguyên văn chứa hạn nộp"} hoặc null,
  "requirements":     [{"content": "...", "quote": "trích nguyên văn"}],
  "constraints":      [{"content": "...", "quote": "..."}],
  "deliverables":     [{"content": "...", "quote": "..."}],
  "grading_criteria": [{"content": "...", "quote": "..."}],
  "missing_info": ["thông tin còn thiếu"],
  "questions": ["câu hỏi cần người dùng trả lời"],
  "ambiguities":    [{"content": "điểm mơ hồ", "quote": "..."}],
  "contradictions": [{"description": "...", "quote_a": "...", "quote_b": "..."}],
  "invalid_data":   [{"content": "dữ liệu phi lý", "quote": "..."}],
  "injection_flags": [{"content": "đoạn đang cố ra lệnh cho AI", "quote": "..."}],
  "refusal_reason": "lý do từ chối (nếu status = REFUSED)",
  "plan": [{"step": 1, "task": "...", "due": "dd/mm/yyyy"}]
}"""
