<!--
SYNC IMPACT REPORT
- Version change: none -> 1.0.0
- List of modified principles: initial draft
- Added/removed sections: all
- Templates requiring updates: none
- Follow-up TODOs: none
-->

# nemog Constitution

## Core Principles

### I. Spec-Driven Intent
Every feature and change must originate from a clear specification. Code and implementation details are secondary to the intent captured in the specification. Implementation without an approved specification is strictly prohibited.

### II. Deterministic Orchestration
AI logic must be managed through structured, predictable workflows. Complexity should be handled by the architectural scaffolding, not by increasing prompt length or model dependency. We prioritize "Scaffolding over Model".

### III. Guardrails by Default
AI outputs and inputs must be validated against safety and functional constraints. Failure to meet guardrails is a system failure, not an edge case. Validation is an integral part of the design, not an afterthought.

### IV. Test-First Integrity
Implementation only proceeds once a test specification exists and has been verified against the feature specification. The Red-Green-Refactor cycle is the baseline development requirement for all features.

### V. Simplicity and Composability
Solutions should be built from small, composable units. Avoid monolithic AI structures; favor multi-step, verifiable flows that are easy to debug and maintain.

## Quality and Compliance

All code must achieve a 100% pass rate on specification-driven tests before being considered for inclusion in the project. Documentation, specifications, and implementation must remain in absolute sync at all times.

## Development Workflow

The project follows a phase-gated development workflow: Specification, Planning, Testing, Tasking, and Implementation. Each phase must produce verifiable artifacts that are cross-checked for consistency before the next phase begins.

## Governance

This constitution is the supreme governing document of the project. Any deviation from these principles must be formally justified, and if the deviation is permanent, the constitution must be amended. Amendments require a version bump following semantic versioning principles.

**Version**: 1.0.0 | **Ratified**: 2026-02-17 | **Last Amended**: 2026-02-17
