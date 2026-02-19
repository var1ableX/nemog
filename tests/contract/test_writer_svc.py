from services.writer_svc import WriterSvc


def test_ts_010_writer_svc_interface() -> None:
    """TS-010: WriterSvc run interface"""
    svc = WriterSvc()
    input_text = "Test Input"
    result = svc.run(input_text)
    assert isinstance(result, str)
    assert result in ["Hello World", "Hello Universe"]
