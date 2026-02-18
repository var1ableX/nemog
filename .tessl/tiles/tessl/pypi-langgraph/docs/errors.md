# Error Handling

Exception classes and error codes for handling graph execution failures, invalid updates, and other error conditions in LangGraph.

## Capabilities

### GraphRecursionError

Exception raised when graph exceeds maximum recursion depth.

```python { .api }
class GraphRecursionError(RecursionError):
    """
    Raised when graph exceeds maximum recursion steps.

    This error occurs when a graph executes more steps than allowed
    by the recursion_limit. This typically indicates an infinite loop
    or a graph that needs more steps to complete.

    Default recursion_limit is 25 steps. Configure it via:
    - RunnableConfig: {"recursion_limit": 100}
    - Graph compilation: graph.with_config(recursion_limit=100)

    Attributes:
        Inherits from RecursionError

    Example:
        try:
            graph.invoke(input)
        except GraphRecursionError as e:
            print(f"Graph exceeded recursion limit: {e}")
            # Increase limit or check for infinite loops
    """
    ...
```

### InvalidUpdateError

Exception raised when attempting an invalid channel update.

```python { .api }
class InvalidUpdateError(Exception):
    """
    Raised when attempting invalid channel update.

    This error occurs when:
    - Updating a channel with incompatible type
    - Writing to a non-existent channel
    - Violating channel constraints
    - Concurrent updates conflict

    The error message includes details about what went wrong and
    which channel was affected.

    Example:
        try:
            graph.update_state(config, invalid_update)
        except InvalidUpdateError as e:
            print(f"Invalid update: {e}")
            # Fix the update to match channel schema
    """
    ...
```

### EmptyChannelError

Exception raised when reading from an empty channel.

```python { .api }
class EmptyChannelError(Exception):
    """
    Raised when reading from empty channel.

    This error occurs when a node tries to read from a channel that
    has no value. This can happen if:
    - Channel was never written to
    - Channel value was cleared
    - Reading before initial state is set

    Ensure channels are initialized or have default values.

    Example:
        try:
            value = channel.get()
        except EmptyChannelError:
            print("Channel has no value yet")
            # Use default or skip operation
    """
    ...
```

### EmptyInputError

Exception raised when graph receives empty input.

```python { .api }
class EmptyInputError(Exception):
    """
    Raised when graph receives empty input.

    This error occurs when:
    - invoke() or stream() called with None/empty dict when input is required
    - Resuming execution without providing required input
    - Input doesn't contain required fields

    Provide valid input that matches the graph's input schema.

    Example:
        try:
            graph.invoke(None)
        except EmptyInputError:
            print("Graph requires input")
            graph.invoke({"field": "value"})
    """
    ...
```

### TaskNotFound

Exception raised in distributed mode when executor cannot find a task.

```python { .api }
class TaskNotFound(Exception):
    """
    Raised when executor cannot find a task (distributed mode).

    This error occurs in distributed execution when:
    - Task ID doesn't exist
    - Task was already processed
    - Task expired or was cleaned up

    This is primarily an internal error for distributed execution.

    Example:
        try:
            executor.execute_task(task_id)
        except TaskNotFound:
            print("Task not found or already processed")
    """
    ...
```

### ErrorCode

Enum of standardized error codes with documentation links.

```python { .api }
class ErrorCode:
    """
    Enum of standardized error codes.

    Error codes provide categorized identifiers for common errors
    with links to documentation for troubleshooting.

    Values:
        GRAPH_RECURSION_LIMIT: Graph exceeded maximum recursion depth
        INVALID_CONCURRENT_GRAPH_UPDATE: Invalid concurrent state update
        INVALID_GRAPH_NODE_RETURN_VALUE: Node returned invalid value type
        MULTIPLE_SUBGRAPHS: Multiple subgraphs in single node
        INVALID_CHAT_HISTORY: Invalid chat history format
    """
    GRAPH_RECURSION_LIMIT: str = "GRAPH_RECURSION_LIMIT"
    INVALID_CONCURRENT_GRAPH_UPDATE: str = "INVALID_CONCURRENT_GRAPH_UPDATE"
    INVALID_GRAPH_NODE_RETURN_VALUE: str = "INVALID_GRAPH_NODE_RETURN_VALUE"
    MULTIPLE_SUBGRAPHS: str = "MULTIPLE_SUBGRAPHS"
    INVALID_CHAT_HISTORY: str = "INVALID_CHAT_HISTORY"
```

### create_error_message

Create a formatted error message with documentation link.

```python { .api }
def create_error_message(
    message: str,
    error_code: ErrorCode
) -> str:
    """
    Create formatted error message with docs link.

    Formats an error message with a standardized error code and
    link to relevant documentation for troubleshooting.

    Args:
        message: Human-readable error description
        error_code: ErrorCode enum value

    Returns:
        Formatted error message with code and documentation link

    Example:
        error_msg = create_error_message(
            "Graph exceeded 25 steps",
            ErrorCode.GRAPH_RECURSION_LIMIT
        )
        raise GraphRecursionError(error_msg)
    """
    ...
```

