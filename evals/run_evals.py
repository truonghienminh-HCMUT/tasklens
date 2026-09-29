"""Chạy Eval Suite cho một phiên bản pipeline trên một model.

    python evals/run_evals.py --version v1 --model gemini --runs 3
    python evals/run_evals.py --version v2 --model anthropic:claude-opus-5 --runs 3 --cases TC02,TC08
    python evals/run_evals.py --version v1 --model mock --runs 1      # chỉ kiểm tra đường ống

Kết quả:
    evals/results/<version>__<provider>-<model>.csv           bảng 7 trường (B12 slide 18)
    evals/results/<version>__<provider>-<model>__summary.json số liệu tổng hợp
    evals/results/raw/<version>__<provider>-<model>/*.json    log thô từng lần chạy (bằng chứng)
Cột Root Cause / Action-Fix / Human Verdict được giữ nguyên khi chạy lại (regression).
"""
from __future__ import annotations

import argparse
import csv
import importlib
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from evals.graders import Ctx, grade  # noqa: E402
from tasklens.adapters import get_adapter  # noqa: E402
from tasklens.io_utils import read_file  # noqa: E402

EVALS = ROOT / "evals"
RETRYABLE = re.compile(r"429|RESOURCE_EXHAUSTED|rate.?limit|overloaded|UNAVAILABLE|503|502|500|timed? ?out", re.I)
KEEP_COLUMNS = ("Root Cause", "Action / Fix", "Human Verdict")
COLUMNS = [
    "Test ID", "Test Name", "Kịch bản", "Input Data", "Expected Behavior", "Actual Behavior",
    "Result", "Runs Pass", "Checks FAIL", "Root Cause", "Action / Fix", "Human Verdict",
    "Avg Latency (s)", "Avg Input Tokens", "Avg Output Tokens",
]


SUITES = {
    # bộ chính: dữ liệu tổng hợp, công khai, tái lập được
    "main": {"cases": EVALS / "test-cases.csv", "inputs": EVALS / "inputs", "suffix": ""},
    # đề thật của người dùng: file nằm trong thư mục private (không lên GitHub)
    "real": {"cases": EVALS / "real-cases.csv", "inputs": ROOT / "demo" / "sample-inputs" / "private", "suffix": "__real"},
}


def load_cases(selected: set[str] | None, suite: str = "main") -> list[dict]:
    with open(SUITES[suite]["cases"], encoding="utf-8", newline="") as f:
        cases = list(csv.DictReader(f))
    for case in cases:
        case["_path"] = SUITES[suite]["inputs"] / case["input_file"]
    return [c for c in cases if not selected or c["id"] in selected]


NOT_RETRYABLE = re.compile(r"\b413\b|too large|context.?length|NOT_FOUND|\b404\b", re.I)
ACCOUNT_IDS = re.compile(r"\b(org|proj|user|acct)[_-][A-Za-z0-9]{8,}")


def redact(message: str) -> str:
    """Che mã định danh tài khoản trong thông báo lỗi trước khi ghi log (log sẽ lên GitHub)."""
    return ACCOUNT_IDS.sub(lambda m: f"{m.group(1)}_[ĐÃ CHE]", message)


RETRY_AFTER = re.compile(r"(?:try again|retry) in (?:(\d+)m)?([\d.]+)s", re.I)
DAILY_HARD_CAP = re.compile(r"PerDay", re.I)  # quota theo ngày của Gemini: chờ vài giây không giải quyết được


def call_with_retry(fn, attempts: int = 6, rate_limit_attempts: int = 60):
    """Thử lại lỗi tạm thời. Nếu nhà cung cấp nói rõ phải chờ bao lâu (rate limit), chờ đúng khoảng đó."""
    delay, errors, waits = 10.0, 0, 0
    while True:
        try:
            return fn()
        except Exception as exc:  # SDK của mỗi hãng ném các lớp lỗi khác nhau
            text = f"{type(exc).__name__} {exc}"
            if NOT_RETRYABLE.search(text) or DAILY_HARD_CAP.search(text) or not RETRYABLE.search(text):
                raise
            hint = RETRY_AFTER.search(text)
            if hint and waits < rate_limit_attempts:
                waits += 1
                wait = min(int(hint.group(1) or 0) * 60 + float(hint.group(2)) + 2, 900)
                print(f"    ! rate limit, chờ {wait:.0f}s theo yêu cầu của nhà cung cấp ({waits}/{rate_limit_attempts})", flush=True)
                time.sleep(wait)
                continue
            errors += 1
            if errors >= attempts:
                raise
            print(f"    ! {type(exc).__name__}, thử lại sau {delay:.0f}s ({errors}/{attempts})", flush=True)
            time.sleep(delay)
            delay = min(delay * 2, 120)


