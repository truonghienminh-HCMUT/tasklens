"""Lớp phòng thủ 1 (Input Sanitization), chạy bằng code TRƯỚC khi gửi bất cứ thứ gì cho model.

- làm sạch văn bản trích từ PDF (ký tự ghép, xuống dòng vỡ)
- chặn đầu vào rỗng / rác (V1: model tự bịa phân tích từ rác)
- che PII và thông tin xác thực (V1: gửi nguyên MSSV/SĐT/email ra dịch vụ ngoài, TC11)
- đánh dấu câu có dấu hiệu ra lệnh cho AI (V1: làm theo injection 3/3 lượt, TC08)
- phân loại yêu cầu ngoài phạm vi / rủi ro cao (V1: nhận chấm điểm hộ, TC07)
- rút gọn ngữ cảnh khi tài liệu vượt ngân sách của model (V1: lỗi 413, TC09)
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

# ---------------------------------------------------------------- làm sạch văn bản

_LIST_MARK = re.compile(r"^([-•●○■]|\d+(\.\d+)*[.)])")


def clean_text(text: str) -> str:
    """NFKC + ghép lại các dòng bị vỡ từng chữ (lỗi phổ biến khi trích PDF)."""
    text = unicodedata.normalize("NFKC", text or "")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)
    lines = [re.sub(r"[ \t]+", " ", line.strip()) for line in text.splitlines()]
    short = lambda s: 0 < len(s.split()) <= 2 and not _LIST_MARK.match(s)  # noqa: E731
    out: list[str] = []
    prev = ""  # dòng có chữ gần nhất (chưa ghép)
    for i, line in enumerate(lines):
        if not line:
            nxt = next((l for l in lines[i + 1:] if l), "")
            # dòng trống kẹp giữa các mẩu 1–2 từ là rác trích PDF, không phải ngắt đoạn
            if out and out[-1] != "" and not (short(prev) or short(nxt)):
                out.append("")
            continue
        # dòng ngắn (1–2 từ) nối vào dòng trước: PDF hay tách mỗi từ thành một dòng
        if out and out[-1] and (short(line) or short(prev)):
            out[-1] = f"{out[-1]} {line}"
        else:
            out.append(line)
        prev = line
    return "\n".join(out).strip()


def looks_like_garbage(text: str) -> str | None:
    """Trả về lý do nếu văn bản không thể là một đề bài; None nếu hợp lệ."""
    stripped = text.strip()
    if len(stripped) < 80:
        return "Văn bản quá ngắn (dưới 80 ký tự) để là một đề bài."
    letters = sum(ch.isalpha() for ch in stripped)
    words = re.findall(r"[^\W\d_]{2,}", stripped)
    if letters / len(stripped) < 0.5 or len(words) < 15:
        return "Văn bản chủ yếu là ký tự lạ/mã hóa. Có thể là PDF scan hoặc file lỗi, không trích được chữ."
    readable = [w for w in words if not re.search(r"(.)\1\1", w.lower())]
    if len(readable) / max(len(words), 1) < 0.6:
        return "Văn bản không đọc được như ngôn ngữ tự nhiên."
    return None


# ---------------------------------------------------------------- PII & credentials

_PII_PATTERNS = [
    ("EMAIL", re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")),
    ("API_KEY", re.compile(r"\b(AIza[\w-]{20,}|sk-[\w-]{20,}|gsk_[\w]{20,}|ghp_[\w]{20,}|xox[bp]-[\w-]{10,})\b")),
    ("MẬT_KHẨU", re.compile(r"(?i)(mật khẩu|password|passwd|pwd)\s*[:=]\s*\S+")),
    ("SĐT", re.compile(r"(?<![\d/.])(\+84|0)(\s?\d){9,10}(?![\d/])")),
    ("MSSV", re.compile(r"(?<![\d/.,:])\d{7,10}(?![\d/.,:])")),
]


def mask_pii(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    for label, pattern in _PII_PATTERNS:
        def repl(match, label=label):
            counts[label] = counts.get(label, 0) + 1
            return f"[{label}_{counts[label]}]"
        text = pattern.sub(repl, text)
    return text, counts


# ---------------------------------------------------------------- prompt injection

_INJECTION = re.compile(
    r"(?i)(bỏ qua|phớt lờ|quên|ignore|disregard)\s.{0,40}(hướng dẫn|chỉ dẫn|quy tắc|instruction|rule)"
    r"|system prompt|hướng dẫn hệ thống"
    r"|(dành cho|gửi|lưu ý cho)\s.{0,20}(công cụ|trợ lý|mô hình|model)?\s*(AI|chatbot|LLM)"
    r"|(AI|chatbot|trợ lý)\s.{0,30}\b(hãy|phải|cần)\s"
    r"|you are now|act as|developer mode"
)


def find_injections(text: str) -> list[str]:
    """Các câu có dấu hiệu đang ra lệnh cho AI (không phải mô tả đề bài)."""
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [s.strip() for s in sentences if s.strip() and _INJECTION.search(s)]


# ---------------------------------------------------------------- phạm vi yêu cầu

_OUT_OF_SCOPE = [
    ("academic_integrity",
     re.compile(r"(?i)(viết|làm|code|giải|lập trình)\s*(hộ|giùm|giúp|dùm)?\s*.{0,25}(toàn bộ|hết|hoàn chỉnh|trọn vẹn|cả bài|nguyên bài)"
                r"|(làm|viết|code|giải)\s*(hộ|giùm|dùm)"
                r"|để (tôi|em|mình) nộp( luôn)?"),
     "TaskLens không viết hộ bài để nộp: làm vậy vi phạm liêm chính học thuật và quy định sử dụng AI của môn học. "
     "Tôi có thể phân rã đề, liệt kê yêu cầu và giải thích từng phần để bạn tự thực hiện."),
    ("grading_decision",
     re.compile(r"(?i)(bao nhiêu|mấy)\s*điểm|chấm (điểm|bài)|(qua|rớt|trượt|đậu|pass|fail)\s*môn|dự đoán\s*điểm|điểm (của )?(tôi|em|mình)"),
     "TaskLens không dự đoán điểm số hay quyết định qua/rớt môn: đó là thẩm quyền của giảng viên. "
     "Bạn có thể hỏi trực tiếp giảng viên phụ trách; tôi có thể trích lại quy định chấm điểm và quy định nộp trễ trong đề để bạn tham khảo."),
]


def classify_request(request: str) -> tuple[str, str] | None:
    """(loại, lý do từ chối) nếu yêu cầu nằm ngoài phạm vi / rủi ro cao; None nếu hợp lệ."""
    for kind, pattern, reason in _OUT_OF_SCOPE:
        if pattern.search(request or ""):
            return kind, reason
    return None


# ---------------------------------------------------------------- quản lý ngữ cảnh

_RELEVANT = re.compile(
    r"(?i)hạn|deadline|nộp|submit|submission|yêu cầu|requirement|phải|must|shall|bắt buộc|required"
    r"|điểm|point|rubric|tiêu chí|criteria|grading|nhóm|team|group|cá nhân|individual|báo cáo|report"
    r"|sản phẩm|deliverable|demo|video|công nghệ|technology|framework|ngôn ngữ|language|định dạng|format"
    r"|trang|page|pdf|github|repository|lms|mốc|milestone|trễ|late|\d{1,2}/\d{1,2}/\d{4}"
)


@dataclass
class ContextSelection:
    text: str
    original_chars: int
    kept_chunks: int = 0
    total_chunks: int = 0
    trimmed: bool = False


def select_context(text: str, budget_chars: int) -> ContextSelection:
    """RAG rút gọn (Buổi 4): nếu tài liệu vượt ngân sách, giữ các đoạn liên quan nhất theo thứ tự gốc."""
    if len(text) <= budget_chars:
        return ContextSelection(text, len(text))
    chunks = [c.strip() for c in re.split(r"\n\s*\n", text) if c.strip()]
    # đoạn quá dài thì cắt tiếp theo câu để chấm điểm chi tiết hơn
    pieces: list[str] = []
    for chunk in chunks:
        if len(chunk) <= 1200:
            pieces.append(chunk)
        else:
            buf = ""
            for sentence in re.split(r"(?<=[.;!?])\s+", chunk):
                if len(buf) + len(sentence) > 1200 and buf:
                    pieces.append(buf)
                    buf = ""
                buf = f"{buf} {sentence}".strip()
            if buf:
                pieces.append(buf)
    scored = sorted(range(len(pieces)), key=lambda i: -len(_RELEVANT.findall(pieces[i])) / (len(pieces[i]) ** 0.5))
    keep, used = set(), 0
    for i in scored:
        if len(_RELEVANT.findall(pieces[i])) == 0:
            break
        if used + len(pieces[i]) > budget_chars:
            continue
        keep.add(i)
        used += len(pieces[i])
    selected = "\n\n".join(pieces[i] for i in sorted(keep))
    return ContextSelection(selected, len(text), len(keep), len(pieces), True)


# ---------------------------------------------------------------- tổng hợp


@dataclass
class SanitizeReport:
    text: str
    garbage_reason: str | None = None
    pii_counts: dict[str, int] = field(default_factory=dict)
    injections: list[str] = field(default_factory=list)
    out_of_scope: tuple[str, str] | None = None
    context: ContextSelection | None = None

    def notes(self) -> list[str]:
        notes = []
        if self.pii_counts:
            detail = ", ".join(f"{n} {k}" for k, n in self.pii_counts.items())
            notes.append(f"Đã che thông tin cá nhân/xác thực trước khi gửi cho model: {detail}.")
        if self.injections:
            notes.append(f"Phát hiện {len(self.injections)} câu có dấu hiệu ra lệnh cho AI; đã coi là dữ liệu, không làm theo.")
        if self.context and self.context.trimmed:
            notes.append(
                f"Tài liệu dài {self.context.original_chars:,} ký tự vượt ngân sách của model: đã giữ "
                f"{self.context.kept_chunks}/{self.context.total_chunks} đoạn liên quan ({len(self.context.text):,} ký tự). "
                "Hãy kiểm tra phần bị lược nếu cần."
            )
        return notes


def sanitize(document: str, request: str, budget_chars: int) -> SanitizeReport:
    text = clean_text(document)
    report = SanitizeReport(text=text, garbage_reason=looks_like_garbage(text), out_of_scope=classify_request(request))
    if report.garbage_reason:
        return report
    masked, report.pii_counts = mask_pii(text)
    report.injections = find_injections(masked)  # tìm trên bản đã che để cảnh báo gửi đi không lộ PII
    report.context = select_context(masked, budget_chars)
    report.text = report.context.text
    return report
