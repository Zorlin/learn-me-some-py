# Progression & Mastery System

**Status:** Documentation skeleton - to be filled

## Overview

Experience points, skill trees, mastery levels, and achievement tracking.

### Table of Contents
- Progression Architecture
- Skill Tree Structure
- Experience System
- Mastery Levels (0-4)
- Unlock Conditions
- Achievement Tracking
- Progression Persistence

### Key Components
- `lmsp/progression/tree.py` - Skill tree (DAG)
- `lmsp/progression/unlock.py` - Unlock conditions
- `lmsp/progression/xp.py` - Experience system
- `lmsp/progression/mastery.py` - Mastery level management

### Dependencies
- Concept DAG integration
- Challenge completion tracking
- Time-based progression
- Persistence layer

### Testing Strategy
- Unit tests for progression logic
- XP calculation tests
- Mastery level advancement tests
- Unlock condition tests

## To Be Completed

- [ ] Progression algorithm details
- [ ] Experience point formula
- [ ] Mastery level criteria
- [ ] Unlock condition specifications
- [ ] Achievement definitions
- [ ] Persistence schema
- [ ] Progression visualization
