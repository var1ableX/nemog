# Message Handling

Specialized utilities for managing conversation messages in agent workflows. Merge, add, and manipulate message lists with automatic deduplication by ID, and manage UI-specific messages with dedicated reducers.

## Capabilities

### add_messages

Merge message lists by updating existing messages by ID or appending new ones.

```python { .api }
def add_messages(
    left: Messages,
    right: Messages,
    format: Literal["langchain-openai"] | None = None
) -> Messages:
    """
    Merge message lists, updating existing messages by ID.

    This function is the default reducer for MessagesState. It merges two
    message lists by:
    - Updating messages that exist in both lists (matched by ID)
    - Appending new messages from the right list
    - Preserving order from the left list
    - Supporting message deletion via RemoveMessage sentinel

    Args:
        left: Existing message list (current state)
        right: New messages to merge (updates)
        format: Optional format hint for message serialization

    Returns:
        Merged message list with updates applied

    Note:
        Messages are matched by their ID. Messages without IDs are always
        appended. Use RemoveMessage to delete messages by ID.
    """
    ...
```

### push_message

Push one or more messages to the messages state.

```python { .api }
def push_message(messages: Messages) -> dict[str, Messages]:
    """
    Push message(s) to state.

    Helper function to construct a state update dict that adds messages
    to the "messages" field.

    Args:
        messages: Single message or list of messages to add

    Returns:
        Dict with "messages" key containing the messages to add

    Example:
        return push_message(AIMessage(content="Hello"))
        # Returns: {"messages": [AIMessage(content="Hello")]}
    """
    ...
```

### push_ui_message

Push a UI message to state with automatic reducer handling.

```python { .api }
def push_ui_message(
    message: UIMessage,
    state_key: str = "ui"
) -> UIMessage:
    """
    Push UI message to state.

    Creates or updates a UI message in the specified state key. UI messages
    are managed separately from conversation messages and are typically used
    for interface elements, loading states, or ephemeral notifications.

    Args:
        message: UIMessage with content and optional id
        state_key: State field name for UI messages (default: "ui")

    Returns:
        The UIMessage that was pushed

    Note:
        Requires using ui_message_reducer for the target state field.
    """
    ...
```

### delete_ui_message

Delete a UI message from state by ID.

```python { .api }
def delete_ui_message(
    id: str,
    state_key: str = "ui"
) -> RemoveUIMessage:
    """
    Delete UI message from state.

    Removes a UI message identified by its ID from the specified state field.

    Args:
        id: ID of the UI message to remove
        state_key: State field name for UI messages (default: "ui")

    Returns:
        RemoveUIMessage marker for deletion

    Note:
        Requires using ui_message_reducer for the target state field.
    """
    ...
```

### ui_message_reducer

Reducer function for managing UI message state updates.

```python { .api }
def ui_message_reducer(
    state: dict | None,
    updates: Any
) -> dict:
    """
    Reducer for UI message updates.

    Handles adding, updating, and removing UI messages from state.
    UI messages are stored by ID and can be individually updated or removed.

    Args:
        state: Current UI message state (dict of id -> message)
        updates: Update to apply (UIMessage, RemoveUIMessage, or dict)

    Returns:
        Updated UI message state dict

    Note:
        Use this as the reducer annotation for UI message state fields:
        ui: Annotated[dict[str, UIMessage], ui_message_reducer]
    """
    ...
```

## Usage Examples

### Basic Message Merging

```python
from langgraph.graph import add_messages, MessagesState, StateGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

class State(MessagesState):
    pass

builder = StateGraph(State)

def chatbot(state: State) -> dict:
    messages = state["messages"]
    last_message = messages[-1]

    # Add AI response
    return {
        "messages": [AIMessage(content=f"Response to: {last_message.content}")]
    }

builder.add_node("chatbot", chatbot)
builder.add_edge(START, "chatbot")
builder.add_edge("chatbot", END)

graph = builder.compile()

# Initial messages
result = graph.invoke({
    "messages": [HumanMessage(content="Hello")]
})

print(result["messages"])
# [HumanMessage(content="Hello"), AIMessage(content="Response to: Hello")]

# Continue conversation - messages are merged
result = graph.invoke({
    "messages": result["messages"] + [HumanMessage(content="How are you?")]
})

print(len(result["messages"]))  # 4 messages total
```

### Message Graph Convenience

```python
from langgraph.graph import MessageGraph, START, END
from langchain_core.messages import HumanMessage, AIMessage

# MessageGraph is pre-configured with MessagesState
graph_builder = MessageGraph()

def respond(state):
    messages = state["messages"]
    return {
        "messages": [AIMessage(content="I'm doing well!")]
    }

graph_builder.add_node("respond", respond)
graph_builder.add_edge(START, "respond")
graph_builder.add_edge("respond", END)

graph = graph_builder.compile()

result = graph.invoke({
    "messages": [HumanMessage(content="Hi")]
})
```

### Using push_message Helper

```python
from langgraph.graph import push_message, MessagesState, StateGraph, START, END
from langchain_core.messages import AIMessage

class State(MessagesState):
    pass

def process_node(state: State):
    # Use push_message helper for cleaner code
    return push_message(AIMessage(content="Processed"))

builder = StateGraph(State)
builder.add_node("process", process_node)
builder.add_edge(START, "process")
builder.add_edge("process", END)

graph = builder.compile()
```

### Updating Messages by ID

