"""Lớp phòng thủ 4 (Output Validation Gate), chạy bằng code SAU khi model trả lời.

Nguyên tắc (Buổi 12, slide 22): "AI nói đã kiểm tra" không phải bằng chứng. Mọi khẳng định
kiểm tra được bằng code thì code kiểm tra; không đạt thì hạ trạng thái hoặc gỡ bỏ, và báo cho người dùng.
Module này độc lập với bộ chấm trong evals/ (không import lẫn nhau).
"""
from __future__ import annotations

import re
import unicodedata
from datetime import date

PLACEHOLDER = re.compile(r"\[(EMAIL|SĐT|MSSV|API_KEY|MẬT_KHẨU)_\d+\]")
ITEM_KEYS = ("requirements", "constraints", "deliverables", "grading_criteria", "ambiguities", "invalid_data", "injection_flags")
_DATE = re.compile(r"(?<!\d)(\d{1,2})\s*[/.-]\s*(\d{1,2})\s*[/.-]\s*(\d{4})(?!\d)")
_TOKEN = re.compile(r"\b[A-Z]{2,}[-_]\d{2,}\b")


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").lower()
    for a, b in (("—", "-"), ("–", "-"), ("“", '"'), ("”", '"'), ("‘", "'"), ("’", "'")):
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip()


def is_grounded(quote: str, source_norm: str) -> bool:
    parts = [p.strip(" \"'.,;:-()[]") for p in re.split(r"\.\.\.|…", _norm(PLACEHOLDER.sub("…", quote)))]
    parts = [p for p in parts if p]
    return bool(parts) and all(p in source_norm for p in parts)


def parse_date(text: str) -> tuple[date | None, str | None]:
    """(ngày hợp lệ, chuỗi ngày gốc). Ngày không có thật trên lịch → (None, chuỗi)."""
    m = _DATE.search(text or "")
    if not m:
        return None, None
    d, mo, y = (int(x) for x in m.groups())
    try:
        return date(y, mo, d), m.group(0)
    except ValueError:
        return None, m.group(0)


_MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"], 1)}
_MONTHS.update({m[:3]: i for m, i in list(_MONTHS.items())})
_EN_MDY = re.compile(r"\b(" + "|".join(_MONTHS) + r")\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})", re.I)
_EN_DMY = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(" + "|".join(_MONTHS) + r")\.?,?\s+(\d{4})", re.I)
_VI = re.compile(r"(\d{1,2})\s+tháng\s+(\d{1,2})(?:\s*(?:năm|,)?\s*(\d{4}))?", re.I)
_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")


def dates_in(text: str) -> set[date]:
    """Mọi ngày HỢP LỆ được nhắc tới trong văn bản, ở các định dạng dd/mm/yyyy, ISO, tiếng Anh, tiếng Việt."""
    found: set[date] = set()

    def add(y, m, d):
        try:
            found.add(date(int(y), int(m), int(d)))
        except (TypeError, ValueError):
            pass

    for d, m, y in _DATE.findall(text):
        add(y, m, d)
    for y, m, d in _ISO.findall(text):
        add(y, m, d)
    month = lambda name: _MONTHS.get(name.lower().rstrip("."))  # noqa: E731
    for mon, d, y in _EN_MDY.findall(text):
        add(y, month(mon), d)
    for d, mon, y in _EN_DMY.findall(text):
        add(y, month(mon), d)
    for d, m, y in _VI.findall(text):
        if y:
            add(y, m, d)
    return found


def _answer_fields(out: dict):
    """(getter, setter) cho các trường là 'lời của hệ thống' (không gồm trích dẫn)."""
    yield lambda: out.get("summary", ""), lambda v: out.__setitem__("summary", v)
    yield lambda: out.get("refusal_reason", ""), lambda v: out.__setitem__("refusal_reason", v)
    for key in ("requirements", "constraints", "deliverables", "grading_criteria"):
        for item in out.get(key) or []:
            yield (lambda i=item: i.get("content", "")), (lambda v, i=item: i.__setitem__("content", v))
    for step in out.get("plan") or []:
        yield (lambda s=step: s.get("task", "")), (lambda v, s=step: s.__setitem__("task", v))


