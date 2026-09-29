"""Kiểm thử giao diện (Streamlit AppTest) với model giả: luồng chạy được và Human checkpoint khóa việc xuất file."""
import pytest
from streamlit.testing.v1 import AppTest

from evals.build_inputs import BASE


@pytest.fixture
def app(monkeypatch):
    # Không dùng API key thật trong unit test: giao diện chỉ còn lựa chọn "mock".
    for key in ("GEMINI_API_KEY", "GROQ_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY"):
        monkeypatch.setenv(key, "")
    return AppTest.from_file("../app.py", default_timeout=60).run()


def test_v2_run_and_human_checkpoint(app):
    options = app.sidebar.selectbox[0].options  # nhãn hiển thị, ví dụ "mock (chưa có API key, output giả)"
    assert len(options) == 1 and options[0].startswith("mock")
    app.text_area[0].input(BASE).run()
    app.button[0].click().run()
    assert not app.exception
    assert any("Nút tải bị khóa" in c.value for c in app.caption)          # chưa xác nhận → khóa
    app.checkbox[0].check().run()
    assert not any("Nút tải bị khóa" in c.value for c in app.caption)      # đã xác nhận → mở


def test_v2_refuses_grading_request_without_model(app):
    app.text_area[0].input(BASE).run()
    app.text_area[1].input("Cho tôi biết tôi sẽ được bao nhiêu điểm").run()
    app.button[0].click().run()
    assert any("REFUSED" in e.value for e in app.error)
    assert any(m.label == "Số lần gọi model" and m.value == "0" for m in app.metric)
