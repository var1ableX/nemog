# Research & Decisions: Graph-Based Application Scaffolding

**Feature**: `001-langgraph-scaffolding`
**Date**: 2026-02-17

## Tessl Tiles

### Installed Tiles

| Technology | Tile | Type | Version |
|------------|------|------|---------|
| LangGraph | `tessl/pypi-langgraph` | Documentation | 1.0.3 |
| Python | `trailofbits/skills` | Skills (modern-python) | 776ccc... |
| LangGraph CLI | `tessl/pypi-langgraph-cli` | Documentation | 0.4.0 |
| Pytest | `tessl/pypi-pytest` | Documentation | 8.4.0 |
| LangChain | `tessl/pypi-langchain` | Documentation | 1.2.1 |

### Available Skills

- `/modern-python` - Generate modern, idiomatic Python code.

### Technologies Without Tiles

- `typing-extensions`: No specific tile found (standard library/common).

## Research Items

### 1. LangGraph Conditional Edges
- **Question**: How to implement branching based on a random number?
- **Finding**: Use `builder.add_conditional_edges(source_node, decision_function, {0: "world_node", 1: "universe_node"})`.
- **Decision**: The `decision_function` will contain `random.randint(0, 1)`.

### 2. Layered Architecture (Main -> Svc -> Graph)
- **Question**: How to best isolate the graph from the entry point?
- **Finding**: The Service layer (`WriterSvc`) should own the `MemorySaver` and the `CompiledGraph` object. `main.py` should only interact with a high-level `run()` method.
- **Decision**: Create a `WriterSvc` class that encapsulates graph compilation.

### 3. State Management
- **Question**: What state is needed for a "Hello World" branch?
- **Finding**: Minimal state needed is a dictionary with a `message` key.
- **Decision**: Use `typing.TypedDict` for `GraphState`.

## Consolidated Findings

- **Decision**: Use LangGraph Functional API (or StateGraph) for simplicity.
- **Rationale**: StateGraph is more explicit for scaffolding and learning.
- **Alternatives considered**: Simple `if/else` in service. Rejected because the goal is specifically to scaffold a graph-based framework.
