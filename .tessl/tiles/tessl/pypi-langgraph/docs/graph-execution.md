# Graph Execution

Execute compiled graphs synchronously or asynchronously with comprehensive streaming support. Control execution flow, visualize graph structure, and retrieve schemas.

## Capabilities

### Synchronous Execution

Execute a graph and wait for completion.

```python { .api }
class CompiledStateGraph:
    def invoke(
        self,
        input: InputT,
        config: RunnableConfig | None = None,
        stream_mode: StreamMode | list[StreamMode] = "values",
        output_keys: str | Sequence[str] | None = None,
        interrupt_before: Sequence[str] | All | None = None,
        interrupt_after: Sequence[str] | All | None = None,
        debug: bool | None = None
    ) -> OutputT:
        """
        Execute graph synchronously with single input.

        Args:
            input: Input data matching input schema
            config: Runtime configuration including thread_id for checkpointing
            stream_mode: Not used in invoke (use stream() instead)
            output_keys: Specific output keys to return
            interrupt_before: Override nodes to interrupt before
            interrupt_after: Override nodes to interrupt after
            debug: Enable debug output

        Returns:
            Output data matching output schema
        """
        ...
```

### Asynchronous Execution

Execute a graph asynchronously.

```python { .api }
class CompiledStateGraph:
    async def ainvoke(
        self,
        input: InputT,
        config: RunnableConfig | None = None,
        stream_mode: StreamMode | list[StreamMode] = "values",
        output_keys: str | Sequence[str] | None = None,
        interrupt_before: Sequence[str] | All | None = None,
        interrupt_after: Sequence[str] | All | None = None,
        debug: bool | None = None
    ) -> OutputT:
        """
        Execute graph asynchronously.

        Args:
            input: Input data matching input schema
            config: Runtime configuration
            stream_mode: Not used in ainvoke (use astream() instead)
            output_keys: Specific output keys to return
            interrupt_before: Override nodes to interrupt before
            interrupt_after: Override nodes to interrupt after
            debug: Enable debug output

        Returns:
            Output data matching output schema
        """
        ...
```

### Streaming Execution

Stream outputs during graph execution with multiple streaming modes.

```python { .api }
class CompiledStateGraph:
    def stream(
        self,
        input: InputT,
        config: RunnableConfig | None = None,
        stream_mode: StreamMode | list[StreamMode] = "updates",
        output_keys: str | Sequence[str] | None = None,
        interrupt_before: Sequence[str] | All | None = None,
        interrupt_after: Sequence[str] | All | None = None,
        debug: bool | None = None,
        subgraphs: bool = False
    ) -> Iterator:
        """
        Stream output during graph execution.

        Args:
            input: Input data matching input schema
            config: Runtime configuration
            stream_mode: How to emit stream output:
                - "values": Emit full state after each step
                - "updates": Emit state updates from each node
                - "checkpoints": Emit checkpoint after each step
                - "tasks": Emit tasks for each step
                - "debug": Emit debug information
                - "messages": Emit messages only (for message graphs)
                - "custom": Emit custom stream output via stream_writer
            output_keys: Specific output keys to stream
            interrupt_before: Override nodes to interrupt before
            interrupt_after: Override nodes to interrupt after
            debug: Enable debug output
            subgraphs: Include subgraph updates in stream

        Yields:
            Stream chunks according to stream_mode
        """
        ...

    async def astream(
        self,
        input: InputT,
        config: RunnableConfig | None = None,
        stream_mode: StreamMode | list[StreamMode] = "updates",
        output_keys: str | Sequence[str] | None = None,
        interrupt_before: Sequence[str] | All | None = None,
        interrupt_after: Sequence[str] | All | None = None,
        debug: bool | None = None,
        subgraphs: bool = False
    ) -> AsyncIterator:
        """
        Stream output asynchronously during graph execution.

        Args: Same as stream()

        Yields:
            Async stream chunks according to stream_mode
        """
        ...
```

### Graph Visualization

Get a drawable representation of the graph structure.

```python { .api }
class CompiledStateGraph:
    def get_graph(
        self,
        config: RunnableConfig | None = None,
        xray: int | bool = False
    ) -> Graph:
        """
        Get drawable graph representation.

        Args:
            config: Optional configuration
            xray: Include internal structure (True/False or depth level)

        Returns:
            Graph object that can be visualized
        """
        ...

    async def aget_graph(
        self,
        config: RunnableConfig | None = None,
        xray: int | bool = False
    ) -> Graph:
        """
        Get graph representation asynchronously.

        Args: Same as get_graph()

        Returns:
            Graph object that can be visualized
        """
        ...
```

### Schema Access

Retrieve input and output schemas for the graph.

```python { .api }
class CompiledStateGraph:
    def get_input_schema(
        self,
        config: RunnableConfig | None = None
    ) -> type[BaseModel]:
        """
        Get Pydantic model for graph input.

        Args:
            config: Optional configuration

        Returns:
            Pydantic BaseModel class representing input schema
        """
        ...

    def get_output_schema(
        self,
        config: RunnableConfig | None = None
    ) -> type[BaseModel]:
        """
        Get Pydantic model for graph output.

        Args:
            config: Optional configuration

        Returns:
            Pydantic BaseModel class representing output schema
        """
        ...

    def get_input_jsonschema(
        self,
        config: RunnableConfig | None = None
    ) -> dict:
        """
        Get JSON schema for graph input.

        Args:
            config: Optional configuration

        Returns:
            JSON schema dict
        """
        ...

    def get_output_jsonschema(
        self,
        config: RunnableConfig | None = None
    ) -> dict:
        """
        Get JSON schema for graph output.

        Args:
            config: Optional configuration

        Returns:
            JSON schema dict
        """
        ...
```

