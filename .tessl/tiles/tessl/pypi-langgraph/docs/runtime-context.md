# Runtime Context

Access runtime context, stores, and custom stream writers from within nodes. Runtime utilities provide access to configuration, persistent storage, and custom output streaming during graph execution.

## Capabilities

### get_config

Get the current RunnableConfig in the execution context.

```python { .api }
def get_config() -> RunnableConfig:
    """
    Get current RunnableConfig in execution context.

    Access the configuration for the current graph execution, including
    thread_id, checkpoint_id, and other configuration values. Must be
    called from within a node during graph execution.

    Returns:
        RunnableConfig with thread_id, checkpoint info, and configuration

    Raises:
        RuntimeError: If called outside of graph execution context

    Example:
        def my_node(state):
            config = get_config()
            thread_id = config["configurable"]["thread_id"]
            return {"result": f"Running in thread {thread_id}"}
    """
    ...
```

### get_store

Get the current BaseStore from within a node.

```python { .api }
def get_store() -> BaseStore:
    """
    Get current BaseStore from within node.

    Access the key-value store configured for this graph execution.
    The store provides persistent storage across executions and can
    be used for long-term data that outlives individual graph runs.

    Returns:
        BaseStore instance for persistent storage

    Raises:
        RuntimeError: If no store configured or called outside execution context

    Example:
        def my_node(state):
            store = get_store()
            value = store.get("my_key")
            store.put("my_key", "new_value")
            return state
    """
    ...
```

### get_stream_writer

Get the StreamWriter for custom stream output.

```python { .api }
def get_stream_writer() -> StreamWriter:
    """
    Get StreamWriter for custom stream output.

    Access the stream writer to emit custom stream events during graph
    execution. Useful for streaming progress updates, intermediate results,
    or custom events to the caller.

    Returns:
        StreamWriter function that accepts any value to stream

    Example:
        def my_node(state):
            writer = get_stream_writer()
            writer({"type": "progress", "status": "processing"})
            # Do work
            writer({"type": "progress", "status": "complete"})
            return state
    """
    ...
```

### Runtime

Bundle run-scoped context, store, stream writer, and previous state.

```python { .api }
class Runtime(Generic[ContextT]):
    """
    Bundles run-scoped context, store, stream writer, and previous state.

    Runtime provides access to all execution-scoped resources in a single
    object. Use get_runtime() to access the runtime from within nodes.

    Fields:
        context: Run-scoped context (e.g., user_id, db_connection, api_keys)
        store: Key-value store for persistent data
        stream_writer: Function for custom stream output
        previous: Previous entrypoint return value (with checkpointer only)
    """
    context: ContextT = None
    store: BaseStore | None = None
    stream_writer: StreamWriter = lambda x: None  # no-op default
    previous: Any = None

    def merge(self, other: Runtime[ContextT]) -> Runtime[ContextT]:
        """
        Merge two runtimes.

        Creates a new runtime by merging fields from two runtimes.
        Non-None values from 'other' override values from 'self'.

        Args:
            other: Runtime to merge with

        Returns:
            New merged Runtime instance
        """
        ...

    def override(self, **overrides: _RuntimeOverrides[ContextT]) -> Runtime[ContextT]:
        """
        Replace runtime values.

        Create a new runtime with specified fields replaced.

        Args:
            **overrides: Fields to override (context, store, stream_writer, previous)

        Returns:
            New Runtime with overridden values

        Example:
            new_runtime = runtime.override(
                context={"user_id": "new_user"},
                store=new_store
            )
        """
        ...
```

### get_runtime

Get the runtime for the current graph execution.

```python { .api }
def get_runtime(
    context_schema: type[ContextT] | None = None
) -> Runtime[ContextT]:
    """
    Get runtime for current graph execution.

    Access all execution-scoped resources (context, store, stream writer,
    previous state) in a single call. More convenient than calling
    get_config(), get_store(), and get_stream_writer() separately.

    Args:
        context_schema: Optional context type for type checking

    Returns:
        Runtime instance with context, store, stream_writer, and previous

    Raises:
        RuntimeError: If called outside of graph execution context

    Example:
        def my_node(state):
            runtime = get_runtime()
            user_id = runtime.context["user_id"]
            runtime.store.put(f"user:{user_id}", state)
            runtime.stream_writer({"event": "processed"})
            return state
    """
    ...
```

## Usage Examples

### Access Thread ID

