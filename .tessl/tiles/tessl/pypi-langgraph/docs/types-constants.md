# Types and Constants

Core type definitions, constants, and data structures used throughout LangGraph for state management, execution control, and graph configuration.

## Capabilities

### Constants

Standard constants for graph execution and node tagging.

```python { .api }
START: str
"""
The first (virtual) node in graph execution.

Use START when defining edges from the entry point to the first
actual node in your graph. START is a special sentinel value that
represents the beginning of graph execution.

Example:
    builder.add_edge(START, "first_node")
"""

END: str
"""
The last (virtual) node in graph execution.

Use END when defining edges that complete graph execution. END is
a special sentinel value that represents the termination point.

Example:
    builder.add_edge("last_node", END)
"""

TAG_NOSTREAM: str
"""
Tag to disable streaming for a chat model.

Add this tag to node metadata to prevent streaming output from
LLM calls within that node. Useful for nodes where you want to
receive complete responses only.

Example:
    builder.add_node("llm", llm_node)
    builder.nodes["llm"].tags.add(TAG_NOSTREAM)
"""

TAG_HIDDEN: str
"""
Tag to hide a node/edge from tracing/streaming environments.

Add this tag to node metadata to exclude it from trace logs and
stream output. Useful for internal utility nodes.

Example:
    builder.add_node("internal", internal_node)
    builder.nodes["internal"].tags.add(TAG_HIDDEN)
"""
```

### StreamMode

Control how execution output is streamed.

```python { .api }
StreamMode = Literal["values", "updates", "checkpoints", "tasks", "debug", "messages", "custom"]
"""
How to emit stream output during execution.

Modes:
    "values": Stream complete state after each node
    "updates": Stream state updates from each node (default)
    "checkpoints": Stream checkpoint metadata after each step
    "tasks": Stream task execution information
    "debug": Stream detailed debugging information
    "messages": Stream message updates (for message-based graphs)
    "custom": Stream custom events from get_stream_writer()

Example:
    for chunk in graph.stream(input, stream_mode="updates"):
        print(chunk)

    # Multiple modes
    for chunk in graph.stream(input, stream_mode=["updates", "custom"]):
        print(chunk)
"""
```

### StateSnapshot

Snapshot of graph state at a specific execution point.

```python { .api }
class StateSnapshot(NamedTuple):
    """
    Snapshot of graph state at the beginning of a step.

    Contains complete state information including current values,
    pending nodes, configuration, and task details. Snapshots are
    returned by get_state() and get_state_history().

    Fields:
        values: Current channel values (dict or custom state object)
        next: Tuple of node names to execute next (empty if complete)
        config: RunnableConfig for this snapshot with checkpoint info
        metadata: Optional checkpoint metadata
        created_at: ISO format timestamp string or None
        parent_config: Parent snapshot's config (for nested graphs) or None
        tasks: Tuple of PregelTask objects for this step
        interrupts: Tuple of pending Interrupt objects
    """
    values: dict[str, Any] | Any
    next: tuple[str, ...]
    config: RunnableConfig
    metadata: CheckpointMetadata | None
    created_at: str | None
    parent_config: RunnableConfig | None
    tasks: tuple[PregelTask, ...]
    interrupts: tuple[Interrupt, ...]
```

### PregelTask

Task information for execution tracking.

```python { .api }
class PregelTask(NamedTuple):
    """
    A task in the Pregel execution.

    Represents a single unit of work (typically a node execution)
    within a graph step. Tasks contain execution state, errors,
    interrupts, and results.

    Fields:
        id: Unique task identifier
        name: Task name (typically the node name)
        path: Execution path (tuple of step identifiers)
        error: Exception if task failed, None otherwise
        interrupts: Tuple of interrupts that occurred in this task
        state: Task state (RunnableConfig or StateSnapshot for subgraphs)
        result: Task result value
    """
    id: str
    name: str
    path: tuple[str | int | tuple, ...]
    error: Exception | None = None
    interrupts: tuple[Interrupt, ...] = ()
    state: None | RunnableConfig | StateSnapshot = None
    result: Any | None = None
```

