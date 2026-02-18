# Pregel API

Low-level graph execution API providing direct control over the Pregel engine. Use the Pregel class and NodeBuilder for advanced use cases requiring fine-grained control over nodes, channels, triggers, and execution.

## Capabilities

### Pregel

The low-level graph execution engine, typically created via StateGraph.compile().

```python { .api }
class Pregel(Generic[StateT, ContextT, InputT, OutputT]):
    """
    Low-level graph execution engine.

    Pregel implements the graph execution model inspired by Google's Pregel
    system. It manages nodes, channels, execution flow, and state persistence.
    Most users should use StateGraph.compile() rather than constructing Pregel
    directly.

    Type Parameters:
        StateT: State type
        ContextT: Context type
        InputT: Input type
        OutputT: Output type
    """

    def __init__(
        self,
        nodes: dict,
        channels: dict,
        input_channels: str | list,
        output_channels: str | list,
        stream_channels: str | list | None = None,
        interrupt_before: Sequence[str] | All = None,
        interrupt_after: Sequence[str] | All = None,
        stream_mode: StreamMode | Sequence[StreamMode] = "updates",
        step_timeout: float | None = None,
        debug: bool = False
    ):
        """
        Initialize Pregel execution engine.

        Args:
            nodes: Dict of node name to PregelNode
            channels: Dict of channel name to BaseChannel
            input_channels: Channel(s) to read input from
            output_channels: Channel(s) to write output to
            stream_channels: Channel(s) to stream during execution
            interrupt_before: Nodes to interrupt before executing
            interrupt_after: Nodes to interrupt after executing
            stream_mode: How to emit stream output
            step_timeout: Timeout for each step in seconds
            debug: Enable debug mode
        """
        ...

    def invoke(
        self,
        input: InputT,
        config: RunnableConfig | None = None,
        stream_mode: StreamMode | Sequence[StreamMode] | None = None,
        output_keys: Sequence[str] | None = None,
        interrupt_before: Sequence[str] | All | None = None,
        interrupt_after: Sequence[str] | All | None = None,
        debug: bool | None = None
    ) -> OutputT:
        """
        Execute graph synchronously with single input.

        Args:
            input: Input value matching input schema
            config: Optional execution configuration
            stream_mode: Override default stream mode
            output_keys: Specific output keys to return
            interrupt_before: Override interrupt_before nodes
            interrupt_after: Override interrupt_after nodes
            debug: Override debug setting

        Returns:
            Output value from final state
        """
        ...

    async def ainvoke(
        self,
        input: InputT,
        config: RunnableConfig | None = None,
        stream_mode: StreamMode | Sequence[StreamMode] | None = None,
        output_keys: Sequence[str] | None = None,
        interrupt_before: Sequence[str] | All | None = None,
        interrupt_after: Sequence[str] | All | None = None,
        debug: bool | None = None
    ) -> OutputT:
        """
        Execute graph asynchronously.

        Args: Same as invoke()

        Returns:
            Output value from final state
        """
        ...

    def stream(
        self,
        input: InputT,
        config: RunnableConfig | None = None,
        stream_mode: StreamMode | Sequence[StreamMode] = "updates",
        output_keys: Sequence[str] | None = None,
        interrupt_before: Sequence[str] | All | None = None,
        interrupt_after: Sequence[str] | All | None = None,
        debug: bool | None = None
    ) -> Iterator:
        """
        Stream output during execution.

        Args:
            input: Input value matching input schema
            config: Optional execution configuration
            stream_mode: How to emit stream output ("values", "updates", etc.)
            output_keys: Specific output keys to stream
            interrupt_before: Override interrupt_before nodes
            interrupt_after: Override interrupt_after nodes
            debug: Override debug setting

        Yields:
            Stream chunks based on stream_mode
        """
        ...

    async def astream(
        self,
        input: InputT,
        config: RunnableConfig | None = None,
        stream_mode: StreamMode | Sequence[StreamMode] = "updates",
        output_keys: Sequence[str] | None = None,
        interrupt_before: Sequence[str] | All | None = None,
        interrupt_after: Sequence[str] | All | None = None,
        debug: bool | None = None
    ) -> AsyncIterator:
        """
        Stream output asynchronously.

        Args: Same as stream()

        Yields:
            Stream chunks based on stream_mode
        """
        ...

    def get_graph(
        self,
        config: RunnableConfig | None = None,
        xray: int | bool = False
    ) -> Graph:
        """
        Get drawable graph representation.

        Args:
            config: Optional configuration for conditional graph
            xray: Include internal subgraph details (int for depth level)

        Returns:
            Graph object that can be drawn or exported
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
            Graph object that can be drawn or exported
        """
        ...

    def get_state(
        self,
        config: RunnableConfig,
        subgraphs: bool = False
    ) -> StateSnapshot:
        """
        Get current state snapshot.

        Args:
            config: Configuration with thread_id
            subgraphs: Include subgraph states

        Returns:
            StateSnapshot with current values and metadata
        """
        ...

    async def aget_state(
        self,
        config: RunnableConfig,
        subgraphs: bool = False
    ) -> StateSnapshot:
        """
        Get state snapshot asynchronously.

        Args: Same as get_state()

        Returns:
            StateSnapshot with current values and metadata
        """
        ...

    def get_state_history(
        self,
        config: RunnableConfig,
        filter: dict | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None
    ) -> Iterator[StateSnapshot]:
        """
        Get historical state snapshots.

        Args:
            config: Configuration with thread_id
            filter: Filter criteria for snapshots
            before: Only return snapshots before this config
            limit: Maximum number of snapshots

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
        Get state history asynchronously.

        Args: Same as get_state_history()

        Yields:
            StateSnapshot objects from newest to oldest
        """
        ...

    def update_state(
        self,
        config: RunnableConfig,
        values: dict | Any | None = None,
        as_node: str | None = None
    ) -> RunnableConfig:
        """
        Update graph state programmatically.

        Args:
            config: Configuration with thread_id
            values: State updates to apply
            as_node: Apply update as if from this node

        Returns:
            Updated RunnableConfig with new checkpoint_id
        """
        ...

    async def aupdate_state(
        self,
        config: RunnableConfig,
        values: dict | Any | None = None,
        as_node: str | None = None
    ) -> RunnableConfig:
        """
        Update state asynchronously.

        Args: Same as update_state()

        Returns:
            Updated RunnableConfig with new checkpoint_id
        """
        ...

    def bulk_update_state(
        self,
        config: RunnableConfig,
        updates: Sequence[Sequence[StateUpdate]]
    ) -> RunnableConfig:
        """
        Apply multiple state updates atomically.

        Args:
            config: Configuration with thread_id
            updates: Sequence of update sequences

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
        Apply multiple updates asynchronously.

        Args: Same as bulk_update_state()

        Returns:
            Updated RunnableConfig with new checkpoint_id
        """
        ...

    def clear_cache(
        self,
        nodes: Sequence[str] | None = None
    ) -> None:
        """
        Clear node cache.

        Args:
            nodes: Specific nodes to clear (None = all nodes)
        """
        ...

    def with_config(
        self,
        config: RunnableConfig | None = None,
        **kwargs
    ) -> Self:
        """
        Create copy with updated config.

        Args:
            config: Config to merge
            **kwargs: Additional config fields

        Returns:
            New Pregel instance with updated config
        """
        ...

    def copy(
        self,
        update: dict | None = None
    ) -> Self:
        """
        Create shallow copy with optional updates.

        Args:
            update: Dict of fields to update

        Returns:
            Copied Pregel instance
        """
        ...

    def validate(self) -> Self:
        """
        Validate graph configuration.

        Returns:
            Self for method chaining

        Raises:
            ValueError: If graph is invalid
        """
        ...
```

