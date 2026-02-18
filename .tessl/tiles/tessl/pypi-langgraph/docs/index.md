# LangGraph

A low-level orchestration framework for building, managing, and deploying long-running, stateful agents and workflows with large language models. LangGraph provides essential infrastructure for creating durable, fault-tolerant agent systems with comprehensive state management, human-in-the-loop capabilities, and seamless integration with LangChain's ecosystem.

## Package Information

- **Package Name**: langgraph
- **Language**: Python
- **Installation**: `pip install langgraph`
- **Version**: 1.0.5

## Core Imports

```python
from langgraph.graph import StateGraph, MessageGraph, MessagesState, START, END
from langgraph.types import Command, Send, interrupt, StreamMode
```

## Basic Usage

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

# Define state schema
class State(TypedDict):
    messages: list[str]
    count: int

# Create graph builder
builder = StateGraph(State)

# Add nodes (processing steps)
def process_node(state: State) -> State:
    return {
        "messages": state["messages"] + ["processed"],
        "count": state["count"] + 1
    }

builder.add_node("process", process_node)

# Define edges (flow control)
builder.add_edge(START, "process")
builder.add_edge("process", END)

# Compile to executable graph
graph = builder.compile()

# Execute synchronously
result = graph.invoke({"messages": [], "count": 0})
print(result)  # {'messages': ['processed'], 'count': 1}

# Or stream output
for chunk in graph.stream({"messages": [], "count": 0}):
    print(chunk)
```

## Architecture

LangGraph is built on a graph-based execution model inspired by Google's Pregel and Apache Beam:

- **Graphs**: Define workflows as directed graphs with nodes (processing steps) and edges (flow control)
- **State Management**: Shared state that nodes read from and write to using configurable channels
- **Checkpointing**: Automatic persistence of state at each step for fault tolerance and resumability
- **Streaming**: Real-time output streaming during execution
- **Human-in-the-Loop**: Interrupt execution to inspect/modify state before continuing

LangGraph provides two main API levels:

1. **High-level Graph API** (`StateGraph`, `MessageGraph`): Builder pattern for defining graphs declaratively
2. **Low-level Pregel API**: Direct control over graph execution engine for advanced use cases

## Capabilities

### Graph Construction

Build stateful workflows using the StateGraph and MessageGraph classes. Define nodes as processing functions, add edges for flow control, and compile to executable graphs.

```python { .api }
class StateGraph:
    def __init__(
        self,
        state_schema: type,
        context_schema: type | None = None,
        input_schema: type | None = None,
        output_schema: type | None = None
    ): ...

    def add_node(self, key: str, action: RunnableLike) -> Self: ...
    def add_edge(self, start_key: str | list[str], end_key: str) -> Self: ...
    def add_conditional_edges(
        self,
        source: str,
        path: Callable,
        path_map: dict[Any, str] | None = None
    ) -> Self: ...
    def compile(
        self,
        checkpointer: Checkpointer = None,
        store: BaseStore = None,
        cache: BaseCache = None,
        interrupt_before: Sequence[str] | All = None,
        interrupt_after: Sequence[str] | All = None,
        debug: bool = False
    ) -> CompiledStateGraph: ...

class MessageGraph(StateGraph):
    """Pre-configured StateGraph for message-based workflows"""
    ...
```

[Graph Construction](./graph-construction.md)

### Graph Execution

Execute compiled graphs synchronously or asynchronously with streaming support. Control execution flow, handle interrupts, and manage state during runtime.

```python { .api }
class CompiledStateGraph:
    def invoke(self, input: InputT, config: RunnableConfig | None = None) -> OutputT: ...
    async def ainvoke(self, input: InputT, config: RunnableConfig | None = None) -> OutputT: ...

    def stream(
        self,
        input: InputT,
        config: RunnableConfig | None = None,
        stream_mode: StreamMode = "updates"
    ) -> Iterator: ...

    async def astream(
        self,
        input: InputT,
        config: RunnableConfig | None = None,
        stream_mode: StreamMode = "updates"
    ) -> AsyncIterator: ...
```

[Graph Execution](./graph-execution.md)

### State Management

Read and update graph state during and after execution. Access state snapshots, historical states, and modify state programmatically.

```python { .api }
class CompiledStateGraph:
    def get_state(self, config: RunnableConfig, subgraphs: bool = False) -> StateSnapshot: ...
    async def aget_state(self, config: RunnableConfig, subgraphs: bool = False) -> StateSnapshot: ...

    def get_state_history(
        self,
        config: RunnableConfig,
        filter: dict | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None
    ) -> Iterator[StateSnapshot]: ...

    def update_state(
        self,
        config: RunnableConfig,
        values: dict | Any | None = None,
        as_node: str | None = None
    ) -> RunnableConfig: ...
```

[State Management](./state-management.md)

### Channels

Implement custom state management patterns using channels. Channels control how state values are stored, updated, and aggregated.

```python { .api }
class LastValue:
    """Store the most recent value, overwriting previous values"""
    ...

class BinaryOperatorAggregate:
    """Aggregate values using a binary operator (e.g., addition, list concatenation)"""
    ...

class Topic:
    """Collect all values as a sequence"""
    ...

class EphemeralValue:
    """Temporary value cleared after each step"""
    ...
