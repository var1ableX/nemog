# State Management

Read and update graph state during and after execution. Access current state snapshots, navigate historical states, and programmatically modify state at any point in the execution timeline.

## Capabilities

### Get Current State

Retrieve the current state of a graph execution.

```python { .api }
class CompiledStateGraph:
    def get_state(
        self,
        config: RunnableConfig,
        subgraphs: bool = False
    ) -> StateSnapshot:
        """
        Get current state snapshot for a graph execution.

        Args:
            config: Configuration with thread_id for the execution
            subgraphs: Include state from subgraphs

        Returns:
            StateSnapshot with current values, next nodes, and metadata
        """
        ...

    async def aget_state(
        self,
        config: RunnableConfig,
        subgraphs: bool = False
    ) -> StateSnapshot:
        """
        Get current state snapshot asynchronously.

        Args: Same as get_state()

        Returns:
            StateSnapshot with current values, next nodes, and metadata
        """
        ...
```

### Get State History

Retrieve historical state snapshots for a graph execution.

```python { .api }
class CompiledStateGraph:
    def get_state_history(
        self,
        config: RunnableConfig,
        filter: dict | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None
    ) -> Iterator[StateSnapshot]:
        """
        Get historical state snapshots in reverse chronological order.

        Args:
            config: Configuration with thread_id for the execution
            filter: Optional filter criteria for snapshots
            before: Only return snapshots before this config
            limit: Maximum number of snapshots to return

        Yields:
            StateSnapshot objects from newest to oldest
        """
        ...

    async def aget_state_history(
        self,
        config: RunnableConfig,
        filter: dict | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None
    ) -> AsyncIterator[StateSnapshot]:
        """
        Get historical state snapshots asynchronously.

        Args: Same as get_state_history()

        Yields:
            StateSnapshot objects from newest to oldest
        """
        ...
```

### Update State

Programmatically update graph state.

```python { .api }
class CompiledStateGraph:
    def update_state(
        self,
        config: RunnableConfig,
        values: dict | Any | None = None,
        as_node: str | None = None
    ) -> RunnableConfig:
        """
        Update graph state programmatically.

        Args:
            config: Configuration with thread_id for the execution
            values: State updates to apply (dict of field updates or full state)
            as_node: Apply update as if it came from this node (affects reducers)

        Returns:
            Updated RunnableConfig with new checkpoint_id

        Note:
            Updates are applied using the same channel reducers as during
            normal execution. Use as_node to control which node's logic applies.
        """
        ...

    async def aupdate_state(
        self,
        config: RunnableConfig,
        values: dict | Any | None = None,
        as_node: str | None = None
    ) -> RunnableConfig:
        """
        Update graph state asynchronously.

        Args: Same as update_state()

        Returns:
            Updated RunnableConfig with new checkpoint_id
        """
        ...
```

### Bulk Update State

Apply multiple state updates atomically.

```python { .api }
class CompiledStateGraph:
    def bulk_update_state(
        self,
        config: RunnableConfig,
        updates: Sequence[Sequence[StateUpdate]]
    ) -> RunnableConfig:
        """
        Apply multiple state updates in a single operation.

        Args:
            config: Configuration with thread_id for the execution
            updates: Sequence of update sequences to apply

        Returns:
            Updated RunnableConfig with new checkpoint_id
        """
        ...

    async def abulk_update_state(
        self,
        config: RunnableConfig,
        updates: Sequence[Sequence[StateUpdate]]
    ) -> RunnableConfig:
        """
        Apply multiple state updates asynchronously.

        Args: Same as bulk_update_state()

        Returns:
            Updated RunnableConfig with new checkpoint_id
        """
        ...
```

## Usage Examples

### Get Current State

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

class State(TypedDict):
    count: int
    message: str

builder = StateGraph(State)
builder.add_node("increment", lambda s: {"count": s["count"] + 1})
builder.add_edge(START, "increment")
builder.add_edge("increment", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "thread-1"}}

# Execute graph
result = graph.invoke({"count": 0, "message": "hello"}, config)

# Get current state
state = graph.get_state(config)
print(state.values)  # {'count': 1, 'message': 'hello'}
print(state.next)    # () - no pending nodes
print(state.config)  # RunnableConfig with checkpoint info
```

### Check Next Nodes

```python
# With interrupt before a node
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["increment"]
)

config = {"configurable": {"thread_id": "thread-2"}}
graph.invoke({"count": 0, "message": "hello"}, config)

