# Retry and Caching

Configure automatic retry behavior for failed nodes and caching policies to optimize performance and reduce redundant computation.

## Capabilities

### RetryPolicy

Configure exponential backoff retry behavior for node failures.

```python { .api }
class RetryPolicy(NamedTuple):
    """
    Configuration for retrying failed nodes.

    Implements exponential backoff with optional jitter to retry node
    execution on failure. Retry policies can be attached to individual
    nodes or applied globally during graph compilation.

    Fields:
        initial_interval: Seconds to wait before first retry (default: 0.5)
        backoff_factor: Multiplier applied to interval after each retry (default: 2.0)
        max_interval: Maximum seconds between retries (default: 128.0)
        max_attempts: Total attempts including first execution (default: 3)
        jitter: Add random jitter to retry intervals to avoid thundering herd (default: True)
        retry_on: Exception types or predicate function to determine if error should be retried
                  (default: default_retry_on - retries most common transient errors)

    Example:
        RetryPolicy(
            initial_interval=1.0,
            backoff_factor=2.0,
            max_interval=60.0,
            max_attempts=5,
            jitter=True,
            retry_on=ConnectionError
        )
    """
    initial_interval: float = 0.5
    backoff_factor: float = 2.0
    max_interval: float = 128.0
    max_attempts: int = 3
    jitter: bool = True
    retry_on: type[Exception] | Sequence[type[Exception]] | Callable[[Exception], bool] = default_retry_on
```

### CachePolicy

Configure caching behavior for node results.

```python { .api }
class CachePolicy:
    """
    Configuration for caching node results.

    Enables caching of node execution results to avoid redundant computation.
    Results are cached based on a key derived from node inputs. Cache policies
    can be attached to individual nodes or the entire graph.

    Fields:
        key_func: Function to generate cache key from node inputs (default: default_cache_key)
                  Receives the same arguments as the node and returns a string or bytes key
        ttl: Time to live in seconds (None = no expiry, default: None)
             After TTL expires, cached results are evicted

    Example:
        CachePolicy(
            key_func=lambda state: f"query:{state['query']}",
            ttl=3600  # Cache for 1 hour
        )
    """
    key_func: Callable[..., str | bytes] = default_cache_key
    ttl: int | None = None
```

## Usage Examples

### Basic Retry Policy

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
from typing_extensions import TypedDict

class State(TypedDict):
    value: int
    attempts: int

def unreliable_node(state: State) -> dict:
    """Simulates a node that might fail"""
    import random
    state["attempts"] = state.get("attempts", 0) + 1

    if random.random() < 0.5:
        raise ConnectionError("Random failure")

    return {"value": state["value"] + 1}

builder = StateGraph(State)

# Configure retry policy at compile time
builder.add_node("unreliable", unreliable_node)
builder.add_edge(START, "unreliable")
builder.add_edge("unreliable", END)

# Add retry policy during compilation
retry_policy = RetryPolicy(
    initial_interval=0.1,
    max_attempts=5,
    retry_on=ConnectionError
)

graph = builder.compile(retry_policy=retry_policy)

result = graph.invoke({"value": 0, "attempts": 0})
print(f"Success after {result['attempts']} attempts")
```

### Retry Specific Exceptions

```python
from langgraph.types import RetryPolicy

# Retry only specific exceptions
retry_policy = RetryPolicy(
    max_attempts=3,
    retry_on=(ConnectionError, TimeoutError, IOError)
)

# Or use a predicate function
def should_retry(exc: Exception) -> bool:
    if isinstance(exc, ValueError):
        return "retry" in str(exc).lower()
    return isinstance(exc, (ConnectionError, TimeoutError))

retry_policy = RetryPolicy(
    max_attempts=4,
    retry_on=should_retry
)
```

### Custom Backoff Configuration

```python
from langgraph.types import RetryPolicy

