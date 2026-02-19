from typing import Any

import pytest


def validate_graph_state(state: Any) -> None:
    """Simple validator to enforce GraphState requirements from spec."""
    if "input" not in state or state["input"] is None:
        raise ValueError("input MUST not be null")
    if (val := state.get("decision")) is not None and not (0 <= val <= 1):
        raise ValueError("decision must be in range [0, 1]")


def test_ts_012_graph_state_input_not_null() -> None:
    """TS-012: GraphState input validation"""
    state = {"input": None, "message": "", "decision": 0}
    with pytest.raises(ValueError, match="input MUST not be null"):
        validate_graph_state(state)


def test_ts_013_graph_state_decision_range() -> None:
    """TS-013: GraphState decision range"""
    # Valid low
    validate_graph_state({"input": "test", "decision": 0})
    # Valid high
    validate_graph_state({"input": "test", "decision": 1})

    # Invalid
    with pytest.raises(ValueError, match=r"decision must be in range \[0, 1\]"):
        validate_graph_state({"input": "test", "decision": 2})

    with pytest.raises(ValueError, match=r"decision must be in range \[0, 1\]"):
        validate_graph_state({"input": "test", "decision": -1})
