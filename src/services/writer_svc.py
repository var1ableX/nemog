from src.graphs.writer_graph import create_graph

class WriterSvc:
    """
    Service layer that acts as the interface between the entry point and the graph engine.
    """
    def __init__(self):
        self.graph = create_graph()

    def run(self, input_text: str) -> str:
        """
        Executes the WriterGraph and returns the result.
        """
        # TS-009: Handle empty input gracefully
        if not input_text:
            input_text = "No input provided"

        initial_state = {
            "input": input_text,
            "message": "",
            "decision": None
        }
        
        result = self.graph.invoke(initial_state)
        return result.get("message", "")
