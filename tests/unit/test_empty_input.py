from src.services.writer_svc import WriterSvc


def test_TS_009_empty_input_handling() -> None:
    """TS-009: Handle empty input"""
    svc = WriterSvc()
    
    # Run with empty string
    result = svc.run("")
    
    assert result in ["Hello World", "Hello Universe"]
