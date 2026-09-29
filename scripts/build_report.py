"""Gộp 12 sản phẩm thành MỘT báo cáo PDF để nộp qua bất kỳ kênh nào (LMS, email, Google Form...).

    python scripts/build_report.py
→ dist/BaoCao_CuoiKhoa_TaskLens.html và .pdf (xuất PDF bằng Microsoft Edge ở chế độ headless)
"""
from __future__ import annotations

import csv
import html
import re
import subprocess
import tempfile
import time
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")

CSS = """
@page { size: A4; margin: 16mm 14mm; }
body { font-family: "Segoe UI", Arial, sans-serif; font-size: 10.5pt; line-height: 1.5; color: #0b0b0b; }
h1 { font-size: 18pt; border-bottom: 2px solid #2a78d6; padding-bottom: 4px; margin-top: 0; }
h2 { font-size: 13.5pt; color: #184f95; margin-top: 18px; }
h3 { font-size: 11.5pt; margin-top: 14px; }
section { page-break-before: always; }
section.cover { page-break-before: auto; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9pt; }
th, td { border: 1px solid #c3c2b7; padding: 4px 6px; vertical-align: top; text-align: left; }
th { background: #f0efec; }
code { font-family: Consolas, monospace; font-size: 9pt; background: #f4f4f2; padding: 0 2px; }
pre { background: #f4f4f2; padding: 8px; white-space: pre-wrap; font-size: 8.5pt; border-left: 3px solid #2a78d6; }
blockquote { color: #52514e; border-left: 3px solid #c3c2b7; margin: 6px 0; padding-left: 10px; }
img { max-width: 100%; }
.label { display: inline-block; background: #2a78d6; color: #fff; padding: 1px 8px; border-radius: 4px; font-size: 9pt; }
.muted { color: #52514e; font-size: 9pt; }
"""


_ITEM = re.compile(r"^(\s*)([-*]|\d+\.)\s+")


def _github_style(text: str) -> str:
    """python-markdown khắt khe hơn GitHub: cần dòng trống trước danh sách và thụt 4 dấu cách cho danh sách con."""
    out, prev, in_code = [], "", False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_code = not in_code
        m = None if in_code else _ITEM.match(line)
        if m:
            indent = len(m.group(1))
            if 0 < indent < 4:
                line = "    " + line.lstrip()
            elif indent == 0 and prev.strip() and not _ITEM.match(prev) and not prev.startswith("|"):
                out.append("")
        out.append(line)
        prev = line
    return "\n".join(out)


def md(path: Path) -> str:
    text = _github_style(path.read_text(encoding="utf-8"))
    # ảnh tương đối → đường dẫn tuyệt đối để trình duyệt tìm thấy khi in PDF
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
                  lambda m: f"![{m.group(1)}]({(path.parent / m.group(2)).resolve().as_uri()})", text)
    return markdown.markdown(text, extensions=["tables", "fenced_code", "nl2br", "sane_lists"])


def csv_table(path: Path, columns: list[str], title: str = "") -> str:
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    head = "".join(f"<th>{html.escape(c)}</th>" for c in columns)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(r.get(c, ''))}</td>" for c in columns) + "</tr>" for r in rows)
    return (f"<h3>{html.escape(title)}</h3>" if title else "") + f"<table><tr>{head}</tr>{body}</table>"


def section(label: str, body: str, cls: str = "") -> str:
    return f'<section class="{cls}"><p><span class="label">{html.escape(label)}</span></p>{body}</section>'


