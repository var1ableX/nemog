# Functional API

Define workflows using Python function decorators instead of graph builders. Create parallelizable tasks and entrypoints with automatic graph generation from decorated functions.

## Capabilities

### Task Decorator

Define parallelizable tasks that can be called from entrypoints or StateGraph nodes.

```python { .api }
def task(
    name: str | None = None,
    retry_policy: RetryPolicy | Sequence[RetryPolicy] | None = None,
    cache_policy: CachePolicy | None = None,
) -> Callable:
    """
    Decorator to define parallelizable LangGraph tasks.

    Tasks decorated with @task return futures when called, allowing for
    parallel execution. They can be called from @entrypoint functions or
    from StateGraph nodes.

    Args:
        name: Optional task name (defaults to function name)
        retry_policy: Retry configuration for handling failures
        cache_policy: Caching configuration for optimization

    Returns:
        Decorated function that returns SyncAsyncFuture when called

    Example:
        @task
        def process_item(item: str) -> str:
            return f"Processed: {item}"

        @entrypoint()
        def workflow(items: list[str]) -> list[str]:
            # Parallel execution
            futures = [process_item(item) for item in items]
            return [f.result() for f in futures]
    """
    ...
```

### Entrypoint Decorator

Convert a function into an executable Pregel graph.

```python { .api }
def entrypoint(
    checkpointer: BaseCheckpointSaver | None = None,
    store: BaseStore | None = None,
    cache: BaseCache | None = None,
    context_schema: type[ContextT] | None = None,
    cache_policy: CachePolicy | None = None,
    retry_policy: RetryPolicy | Sequence[RetryPolicy] | None = None,
) -> Callable:
    """
    Decorator to convert a function into a Pregel graph.

    The decorated function becomes an executable graph with invoke/stream
    methods. Supports both synchronous and asynchronous functions.

    Args:
        checkpointer: Checkpoint saver for state persistence
        store: Key-value store for long-term data
        cache: Cache for task results
        context_schema: Type for run-scoped context data
        cache_policy: Default caching policy for all tasks
        retry_policy: Default retry policy for all tasks

    Returns:
        Pregel graph that can be invoked or streamed

    Example:
        @entrypoint(checkpointer=MemorySaver())
        def workflow(input: str) -> str:
            result = process(input)
            return result

        # Execute like a compiled graph
        output = workflow.invoke("test")
    """
    ...
```

### Entrypoint Final

Decouple return value from saved state in entrypoints.

```python { .api }
class entrypoint.final:
    """
    Dataclass for decoupling return value from checkpoint state.

    Use this to return a different value to the caller than what
    is saved to the checkpoint.

    Fields:
        value: Value to return to caller
        save: Value to save to checkpoint

    Example:
        @entrypoint(checkpointer=MemorySaver())
        def workflow(input: str) -> entrypoint.final:
            processed = process(input)
            # Return summary to caller, save full data to checkpoint
            return entrypoint.final(
                value={"summary": processed[:100]},
                save={"full": processed}
            )
    """
    value: Any  # Value to return
    save: Any   # Value to save
```

### Task Function Methods

Methods available on decorated task functions.

```python { .api }
class _TaskFunction:
    """
    Decorated task function with additional methods.

    Returned by @task decorator.
    """

    def __call__(self, *args, **kwargs) -> SyncAsyncFuture:
        """
        Call the task and return a future.

        Returns:
            Future that can be awaited or .result() called
        """
        ...

    def clear_cache(self, cache: BaseCache) -> None:
        """
        Clear cache for this task synchronously.

        Args:
            cache: Cache instance to clear
        """
        ...

    async def aclear_cache(self, cache: BaseCache) -> None:
        """
        Clear cache for this task asynchronously.

        Args:
            cache: Cache instance to clear
        """
        ...
```

## Usage Examples

### Basic Task and Entrypoint

```python
from langgraph.func import task, entrypoint

@task
def add_one(x: int) -> int:
    return x + 1

@task
def multiply_two(x: int) -> int:
    return x * 2

@entrypoint()
def workflow(x: int) -> int:
    # Call tasks sequentially
    result1 = add_one(x)
    result2 = multiply_two(result1.result())
    return result2.result()

# Execute
output = workflow.invoke(5)
print(output)  # (5 + 1) * 2 = 12
```

### Parallel Task Execution

```python
from langgraph.func import task, entrypoint

@task
def process_item(item: str) -> str:
    # Simulate processing
    return f"Processed: {item}"

@entrypoint()
def parallel_workflow(items: list[str]) -> list[str]:
    # Launch all tasks in parallel
    futures = [process_item(item) for item in items]

    # Wait for all results
    results = [f.result() for f in futures]

    return results

# Execute
items = ["item1", "item2", "item3"]
results = parallel_workflow.invoke(items)
print(results)
# ['Processed: item1', 'Processed: item2', 'Processed: item3']
```

### Async Entrypoint

```python
import asyncio
from langgraph.func import task, entrypoint

@task
async def fetch_data(url: str) -> dict:
    # Async task
    await asyncio.sleep(0.1)
    return {"url": url, "data": "content"}

@entrypoint()
async def async_workflow(urls: list[str]) -> list[dict]:
    # Parallel async tasks
    futures = [fetch_data(url) for url in urls]

    # Await all results
    results = [await f for f in futures]

    return results

# Execute
urls = ["url1", "url2", "url3"]
results = asyncio.run(async_workflow.ainvoke(urls))
print(results)
```

