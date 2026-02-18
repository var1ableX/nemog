import pytest
import random
from src.graphs.writer_graph import create_graph

def test_TS_005_conditional_transition_logic():
    """TS-005: Conditional transition based on dynamic value"""
    graph = create_graph()
    # If it runs and returns a valid message, the transition logic was executed
    result = graph.invoke({"input": "test", "message": "", "decision": None})
    assert result["message"] in ["Hello World", "Hello Universe"]

def test_TS_006_outcome_world(monkeypatch):
    """TS-006: Outcome for specific dynamic value (0)"""
    import random
    monkeypatch.setattr(random, "randint", lambda a, b: 0)
    graph = create_graph()
    result = graph.invoke({"input": "test", "message": "", "decision": None})
    assert result["message"] == "Hello World"

def test_TS_007_outcome_universe(monkeypatch):
    """TS-007: Outcome for alternative dynamic value (1)"""
    import random
    monkeypatch.setattr(random, "randint", lambda a, b: 1)
    graph = create_graph()
    result = graph.invoke({"input": "test", "message": "", "decision": None})
    assert result["message"] == "Hello Universe"

def test_TS_008_reachability_both_paths():
    """TS-008: Reachability of both paths"""
    graph = create_graph()
    outputs = set()
    for _ in range(50): # Increased iterations to reduce fluke risk
        result = graph.invoke({"input": "test", "message": "", "decision": None})
        outputs.add(result["message"])
    assert "Hello World" in outputs
    assert "Hello Universe" in outputs

def test_TS_011_graph_compilation():
    """TS-011: WriterGraph compilation"""
    graph = create_graph()
    assert graph is not None
    assert hasattr(graph, "invoke")
