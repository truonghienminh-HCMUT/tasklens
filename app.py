"""Giao diện web TaskLens.   Chạy:  streamlit run app.py"""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from tasklens.adapters import get_adapter  # noqa: E402
from tasklens.config import DEFAULT_MODELS, available_providers  # noqa: E402
from tasklens.io_utils import extract_text  # noqa: E402
from tasklens.pipeline_v1 import DEFAULT_REQUEST  # noqa: E402
from tasklens.render import SECTIONS, STATUS_LABEL, to_markdown  # noqa: E402

st.set_page_config(page_title="TaskLens — Phân rã đề bài tập lớn", page_icon="🔎", layout="wide")

VERSIONS = [v for v in ("v2", "v1") if (ROOT / "src" / "tasklens" / f"pipeline_{v}.py").exists()]
STATUS_STYLE = {"OK": st.success, "NEED_INFO": st.warning, "REFUSED": st.error, "INVALID_INPUT": st.error}

# ---------------- Sidebar: cấu hình ----------------
with st.sidebar:
    st.header("Cấu hình")
    version = st.radio("Phiên bản pipeline", VERSIONS, format_func=lambda v: v.upper(),
                       help="V1: một lần gọi model. V2: có cổng lọc đầu vào, hỏi lại và kiểm chứng trích dẫn.")
    providers = available_providers() or ["mock"]
    provider = st.selectbox("Nhà cung cấp model", providers,
                            format_func=lambda p: "mock (chưa có API key, output giả)" if p == "mock" else p)
    model = st.text_input("Model", value=DEFAULT_MODELS[provider], disabled=provider == "mock")
    st.divider()
    st.caption(
        f"Đề bài sẽ được gửi tới dịch vụ **{provider}** để phân tích. "
        + ("V2 tự che email, SĐT, MSSV, API key trước khi gửi. " if version == "v2" else
           "V1 **không** lọc dữ liệu cá nhân: đừng tải lên tài liệu chứa thông tin của người khác. ")
        + "TaskLens chỉ đọc và xuất kết quả; không gửi email, không nộp bài, không xóa gì."
    )

# ---------------- Input ----------------
st.title("🔎 TaskLens")
st.caption("Trợ lý phân rã đề bài tập lớn: trích yêu cầu kèm trích dẫn nguyên văn, phát hiện thiếu sót/mâu thuẫn, "
           "chỉ lập kế hoạch khi đủ dữ kiện.")

col_in, col_opt = st.columns([3, 2])
with col_in:
    uploaded = st.file_uploader("Tải đề bài (PDF, DOCX, TXT, MD)", type=["pdf", "docx", "txt", "md"])
    pasted = st.text_area("…hoặc dán nội dung đề bài", height=220)
with col_opt:
    request = st.text_area("Bạn muốn TaskLens làm gì?", value=DEFAULT_REQUEST, height=90)
    known_deadline = st.text_input("Hạn nộp (nếu đề không ghi / bạn đã biết)", placeholder="VD: 23:59 15/12/2026",
                                   disabled=version == "v1", help="Chỉ dùng ở V2")
    run_clicked = st.button("Phân tích đề bài", type="primary", width="stretch")

document = ""
if uploaded is not None:
    document = extract_text(uploaded.getvalue(), uploaded.name)
    with st.expander(f"Văn bản trích từ {uploaded.name} ({len(document):,} ký tự)"):
        st.text(document[:5000] + ("\n…" if len(document) > 5000 else ""))
elif pasted.strip():
    document = pasted

if run_clicked:
    pipeline = importlib.import_module(f"tasklens.pipeline_{version}")
    spec = provider if provider == "mock" else f"{provider}:{model}"
    kwargs = {"known_deadline": known_deadline} if version == "v2" else {}
    with st.spinner(f"Đang phân tích bằng {spec}…"):
        try:
            result = pipeline.run(document, request, get_adapter(spec), **kwargs)
            st.session_state["result"] = result
            st.session_state["meta"] = {"version": version.upper(), "model": spec}
            st.session_state["confirmed"] = False
        except Exception as exc:
            st.session_state.pop("result", None)
            st.error(f"Lỗi khi gọi model: {type(exc).__name__}: {exc}")

# ---------------- Output ----------------
result = st.session_state.get("result")
if result is not None:
    meta = st.session_state["meta"]
    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Phiên bản", meta["version"])
    m2.metric("Số lần gọi model", len(result.responses))
    m3.metric("Thời gian", f"{result.latency_s:.1f} s")
    m4.metric("Token vào / ra", f"{result.input_tokens:,} / {result.output_tokens:,}")

    for note in result.notes:
        st.info(note)

    out = result.output
    if out is None:
        st.error("Model không trả về JSON đúng cấu trúc.")
        st.code(result.raw_text[:4000])
        if result.error:
            st.caption(result.error)
    else:
        STATUS_STYLE.get(out["status"], st.info)(f"**{out['status']}**: {STATUS_LABEL.get(out['status'], '')}")
        if out.get("refusal_reason"):
            st.markdown(f"**Lý do:** {out['refusal_reason']}")
        if out.get("summary"):
            st.markdown(f"**Tóm tắt:** {out['summary']}")
        deadline = out.get("deadline")
        st.markdown(f"**Hạn nộp:** {deadline['value'] if deadline else '_chưa xác định_'}"
                    + (f"  \n> {deadline['quote']}" if deadline and deadline.get("quote") else ""))

        if out.get("missing_info") or out.get("questions"):
            with st.container(border=True):
                st.markdown("#### ❓ Cần bạn bổ sung / làm rõ")
                for item in out.get("missing_info") or []:
                    st.markdown(f"- Thiếu: {item}")
                for q in out.get("questions") or []:
                    st.markdown(f"- {q}")

        if out.get("contradictions"):
            st.markdown("#### ⚠️ Mâu thuẫn trong đề")
            st.dataframe(pd.DataFrame(out["contradictions"]).rename(
                columns={"description": "Mô tả", "quote_a": "Trích dẫn A", "quote_b": "Trích dẫn B"}),
                width="stretch", hide_index=True)

        for key, title in SECTIONS:
            if out.get(key):
                st.markdown(f"#### {title}")
                st.dataframe(pd.DataFrame(out[key]).rename(columns={"content": "Nội dung", "quote": "Trích dẫn nguyên văn"}),
                             width="stretch", hide_index=True)

        if out.get("plan"):
            st.markdown("#### 🗓️ Kế hoạch thực hiện")
            st.dataframe(pd.DataFrame(out["plan"]).rename(columns={"step": "Bước", "task": "Công việc", "due": "Mốc"}),
                         width="stretch", hide_index=True)

        # Human checkpoint: người dùng phải xác nhận trước khi xuất kết quả.
        st.divider()
        confirmed = st.checkbox("Tôi đã đối chiếu kết quả với đề gốc và chịu trách nhiệm khi sử dụng.", key="confirmed")
        c1, c2 = st.columns(2)
        c1.download_button("Tải Markdown", to_markdown(out, meta), file_name="tasklens-phan-tich.md",
                           disabled=not confirmed, width="stretch")
        c2.download_button("Tải JSON", json.dumps(out, ensure_ascii=False, indent=2), file_name="tasklens-phan-tich.json",
                           disabled=not confirmed, width="stretch")
        if not confirmed:
            st.caption("Nút tải bị khóa cho tới khi bạn xác nhận đã đối chiếu (Human-in-the-loop).")

    with st.expander("Câu trả lời thô của model"):
        st.code(result.raw_text[:8000])