def run_one(pipeline, adapter, case: dict, k: int, raw_dir: Path, regrade: bool = False, resume: bool = False) -> dict:
    document = read_file(case["_path"])
    raw_path = raw_dir / f"{case['id']}__r{k}.json"
    if resume and raw_path.exists() and not json.loads(raw_path.read_text(encoding="utf-8")).get("error"):
        regrade = True  # lượt này đã chạy thành công: dùng lại câu trả lời đã lưu, không gọi model lần nữa
    if regrade:
        # Chấm lại từ câu trả lời thô đã lưu: giữ nguyên số liệu đo (latency, token), không gọi model.
        record = json.loads(raw_path.read_text(encoding="utf-8"))
        record["regraded_at"] = datetime.now().isoformat(timespec="seconds")
    else:
        record = {"case": case["id"], "run": k, "error": ""}
    try:
        if regrade:
            if record.get("error"):
                raise RuntimeError(record["error"])
            result = pipeline.replay(document, case["user_request"], record["raw_text"], adapter=adapter)
        else:
            result = call_with_retry(lambda: pipeline.run(document, case["user_request"], adapter))
            record.update(
                raw_text=result.raw_text,
                notes=result.notes,
                latency_s=round(result.latency_s, 2),
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                model_calls=len(result.responses),
                stop_reasons=[r.stop_reason for r in result.responses],
                sent=result.sent,
            )
        ctx = Ctx(result.output, result.raw_text, document, result.sent, result.system_prompt)
        checks = grade(ctx, case["checks"])
        record.update(output=result.output, parse_error=result.error)
    except Exception as exc:
        message = redact(str(exc) if regrade else f"{type(exc).__name__}: {str(exc)[:300]}")
        checks = [("api_call", False, message)]
        record["error"] = message
    record["checks"] = [{"check": n, "pass": ok, "detail": d} for n, ok, d in checks]
    record["passed"] = all(ok for _, ok, _ in checks)
    raw_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    mark = "PASS" if record["passed"] else "FAIL"
    print(f"  {case['id']} r{k}: {mark}" + ("" if record["passed"] else f"  <- {[c['check'] for c in record['checks'] if not c['pass']]}"), flush=True)
    return record