### NodeBuilder

Builder class for configuring Pregel nodes with fine-grained control.

```python { .api }
class NodeBuilder:
    """
    Builder for configuring a Pregel node.

    NodeBuilder provides a fluent API for constructing nodes with
    specific channel subscriptions, triggers, actions, and policies.
    """

    def __init__(self):
        """Initialize empty node builder."""
        ...

    def subscribe_only(
        self,
        channel: str
    ) -> Self:
        """
        Subscribe to single channel only (triggers on that channel).

        Args:
            channel: Channel name to subscribe to exclusively

        Returns:
            Self for method chaining

        Note:
            Node will only execute when this specific channel is updated.
        """
        ...

    def subscribe_to(
        self,
        *channels: str
    ) -> Self:
        """
        Subscribe to multiple channels (triggers on any).

        Args:
            *channels: Channel names to subscribe to

        Returns:
            Self for method chaining

        Note:
            Node executes when any of these channels are updated.
        """
        ...

    def read_from(
        self,
        *channels: str
    ) -> Self:
        """
        Read from channels (node receives these channel values).

        Args:
            *channels: Channel names to read from

        Returns:
            Self for method chaining

        Note:
            Node input will contain values from these channels.
        """
        ...

    def do(
        self,
        action: RunnableLike
    ) -> Self:
        """
        Set node action/processor function.

        Args:
            action: Function or Runnable to execute for this node

        Returns:
            Self for method chaining

        Note:
            This is the core logic that executes when node is triggered.
        """
        ...

    def write_to(
        self,
        *channels: str,
        mapper: Callable | None = None
    ) -> Self:
        """
        Write to channels (node output goes to these channels).

        Args:
            *channels: Channel names to write to
            mapper: Optional function to map node output to channel writes

        Returns:
            Self for method chaining

        Note:
            If mapper is provided, it transforms node output before writing.
        """
        ...

    def meta(
        self,
        *tags: str,
        **metadata: Any
    ) -> Self:
        """
        Add metadata and tags to node.

        Args:
            *tags: Tags to add (e.g., TAG_NOSTREAM, TAG_HIDDEN)
            **metadata: Key-value metadata pairs

        Returns:
            Self for method chaining

        Example:
            builder.meta(TAG_NOSTREAM, priority="high", timeout=30)
        """
        ...

    def add_retry_policies(
        self,
        *policies: RetryPolicy
    ) -> Self:
        """
        Add retry policies to node.

        Args:
            *policies: RetryPolicy instances to apply

        Returns:
            Self for method chaining

        Note:
            Multiple policies can be added. They are tried in order.
        """
        ...

    def add_cache_policy(
        self,
        policy: CachePolicy
    ) -> Self:
        """
        Add cache policy to node.

        Args:
            policy: CachePolicy instance

        Returns:
            Self for method chaining

        Note:
            Only one cache policy per node.
        """
        ...

    def build(self) -> PregelNode:
        """
        Build the configured node.

        Returns:
            PregelNode ready for use in Pregel graph

        Raises:
            ValueError: If node configuration is incomplete
        """
        ...
```

