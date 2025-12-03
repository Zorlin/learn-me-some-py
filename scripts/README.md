# Swarm Orchestrator

This directory contains the swarm orchestration script for managing 20 Claude agents across 4 development phases.

## Usage

```bash
# Run full swarm orchestration
python scripts/swarm_orchestrator.py

# Or make it executable and run directly
./scripts/swarm_orchestrator.py
```

## Architecture

The swarm organizer manages **20 Claude agents** across **4 phases**:

### Phase 1: Documentation (8 agents)
- Vision & Philosophy
- Architecture
- Concepts
- Input Systems
- Adaptive Engine
- Multiplayer
- Introspection
- API Reference

### Phase 2: Core Systems (5 agents)
- Concept Registry & DAG
- Challenge Loader & Validator
- Progression System
- Game Loop & State
- Basic TUI Renderer

### Phase 3: Advanced Features (4 agents)
- Gamepad Input System
- Advanced Adaptive Features
- Multiplayer Integration
- Introspection System

### Phase 4: Polish & Integration (3 agents)
- Content Creation (TOML)
- System Integration & CLI
- Comprehensive Testing

## Features

- **Parallel execution**: Agents within same phase run concurrently
- **Dependency tracking**: Automatic dependency resolution
- **Failure handling**: Track failures, attempt recovery
- **Progress reporting**: Real-time status updates
- **Final report**: JSON report with metrics

## Output

Logs and reports are saved to:
- `.palace/swarm_logs/` - Individual agent logs
- `.palace/swarm_logs/swarm_report_*.json` - Final execution report

## Agent Details

Each agent has:
- **Unique ID**: For tracking and logging
- **Phase assignment**: Determines execution order
- **Task description**: What the agent builds
- **Dependencies**: Prerequisites before execution
- **Status tracking**: PENDING → RUNNING → COMPLETED/FAILED/BLOCKED

## Infrastructure-First Approach

The orchestration follows an infrastructure-first methodology:
1. **Foundation first**: Documentation and architecture
2. **Core systems next**: Essential game systems
3. **Rich features third**: Advanced capabilities
4. **Polish last**: Integration and testing

This ensures each phase builds solidly on previous work, minimizing rework and maximizing coherence.