```python
from langgraph.graph import StateGraph, START, END
from langgraph.config import get_config
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

class State(TypedDict):
    message: str
    thread: str

def log_thread(state: State) -> dict:
    config = get_config()
    thread_id = config["configurable"]["thread_id"]
    return {"thread": thread_id}

builder = StateGraph(State)
builder.add_node("log", log_thread)
builder.add_edge(START, "log")
builder.add_edge("log", END)

graph = builder.compile(checkpointer=MemorySaver())

result = graph.invoke(
    {"message": "test", "thread": ""},
    {"configurable": {"thread_id": "thread-123"}}
)

print(result["thread"])  # "thread-123"
```

### Using Store for Persistence

```python
from langgraph.graph import StateGraph, START, END
from langgraph.config import get_store
from langgraph.store.memory import InMemoryStore
from typing_extensions import TypedDict

class State(TypedDict):
    user_id: str
    count: int

def increment_user_count(state: State) -> dict:
    store = get_store()
    user_id = state["user_id"]

    # Get current count from store
    key = f"user:{user_id}:count"
    current = store.get(key) or 0

    # Increment and save
    new_count = current + 1
    store.put(key, new_count)

    return {"count": new_count}

builder = StateGraph(State)
builder.add_node("increment", increment_user_count)
builder.add_edge(START, "increment")
builder.add_edge("increment", END)

store = InMemoryStore()
graph = builder.compile(store=store)

# Each invocation increments the user's count in the store
result1 = graph.invoke({"user_id": "user-1", "count": 0})
print(result1["count"])  # 1

result2 = graph.invoke({"user_id": "user-1", "count": 0})
print(result2["count"])  # 2
```

### Custom Stream Events

```python
from langgraph.graph import StateGraph, START, END
from langgraph.config import get_stream_writer
from typing_extensions import TypedDict

class State(TypedDict):
    items: list[str]
    processed: list[str]

def process_items(state: State) -> dict:
    writer = get_stream_writer()
    processed = []

    for i, item in enumerate(state["items"]):
        # Stream progress event
        writer({
            "type": "progress",
            "current": i + 1,
            "total": len(state["items"]),
            "item": item
        })

        # Process item
        result = f"Processed: {item}"
        processed.append(result)

    # Stream completion event
    writer({"type": "complete", "count": len(processed)})

    return {"processed": processed}

builder = StateGraph(State)
builder.add_node("process", process_items)
builder.add_edge(START, "process")
builder.add_edge("process", END)

graph = builder.compile()

# Stream custom events along with normal output
for chunk in graph.stream(
    {"items": ["a", "b", "c"], "processed": []},
    stream_mode=["updates", "custom"]
):
    print(chunk)
# Prints progress events and final result
```

### Using Runtime Context

```python
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import get_runtime
from typing_extensions import TypedDict

class State(TypedDict):
    query: str
    result: str

class Context(TypedDict):
    user_id: str
    api_key: str

def search_with_context(state: State) -> dict:
    runtime = get_runtime(Context)

    # Access context
    user_id = runtime.context["user_id"]
    api_key = runtime.context["api_key"]

    # Use store
    if runtime.store:
        search_history = runtime.store.get(f"history:{user_id}") or []
        search_history.append(state["query"])
        runtime.store.put(f"history:{user_id}", search_history)

    # Stream progress
    runtime.stream_writer({"status": "searching", "query": state["query"]})

    # Perform search with API key
    result = f"Search result for {state['query']} (user: {user_id})"

    return {"result": result}

builder = StateGraph(State, context_schema=Context)
builder.add_node("search", search_with_context)
builder.add_edge(START, "search")
builder.add_edge("search", END)

graph = builder.compile(store=InMemoryStore())

result = graph.invoke(
    {"query": "test", "result": ""},
    {
        "configurable": {
            "thread_id": "thread-1",
            "context": {
                "user_id": "user-123",
                "api_key": "secret"
            }
        }
    }
)
```

### Accessing Previous State

```python
from langgraph.graph import StateGraph, START, END
from langgraph.runtime import get_runtime
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

class State(TypedDict):
    value: int

def check_previous(state: State) -> dict:
    runtime = get_runtime()

    if runtime.previous is not None:
        prev_value = runtime.previous.get("value", 0)
        print(f"Previous value: {prev_value}")

    return {"value": state["value"] + 1}

builder = StateGraph(State)
builder.add_node("increment", check_previous)
builder.add_edge(START, "increment")
builder.add_edge("increment", END)

# Previous state requires checkpointer
graph = builder.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "thread-1"}}

# First run - no previous
result1 = graph.invoke({"value": 0}, config)

# Second run - has previous
result2 = graph.invoke({"value": 10}, config)
# Prints: "Previous value: 1"
```