## Usage Examples

### Handling Recursion Errors

```python
from langgraph.graph import StateGraph, START, END
from langgraph.errors import GraphRecursionError
from typing_extensions import TypedDict

class State(TypedDict):
    count: int

def increment(state: State) -> dict:
    # Infinite loop - always continues
    return {"count": state["count"] + 1}

def router(state: State) -> str:
    # Never reaches END
    return "increment"

builder = StateGraph(State)
builder.add_node("increment", increment)
builder.add_edge(START, "increment")
builder.add_conditional_edges("increment", router, {
    "increment": "increment",
    "end": END
})

graph = builder.compile()

try:
    # Will hit recursion limit
    result = graph.invoke({"count": 0})
except GraphRecursionError as e:
    print(f"Error: {e}")
    print("Fix: Add termination condition or increase recursion_limit")

    # Increase recursion limit
    result = graph.invoke(
        {"count": 0},
        {"recursion_limit": 100}
    )
```

### Handling Invalid Updates

```python
from langgraph.graph import StateGraph, START, END
from langgraph.errors import InvalidUpdateError
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

class State(TypedDict):
    value: int
    name: str

builder = StateGraph(State)
builder.add_node("process", lambda s: {"value": s["value"] + 1})
builder.add_edge(START, "process")
builder.add_edge("process", END)

graph = builder.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "thread-1"}}
graph.invoke({"value": 0, "name": "test"}, config)

try:
    # Try to update with wrong type
    graph.update_state(config, {"value": "not a number"})
except InvalidUpdateError as e:
    print(f"Invalid update: {e}")
    # Fix: Use correct type
    graph.update_state(config, {"value": 42})
```

### Handling Empty Input

```python
from langgraph.errors import EmptyInputError

builder = StateGraph(State)
builder.add_node("process", process_fn)
builder.add_edge(START, "process")
builder.add_edge("process", END)

graph = builder.compile()

try:
    # Try to invoke without required input
    result = graph.invoke(None)
except EmptyInputError:
    print("Graph requires input")
    # Provide valid input
    result = graph.invoke({"value": 0, "name": "test"})
```

### Handling Empty Channels

```python
from langgraph.channels import LastValue
from langgraph.errors import EmptyChannelError

channel = LastValue(int)

try:
    # Try to read before writing
    value = channel.get()
except EmptyChannelError:
    print("Channel is empty, using default")
    value = 0

# Or check availability first
if channel.is_available():
    value = channel.get()
else:
    value = 0
```

### Using Error Codes

```python
from langgraph.errors import ErrorCode, create_error_message

# Check for specific error conditions
def validate_graph_state(state):
    if state.get("depth", 0) > 100:
        error_msg = create_error_message(
            "Graph depth exceeded safe limit",
            ErrorCode.GRAPH_RECURSION_LIMIT
        )
        raise ValueError(error_msg)

# Error message includes code and documentation link
```

### Retry on Specific Errors

```python
from langgraph.types import RetryPolicy
from langgraph.errors import InvalidUpdateError

def should_retry(exc: Exception) -> bool:
    # Don't retry on invalid updates
    if isinstance(exc, InvalidUpdateError):
        return False
    # Retry on network errors
    return isinstance(exc, (ConnectionError, TimeoutError))

retry_policy = RetryPolicy(
    max_attempts=3,
    retry_on=should_retry
)

graph = builder.compile(retry_policy=retry_policy)
```

### Graceful Error Handling in Nodes

```python
from langgraph.graph import StateGraph, START, END
from langgraph.errors import EmptyChannelError, InvalidUpdateError

def safe_node(state: State) -> dict:
    try:
        # Attempt operation
        result = risky_operation(state)
        return {"result": result}
    except EmptyChannelError:
        # Handle empty channel gracefully
        return {"result": "default"}
    except InvalidUpdateError as e:
        # Log and skip update
        print(f"Skipping invalid update: {e}")
        return {}

builder = StateGraph(State)
builder.add_node("safe", safe_node)
builder.add_edge(START, "safe")
builder.add_edge("safe", END)

graph = builder.compile()
```

### Logging Errors with Codes

```python
import logging
from langgraph.errors import GraphRecursionError, ErrorCode

logger = logging.getLogger(__name__)

try:
    result = graph.invoke(input, config)
except GraphRecursionError as e:
    logger.error(
        f"Error Code: {ErrorCode.GRAPH_RECURSION_LIMIT}",
        extra={
            "error_code": ErrorCode.GRAPH_RECURSION_LIMIT,
            "error_message": str(e),
            "config": config
        }
    )
    raise
```

### Custom Error Messages