### StateUpdate

State update with node and task context.

```python { .api }
class StateUpdate(NamedTuple):
    """
    State update with optional node and task context.

    Represents a state modification with metadata about where it
    originated. Used in bulk_update_state() operations.

    Fields:
        values: State values to update (dict of field updates or full state)
        node: Node name that produced this update (optional)
        task: Task ID that produced this update (optional)
    """
    values: dict | Any
    node: str | None = None
    task: str | None = None
```

### Durability

Persistence mode for graph execution.

```python { .api }
Durability = Literal["sync", "async", "exit"]
"""
Controls how and when state is persisted.

Modes:
    "sync": Synchronous checkpointing after each step (default)
    "async": Asynchronous checkpointing in background
    "exit": Only checkpoint when graph execution completes

Example:
    graph = builder.compile(
        checkpointer=checkpointer,
        durability="async"
    )
"""
```

### All

Special value for interrupting at all nodes.

```python { .api }
All = Literal["*"]
"""
Special value to indicate all nodes.

Use with interrupt_before or interrupt_after to interrupt at
every node in the graph.

Example:
    graph = builder.compile(
        checkpointer=checkpointer,
        interrupt_before="*"  # Interrupt before every node
    )
"""
```

### Send

Message to send to a specific node for dynamic fanout.

```python { .api }
class Send:
    """
    Message to send to a specific node.

    Use Send to dynamically route execution to specific nodes,
    typically for parallel processing (fan-out pattern).

    Fields:
        node: Target node name
        arg: State or message to send to the node

    Example:
        def fan_out(state):
            # Process each item in parallel
            return [Send("process_item", item) for item in state["items"]]

        builder.add_conditional_edges("fan_out", fan_out)
    """
    node: str
    arg: Any

    def __init__(self, node: str, arg: Any):
        """
        Create a Send message.

        Args:
            node: Target node name
            arg: Value to send to node
        """
        ...
```

### Command

Command to update state and control flow.

```python { .api }
class Command:
    """
    Command to update graph state and send to nodes.

    Commands provide fine-grained control over graph execution,
    allowing you to update state, resume from interrupts, and
    navigate to specific nodes.

    Fields:
        graph: Graph target (None=current, "__parent__"=parent graph)
        update: State update to apply
        resume: Value to resume with (for interrupt resumption)
        goto: Nodes to navigate to (Send or sequence of Send)
    """
    graph: str | None = None
    update: Any | None = None
    resume: dict[str, Any] | Any | None = None
    goto: Send | Sequence[Send] = ()

    def __init__(
        self,
        *,
        graph: str | None = None,
        update: Any | None = None,
        resume: dict[str, Any] | Any | None = None,
        goto: Send | Sequence[Send] = ()
    ):
        """
        Create a Command.

        Args:
            graph: Target graph (None=current, "__parent__"=parent)
            update: State update to apply
            resume: Value to resume with after interrupt
            goto: Nodes to send execution to
        """
        ...
```

### Overwrite

Bypass reducer and write directly to channel.

```python { .api }
class Overwrite:
    """
    Bypass reducer and write directly to BinaryOperatorAggregate channel.

    Normally, channel updates go through reducers that merge values.
    Overwrite bypasses the reducer and replaces the value directly.

    Fields:
        value: Value to write, bypassing reducer

    Example:
        # With normal update, values are merged
        return {"items": [1, 2, 3]}  # Appends to existing items

        # With Overwrite, value is replaced
        from langgraph.types import Overwrite
        return {"items": Overwrite([1, 2, 3])}  # Replaces items entirely
    """
    value: Any

    def __init__(self, value: Any):
        """
        Create an Overwrite wrapper.

        Args:
            value: Value to write directly to channel
        """
        ...
```

