# Interrupts and Human-in-the-Loop

Pause graph execution at specific points to allow human inspection, intervention, and approval. Resume execution with modified state or user input, enabling human-in-the-loop workflows.

## Capabilities

### Interrupt Function

Interrupt graph execution from within a node with a resumable value.

```python { .api }
def interrupt(value: Any) -> Any:
    """
    Interrupt graph execution from within a node.

    The graph will pause and return the interrupt value. Execution can be
    resumed later by passing a Command with resume value.

    Args:
        value: Value to return to caller. This can be used to prompt for input,
               show options, or provide context for the interrupt.

    Returns:
        The resume value provided when execution continues.

    Raises:
        GraphInterrupt: Internally raised to pause execution (caught by runtime)

    Example:
        def approval_node(state):
            # Interrupt and ask for approval
            user_approved = interrupt("Please approve this action")
            if user_approved:
                return {"status": "approved"}
            else:
                return {"status": "rejected"}
    """
    ...
```

### Command

Control graph flow and provide resume values after interrupts.

```python { .api }
class Command:
    """
    Command to update graph state and control flow upon resumption.

    Use this when resuming from an interrupt or when sending dynamic messages
    to nodes during execution.

    Fields:
        graph: Target graph ("__parent__" for parent graph, None for current)
        update: State updates to apply
        resume: Value to resume with (passed to node that called interrupt())
        goto: Nodes to navigate to (Send objects or node names)
    """
    graph: str | None = None
    update: Any | None = None
    resume: dict[str, Any] | Any | None = None
    goto: Send | Sequence[Send] = ()
```

### Send

Send messages to specific nodes for dynamic parallel execution.

```python { .api }
class Send:
    """
    Message to send to a specific node.

    Used for dynamic parallel execution where the number and targets of
    parallel branches are determined at runtime.

    Fields:
        node: Target node name to execute
        arg: State or message to send to the node
    """
    node: str
    arg: Any
```

### Interrupt Configuration

Configure interrupts when compiling the graph.

```python { .api }
class StateGraph:
    def compile(
        self,
        interrupt_before: Sequence[str] | All = None,
        interrupt_after: Sequence[str] | All = None,
        ...
    ) -> CompiledStateGraph:
        """
        Compile graph with interrupt configuration.

        Args:
            interrupt_before: Nodes to interrupt before executing.
                             Use ["*"] or All to interrupt before all nodes.
            interrupt_after: Nodes to interrupt after executing.
                            Use ["*"] or All to interrupt after all nodes.
            ...

        Returns:
            Compiled graph with interrupt points configured
        """
        ...
```

## Usage Examples

### Basic Interrupt for Approval

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

class State(TypedDict):
    request: str
    approved: bool
    response: str

def request_approval(state: State) -> dict:
    """Node that interrupts for human approval"""
    # Interrupt execution and wait for approval
    approval_response = interrupt(
        f"Approve request: {state['request']}? (yes/no)"
    )
    return {"approved": approval_response == "yes"}

def process_request(state: State) -> dict:
    """Process if approved"""
    if state["approved"]:
        return {"response": f"Processed: {state['request']}"}
    else:
        return {"response": "Request denied"}

builder = StateGraph(State)
builder.add_node("approval", request_approval)
builder.add_node("process", process_request)
builder.add_edge(START, "approval")
builder.add_edge("approval", "process")
builder.add_edge("process", END)

# Must have checkpointer for interrupts
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

# Execute until interrupt
config = {"configurable": {"thread_id": "thread-1"}}
result = None
for chunk in graph.stream(
    {"request": "deploy to production", "approved": False, "response": ""},
    config
):
    print(f"Chunk: {chunk}")
# Execution pauses at interrupt()

# Check state - next node shows where we're paused
state = graph.get_state(config)
print(f"Paused, next: {state.next}")
print(f"Interrupts: {state.interrupts}")

# Resume with approval
for chunk in graph.stream(Command(resume="yes"), config):
    print(f"After approval: {chunk}")
```

### Interrupt Before Node

```python
# Configure interrupts at compile time
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["approval"]  # Pause before approval node
)

config = {"configurable": {"thread_id": "thread-2"}}

# Execute - will stop before approval node
for chunk in graph.stream(
    {"request": "delete database", "approved": False, "response": ""},
    config
):
    print(chunk)

# Check where we're paused
state = graph.get_state(config)
print(f"Paused before: {state.next}")  # ('approval',)

# Can modify state before continuing
new_config = graph.update_state(
    config,
    {"request": "delete test database"}  # Modify request
)

# Resume execution
for chunk in graph.stream(None, new_config):
    print(chunk)
```

### Interrupt After Node

```python
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_after=["approval"]  # Pause after approval node
)

config = {"configurable": {"thread_id": "thread-3"}}

# Execute - will stop after approval
for chunk in graph.stream(
    {"request": "restart service", "approved": False, "response": ""},
    config
):
    print(chunk)

# Check state after approval ran
state = graph.get_state(config)
print(f"Approved: {state.values['approved']}")
print(f"Next: {state.next}")  # ('process',)

