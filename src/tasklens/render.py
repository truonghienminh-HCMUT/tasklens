"""Chuyển kết quả phân tích thành Markdown để xuất file (bước ACTION: chỉ xuất, không gửi)."""
from __future__ import annotations

STATUS_LABEL = {
    "OK": "Phân tích xong",
    "NEED_INFO": "Cần bạn bổ sung thông tin",
    "REFUSED": "Từ chối yêu cầu",
    "INVALID_INPUT": "Đầu vào không phải đề bài",
}

SECTIONS = [
    ("requirements", "Yêu cầu chức năng / nội dung"),
    ("constraints", "Ràng buộc"),
    ("deliverables", "Sản phẩm phải nộp"),
    ("grading_criteria", "Tiêu chí chấm điểm"),
    ("ambiguities", "Điểm mơ hồ"),
    ("invalid_data", "Dữ liệu bất thường"),
    ("injection_flags", "Đoạn văn đáng ngờ (đang cố ra lệnh cho AI)"),
]


def _items(items: list[dict]) -> list[str]:
    lines = []
    for item in items:
        quote = f'\n  > "{item["quote"]}"' if item.get("quote") else ""
        lines.append(f"- {item.get('content', '')}{quote}")
    return lines


def to_markdown(out: dict, meta: dict | None = None) -> str:
    meta = meta or {}
    lines = [
        "# Phân tích đề bài — TaskLens",
        "",
        f"**Trạng thái:** {out['status']} ({STATUS_LABEL.get(out['status'], '')})",
    ]
    if meta:
        lines.append(f"**Phiên bản / model:** {meta.get('version', '')} · {meta.get('model', '')}")
    lines += ["", "> Kết quả do AI tạo và đã được người dùng xác nhận đối chiếu với đề gốc. "
              "Đề gốc và thông báo của giảng viên luôn là căn cứ cuối cùng.", ""]
    if out.get("summary"):
        lines += ["## Tóm tắt", out["summary"], ""]
    if out.get("refusal_reason"):
        lines += ["## Lý do từ chối", out["refusal_reason"], ""]
    deadline = out.get("deadline")
    lines += ["## Hạn nộp", f"{deadline['value']}" + (f'\n> "{deadline["quote"]}"' if deadline.get("quote") else "") if deadline else "Chưa xác định", ""]
    for key, title in SECTIONS:
        if out.get(key):
            lines += [f"## {title}", *_items(out[key]), ""]
    if out.get("contradictions"):
        lines.append("## Mâu thuẫn trong đề")
        for c in out["contradictions"]:
            lines.append(f"- {c.get('description', '')}")
            for q in (c.get("quote_a"), c.get("quote_b")):
                if q:
                    lines.append(f'  > "{q}"')
        lines.append("")
    if out.get("missing_info"):
        lines += ["## Thông tin còn thiếu", *[f"- {m}" for m in out["missing_info"]], ""]
    if out.get("questions"):
        lines += ["## Câu hỏi cần làm rõ", *[f"- {q}" for q in out["questions"]], ""]
    if out.get("plan"):
        lines += ["## Kế hoạch thực hiện", "", "| Bước | Công việc | Mốc hoàn thành |", "|---|---|---|"]
        lines += [f"| {s.get('step', '')} | {s.get('task', '')} | {s.get('due', '')} |" for s in out["plan"]]
        lines.append("")
    return "\n".join(lines)