## Usage Examples

### Using START and END

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    value: int

builder = StateGraph(State)

builder.add_node("process", lambda s: {"value": s["value"] + 1})

# Connect from START to first node
builder.add_edge(START, "process")

# Connect from last node to END
builder.add_edge("process", END)

graph = builder.compile()
```

### Stream Modes

```python
from langgraph.graph import StateGraph, START, END

builder = StateGraph(State)
builder.add_node("step1", step1_fn)
builder.add_node("step2", step2_fn)
builder.add_edge(START, "step1")
builder.add_edge("step1", "step2")
builder.add_edge("step2", END)

graph = builder.compile()

# Stream state updates (default)
for chunk in graph.stream(input, stream_mode="updates"):
    print(f"Update: {chunk}")

# Stream complete state values
for chunk in graph.stream(input, stream_mode="values"):
    print(f"Full state: {chunk}")

# Stream multiple modes
for chunk in graph.stream(input, stream_mode=["updates", "debug"]):
    print(f"Event: {chunk}")
```

### StateSnapshot Inspection

```python
from langgraph.checkpoint.memory import MemorySaver

graph = builder.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "thread-1"}}
graph.invoke(input, config)

# Get current state snapshot
snapshot = graph.get_state(config)

print(f"Values: {snapshot.values}")
print(f"Next nodes: {snapshot.next}")
print(f"Created at: {snapshot.created_at}")
print(f"Config: {snapshot.config}")

# Check for interrupts
if snapshot.interrupts:
    for interrupt in snapshot.interrupts:
        print(f"Interrupt: {interrupt.value}")

# Inspect tasks
for task in snapshot.tasks:
    print(f"Task {task.name}: {task.id}")
    if task.error:
        print(f"  Error: {task.error}")
```

### Dynamic Routing with Send

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send
from typing_extensions import TypedDict

class State(TypedDict):
    items: list[str]
    results: list[str]

def fan_out(state: State):
    # Send each item to process_item node in parallel
    return [Send("process_item", {"item": item}) for item in state["items"]]

def process_item(item_state: dict) -> dict:
    item = item_state["item"]
    return {"results": [f"Processed: {item}"]}

builder = StateGraph(State)
builder.add_node("fan_out", fan_out)
builder.add_node("process_item", process_item)

builder.add_edge(START, "fan_out")
builder.add_conditional_edges("fan_out", lambda s: [])  # Dynamic sends
builder.add_edge("process_item", END)

graph = builder.compile()

result = graph.invoke({
    "items": ["a", "b", "c"],
    "results": []
})
# All items processed in parallel
```

### Command for Flow Control

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, Send

def router(state: State):
    if state["error"]:
        # Update state and go to error handler
        return Command(
            update={"status": "error"},
            goto=Send("handle_error", state)
        )
    else:
        # Update state and continue to success path
        return Command(
            update={"status": "success"},
            goto=Send("process", state)
        )

builder = StateGraph(State)
builder.add_node("router", router)
builder.add_node("handle_error", handle_error_fn)
builder.add_node("process", process_fn)
builder.add_edge(START, "router")
builder.add_conditional_edges("router", lambda s: [])
```

### Resuming with Command

```python
from langgraph.types import Command, interrupt

def node_with_interrupt(state):
    # Interrupt and wait for user input
    user_input = interrupt("Need input")

    return {"result": f"Got: {user_input}"}

graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "thread-1"}}

# Stream until interrupt
for chunk in graph.stream(input, config):
    print(chunk)