## Usage Examples

### Direct Pregel Construction

```python
from langgraph.pregel import Pregel, NodeBuilder
from langgraph.channels import LastValue
from langgraph.constants import START, END

# Define channels
channels = {
    "input": LastValue(dict),
    "output": LastValue(dict)
}

# Build nodes
process_node = NodeBuilder() \
    .read_from("input") \
    .do(lambda x: {"result": x["value"] + 1}) \
    .write_to("output") \
    .build()

nodes = {
    "process": process_node
}

# Create Pregel instance
pregel = Pregel(
    nodes=nodes,
    channels=channels,
    input_channels="input",
    output_channels="output",
    stream_channels=["output"]
)

# Execute
result = pregel.invoke({"value": 5})
print(result)  # {"result": 6}
```

### NodeBuilder with Subscriptions

```python
from langgraph.pregel import NodeBuilder
from langgraph.channels import LastValue

# Create channels
channels = {
    "signal": LastValue(bool),
    "data": LastValue(dict),
    "output": LastValue(dict)
}

# Node that only executes when signal changes
conditional_node = NodeBuilder() \
    .subscribe_only("signal") \
    .read_from("signal", "data") \
    .do(lambda state: {"output": state["data"]} if state["signal"] else {}) \
    .write_to("output") \
    .build()

# Node that executes when any channel changes
listener_node = NodeBuilder() \
    .subscribe_to("signal", "data") \
    .read_from("signal", "data") \
    .do(lambda state: {"output": "updated"}) \
    .write_to("output") \
    .build()
```