### Configuration and Caching

Configure graph execution and manage caching.

```python { .api }
class CompiledStateGraph:
    def with_config(
        self,
        config: RunnableConfig | None = None,
        **kwargs
    ) -> Self:
        """
        Create a copy of the graph with updated configuration.

        Args:
            config: New configuration
            **kwargs: Additional config parameters

        Returns:
            New graph instance with updated config
        """
        ...

    def copy(self, update: dict | None = None) -> Self:
        """
        Create a shallow copy of the graph.

        Args:
            update: Optional dict of attributes to update

        Returns:
            Copied graph instance
        """
        ...

    def validate(self) -> Self:
        """
        Validate graph configuration.

        Returns:
            Self for method chaining

        Raises:
            ValueError: If configuration is invalid
        """
        ...

    def clear_cache(self, nodes: Sequence[str] | None = None) -> None:
        """
        Clear cache for specified nodes or all nodes.

        Args:
            nodes: Node names to clear cache for (None = all nodes)
        """
        ...
```

## Usage Examples

### Basic Invocation

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    input: str
    output: str

builder = StateGraph(State)
builder.add_node("process", lambda s: {"output": s["input"].upper()})
builder.add_edge(START, "process")
builder.add_edge("process", END)

graph = builder.compile()

# Synchronous execution
result = graph.invoke({"input": "hello", "output": ""})
print(result)  # {'input': 'hello', 'output': 'HELLO'}
```

### Asynchronous Execution

```python
import asyncio

async def run_async():
    result = await graph.ainvoke({"input": "hello", "output": ""})
    print(result)

asyncio.run(run_async())
```

### Streaming Updates

```python
# Stream state updates from each node
for chunk in graph.stream({"input": "hello", "output": ""}):
    print(f"Update: {chunk}")
    # Output: {'process': {'output': 'HELLO'}}
```

### Streaming Full State

```python
# Stream complete state after each step
for state in graph.stream(
    {"input": "hello", "output": ""},
    stream_mode="values"
):
    print(f"State: {state}")
    # Output: {'input': 'hello', 'output': 'HELLO'}
```

### Multiple Stream Modes

```python
# Stream both updates and full state
for chunk in graph.stream(
    {"input": "hello", "output": ""},
    stream_mode=["updates", "values"]
):
    print(chunk)
```

### Streaming with Checkpointing

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# Stream with thread_id for checkpointing
config = {"configurable": {"thread_id": "thread-1"}}
for chunk in graph.stream({"input": "hello", "output": ""}, config):
    print(chunk)
```

### Async Streaming

```python
async def stream_async():
    async for chunk in graph.astream({"input": "hello", "output": ""}):
        print(f"Async chunk: {chunk}")

asyncio.run(stream_async())
```

### Visualizing the Graph

```python
# Get graph representation
graph_viz = graph.get_graph()

# Draw the graph (requires graphviz)
try:
    from IPython.display import Image, display
    display(Image(graph_viz.draw_mermaid_png()))
except Exception:
    # Fallback to ASCII representation
    print(graph_viz.draw_ascii())
```

### With Interrupts

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["process"]  # Interrupt before "process" node
)

config = {"configurable": {"thread_id": "thread-1"}}

# Execute until interrupt
for chunk in graph.stream({"input": "hello", "output": ""}, config):
    print(chunk)
# Execution stops before "process" node

# Continue execution
from langgraph.types import Command
for chunk in graph.stream(Command(resume=None), config):
    print(chunk)
# Execution continues from interrupt point
```

### Custom Stream Output

```python
def custom_writer(value):
    """Custom stream writer function"""
    print(f"Custom output: {value}")

from langgraph.config import get_stream_writer

def node_with_custom_output(state):
    writer = get_stream_writer()
    writer("Processing started")
    result = state["input"].upper()
    writer("Processing complete")
    return {"output": result}

builder = StateGraph(State)
builder.add_node("process", node_with_custom_output)
builder.add_edge(START, "process")
builder.add_edge("process", END)

graph = builder.compile()

# Stream custom outputs
for chunk in graph.stream(
    {"input": "hello", "output": ""},
    stream_mode="custom"
):
    print(chunk)
```

## Types

### StreamMode

```python { .api }
StreamMode = Literal[
    "values",      # Emit full state after each step
    "updates",     # Emit state updates from each node
    "checkpoints", # Emit checkpoint after each step
    "tasks",       # Emit tasks for each step
    "debug",       # Emit debug information
    "messages",    # Emit messages only (for message graphs)
    "custom"       # Emit custom stream output
]
```

### RunnableConfig

```python { .api }
class RunnableConfig(TypedDict, total=False):
    """
    Configuration for graph execution.

    Fields:
        configurable: Dict with optional keys:
            - thread_id: Identifier for checkpointing/state management
            - checkpoint_id: Specific checkpoint to resume from
            - context: Run-scoped context data
        tags: List of tags for tracing/filtering
        metadata: Additional metadata
        recursion_limit: Maximum number of steps (default: 25)
        max_concurrency: Maximum parallel tasks
    """
    configurable: dict
    tags: list[str]
    metadata: dict
    recursion_limit: int
    max_concurrency: int
```