# Check what's next
state = graph.get_state(config)
print(state.next)  # ('increment',) - interrupted before this node
print(state.values)  # {'count': 0, 'message': 'hello'} - not yet incremented
```

### Browse State History

```python
# Execute multiple steps
for i in range(5):
    graph.invoke({"count": i, "message": f"step {i}"}, config)

# Get history (newest first)
for snapshot in graph.get_state_history(config, limit=3):
    print(f"Checkpoint at {snapshot.created_at}")
    print(f"  Values: {snapshot.values}")
    print(f"  Next nodes: {snapshot.next}")
```

### Update State Externally

```python
config = {"configurable": {"thread_id": "thread-3"}}

# Execute initial state
graph.invoke({"count": 0, "message": "start"}, config)

# Get current state
state = graph.get_state(config)
print(state.values)  # {'count': 1, 'message': 'start'}

# Update state externally
new_config = graph.update_state(
    config,
    {"count": 10, "message": "updated"}
)

# Verify update
state = graph.get_state(new_config)
print(state.values)  # {'count': 10, 'message': 'updated'}
```

### Update as Specific Node

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated
from operator import add

class State(TypedDict):
    items: Annotated[list[str], add]  # List concatenation reducer

def node_a(state: State) -> dict:
    return {"items": ["from_a"]}

def node_b(state: State) -> dict:
    return {"items": ["from_b"]}

builder = StateGraph(State)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_edge(START, "node_a")
builder.add_edge("node_a", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "thread-4"}}

# Execute
graph.invoke({"items": []}, config)
state = graph.get_state(config)
print(state.values)  # {'items': ['from_a']}

# Update as node_b (uses concatenation reducer)
new_config = graph.update_state(
    config,
    {"items": ["from_b"]},
    as_node="node_b"
)

state = graph.get_state(new_config)
print(state.values)  # {'items': ['from_a', 'from_b']}
```

### Resume from Historical State

```python
# Execute multiple times
for i in range(3):
    config = {"configurable": {"thread_id": "thread-5"}}
    graph.invoke({"count": i, "message": f"step {i}"}, config)

# Get history
history = list(graph.get_state_history(config, limit=3))

# Resume from second-to-last checkpoint
old_checkpoint = history[1]  # Second newest
print(f"Resuming from: {old_checkpoint.values}")

# Continue execution from that point
result = graph.invoke(None, old_checkpoint.config)
print(f"Result: {result}")
```

### State with Subgraphs

```python
# For graphs containing subgraphs
state = graph.get_state(config, subgraphs=True)

# state.tasks will contain subgraph states
for task in state.tasks:
    if task.state:
        print(f"Subgraph {task.name} state: {task.state}")
```

### Async State Operations

```python
import asyncio

async def async_state_operations():
    # Async state retrieval
    state = await graph.aget_state(config)
    print(state.values)

    # Async state update
    new_config = await graph.aupdate_state(
        config,
        {"count": 20}
    )

    # Async history
    async for snapshot in graph.aget_state_history(config, limit=5):
        print(f"Historic state: {snapshot.values}")

asyncio.run(async_state_operations())
```

### Bulk State Updates

```python
from langgraph.types import StateUpdate

# Prepare multiple updates
updates = [
    [StateUpdate(values={"count": 5}, node="node_a")],
    [StateUpdate(values={"message": "bulk update"}, node="node_b")]
]

# Apply all updates atomically
new_config = graph.bulk_update_state(config, updates)

state = graph.get_state(new_config)
print(state.values)
```

## Types

### StateSnapshot

```python { .api }
class StateSnapshot(NamedTuple):
    """
    Snapshot of graph state at a specific point in execution.

    Fields:
        values: Current state values (dict or custom state object)
        next: Tuple of node names to execute next (empty if execution complete)
        config: RunnableConfig for this snapshot with checkpoint information
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

### StateUpdate

```python { .api }
class StateUpdate(NamedTuple):
    """
    State update with optional node and task context.

    Fields:
        values: State values to update
        node: Node name that produced this update (optional)
        task: Task that produced this update (optional)
    """
    values: dict | Any
    node: str | None = None
    task: str | None = None
```

### PregelTask

```python { .api }
class PregelTask(NamedTuple):
    """
    A task in the Pregel execution.

    Fields:
        id: Unique task identifier
        name: Task name (typically node name)
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