### NodeBuilder with Retry and Cache

```python
from langgraph.pregel import NodeBuilder
from langgraph.types import RetryPolicy, CachePolicy

def expensive_operation(state):
    # Might fail or be slow
    return {"result": complex_computation(state)}

node = NodeBuilder() \
    .read_from("input") \
    .do(expensive_operation) \
    .write_to("output") \
    .add_retry_policies(
        RetryPolicy(
            max_attempts=3,
            retry_on=ConnectionError
        )
    ) \
    .add_cache_policy(
        CachePolicy(ttl=3600)
    ) \
    .build()
```

### Custom Channel Mapping

```python
from langgraph.pregel import NodeBuilder

def output_mapper(result):
    # Transform node output before writing to channels
    return {
        "result": result["value"],
        "metadata": {"processed": True}
    }

node = NodeBuilder() \
    .read_from("input") \
    .do(process_fn) \
    .write_to("result", "metadata", mapper=output_mapper) \
    .build()
```

### Node with Metadata

```python
from langgraph.pregel import NodeBuilder
from langgraph.constants import TAG_NOSTREAM, TAG_HIDDEN

# Hidden node with custom metadata
node = NodeBuilder() \
    .read_from("input") \
    .do(internal_fn) \
    .write_to("output") \
    .meta(
        TAG_HIDDEN,
        priority="low",
        timeout=30,
        description="Internal utility node"
    ) \
    .build()
```

### Multiple Retry Policies

```python
from langgraph.pregel import NodeBuilder
from langgraph.types import RetryPolicy

# Different retry strategies for different errors
node = NodeBuilder() \
    .read_from("input") \
    .do(api_call) \
    .write_to("output") \
    .add_retry_policies(
        RetryPolicy(
            max_attempts=5,
            initial_interval=0.1,
            retry_on=ConnectionError
        ),
        RetryPolicy(
            max_attempts=3,
            initial_interval=1.0,
            retry_on=TimeoutError
        )
    ) \
    .build()
```

### Pregel with Step Timeout

```python
from langgraph.pregel import Pregel

pregel = Pregel(
    nodes=nodes,
    channels=channels,
    input_channels="input",
    output_channels="output",
    step_timeout=30.0  # 30 second timeout per step
)

try:
    result = pregel.invoke(input)
except TimeoutError:
    print("Step exceeded 30 second timeout")
```

### Pregel Stream Modes

```python
from langgraph.pregel import Pregel

pregel = Pregel(
    nodes=nodes,
    channels=channels,
    input_channels="input",
    output_channels="output",
    stream_mode=["updates", "debug"]  # Multiple stream modes
)

for chunk in pregel.stream(input):
    print(f"Stream event: {chunk}")
```

### Dynamic Node Execution

```python
from langgraph.pregel import Pregel, NodeBuilder
from langgraph.channels import LastValue

# Nodes that trigger based on channel updates
node_a = NodeBuilder() \
    .subscribe_only("channel_a") \
    .read_from("channel_a") \
    .do(lambda x: {"result_a": x["value"]}) \
    .write_to("result_a") \
    .build()

node_b = NodeBuilder() \
    .subscribe_only("channel_b") \
    .read_from("channel_b") \
    .do(lambda x: {"result_b": x["value"]}) \
    .write_to("result_b") \
    .build()

channels = {
    "channel_a": LastValue(dict),
    "channel_b": LastValue(dict),
    "result_a": LastValue(dict),
    "result_b": LastValue(dict)
}

pregel = Pregel(
    nodes={"node_a": node_a, "node_b": node_b},
    channels=channels,
    input_channels=["channel_a", "channel_b"],
    output_channels=["result_a", "result_b"]
)

# Only nodes subscribed to updated channels will execute
result = pregel.invoke({"channel_a": {"value": 1}})
# Only node_a executes
```

