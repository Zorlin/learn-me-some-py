#!/usr/bin/env python3
"""
Swarm Orchestrator - LMSP Development
Manages 20 Claude agents across 4 development phases.

Infrastructure-first approach:
- Phase 1: Documentation (8 agents)
- Phase 2: Core Systems (5 agents)
- Phase 3: Advanced Features (4 agents)
- Phase 4: Polish & Integration (3 agents)
"""

import asyncio
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any


class AgentStatus(Enum):
    """Agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Agent:
    """Represents a single Claude agent with task assignment"""
    id: str
    name: str
    phase: int
    task_description: str
    dependencies: List[str] = field(default_factory=list)
    status: AgentStatus = AgentStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    exit_code: Optional[int] = None
    output_file: Optional[Path] = None
    error_log: Optional[Path] = None
    process: Optional[subprocess.Popen] = None

    @property
    def duration(self) -> Optional[float]:
        """Calculate agent runtime duration"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        data['process'] = None  # Can't serialize subprocess
        return data


@dataclass
class SwarmReport:
    """Final swarm execution report"""
    start_time: datetime
    end_time: Optional[datetime] = None
    phases_completed: int = 0
    agents_total: int = 0
    agents_completed: int = 0
    agents_failed: int = 0
    agents: List[Dict[str, Any]] = field(default_factory=list)
    phase_summaries: Dict[int, Dict[str, Any]] = field(default_factory=dict)

    def to_json(self, path: Path):
        """Save report as JSON"""
        data = {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'phases_completed': self.phases_completed,
            'agents_total': self.agents_total,
            'agents_completed': self.agents_completed,
            'agents_failed': self.agents_failed,
            'agents': self.agents,
            'phase_summaries': self.phase_summaries,
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


class SwarmOrchestrator:
    """
    Orchestrates 20 Claude agents across 4 phases for LMSP development.

    Infrastructure-first: Each phase builds on previous work.
    Parallel execution: Agents within same phase run concurrently.
    Failure handling: Track failures, attempt recovery, continue execution.
    """

    def __init__(self, project_root: Path = Path("/mnt/castle/garage/learn-me-some-py")):
        self.project_root = project_root
        self.logs_dir = project_root / ".palace" / "swarm_logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.agents: List[Agent] = []
        self.report = SwarmReport(start_time=datetime.now())

        self._define_agents()

    def _define_agents(self):
        """Define all 20 agents with their tasks and dependencies"""

        # PHASE 1: Documentation (8 agents) - Foundation
        self.agents.extend([
            Agent(
                id="doc-vision",
                name="Vision & Philosophy Documentation",
                phase=1,
                task_description="Extract vision, philosophy, and core innovation from ULTRASPEC into docs/VISION.md",
            ),
            Agent(
                id="doc-architecture",
                name="Architecture Documentation",
                phase=1,
                task_description="Document system architecture, components, and integration patterns in docs/ARCHITECTURE.md",
            ),
            Agent(
                id="doc-concepts",
                name="Concept System Documentation",
                phase=1,
                task_description="Document concept DAG, mastery levels, and progressive disclosure in docs/CONCEPTS.md",
            ),
            Agent(
                id="doc-input",
                name="Input Systems Documentation",
                phase=1,
                task_description="Document radial typing, easy mode, emotional input in docs/INPUT_SYSTEMS.md",
            ),
            Agent(
                id="doc-adaptive",
                name="Adaptive Engine Documentation",
                phase=1,
                task_description="Document recommendation engine, fun tracking, weakness detection in docs/ADAPTIVE_ENGINE.md",
            ),
            Agent(
                id="doc-multiplayer",
                name="Multiplayer Documentation",
                phase=1,
                task_description="Document player-zero integration, session modes, stream-JSON protocol in docs/MULTIPLAYER.md",
            ),
            Agent(
                id="doc-introspection",
                name="Introspection Documentation",
                phase=1,
                task_description="Document TAS, screenshots, video mosaics, wireframes in docs/INTROSPECTION.md",
            ),
            Agent(
                id="doc-api",
                name="API Reference Documentation",
                phase=1,
                task_description="Generate API reference for emotional, adaptive, player-zero modules in docs/API_REFERENCE.md",
            ),
        ])

        # PHASE 2: Core Systems (5 agents) - Build foundation
        phase1_deps = [f"doc-{x}" for x in ["vision", "architecture", "concepts"]]

        self.agents.extend([
            Agent(
                id="core-concepts",
                name="Concept Registry & DAG",
                phase=2,
                task_description="Implement lmsp/python/concepts.py with DAG, registry, prerequisite checking",
                dependencies=["doc-concepts"],
            ),
            Agent(
                id="core-challenges",
                name="Challenge Loader & Validator",
                phase=2,
                task_description="Implement lmsp/python/challenges.py and lmsp/python/validator.py for loading/running challenges",
                dependencies=["doc-concepts"],
            ),
            Agent(
                id="core-progression",
                name="Progression System",
                phase=2,
                task_description="Implement lmsp/progression/ (tree.py, unlock.py, xp.py, mastery.py)",
                dependencies=["doc-concepts", "core-concepts"],
            ),
            Agent(
                id="core-game-loop",
                name="Game Loop & State",
                phase=2,
                task_description="Implement lmsp/game/engine.py and lmsp/game/state.py for core game loop",
                dependencies=["doc-architecture", "core-concepts"],
            ),
            Agent(
                id="core-tui",
                name="Basic TUI Renderer",
                phase=2,
                task_description="Implement lmsp/game/renderer.py using Rich/Textual for keyboard-based interface",
                dependencies=["doc-architecture", "core-game-loop"],
            ),
        ])

        # PHASE 3: Advanced Features (4 agents) - Add richness
        phase2_deps = ["core-concepts", "core-challenges", "core-game-loop"]

        self.agents.extend([
            Agent(
                id="adv-input",
                name="Gamepad Input System",
                phase=3,
                task_description="Implement lmsp/input/gamepad.py and lmsp/input/radial.py for controller support",
                dependencies=["doc-input", "core-tui"],
            ),
            Agent(
                id="adv-adaptive",
                name="Advanced Adaptive Features",
                phase=3,
                task_description="Implement lmsp/adaptive/spaced.py, fun.py, weakness.py, project.py",
                dependencies=["doc-adaptive", "core-concepts", "core-progression"],
            ),
            Agent(
                id="adv-multiplayer",
                name="Multiplayer Integration",
                phase=3,
                task_description="Implement lmsp/multiplayer/ for player-zero integration and session modes",
                dependencies=["doc-multiplayer", "core-game-loop"],
            ),
            Agent(
                id="adv-introspection",
                name="Introspection System",
                phase=3,
                task_description="Implement lmsp/introspection/ for screenshots, video, wireframes, mosaics",
                dependencies=["doc-introspection", "core-game-loop"],
            ),
        ])

        # PHASE 4: Polish & Integration (3 agents) - Ship it!
        phase3_deps = ["adv-input", "adv-adaptive", "adv-multiplayer"]

        self.agents.extend([
            Agent(
                id="polish-content",
                name="Content Creation (TOML)",
                phase=4,
                task_description="Create concepts/*.toml and challenges/*.toml for all levels",
                dependencies=["core-concepts", "core-challenges"],
            ),
            Agent(
                id="polish-integration",
                name="System Integration & CLI",
                phase=4,
                task_description="Implement lmsp/main.py CLI, integrate all systems, add pyproject.toml entry points",
                dependencies=phase3_deps,
            ),
            Agent(
                id="polish-tests",
                name="Comprehensive Testing",
                phase=4,
                task_description="Create tests for all modules, ensure >90% coverage, fix failing tests",
                dependencies=["polish-integration"],
            ),
        ])

        self.report.agents_total = len(self.agents)

    async def run(self, max_parallel: int = 8):
        """
        Execute all agents across 4 phases.

        Args:
            max_parallel: Maximum agents to run concurrently per phase
        """
        print(f"\n🚀 Starting Swarm Orchestrator - {self.report.agents_total} agents across 4 phases\n")
        print(f"📁 Project: {self.project_root}")
        print(f"📊 Logs: {self.logs_dir}\n")

        for phase in range(1, 5):
            await self._execute_phase(phase, max_parallel)

        self.report.end_time = datetime.now()
        await self._generate_report()

    async def _execute_phase(self, phase: int, max_parallel: int):
        """Execute all agents in a given phase"""
        phase_agents = [a for a in self.agents if a.phase == phase]

        if not phase_agents:
            return

        print(f"\n{'='*80}")
        print(f"PHASE {phase}: {len(phase_agents)} agents")
        print(f"{'='*80}\n")

        # Group agents by dependency levels for proper ordering
        ready = []
        waiting = []

        for agent in phase_agents:
            if self._dependencies_met(agent):
                ready.append(agent)
            else:
                waiting.append(agent)

        while ready or waiting:
            # Launch ready agents (up to max_parallel)
            batch = []
            while ready and len(batch) < max_parallel:
                agent = ready.pop(0)
                self._launch_agent(agent)
                batch.append(agent)

            if batch:
                # Wait for at least one to complete
                await self._wait_for_batch(batch)

                # Check if any waiting agents are now ready
                newly_ready = []
                for agent in waiting[:]:
                    if self._dependencies_met(agent):
                        waiting.remove(agent)
                        newly_ready.append(agent)
                ready.extend(newly_ready)
            elif waiting:
                # All ready agents launched, wait for completions to unblock waiting
                running = [a for a in phase_agents if a.status == AgentStatus.RUNNING]
                if running:
                    await self._wait_for_batch(running)
                else:
                    # Deadlock or all blocked
                    print(f"\n⚠️  Warning: {len(waiting)} agents blocked with unmet dependencies")
                    for agent in waiting:
                        agent.status = AgentStatus.BLOCKED
                    break
            else:
                break

        # Summarize phase
        completed = sum(1 for a in phase_agents if a.status == AgentStatus.COMPLETED)
        failed = sum(1 for a in phase_agents if a.status == AgentStatus.FAILED)
        blocked = sum(1 for a in phase_agents if a.status == AgentStatus.BLOCKED)

        self.report.phase_summaries[phase] = {
            'total': len(phase_agents),
            'completed': completed,
            'failed': failed,
            'blocked': blocked,
        }

        if completed == len(phase_agents):
            self.report.phases_completed += 1

        print(f"\n📊 Phase {phase} Summary:")
        print(f"   ✅ Completed: {completed}/{len(phase_agents)}")
        if failed:
            print(f"   ❌ Failed: {failed}")
        if blocked:
            print(f"   🚫 Blocked: {blocked}")

    def _dependencies_met(self, agent: Agent) -> bool:
        """Check if all dependencies are satisfied"""
        for dep_id in agent.dependencies:
            dep_agent = next((a for a in self.agents if a.id == dep_id), None)
            if not dep_agent or dep_agent.status != AgentStatus.COMPLETED:
                return False
        return True

    def _launch_agent(self, agent: Agent):
        """Launch a Claude Code agent via subprocess"""
        agent.status = AgentStatus.RUNNING
        agent.start_time = time.time()

        # Prepare output files
        agent.output_file = self.logs_dir / f"{agent.id}.log"
        agent.error_log = self.logs_dir / f"{agent.id}.error.log"

        print(f"🔷 Launching: {agent.name} ({agent.id})")

        # Build Claude Code command
        # Using Palace's 'pal next' with specific task
        cmd = [
            "pal", "next",
            "--task", agent.task_description,
            "--model", "sonnet",
            "--output", str(agent.output_file),
        ]

        try:
            agent.process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=open(agent.output_file, 'w'),
                stderr=open(agent.error_log, 'w'),
                text=True,
            )
        except Exception as e:
            print(f"   ❌ Failed to launch: {e}")
            agent.status = AgentStatus.FAILED
            agent.end_time = time.time()

    async def _wait_for_batch(self, batch: List[Agent]):
        """Wait for agents in batch to complete"""
        while True:
            for agent in batch:
                if agent.status != AgentStatus.RUNNING:
                    continue

                if agent.process is None:
                    continue

                # Check if process completed
                retcode = agent.process.poll()
                if retcode is not None:
                    agent.end_time = time.time()
                    agent.exit_code = retcode

                    if retcode == 0:
                        agent.status = AgentStatus.COMPLETED
                        self.report.agents_completed += 1
                        print(f"   ✅ {agent.name} ({agent.duration:.1f}s)")
                    else:
                        agent.status = AgentStatus.FAILED
                        self.report.agents_failed += 1
                        print(f"   ❌ {agent.name} failed (exit code {retcode})")

            # Check if all completed
            if all(a.status in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.BLOCKED]
                   for a in batch):
                break

            await asyncio.sleep(1)

    async def _generate_report(self):
        """Generate final swarm execution report"""
        # Collect agent data
        self.report.agents = [agent.to_dict() for agent in self.agents]

        # Save JSON report
        report_file = self.logs_dir / f"swarm_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.report.to_json(report_file)

        # Print summary
        print(f"\n{'='*80}")
        print("SWARM EXECUTION COMPLETE")
        print(f"{'='*80}\n")

        total_duration = (self.report.end_time - self.report.start_time).total_seconds()

        print(f"⏱️  Total Duration: {total_duration:.1f}s ({total_duration/60:.1f} minutes)")
        print(f"📊 Phases Completed: {self.report.phases_completed}/4")
        print(f"✅ Agents Completed: {self.report.agents_completed}/{self.report.agents_total}")
        print(f"❌ Agents Failed: {self.report.agents_failed}/{self.report.agents_total}")
        print(f"\n📄 Full report: {report_file}")

        # Print phase summaries
        print(f"\n{'='*80}")
        print("PHASE SUMMARIES")
        print(f"{'='*80}\n")

        for phase, summary in sorted(self.report.phase_summaries.items()):
            print(f"Phase {phase}:")
            print(f"  ✅ {summary['completed']}/{summary['total']} completed")
            if summary['failed']:
                print(f"  ❌ {summary['failed']} failed")
            if summary['blocked']:
                print(f"  🚫 {summary['blocked']} blocked")
            print()

        # List failed agents
        failed = [a for a in self.agents if a.status == AgentStatus.FAILED]
        if failed:
            print(f"{'='*80}")
            print("FAILED AGENTS")
            print(f"{'='*80}\n")
            for agent in failed:
                print(f"❌ {agent.name} ({agent.id})")
                print(f"   Error log: {agent.error_log}")
                print()

        return report_file


async def main():
    """Main entry point"""
    orchestrator = SwarmOrchestrator()
    await orchestrator.run(max_parallel=8)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(130)