def describe(record: dict) -> str:
    out = record.get("output")
    if record.get("error"):
        return f"LỖI GỌI API: {record['error']}"
    if out is None:
        return f"Không trả về JSON hợp lệ ({record.get('parse_error', '')[:120]})"
    dl = (out.get("deadline") or {}).get("value", "null")
    parts = [
        f"status={out.get('status')}",
        f"deadline={dl}",
        f"plan={len(out.get('plan') or [])} bước",
        f"missing={len(out.get('missing_info') or [])}",
        f"questions={len(out.get('questions') or [])}",
        f"contradictions={len(out.get('contradictions') or [])}",
        f"invalid={len(out.get('invalid_data') or [])}",
        f"injection_flags={len(out.get('injection_flags') or [])}",
    ]
    if out.get("refusal_reason"):
        parts.append(f"refusal='{out['refusal_reason'][:100]}'")
    return "; ".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True, help="v1 | v2")
    ap.add_argument("--model", required=True, help="gemini | openai[:model] | anthropic[:model] | mock")
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--cases", default="", help="VD: TC01,TC08 (mặc định: tất cả)")
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--regrade", action="store_true",
                    help="Chấm lại từ log thô đã lưu (sau khi sửa bộ chấm/schema), không gọi model")
    ap.add_argument("--resume", action="store_true",
                    help="Giữ các lượt đã chạy thành công, chỉ gọi model cho lượt còn thiếu/bị lỗi API")
    ap.add_argument("--suite", choices=list(SUITES), default="main",
                    help="main: 11 ca tổng hợp | real: đề thật trong demo/sample-inputs/private")
    args = ap.parse_args()

    pipeline = importlib.import_module(f"tasklens.pipeline_{args.version}")
    adapter = get_adapter(args.model)
    tag = f"{args.version}__{adapter.provider}-{adapter.model}".replace(":", "-").replace("/", "-") + SUITES[args.suite]["suffix"]
    results_dir = EVALS / "results" / ("_mock" if adapter.provider == "mock" else "")
    raw_dir = results_dir / "raw" / tag
    raw_dir.mkdir(parents=True, exist_ok=True)

    cases = load_cases(set(filter(None, args.cases.split(","))) or None, args.suite)
    mode = "CHẤM LẠI từ log thô" if args.regrade else "Eval"
    print(f"{mode} {args.version} trên {adapter.provider}:{adapter.model}: {len(cases)} ca × {args.runs} lần", flush=True)

    jobs = [(case, k) for case in cases for k in range(1, args.runs + 1)]
    with ThreadPoolExecutor(max_workers=1 if args.regrade else args.workers) as pool:
        records = list(pool.map(
            lambda job: run_one(pipeline, adapter, job[0], job[1], raw_dir, args.regrade, args.resume), jobs))

    csv_path = results_dir / f"{tag}.csv"
    previous = {}
    if csv_path.exists():
        with open(csv_path, encoding="utf-8-sig", newline="") as f:
            previous = {row["Test ID"]: row for row in csv.DictReader(f)}

    rows, per_case = [], {}
    for case in cases:
        recs = [r for r in records if r["case"] == case["id"]]
        n_pass = sum(r["passed"] for r in recs)
        result = "PASS" if n_pass == len(recs) else ("FAIL" if n_pass == 0 else "FLAKY")
        rep = next((r for r in recs if not r["passed"]), recs[0])
        failed = sorted({f"{c['check']} → {c['detail']}" for r in recs for c in r["checks"] if not c["pass"]})
        ok_recs = [r for r in recs if not r["error"]]
        avg = lambda key: round(sum(r.get(key) or 0 for r in ok_recs) / len(ok_recs), 2) if ok_recs else ""  # noqa: E731
        request = f" | Yêu cầu: {case['user_request']}" if case["user_request"] else ""
        row = {
            "Test ID": case["id"],
            "Test Name": case["name"],
            "Kịch bản": case["scenario"],
            "Input Data": f"{case['_path'].relative_to(ROOT).as_posix()}{request}",
            "Expected Behavior": case["expected_behavior"],
            "Actual Behavior": describe(rep),
            "Result": result,
            "Runs Pass": f"{n_pass}/{len(recs)}",
            "Checks FAIL": " || ".join(failed),
            "Avg Latency (s)": avg("latency_s"),
            "Avg Input Tokens": avg("input_tokens"),
            "Avg Output Tokens": avg("output_tokens"),
        }
        for col in KEEP_COLUMNS:
            row[col] = previous.get(case["id"], {}).get(col, "")
        rows.append(row)
        per_case[case["id"]] = {"result": result, "runs_pass": n_pass, "runs": len(recs)}

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    ok_records = [r for r in records if not r["error"]]
    summary = {
        "version": args.version,
        "provider": adapter.provider,
        "model": adapter.model,
        "runs_per_case": args.runs,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "regraded_from_raw": args.regrade,
        "cases": per_case,
        "cases_pass_strict": sum(v["result"] == "PASS" for v in per_case.values()),
        "cases_total": len(per_case),
        "run_pass_rate": round(sum(r["passed"] for r in records) / len(records), 3),
        "json_valid_rate": round(sum(r.get("output") is not None for r in ok_records) / max(len(ok_records), 1), 3),
        "api_errors": len(records) - len(ok_records),
        "avg_latency_s": round(sum(r["latency_s"] for r in ok_records) / max(len(ok_records), 1), 2),
        "total_input_tokens": sum(r.get("input_tokens") or 0 for r in ok_records),
        "total_output_tokens": sum(r.get("output_tokens") or 0 for r in ok_records),
    }
    (results_dir / f"{tag}__summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"\nKết quả: {summary['cases_pass_strict']}/{summary['cases_total']} ca PASS ổn định "
        f"| tỉ lệ lần chạy đạt {summary['run_pass_rate']:.0%} | JSON hợp lệ {summary['json_valid_rate']:.0%} "
        f"| lỗi API {summary['api_errors']}\n→ {csv_path.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
