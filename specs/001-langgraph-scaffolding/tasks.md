# Tasks: Graph-Based Application Scaffolding

**Feature**: `001-langgraph-scaffolding`
**Date**: 2026-02-17
**Status**: Ready for implementation

## Plan Readiness Report

```text
+-----------------------------------------------+
|  PLAN READINESS REPORT                        |
+-----------------------------------------------+
|  Tech Stack:       Defined              [Y]   |
|  User Stories:     3 found with criteria[Y]   |
|  Shared Entities:  1 (GraphState)       [Y]   |
|  API Contracts:    1 service run method [Y]   |
|  Research Items:   3 decisions documented[Y]  |
+-----------------------------------------------+
|  TASK GENERATION: READY                       |
+-----------------------------------------------+
```

## Implementation Strategy
Following the **Red-Green-Refactor** constitutional requirement, all implementation tasks are preceded by test creation tasks. We will build the scaffolding incrementally:
1. **Setup**: Initialize the project structure.
2. **Foundational**: Define the state and input stubs.
3. **User Story 1 (P1)**: Implement the core "Hello World" graph flow.
4. **User Story 2 (P2)**: Implement the layered architecture (Service -> Graph).
5. **User Story 3 (P3)**: Implement conditional branching logic.
6. **Polish**: Final integration and verification.

---

## Phase 1: Setup

- [x] T001 Create project structure: `src/app/`, `src/services/`, `src/graphs/`, `tests/unit/`, `tests/integration/`, `tests/contract/`
- [x] T002 Configure `pyproject.toml` or `requirements.txt` with `langgraph`, `typing-extensions`, `pytest`, `pytest-asyncio`

## Phase 2: Foundational

- [x] T003 Create `src/graphs/state.py` and implement `GraphState` TypedDict
- [x] T004 [P] Implement `src/app/stubs.py` with `userPrompt` function returning a hardcoded string
- [x] T005 [P] Create unit test `tests/unit/test_state.py` to satisfy TS-012 and TS-013

## Phase 3: User Story 1 - Basic "Hello World" Execution (Priority: P1)

- [x] T006 [US1] Create integration test `tests/integration/test_hello_world.py` to satisfy TS-001 and TS-002
- [x] T007 [US1] Create `src/graphs/writer_graph.py` and implement a basic `StateGraph` with a single processing node
- [x] T008 [US1] Implement `src/app/main.py` entry point to execute the graph directly (initial version)
- [x] T009 [US1] Verify T006 passes (Red-Green cycle)

## Phase 4: User Story 2 - Layered Architecture Invocation (Priority: P2)

- [x] T010 [US2] Create contract test `tests/contract/test_writer_svc.py` to satisfy TS-010
- [x] T011 [US2] Implement `src/services/writer_svc.py` with `WriterSvc` class to encapsulate graph execution
- [x] T012 [US2] Refactor `src/app/main.py` to call `WriterSvc` instead of the graph directly per TS-003 and TS-004
- [x] T013 [US2] Verify T010 passes and TS-003/TS-004 are satisfied

## Phase 5: User Story 3 - Conditional Logic Demonstration (Priority: P3)

- [x] T014 [US3] Create integration test `tests/integration/test_branching.py` to satisfy TS-005, TS-006, and TS-007
- [x] T015 [US3] Update `src/graphs/writer_graph.py` to include a conditional edge with random logic per TS-005
- [x] T016 [US3] Implement `world_node` and `universe_node` in `src/graphs/writer_graph.py` per TS-006 and TS-007
- [x] T017 [US3] Verify T014 passes and TS-008 (reachability) is satisfied by running multiple times

## Final Phase: Polish & Cross-Cutting Concerns

- [x] T018 Implement graceful handling for empty input in `src/services/writer_svc.py` to satisfy TS-009
- [x] T019 Final verification: Run all tests in `tests/` and ensure 100% pass rate
- [x] T020 Review implementation against `quickstart.md` and `CONSTITUTION.md`

---

## Dependency Graph Analysis

```text
+-----------------------------------------------+
|  DEPENDENCY GRAPH ANALYSIS                    |
+-----------------------------------------------+
|  Total Tasks:      20                         |
|  Circular Deps:    None found           [Y]   |
|  Orphan Tasks:     None found           [Y]   |
|  Critical Path:    T001 -> T003 -> T006 -> T007 -> T010 -> T011 -> T014 -> T015 -> T019
|  Phase Boundaries: Valid                [Y]   |
|  Story Independence: Yes                [Y]   |
+-----------------------------------------------+
|  Parallel Opportunities: T004, T005, T010     |
+-----------------------------------------------+
```

### Parallel Batches
- **Batch 1**: [T004, T005] (Setup & Foundation)
- **Batch 2**: [T010] (User Story 2 Contract Test)

## Traceability Summary
Tasks are mapped directly to Test Specifications (TS-XXX) to ensure TDD compliance:
- **TS-001, TS-002** -> T006
- **TS-003, TS-004** -> T012
- **TS-005, TS-006, TS-007** -> T014
- **TS-008** -> T017
- **TS-009** -> T018
- **TS-010** -> T010
- **TS-011** -> T007
- **TS-012, TS-013** -> T005