# Resume with value
result = graph.invoke(
    Command(resume="user provided value"),
    config
)
```

### Using Overwrite

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Overwrite
from typing_extensions import TypedDict, Annotated
from operator import add

class State(TypedDict):
    items: Annotated[list[str], add]  # List concatenation reducer

builder = StateGraph(State)

def normal_update(state: State):
    # Appends to existing items (uses add reducer)
    return {"items": ["new_item"]}

def replace_items(state: State):
    # Replaces items entirely (bypasses add reducer)
    return {"items": Overwrite(["only_item"])}

builder.add_node("append", normal_update)
builder.add_node("replace", replace_items)

builder.add_edge(START, "append")
builder.add_edge("append", "replace")
builder.add_edge("replace", END)

graph = builder.compile()

result = graph.invoke({"items": ["initial"]})
print(result["items"])  # ["only_item"] - replaced, not appended
```

### Interrupt All Nodes

```python
from langgraph.checkpoint.memory import MemorySaver

# Interrupt before every node
graph = builder.compile(
    checkpointer=MemorySaver(),
    interrupt_before="*"  # Special All value
)

config = {"configurable": {"thread_id": "thread-1"}}

# Step through execution node by node
graph.invoke(input, config)

while True:
    snapshot = graph.get_state(config)
    if not snapshot.next:
        break

    print(f"About to execute: {snapshot.next}")
    graph.invoke(None, config)  # Continue one step
```

### Durability Modes

```python
from langgraph.checkpoint.memory import MemorySaver

# Synchronous checkpointing (default)
graph_sync = builder.compile(
    checkpointer=MemorySaver(),
    durability="sync"
)

# Asynchronous checkpointing
graph_async = builder.compile(
    checkpointer=MemorySaver(),
    durability="async"
)

# Only checkpoint on exit
graph_exit = builder.compile(
    checkpointer=MemorySaver(),
    durability="exit"
)
```

### StateUpdate for Bulk Operations

```python
from langgraph.types import StateUpdate

# Prepare multiple updates with node context
updates = [
    [StateUpdate(values={"count": 5}, node="counter")],
    [StateUpdate(values={"message": "updated"}, node="logger")]
]

# Apply all updates atomically
config = graph.bulk_update_state(config, updates)
```

### Tags for Node Behavior

```python
from langgraph.constants import TAG_NOSTREAM, TAG_HIDDEN

builder = StateGraph(State)

# Add node with no streaming
builder.add_node("llm", llm_node)
builder.nodes["llm"].tags.add(TAG_NOSTREAM)

# Add hidden utility node
builder.add_node("internal", internal_node)
builder.nodes["internal"].tags.add(TAG_HIDDEN)

graph = builder.compile()

# llm node won't stream, internal node won't appear in traces
```

### Parent Graph Commands

```python
from langgraph.types import Command

def subgraph_node(state):
    # Command parent graph from within subgraph
    return Command(
        graph="__parent__",
        update={"parent_field": "updated from child"}
    )

# Useful for nested graph communication
```

## Types

### Checkpointer

```python { .api }
Checkpointer = None | bool | BaseCheckpointSaver
"""
Checkpointer configuration type.

Values:
    None: No checkpointing
    True: Use default in-memory checkpointer
    BaseCheckpointSaver: Custom checkpointer implementation
"""
```

### StreamWriter

```python { .api }
StreamWriter = Callable[[Any], None]
"""
Function type for custom stream output.

Accepts any JSON-serializable value to emit as a custom stream event.
"""
```

### Interrupt

```python { .api }
class Interrupt:
    """
    Information about an interrupt in a node.

    Fields:
        value: The value associated with the interrupt
        id: The interrupt ID used for resumption
    """
    value: Any
    id: str
```

### RunnableConfig

```python { .api }
class RunnableConfig(TypedDict):
    """
    Configuration for graph execution.

    Fields:
        configurable: Dict with thread_id, checkpoint_id, context, etc.
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

### CheckpointMetadata

```python { .api }
class CheckpointMetadata(TypedDict):
    """
    Metadata for a checkpoint.

    Contains information about the checkpoint creation context,
    including source, step, and custom metadata.
    """
    source: str
    step: int
    writes: dict[str, Any]
    parents: dict[str, str]
```
