"""TaskLens V2: AI Workflow Level 2 có cổng kiểm soát bằng code ở cả đầu vào lẫn đầu ra.

    SANITIZE (code) → PRE-CHECK (code) → MODEL → VALIDATE (code, thử lại 1 lần nếu JSON hỏng) → [HUMAN ở UI] → xuất file
                                                                   + AUDIT LOG (không lưu nội dung đề)
Mỗi bước gắn với một lỗi thật của V1, xem evals/failure-analysis.md.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime

from tasklens.adapters import ModelAdapter
from tasklens.config import LOGS_DIR, load_instruction
from tasklens.pipeline_v1 import DEFAULT_REQUEST, RunResult, parse_output
from tasklens.sanitize import mask_pii, sanitize
from tasklens.schema import Analysis, json_schema
from tasklens.validate import validate

VERSION = "v2"
# V1 để mặc định của nhà cung cấp và bị cắt ở 3.072 token (gpt-oss trên Groq). V2 đặt giới hạn rõ ràng.
MAX_OUTPUT_TOKENS = 8192
# Phân rã một đề là tác vụ nhỏ: yêu cầu model suy luận ít (tiết kiệm token, giảm nguy cơ bị cắt).
EFFORT = "low"


def build_user_message(text: str, request: str, known_deadline: str, injections: list[str]) -> str:
    warnings = "\n".join(f"- {s}" for s in injections) or "(không có)"
    extra = f"Hạn nộp sinh viên cung cấp: {known_deadline}" if known_deadline.strip() else "(không có)"
    return (
        f"<yeu_cau_nguoi_dung>\n{request or DEFAULT_REQUEST}\n</yeu_cau_nguoi_dung>\n\n"
        f"<thong_tin_bo_sung>\n{extra}\n</thong_tin_bo_sung>\n\n"
        f"<canh_bao_he_thong>\n{warnings}\n</canh_bao_he_thong>\n\n"
        f"<de_bai>\n{text}\n</de_bai>"
    )


def _offline(status: str, reason: str) -> dict:
    """Kết quả do code quyết định, không gọi model (đầu vào rác / yêu cầu ngoài phạm vi)."""
    out = Analysis(status=status).model_dump()
    if status == "REFUSED":
        out["refusal_reason"] = reason
    else:
        out["summary"] = reason
        out["missing_info"] = ["Một đề bài có nội dung đọc được (PDF có lớp chữ, DOCX hoặc văn bản dán trực tiếp)."]
    return out


def _audit(result: RunResult, adapter: ModelAdapter, document: str) -> None:
    """Lớp 6 (Audit Logging): chỉ ghi siêu dữ liệu, không ghi nội dung đề hay câu trả lời."""
    try:
        LOGS_DIR.mkdir(exist_ok=True)
        entry = {
            "time": datetime.now().isoformat(timespec="seconds"),
            "version": VERSION,
            "model": f"{adapter.provider}:{adapter.model}",
            "status": (result.output or {}).get("status", "ERROR"),
            "model_calls": len(result.responses),
            "input_tokens": result.input_tokens,
            "output_tokens": result.output_tokens,
            "latency_s": round(result.latency_s, 2),
            "doc_chars": len(document),
            "doc_sha256": hashlib.sha256(document.encode("utf-8")).hexdigest()[:12],
            "notes": len(result.notes),
        }
        with open(LOGS_DIR / "audit.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # log hỏng không được làm hỏng kết quả cho người dùng


def _finish(result: RunResult, report, known_deadline: str) -> RunResult:
    if result.output is not None:
        result.notes += validate(result.output, report.text, system_prompt=result.system_prompt,
                                 injections=report.injections, known_deadline=known_deadline)
    return result


def run(document: str, request: str, adapter: ModelAdapter, known_deadline: str = "") -> RunResult:
    system = load_instruction(VERSION)
    request_masked, _ = mask_pii(request or "")
    report = sanitize(document, request_masked, adapter.max_input_chars)
    result = RunResult(version=VERSION, output=None, raw_text="", system_prompt=system, notes=report.notes())

    # PRE-CHECK bằng code: không tốn lượt gọi model, không phụ thuộc model có "nghe lời" hay không.
    if report.garbage_reason:
        result.output = _offline("INVALID_INPUT", report.garbage_reason)
    elif report.out_of_scope:
        result.output = _offline("REFUSED", report.out_of_scope[1])
        result.notes.append("Yêu cầu bị chặn ở cổng kiểm tra phạm vi, không gửi tới model.")
    else:
        message = build_user_message(report.text, request_masked, known_deadline, report.injections)
        schema = json_schema()
        for attempt in (1, 2):
            response = adapter.generate(system, message, json_schema=schema,
                                        max_output_tokens=MAX_OUTPUT_TOKENS, effort=EFFORT)
            result.responses.append(response)
            result.sent.append(message)
            result.raw_text = response.text
            result.output, result.error = parse_output(response.text)
            if result.output is not None:
                break
            if attempt == 1:  # thử lại đúng 1 lần, kèm lỗi cụ thể để model tự sửa
                message += (f"\n\n<loi_lan_truoc>\n{result.error[:300]}\n(stop_reason: {response.stop_reason})\n</loi_lan_truoc>\n"
                            "Câu trả lời trước không phải JSON hợp lệ theo cấu trúc. Trả lời lại DUY NHẤT JSON hợp lệ, "
                            "ngắn gọn hơn (summary ≤ 2 câu, mỗi danh sách ≤ 6 mục).")
                result.notes.append("Lần gọi đầu trả JSON không hợp lệ: đã tự động thử lại 1 lần.")
        _finish(result, report, known_deadline)
    _audit(result, adapter, document)
    return result


def replay(document: str, request: str, raw_text: str, adapter: ModelAdapter | None = None,
           known_deadline: str = "") -> RunResult:
    """Chấm lại từ câu trả lời thô đã lưu: chạy lại các bước code (sanitize, validate), không gọi model."""
    system = load_instruction(VERSION)
    request_masked, _ = mask_pii(request or "")
    report = sanitize(document, request_masked, adapter.max_input_chars if adapter else 10**9)
    result = RunResult(version=VERSION, output=None, raw_text=raw_text, system_prompt=system, notes=report.notes())
    if report.garbage_reason:
        result.output = _offline("INVALID_INPUT", report.garbage_reason)
    elif report.out_of_scope:
        result.output = _offline("REFUSED", report.out_of_scope[1])
    else:
        result.sent = [build_user_message(report.text, request_masked, known_deadline, report.injections)]
        result.output, result.error = parse_output(raw_text)
        _finish(result, report, known_deadline)
    return result
