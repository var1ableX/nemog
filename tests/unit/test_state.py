from typing import Any
import pytest
from src.graphs.state import GraphState

def validate_graph_state(state: Any):
    """Simple validator to enforce GraphState requirements from spec."""
    if "input" not in state or state["input"] is None:
        raise ValueError("input MUST not be null")
    
    if "decision" in state:
        if state["decision"] is not None and not (0 <= state["decision"] <= 1):
            raise ValueError("decision must be in range [0, 1]")

def test_TS_012_graph_state_input_not_null():
    """TS-012: GraphState input validation"""
    state = {"input": None, "message": "", "decision": 0}
    with pytest.raises(ValueError, match="input MUST not be null"):
        validate_graph_state(state)

def test_TS_013_graph_state_decision_range():
    """TS-013: GraphState decision range"""
    # Valid low
    validate_graph_state({"input": "test", "decision": 0})
    # Valid high
    validate_graph_state({"input": "test", "decision": 1})
    
    # Invalid
    with pytest.raises(ValueError, match="decision must be in range \[0, 1\]"):
        validate_graph_state({"input": "test", "decision": 2})
    
    with pytest.raises(ValueError, match="decision must be in range \[0, 1\]"):
        validate_graph_state({"input": "test", "decision": -1})
