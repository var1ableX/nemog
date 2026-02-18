import pytest
from src.graphs.writer_graph import create_graph
from src.app.stubs import user_prompt

def test_TS_001_graph_execution_output():
    """TS-001: Entry point execution (Hello World/Universe)"""
    graph = create_graph()
    input_text = user_prompt()
    
    # Run the graph
    result = graph.invoke({"input": input_text, "message": "", "decision": None})
    
    assert result["message"] in ["Hello World", "Hello Universe"]

def test_TS_002_graph_input_traceability(caplog):
    """TS-002: Traceability of input string"""
    import logging
    # Set up logging capture
    logging.getLogger().setLevel(logging.INFO)
    
    graph = create_graph()
    input_text = "Specific Traceable Input"
    
    graph.invoke({"input": input_text, "message": "", "decision": None})
    
    # Check if input_text appears in logs
    assert input_text in caplog.text

def test_TS_003_main_calls_stub(monkeypatch):
    """TS-003: Entry point call to input stub"""
    import src.app.main
    called = False
    def mock_prompt():
        nonlocal called
        called = True
        return "mock"
    
    monkeypatch.setattr(src.app.main, "user_prompt", mock_prompt)
    src.app.main.main()
    assert called

def test_TS_004_svc_executes_graph():
    """TS-004: Service layer execution of graph engine"""
    from src.services.writer_svc import WriterSvc
    svc = WriterSvc()
    result = svc.run("test")
    assert result in ["Hello World", "Hello Universe"]