### Runtime Merge and Override

```python
from langgraph.runtime import Runtime

# Create base runtime
runtime1 = Runtime(
    context={"user_id": "user-1"},
    store=store1
)

runtime2 = Runtime(
    context={"api_key": "secret"},
    stream_writer=custom_writer
)

# Merge runtimes
merged = runtime1.merge(runtime2)
# merged has: user_id, api_key, store1, custom_writer

# Override specific fields
overridden = runtime1.override(
    context={"user_id": "user-2"},
    store=store2
)
# overridden has: user_id=user-2, store2
```

### Conditional Store Usage

```python
from langgraph.config import get_store
from typing_extensions import TypedDict

class State(TypedDict):
    key: str
    value: str
    cached: bool

def maybe_cache(state: State) -> dict:
    try:
        store = get_store()
        # Store is available
        store.put(state["key"], state["value"])
        return {"cached": True}
    except RuntimeError:
        # No store configured
        return {"cached": False}

# Works whether or not store is configured
```

### Multiple Custom Stream Events

```python
from langgraph.config import get_stream_writer

def complex_operation(state):
    writer = get_stream_writer()

    # Stream different event types
    writer({"type": "start", "timestamp": time.time()})

    for step in ["prepare", "process", "finalize"]:
        writer({"type": "step", "name": step, "status": "running"})
        # Do work
        writer({"type": "step", "name": step, "status": "complete"})

    writer({"type": "end", "duration": time.time() - start})

    return state

# Consume custom events
for chunk in graph.stream(input, stream_mode="custom"):
    event = chunk[1]  # Custom events are in second position
    print(f"{event['type']}: {event}")
```

### Database Connection in Context

```python
from langgraph.runtime import get_runtime
from typing_extensions import TypedDict

class State(TypedDict):
    query: str
    results: list[dict]

class Context(TypedDict):
    db_connection: Any
    user_id: str

def query_database(state: State) -> dict:
    runtime = get_runtime(Context)

    # Use database connection from context
    db = runtime.context["db_connection"]
    user_id = runtime.context["user_id"]

    # Execute query with user context
    results = db.execute(state["query"], user_id=user_id)

    return {"results": results}

# Pass database connection via context
with db.connection() as conn:
    result = graph.invoke(
        {"query": "SELECT * FROM items", "results": []},
        {
            "configurable": {
                "thread_id": "thread-1",
                "context": {
                    "db_connection": conn,
                    "user_id": "user-123"
                }
            }
        }
    )
```

### Async Runtime Access

```python
import asyncio
from langgraph.runtime import get_runtime

async def async_node(state: State) -> dict:
    runtime = get_runtime()

    # All runtime utilities work in async context
    config = get_config()
    store = get_store()
    writer = get_stream_writer()

    # Async store operations
    if hasattr(store, 'aget'):
        value = await store.aget("key")

    writer({"status": "async_processing"})

    return state
```

## Types

### RunnableConfig

```python { .api }
class RunnableConfig(TypedDict):
    """
    Configuration for graph execution.

    Fields:
        configurable: Dict with thread_id, checkpoint_id, and custom config
        tags: List of tags for tracing
        metadata: Dict of metadata
        recursion_limit: Maximum execution steps
        callbacks: Callback handlers
    """
    configurable: dict[str, Any]
    tags: list[str]
    metadata: dict[str, Any]
    recursion_limit: int
    callbacks: list[Any]
```

### StreamWriter

```python { .api }
StreamWriter = Callable[[Any], None]
"""
Function type for custom stream output.

Accepts any value to emit as a custom stream event.
The value should be JSON-serializable.
"""
```

### BaseStore

```python { .api }
class BaseStore:
    """
    Abstract base class for key-value stores.

    Stores provide persistent storage across graph executions.
    Common implementations: InMemoryStore, RedisStore, etc.

    Key methods:
        get(key: str) -> Any: Retrieve value by key
        put(key: str, value: Any) -> None: Store value
        delete(key: str) -> None: Remove value
        list(prefix: str) -> list[str]: List keys with prefix
    """
    ...
```

### ContextT

```python { .api }
ContextT = TypeVar('ContextT', bound=StateLike | None, default=None)
"""
Type variable for run-scoped context.

Context provides execution-scoped data like user IDs, database
connections, API keys, etc. Context is passed via config and
accessed through get_runtime() or by defining a context_schema.
"""
```