# Aggressive retry with faster backoff
aggressive_retry = RetryPolicy(
    initial_interval=0.1,
    backoff_factor=1.5,
    max_interval=10.0,
    max_attempts=10,
    jitter=True
)

# Conservative retry with slower backoff
conservative_retry = RetryPolicy(
    initial_interval=2.0,
    backoff_factor=3.0,
    max_interval=300.0,
    max_attempts=3,
    jitter=False
)
```

### Node-Level Retry Policy

```python
from langgraph.graph import StateGraph, START, END
from langgraph.pregel import NodeBuilder
from langgraph.types import RetryPolicy

builder = StateGraph(State)

# Use NodeBuilder for fine-grained control
node = NodeBuilder() \
    .do(unreliable_node) \
    .add_retry_policies(
        RetryPolicy(
            initial_interval=0.5,
            max_attempts=5,
            retry_on=ConnectionError
        )
    ) \
    .build()

# Node-level retry policy takes precedence over graph-level
```

### Basic Caching

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import CachePolicy
from typing_extensions import TypedDict

class State(TypedDict):
    query: str
    result: str

def expensive_computation(state: State) -> dict:
    """Simulates expensive computation"""
    import time
    time.sleep(2)  # Expensive operation

    result = f"Result for: {state['query']}"
    return {"result": result}

builder = StateGraph(State)
builder.add_node("compute", expensive_computation)
builder.add_edge(START, "compute")
builder.add_edge("compute", END)

# Enable caching with default key function
cache_policy = CachePolicy(ttl=300)  # Cache for 5 minutes

graph = builder.compile(cache_policy=cache_policy)

# First call - takes 2 seconds
result1 = graph.invoke({"query": "test", "result": ""})

# Second call with same input - instant (cached)
result2 = graph.invoke({"query": "test", "result": ""})
```

### Custom Cache Key Function

```python
from langgraph.types import CachePolicy

# Cache based on specific state fields
def custom_key(state: State) -> str:
    # Only cache based on query, ignore other fields
    return f"query:{state['query']}"

cache_policy = CachePolicy(
    key_func=custom_key,
    ttl=3600  # 1 hour
)

# More complex key generation
def complex_key(state: State) -> str:
    import hashlib
    # Include multiple fields in cache key
    key_data = f"{state['query']}:{state.get('context', '')}"
    return hashlib.md5(key_data.encode()).hexdigest()

cache_policy = CachePolicy(key_func=complex_key)
```

### Cache with No Expiry

```python
from langgraph.types import CachePolicy

# Cache indefinitely (until manually cleared)
permanent_cache = CachePolicy(
    key_func=lambda state: state['id'],
    ttl=None
)

graph = builder.compile(cache_policy=permanent_cache)

# Manually clear cache when needed
graph.clear_cache()  # Clear all node caches
graph.clear_cache(nodes=["compute"])  # Clear specific node
```

### Functional API with Retry and Cache

```python
from langgraph.func import task, entrypoint
from langgraph.types import RetryPolicy, CachePolicy

# Configure retry on task level
@task(
    retry_policy=RetryPolicy(
        max_attempts=5,
        retry_on=ConnectionError
    ),
    cache_policy=CachePolicy(ttl=600)
)
def fetch_data(url: str) -> dict:
    import requests
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

@entrypoint(
    retry_policy=RetryPolicy(max_attempts=3),
    cache_policy=CachePolicy(ttl=300)
)
def workflow(query: str) -> dict:
    data_future = fetch_data(f"https://api.example.com/search?q={query}")
    data = data_future.result()
    return data

# Both task and entrypoint have retry and caching
```

### Combining Retry and Cache

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy, CachePolicy

builder = StateGraph(State)
builder.add_node("fetch", fetch_data_node)
builder.add_edge(START, "fetch")
builder.add_edge("fetch", END)

# Retry on failure, cache on success
graph = builder.compile(
    retry_policy=RetryPolicy(
        max_attempts=3,
        retry_on=(ConnectionError, TimeoutError)
    ),
    cache_policy=CachePolicy(ttl=600)
)

