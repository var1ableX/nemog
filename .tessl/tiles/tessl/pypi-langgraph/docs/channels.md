# Channels

Channels control how state values are stored, updated, and aggregated in LangGraph. They define the behavior of state fields, including how multiple updates are combined and when values are cleared.

## Capabilities

### Base Channel

Abstract base class for all channel implementations.

```python { .api }
class BaseChannel:
    """
    Base class for all channel types.

    Channels manage individual state fields and control update behavior.
    """

    def get(self) -> Value:
        """Get current channel value"""
        ...

    def update(self, updates: Sequence[Update]) -> bool:
        """
        Apply updates to the channel.

        Args:
            updates: Sequence of update values

        Returns:
            True if channel value changed
        """
        ...

    def checkpoint(self) -> Checkpoint:
        """Serialize channel state for checkpointing"""
        ...

    @classmethod
    def from_checkpoint(cls, checkpoint: Checkpoint) -> Self:
        """Restore channel from checkpoint"""
        ...

    def is_available(self) -> bool:
        """Check if channel has a value"""
        ...

    def copy(self) -> Self:
        """Create a copy of the channel"""
        ...
```

### LastValue

Store the most recent value, overwriting previous values.

```python { .api }
class LastValue:
    """
    Channel that stores only the latest value.

    Each update replaces the previous value completely.
    This is the default channel type for state fields.

    Example:
        class State(TypedDict):
            counter: int  # Uses LastValue by default

        # Update 1: counter = 5
        # Update 2: counter = 10
        # Final value: 10
    """
    ...
```

### BinaryOperatorAggregate

Aggregate values using a binary operator (e.g., addition, list concatenation).

```python { .api }
class BinaryOperatorAggregate:
    """
    Channel that aggregates values using a binary operator.

    Common operators:
    - operator.add: Addition for numbers, concatenation for lists/strings
    - operator.or_: Union for sets
    - Custom functions: lambda a, b: custom_merge(a, b)

    Example:
        from operator import add
        from typing_extensions import Annotated

        class State(TypedDict):
            # List concatenation
            items: Annotated[list[str], add]
            # Number addition
            total: Annotated[int, add]

        # items: [] + ["a"] + ["b", "c"] = ["a", "b", "c"]
        # total: 0 + 5 + 10 = 15
    """
    ...
```

### Topic

Collect all values as a sequence without aggregation.

```python { .api }
class Topic:
    """
    Channel that accumulates all values in order.

    Unlike BinaryOperatorAggregate with add, Topic maintains each
    value as a separate item rather than merging them.

    Example:
        class State(TypedDict):
            updates: Annotated[list, Topic]

        # Update 1: {"updates": [1, 2]}
        # Update 2: {"updates": [3]}
        # Final value: [[1, 2], [3]] (not [1, 2, 3])
    """
    ...
```

### EphemeralValue

Temporary value cleared after each step.

```python { .api }
class EphemeralValue:
    """
    Channel that stores a value temporarily.

    The value is available within a single step but is automatically
    cleared before the next step begins. Useful for one-time signals
    or temporary data that shouldn't persist.

    Example:
        class State(TypedDict):
            signal: Annotated[str, EphemeralValue]
            data: str

        # Step 1: signal="process", data="input"
        # Step 2: signal is cleared automatically, data persists
    """
    ...
```

### LastValueAfterFinish

Like LastValue but only updates after step completion.

```python { .api }
class LastValueAfterFinish:
    """
    Channel that updates only after a step finishes.

    Unlike LastValue which updates immediately, this channel waits
    until all nodes in the current step complete before updating.
    Useful for synchronization across parallel nodes.

    Example:
        class State(TypedDict):
            status: Annotated[str, LastValueAfterFinish]

        # Parallel nodes both update status
        # Final status is set only after both complete
    """
    ...
```

### AnyValue

Accept and store any value without special behavior.

```python { .api }
class AnyValue:
    """
    Channel that accepts any value with no special update logic.

    Similar to LastValue but with looser constraints.
    """
    ...
```

### NamedBarrierValue

Wait for all named sources to update before providing value.

```python { .api }
class NamedBarrierValue:
    """
    Channel that requires updates from all specified sources.

    Value becomes available only after all named sources have
    provided updates. Useful for synchronization patterns where
    a node should only execute after multiple upstream nodes complete.

    Example:
        # Channel configured to wait for "node_a" and "node_b"
        # Value is None until both nodes have updated
        # After both update, value becomes available
    """
    ...
```

### NamedBarrierValueAfterFinish

NamedBarrierValue that updates after step completion.

```python { .api }
class NamedBarrierValueAfterFinish:
    """
    NamedBarrierValue that updates only after step finishes.

    Combines barrier synchronization with deferred updates.
    """
    ...
```

### UntrackedValue

Value not tracked in checkpoints.

```python { .api }
class UntrackedValue:
    """
    Channel whose value is not saved to checkpoints.

    Useful for transient data that doesn't need persistence,
    such as cache or temporary computation results.

    Example:
        class State(TypedDict):
            data: str  # Saved to checkpoints
            cache: Annotated[dict, UntrackedValue]  # Not saved
    """
    ...
```

## Usage Examples

### LastValue (Default Behavior)

```python
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

class State(TypedDict):
    value: int  # LastValue by default

def node_a(state: State) -> dict:
    return {"value": 10}

def node_b(state: State) -> dict:
    return {"value": 20}  # Overwrites previous value

builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", END)

graph = builder.compile()
result = graph.invoke({"value": 0})
print(result["value"])  # 20 (last value wins)
```

