# Adaptive Learning System

**Status:** Documentation skeleton - to be filled

## Overview

The core adaptive AI engine that learns the player's learning style, strengths, and weaknesses.

### Table of Contents
- Engine Architecture
- Recommendation Algorithm
- Learning Profile
- Session Management
- Data Persistence

### Key Components
- `lmsp/adaptive/engine.py` - Core adaptive AI
- `lmsp/adaptive/spaced.py` - Spaced repetition scheduler
- `lmsp/adaptive/fun.py` - Fun tracking
- `lmsp/adaptive/weakness.py` - Weakness detection
- `lmsp/adaptive/project.py` - Project-driven curriculum

### Dependencies
- Learning profile storage
- Spaced repetition algorithm (Anki-style)
- Time/datetime utilities
- JSON serialization

### Testing Strategy
- Unit tests for recommendation logic
- Mock learner profiles for different scenarios
- Spaced repetition schedule validation

## To Be Completed

- [ ] Recommendation algorithm details
- [ ] Spaced repetition schedule specification
- [ ] Fun tracking metrics
- [ ] Weakness detection heuristics
- [ ] Project curriculum generation
- [ ] Profile schema documentation