```

[Channels](./channels.md)

### Human-in-the-Loop & Interrupts

Pause graph execution at specific points to allow human inspection and intervention. Resume execution with modified state or user input.

```python { .api }
def interrupt(value: Any) -> Any:
    """Interrupt execution from within a node with a resumable value"""
    ...

class Command:
    """Command to update state and control flow upon resumption"""
    graph: str | None = None
    update: Any | None = None
    resume: dict[str, Any] | Any | None = None
    goto: Send | Sequence[Send] = ()
```

[Interrupts and Human-in-the-Loop](./interrupts.md)

### Functional API

Define workflows using Python function decorators instead of graph builders. Create parallelizable tasks and entrypoints with automatic graph generation.

```python { .api }
@task(
    name: str | None = None,
    retry_policy: RetryPolicy | Sequence[RetryPolicy] | None = None,
    cache_policy: CachePolicy | None = None,
)
def my_task(...) -> T: ...

@entrypoint(
    checkpointer: BaseCheckpointSaver | None = None,
    store: BaseStore | None = None,
    cache: BaseCache | None = None,
    context_schema: type[ContextT] | None = None,
)
def my_workflow(input: InputT) -> OutputT: ...
```

[Functional API](./functional-api.md)

### Message Handling

Specialized utilities for managing conversation messages in agent workflows. Merge, add, and manipulate message lists with automatic deduplication.

```python { .api }
def add_messages(
    left: Messages,
    right: Messages,
    format: Literal["langchain-openai"] | None = None
) -> Messages:
    """Merge message lists, updating existing messages by ID"""
    ...

class MessagesState(TypedDict):
    """Predefined state schema with messages field"""
    messages: Annotated[list[MessageLikeRepresentation], add_messages]
```

[Message Handling](./messages.md)

### Retry and Caching

Configure automatic retry behavior for failed nodes and caching policies to optimize performance.

```python { .api }
class RetryPolicy(NamedTuple):
    """Configuration for retrying failed nodes"""
    initial_interval: float = 0.5
    backoff_factor: float = 2.0
    max_interval: float = 128.0
    max_attempts: int = 3
    jitter: bool = True
    retry_on: type[Exception] | Sequence[type[Exception]] | Callable[[Exception], bool] = default_retry_on

class CachePolicy:
    """Configuration for caching node results"""
    key_func: Callable[..., str | bytes] = default_cache_key
    ttl: int | None = None
```

[Retry and Caching](./retry-caching.md)

### Runtime Context

Access runtime context, stores, and custom stream writers from within nodes.

```python { .api }
def get_config() -> RunnableConfig:
    """Get current RunnableConfig in execution context"""
    ...

def get_store() -> BaseStore:
    """Get current BaseStore from within node"""
    ...

def get_stream_writer() -> StreamWriter:
    """Get StreamWriter for custom stream output"""
    ...

def get_runtime(context_schema: type[ContextT] | None = None) -> Runtime[ContextT]:
    """Get runtime for current graph execution"""
    ...
```

[Runtime Context](./runtime-context.md)

### Low-Level Pregel API

Direct control over the graph execution engine for advanced use cases requiring fine-grained control over nodes, channels, and execution.

```python { .api }
class Pregel:
    """Low-level graph execution engine"""
    def __init__(
        self,
        nodes: dict,
        channels: dict,
        input_channels: str | list,
        output_channels: str | list,
        ...
    ): ...

class NodeBuilder:
    """Builder for configuring Pregel nodes"""
    def subscribe_to(self, *channels: str) -> Self: ...
    def read_from(self, *channels: str) -> Self: ...
    def do(self, action: RunnableLike) -> Self: ...
    def write_to(self, *channels: str, mapper: Callable | None = None) -> Self: ...
```

[Pregel API](./pregel.md)

### Types and Constants

Core type definitions, constants, and data structures used throughout LangGraph.

```python { .api }
# Constants
START: str  # First (virtual) node
END: str    # Last (virtual) node
TAG_NOSTREAM: str  # Disable streaming tag
TAG_HIDDEN: str    # Hide from tracing tag

# Stream modes
StreamMode = Literal["values", "updates", "checkpoints", "tasks", "debug", "messages", "custom"]

# State snapshot
class StateSnapshot(NamedTuple):
    values: dict[str, Any] | Any
    next: tuple[str, ...]
    config: RunnableConfig
    metadata: CheckpointMetadata | None
    created_at: str | None
    parent_config: RunnableConfig | None
    tasks: tuple[PregelTask, ...]
    interrupts: tuple[Interrupt, ...]

# Send messages to specific nodes
class Send:
    node: str
    arg: Any
```

[Types and Constants](./types-constants.md)

### Error Handling

Exception classes and error codes for handling graph execution failures.

```python { .api }
class GraphRecursionError(RecursionError):
    """Raised when graph exceeds maximum recursion steps"""
    ...

class InvalidUpdateError(Exception):
    """Raised when attempting invalid channel update"""
    ...

class EmptyChannelError(Exception):
    """Raised when reading from empty channel"""
    ...

class ErrorCode:
    GRAPH_RECURSION_LIMIT: str
    INVALID_CONCURRENT_GRAPH_UPDATE: str
    INVALID_GRAPH_NODE_RETURN_VALUE: str
    MULTIPLE_SUBGRAPHS: str
    INVALID_CHAT_HISTORY: str
```

[Error Handling](./errors.md)