### BinaryOperatorAggregate for List Concatenation

```python
from operator import add
from typing_extensions import Annotated

class State(TypedDict):
    items: Annotated[list[str], add]  # List concatenation

def node_a(state: State) -> dict:
    return {"items": ["a", "b"]}

def node_b(state: State) -> dict:
    return {"items": ["c"]}

builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", END)

graph = builder.compile()
result = graph.invoke({"items": []})
print(result["items"])  # ['a', 'b', 'c']
```

### BinaryOperatorAggregate for Number Addition

```python
from operator import add
from typing_extensions import Annotated

class State(TypedDict):
    total: Annotated[int, add]
    count: Annotated[int, add]

def node_a(state: State) -> dict:
    return {"total": 10, "count": 1}

def node_b(state: State) -> dict:
    return {"total": 20, "count": 1}

builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", END)

graph = builder.compile()
result = graph.invoke({"total": 0, "count": 0})
print(result)  # {'total': 30, 'count': 2}
```

### Custom Binary Operator

```python
from typing_extensions import Annotated

def merge_dicts(a: dict, b: dict) -> dict:
    """Custom merge function"""
    return {**a, **b}

class State(TypedDict):
    metadata: Annotated[dict, merge_dicts]

def node_a(state: State) -> dict:
    return {"metadata": {"key1": "value1"}}

def node_b(state: State) -> dict:
    return {"metadata": {"key2": "value2"}}

builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", END)

graph = builder.compile()
result = graph.invoke({"metadata": {}})
print(result["metadata"])  # {'key1': 'value1', 'key2': 'value2'}
```

### EphemeralValue for One-Time Signals

```python
from langgraph.channels import EphemeralValue
from typing_extensions import Annotated

class State(TypedDict):
    data: str
    trigger: Annotated[str | None, EphemeralValue]

def node_a(state: State) -> dict:
    # Set ephemeral trigger
    return {"data": "processed", "trigger": "done"}

def node_b(state: State) -> dict:
    # Trigger is automatically cleared before this node
    trigger = state.get("trigger")  # None
    return {"data": state["data"] + "_more"}

builder = StateGraph(State)
builder.add_node("a", node_a)
builder.add_node("b", node_b)
builder.add_edge(START, "a")
builder.add_edge("a", "b")
builder.add_edge("b", END)

graph = builder.compile()
result = graph.invoke({"data": "", "trigger": None})
print(result)  # {'data': 'processed_more', 'trigger': None}
```

### UntrackedValue for Cache

```python
from langgraph.channels import UntrackedValue
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import Annotated

class State(TypedDict):
    query: str
    result: str
    cache: Annotated[dict, UntrackedValue]  # Not saved to checkpoints

def process(state: State) -> dict:
    # Use cache
    if state["query"] in state.get("cache", {}):
        result = state["cache"][state["query"]]
    else:
        result = f"Computed: {state['query']}"

    # Update cache (won't be in checkpoint)
    new_cache = state.get("cache", {})
    new_cache[state["query"]] = result

    return {"result": result, "cache": new_cache}

builder = StateGraph(State)
builder.add_node("process", process)
builder.add_edge(START, "process")
builder.add_edge("process", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "1"}}
result = graph.invoke(
    {"query": "test", "result": "", "cache": {}},
    config
)

# Get state - cache is not in checkpoint
state = graph.get_state(config)
print("cache" in state.values)  # False (not persisted)
print("result" in state.values)  # True (persisted)
```

### Parallel Updates with BinaryOperatorAggregate

```python
from operator import add
from typing_extensions import Annotated
from langgraph.types import Send

class State(TypedDict):
    items: list[int]
    results: Annotated[list[str], add]

def fan_out(state: State) -> list[Send]:
    return [Send("process", item) for item in state["items"]]

def process(item: int) -> dict:
    return {"results": [f"result_{item}"]}

builder = StateGraph(State)
builder.add_node("fan_out", fan_out)
builder.add_node("process", process)
builder.add_edge(START, "fan_out")
builder.add_conditional_edges("fan_out", lambda x: [])
builder.add_edge("process", END)

graph = builder.compile()
result = graph.invoke({"items": [1, 2, 3], "results": []})
print(result["results"])
# All parallel results aggregated: ['result_1', 'result_2', 'result_3']
```

## Channel Selection Guide

| Channel Type | Use When |
|-------------|----------|
| `LastValue` | Default behavior - latest value overwrites previous |
| `BinaryOperatorAggregate` | Accumulating values (lists, sums, merges) |
| `Topic` | Need all update values as separate items |
| `EphemeralValue` | Temporary signals/data that shouldn't persist |
| `UntrackedValue` | Transient data that doesn't need checkpointing |
| `LastValueAfterFinish` | Synchronize updates across parallel nodes |
| `NamedBarrierValue` | Wait for multiple specific sources |
| `AnyValue` | Flexible value storage |

## Types

### Annotated

```python { .api }
from typing_extensions import Annotated

# Syntax for custom channel behavior
FieldType = Annotated[BaseType, ChannelOrReducer]

# Examples:
items: Annotated[list[str], add]  # BinaryOperatorAggregate
signal: Annotated[str, EphemeralValue]  # EphemeralValue
cache: Annotated[dict, UntrackedValue]  # UntrackedValue
```
