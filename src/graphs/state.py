from typing_extensions import TypedDict
from typing import Optional

class GraphState(TypedDict):
    """
    The primary state object passed between nodes in the graph.
    
    Fields:
        input: The initial string from userPrompt. MUST not be null.
        message: The generated greeting. Defaults to empty string.
        decision: The random value (0 or 1). Range [0, 1].
    """
    input: str
    message: str
    decision: Optional[int]