# If fetch fails, retry up to 3 times
# If successful, cache result for 10 minutes
```

### Per-Node Retry Policies

```python
from langgraph.graph import StateGraph, START, END
from langgraph.pregel import NodeBuilder
from langgraph.types import RetryPolicy

builder = StateGraph(State)

# Critical node with aggressive retry
critical_node = NodeBuilder() \
    .do(critical_operation) \
    .add_retry_policies(
        RetryPolicy(max_attempts=10, initial_interval=0.1)
    ) \
    .build()

# Non-critical node with conservative retry
optional_node = NodeBuilder() \
    .do(optional_operation) \
    .add_retry_policies(
        RetryPolicy(max_attempts=2, initial_interval=1.0)
    ) \
    .build()

builder.add_node("critical", critical_node)
builder.add_node("optional", optional_node)
```

### Multiple Retry Policies

```python
from langgraph.pregel import NodeBuilder
from langgraph.types import RetryPolicy

# Apply multiple retry policies (tried in order)
node = NodeBuilder() \
    .do(operation) \
    .add_retry_policies(
        RetryPolicy(max_attempts=3, retry_on=ConnectionError),
        RetryPolicy(max_attempts=2, retry_on=TimeoutError)
    ) \
    .build()

# First policy for ConnectionError, second for TimeoutError
```

### Async with Retry and Cache

```python
import asyncio
from langgraph.types import RetryPolicy, CachePolicy

async def async_operation(state: State) -> dict:
    # Async operations benefit from retry/cache too
    await asyncio.sleep(1)
    return {"result": "done"}

builder = StateGraph(State)
builder.add_node("async_op", async_operation)
builder.add_edge(START, "async_op")
builder.add_edge("async_op", END)

graph = builder.compile(
    retry_policy=RetryPolicy(max_attempts=3),
    cache_policy=CachePolicy(ttl=300)
)

result = await graph.ainvoke({"result": ""})
```

### Cache Clearing

```python
from langgraph.func import task

@task(cache_policy=CachePolicy(ttl=3600))
def cached_task(x: int) -> int:
    return x * 2

# Clear cache programmatically
from langgraph.cache import BaseCache

cache = get_cache()  # Get your cache instance

# Clear specific task cache
cached_task.clear_cache(cache)

# Async cache clearing
await cached_task.aclear_cache(cache)
```

## Types

### default_retry_on

```python { .api }
def default_retry_on(exc: Exception) -> bool:
    """
    Default retry predicate function.

    Returns True for common transient errors that are safe to retry:
    - ConnectionError
    - TimeoutError
    - Temporary network failures
    - Rate limiting errors

    Args:
        exc: The exception that occurred

    Returns:
        True if the exception should trigger a retry, False otherwise
    """
    ...
```

### default_cache_key

```python { .api }
def default_cache_key(*args, **kwargs) -> str:
    """
    Default cache key generation function.

    Generates a cache key by serializing the function arguments.
    Uses stable JSON serialization to ensure consistent keys.

    Args:
        *args: Positional arguments to the cached function
        **kwargs: Keyword arguments to the cached function

    Returns:
        String cache key derived from arguments
    """
    ...
```

### Retry Intervals

The actual retry intervals follow the formula:

```
interval = min(
    initial_interval * (backoff_factor ^ attempt),
    max_interval
)

if jitter:
    interval = interval * random.uniform(0.5, 1.5)
```

Example with `RetryPolicy(initial_interval=1.0, backoff_factor=2.0, max_interval=60.0)`:
- Attempt 1: No delay (initial execution)
- Attempt 2: 1.0 seconds
- Attempt 3: 2.0 seconds
- Attempt 4: 4.0 seconds
- Attempt 5: 8.0 seconds
- Attempt 6: 16.0 seconds
- Attempt 7: 32.0 seconds
- Attempt 8+: 60.0 seconds (capped at max_interval)