```python
from langgraph.errors import create_error_message, ErrorCode

def validate_node_return(value):
    if not isinstance(value, dict):
        error_msg = create_error_message(
            f"Node returned {type(value).__name__} instead of dict",
            ErrorCode.INVALID_GRAPH_NODE_RETURN_VALUE
        )
        raise ValueError(error_msg)

    return value
```

### Handling Concurrent Update Errors

```python
from langgraph.errors import InvalidUpdateError, ErrorCode
from langgraph.checkpoint.memory import MemorySaver

graph = builder.compile(checkpointer=MemorySaver())

config = {"configurable": {"thread_id": "thread-1"}}

try:
    # Two processes trying to update same thread
    graph.update_state(config, update1)
    graph.update_state(config, update2)  # Might fail if concurrent
except InvalidUpdateError as e:
    if ErrorCode.INVALID_CONCURRENT_GRAPH_UPDATE in str(e):
        print("Concurrent update detected, retrying...")
        # Retry with fresh config
        fresh_config = graph.get_state(config).config
        graph.update_state(fresh_config, update2)
```

### TaskNotFound in Distributed Mode

```python
from langgraph.errors import TaskNotFound

def execute_distributed_task(executor, task_id):
    try:
        result = executor.execute_task(task_id)
        return result
    except TaskNotFound:
        print(f"Task {task_id} not found or expired")
        # Task might have been processed already
        return None
```

### Error Recovery Pattern

```python
from langgraph.errors import (
    GraphRecursionError,
    InvalidUpdateError,
    EmptyInputError
)

def execute_with_recovery(graph, input_data, config):
    try:
        return graph.invoke(input_data, config)
    except GraphRecursionError:
        # Increase limit and retry
        config["recursion_limit"] = config.get("recursion_limit", 25) * 2
        return graph.invoke(input_data, config)
    except EmptyInputError:
        # Provide default input
        default_input = {"field": "default"}
        return graph.invoke(default_input, config)
    except InvalidUpdateError as e:
        # Log and re-raise
        print(f"Unrecoverable error: {e}")
        raise
```

### Validation with Error Codes

```python
from langgraph.errors import ErrorCode, create_error_message

def validate_state_schema(state, schema):
    for field, field_type in schema.items():
        if field not in state:
            error_msg = create_error_message(
                f"Missing required field: {field}",
                ErrorCode.INVALID_GRAPH_NODE_RETURN_VALUE
            )
            raise ValueError(error_msg)

        if not isinstance(state[field], field_type):
            error_msg = create_error_message(
                f"Field {field} has wrong type: {type(state[field]).__name__}",
                ErrorCode.INVALID_GRAPH_NODE_RETURN_VALUE
            )
            raise ValueError(error_msg)
```

## Types

### Internal Exceptions

```python { .api }
class GraphInterrupt(GraphBubbleUp):
    """
    Internal exception raised when subgraph is interrupted.

    This is an internal control flow exception used by LangGraph
    to handle interrupts in subgraphs. Not typically caught by user code.
    """
    ...

class GraphBubbleUp(Exception):
    """
    Internal exception for control flow.

    Base class for internal exceptions used to control graph execution
    flow. Not intended to be caught or raised by user code.
    """
    ...

class ParentCommand(GraphBubbleUp):
    """
    Internal exception for parent graph commands.

    Used internally when a subgraph sends a Command targeting its
    parent graph. Not intended to be caught or raised by user code.
    """
    ...

class NodeInterrupt(GraphInterrupt):
    """
    Deprecated - use interrupt() function instead.

    This exception was previously used to interrupt execution from
    within a node. Use the interrupt() function instead:

    # Old way (deprecated)
    raise NodeInterrupt(value)

    # New way
    from langgraph.types import interrupt
    result = interrupt(value)
    """
    ...
```

### Error Message Format

Error messages created with `create_error_message()` follow this format:

```
<error_description>

Error Code: <ERROR_CODE>
Documentation: https://python.langchain.com/docs/langgraph/errors/<error_code>
```

Example:
```
Graph exceeded maximum recursion depth of 25 steps

Error Code: GRAPH_RECURSION_LIMIT
Documentation: https://python.langchain.com/docs/langgraph/errors/graph_recursion_limit
```

### Common Error Scenarios

| Error | Common Causes | Solutions |
|-------|--------------|-----------|
| `GraphRecursionError` | Infinite loop, missing termination condition | Add END condition, increase recursion_limit |
| `InvalidUpdateError` | Wrong type, non-existent channel, concurrent updates | Match schema, check channel names, use fresh config |
| `EmptyChannelError` | Reading before writing, uninitialized channel | Initialize channels, check is_available() |
| `EmptyInputError` | Missing required input, None passed to invoke | Provide valid input matching input_schema |
| `TaskNotFound` | Task expired, already processed (distributed mode) | Check task exists, handle idempotently |
