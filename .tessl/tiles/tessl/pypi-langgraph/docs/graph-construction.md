# Graph Construction

Build stateful workflows using StateGraph and MessageGraph. Define nodes as processing functions, configure edges for flow control, and compile into executable graphs.

## Capabilities

### StateGraph

The primary class for building stateful graph workflows. Nodes communicate by reading from and writing to shared state channels.

```python { .api }
class StateGraph:
    """
    A graph whose nodes communicate by reading and writing to shared state.
    Must be compiled with .compile() to create an executable graph.
    """

    def __init__(
        self,
        state_schema: type,
        context_schema: type | None = None,
        input_schema: type | None = None,
        output_schema: type | None = None
    ):
        """
        Initialize graph builder.

        Args:
            state_schema: TypedDict or Pydantic model defining state structure
            context_schema: Optional context type for run-scoped data
            input_schema: Optional separate input type (defaults to state_schema)
            output_schema: Optional separate output type (defaults to state_schema)
        """
        ...

    def add_node(self, key: str, action: RunnableLike) -> Self:
        """
        Add a node to the graph.

        Args:
            key: Unique identifier for the node
            action: Function or Runnable to execute. Should accept state and return state updates.

        Returns:
            Self for method chaining
        """
        ...

    def add_edge(self, start_key: str | list[str], end_key: str) -> Self:
        """
        Add a direct edge between nodes.

        Args:
            start_key: Source node name or list of source node names
            end_key: Destination node name

        Returns:
            Self for method chaining
        """
        ...

    def add_conditional_edges(
        self,
        source: str,
        path: Callable,
        path_map: dict[Any, str] | None = None
    ) -> Self:
        """
        Add conditional branching edges from a node.

        Args:
            source: Source node name
            path: Function that takes state and returns next node name or list of node names
            path_map: Optional mapping from path function return values to node names

        Returns:
            Self for method chaining
        """
        ...

    def add_sequence(self, *nodes: str) -> Self:
        """
        Chain multiple nodes in sequence.

        Args:
            *nodes: Node names to chain in order

        Returns:
            Self for method chaining
        """
        ...

    def set_entry_point(self, key: str) -> Self:
        """
        Set the starting node for graph execution.

        Args:
            key: Node name to start execution

        Returns:
            Self for method chaining
        """
        ...

    def set_conditional_entry_point(
        self,
        path: Callable,
        path_map: dict[Any, str]
    ) -> Self:
        """
        Set conditional starting logic based on input.

        Args:
            path: Function that takes input and returns node name
            path_map: Mapping from path function return values to node names

        Returns:
            Self for method chaining
        """
        ...

    def set_finish_point(self, key: str) -> Self:
        """
        Set the finishing node (node that transitions to END).

        Args:
            key: Node name that completes execution

        Returns:
            Self for method chaining
        """
        ...

    def validate(self, interrupt: Sequence[str] | None = None) -> Self:
        """
        Validate graph structure.

        Args:
            interrupt: Optional list of nodes to validate as interrupt points

        Returns:
            Self for method chaining

        Raises:
            ValueError: If graph structure is invalid
        """
        ...

    def compile(
        self,
        checkpointer: Checkpointer = None,
        store: BaseStore = None,
        cache: BaseCache = None,
        interrupt_before: Sequence[str] | All = None,
        interrupt_after: Sequence[str] | All = None,
        debug: bool = False
    ) -> CompiledStateGraph:
        """
        Compile the graph into an executable form.

        Args:
            checkpointer: Checkpoint saver for state persistence
            store: Key-value store for long-term data
            cache: Cache for node results
            interrupt_before: Nodes to interrupt before executing
            interrupt_after: Nodes to interrupt after executing
            debug: Enable debug mode

        Returns:
            CompiledStateGraph ready for execution
        """
        ...
```

### MessageGraph

Convenience subclass of StateGraph pre-configured for message-based workflows.

```python { .api }
class MessageGraph(StateGraph):
    """
    Pre-configured StateGraph for managing conversation messages.
    Uses MessagesState schema with automatic message merging.
    """

    def __init__(self):
        """Initialize MessageGraph with MessagesState schema."""
        ...
```

