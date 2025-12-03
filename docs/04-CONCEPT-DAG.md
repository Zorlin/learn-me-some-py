# Python Concept DAG (Directed Acyclic Graph)

**Status:** Documentation skeleton - to be filled

## Overview

Progressive disclosure system organizing Python concepts as a DAG with prerequisites and mastery levels.

### Table of Contents
- DAG Structure
- Concept Definition Format
- Prerequisite Resolution
- Mastery Level System
- Unlocking Mechanics
- Dynamic Registration

### Key Components
- `lmsp/python/concepts.py` - Concept DAG management
- `concepts/` - TOML concept definitions
- `concepts/level_0/` through `concepts/level_6/` - Level-specific concepts

### Dependencies
- TOML parsing
- Graph library (networkx)
- Concept schema validation

### Testing Strategy
- Unit tests for DAG validation
- Cycle detection tests
- Prerequisite resolution tests

## To Be Completed

- [ ] Complete DAG diagram
- [ ] Concept schema specification
- [ ] TOML format documentation
- [ ] Prerequisite resolution algorithm
- [ ] Mastery level progression rules
- [ ] Unlock condition logic
- [ ] Dynamic registration mechanism
