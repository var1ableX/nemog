# Data Model: Graph-Based Application Scaffolding

**Feature**: `001-langgraph-scaffolding`

## Entities

### 1. GraphState
The primary state object passed between nodes in the graph.

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `input` | `str` | The initial string from `userPrompt`. | MUST not be null. |
| `message` | `str` | The generated greeting. | Defaults to empty string. |
| `decision` | `int` | The random value (0 or 1). | Range [0, 1]. |

## State Transitions (Graph Flow)

1. **START** -> `process_input` node
2. `process_input` -> **Conditional Edge**
   - If `decision == 0` -> `world_node`
   - If `decision == 1` -> `universe_node`
3. `world_node` -> **END**
4. `universe_node` -> **END**

## Logic Definition

- **`process_input`**: Generates `random.randint(0, 1)` and stores in state.
- **`world_node`**: Sets `message = "Hello World"`.
- **`universe_node`**: Sets `message = "Hello Universe"`.
