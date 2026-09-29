"""Tổng hợp kết quả thật trong evals/results/ thành bảng + biểu đồ so sánh V1/V2 × model.

    python evals/compare.py
Sinh ra:
    evals/results/comparison.md   bảng số liệu (bộ chính + bộ đề thật)
    evals/v1-vs-v2.png            số ca PASS ổn định theo phiên bản và model (bộ chính)
    evals/per-case-heatmap.png    số lần đạt của từng ca (bộ chính)
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

EVALS = Path(__file__).resolve().parent
RESULTS = EVALS / "results"

# Bảng màu đã kiểm tra bằng validator của skill dataviz (light surface #fcfcfb).
SURFACE, INK, INK_2, MUTED, GRID, AXIS = "#fcfcfb", "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
SERIES = {"v1": "#2a78d6", "v2": "#eb6834"}
RAMP = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]  # tỉ lệ lần đạt 0 → 100%, ordinal
MODEL_LABEL = {
    "openai/gpt-oss-120b": "gpt-oss-120b (OpenAI, qua Groq)",
    "gemma-4-26b-a4b-it": "Gemma 4 26B (Google, qua Gemini API)",
}
MODEL_SHORT = {"openai/gpt-oss-120b": "gpt-oss", "gemma-4-26b-a4b-it": "gemma"}

plt.rcParams.update({"font.family": ["Segoe UI", "DejaVu Sans"], "font.size": 11, "axes.edgecolor": AXIS})


def load(suite: str = "main") -> list[dict]:
    runs = []
    for path in sorted(RESULTS.glob("v*__*__summary.json")):
        if path.name.endswith("__real__summary.json") != (suite == "real"):
            continue
        summary = json.loads(path.read_text(encoding="utf-8"))
        if summary["model"] not in MODEL_LABEL:
            continue
        with open(path.with_name(path.name.replace("__summary.json", ".csv")), encoding="utf-8-sig") as f:
            summary["rows"] = {r["Test ID"]: r for r in csv.DictReader(f)}
        runs.append(summary)
    return sorted(runs, key=lambda r: (list(MODEL_LABEL).index(r["model"]), r["version"]))


def _style(ax, fig):
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)


def rounded_bar(ax, x, width, height, color):
    """Cột có đầu bo 4px phía trên, đáy phẳng neo vào trục (mark spec của skill dataviz)."""
    if height <= 0:
        return
    px_to_x = (ax.get_xlim()[1] - ax.get_xlim()[0]) / ax.bbox.width
    px_to_y = (ax.get_ylim()[1] - ax.get_ylim()[0]) / ax.bbox.height
    r = 4 * ax.figure.dpi / 72 * px_to_x
    ax.add_patch(FancyBboxPatch((x, 0), width, height, boxstyle=f"round,pad=0,rounding_size={r}",
                                mutation_aspect=px_to_y / px_to_x, fc=color, ec="none"))
    ax.add_patch(Rectangle((x, 0), width, min(height, r * px_to_y / px_to_x), fc=color, ec="none"))


def bar_chart(runs: list[dict]) -> None:
    models = [m for m in MODEL_LABEL if any(r["model"] == m for r in runs)]
    versions = [v for v in ("v1", "v2") if any(r["version"] == v for r in runs)]
    total = max(r["cases_total"] for r in runs)
    fig, ax = plt.subplots(figsize=(8.4, 4.8), dpi=200)
    _style(ax, fig)
    ax.set_xlim(-0.6, len(models) - 0.4)
    ax.set_ylim(0, total + 1.4)
    width, gap = 0.34, 0.02
    for i, model in enumerate(models):
        for j, version in enumerate(versions):
            run = next((r for r in runs if r["model"] == model and r["version"] == version), None)
            if run is None:
                continue
            x = i - (len(versions) * width) / 2 + j * width + gap / 2
            value = run["cases_pass_strict"]
            rounded_bar(ax, x, width - gap, value, SERIES[version])
            ax.text(x + (width - gap) / 2, value + 0.2, f"{value}/{run['cases_total']}", ha="center", va="bottom",
                    color=INK, fontsize=11, fontweight="bold")
    labels = []
    for m in models:
        n = {r["runs_per_case"] for r in runs if r["model"] == m}
        labels.append(f"{MODEL_LABEL[m]}\n{'/'.join(map(str, sorted(n)))} lần chạy mỗi ca")
    ax.set_xticks(range(len(models)), labels, color=INK_2, fontsize=10)
    ax.set_yticks(range(0, total + 1, 2))
    ax.tick_params(axis="y", colors=MUTED, length=0)
    ax.tick_params(axis="x", length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.set_ylabel("Số ca PASS ở mọi lần chạy", color=INK_2)
    ax.set_title(f"TaskLens: số ca kiểm thử đạt trên {total} ca", color=INK, loc="left", fontsize=13, pad=14)
    handles = [Rectangle((0, 0), 1, 1, fc=SERIES[v]) for v in versions]
    ax.legend(handles, [v.upper() for v in versions], frameon=False, loc="upper left", ncols=len(versions), labelcolor=INK_2)
    fig.tight_layout()
    fig.savefig(EVALS / "v1-vs-v2.png", facecolor=SURFACE)
    plt.close(fig)


def heatmap(runs: list[dict]) -> None:
    cases = list(runs[0]["cases"])
    names = {cid: runs[0]["rows"][cid]["Test Name"] for cid in cases}
    fig, ax = plt.subplots(figsize=(2.6 + 1.5 * len(runs), 0.42 * len(cases) + 1.7), dpi=200)
    _style(ax, fig)
    for col, run in enumerate(runs):
        for row, cid in enumerate(cases):
            info = run["cases"].get(cid)
            if info is None:
                continue
            share = info["runs_pass"] / info["runs"]
            ax.add_patch(Rectangle((col + 0.03, row + 0.05), 0.94, 0.9, fc=RAMP[round(share * 3)], ec=SURFACE, lw=2))
            ax.text(col + 0.5, row + 0.5, f"{info['runs_pass']}/{info['runs']}", ha="center", va="center", fontsize=10,
                    color=INK if share == 0 else "#ffffff", fontweight="bold")
    ax.set_xlim(0, len(runs))
    ax.set_ylim(len(cases), 0)
    ax.set_xticks([c + 0.5 for c in range(len(runs))],
                  [f"{r['version'].upper()}\n{MODEL_SHORT[r['model']]}" for r in runs], color=INK_2)
    ax.xaxis.tick_top()
    ax.set_yticks([i + 0.5 for i in range(len(cases))], [f"{c} {names[c]}" for c in cases], color=INK_2)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("Số lần đạt / số lần chạy, theo từng ca", color=INK, loc="left", fontsize=12, pad=34)
    fig.tight_layout()
    fig.savefig(EVALS / "per-case-heatmap.png", facecolor=SURFACE)
    plt.close(fig)


def tables(runs: list[dict], title: str) -> str:
    head = [f"{r['version'].upper()} · {MODEL_SHORT[r['model']]}" for r in runs]
    lines = [f"## {title}", "", "| Chỉ số | " + " | ".join(head) + " |", "|---|" + "---|" * len(runs)]
    metrics = [
        ("Số lần chạy mỗi ca", lambda r: str(r["runs_per_case"])),
        ("Ca PASS ở mọi lần chạy", lambda r: f"{r['cases_pass_strict']}/{r['cases_total']}"),
        ("Tỉ lệ lần chạy đạt", lambda r: f"{r['run_pass_rate']:.0%}"),
        ("JSON hợp lệ theo schema", lambda r: f"{r['json_valid_rate']:.0%}"),
        ("Lỗi gọi API", lambda r: str(r["api_errors"])),
        ("Độ trễ TB / lần (s)", lambda r: f"{r['avg_latency_s']:.1f}"),
        ("Tổng token vào / ra", lambda r: f"{r['total_input_tokens']:,} / {r['total_output_tokens']:,}"),
    ]
    for label, fn in metrics:
        lines.append(f"| {label} | " + " | ".join(fn(r) for r in runs) + " |")
    lines += ["", "| Ca | " + " | ".join(head) + " |", "|---|" + "---|" * len(runs)]
    icon = {"PASS": "✅", "FLAKY": "⚠️", "FAIL": "❌"}
    for cid in runs[0]["cases"]:
        cells = []
        for r in runs:
            info = r["cases"].get(cid)
            cells.append(f"{info['runs_pass']}/{info['runs']} {icon[info['result']]}" if info else "–")
        lines.append(f"| {cid} {runs[0]['rows'][cid]['Test Name']} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    main_runs, real_runs = load("main"), load("real")
    if not main_runs:
        raise SystemExit("Chưa có kết quả trong evals/results/")
    text = "# Bảng so sánh (sinh tự động bởi evals/compare.py, KHÔNG sửa tay)\n\n"
    text += tables(main_runs, "Bộ chính: 11 ca thử lửa (dữ liệu tổng hợp)")
    if real_runs:
        text += "\n" + tables(real_runs, "Bộ đề thật: 3 ca (đề của người làm bài, không công khai)")
    (RESULTS / "comparison.md").write_text(text, encoding="utf-8")
    bar_chart(main_runs)
    heatmap(main_runs)
    print(text)


if __name__ == "__main__":
    main()