```python
from langgraph.graph import add_messages, MessagesState, StateGraph, START, END
from langchain_core.messages import AIMessage
from typing_extensions import Annotated

class State(MessagesState):
    pass

builder = StateGraph(State)

def initial_response(state: State):
    # Create message with explicit ID
    return {
        "messages": [AIMessage(content="Thinking...", id="response-1")]
    }

def update_response(state: State):
    # Update the message with the same ID
    return {
        "messages": [AIMessage(content="Done thinking!", id="response-1")]
    }

builder.add_node("initial", initial_response)
builder.add_node("update", update_response)
builder.add_edge(START, "initial")
builder.add_edge("initial", "update")
builder.add_edge("update", END)

graph = builder.compile()

result = graph.invoke({"messages": []})
print(len(result["messages"]))  # 1 - message was updated, not appended
print(result["messages"][0].content)  # "Done thinking!"
```

### Custom Message State with add_messages

```python
from langgraph.graph import add_messages, StateGraph, START, END
from typing_extensions import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class CustomState(TypedDict):
    conversation: Annotated[list[BaseMessage], add_messages]
    context: str

def chat_node(state: CustomState):
    messages = state["conversation"]
    context = state["context"]

    return {
        "conversation": [AIMessage(content=f"Responding in {context} context")]
    }

builder = StateGraph(CustomState)
builder.add_node("chat", chat_node)
builder.add_edge(START, "chat")
builder.add_edge("chat", END)

graph = builder.compile()

result = graph.invoke({
    "conversation": [HumanMessage(content="Hello")],
    "context": "technical"
})

print(len(result["conversation"]))  # 2 messages
```

### UI Messages for Interface State

```python
from langgraph.graph import StateGraph, START, END
from langgraph.graph import push_ui_message, delete_ui_message, ui_message_reducer, UIMessage
from typing_extensions import TypedDict, Annotated

class State(TypedDict):
    query: str
    result: str
    ui: Annotated[dict[str, UIMessage], ui_message_reducer]

builder = StateGraph(State)

def show_loading(state: State):
    # Show loading UI message
    return {
        "ui": push_ui_message(
            UIMessage(id="loading", content="Processing your request...")
        )
    }

def process_query(state: State):
    # Process the query
    result = f"Processed: {state['query']}"
    return {"result": result}

def hide_loading(state: State):
    # Remove loading message
    return {
        "ui": delete_ui_message("loading")
    }

builder.add_node("loading", show_loading)
builder.add_node("process", process_query)
builder.add_node("cleanup", hide_loading)
builder.add_edge(START, "loading")
builder.add_edge("loading", "process")
builder.add_edge("process", "cleanup")
builder.add_edge("cleanup", END)

graph = builder.compile()

result = graph.invoke({
    "query": "test",
    "result": "",
    "ui": {}
})

print(result["ui"])  # {} - loading message was removed
```

### Multiple UI Messages

```python
from langgraph.graph import push_ui_message, UIMessage, ui_message_reducer
from typing_extensions import TypedDict, Annotated

class State(TypedDict):
    ui: Annotated[dict[str, UIMessage], ui_message_reducer]

def add_notifications(state: State):
    return {
        "ui": {
            "notification-1": UIMessage(id="notification-1", content="Task 1 complete"),
            "notification-2": UIMessage(id="notification-2", content="Task 2 started"),
        }
    }

# UI messages are merged by ID
```

### Removing All Messages

```python
from langgraph.graph import add_messages, REMOVE_ALL_MESSAGES
from langchain_core.messages import HumanMessage, AIMessage

# Use REMOVE_ALL_MESSAGES sentinel to clear message list
def clear_history(state):
    return {
        "messages": [REMOVE_ALL_MESSAGES, HumanMessage(content="Starting fresh")]
    }

# Results in a state with only the new message
```

### Format-Specific Message Handling

```python
from langgraph.graph import add_messages
from langchain_core.messages import AIMessage

# Use format parameter for specific serialization
messages = add_messages(
    left=[AIMessage(content="Hello")],
    right=[AIMessage(content="World")],
    format="langchain-openai"
)

# Messages are merged with OpenAI-specific formatting rules
```

## Types

### Messages

```python { .api }
Messages = list[MessageLikeRepresentation] | MessageLikeRepresentation
"""
Type alias for message or list of messages.

MessageLikeRepresentation includes:
- LangChain BaseMessage subclasses (HumanMessage, AIMessage, SystemMessage, etc.)
- Dict representations of messages
- Tuples of (role, content)
"""
```

### MessagesState

```python { .api }
class MessagesState(TypedDict):
    """
    Predefined state schema with messages field.

    The messages field uses add_messages as its reducer, automatically
    merging new messages with existing ones by ID.

    Fields:
        messages: List of conversation messages with automatic merging
    """
    messages: Annotated[list[MessageLikeRepresentation], add_messages]
```

### UIMessage

```python { .api }
class UIMessage(TypedDict):
    """
    UI message for interface state management.

    UI messages are separate from conversation messages and are typically
    used for loading states, notifications, and other ephemeral UI elements.

    Fields:
        id: Unique identifier for the message (optional, auto-generated if not provided)
        content: Message content (string or any JSON-serializable data)
    """
    id: str | None
    content: Any
```

### RemoveUIMessage

```python { .api }
class RemoveUIMessage(TypedDict):
    """
    Marker for removing a UI message by ID.

    Created by delete_ui_message() function.

    Fields:
        id: ID of the UI message to remove
        remove: Always True (marker flag)
    """
    id: str
    remove: bool
```

### REMOVE_ALL_MESSAGES

```python { .api }
REMOVE_ALL_MESSAGES: str = "__remove_all__"
"""
Sentinel value to remove all messages from a message list.

Use this in a message update to clear all existing messages before
adding new ones.

Example:
    return {"messages": [REMOVE_ALL_MESSAGES, HumanMessage(content="New")]}
"""
```