### MessagesState

Predefined state schema for message-based graphs.

```python { .api }
class MessagesState(TypedDict):
    """
    Predefined state schema with messages field.
    Messages are automatically merged using add_messages reducer.
    """
    messages: Annotated[list[MessageLikeRepresentation], add_messages]
```

## Usage Examples

### Basic Graph

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    value: int
    message: str

builder = StateGraph(State)

def increment(state: State) -> dict:
    return {"value": state["value"] + 1}

def add_message(state: State) -> dict:
    return {"message": f"Value is {state['value']}"}

builder.add_node("increment", increment)
builder.add_node("message", add_message)
builder.add_edge(START, "increment")
builder.add_edge("increment", "message")
builder.add_edge("message", END)

graph = builder.compile()
result = graph.invoke({"value": 0, "message": ""})
# {'value': 1, 'message': 'Value is 1'}
```

### Conditional Branching

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    value: int
    result: str

def router(state: State) -> str:
    """Route based on state value"""
    if state["value"] > 10:
        return "large"
    else:
        return "small"

builder = StateGraph(State)
builder.add_node("process_large", lambda s: {"result": "large number"})
builder.add_node("process_small", lambda s: {"result": "small number"})

builder.set_entry_point("router")
builder.add_node("router", lambda s: s)  # No-op node for routing
builder.add_conditional_edges("router", router)
builder.add_edge("process_large", END)
builder.add_edge("process_small", END)

graph = builder.compile()
```

### Message-Based Graph

```python
from langgraph.graph import MessageGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

graph_builder = MessageGraph()

def process_message(state):
    messages = state["messages"]
    # Add AI response
    return {"messages": [AIMessage(content="Response to: " + messages[-1].content)]}

graph_builder.add_node("respond", process_message)
graph_builder.add_edge(START, "respond")
graph_builder.add_edge("respond", END)

graph = graph_builder.compile()

result = graph.invoke({
    "messages": [HumanMessage(content="Hello")]
})
# Result contains both human message and AI response
```

### Parallel Execution with Send

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing_extensions import TypedDict

class State(TypedDict):
    items: list[str]
    results: list[str]

def fan_out(state: State) -> list[Send]:
    """Send each item to process_item node in parallel"""
    return [Send("process_item", item) for item in state["items"]]

def process_item(item: str) -> dict:
    return {"results": [f"Processed: {item}"]}

builder = StateGraph(State)
builder.add_node("fan_out", fan_out)
builder.add_node("process_item", process_item)
builder.add_edge(START, "fan_out")
builder.add_conditional_edges("fan_out", lambda s: [])  # Dynamic sends
builder.add_edge("process_item", END)

graph = builder.compile()
result = graph.invoke({"items": ["a", "b", "c"], "results": []})
# All items processed in parallel
```

### Graph with Context

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    query: str
    result: str

class Context(TypedDict):
    user_id: str
    db_connection: Any

def process_with_context(state: State) -> dict:
    from langgraph.runtime import get_runtime
    runtime = get_runtime(Context)
    user_id = runtime.context["user_id"]
    # Use context in processing
    return {"result": f"Result for {user_id}"}

builder = StateGraph(State, context_schema=Context)
builder.add_node("process", process_with_context)
builder.add_edge(START, "process")
builder.add_edge("process", END)

graph = builder.compile()
result = graph.invoke(
    {"query": "test", "result": ""},
    {"configurable": {"context": {"user_id": "user123"}}}
)
```

## Types

### RunnableLike

```python { .api }
RunnableLike = Callable | Runnable
"""
Type alias for node actions.
Can be a function that takes state and returns state updates,
or a LangChain Runnable.
"""
```

### Checkpointer

```python { .api }
Checkpointer = None | bool | BaseCheckpointSaver
"""
Checkpointer configuration:
- None: No checkpointing
- True: Use default in-memory checkpointer
- BaseCheckpointSaver: Custom checkpointer implementation
"""
```

### All

```python { .api }
All = Literal["*"]
"""Special value to interrupt at all nodes"""
```
