# nemog Development Guide

**Last updated**: 2026-02-17

## Overview

This project uses specification-driven development with Intent Integrity Kit skills.

## Workflow

The development workflow follows these phases:

1. `/iikit-constitution` - Define project governance principles
2. `/iikit-specify` - Create feature specification from natural language
3. `/iikit-clarify` - Resolve ambiguities (max 5 questions)
4. `/iikit-plan` - Create technical implementation plan
5. `/iikit-checklist` - Generate domain-specific quality checklists
6. `/iikit-tasks` - Generate task breakdown
7. `/iikit-analyze` - Validate cross-artifact consistency
8. `/iikit-implement` - Execute implementation

**Never skip phases.** Each skill validates its prerequisites.

## Constitution

Read `CONSTITUTION.md` for this project's governing principles.

## Active Technologies

- Python 3.12 + `langgraph`, `typing-extensions` (001-langgraph-scaffolding)

## Project Structure

```text
src/
tests/
```

## Commands

```bash
cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .
```

## Conventions

[LANGUAGE-SPECIFIC, ONLY FOR LANGUAGES IN USE]

## Recent Changes

- 001-langgraph-scaffolding: Added Python 3.12 + `langgraph`, `typing-extensions`

<!-- IIKIT-TECH-START -->
<!-- Tech stack will be inserted here by /iikit-plan -->
<!-- IIKIT-TECH-END -->
