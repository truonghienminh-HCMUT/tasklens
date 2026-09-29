"""Kiểm tra an toàn rồi đóng gói repo thành dist/TaskLens.zip (kèm báo cáo PDF nếu đã build).

    python scripts/package.py

Chỉ lấy file KHÔNG bị .gitignore chặn, rồi từ chối đóng gói nếu phát hiện:
- file nhạy cảm (.env, log vận hành, đề thật trong private/, log thô của ca đề thật RCxx)
- chuỗi giống API key hoặc mã định danh tài khoản
Chạy lại script này trước mỗi lần nộp hoặc push lên GitHub.
"""
from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PATHS = re.compile(r"(^|/)\.env$|^logs/|/private/|RC\d{2}__r\d+\.json$|__real/")
SECRET = re.compile(r"AIza[0-9A-Za-z_-]{30,}|gsk_[0-9A-Za-z]{20,}|sk-[0-9A-Za-z_-]{20,}|sk-ant-[0-9A-Za-z_-]{20,}|\borg_[0-9a-z]{20,}")
EXCLUDE = {"CHECKPOINT.md"}  # file làm việc nội bộ


def publishable_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [f for f in out.splitlines() if f and f not in EXCLUDE]


def main() -> None:
    files = publishable_files()
    problems = [f"file nhạy cảm: {f}" for f in files if FORBIDDEN_PATHS.search(f)]
    for f in files:
        path = ROOT / f
        if path.suffix.lower() in {".png", ".pdf", ".zip"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if SECRET.search(text):
            problems.append(f"chuỗi giống API key/mã tài khoản trong: {f}")
    if problems:
        print("KHÔNG đóng gói, vì phát hiện:\n  " + "\n  ".join(problems))
        sys.exit(1)

    out = ROOT / "dist" / "TaskLens.zip"
    out.parent.mkdir(exist_ok=True)
    report = ROOT / "dist" / "BaoCao_CuoiKhoa_TaskLens.pdf"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in files:
            z.write(ROOT / f, f"tasklens/{f}")
        if report.exists():
            z.write(report, f"tasklens/{report.name}")
    print(f"Kiểm tra an toàn: đạt ({len(files)} file, không có file nhạy cảm hay key)")
    print(f"→ {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