def main() -> None:
    results = ROOT / "evals" / "results"
    parts = [section("Hồ sơ nộp bài", md(ROOT / "SUBMISSION.md"), "cover")]
    parts.append(section("Sản phẩm #1", md(ROOT / "docs" / "01-problem-statement.md")))
    parts.append(section("Sản phẩm #2", md(ROOT / "docs" / "system-design.md")
                         + f'<h2>Sơ đồ workflow</h2><img src="{(ROOT / "docs" / "workflow-diagram.png").as_uri()}">'))
    parts.append(section("Sản phẩm #3", md(ROOT / "instructions" / "system-prompt-v1.md")
                         + "<p class='muted'>Mã nguồn: src/tasklens/pipeline_v1.py</p>"))
    parts.append(section("Sản phẩm #4", "<h1>4. Bộ kiểm thử thử lửa (Eval Suite)</h1>"
                         + csv_table(ROOT / "evals" / "test-cases.csv", ["id", "scenario", "user_request", "expected_behavior", "checks"],
                                     "Bộ chính: 11 ca (10 tình huống slide 17 + 1 ca PII)")
                         + csv_table(ROOT / "evals" / "real-cases.csv", ["id", "scenario", "user_request", "expected_behavior", "checks"],
                                     "Bộ đề thật: 3 ca")))
    v1_tables = "".join(
        csv_table(p, ["Test ID", "Kịch bản", "Expected Behavior", "Actual Behavior", "Result", "Runs Pass", "Checks FAIL"], p.stem)
        for p in sorted(results.glob("v1__*.csv")))
    parts.append(section("Sản phẩm #5", "<h1>5. Kết quả kiểm thử thực tế của V1</h1>" + v1_tables))
    parts.append(section("Sản phẩm #6", md(ROOT / "evals" / "failure-analysis.md")))
    parts.append(section("Sản phẩm #7", md(ROOT / "instructions" / "system-prompt-v2.md")
                         + "<p class='muted'>Mã nguồn: src/tasklens/pipeline_v2.py, sanitize.py, validate.py</p>"))
    parts.append(section("Sản phẩm #8", md(ROOT / "evals" / "v1-vs-v2.md")))
    parts.append(section("Sản phẩm #9", md(ROOT / "docs" / "model-swap-log.md")))
    parts.append(section("Sản phẩm #10", md(ROOT / "docs" / "limitations-safety.md")))
    parts.append(section("Sản phẩm #11", md(ROOT / "demo" / "demo-script.md")))
    parts.append(section("Sản phẩm #12", md(ROOT / "docs" / "case-study.md")))
    parts.append(section("Phụ lục", md(ROOT / "docs" / "qa-prep.md")))

    DIST.mkdir(exist_ok=True)
    out_html = DIST / "BaoCao_CuoiKhoa_TaskLens.html"
    out_html.write_text(f"<!doctype html><html lang='vi'><head><meta charset='utf-8'><title>TaskLens: Báo cáo cuối khóa</title>"
                        f"<style>{CSS}</style></head><body>{''.join(parts)}</body></html>", encoding="utf-8")
    out_pdf = DIST / "BaoCao_CuoiKhoa_TaskLens.pdf"
    out_pdf.unlink(missing_ok=True)
    # Hồ sơ Edge riêng: không đụng tới cửa sổ Edge người dùng đang mở (nếu dùng chung, lệnh in bị bỏ qua).
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as profile:  # Edge có thể còn giữ file lúc dọn
        subprocess.run([str(EDGE), "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={profile}", f"--print-to-pdf={out_pdf}", out_html.as_uri()],
                       check=True, timeout=180)
        # Trình khởi chạy Edge có thể thoát trước khi tiến trình con in xong: chờ file xuất hiện và ổn định.
        size, deadline = -1, time.time() + 120
        while time.time() < deadline:
            if out_pdf.exists() and out_pdf.stat().st_size == size and size > 0:
                break
            size = out_pdf.stat().st_size if out_pdf.exists() else -1
            time.sleep(2)
        if not out_pdf.exists():
            raise SystemExit("Edge không tạo được PDF. Mở file HTML trong dist/ và in ra PDF thủ công (Ctrl+P).")
    print(f"→ {out_html.relative_to(ROOT)}\n→ {out_pdf.relative_to(ROOT)} ({out_pdf.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
