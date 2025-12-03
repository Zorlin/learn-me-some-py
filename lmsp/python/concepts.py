"""
Concept DAG Loader
==================

Python concepts are organized as a Directed Acyclic Graph (DAG), not a linear list.
This allows learners to explore multiple paths based on interests and goals.

Concepts are defined in TOML files under concepts/level_N/ directories.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import networkx as nx

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older versions


@dataclass
class Concept:
    """
    A Python concept that can be learned.

    Concepts have prerequisites - you can't learn functions
    before you understand variables.
    """
    id: str
    name: str
    level: int
    prerequisites: list[str] = field(default_factory=list)

    # Description
    description_brief: str = ""
    description_detailed: str = ""

    # Methods this concept introduces (for collections, classes, etc.)
    methods: dict[str, str] = field(default_factory=dict)

    # Common mistakes to watch for
    gotchas: dict[str, str] = field(default_factory=dict)

    # Controller tutorial
    gamepad_tutorial: str = ""

    # Associated challenges
    challenge_starter: Optional[str] = None
    challenge_intermediate: Optional[str] = None
    challenge_mastery: Optional[str] = None

    # Fun factor for adaptive engine
    fun_type: str = "puzzle"
    fun_description: str = ""
    fun_examples: list[str] = field(default_factory=list)

    # Adaptive signals
    weakness_signals: list[str] = field(default_factory=list)
    strength_indicators: list[str] = field(default_factory=list)

    @classmethod
    def from_toml(cls, data: dict) -> "Concept":
        """Parse a Concept from TOML data."""
        concept_section = data.get("concept", {})
        description = data.get("description", {})
        challenges = data.get("challenges", {})
        fun_factor = data.get("fun_factor", {})
        adaptive = data.get("adaptive", {})
        gamepad = data.get("gamepad_tutorial", {})

        return cls(
            id=concept_section.get("id", "unknown"),
            name=concept_section.get("name", "Unknown Concept"),
            level=concept_section.get("level", 0),
            prerequisites=concept_section.get("prerequisites", []),
            description_brief=description.get("brief", ""),
            description_detailed=description.get("detailed", ""),
            methods=data.get("methods", {}),
            gotchas=data.get("gotchas", {}),
            gamepad_tutorial=gamepad.get("text", ""),
            challenge_starter=challenges.get("starter"),
            challenge_intermediate=challenges.get("intermediate"),
            challenge_mastery=challenges.get("mastery"),
            fun_type=fun_factor.get("type", "puzzle"),
            fun_description=fun_factor.get("description", ""),
            fun_examples=fun_factor.get("examples", []),
            weakness_signals=adaptive.get("weakness_signals", []),
            strength_indicators=adaptive.get("strength_indicators", []),
        )


class ConceptLoader:
    """
    Loads concepts from TOML files.

    Directory structure:
        concepts/
            level_0/
                variables.toml
                types.toml
            level_1/
                if_else.toml
                for_loops.toml
    """

    def __init__(self, concepts_dir: Path):
        self.concepts_dir = Path(concepts_dir)
        self._cache: dict[str, Concept] = {}

    def load(self, concept_id: str) -> Optional[Concept]:
        """Load a single concept by ID."""
        if concept_id in self._cache:
            return self._cache[concept_id]

        # Search all level directories
        for level_dir in sorted(self.concepts_dir.iterdir()):
            if not level_dir.is_dir() or not level_dir.name.startswith("level_"):
                continue

            for toml_file in level_dir.glob("*.toml"):
                concept = self._load_file(toml_file)
                if concept and concept.id == concept_id:
                    self._cache[concept_id] = concept
                    return concept

        return None

    def load_all(self) -> list[Concept]:
        """Load all concepts from all levels."""
        concepts = []

        for level_dir in sorted(self.concepts_dir.iterdir()):
            if not level_dir.is_dir() or not level_dir.name.startswith("level_"):
                continue

            for toml_file in level_dir.glob("*.toml"):
                concept = self._load_file(toml_file)
                if concept:
                    self._cache[concept.id] = concept
                    concepts.append(concept)

        return concepts

    def get_by_level(self, level: int) -> list[Concept]:
        """Get all concepts at a specific level."""
        all_concepts = self.load_all()
        return [c for c in all_concepts if c.level == level]

    def _load_file(self, path: Path) -> Optional[Concept]:
        """Load a concept from a TOML file."""
        try:
            with open(path, "rb") as f:
                data = tomllib.load(f)
            return Concept.from_toml(data)
        except Exception as e:
            print(f"Warning: Failed to load {path}: {e}")
            return None


class ConceptRegistry:
    """
    Registry for dynamic concept management with DAG validation.

    Ensures:
    - No cycles in prerequisites
    - All prerequisites exist
    - Concepts can be queried by unlock status
    """

    def __init__(self):
        self.concepts: dict[str, Concept] = {}

    def register(self, concept: Concept):
        """Register a concept, validating prerequisites."""
        # Check all prerequisites exist
        for prereq in concept.prerequisites:
            if prereq not in self.concepts:
                raise ValueError(
                    f"Concept '{concept.id}' has unknown prerequisite: '{prereq}'"
                )

        # Check for cycles (simple DFS)
        if self._would_create_cycle(concept):
            raise ValueError(
                f"Adding concept '{concept.id}' would create a cycle"
            )

        self.concepts[concept.id] = concept

    def register_all(self, concepts: list[Concept]):
        """Register multiple concepts, sorting by level to handle dependencies."""
        # Sort by level to ensure prerequisites are registered first
        sorted_concepts = sorted(concepts, key=lambda c: c.level)

        for concept in sorted_concepts:
            # For bulk registration, allow missing prerequisites (they'll come)
            self.concepts[concept.id] = concept

    def get_unlockable(self, mastered: set[str]) -> list[Concept]:
        """Get concepts that can be unlocked given current mastery."""
        unlockable = []

        for concept in self.concepts.values():
            # Skip already mastered
            if concept.id in mastered:
                continue

            # Check all prerequisites are mastered
            if all(p in mastered for p in concept.prerequisites):
                unlockable.append(concept)

        return unlockable

    def get_all_by_level(self, level: int) -> list[Concept]:
        """Get all concepts at a specific level."""
        return [c for c in self.concepts.values() if c.level == level]

    def get_prerequisites_for(self, concept_id: str) -> list[Concept]:
        """Get all prerequisites for a concept (recursive)."""
        concept = self.concepts.get(concept_id)
        if not concept:
            return []

        prereqs = []
        visited = set()

        def collect_prereqs(cid: str):
            if cid in visited:
                return
            visited.add(cid)

            c = self.concepts.get(cid)
            if not c:
                return

            for prereq_id in c.prerequisites:
                collect_prereqs(prereq_id)
                prereq = self.concepts.get(prereq_id)
                if prereq:
                    prereqs.append(prereq)

        collect_prereqs(concept_id)
        return prereqs

    def _would_create_cycle(self, new_concept: Concept) -> bool:
        """Check if adding this concept would create a cycle."""
        # Check if any of the new concept's prerequisites
        # eventually depend on this concept
        def has_path_to(from_id: str, to_id: str, visited: set) -> bool:
            if from_id == to_id:
                return True
            if from_id in visited:
                return False
            visited.add(from_id)

            concept = self.concepts.get(from_id)
            if not concept:
                return False

            for prereq in concept.prerequisites:
                if has_path_to(prereq, to_id, visited):
                    return True

            return False

        # Check if any prerequisite has a path back to this concept
        for prereq in new_concept.prerequisites:
            if has_path_to(prereq, new_concept.id, set()):
                return True

        return False


class ConceptDAG:
    """
    Complete DAG implementation using networkx for advanced graph operations.

    Provides:
    - Topological sorting (learning order)
    - Unlocks tracking (what each concept enables)
    - Cycle detection and validation
    - Path finding between concepts
    """

    def __init__(self, concepts_dir: Path):
        self.concepts_dir = Path(concepts_dir)
        self.concepts: dict[str, Concept] = {}
        self.graph = nx.DiGraph()

    def load_all(self) -> dict[str, Concept]:
        """Load all concepts and build the DAG."""
        loader = ConceptLoader(self.concepts_dir)
        concepts_list = loader.load_all()

        # Store concepts
        for concept in concepts_list:
            self.concepts[concept.id] = concept

        # Build directed graph: edge from prereq -> concept
        for concept in concepts_list:
            self.graph.add_node(concept.id)
            for prereq in concept.prerequisites:
                if prereq not in self.concepts:
                    print(f"Warning: Concept '{concept.id}' references unknown prerequisite '{prereq}'")
                    continue
                # Edge direction: prereq -> concept (prereq unlocks concept)
                self.graph.add_edge(prereq, concept.id)

        return self.concepts

    def get_concept(self, concept_id: str) -> Optional[Concept]:
        """Get a concept by ID."""
        return self.concepts.get(concept_id)

    def get_prerequisites(self, concept_id: str) -> list[str]:
        """
        Get direct prerequisites for a concept.

        Returns:
            List of concept IDs that must be mastered before this one.
        """
        concept = self.concepts.get(concept_id)
        if not concept:
            return []
        return concept.prerequisites.copy()

    def get_all_prerequisites(self, concept_id: str) -> list[str]:
        """
        Get ALL prerequisites recursively (transitive closure).

        Returns:
            List of all concept IDs in the prerequisite chain.
        """
        if concept_id not in self.graph:
            return []

        # All ancestors in the DAG
        try:
            ancestors = nx.ancestors(self.graph, concept_id)
            return list(ancestors)
        except nx.NetworkXError:
            return []

    def get_unlocks(self, concept_id: str) -> list[str]:
        """
        Get concepts directly unlocked by mastering this concept.

        Returns:
            List of concept IDs that become available after mastering this one.
        """
        if concept_id not in self.graph:
            return []

        # Direct successors (concepts that have this as prerequisite)
        return list(self.graph.successors(concept_id))

    def get_all_unlocks(self, concept_id: str) -> list[str]:
        """
        Get ALL concepts unlocked recursively by mastering this concept.

        Returns:
            List of all concept IDs in the unlock chain.
        """
        if concept_id not in self.graph:
            return []

        # All descendants in the DAG
        try:
            descendants = nx.descendants(self.graph, concept_id)
            return list(descendants)
        except nx.NetworkXError:
            return []

    def topological_sort(self) -> list[str]:
        """
        Get concepts in valid learning order (topological sort).

        Returns:
            List of concept IDs in an order where all prerequisites
            come before their dependent concepts.

        Raises:
            nx.NetworkXError if the graph contains cycles.
        """
        return list(nx.topological_sort(self.graph))

    def get_unlockable(self, mastered: set[str]) -> list[str]:
        """
        Get concepts that can be unlocked given current mastery.

        A concept is unlockable if:
        1. It hasn't been mastered yet
        2. All its prerequisites have been mastered

        Returns:
            List of concept IDs ready to learn.
        """
        unlockable = []

        for concept_id, concept in self.concepts.items():
            # Skip already mastered
            if concept_id in mastered:
                continue

            # Check if all prerequisites are mastered
            if all(prereq in mastered for prereq in concept.prerequisites):
                unlockable.append(concept_id)

        return unlockable

    def validate_dag(self) -> list[str]:
        """
        Validate the concept DAG for common errors.

        Returns:
            List of error messages. Empty list means valid DAG.
        """
        errors = []

        # Check for cycles
        if not nx.is_directed_acyclic_graph(self.graph):
            try:
                cycle = nx.find_cycle(self.graph)
                cycle_str = " -> ".join(f"{u}" for u, v in cycle)
                errors.append(f"Cycle detected: {cycle_str}")
            except nx.NetworkXNoCycle:
                errors.append("Graph is not a DAG (has cycles)")

        # Check for missing prerequisites
        for concept_id, concept in self.concepts.items():
            for prereq in concept.prerequisites:
                if prereq not in self.concepts:
                    errors.append(
                        f"Concept '{concept_id}' references unknown prerequisite '{prereq}'"
                    )

        # Check for orphaned nodes (no edges at all)
        isolated = list(nx.isolates(self.graph))
        if isolated:
            # Root nodes (no prerequisites) are OK
            for node_id in isolated:
                concept = self.concepts.get(node_id)
                if concept and len(concept.prerequisites) == 0:
                    # This is a root concept, not an error
                    continue
                errors.append(f"Orphaned concept: '{node_id}' (no connections)")

        # Check for multiple components (disconnected subgraphs)
        if not nx.is_weakly_connected(self.graph):
            num_components = nx.number_weakly_connected_components(self.graph)
            errors.append(
                f"Graph is disconnected: {num_components} separate components"
            )

        return errors

    def get_learning_path(self, from_concept: str, to_concept: str) -> list[str]:
        """
        Find the shortest learning path between two concepts.

        Returns:
            List of concept IDs forming a path from from_concept to to_concept.
            Empty list if no path exists.
        """
        if from_concept not in self.graph or to_concept not in self.graph:
            return []

        try:
            path = nx.shortest_path(self.graph, from_concept, to_concept)
            return path
        except nx.NetworkXNoPath:
            return []

    def get_concepts_by_level(self, level: int) -> list[Concept]:
        """Get all concepts at a specific level."""
        return [c for c in self.concepts.values() if c.level == level]

    def get_root_concepts(self) -> list[str]:
        """
        Get root concepts (no prerequisites).

        These are the entry points for learning.
        """
        return [
            concept_id
            for concept_id, concept in self.concepts.items()
            if len(concept.prerequisites) == 0
        ]

    def get_leaf_concepts(self) -> list[str]:
        """
        Get leaf concepts (don't unlock anything else).

        These are terminal/advanced concepts.
        """
        return [
            concept_id
            for concept_id in self.concepts.keys()
            if len(list(self.graph.successors(concept_id))) == 0
        ]


# Self-teaching note:
#
# This file demonstrates:
# - Dataclasses with complex field types (Level 5+)
# - TOML parsing with tomli (Standard library extension)
# - Graph algorithms: DAG validation, cycle detection (Level 4+)
# - Optional types and default values (Professional Python)
# - Path handling with pathlib (Standard library)
# - Recursive algorithms (collect_prereqs)
#
# The learner will understand this after mastering:
# - Level 2: Collections (lists, dicts)
# - Level 3: Functions and recursion
# - Level 5: Classes and dataclasses