### Pregel with Interrupts

```python
from langgraph.pregel import Pregel
from langgraph.checkpoint.memory import MemorySaver

pregel = Pregel(
    nodes=nodes,
    channels=channels,
    input_channels="input",
    output_channels="output",
    interrupt_before=["critical_node"],
    interrupt_after=["review_node"]
)

# Requires checkpointer for interrupts
checkpointer = MemorySaver()
pregel = pregel.with_config(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "thread-1"}}

# Execute until interrupt
pregel.invoke(input, config)

# Check state at interrupt
state = pregel.get_state(config)
print(f"Interrupted before: {state.next}")

# Continue
pregel.invoke(None, config)
```

### Pregel Copy and Configure

```python
from langgraph.pregel import Pregel

# Base pregel
base_pregel = Pregel(
    nodes=nodes,
    channels=channels,
    input_channels="input",
    output_channels="output"
)

# Create configured variants
debug_pregel = base_pregel.with_config(debug=True)

timeout_pregel = base_pregel.copy(update={
    "step_timeout": 60.0
})

# Each variant is independent
```

### Advanced Channel Configuration

```python
from langgraph.pregel import Pregel, NodeBuilder
from langgraph.channels import LastValue, BinaryOperatorAggregate
from operator import add

channels = {
    "input": LastValue(dict),
    "accumulator": BinaryOperatorAggregate(list, add),
    "output": LastValue(list)
}

accumulate_node = NodeBuilder() \
    .read_from("input", "accumulator") \
    .do(lambda state: {"accumulator": [state["input"]["value"]]}) \
    .write_to("accumulator") \
    .build()

finalize_node = NodeBuilder() \
    .read_from("accumulator") \
    .do(lambda state: {"output": state["accumulator"]}) \
    .write_to("output") \
    .build()

pregel = Pregel(
    nodes={"accumulate": accumulate_node, "finalize": finalize_node},
    channels=channels,
    input_channels="input",
    output_channels="output"
)
```

### Pregel Validation

```python
from langgraph.pregel import Pregel

try:
    pregel = Pregel(
        nodes=nodes,
        channels=channels,
        input_channels="input",
        output_channels="output"
    )

    # Validate configuration
    pregel.validate()

except ValueError as e:
    print(f"Invalid graph configuration: {e}")
```

### Async Pregel Operations

```python
import asyncio
from langgraph.pregel import Pregel

async def execute_async():
    pregel = Pregel(
        nodes=nodes,
        channels=channels,
        input_channels="input",
        output_channels="output"
    )

    # Async invoke
    result = await pregel.ainvoke(input)

    # Async stream
    async for chunk in pregel.astream(input):
        print(f"Chunk: {chunk}")

    # Async state operations
    config = {"configurable": {"thread_id": "thread-1"}}
    state = await pregel.aget_state(config)

asyncio.run(execute_async())
```

## Types

### PregelNode

```python { .api }
class PregelNode:
    """
    A configured node in the Pregel execution graph.

    Created by NodeBuilder.build(). Contains channel subscriptions,
    action, and policies.

    Fields:
        channels: Channels this node reads from
        triggers: Channels that trigger this node
        action: Function or Runnable to execute
        writers: Channels to write output to
        retry_policies: Retry policies for this node
        cache_policy: Cache policy for this node
        tags: Set of tags
        metadata: Dict of metadata
    """
    ...
```

### RunnableLike

```python { .api }
RunnableLike = Callable | Runnable
"""
Type alias for node actions.

Can be:
- A function that takes state and returns updates
- A LangChain Runnable
"""
```

### Graph

```python { .api }
class Graph:
    """
    Drawable graph representation.

    Returned by get_graph() for visualization and export.

    Methods:
        draw_ascii(): Draw graph as ASCII art
        draw_mermaid(): Generate Mermaid diagram
        draw_png(): Generate PNG image (requires graphviz)
    """
    ...
```