# Can modify approval before continuing
new_config = graph.update_state(
    config,
    {"approved": True}
)

# Continue to process
for chunk in graph.stream(None, new_config):
    print(chunk)
```

### Multiple Interrupts in Workflow

```python
class WorkflowState(TypedDict):
    plan: str
    plan_approved: bool
    execution_log: list[str]
    final_approved: bool

def create_plan(state: WorkflowState) -> dict:
    plan = "1. Backup data\n2. Update schema\n3. Migrate data"
    return {"plan": plan}

def review_plan(state: WorkflowState) -> dict:
    # First interrupt
    approved = interrupt(f"Review plan:\n{state['plan']}")
    return {"plan_approved": approved}

def execute_plan(state: WorkflowState) -> dict:
    log = ["Executed step 1", "Executed step 2", "Executed step 3"]
    return {"execution_log": log}

def final_review(state: WorkflowState) -> dict:
    # Second interrupt
    approved = interrupt(
        f"Execution complete:\n{chr(10).join(state['execution_log'])}\nApprove?"
    )
    return {"final_approved": approved}

builder = StateGraph(WorkflowState)
builder.add_node("plan", create_plan)
builder.add_node("review", review_plan)
builder.add_node("execute", execute_plan)
builder.add_node("final", final_review)
builder.add_edge(START, "plan")
builder.add_edge("plan", "review")
builder.add_edge("review", "execute")
builder.add_edge("execute", "final")
builder.add_edge("final", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "workflow-1"}}

# Execute until first interrupt
for chunk in graph.stream({
    "plan": "",
    "plan_approved": False,
    "execution_log": [],
    "final_approved": False
}, config):
    print(f"Step 1: {chunk}")

# Resume plan review with approval
for chunk in graph.stream(Command(resume=True), config):
    print(f"Step 2: {chunk}")

# Resume final review with approval
for chunk in graph.stream(Command(resume=True), config):
    print(f"Step 3: {chunk}")
```

### Dynamic Parallel Execution with Send

```python
from langgraph.types import Send

class ParallelState(TypedDict):
    items: list[str]
    results: list[str]

def fan_out(state: ParallelState) -> list[Send]:
    """Create parallel Send for each item"""
    return [Send("process_item", {"item": item}) for item in state["items"]]

def process_item(item_data: dict) -> dict:
    """Process single item"""
    result = f"Processed: {item_data['item']}"
    return {"results": [result]}

builder = StateGraph(ParallelState)
builder.add_node("fan_out", fan_out)
builder.add_node("process_item", process_item)
builder.add_edge(START, "fan_out")
builder.add_conditional_edges("fan_out", lambda x: [])  # Dynamic sends
builder.add_edge("process_item", END)

graph = builder.compile()

result = graph.invoke({
    "items": ["task1", "task2", "task3"],
    "results": []
})
print(result["results"])
# All items processed in parallel
```

### Command with State Update and Resume

```python
class TaskState(TypedDict):
    task: str
    params: dict
    result: str

def execute_task(state: TaskState) -> dict:
    # Interrupt for parameter confirmation
    confirmed_params = interrupt({
        "message": "Confirm parameters",
        "task": state["task"],
        "params": state["params"]
    })
    # Use confirmed params
    return {"result": f"Executed with {confirmed_params}"}

builder = StateGraph(TaskState)
builder.add_node("execute", execute_task)
builder.add_edge(START, "execute")
builder.add_edge("execute", END)

checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "task-1"}}

# Execute until interrupt
for chunk in graph.stream({
    "task": "backup",
    "params": {"target": "prod"},
    "result": ""
}, config):
    print(chunk)

# Resume with modified params and state update
for chunk in graph.stream(
    Command(
        update={"task": "backup_verified"},  # Update state
        resume={"target": "staging"}  # Modified params
    ),
    config
):
    print(chunk)
```

### Interrupt All Nodes

```python
# Interrupt before every node
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["*"]  # or interrupt_before=All
)

# Each node requires explicit continuation
config = {"configurable": {"thread_id": "manual-1"}}

# Will stop before first node
for chunk in graph.stream(initial_state, config):
    print(chunk)

# Continue to next node
for chunk in graph.stream(None, config):
    print(chunk)

# Continue to next node
for chunk in graph.stream(None, config):
    print(chunk)
```

### Check Interrupt Status

```python
# Get current state to check interrupts
state = graph.get_state(config)

if state.interrupts:
    print(f"Graph is interrupted: {len(state.interrupts)} interrupts")
    for intr in state.interrupts:
        print(f"  Interrupt ID: {intr.id}")
        print(f"  Value: {intr.value}")
else:
    print("No interrupts")

# Check next nodes
if state.next:
    print(f"Next to execute: {state.next}")
else:
    print("Execution complete")
```

## Types

### All

```python { .api }
All = Literal["*"]
"""
Special value to interrupt at all nodes.
Use as interrupt_before or interrupt_after value.
"""
```