### With Retry Policy

```python
from langgraph.func import task, entrypoint
from langgraph.types import RetryPolicy

# Task with retry configuration
@task(retry_policy=RetryPolicy(
    initial_interval=1.0,
    max_attempts=3,
    backoff_factor=2.0
))
def unreliable_task(x: int) -> int:
    # May fail occasionally
    if x < 0:
        raise ValueError("Negative value")
    return x * 2

@entrypoint()
def workflow_with_retry(x: int) -> int:
    future = unreliable_task(x)
    return future.result()

# If unreliable_task fails, it will retry up to 3 times
result = workflow_with_retry.invoke(5)
print(result)  # 10
```

### With Caching

```python
from langgraph.func import task, entrypoint
from langgraph.types import CachePolicy

# Task with caching
@task(cache_policy=CachePolicy(
    ttl=3600  # Cache for 1 hour
))
def expensive_computation(x: int) -> int:
    # Expensive operation
    return x ** 2

@entrypoint(cache=InMemoryCache())
def workflow_with_cache(values: list[int]) -> list[int]:
    futures = [expensive_computation(v) for v in values]
    return [f.result() for f in futures]

# First call computes, second call uses cache
result1 = workflow_with_cache.invoke([1, 2, 3])
result2 = workflow_with_cache.invoke([1, 2, 3])  # Cached
```

### With Checkpointing

```python
from langgraph.func import task, entrypoint
from langgraph.checkpoint.memory import MemorySaver

@task
def step_one(x: int) -> int:
    return x + 1

@task
def step_two(x: int) -> int:
    return x * 2

@entrypoint(checkpointer=MemorySaver())
def workflow(x: int) -> int:
    result1 = step_one(x).result()
    result2 = step_two(result1).result()
    return result2

# Execute with thread_id for checkpointing
config = {"configurable": {"thread_id": "workflow-1"}}
result = workflow.invoke(5, config)
print(result)  # (5 + 1) * 2 = 12

# State is checkpointed at each step
```

### Streaming Results

```python
from langgraph.func import task, entrypoint

@task
def process_batch(batch: list[int]) -> list[int]:
    return [x * 2 for x in batch]

@entrypoint()
def streaming_workflow(data: list[int]) -> list[int]:
    # Process in batches
    batches = [data[i:i+2] for i in range(0, len(data), 2)]
    futures = [process_batch(batch) for batch in batches]

    # Collect results
    results = []
    for f in futures:
        results.extend(f.result())

    return results

# Stream execution
for chunk in streaming_workflow.stream([1, 2, 3, 4, 5, 6]):
    print(f"Chunk: {chunk}")
```

### With Context

```python
from langgraph.func import task, entrypoint
from langgraph.runtime import get_runtime
from typing_extensions import TypedDict

class Context(TypedDict):
    user_id: str
    api_key: str

@task
def api_call(data: str) -> str:
    # Access runtime context
    runtime = get_runtime(Context)
    user_id = runtime.context["user_id"]
    api_key = runtime.context["api_key"]

    # Use context in task
    return f"Called API for {user_id} with {data}"

@entrypoint(context_schema=Context)
def workflow(data: str) -> str:
    result = api_call(data)
    return result.result()

# Execute with context
result = workflow.invoke(
    "test data",
    {"configurable": {"context": {
        "user_id": "user123",
        "api_key": "secret"
    }}}
)
print(result)
```

### Entrypoint Final for Different Return and Save

```python
from langgraph.func import task, entrypoint
from langgraph.checkpoint.memory import MemorySaver

@task
def generate_report(data: str) -> dict:
    # Generate full report
    return {
        "summary": f"Summary of {data}",
        "details": f"Full details about {data}" * 100,
        "metadata": {"length": len(data)}
    }

@entrypoint(checkpointer=MemorySaver())
def workflow(data: str) -> entrypoint.final:
    report = generate_report(data).result()

    # Return just summary to caller
    # Save full report to checkpoint
    return entrypoint.final(
        value=report["summary"],
        save=report
    )

config = {"configurable": {"thread_id": "report-1"}}

# Get summary
result = workflow.invoke("input data", config)
print(result)  # "Summary of input data"

# Full report is in checkpoint
from langgraph.pregel import Pregel
state = Pregel.get_state(config)  # Contains full report
```

### Mixed Task and StateGraph Usage

```python
from langgraph.func import task
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

@task
def parallel_task(item: str) -> str:
    return f"Processed: {item}"

class State(TypedDict):
    items: list[str]
    results: list[str]

def fan_out_node(state: State) -> dict:
    # Call tasks from StateGraph node
    futures = [parallel_task(item) for item in state["items"]]
    results = [f.result() for f in futures]
    return {"results": results}

builder = StateGraph(State)
builder.add_node("process", fan_out_node)
builder.add_edge(START, "process")
builder.add_edge("process", END)

graph = builder.compile()
result = graph.invoke({"items": ["a", "b", "c"], "results": []})
print(result["results"])
```

## Types

### SyncAsyncFuture

```python { .api }
class SyncAsyncFuture:
    """
    Future returned by @task decorated functions.

    Can be used in both sync and async contexts.
    """

    def result(self) -> T:
        """
        Get result synchronously.

        Returns:
            Task result

        Raises:
            Exception: If task failed
        """
        ...

    async def __await__(self) -> T:
        """
        Await result asynchronously.

        Returns:
            Task result

        Raises:
            Exception: If task failed
        """
        ...
```
