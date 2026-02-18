# Quickstart: Graph-Based Application Scaffolding

**Feature**: `001-langgraph-scaffolding`

## Installation

Ensure dependencies are installed:
```bash
pip install langgraph typing-extensions pytest pytest-asyncio
```

## Running the Application

Execute the entry point:
```bash
python src/app/main.py
```

### Expected Output
The application will print a message based on a random decision:
```text
Input received: [Hardcoded String]
Result: Hello World
```
OR
```text
Input received: [Hardcoded String]
Result: Hello Universe
```

## Running Tests

Execute the test suite:
```bash
pytest
```

## Adding a New Branch

To add "Hello Multiverse":
1. Add a node `multiverse_node` in `writer_graph.py`.
2. Update the conditional edge mapping to include a new value (e.g., `2`).
3. Update the decision logic to include `2`.
