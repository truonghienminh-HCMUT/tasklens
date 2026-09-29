"""Hợp đồng output: null ở trường tùy chọn = rỗng; trường bắt buộc vẫn phải có giá trị."""
import pytest
from pydantic import ValidationError

from tasklens.pipeline_v1 import parse_output
from tasklens.schema import Analysis


def test_null_optional_fields_become_empty():
    a = Analysis.model_validate({
        "status": "OK", "refusal_reason": None, "deadline": None, "plan": None,
        "requirements": [{"content": "x", "quote": None}],
        "contradictions": [{"description": "d", "quote_a": None, "quote_b": None}],
    })
    assert a.refusal_reason == "" and a.plan == [] and a.deadline is None
    assert a.requirements[0].quote == "" and a.contradictions[0].quote_a == ""


@pytest.mark.parametrize("payload", [
    {"status": None},
    {"status": "MAYBE"},
    {"status": "OK", "requirements": [{"content": None}]},
    {"status": "OK", "plan": [{"step": 1, "task": None}]},
])
def test_required_fields_still_enforced(payload):
    with pytest.raises(ValidationError):
        Analysis.model_validate(payload)


def test_truncated_json_is_rejected():
    output, error = parse_output('{"status": "OK", "summary": "đề bài về LabBoo')
    assert output is None and "ValueError" in error