def validate(out: dict, source: str, *, system_prompt: str, injections: list[str], known_deadline: str = "") -> list[str]:
    """Sửa `out` tại chỗ theo các luật kiểm chứng; trả về ghi chú cho người dùng."""
    notes: list[str] = []
    source_norm = _norm(source)

    # 1) Trích dẫn phải có thật trong đề. PII đã che hiển thị thành '…'.
    removed = 0
    for key in ITEM_KEYS:
        for item in out.get(key) or []:
            quote = PLACEHOLDER.sub("…", item.get("quote", ""))
            if quote and not is_grounded(quote, source_norm):
                item["quote"] = ""
                item["content"] = f"{item.get('content', '')} (chưa tìm thấy câu nguyên văn trong đề, hãy tự kiểm tra)"
                removed += 1
            else:
                item["quote"] = quote
    for c in out.get("contradictions") or []:
        for k in ("quote_a", "quote_b"):
            quote = PLACEHOLDER.sub("…", c.get(k, ""))
            if quote and not is_grounded(quote, source_norm):
                c[k] = ""
                removed += 1
            else:
                c[k] = quote
    if removed:
        notes.append(f"Đã gỡ {removed} trích dẫn không tìm thấy nguyên văn trong đề (có thể do AI diễn giải/bịa).")

    # 2) Hạn nộp: phải là ngày có thật, có căn cứ trong đề (hoặc do người dùng cung cấp).
    user_date, _ = parse_date(known_deadline)
    deadline = out.get("deadline")
    if user_date:
        out["deadline"] = {"value": known_deadline.strip(), "quote": ""}
        notes.append("Hạn nộp lấy theo thông tin bạn cung cấp.")
    elif deadline:
        when, raw = parse_date(deadline.get("value", ""))
        quote = PLACEHOLDER.sub("…", deadline.get("quote", ""))
        if raw and when is None:
            out.setdefault("invalid_data", []).append(
                {"content": f"Hạn nộp '{deadline.get('value')}' không phải một ngày có thật trên lịch.", "quote": quote})
            out["deadline"] = None
            notes.append(f"Hạn nộp '{raw}' không tồn tại trên lịch: không dùng để lập kế hoạch.")
        elif when is None:
            out["deadline"] = None
        elif when not in dates_in(source):
            out["deadline"] = None
            notes.append(f"Hạn nộp {raw} do AI đưa ra không xuất hiện trong đề: đã bỏ, cần bạn xác nhận.")
        else:
            deadline["quote"] = quote if quote and is_grounded(quote, source_norm) else ""

    # 3) Cổng lập kế hoạch: chỉ có kế hoạch khi trạng thái OK và có hạn nộp hợp lệ.
    if out.get("status") == "OK" and not out.get("deadline"):
        out["status"] = "NEED_INFO"
        out.setdefault("missing_info", []).append("Hạn nộp chính thức của bài (không tìm thấy hoặc không hợp lệ).")
        out.setdefault("questions", []).append("Hạn nộp chính thức của bài là ngày nào (theo lớp của bạn)?")
    if out.get("status") != "OK" and out.get("plan"):
        out["plan"] = []
        notes.append("Chưa đủ dữ kiện nên KHÔNG lập kế hoạch (tránh lập kế hoạch trên giả định).")
    limit, _ = parse_date((out.get("deadline") or {}).get("value", ""))
    if limit:
        late = [s for s in out.get("plan") or [] if (parse_date(s.get("due", ""))[0] or limit) > limit]
        if late:
            notes.append(f"Cảnh báo: {len(late)} mốc kế hoạch nằm sau hạn nộp, cần điều chỉnh.")

    # 4) Injection: đoạn nghi vấn phát hiện bằng code luôn được gắn cờ; mã/chuỗi mà nó yêu cầu chèn bị gỡ khỏi câu trả lời.
    flagged = {_norm(i.get("quote", "")) for i in out.get("injection_flags") or []}
    for sentence in injections:
        if not any(_norm(sentence)[:60] in f or f[:60] in _norm(sentence) for f in flagged if f):
            out.setdefault("injection_flags", []).append(
                {"content": "Câu có dấu hiệu ra lệnh cho AI (hệ thống phát hiện), đã coi là dữ liệu và không làm theo.", "quote": sentence})
    payloads = {t for s in injections for t in _TOKEN.findall(s)} | {q for s in injections for q in re.findall(r'"([^"]{3,80})"', s)}
    scrubbed = 0
    for get, set_ in _answer_fields(out):
        value = get()
        for p in payloads:
            if p and p in value:
                value = value.replace(p, "").strip(" .:,-")
                scrubbed += 1
        set_(value)
    if scrubbed:
        notes.append("Đã gỡ nội dung mà đoạn văn nghi vấn yêu cầu chèn vào câu trả lời.")

    # 5) Không để lộ system prompt.
    prompt_lines = [_norm(l) for l in system_prompt.splitlines() if len(l.strip()) >= 40]
    leaked = 0
    for get, set_ in _answer_fields(out):
        value_norm = _norm(get())
        if any(l in value_norm for l in prompt_lines):
            set_("[Đã chặn: nội dung trùng với hướng dẫn hệ thống]")
            leaked += 1
    if leaked:
        notes.append("Đã chặn nội dung trùng với hướng dẫn hệ thống (chống lộ system prompt).")

    # 6) Nhất quán trạng thái.
    if out.get("status") == "REFUSED" and not out.get("refusal_reason"):
        out["refusal_reason"] = "Yêu cầu nằm ngoài phạm vi hỗ trợ của TaskLens."
    if out.get("status") in ("REFUSED", "INVALID_INPUT"):
        out["plan"] = []
    if out.get("status") == "INVALID_INPUT":
        for key in ("requirements", "constraints", "deliverables", "grading_criteria"):
            out[key] = []
        out["deadline"] = None
    return notes
